from LeaveTrackingApp.models import Holiday, yearCalendar
from rest_framework import serializers


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
