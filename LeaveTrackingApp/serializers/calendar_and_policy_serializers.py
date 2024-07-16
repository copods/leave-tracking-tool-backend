from LeaveTrackingApp.models import Holiday, LeavePolicy, LeaveType, YearPolicy, yearCalendar
from rest_framework import serializers
from django.db import transaction
from common.models import Comment
from common.serializers import CommentSerializer
 

class HolidaySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Holiday
        fields = '__all__'


class YearCalendarSerializer(serializers.ModelSerializer):
    holidays = HolidaySerializer(many=True)
    comments = CommentSerializer(many=True, required=False)
    status = serializers.CharField(source='status_choices', read_only=True)

    class Meta:
        model = yearCalendar
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        holiday_data = validated_data.pop('holidays')
        comments = validated_data.pop('comments', [])
        if 'status' in validated_data:
            validated_data['status'] = 'draft'
        holiday_calendar = yearCalendar.objects.create(**validated_data)
        for holiday in holiday_data:
            holiday = Holiday.objects.create(**holiday)
            holiday_calendar.holidays.add(holiday)

        for comment in comments:
            comment = Comment.objects.create(**comment)
            holiday_calendar.comments.add(comment)

        return holiday_calendar

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data['status'] = 'draft' # set status to draft when policy gets edited
        holiday_data = validated_data.pop('holidays', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if holiday_data:
            provided_holiday_ids = [holiday.get('id') for holiday in holiday_data if holiday.get('id')]
            existing_holidays = {str(holiday.id): holiday for holiday in instance.holidays.filter(id__in=provided_holiday_ids)}
            for holiday in holiday_data:
                holiday_id = holiday.get('id')
                if holiday_id and str(holiday_id) in existing_holidays:
                    holiday_instance = existing_holidays[str(holiday_id)]
                    holiday_serializer = HolidaySerializer(instance=holiday_instance, data=holiday, partial=True)
                    if holiday_serializer.is_valid(raise_exception=True):
                        holiday_serializer.save()

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['holidays'] = HolidaySerializer(instance.holidays.all(), many=True).data
        return representation


class LeavePolicySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = LeavePolicy
        fields = '__all__'
        extra_kwargs = {'leave_type': {'read_only': True}}

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
        fields = ['id', 'name', 'details', 'description', 'created_at', 'updated_at']

class YearPolicySerializer(serializers.ModelSerializer):
    leave_policies = LeavePolicySerializer(many=True)
    comments = CommentSerializer(many=True, required=False)
    status = serializers.CharField(source='status_choices', read_only=True)

    class Meta:
        model = YearPolicy
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        policies_data = validated_data.pop('leave_policies')
        comments = validated_data.pop('comments', [])
        if 'status' in validated_data:
            validated_data['status'] = 'draft' 
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

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data['status'] = 'draft' # set status to draft when policy gets edited
        policies_data = validated_data.pop('leave_policies', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if policies_data:
            provided_policy_ids = [policy_data.get('id') for policy_data in policies_data if policy_data.get('id')]
            existing_policies = {str(policy.id): policy for policy in instance.leave_policies.filter(id__in=provided_policy_ids)}
            for policy_data in policies_data:
                policy_id = policy_data.get('id')
                if policy_id and str(policy_id) in existing_policies:
                    leave_policy_instance = existing_policies[str(policy_id)]
                    leave_policy_serializer = LeavePolicySerializer(instance=leave_policy_instance, data=policy_data, partial=True)
                    if leave_policy_serializer.is_valid(raise_exception=True):
                        leave_policy_serializer.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['leave_policies'] = LeavePolicyUtilSerializer(instance.leave_policies.all(), many=True).data
        return representation