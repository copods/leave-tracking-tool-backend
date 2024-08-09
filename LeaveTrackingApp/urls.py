from django.urls import path, re_path
from LeaveTrackingApp.views import *


urlpatterns = [
    re_path(r'^createLeaveRequest$', createLeaveRequest),
    re_path(r'^getLeaveTypes$', getLeaveTypes),
    re_path(r'^getLeavesList$', getLeavesList),
    re_path(r'^getLeaveDetails/([0-9a-f-]+)$', getLeaveDetails),
    re_path(r'^getUserLeaveStats$', getUserLeaveStats),
    re_path(r'^getEmployeeLeaveStats/([0-9a-f-]+)$', getEmployeeLeaveStats),
    re_path(r'^addLeaveStatus$', addLeaveStatus),
    re_path(r'^getEmployeeAttendance$', getEmployeeAttendance),
    re_path(r'^enableEditLeave$', enableEditLeave),
    re_path(r'^getUnpaidData$', getUnpaidData),
    re_path(r'^editLeave/([0-9a-f-]+)$', editLeave),

    # holiday urls
    re_path(r'^createHolidayCalendar$', createHolidayCalendar),
    re_path(r'^getHolidayCalendar$', getHolidayCalendar),
    re_path(r'^updateYearCalendar/([0-9a-f-]+)$', updateYearCalendar),

    #leave policy urls
    re_path(r'^createYearPolicy$', createYearPolicy),
    re_path(r'^getYearPolicy$', getYearPolicy),
    re_path(r'^updateYearPolicy/([0-9a-f-]+)$', updateYearPolicy),
    re_path(r'^getLeaveStatusCount$', getLeaveStatusCount)
]
