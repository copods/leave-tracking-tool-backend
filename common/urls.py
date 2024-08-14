from common.views import *
from django.urls import re_path

urlpatterns = [
    #miscellaneous apis
    re_path(r'^clearAllLeaves$', clear_all_leaves),
    re_path(r'^clearAllNotifications$', clear_all_notifications),
    re_path(r'^sendDummyNotification$', send_dummy_notification),
    re_path(r'^getFcmTokens$', get_fcm_tokens),
    re_path(r'^fetchNotificationsDummy$', fetch_notifications),
    re_path(r'^clearLeavesOfUser/([0-9a-f-]+)$', clear_leaves_of_user),

]
