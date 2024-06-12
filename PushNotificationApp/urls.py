from django.urls import path, re_path

from PushNotificationApp.views.push_notification_views import (FCMTokenList, MultiplefcmTokensValidate, fcmTokenStore, fcmTokenValidate)

# from UserApp.views.user_views import (
#     userList, 
#     createUser, 
#     user,
#     workTypeCounts,
#     createUserUnauthorized,
#     bulkUserAdd
# )



urlpatterns = [
    re_path(r'^fcmTokenStore$', fcmTokenStore),
    re_path(r'^fcmTokenValidate$', fcmTokenValidate),
    re_path(r'^MultiplefcmTokensValidate$', MultiplefcmTokensValidate),
     re_path(r'^FCMTokenList$', FCMTokenList),
    # FCMTokenList
    
]
