# Generated by Django 5.0.4 on 2024-08-02 18:07

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PushNotificationApp', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='leaveApplicationId',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='types',
        ),
        migrations.AddField(
            model_name='notification',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='notification',
            name='object_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='target_platforms',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), default=list, size=None),
        ),
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('leave_request', 'Leave Request'), ('calendar', 'Calendar'), ('leave_policy', 'Leave Policy')], default='leave_request', max_length=100, verbose_name='notification type'),
        ),
    ]
