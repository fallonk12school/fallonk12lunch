# Generated by Django 3.1.2 on 2020-11-10 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20200904_1130'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['submitted']},
        ),
        migrations.AddField(
            model_name='transaction',
            name='ps_transaction_id',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
