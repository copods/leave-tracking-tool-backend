# Generated by Django 5.0.4 on 2024-06-07 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0004_alter_holiday_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='leave',
            name='editStatus',
            field=models.CharField(choices=[('Edited', 'Edited'), ('Requested-For-Edit', 'Requested-For-Edit')], max_length=100, null=True),
        ),
    ]