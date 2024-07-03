# Generated by Django 5.0.4 on 2024-07-02 09:15

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0004_alter_leave_editstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeavePolicy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('name', models.CharField(max_length=25)),
                ('max_days_allowed', models.FloatField(blank=True, null=True)),
                ('description', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, null=True, size=None)),
                ('draft_state', models.JSONField(default=dict, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('leave_type', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leave_policy_type', to='LeaveTrackingApp.leavetype')),
            ],
        ),
        migrations.CreateModel(
            name='YearPolicy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('year', models.IntegerField()),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Expired', 'Expired'), ('Published', 'Published')], default='Draft', max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('leave_policies', models.ManyToManyField(to='LeaveTrackingApp.leavepolicy')),
            ],
        ),
    ]