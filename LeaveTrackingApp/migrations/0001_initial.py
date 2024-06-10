# Generated by Django 5.0.4 on 2024-06-10 06:48

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('UserApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('date', models.DateField()),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('Optional', 'Optional'), ('Confirmed', 'Confirmed')], default='Confirmed', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RuleSet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('name', models.CharField(max_length=100)),
                ('max_days_allowed', models.FloatField(blank=True, null=True)),
                ('duration', models.CharField(default=None, max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DayDetails',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('date', models.DateField()),
                ('is_half_day', models.BooleanField()),
                ('half_day_type', models.CharField(blank=True, choices=[('FH', 'First Half'), ('SH', 'Second Half')], max_length=2, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LeaveTrackingApp.leavetype')),
            ],
        ),
        migrations.AddField(
            model_name='leavetype',
            name='rule_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LeaveTrackingApp.ruleset'),
        ),
        migrations.CreateModel(
            name='StatusReason',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('status', models.CharField(choices=[('P', 'PENDING'), ('A', 'APPROVED'), ('R', 'REJECTED'), ('W', 'WITHDRAWN')], default='P', max_length=100)),
                ('reason', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('leave_reason', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('P', 'PENDING'), ('A', 'APPROVED'), ('R', 'REJECTED'), ('W', 'WITHDRAWN')], default='P', max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('assets_documents', models.FileField(blank=True, null=True, upload_to='')),
                ('editStatus', models.CharField(choices=[('Edited', 'Edited'), ('Requested-For-Edit', 'Requested-For-Edit')], max_length=100, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approver_of_leave', to='UserApp.user')),
                ('day_details', models.ManyToManyField(to='LeaveTrackingApp.daydetails')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_of_leaves', to='UserApp.user')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LeaveTrackingApp.leavetype')),
                ('status_reasons', models.ManyToManyField(blank=True, to='LeaveTrackingApp.statusreason')),
            ],
        ),
        migrations.CreateModel(
            name='yearCalendar',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('year', models.IntegerField()),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Approved', 'Approved'), ('Published', 'Published')], default='Draft', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('holidays', models.ManyToManyField(to='LeaveTrackingApp.holiday')),
            ],
        ),
    ]
