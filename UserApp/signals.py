from django.dispatch import Signal

# custom signal to handle change in Leave model on soft delete of user (approver)
user_pre_soft_delete_signal = Signal()


#add more signals here
