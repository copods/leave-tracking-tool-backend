from django.urls import path, re_path
from LeaveTrackingApp.views.holiday_calendar_views import createHolidayCalendar, getHolidayCalendars
from LeaveTrackingApp.views.leaves_views import (
    createLeaveRequest, 
    getLeaveDetails, 
    getLeaveTypes,
    getUserLeaveStats, 
    leavesForApprover, 
    getUserLeaves,
    updateLeaveStatus
)


urlpatterns = [
    re_path(r'^createLeaveRequest$', createLeaveRequest),
    re_path(r'^getLeaveTypes$', getLeaveTypes),
    re_path(r'^leavesForApprover$', leavesForApprover),
    re_path(r'^getUserLeaves$', getUserLeaves),
    re_path(r'^getLeaveDetails/([0-9a-f-]+)$', getLeaveDetails),
    re_path(r'^getUserLeaveStats$', getUserLeaveStats),
    re_path(r'^updateLeaveStatus$', updateLeaveStatus),

    # holiday urls
    re_path(r'^createHolidayCalendar$', createHolidayCalendar),
    re_path(r'^getHolidayCalendars$', getHolidayCalendars)
]
