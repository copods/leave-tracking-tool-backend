# Generated by Django 5.0.4 on 2024-05-19 16:47

import apps.user.models
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('department', '0001_initial'),
        ('role', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Public identifier')),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.BigIntegerField(validators=[apps.user.models.validate_phone_number])),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('dob', models.DateField()),
                ('profile_image', models.CharField(null=True)),
                ('doj', models.DateField()),
                ('work_type', models.CharField(choices=[('WFO', 'Work From Office'), ('WFH', 'Work From Home')], max_length=3, null=True)),
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
                ('emergency_contact_number', models.BigIntegerField(null=True, validators=[apps.user.models.validate_phone_number])),
                ('emergency_contact_relation', models.CharField(max_length=100, null=True)),
                ('emergency_contact_email', models.EmailField(max_length=100, null=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='department.department')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='role.role')),
            ],
        ),
    ]
