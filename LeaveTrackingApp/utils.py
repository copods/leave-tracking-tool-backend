from LeaveTrackingApp.models import Leave, RuleSet, LeaveType
from django.db.models import Q
from LeaveTrackingApp.serializers import LeaveSerializer, LeaveUtilSerializer
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
            ~Q(status="W") &
            (
                (Q(start_date__gte=start_date) & Q(start_date__lt=end_date)) | Q(end_date__gte=start_date)
            )
        )

        quarterly_leave_types = LeaveType.objects.filter(~Q(rule_set__duration="None") ).values_list('name', flat=True)
        yearly_leave_types = LeaveType.objects.filter(Q(rule_set__duration="None") & ~Q(rule_set__name="miscellaneous_leave")).values_list('name', flat=True)

        print('1********')

        year_leave_stats = {
            'year': f'{year}-{int(year) + 1}',
            'yearly_leaves': [],
            'quarterly_leaves': [],
        }

        print('2*********')

        # Calculate yearly leave statistics
        for leave_type in yearly_leave_types:
            yearly_leave_obj = {}
            leaves = user_leaves_for_year.filter(leave_type__name=leave_type)
            if leaves:
                yearly_leave_obj['leave_type'] = leave_type
                yearly_leave_obj['totalDays'] = LeaveType.objects.get(name=leave_type).rule_set.max_days_allowed

                leaves_data = LeaveUtilSerializer(leaves, many=True).data
                leaves_taken = 0
                unpaid = 0
                for leave in leaves_data:
                    leave_days = leave['day_details']
                    leave_days.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
                    #the case where leave overlapped two years, filter off day details array accordingly
                    leave_days = [
                        day for day in leave_days
                        if start_date <= datetime.strptime(day['date'], "%Y-%m-%d").date() < end_date
                    ]
                    leave_days = [
                        {
                            'id': day['id'],
                            'date': day['date'],
                            'is_half_day': day['is_half_day'],
                            'unpaid': False,
                        }
                        for day in leave_days
                    ]
                    leave_days, unpaid_count = find_unpaid_days(leave_days, leaves_taken, yearly_leave_obj['totalDays'])
                    leave['day_details'] = leave_days
                    unpaid += unpaid_count
                    leaves_taken += len(leave_days)
                    print('****', leaves_taken, '****')


                yearly_leave_obj['daysTaken'] = leaves_taken
                yearly_leave_obj['remaining'] = max(yearly_leave_obj['totalDays'] - yearly_leave_obj['daysTaken'], 0)
                yearly_leave_obj['unpaid_count'] = unpaid
                yearly_leave_obj['leaves'] = [
                    {
                        'id': leave['id'],
                        'start_date': leave['start_date'],
                        'end_date': leave['end_date'],
                        'status': leave['status'],
                        'day_details': leave['day_details'], 
                    }
                    for leave in leaves_data
                ]
            else:
                max_days = LeaveType.objects.get(name=leave_type).rule_set.max_days_allowed
                yearly_leave_obj = {
                    'leave_type': leave_type,
                    'daysTaken': 0,
                    'totalDays': max_days,
                    'remaining': max_days,
                    'unpaid_count': 0,
                    'leaves': []
                }

            year_leave_stats['yearly_leaves'].append(yearly_leave_obj)

        print('3*********')

        # Organize quarterly leaves and day details
        quarterly_leaves_for_year = {leave_type: [] for leave_type in quarterly_leave_types}

        for leave_type in quarterly_leave_types:
            leave_requests = user_leaves_for_year.filter(leave_type__name=leave_type).order_by('start_date')
            leave_requests = LeaveUtilSerializer(leave_requests, many=True).data
            for leave in leave_requests:
                day_details = leave['day_details']
                day_details.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
                temp_days = []
                for day in day_details:
                    #case where quarterly leave overlapped two years, filter off their days accordingly
                    if start_date <= datetime.strptime(day['date'], "%Y-%m-%d").date() < end_date:
                        temp_days.append({
                            'id': day['id'],
                            'date': day['date'],
                            'is_half_day': day['is_half_day'],
                            'unpaid': False,
                        })
                leave['day_details'] = temp_days
                leave_data = {
                    'id': leave['id'],
                    'start_date': leave['start_date'],
                    'end_date': leave['end_date'],
                    'status': leave['status'],
                    'day_details': leave['day_details'],
                }
                quarterly_leaves_for_year[leave_type].append(leave_data)
        
        print('4*********')
        
        # Calculate quarterly statistics
        for i in range(4):
            quarter_obj = {
                'title': f'Q{i + 1}',
                'months': yearly_quarters[year][i]['months'],
                # 'unpaid_count': [0, 0, 0]  #  unpaid days per month -> corresponds to each month for that quarter
            }
            print('here0')
            for leave_type in quarterly_leave_types:
                if leave_type not in quarter_obj:
                    quarter_obj[leave_type] = {
                        'totalDays': 0,
                        'daysTaken': 0,
                        'remaining': 0,
                        'unpaid_count': 0,
                        'leaves': [],
                    }
                quarter_obj[leave_type]['totalDays'] = LeaveType.objects.get(name=leave_type).rule_set.max_days_allowed
                leaves_for_curr_quarter = [
                    leave 
                    for leave in quarterly_leaves_for_year[leave_type]
                    if (
                        (datetime.strptime(leave['start_date'], "%Y-%m-%d").date() >= yearly_quarters[year][i]['start_date'] and
                        datetime.strptime(leave['start_date'], "%Y-%m-%d").date() < yearly_quarters[year][i]['end_date']) or
                        datetime.strptime(leave['end_date'], "%Y-%m-%d").date() >= yearly_quarters[year][i]['start_date']
                    )
                ]

                print('here1')

                leaves_taken = 0
                unpaid = 0
                for leave in leaves_for_curr_quarter:
                    # leaves overlapping quarters is handled here -> put days in respective quarter accordingly in respective leave
                    days_in_quarter = [
                        day
                        for day in leave['day_details']
                        if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']
                    ]
                    days_in_quarter, unpaid_count = find_unpaid_days(days_in_quarter, leaves_taken, quarter_obj[leave_type]['totalDays'])
                    leaves_taken += len(days_in_quarter)
                    unpaid += unpaid_count
                    leave['day_details'] = days_in_quarter
                    
                print('here2')

                quarter_obj[leave_type]['daysTaken'] = leaves_taken
                quarter_obj[leave_type]['remaining'] = max(quarter_obj[leave_type]['totalDays'] - quarter_obj[leave_type]['daysTaken'], 0)
                quarter_obj[leave_type]['leaves'] = leaves_for_curr_quarter
                quarter_obj[leave_type]['unpaid_count'] = unpaid        

                year_leave_stats[f'{leave_type}_taken'] = quarter_obj[leave_type]['daysTaken']
                year_leave_stats[f'total_{leave_type}'] = quarter_obj[leave_type]['totalDays']
            
            print('here3')
            year_leave_stats['quarterly_leaves'].append(quarter_obj)
        
        print('5*********')

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

def find_unpaid_days(days, days_taken, max_days_allowed):
    unpaid = 0
    modified_days = days
    count= 0
    print(max_days_allowed, '\n', days_taken, '\n', days)
    for day in modified_days:
        count += 0.5 if day['is_half_day'] else 1
        if days_taken+count > max_days_allowed:
            unpaid += 1
            day['unpaid'] = True
    return modified_days, unpaid
            


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
