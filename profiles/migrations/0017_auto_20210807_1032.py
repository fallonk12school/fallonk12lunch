# Generated by Django 3.2.5 on 2021-08-07 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0016_remove_lunch_uuid_null'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='lunch_id',
        ),
        migrations.AddField(
            model_name='profile',
            name='cards_printed',
            field=models.SmallIntegerField(default=0, help_text='How many lunch cards have been printer for this user?', verbose_name='# of Lunch Cards Printed'),
        ),
    ]
