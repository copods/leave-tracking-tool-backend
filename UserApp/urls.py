from django.urls import re_path
from UserApp.views.user_views import (
    userList, 
    createUser, 
    user,
    workTypeCounts,
    createUserUnauthorized,
    bulkUserAdd,
)
from UserApp.views.authentication_views import (
    googleSignIn, 
    adminPanelGoogleSignIn, 
    accessTokenValidate, 
    refreshToken
)
from UserApp.views.role_department_views import role, department

urlpatterns = [
    # Authentication APIs URL
    re_path(r'^googleSignIn$', googleSignIn),
    re_path(r'^adminPanelGoogleSignIn$', adminPanelGoogleSignIn),
    re_path(r'^accessTokenValidate$', accessTokenValidate),
    re_path(r'^refreshToken$', refreshToken),

    # users APIs URL
    re_path(r'^users$', userList),
    re_path(r'^createUser$', createUser),
    re_path(r'^user/([0-9a-f-]+)$', user),
    re_path(r'^workTypeCounts$', workTypeCounts),
    re_path(r'^createFirstUser$', createUserUnauthorized),
    re_path(r'^bulkUserAdd$', bulkUserAdd),

    # roles and department APIs URL
    re_path(r'^roles$', role),
    re_path(r'^departments$', department),
]
