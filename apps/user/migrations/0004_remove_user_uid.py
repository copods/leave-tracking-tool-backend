# Generated by Django 5.0.4 on 2024-04-10 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="uid",
        ),
    ]
