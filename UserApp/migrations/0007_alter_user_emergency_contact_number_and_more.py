# Generated by Django 5.0.4 on 2024-06-13 11:30

import UserApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0006_user_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='emergency_contact_number',
            field=models.BigIntegerField(null=True, validators=[UserApp.models.validate_phone_number]),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.CharField(max_length=250),
        ),
    ]
