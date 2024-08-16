from LeaveTrackingApp.models import Leave, RuleSet, LeaveType
from django.db.models import Q
from LeaveTrackingApp.serializers import LeaveUtilSerializer
from UserApp.models import User
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
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
                    if (yearly_quarters[year][i]['start_date'] <= datetime.strptime(day['date'], "%Y-%m-%d").date() <= yearly_quarters[year][i]['end_date']) and not day['is_withdrawn']
                ]

                max_pto = LeaveType.objects.get(name='pto').rule_set.max_days_allowed

                if leave['leave_type'] in miscellaneous_types:
                    temp_leaves_taken = taken_unpaid_obj['pto']['leaves_taken']
                    x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_pto, max_wfh_days=0)
                    taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                    taken_unpaid_obj['pto']['unpaid'] += x[1]

                else:
                    if leave['leave_type'] in ['pto', 'wfh']:
                        max_wfh_days = LeaveType.objects.get(name='wfh').rule_set.max_days_allowed
                        x = find_unpaid_days(days_in_quarter, leaves_taken=taken_unpaid_obj['pto']['leaves_taken'], wfh_taken=taken_unpaid_obj['wfh']['leaves_taken'], max_leave_days=max_pto, max_wfh_days=max_wfh_days)
                        taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                        taken_unpaid_obj['wfh']['leaves_taken'] += x[2]
                    else: 
                        max_days_allowed = LeaveType.objects.get(name=leave['leave_type']).rule_set.max_days_allowed
                        temp_leaves_taken = taken_unpaid_obj[leave['leave_type']]['leaves_taken']
                        x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_days_allowed, max_wfh_days=0)
                        taken_unpaid_obj[leave['leave_type']]['leaves_taken'] += x[3]
                        taken_unpaid_obj['pto']['leaves_taken'] += min(max_pto, x[3] - x[1]) #reducing available pto if these yearly leaves are taken in the current quarter

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
            Q(user__id=user_id) & ~Q(status__in=['W','R']) & 
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
            'yearly_leaves': [],
            'data': [],
        }

        quarterly_leave_types = LeaveType.objects.filter(~Q(rule_set__duration="None") | Q(rule_set__name="miscellaneous_leave")).values_list('name', flat=True)
        yearly_leave_types = LeaveType.objects.filter(Q(rule_set__duration="None") & ~Q(rule_set__name="miscellaneous_leave")).values_list('name', flat=True)
        rulesets = RuleSet.objects.all()

        ######TODO: handle the case when yearly leaves exceed the max allowed, they must be counted into quarterly leaves######

        #find yearly leaves taken
        for leave_type in yearly_leave_types:
            leave_request = user_leaves_for_year.filter(leave_type__name=leave_type, status='A').order_by('start_date').first()
            if leave_request:
                leave_request = LeaveUtilSerializer(leave_request).data
                max_days = rulesets.filter(name=leave_type).first().max_days_allowed
                year_leave_stats['yearly_leaves'].append({
                    'leaveType': leave_request['leave_type'],
                    'daysTaken' : len(leave_request['day_details']),
                    'totalDays': max_days,
                    'remaining': max(0, max_days - len(leave_request['day_details'])),
                    'dayDetails': [{'id': day['id'], 'date': day['date']} for day in leave_request['day_details']]
                })

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
                    if start_date <= datetime.strptime(day['date'], "%Y-%m-%d").date() <= end_date and not day['is_withdrawn']:
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

            leave_days_in_curr_quarter = [day for day in leave_wfh_for_year['leaves'] if yearly_quarters[year][i]['start_date'] <= datetime.strptime(day['date'], "%Y-%m-%d").date() <= yearly_quarters[year][i]['end_date']]
            wfh_days_in_curr_quarter = [day for day in leave_wfh_for_year['wfh'] if yearly_quarters[year][i]['start_date'] <= datetime.strptime(day['date'], "%Y-%m-%d").date() <= yearly_quarters[year][i]['end_date']]

            max_days = list(rulesets.filter(Q(name='pto') | Q(name='wfh')).values_list('max_days_allowed', flat=True))
            
            cnt=0
            for day in leave_days_in_curr_quarter:
                cnt += 0.5 if day['is_half_day'] else 1
                if cnt > max_days[0]:
                    quarter_obj['unpaid'].append(day)
            cnt=0
            for day in wfh_days_in_curr_quarter:
                cnt += 0.5 if day['is_half_day'] else 1
                if cnt > max_days[1]:
                    quarter_obj['unpaid'].append(day)
            
            quarter_obj['unpaid'].sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
            
            leave_days_cnt = sum(0.5 if day['is_half_day'] else 1 for day in leave_days_in_curr_quarter)
            wfh_days_cnt = sum(0.5 if day['is_half_day'] else 1 for day in wfh_days_in_curr_quarter)
            quarter_obj['leaves'] = {
                'days_taken': leave_days_cnt,
                'total_days': max_days[0],
                'remaining': max(max_days[0] - leave_days_cnt, 0),
                'day_details': leave_days_in_curr_quarter
            }
            quarter_obj['wfh'] = {
                'days_taken': wfh_days_cnt,
                'total_days': max_days[1],
                'remaining': max(max_days[1] - wfh_days_cnt, 0),
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
    quarter_start_dates = [date(year, doj_month, doj_date) + relativedelta(months=i) for i in range(0, 12, 3)]
    quarters = [
        {
            'start_date': start_date,
            'end_date': start_date + relativedelta(months=3) - timedelta(days=1),
            'months': [calendar.month_abbr[(start_date.month+i-1)%12+1] for i in range(3)],
        } 
        for start_date in quarter_start_dates
    ]
    return quarters

def get_monthwise_unpaid(days, max_days_allowed, months):
    days.sort()
    taken = 0
    unpaid = [0,0,0]
    for day in days:
        if day['is_half_day']:
            taken += 0.5
        else:
            taken += 1
        if(taken > max_days_allowed):
            unpaid[months.index(calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month])] += 1
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

    return modified_days, unpaid, wfh_count, leave_count

def get_leave_summary(leaves_data, start_date, end_date, yearly=False):
    max_days = list(LeaveType.objects.filter(Q(name='pto') | Q(name='wfh')).values_list('rule_set__max_days_allowed', flat=True))
    leave_summary = {
        'total_leaves': max_days[0]*4 if yearly else max_days[0],
        'leaves_taken': 0,
        'total_wfh': max_days[1]*4 if yearly else max_days[1],
        'wfh_taken': 0
    }
    quarterly_leave_types = LeaveType.objects.filter(Q(rule_set__duration='quarterly') | Q(rule_set__name='miscellaneous_leave')).values_list('name', flat=True)
    for leave in leaves_data:
        if leave['status'] == 'A':
            for day in leave['day_details']:
                if datetime.strptime(day['date'], "%Y-%m-%d").date() >= start_date and datetime.strptime(day['date'], "%Y-%m-%d").date() <= end_date and not day['is_withdrawn']:
                    if not day['type'] in quarterly_leave_types:
                        continue
                    elif day['type'] == 'wfh':
                        leave_summary['wfh_taken'] += 0.5 if day['is_half_day'] else 1
                    else:
                        leave_summary['leaves_taken'] += 0.5 if day['is_half_day'] else 1
    return leave_summary


def get_users_for_day(leaves_data, curr_date, wfh=False):
    users = []
    for leave in leaves_data:
        for day in leave['day_details']:
            if datetime.strptime(day['date'], "%Y-%m-%d").date() == curr_date:
                user = {
                    'name': leave['name'], 
                    'profile_pic': leave['profilePicture'], 
                    'leave_type': leave['leave_type'],
                    'date_range': f'{leave["start_date"]} - {leave["end_date"]}'
                }
                if wfh:
                    if day['type']=='wfh':
                        users.append(user)
                else:
                    if not day['type']=='wfh':
                        users.append(user)
                break
    data = {
        'date': curr_date,
        'users_count': len(users),
        'users': users
    }
    return data

def get_unpaid_data(user, user_leaves, leave_types, curr_year, month):
    try:

        yearly_quarters = get_quarters(user.date_of_joining, None)
        year = list(yearly_quarters.keys())[0]
        start_date = yearly_quarters[year][0]['start_date']
        end_date = yearly_quarters[year][3]['end_date']

        if year==curr_year and start_date.month > month:
            return []
        
        user_leaves_for_year = user_leaves.filter(start_date__lte=end_date, end_date__gte=start_date).order_by('start_date')

        type_names = leave_types.values_list('name', flat=True)
        taken_unpaid_obj = { type: {'leaves_taken' : 0, 'unpaid' : 0} for type in type_names }

        quarterly_leave_types = user_leaves_for_year.filter(Q(leave_type__rule_set__duration="quarterly") | Q(leave_type__rule_set__name="miscellaneous_leave")).values_list('leave_type__name', flat=True).distinct()
        miscellaneous_types = user_leaves_for_year.filter(Q(leave_type__rule_set__name="miscellaneous_leave")).values_list('leave_type__name', flat=True).distinct()
        
        unpaid_days_for_month = []

        curr_quarter = prev_quarter = None
        for i in range(4):
            if month in yearly_quarters[year][i]['months']:
                curr_quarter = i
                prev_quarter = i-1 if i>0 else i
                break

        for i in range(prev_quarter, curr_quarter+1):
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

                max_pto = leave_types.get(name='pto').rule_set.max_days_allowed

                if leave['leave_type'] in miscellaneous_types:
                    temp_leaves_taken = taken_unpaid_obj['pto']['leaves_taken']
                    x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_pto, max_wfh_days=0)
                    taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                    taken_unpaid_obj['pto']['unpaid'] += x[1]

                else:
                    if leave['leave_type'] in ['pto', 'wfh']:
                        max_wfh_days = leave_types.get(name='wfh').rule_set.max_days_allowed
                        x = find_unpaid_days(days_in_quarter, leaves_taken=taken_unpaid_obj['pto']['leaves_taken'], wfh_taken=taken_unpaid_obj['wfh']['leaves_taken'], max_leave_days=max_pto, max_wfh_days=max_wfh_days)
                        taken_unpaid_obj['pto']['leaves_taken'] += x[3]
                        taken_unpaid_obj['wfh']['leaves_taken'] += x[2]
                    else: 
                        max_days_allowed = leave_types.get(name=leave['leave_type']).rule_set.max_days_allowed
                        temp_leaves_taken = taken_unpaid_obj[leave['leave_type']]['leaves_taken']
                        x = find_unpaid_days(days_in_quarter, leaves_taken=temp_leaves_taken, wfh_taken=0, max_leave_days=max_days_allowed, max_wfh_days=0)
                        taken_unpaid_obj[leave['leave_type']]['leaves_taken'] += x[3]
                        taken_unpaid_obj['pto']['leaves_taken'] += min(max_pto, x[3] - x[1]) #reducing available pto if these yearly leaves are taken in the current quarter

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

def check_leave_overlap(leave_data):
    overlap = False
    start_date = leave_data['start_date']
    end_date = leave_data['end_date']
    earlier_leave = Leave.objects.filter(
        Q(user=leave_data['user']) & ~Q(status__in=['R', 'W']) &
        (Q(start_date__lte=end_date ) & Q(end_date__gte=start_date)) 
    )
    if earlier_leave.exists():
        overlap = True
    return overlap

def is_block_leave(leave_data):
    # if a combo of 5 leaves and 2 wfh are there -> block leave
    leave_type_name = LeaveType.objects.get(id=leave_data['leave_type']).name
    if leave_type_name != 'pto':
        return False
    leave_cnt = wfh_cnt = 0
    leave_type_ids = LeaveType.objects.filter(name__in=['pto', 'wfh']).values_list('id', flat=True)
    for day in leave_data['day_details']:
        if day['is_half_day']:
                return False
        if day['type'] == str(leave_type_ids[0]):
            leave_cnt += 1
        elif day['type'] == str(leave_type_ids[1]):
            wfh_cnt += 1
    
    if leave_cnt == 5 and wfh_cnt == 2:
        return True
    return False

def is_block_leave_taken(leave_data):
    #check if this is block leave
    if not is_block_leave(leave_data):
        return False

    #check if block leave is taken within last 90 days
    start_date = datetime.strptime(leave_data['start_date'], "%Y-%m-%d") - timedelta(days=90)
    end_date = datetime.strptime(leave_data['end_date'], "%Y-%m-%d")
    leaves = Leave.objects.filter(
        Q(user__id=leave_data['user']) & Q(status__in=['A', 'P']) &
        Q(leave_type__name='pto') &
        (Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
    )
    for leave in leaves:
        if len(leave['day_details']) == 7:
            return True
    return False

def is_leave_valid(leave_data):
    messages = []
    misc_leave_types = {f'{leave_type.name}': str(leave_type.id) for leave_type in LeaveType.objects.filter(rule_set__name='miscellaneous_leave')}
    sick_leave_type = misc_leave_types.get('sick_leave')
    valid = True

    #1: check if leave overlaps
    if check_leave_overlap(leave_data):
        messages.append('You have already applied leave for some of these days')
        valid = False

    #2: check if leave start date is after one week
    elif datetime.strptime(leave_data['start_date'], "%Y-%m-%d") < datetime.now() + timedelta(days=7) and leave_data['leave_type'] not in misc_leave_types:
        messages.append('Leave cannot be applied for less than one week')
        valid = False

    #3: if its a sick leave of at least 2 days, a file must be attached
    elif leave_data['leave_type'] == str(sick_leave_type.id):
        if len(leave_data['day_details']) >= 2 and leave_data['assets_documents'] is None:
            messages.append('Sick Leave of at least 2 days must have a file attached')
            valid = False

    #4: Block leave validation
    elif is_block_leave_taken(leave_data):
        messages.append("you can't take a block leave before 90 days of your last block leave")
        valid = False

    return {'valid': valid, 'messages': messages}