from django.urls import re_path

from LeaveTrackingApp.views.leaves_views import createLeaveRequest, getLeaveTypes, getAllLeaves, getUserLeaves

urlpatterns = [
    re_path(r'^createLeaveRequest$', createLeaveRequest),
    re_path(r'^getLeaveTypes$', getLeaveTypes),
    re_path(r'^getAllLeaves$', getAllLeaves),
    re_path(r'^getUserLeaves$', getUserLeaves),
]