from django.urls import re_path

from LeaveTrackingApp.views.leaves_views import createLeaveRequest, getLeaveTypes, getAllLeaves, getUserLeaves
from LeaveTrackingApp.views.holiday_calendar_views import createHolidayCalendar, getHolidayCalendars

urlpatterns = [
    re_path(r'^createLeaveRequest$', createLeaveRequest),
    re_path(r'^getLeaveTypes$', getLeaveTypes),
    re_path(r'^getAllLeaves$', getAllLeaves),
    re_path(r'^getUserLeaves$', getUserLeaves),

    # holiday urls
    re_path(r'^createHolidayCalendar$', createHolidayCalendar),
    re_path(r'^getHolidayCalendars$', getHolidayCalendars),
]
