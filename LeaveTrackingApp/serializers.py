from rest_framework import serializers
from LeaveTrackingApp.models import Leave, LeaveType, RuleSet, DayDetails, Holiday, yearCalendar

class RuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSet
        fields = '__all__'

class LeaveTypeSerializer(serializers.ModelSerializer):
    rule_set = RuleSetSerializer(read_only=True)

    class Meta:
        model = LeaveType
        fields = '__all__'

class DayDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayDetails
        fields = '__all__'

class LeaveSerializer(serializers.ModelSerializer):
    day_details = DayDetailSerializer(many=True)

    class Meta:
        model = Leave
        fields = '__all__'

    def create(self, validated_data):
        day_details_data = validated_data.pop('day_details')
        leave = Leave.objects.create(**validated_data)
        for day_detail_data in day_details_data:
            day_detail = DayDetails.objects.create(**day_detail_data)
            leave.day_details.add(day_detail)
        return leave

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