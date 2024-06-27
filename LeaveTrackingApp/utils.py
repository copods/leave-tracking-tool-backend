from LeaveTrackingApp.models import Leave, RuleSet, LeaveType
from django.db.models import Q
from LeaveTrackingApp.serializers import LeaveUtilSerializer
from UserApp.models import User
from datetime import date, datetime, timedelta
import calendar


def user_leave_stats_hr_view(user_id, year_range):
    '''
        Algo:
            1. Get user doj
            2. Get yearly quarters data (start date and end dates, months etc.)
            3. Filter the leaves for the current year
            4. Get leave summary for the year
            5. Now calculate the leaves data for each quarter in the year
                5.1. Get leave summary for each quarter
                5.2. Filter off the leave data for each quarter
                5.3. Filter off the days of those leaves for each quarter
                5.4. Find which leaves are paid and which are unpaid, also have a count of unpaid 
            6. Return the yearly leave stats

            Edge cases to consider:
                1. Leaves for the current year are not present
                2. consider miscellaneous leaves into pto and calculate unpaid count accordingly
                3. for pto (which can be combination of leaves and wfh), calculate unpaid count accordingly
                4. for yearly leave types (marriage, maternity, etc.), calculate unpaid count accordingly and dont include in leave summary
                   which shows only pto leaves and wfh taken in a quarter or the full year.
    '''
    try:
        user = User.objects.get(id=user_id)
        doj = user.date_of_joining
        yearly_quarters = get_quarters(doj, year_range)
        year = list(yearly_quarters.keys())[0]
        start_date = yearly_quarters[year][0]['start_date']
        end_date = yearly_quarters[year][3]['end_date']

        user_leaves_for_year = Leave.objects.filter(
            Q(user__id=user_id) & ~Q(status="W") & 
            ( (Q(start_date__lte=end_date) & Q(end_date__gte=start_date)) )
        ).order_by('start_date')

        leaves_data = LeaveUtilSerializer(user_leaves_for_year, many=True).data
        leave_summary = get_leave_summary(leaves_data, start_date, end_date, yearly=True)

        year_leave_stats = {
            'year': f'{year}-{int(year) + 1}',
            'pto_taken' : leave_summary['leaves_taken'],
            'total_pto': leave_summary['total_leaves'],
            'wfh_taken': leave_summary['wfh_taken'],
            'total_wfh': leave_summary['total_wfh'],
            'data': []
        }

        leave_types = LeaveType.objects.values_list('name', flat=True).distinct()
        taken_unpaid_obj = {
            type: {
                'leaves_taken' : 0,
                'unpaid' : 0
            }
            for type in leave_types
        }
        quarterly_leave_types = user_leaves_for_year.filter(Q(leave_type__rule_set__duration="quarterly") | Q(leave_type__rule_set__name="miscellaneous_leave")).values_list('leave_type__name', flat=True).distinct()
        miscellaneous_types = user_leaves_for_year.filter(Q(leave_type__rule_set__name="miscellaneous_leave")).values_list('leave_type__name', flat=True).distinct()
        
        # Calculate quarterly statistics
        for i in range(4):
            quarter_obj = {
                'title': f'Q{i + 1}',
                'months': yearly_quarters[year][i]['months'],
                'total_unpaid': 0,
                'quarter_summary': {},
                'leaves': []
            }
            
            leaves_for_curr_quarter = LeaveUtilSerializer(
                user_leaves_for_year.filter(
                    Q(start_date__lte=yearly_quarters[year][i]['end_date']) & Q(end_date__gte=yearly_quarters[year][i]['start_date'])
                ).order_by('start_date'), many=True
            ).data
        
            quarter_obj['quarter_summary'] = get_leave_summary(leaves_for_curr_quarter, yearly_quarters[year][i]['start_date'], yearly_quarters[year][i]['end_date'])

            for leave in leaves_for_curr_quarter:
                # leaves overlapping quarters is handled here -> put days in respective quarter accordingly in respective leave
                days_in_quarter = [
                    day
                    for day in leave['day_details']
                    if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']
                ]

                if leave["leave_type"] == 'paternity_leave':
                    print('\n\n', leave['leave_type'], '->', len(days_in_quarter)) 
                
                if leave['leave_type'] in miscellaneous_types:
                    max_days_allowed = LeaveType.objects.get(name='pto').rule_set.max_days_allowed
                    temp_leaves_taken = taken_unpaid_obj['pto']['leaves_taken']
                    x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_days_allowed, max_wfh_days=0)
                    taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                    taken_unpaid_obj['pto']['unpaid'] += x[1]

                else:
                    if leave['leave_type'] == 'pto':
                        max_leave_days = LeaveType.objects.get(name='pto').rule_set.max_days_allowed
                        max_wfh_days = LeaveType.objects.get(name='wfh').rule_set.max_days_allowed
                        x = find_unpaid_days(days_in_quarter, leaves_taken=taken_unpaid_obj['pto']['leaves_taken'], wfh_taken=taken_unpaid_obj['wfh']['leaves_taken'], max_leave_days=max_leave_days, max_wfh_days=max_wfh_days)
                        taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                        taken_unpaid_obj['wfh']['leaves_taken'] += x[2]
                    else: 
                        max_days_allowed = LeaveType.objects.get(name=leave['leave_type']).rule_set.max_days_allowed
                        temp_leaves_taken = taken_unpaid_obj[leave['leave_type']]['leaves_taken']
                        x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_days_allowed, max_wfh_days=0)
                        taken_unpaid_obj[leave['leave_type']]['leaves_taken'] += x[3]
                        #reducing available pto if these yearly leaves are taken in the current quarter
                        max_pto = LeaveType.objects.get(name='pto').rule_set.max_days_allowed
                        taken_unpaid_obj['pto']['leaves_taken'] += min(max_pto, taken_unpaid_obj[leave['leave_type']]['leaves_taken'])

                    taken_unpaid_obj[leave['leave_type']]['unpaid'] += x[1]

                leave['day_details'] = x[0]

                temp = {
                    'id': leave['id'],
                    'start_date': leave['start_date'],
                    'end_date': leave['end_date'],
                    'type': leave['leave_type'],
                    'status': leave['status'],
                    'unpaid_count': x[1]
                }
                quarter_obj['total_unpaid'] += x[1]       
                quarter_obj['leaves'].append(temp)
            
            if 'pto' in taken_unpaid_obj.keys():
                taken_unpaid_obj['pto']['unpaid'] = taken_unpaid_obj['pto']['leaves_taken'] = 0
            if 'wfh' in taken_unpaid_obj.keys():
                taken_unpaid_obj['wfh']['unpaid'] = taken_unpaid_obj['wfh']['leaves_taken'] = 0
            for lt in quarterly_leave_types:
                taken_unpaid_obj[lt]['unpaid'] = taken_unpaid_obj[lt]['leaves_taken'] = 0

            year_leave_stats['data'].append(quarter_obj)

        return year_leave_stats

    except Exception as e:
        raise e

def user_leave_stats_user_view(user_id, year_range):
    '''
        Algo:
            1. Get user doj
            2. Get yearly quarters object (having start, end dates, months etc.)
            3. Filter off user's leaves for that year
            4. prepare leave days for quarterly leaves and start and end dates for yearly leaves
            5. find number of unpaid leaves
            6. return leave stats
    '''
    try:
        user = User.objects.get(id=user_id)
        doj = user.date_of_joining
        yearly_quarters = get_quarters(doj, year_range)
        year = list(yearly_quarters.keys())[0]
        start_date = yearly_quarters[year][0]['start_date']
        end_date = yearly_quarters[year][3]['end_date']

        user_leaves_for_year = Leave.objects.filter(
            Q(user__id=user_id) & ~Q(status='W') & 
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date) 
        )

        data = LeaveUtilSerializer(user_leaves_for_year, many=True).data
        leave_summary = get_leave_summary(data, start_date, end_date, yearly=True)
        year_leave_stats = {
            'year': f'{year}-{int(year) + 1}',
            'pto_taken' : leave_summary['leaves_taken'],
            'total_pto': leave_summary['total_leaves'],
            'wfh_taken': leave_summary['wfh_taken'],
            'total_wfh': leave_summary['total_wfh'],
            'data': [],
        }

        quarterly_leave_types = LeaveType.objects.filter(~Q(rule_set__duration="None") | Q(rule_set__name="miscellaneous_leave")).values_list('name', flat=True)
        yearly_leave_types = LeaveType.objects.filter(Q(rule_set__duration="None") & ~Q(rule_set__name="miscellaneous_leave")).values_list('name', flat=True)


        # Organize quarterly leaves and day details
        leave_wfh_for_year = {
            'leaves': [],
            'wfh': []
        }

        for leave_type in quarterly_leave_types:
            leave_requests = user_leaves_for_year.filter(leave_type__name=leave_type).order_by('start_date')
            leave_requests = LeaveUtilSerializer(leave_requests, many=True).data
            for leave in leave_requests:
                day_details = leave['day_details']
                for day in day_details:
                    #case where quarterly leave overlapped two years, filter off their days accordingly
                    if start_date <= datetime.strptime(day['date'], "%Y-%m-%d").date() < end_date:
                        temp_day = {
                            'date': day['date'],
                            'status': leave['status'],
                            'is_half_day': day['is_half_day'],
                            'type': day['type']
                        }
                        if day['type'] == 'wfh':
                            leave_wfh_for_year['wfh'].append(temp_day)
                        else:
                            leave_wfh_for_year['leaves'].append(temp_day)

        # Calculate quarterly statistics
        for i in range(4):
            quarter_obj = {
                'title': f'Q{i + 1}',
                'months': yearly_quarters[year][i]['months'],
                'unpaid': []  
            }

            #check if any yearly leave overlaps with this quarter
            for leave_type in yearly_leave_types:
                leave_request = user_leaves_for_year.filter(leave_type__name=leave_type, start_date__lte=yearly_quarters[year][i]['end_date'], end_date__gte=yearly_quarters[year][i]['start_date']).order_by('start_date').first()
                leave_request = LeaveUtilSerializer(leave_request).data
                if leave_request:
                    quarter_obj[leave_type] = {
                        'start_date': leave_request['start_date'],
                        'end_date': leave_request['end_date'],
                    }

            leave_days_in_curr_quarter = []
            wfh_days_in_curr_quarter = []

            # leaves overlapping quarters is handled here -> put days in respective quarter of days array accordingly
            for day in leave_wfh_for_year['leaves']:
                if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']:
                        leave_days_in_curr_quarter.append(day)

            for day in leave_wfh_for_year['wfh']:
                if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']:
                    wfh_days_in_curr_quarter.append(day)

            leave_days_in_curr_quarter.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
            wfh_days_in_curr_quarter.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))

            max_days = list(LeaveType.objects.filter(Q(name='pto') | Q(name='wfh')).values_list('rule_set__max_days_allowed', flat=True))

            count=0
            for day in leave_days_in_curr_quarter:
                count += 1
                if count > max_days[0]:
                    quarter_obj['unpaid'].append(day)
            count=0
            for day in wfh_days_in_curr_quarter:
                count += 1
                if count > max_days[1]:
                    quarter_obj['unpaid'].append(day)

            quarter_obj['leaves'] = {
                'days_taken': len(leave_days_in_curr_quarter),
                'total_days': max_days[0],
                'remaining': max(max_days[0] - len(leave_days_in_curr_quarter), 0),
                'day_details': leave_days_in_curr_quarter
            }
            quarter_obj['wfh'] = {
                'days_taken': len(wfh_days_in_curr_quarter),
                'total_days': max_days[1],
                'remaining': max(max_days[1] - len(wfh_days_in_curr_quarter), 0),
                'day_details': wfh_days_in_curr_quarter
            }

            year_leave_stats['data'].append(quarter_obj)

        return year_leave_stats

    except Exception as e:
        raise e


def get_quarters(user_doj, year_range):
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
        str(year) : get_quarters_util(year,doj_date,doj_month)
        for year in range(start_year, last_year+1)
    }
    
    return years_quarters

def get_quarters_util(year, doj_date, doj_month):
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
                'end_date': end_date-timedelta(days=1),
                'months': month_abbrs,
            }
            quarters.append(quarter)

        return quarters

def add_months(original_date, months_to_add):
    year, month = divmod(original_date.year*12 + original_date.month + months_to_add, 12)
    return original_date.replace(year=year, month=month % 12, day=original_date.day)

def get_monthwise_unpaid(days, max_days_allowed, months):
    days.sort()
    taken = 0
    unpaid = [0,0,0]
    for day in days:
        taken += 1
        if(taken > max_days_allowed):
            unpaid[months.index(calendar.month_abbr[day.month])] += 1
    return unpaid

def find_unpaid_days(days, leaves_taken, wfh_taken, max_leave_days, max_wfh_days):
    unpaid = 0
    modified_days = days
    leave_count = wfh_count = 0
    for day in modified_days:
        if day['type'] != 'wfh':
            leave_count += 0.5 if day['is_half_day'] else 1
            if leaves_taken + leave_count > max_leave_days:
                unpaid += 1
                day['unpaid'] = True
            else:
                day['unpaid'] = False
        else:
            wfh_count += 1 if day['is_half_day'] else 1
            if wfh_taken + wfh_count > max_wfh_days:
                unpaid += 1
                day['unpaid'] = True
            else:
                day['unpaid'] = False

    return modified_days, unpaid, wfh_taken+wfh_count, leaves_taken+leave_count

def get_leave_summary(leaves_data, start_date, end_date, yearly=False):
    leave_summary = {
        'total_leaves': 0,
        'leaves_taken': 0,
        'total_wfh': 0,
        'wfh_taken': 0
    }
    max_days = list(LeaveType.objects.filter(Q(name='pto') | Q(name='wfh')).values_list('rule_set__max_days_allowed', flat=True))
    leave_summary['total_leaves'] = max_days[0]*4 if yearly else max_days[0]
    leave_summary['total_wfh'] = max_days[1]*4 if yearly else max_days[1]

    quarterly_leave_types = LeaveType.objects.filter(Q(rule_set__duration='quarterly') | Q(rule_set__name='miscellaneous_leave')).values_list('name', flat=True)

    for leave in leaves_data:
        for day in leave['day_details']:
            if datetime.strptime(day['date'], "%Y-%m-%d").date() >= start_date and datetime.strptime(day['date'], "%Y-%m-%d").date() <= end_date:
                if not day['type'] in quarterly_leave_types:
                    continue
                elif day['type'] == 'wfh':
                    leave_summary['wfh_taken'] += 0.5 if day['is_half_day'] else 1
                else:
                    leave_summary['leaves_taken'] += 0.5 if day['is_half_day'] else 1
    
    return leave_summary


def get_users_for_day(leaves_data, curr_date, wfh=False):
    users = []
    wfh_id = LeaveType.objects.get(name='wfh').id

    for leave in leaves_data:
        for day in leave['day_details']:
            if datetime.strptime(day['date'], "%Y-%m-%d").date() == curr_date:
                user = {
                    'name': leave['name'], 
                    'profile_pic': leave['profilePicture'], 
                    'leave_type': leave['leave_type'],
                    'date_range': f'{leave["start_date"]} - {leave["end_date"]}'
                }
                if wfh :
                    if day['type']==wfh_id:
                        users.append(user)
                else:
                    if not day['type']==wfh_id:
                        users.append(user)
                break
    data = {
        'date': curr_date,
        'users_count': len(users),
        'users': users
    }
    return data

def check_leave_overlap(leave_data):
    overlap = False
    start_date = leave_data['start_date']
    end_date = leave_data['end_date']
    earlier_leave = Leave.objects.filter(
        Q(user=leave_data['user']) &
        (Q(start_date__lte=end_date ) & Q(end_date__gte=start_date)) 
    )
    if earlier_leave.exists():
        overlap = True
    return overlap

def get_unpaid_data(user, curr_year, month):
    try:

        yearly_quarters = get_quarters(user.date_of_joining, None)
        year = list(yearly_quarters.keys())[0]
        start_date = yearly_quarters[year][0]['start_date']
        end_date = yearly_quarters[year][3]['end_date']

        if year==curr_year and start_date.month > month:
            return []
        
        user_leaves_for_year = Leave.objects.filter(user=user, start_date__lte=end_date, end_date__gte=start_date).order_by('start_date')

        leave_types = LeaveType.objects.values_list('name', flat=True).distinct()
        taken_unpaid_obj = {
            type: {
                'leaves_taken' : 0,
                'unpaid' : 0
            }
            for type in leave_types
        }
        quarterly_leave_types = user_leaves_for_year.filter(Q(leave_type__rule_set__duration="quarterly") | Q(leave_type__rule_set__name="miscellaneous_leave")).values_list('leave_type__name', flat=True).distinct()
        miscellaneous_types = user_leaves_for_year.filter(Q(leave_type__rule_set__name="miscellaneous_leave")).values_list('leave_type__name', flat=True).distinct()
        
        unpaid_days_for_month = []

        for i in range(4):
            leaves_for_curr_quarter = LeaveUtilSerializer(
                user_leaves_for_year.filter(
                    Q(start_date__lte=yearly_quarters[year][i]['end_date']) & Q(end_date__gte=yearly_quarters[year][i]['start_date'])
                ).order_by('start_date'), many=True
            ).data

            for leave in leaves_for_curr_quarter:
                # leaves overlapping quarters is handled here -> put days in respective quarter accordingly in respective leave
                days_in_quarter = [
                    day
                    for day in leave['day_details']
                    if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']
                ]
                
                if leave['leave_type'] in miscellaneous_types:
                    max_days_allowed = LeaveType.objects.get(name='pto').rule_set.max_days_allowed
                    temp_leaves_taken = taken_unpaid_obj['pto']['leaves_taken']
                    
                    x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_days_allowed, max_wfh_days=0)
                    taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                    taken_unpaid_obj['pto']['unpaid'] += x[1]

                else:
                    if leave['leave_type'] == 'pto':
                        max_leave_days = LeaveType.objects.get(name='pto').rule_set.max_days_allowed
                        max_wfh_days = LeaveType.objects.get(name='wfh').rule_set.max_days_allowed

                        x = find_unpaid_days(days_in_quarter, leaves_taken=taken_unpaid_obj['pto']['leaves_taken'], wfh_taken=taken_unpaid_obj['wfh']['leaves_taken'], max_leave_days=max_leave_days, max_wfh_days=max_wfh_days)
                        taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                        taken_unpaid_obj['wfh']['leaves_taken'] += x[2]
                    else: 
                        max_days_allowed = LeaveType.objects.get(name=leave['leave_type']).rule_set.max_days_allowed
                        temp_leaves_taken = taken_unpaid_obj[leave['leave_type']]['leaves_taken']

                        x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_days_allowed, max_wfh_days=0)
                        taken_unpaid_obj[leave['leave_type']]['leaves_taken'] += x[3]

                    taken_unpaid_obj[leave['leave_type']]['unpaid'] += x[1]

                leave['day_details'] = x[0]

                for day in leave['day_details']:
                    if day['unpaid'] and calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] == month:
                        unpaid_days_for_month.append(day['date'])
            
            for lt in quarterly_leave_types:
                taken_unpaid_obj[lt]['unpaid'] = taken_unpaid_obj[lt]['leaves_taken'] = 0

        return unpaid_days_for_month

    except Exception as e:
        raise e
