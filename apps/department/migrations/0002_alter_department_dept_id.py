# Generated by Django 5.0.4 on 2024-05-14 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='dept_id',
            field=models.CharField(default='In0gmMqg_8m', max_length=12, primary_key=True, serialize=False),
        ),
    ]