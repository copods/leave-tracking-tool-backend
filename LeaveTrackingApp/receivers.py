from django.dispatch import receiver
from django.db.models import Q
from UserApp.signals import user_pre_soft_delete_signal
from UserApp.models import User
from LeaveTrackingApp.models import Leave

@receiver(user_pre_soft_delete_signal, sender=User)
def update_leave_approver(sender, instance, **kwargs):
    
    leaves_with_instance_as_user = Leave.objects.filter(user=instance)
    leaves_with_instance_as_approver = Leave.objects.filter(approver=instance)

    #modify leaves which are approved by instance
    if leaves_with_instance_as_approver.exists():
        # if the instance is hr, find another one, if not found, find admin, if no admin, send error -> IT MAY CHANGE AS HIERARCHY CHANGES
        if instance.role.role_key == 'hr':
            other_hr = User.objects.filter(role__role_key='hr').exclude(id=instance.id).first()
            if other_hr:
                leaves_with_instance_as_approver.update(approver=other_hr)
            else:
                admin = User.objects.filter(role__role_key='admin').first()
                if admin:
                    leaves_with_instance_as_approver.update(approver=admin)
                else: 
                    raise ValueError("Cannot delete user, no one available to replace the approver.")
        else:
            # Find the first user whose role is hr  ->  IT MAY CHANGE AS HIERARCHY CHANGES
            hr = User.objects.filter(role__role_key='hr').first()
            if hr:
                leaves_with_instance_as_approver.update(approver=hr)
            else:
                admin = User.objects.filter(role__role_key='admin').first()
                if admin:
                    leaves_with_instance_as_approver.update(approver=admin)
                else: 
                    raise ValueError("Cannot delete user, no one available to replace the approver.") 
    
    # delete the leaves which have instance as the user
    elif leaves_with_instance_as_user.exists():
        leaves_with_instance_as_user.delete()

    else:
        return
