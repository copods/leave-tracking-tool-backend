# Generated by Django 5.0.4 on 2024-06-14 07:12

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0006_leave_status_reasons'),
        ('PushNotificationApp', '0001_initial'),
        ('UserApp', '0007_alter_user_emergency_contact_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('types', models.CharField(choices=[('Leave Request', 'Leave Request'), ('Upcoming Holidays', 'Upcoming Holidays')], max_length=100, unique=True, verbose_name='notification types')),
                ('isRead', models.BooleanField(default=False)),
                ('receivers', django.contrib.postgres.fields.ArrayField(base_field=models.UUIDField(), size=None)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('subtitle', models.CharField(max_length=300, verbose_name='subtitle')),
                ('redireactionUrl', models.CharField(max_length=250, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_created_by', to='UserApp.user')),
                ('leaveApplicationId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leave_request', to='LeaveTrackingApp.leave')),
            ],
        ),
    ]
