# Generated by Django 5.0.4 on 2024-05-28 12:35

import UserApp.models
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('department_key', models.CharField(max_length=100)),
                ('department_name', models.CharField(max_length=100)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('role_key', models.CharField(max_length=100)),
                ('role_name', models.CharField(max_length=100)),
                ('permissions', models.JSONField(default=dict)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Public identifier')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=100)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('date_of_birth', models.DateField()),
                ('profile_image', models.CharField(max_length=100)),
                ('date_of_joining', models.DateField()),
                ('work_type', models.CharField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract')], max_length=9, null=True)),
                ('designation', models.CharField(max_length=100, null=True)),
                ('work_location', models.CharField(max_length=100, null=True)),
                ('current_address_line', models.CharField(max_length=200, null=True)),
                ('current_address_city', models.CharField(max_length=100, null=True)),
                ('current_address_state', models.CharField(max_length=100, null=True)),
                ('current_address_pincode', models.IntegerField(null=True)),
                ('permanent_address_line', models.CharField(max_length=200, null=True)),
                ('permanent_address_city', models.CharField(max_length=100, null=True)),
                ('permanent_address_state', models.CharField(max_length=100, null=True)),
                ('permanent_address_pincode', models.IntegerField(null=True)),
                ('emergency_contact_name', models.CharField(max_length=100, null=True)),
                ('emergency_contact_number', models.BigIntegerField(null=True, validators=[UserApp.models.validate_phone_number])),
                ('emergency_contact_relation', models.CharField(max_length=100, null=True)),
                ('emergency_contact_email', models.EmailField(max_length=100, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='UserApp.department')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='UserApp.role')),
            ],
        ),
    ]
