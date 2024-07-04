from LeaveTrackingApp.models import Holiday, LeavePolicy, LeaveType, YearPolicy, yearCalendar
from rest_framework import serializers
from django.db import transaction
from common.models import Comment
from common.serializers import CommentSerializer


class HolidaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = '__all__'


class YearCalendarSerializerList(serializers.ModelSerializer):
    holidays = HolidaySerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = yearCalendar
        fields = '__all__'


class YearCalendarSerializer(serializers.ModelSerializer):
    holidays = HolidaySerializer(many=True)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = yearCalendar
        fields = '__all__'

    def create(self, validated_data):
        holiday_data = validated_data.pop('holidays')
        comments = validated_data.pop('comments', [])
        holiday_calendar = yearCalendar.objects.create(**validated_data)
        for holiday in holiday_data:
            holiday = Holiday.objects.create(**holiday)
            holiday_calendar.holidays.add(holiday)

        for comment in comments:
            comment = Comment.objects.create(**comment)
            holiday_calendar.comments.add(comment)

        return holiday_calendar


class LeavePolicySerializer(serializers.ModelSerializer):
   
    class Meta:
        model = LeavePolicy
        fields = '__all__'
        extra_kwargs = { 'leave_type': {'read_only': True} }

    def validate(self, data):
        leave_type_name = data.get('name')
        if leave_type_name:
            try:
                leave_type_names = LeaveType.objects.values_list('name', flat=True)
                if leave_type_name in leave_type_names:
                    leave_type = LeaveType.objects.get(name=leave_type_name)
                    data['leave_type'] = leave_type
            except LeaveType.DoesNotExist:
                raise serializers.ValidationError({'name': f"LeaveType with name '{leave_type_name}' does not exist."})
        else:
            raise serializers.ValidationError({'name': "This field is required."})
        return data
    
class LeavePolicyUtilSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = LeavePolicy
        fields = ['id', 'name', 'max_days_allowed', 'description', 'created_at', 'updated_at']

class YearPolicySerializer(serializers.ModelSerializer):
    leave_policies = LeavePolicySerializer(many=True)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = YearPolicy
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        policies_data = validated_data.pop('leave_policies')
        comments = validated_data.pop('comments', [])
        year_policy = YearPolicy.objects.create(**validated_data)

        for policy_data in policies_data:
            leave_policy_serializer = LeavePolicySerializer(data=policy_data)
            if leave_policy_serializer.is_valid(raise_exception=True):
                leave_policy = leave_policy_serializer.save()
                year_policy.leave_policies.add(leave_policy)
        
        for comment in comments:
            comment = Comment.objects.create(**comment)
            year_policy.comments.add(comment)

        return year_policy

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['leave_policies'] = LeavePolicyUtilSerializer(instance.leave_policies.all(), many=True).data
        return representation