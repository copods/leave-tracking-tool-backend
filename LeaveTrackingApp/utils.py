from LeaveTrackingApp.models import Leave, RuleSet, LeaveType
from django.db.models import Q
from LeaveTrackingApp.serializers import LeaveSerializer
from UserApp.models import User
from datetime import date, datetime
import calendar


def getYearLeaveStats(user_id, year_range):
    try:
        user = User.objects.get(id=user_id)
        doj = user.date_of_joining
        yearly_quarters = getYearlyQuarters(doj, year_range)
        year = list(yearly_quarters.keys())[0]
        start_date = yearly_quarters[year][0]['start_date']
        end_date = yearly_quarters[year][3]['end_date']

        user_leaves_for_year = Leave.objects.filter(
            Q(user__id=user_id) &
            (
                (Q(start_date__gte=start_date) & Q(start_date__lt=end_date)) | Q(end_date__gte=start_date)
            )
        )

        quarterly_leave_types = LeaveType.objects.exclude(rule_set__duration="None").values_list('name', flat=True)
        yearly_leave_types = LeaveType.objects.filter(Q(rule_set__duration="None") & ~Q(rule_set__name="miscellaneous_leave")).values_list('name', flat=True)

        year_leave_stats = {
            'year': f'{year}-{int(year) + 1}',
            'yearly_leaves': [],
            'quarterly_leaves': [],
        }
        for leave_type in quarterly_leave_types:
            year_leave_stats[f'{leave_type}_taken'] = 0
            year_leave_stats[f'total_{leave_type}'] = 0

        # Calculate yearly leave statistics
        for leave_type in yearly_leave_types:
            yearly_leave_obj = {}
            leaves = user_leaves_for_year.filter(
                Q(leave_type__name=leave_type) &
                (
                    (Q(start_date__gte=start_date) & Q(start_date__lt=end_date)) | Q(end_date__gte=start_date)
                )
            )
            if leaves:
                leaves_data = LeaveSerializer(leaves, many=True).data
                leave_days = []
                for leave in leaves_data:
                    leave_days.extend(leave['day_details'])
                leave_days.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
                #the case where leave overlapped two years, filter off day details array accordingly
                leave_days = [
                    day for day in leave_days
                    if start_date <= datetime.strptime(day['date'], "%Y-%m-%d").date() < end_date
                ]

                yearly_leave_obj['leave_type'] = leave_type
                yearly_leave_obj['daysTaken'] = len(leave_days)
                yearly_leave_obj['totalDays'] = LeaveType.objects.get(name=leave_type).rule_set.max_days_allowed
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
                max_days = LeaveType.objects.get(name=leave_type).rule_set.max_days_allowed
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
                (
                    (Q(start_date__gte=start_date) & Q(start_date__lt=end_date)) | Q(end_date__gte=start_date)
                )
            ).order_by('start_date')
            leave_requests = LeaveSerializer(leave_requests, many=True).data
            leave_days = []
            for leave in leave_requests:
                day_details = leave['day_details']
                day_details.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
                for day in day_details:
                    #case where quarterly leave overlapped two years, filter off their days accordingly
                    if start_date <= datetime.strptime(day['date'], "%Y-%m-%d").date() < end_date:
                        leave_days.append({
                            'date': day['date'],
                            'status': leave['status']
                        })

            quarterly_leaves_days_for_year[leave_type] = leave_days
        
        # Calculate quarterly statistics
        for i in range(4):
            quarter_obj = {
                'title': f'Q{i + 1}',
                'months': yearly_quarters[year][i]['months'],
                'unpaid': [0, 0, 0]  #  unpaid days per month -> corresponds to each month for that quarter
            }
            for leave_type in quarterly_leave_types:
                days_in_quarter = []
                # leaves overlapping quarters is handled here -> put days in respective quarter of days array accordingly
                for day in quarterly_leaves_days_for_year[leave_type]:
                    if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']:
                        days_in_quarter.append(day)

                max_days = LeaveType.objects.get(name=leave_type).rule_set.max_days_allowed
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

                year_leave_stats[f'{leave_type}_taken'] += quarter_obj[leave_type]['daysTaken']
                year_leave_stats[f'total_{leave_type}'] += quarter_obj[leave_type]['totalDays']
            
            year_leave_stats['quarterly_leaves'].append(quarter_obj)

        return year_leave_stats

    except Exception as e:
        raise e


def getYearlyQuarters(user_doj, year_range):
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
    
    return years_quarters

def getQuartersUtil(year, doj_date, doj_month):
        quarter_start_dates = [
            date(year, doj_month, doj_date),
            add_months(date(year, doj_month, doj_date), 3),
            add_months(date(year, doj_month, doj_date), 6),
            add_months(date(year, doj_month, doj_date), 9),
        ]

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
            quarters.append(quarter)

        return quarters

def add_months(original_date, months_to_add):
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


def get_onleave_wfh_details(wfh_leaves_data, on_leave_data, curr_date):
    wfh_users = []
    on_leave_users = []
    for leave in wfh_leaves_data:
        for day in leave['day_details']:
            if datetime.strptime(day['date'], "%Y-%m-%d").date() == curr_date:
                wfh_users.append(leave['user'])
                break

    for leave in on_leave_data:
        for day in leave['day_details']:
            if datetime.strptime(day['date'], "%Y-%m-%d").date() == curr_date:
                on_leave_users.append(leave['user'])
                break

    return {
        'date': curr_date,
        'on_leave_count': len(on_leave_users),
        'wfh_count': len(wfh_users),
        'wfh_users': wfh_users,
        'on_leave_users': on_leave_users
    }

def check_leave_overlap(leave_data):
    overlap = False
    start_date = leave_data['start_date']
    end_date = leave_data['end_date']
    # (x>=st and y<=ed) or (x<=st and (y>=st or y<=ed)) or (x>=st and y>=ed) or (x<=st and y>=ed) => x<=ed and y>=st
    earlier_leave = Leave.objects.filter(
        Q(user=leave_data['user']) &
        (Q(start_date__lte=end_date ) & Q(end_date__gte=start_date)) 
    )
    if earlier_leave.exists():
        overlap = True
    return overlap
