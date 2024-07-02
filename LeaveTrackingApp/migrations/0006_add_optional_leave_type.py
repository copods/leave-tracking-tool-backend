from django.db import migrations

def add_data(apps, schema_editor):
    RuleSet = apps.get_model('LeaveTrackingApp', 'RuleSet')
    RuleSet.objects.create(name='optional', max_days_allowed=2, duration='None')

    LeaveType = apps.get_model('LeaveTrackingApp', 'LeaveType')
    optional = RuleSet.objects.get(name='optional')
    
    LeaveType.objects.create(name='optional', rule_set=optional)

class Migration(migrations.Migration):

    dependencies = [
        ('LeaveTrackingApp', '0005_leavepolicy_yearpolicy'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]
