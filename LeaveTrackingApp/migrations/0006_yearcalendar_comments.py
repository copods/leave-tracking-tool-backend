# Generated by Django 5.0.4 on 2024-07-09 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0005_yearcalendar_comments_alter_statusreason_reason_and_more'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='yearcalendar',
            name='comments',
            field=models.ManyToManyField(blank=True, to='common.comment'),
        ),
    ]