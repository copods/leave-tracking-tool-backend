# Generated by Django 5.0.4 on 2024-07-08 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0006_alter_statusreason_reason_alter_statusreason_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yearcalendar',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('approved', 'Approved'), ('published', 'Published'), ('sent_for_approval', 'Sent For Approval')], default='draft', max_length=20),
        ),
    ]
