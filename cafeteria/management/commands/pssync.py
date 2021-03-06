#
# pssync.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.utils import timezone

import logging

from cafeteria.models import GradeLevel, School
from powerschool.powerschool import Powerschool
from profiles.models import Profile


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Synchronize resources from PowerSchool to Lunch Manager'

    def add_arguments(self, parser):
        parser.add_argument(
            'resource',
            choices=['all', 'schools', 'staff', 'students'],
            default='all',
            help='Select the resource to sycn from PowerSchool. The default is to sync ALL resources.',
            nargs='?'
        )

    def handle(self, *args, **options):
        client = Powerschool()
        if options['resource'] == 'all':
            self.sync_schools_using_client(client)
            self.sync_students_using_client(client)
            self.sync_staff_using_client(client)
        elif options['resource'] == 'schools':
            self.sync_schools_using_client(client)
        elif options['resource'] == 'staff':
            self.sync_staff_using_client(client)
        elif options['resource'] == 'students':
            self.sync_students_using_client(client)

    def sync_schools_using_client(self, client):
        logger.info('Synchronizing schools...')
        schools = client.schools()
        for item in schools:
            school, created = School.objects.update_or_create(id=item['id'],
                                                              defaults={
                'name': item['name'],
                'school_number': item['school_number']
            })
            if (created == False and school.active == True):
                start = item['low_grade']
                end = item['high_grade']
                for grade_level in range(start, end + 1):
                    grade, created = GradeLevel.objects.update_or_create(value=grade_level,
                        defaults={
                            'school': school
                        })
        logger.info('All schools successfully synchronized...')

    def sync_staff_using_client(self, client):
        logger.info('Synchronizing staff...')
        active_staff = client.active_staff()
        newly_created = 0
        for member in active_staff:
            try:
                phone = 'x' + member['school_phone'][-4:]
            except:
                phone = 'x7900'
            try:
                room = member['homeroom']
            except:
                room = 'n/a'
            # look for an existing profile and create a new one if not found
            staff, created = Profile.objects.update_or_create(user_dcid=member['dcid'],
                                                              defaults={
                'last_sync': timezone.now(),
                'phone': phone,
                'role': Profile.STAFF,
                'room': room,
                'active': True,
                'user_number': member['teachernumber'],
            }
            )
            try:
                email_address = member['teacherloginid'] + '@nrcaknights.com'
            except:
                try:
                    email_address = member['loginid'] + '@nrcaknights.com'
                except:
                    email_address = member['user_dcid'] + '@nrcaknights.com'
            # if a new profile is created, create the corresponding user
            if created:
                user, created = User.objects.get_or_create(
                    first_name=member['first_name'],
                    last_name=member['last_name'],
                    email=email_address,
                    username=email_address,
                )
                staff.user = user
                staff.save()
                newly_created = newly_created + 1
            # if the staff member already exists, update the user info
            else:
                user = staff.user
                if user:
                    user.first_name = member['first_name']
                    user.last_name = member['last_name']
                    user.email = email_address
                    user.username = email_address
                    user.is_active = True
                    user.save()
                else:
                    user, created = User.objects.get_or_create(
                        first_name=member['first_name'],
                        last_name=member['last_name'],
                        email=email_address,
                        username=email_address,
                    )
                    staff.user = user
                    staff.save()
            # if the staff member has a homeroom, update their roster
            homeroom_roster = client.homeroom_roster_for_teacher(
                staff.user_dcid)
            if homeroom_roster:
                try:
                    grade_level = homeroom_roster[0]['grade_level']
                    count = 1
                    while grade_level == "" and count < len(homeroom_roster):
                        grade_level = homeroom_roster[count]['grade_level']
                        count = count + 1
                    staff.grade = GradeLevel.objects.get(value=int(grade_level))
                except:
                    staff.grade = None
                    logger.error('No grade level assigned to homeroom teacher: {}'.format(staff.name()))
                staff.students.clear()
                for student in homeroom_roster:
                    try:
                        student = Profile.objects.get(
                            student_dcid=int(student['dcid']))
                        staff.students.add(student)
                    except:
                        pass
            else:
                staff.grade = None
            staff.save()
        logger.info('Retrieved {} staff, created {} new staff members'.format(
            len(active_staff), newly_created))

    def sync_students_using_client(self, client):
        logger.info('Synchronizing students...')
        for school in School.objects.filter(active=True):
            logger.info('Sycning students from {} (id {})...'.format(
                school, school.id))
            active_students = client.studentsForSchool(
                school.id, 'lunch,school_enrollment')
            newly_created = 0
            for member in active_students:
                # look for an existing student and create a new one if not found
                grade = GradeLevel.objects.get(value=member['school_enrollment']['grade_level'])
                student, created = Profile.objects.update_or_create(student_dcid=member['id'],
                                                                    defaults={
                    'grade': grade,
                    'last_sync': timezone.now(),
                    'role': Profile.STUDENT,
                    'school': School.objects.get(id=member['school_enrollment']['school_id']),
                    'active': True,
                    'user_number': member['local_id'],
                }
                )
                try:
                    email_address = member['student_username'] + \
                        '@nrcaknights.com'
                except:
                    email_address = str(member['id']) + '@nrcaknights.com'
                # if a new student is created, create the corresponding user
                if created:
                    user, created = User.objects.get_or_create(
                        first_name=member['name']['first_name'],
                        last_name=member['name']['last_name'],
                        email=email_address,
                        username=email_address,
                    )
                    student.user = user
                    student.save()
                    newly_created = newly_created + 1
                # if the student already exists, update the user info
                else:
                    user = student.user
                    if user:
                        user.first_name = member['name']['first_name']
                        user.last_name = member['name']['last_name']
                        user.email = email_address
                        user.username = email_address
                        user.is_active = True
                        user.save()
                    else:
                        user, created = User.objects.get_or_create(
                            first_name=member['name']['first_name'],
                            last_name=member['name']['last_name'],
                            email=email_address,
                            username=email_address,
                        )
                        student.user = user
                        student.save()
            logger.info('Retreived {} students, created {} new students'.format(
                len(active_students), newly_created))
