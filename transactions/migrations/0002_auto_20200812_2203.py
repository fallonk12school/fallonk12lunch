# Generated by Django 3.1 on 2020-08-13 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='menu_items',
            field=models.ManyToManyField(blank=True, related_name='transactions', through='transactions.MenuLineItem', to='menu.MenuItem'),
        ),
    ]
