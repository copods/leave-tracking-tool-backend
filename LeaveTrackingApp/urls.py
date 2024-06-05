from django.urls import path, re_path

from LeaveTrackingApp.views.holiday_calendar_views import createHolidayCalendar, getHolidayCalendars
from LeaveTrackingApp.views.leaves_views import createLeaveRequest, getLeaveTypes, leavesForApprover, getUserLeaves

urlpatterns = [
    re_path(r'^createLeaveRequest$', createLeaveRequest),
    re_path(r'^getLeaveTypes$', getLeaveTypes),
    re_path(r'^leavesForApprover$', leavesForApprover),
    re_path(r'^getUserLeaves/([0-9a-f-]+)$', getUserLeaves),

    # holiday urls
    re_path(r'^createHolidayCalendar$', createHolidayCalendar),
    re_path(r'^getHolidayCalendars$', getHolidayCalendars)
]
