import copy
import io

from pathlib import Path
from typing import List

from reportlab import platypus
from reportlab.graphics.barcode import qr
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm

from django.http import FileResponse
from django.utils import timezone

from profiles.models import Profile


def lunch_card_for_users(profiles: List[Profile]) -> FileResponse:
    buffer = io.BytesIO()
    card_width = 86*mm
    card_height = 54*mm
    margin = 2*mm
    document = platypus.BaseDocTemplate(buffer, pagesize=(card_width, card_height), rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)

    styles = getSampleStyleSheet()
    title_style = copy.copy(styles['Title'])
    title_style.fontSize = 20
    title_style.leading = 20
    title_style.spaceBefore = 0
    title_style.spaceAfter = 0
    normal_style = copy.copy(styles['Normal'])
    normal_style.fontSize = 16
    normal_style.leading = 18
    normal_style.alignment = TA_CENTER
    role_style = copy.copy(styles['Normal'])
    role_style.fontSize = 8
    role_style.leading = 8
    role_style.textTransform = 'uppercase'
    role_style.alignment = TA_CENTER

    qr_size = 37*mm
    top_offset = 4*mm
    role_height = 8*mm
    title_height = card_height - qr_size - top_offset
    
    frames = [platypus.Frame(document.leftMargin, card_height - title_height - top_offset, document.width, title_height, id="title-frame")]
    frames.append(platypus.Frame(document.leftMargin, document.bottomMargin, document.width - qr_size, qr_size, id="image-frame"))
    frames.append(platypus.Frame(document.leftMargin, document.bottomMargin, document.width - qr_size, qr_size, id="misc-frame"))
    frames.append(platypus.Frame(document.leftMargin, 0, document.width - qr_size, role_height, id="role-frame"))
    frames.append(platypus.Frame(card_width - qr_size, document.bottomMargin - margin, qr_size, qr_size, id="qr-frame"))
    template = platypus.PageTemplate(frames=frames)
    document.addPageTemplates(template)

    image_path = Path(__file__).resolve(strict=True).parent / 'report_images/knights-head.jpg'
    image = platypus.Image(image_path, width=30*mm, height=30*mm)

    data = []
    for profile in profiles:
        profile.cards_printed = profile.cards_printed + 1
        profile.save()
        name = platypus.Paragraph(profile.name(), title_style)
        data.append(platypus.KeepInFrame(card_width, title_height, content=[name]))
        data.append(platypus.FrameBreak('image-frame'))
        data.append(image)
        data.append(platypus.FrameBreak('misc-frame'))
        data.append(platypus.Paragraph('NRCA Cafeteria<br/>Lunch Card', normal_style))
        data.append(platypus.FrameBreak('role-frame'))
        data.append(platypus.Paragraph(profile.get_role_display(), role_style))
        data.append(platypus.FrameBreak('qr-frame'))
        data.append(qr.QrCode(str(profile.lunch_uuid), qrBorder=0))
        data.append(platypus.PageBreak())
    document.build(data)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='lunch_cards.pdf')

def orders_report_by_homeroom(todays_orders: List) -> FileResponse:
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    
    # create some styles and the base document
    normal_style = copy.copy(styles['Normal'])
    normal_style.fontSize = 12
    normal_style.leading = 14
    item_count_style = copy.copy(styles['Normal'])
    item_count_style.fontSize = 14
    item_count_style.leading = 16
    title_style = copy.copy(styles['Title'])
    title_style.fontSize = 26
    margin = 0.5*inch
    document = platypus.BaseDocTemplate(buffer, pagesize=letter, rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)
    
    # create the title frame
    title_frame_height = 0.5*inch
    title_frame_bottom = document.height + document.bottomMargin - title_frame_height
    title_frame = platypus.Frame(document.leftMargin, title_frame_bottom, document.width - document.rightMargin, title_frame_height)
    frames = [title_frame]
    
    # create three frames to hold the list of orders for each item
    item_frame_height = 2.0*inch
    student_frame_height = title_frame_bottom - (2.25*inch) - document.bottomMargin
    frame_width = document.width / 3.0
    for frame in range(3):
        left_margin = document.leftMargin + (frame * frame_width)
        column = platypus.Frame(left_margin, document.bottomMargin + item_frame_height, frame_width, student_frame_height, id='student-frame-{}'.format(frame))
        frames.append(column)
    
    # create a frame to hold the list of item totals
    column = platypus.Frame(document.leftMargin, document.bottomMargin, document.width, item_frame_height, id='item-frame')
    frames.append(column)

    template = platypus.PageTemplate(frames=frames)
    document.addPageTemplates(template)
    
    data = []
    for orders in todays_orders:
        item_orders = {}
        item_counts = {}
        teacher = orders['teacher']
        for item in orders['orders']:
            student = item.transaction.transactee.name()
            if item.quantity > 1:
                student = student + ' ({})'.format(item.quantity)
            if item.menu_item in item_orders:
                item_orders[item.menu_item].append(student)
            else:
                item_orders[item.menu_item] = [student]
            if item.menu_item in item_counts:
                item_counts[item.menu_item] = item_counts[item.menu_item] + item.quantity
            else:
                item_counts[item.menu_item] = item.quantity
        title = teacher.user.last_name
        data.append(platypus.Paragraph(title, title_style))
        data.append(platypus.FrameBreak())
        for item in item_orders:
            content = [platypus.Paragraph('<b><u>{}</u></b>'.format(item.name), normal_style)]
            for student in item_orders[item]:
                content.append(platypus.Paragraph(student, normal_style))
            content.append(platypus.Paragraph('<br/><br/>', normal_style))
            data.append(platypus.KeepTogether(content))
        data.append(platypus.FrameBreak('item-frame'))
        data.append(platypus.HRFlowable())
        content = []
        for item in item_counts:
            content.append(platypus.Paragraph('{} - <b>{}</b>'.format(item.name, item_counts[item]), item_count_style))
        data.append(platypus.BalancedColumns(content, nCols = 2, topPadding=(0.25 * inch)))
        data.append(platypus.PageBreak())
    document.build(data)
    buffer.seek(0)
    today = timezone.now()
    report_name = 'class_orders_{}-{}-{}.pdf'.format(today.year, today.month, today.day)
    return FileResponse(buffer, as_attachment=True, filename=report_name)