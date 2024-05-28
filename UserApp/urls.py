from django.urls import re_path

from UserApp.views.user_views import userList, createUser, user

urlpatterns = [
    re_path(r'^users$', userList),
    re_path(r'^createUser$', createUser),
    re_path(r'^user/([0-9a-f-]+)$', user)
]
