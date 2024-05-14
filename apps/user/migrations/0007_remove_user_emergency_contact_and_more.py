# Generated by Django 5.0.4 on 2024-05-14 10:37

import apps.user.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_user_department'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='emergency_contact',
        ),
        migrations.AddField(
            model_name='user',
            name='current_address_city',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='current_address_line',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='current_address_pincode',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='current_address_state',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='designation',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='dob',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='user',
            name='emergency_contact_email',
            field=models.EmailField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='emergency_contact_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='emergency_contact_number',
            field=models.BigIntegerField(null=True, validators=[apps.user.models.validate_phone_number]),
        ),
        migrations.AddField(
            model_name='user',
            name='emergency_contact_relation',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='permanent_address_city',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='permanent_address_line',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='permanent_address_pincode',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='permanent_address_state',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='work_location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.BigIntegerField(validators=[apps.user.models.validate_phone_number]),
        ),
    ]
