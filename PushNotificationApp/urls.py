from django.urls import path, re_path
from PushNotificationApp.views import *

urlpatterns = [
    re_path(r'^fcmTokenStore$', fcmTokenStore),
    re_path(r'^fcmTokenValidate$', fcmTokenValidate),
    re_path(r'^fetchNotifications$', fetchNotifications),
    re_path(r'^updateNotifications$', updateNotifications),
]
