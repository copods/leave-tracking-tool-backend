from django.urls import path, re_path
from LeaveTrackingApp.views import *


urlpatterns = [
    re_path(r'^createLeaveRequest$', createLeaveRequest),
    re_path(r'^getLeaveTypes$', getLeaveTypes),
    re_path(r'^leavesForApprover$', leavesForApprover),
    re_path(r'^getUserLeaves$', getUserLeaves),
    re_path(r'^getLeaveDetails/([0-9a-f-]+)$', getLeaveDetails),
    re_path(r'^getUserLeaveStats$', getUserLeaveStats),
    re_path(r'^addLeaveStatus$', addLeaveStatus),
    re_path(r'^getOnLeaveAndWFH$', getOnLeaveAndWFH),
    re_path(r'^enableEditLeave$', enableEditLeave),

    # holiday urls
    re_path(r'^createHolidayCalendar$', createHolidayCalendar),
    re_path(r'^getHolidayCalendars$', getHolidayCalendars)
]
