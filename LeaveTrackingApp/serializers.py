from rest_framework import serializers
from LeaveTrackingApp.models import Leave, LeaveType, RuleSet, DayDetails, Holiday, StatusReason, yearCalendar

#------------other serializers---------------
class RuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSet
        fields = '__all__'

class DayDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayDetails
        fields = '__all__'

class StatusReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusReason
        fields = '__all__'

#-----------------leave related serializers---------------------
class LeaveTypeSerializer(serializers.ModelSerializer):
    rule_set = RuleSetSerializer(read_only=True)

    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveSerializer(serializers.ModelSerializer):
    day_details = DayDetailSerializer(many=True)
    status_reasons = StatusReasonSerializer(many=True, required=False)

    class Meta:
        model = Leave
        fields = '__all__'

    def create(self, validated_data):
        day_details_data = validated_data.pop('day_details', [])
        status_reasons_data = validated_data.pop('status_reasons', [])
        leave = Leave.objects.create(**validated_data)
        leave.status_reasons.set(status_reasons_data)
        for day_detail_data in day_details_data:
            day_detail = DayDetails.objects.create(**day_detail_data)
            leave.day_details.add(day_detail)
        return leave

class LeaveUtilSerializer(serializers.ModelSerializer):
    day_details = DayDetailSerializer(many=True)
    user = serializers.SerializerMethodField('get_user')
    class Meta:
        model = Leave
        fields = ['user','day_details']
    
    def get_user(self, obj):
        return {'name': obj.user.long_name(), 'profilePicture': obj.user.profile_image}
    
class LeaveListSerializer(serializers.ModelSerializer):
    requestedBy = serializers.SerializerMethodField('get_requestedBy')
    leaveType = serializers.CharField(source='leave_type.name')
    leaveStatus = serializers.CharField(source='status')
    startDate = serializers.DateField(source='start_date')
    endDate = serializers.DateField(source='end_date')
    modifiedOn = serializers.SerializerMethodField('get_modifiedOn')

    class Meta:
        model = Leave
        fields = [ 'id', 'requestedBy', 'leaveType', 'leaveStatus', 'startDate', 'endDate', 'modifiedOn', 'editStatus']
    
    def get_requestedBy(self, obj):
        leave_user = { "name": obj.user.long_name(), "profilePicture": obj.user.profile_image}
        return leave_user
    
    def get_modifiedOn(self, obj):
        return obj.updated_at.date()

class UserLeaveListSerializer(serializers.ModelSerializer):
    leaveType = serializers.CharField(source='leave_type.name')
    leaveStatus = serializers.CharField(source='status')
    startDate = serializers.DateField(source='start_date')
    endDate = serializers.DateField(source='end_date')
    updatedOn = serializers.SerializerMethodField('get_updatedOn')
    
    class Meta:
        model = Leave
        fields = ['id', 'leaveType', 'leaveStatus', 'startDate', 'endDate', 'updatedOn']
    
    def get_updatedOn(self, obj):
        latest_status = obj.status_reasons.order_by('-created_at').first()
        return latest_status.created_at.date() if latest_status else obj.updated_at.date()
    
    
# ----------------calendar related serializers--------------------
class HolidaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = '__all__'

class YearCalendarSerializerList(serializers.ModelSerializer):
    holidays = HolidaySerializer(many=True)

    class Meta:
        model = yearCalendar
        fields = '__all__'

class YearCalendarSerializer(serializers.ModelSerializer):
    holidays = HolidaySerializer(many=True)

    class Meta:
        model = yearCalendar
        fields = '__all__'

    def create(self, validated_data):
        holiday_data = validated_data.pop('holidays')
        holiday_calendar = yearCalendar.objects.create(**validated_data)
        for holiday in holiday_data:
            holiday = Holiday.objects.create(**holiday)
            holiday_calendar.holidays.add(holiday)
        return holiday_calendar
