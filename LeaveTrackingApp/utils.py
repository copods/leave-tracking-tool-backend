from LeaveTrackingApp.models import Leave, RuleSet, LeaveType
from django.db.models import Q
from LeaveTrackingApp.serializers import LeaveSerializer
from UserApp.models import User
from datetime import date, datetime
import calendar

# get user leave statistics 
######### IMP: need to handle the leave which was started in previous quarter and ended in current quarter,
    #########      slice its date details while counting total leaves in quarter 


##for one year
def getYearLeaveStats(user_id, year_range):
    try:
        # Get user's date of joining
        user = User.objects.get(id=user_id)
        doj = user.date_of_joining
        yearly_quarters = getYearlyQuarters(doj, year_range)
        year = list(yearly_quarters.keys())[0]
        start_date = yearly_quarters[year][0]['start_date']
        end_date = yearly_quarters[year][3]['end_date']

        user_leaves_for_year = Leave.objects.filter(
            Q(user__id=user_id) &
            (
                Q(start_date__gte=start_date) &
                Q(start_date__lt=end_date)
            )
        )

        quarterly_leave_types = LeaveType.objects.filter(~Q(rule_set__duration="None")).values_list('name', flat=True)
        yearly_leave_types = RuleSet.objects.filter(Q(duration="None") & ~Q(name="miscellaneous_leave")).values_list('name', flat=True)

        year_leave_stats = {
            'year': f'{year}-{int(year) + 1}',
            'yearly_leaves': [],
            'quarterly_leaves': []
        }

        # Calculate yearly leave statistics
        for leave_type in yearly_leave_types:
            yearly_leave_obj = {}
            leave = user_leaves_for_year.filter(
                Q(leave_type__name=leave_type) &
                Q(start_date__gte=start_date) &
                Q(start_date__lt=end_date)
            ).first()  # taking first because there should be only one in a year

            if leave:
                # Serialize the leave to get day details
                leave = LeaveSerializer(leave).data
                leave_days = leave['day_details']
                yearly_leave_obj['leave_type'] = leave_type
                yearly_leave_obj['daysTaken'] = len(leave_days)
                yearly_leave_obj['totalDays'] = RuleSet.objects.get(name=leave_type).max_days_allowed
                yearly_leave_obj['remaining'] = max(yearly_leave_obj['totalDays'] - yearly_leave_obj['daysTaken'], 0)
                yearly_leave_obj['dayDetails'] = [
                    {
                        'id': day['id'],
                        'date': day['date'],
                        'isHalfDay': day['is_half_day']
                    }
                    for day in leave_days
                ]
            else:
                max_days = RuleSet.objects.get(name=leave_type).max_days_allowed
                yearly_leave_obj = {
                    'leave_type': leave_type,
                    'daysTaken': 0,
                    'totalDays': max_days,
                    'remaining': max_days,
                    'dayDetails': []
                }

            year_leave_stats['yearly_leaves'].append(yearly_leave_obj)


        # Organize quarterly leaves and day details
        quarterly_leaves_days_for_year = {leave_type: [] for leave_type in quarterly_leave_types}

        for leave_type in quarterly_leave_types:
            leave_requests = user_leaves_for_year.filter(
                Q(leave_type__name=leave_type) &
                Q(start_date__gte=start_date) &
                Q(start_date__lt=end_date)
            ).order_by('start_date')
            # Serialize each leave request to get day details
            leave_requests = LeaveSerializer(leave_requests, many=True).data
            for leave_request in leave_requests:
                days = leave_request['day_details']
                for day in days:
                    quarterly_leaves_days_for_year[leave_type].append({
                        'date': day['date'],
                        'status': leave_request['status']
                    })
        
        # Calculate quarterly statistics
        for i in range(4):
            quarter_obj = {
                'title': f'Q{i + 1}',
                'months': yearly_quarters[year][i]['months'],
                'unpaid': [0, 0, 0]  #  unpaid days per month -> corresponds to each month for that quarter
            }
            for leave_type in quarterly_leave_types:
                days_in_quarter = []
                for day in quarterly_leaves_days_for_year[leave_type]:
                    if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']:
                        days_in_quarter.append(day)

                max_days = RuleSet.objects.get(name=leave_type).max_days_allowed
                quarter_obj[leave_type] = {
                    'daysTaken': len(days_in_quarter),
                    'totalDays': max_days,
                    'remaining': max(max_days - len(days_in_quarter), 0),
                    'dayDetails': days_in_quarter
                }

                unpaid_for_leave_type = calculateUnpaidLeaves(
                    [datetime.strptime(day['date'], "%Y-%m-%d") for day in days_in_quarter],
                    quarter_obj[leave_type]['totalDays'],
                    yearly_quarters[year][i]['months']
                )

                quarter_obj['unpaid'] = [sum(x) for x in zip(quarter_obj['unpaid'], unpaid_for_leave_type)]

            year_leave_stats['quarterly_leaves'].append(quarter_obj)

        return year_leave_stats

    except Exception as e:
        raise e





def getYearlyQuarters(user_doj, year_range):
    print(user_doj, year_range)
    doj_year = user_doj.year
    doj_month = user_doj.month
    doj_date = user_doj.day
    if(year_range):
        start_year, last_year = year_range.split('-')
        start_year = int(start_year)
        last_year = int(last_year)-1
        if start_year < doj_year:
            raise ValueError('Invalid start year in range')
    else:
        last_year = start_year = datetime.now().date().year if datetime.now().date().month >= doj_month else datetime.now().date().year - 1
    years_quarters = {
        str(year) : getQuartersUtil(year,doj_date,doj_month)
        for year in range(start_year, last_year+1)
    }
    print('here')
    return years_quarters

def getQuartersUtil(year, doj_date, doj_month):
        print('here bhai here')
        quarter_start_dates = [
            date(year, doj_month, doj_date),
            add_months(date(year, doj_month, doj_date), 3),
            add_months(date(year, doj_month, doj_date), 6),
            add_months(date(year, doj_month, doj_date), 9),
        ]
        print(quarter_start_dates, '\n\n\n')

        quarters = []
        for start_date in quarter_start_dates:
            end_date = add_months(start_date, 3)
            months = [(start_date.month + i - 1) % 12 + 1 for i in range(3)]
            month_abbrs = [calendar.month_abbr[month] for month in months]
            quarter = {
                'start_date': start_date,
                'end_date': end_date,
                'months': month_abbrs,
            }
            print(f"Calculated quarter: {quarter}")
            quarters.append(quarter)

        print('here in here')
        return quarters

def add_months(original_date, months_to_add):
    print('here in calculation')
    year, month = divmod(original_date.year*12 + original_date.month + months_to_add, 12)
    return original_date.replace(year=year, month=month % 12, day=original_date.day)

def calculateUnpaidLeaves(days, max_days_allowed, months):
    days.sort()
    taken = 0
    unpaid = [0,0,0]
    for day in days:
        taken += 1
        if(taken > max_days_allowed):
            unpaid[months.index(calendar.month_abbr[day.month])] += 1
    return unpaid





#  object format:
#
# {
#     year: 2023-2024,
#     yearly_leaves_stats:[
#         {
#             leave_type: maternity_leave,
#             daysTaken: 0,
#             totalDays: 0,
#             remaining: 0,
#             dayDetails: []
#         },
#         ...
#     ],
#     quarterly_leaves_stats: [
#         {
#             title: Q1,
#             months: [],
#             unpaid : [int,int,int]
#             leave_type1: {
#                 daysTaken: 0,
#                 totalDays: 0,
#                 remaining: 0,
#                 dayDetails: []
#             },
#             leave_type2: {
#                 daysTaken: 0,
#                 totalDays: 0,
#                 remaining: 0,
#                 dayDetails: []
#             }
#             ...
#         },
#         {
#             title: Q2,
#             months: [],
#             unpaid : [int,int,int]
#             leave_type1: {
#                 daysTaken: 0,
#                 totalDays: 0,
#                 remaining: 0,
#                 dayDetails: []
#             },
#             ...
#         },
#         ...
#     ]
# }