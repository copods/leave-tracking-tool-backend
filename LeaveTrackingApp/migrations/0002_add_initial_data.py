# Generated by Django 5.0.4 on 2024-06-18 04:59

from django.db import migrations

def add_initial_data(apps, schema_editor):
    RuleSet = apps.get_model('LeaveTrackingApp', 'RuleSet')
    RuleSet.objects.create(name='pto', max_days_allowed=4.5, duration='quarterly')
    RuleSet.objects.create(name='maternity_leave', max_days_allowed=180, duration='None')
    RuleSet.objects.create(name='paternity_leave', max_days_allowed=10, duration='None')
    RuleSet.objects.create(name='marriage_leave', max_days_allowed=5, duration='None')
    RuleSet.objects.create(name='work_from_home', max_days_allowed=5, duration='quarterly')
    RuleSet.objects.create(name='miscellaneous_leave', duration='None')

    LeaveType = apps.get_model('LeaveTrackingApp', 'LeaveType')
    pto = RuleSet.objects.get(name='pto')
    maternity_leave = RuleSet.objects.get(name='maternity_leave')
    paternity_leave = RuleSet.objects.get(name='paternity_leave')
    marriage_leave = RuleSet.objects.get(name='marriage_leave')
    work_from_home = RuleSet.objects.get(name='work_from_home')
    miscellaneous_leave = RuleSet.objects.get(name='miscellaneous_leave')
    
    LeaveType.objects.create(name='emergency_leave', rule_set=miscellaneous_leave)
    LeaveType.objects.create(name='pto', rule_set=pto)
    LeaveType.objects.create(name='sick_leave', rule_set=miscellaneous_leave)
    LeaveType.objects.create(name='wfh', rule_set=work_from_home)
    LeaveType.objects.create(name='paternity_leave', rule_set=paternity_leave)
    LeaveType.objects.create(name='maternity_leave', rule_set=maternity_leave)
    LeaveType.objects.create(name='marriage_leave', rule_set=marriage_leave)

class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]
