from LeaveTrackingApp.models import Leave, RuleSet, LeaveType
from django.db.models import Q
from LeaveTrackingApp.serializers import LeaveUtilSerializer
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

        year_leave_stats = {
            'year': f'{year}-{int(year) + 1}',
            'data': []
        }
        
        # Calculate quarterly statistics
        for i in range(4):
            quarter_obj = {
                'title': f'Q{i + 1}',
                'months': yearly_quarters[year][i]['months'],
                'total_unpaid': 0,
                'leaves': []
            }

            leaves_for_curr_quarter = LeaveUtilSerializer(
                user_leaves_for_year.filter(
                    ( Q(start_date__gte=yearly_quarters[year][i]['start_date']) & Q(start_date__lt=yearly_quarters[year][i]['end_date']) ) |
                    Q(end_date__gte=yearly_quarters[year][i]['start_date'])
                ), many=True
            ).data
            
            leave_types = user_leaves_for_year.values_list('leave_type__name', flat=True).distinct()
            taken_unpaid_obj = {
                type: {
                    'leaves_taken' : 0,
                    'unpaid' : 0
                }
                for type in leave_types
            }
            for leave in leaves_for_curr_quarter:
                max_days_allowed = LeaveType.objects.get(name=leave['leave_type']).rule_set.max_days_allowed
                # leaves overlapping quarters is handled here -> put days in respective quarter accordingly in respective leave
                days_in_quarter = [
                    day
                    for day in leave['day_details']
                    if calendar.month_abbr[datetime.strptime(day['date'], "%Y-%m-%d").month] in yearly_quarters[year][i]['months']
                ]
                days_in_quarter, unpaid_count = find_unpaid_days(days_in_quarter, taken_unpaid_obj[leave['leave_type']]['leaves_taken'], max_days_allowed)
                taken_unpaid_obj[leave['leave_type']]['leaves_taken'] += len(days_in_quarter)
                taken_unpaid_obj[leave['leave_type']]['unpaid'] += unpaid_count
                leave['day_details'] = days_in_quarter

                temp = {
                    'id': leave['id'],
                    'start_date': leave['start_date'],
                    'end_date': leave['end_date'],
                    'type': leave['leave_type'],
                    'status': leave['status'],
                    'unpaid_count': unpaid_count
                }
                quarter_obj['total_unpaid'] += unpaid_count       
                quarter_obj['leaves'].append(temp)

            year_leave_stats['data'].append(quarter_obj)

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

def get_monthwise_unpaid(days, max_days_allowed, months):
    days.sort()
    taken = 0
    unpaid = [0,0,0]
    for day in days:
        taken += 1
        if(taken > max_days_allowed):
            unpaid[months.index(calendar.month_abbr[day.month])] += 1
    return unpaid

def find_unpaid_days(days, days_taken, max_days_allowed):
    unpaid = 0
    modified_days = days
    count= 0
    for day in modified_days:
        count += 0.5 if day['is_half_day'] else 1
        if days_taken+count > max_days_allowed:
            unpaid += 1
            day['unpaid'] = True
        else:
            day['unpaid'] = False
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
