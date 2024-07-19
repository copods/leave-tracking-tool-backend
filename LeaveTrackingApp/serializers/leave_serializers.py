from LeaveTrackingApp.models import Leave, LeaveType, RuleSet, DayDetails, StatusReason
from rest_framework import serializers


class RuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSet
        fields = '__all__'


class DayDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = DayDetails
        fields = '__all__'

class DayDetailsUtilSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='type.name')

    class Meta:
        model = DayDetails
        fields = '__all__'


class StatusReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusReason
        fields = '__all__'

# TODO: for future need
# class StatusReasonUtilSerializer(serializers.ModelSerializer):
#     user = serializers.SerializerMethodField('get_user')

#     class Meta:
#         model = StatusReason
#         fields = '__all__'

#     def get_user(self, obj):
#         return {
#             'name': obj.user.long_name(),
#             'profilePicture': obj.user.profile_image
#         }


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

    def update(self, instance, validated_data):
        day_details_data = validated_data.pop('day_details', [])
        if day_details_data:
            provided_days_ids = [day_data.get('id') for day_data in day_details_data if day_data.get('id')]
            existing_days = {str(day.id): day for day in instance.day_details.filter(id__in=provided_days_ids)}
            for day_data in day_details_data:
                day_id = day_data.get('id')
                if day_id and str(day_id) in existing_days:
                    day_instance = existing_days[str(day_id)]
                    if day_data.get('type'):
                        day_data['type'] = day_data['type'].id
                    day_serializer = DayDetailSerializer(instance=day_instance, data=day_data, partial=True)
                    if day_serializer.is_valid(raise_exception=True):
                        day_serializer.save()
        return instance

class LeaveDetailSerializer(serializers.ModelSerializer):
    day_details = DayDetailsUtilSerializer(many=True)
    status_reasons = StatusReasonSerializer(many=True, required=False)
    # status_reasons = StatusReasonUtilSerializer(many=True, required=False)  # TODO: use this in second phase
    user = serializers.SerializerMethodField('get_user')
    approver = serializers.SerializerMethodField('get_approver')
    leave_type = serializers.CharField(source='leave_type.name')
    editStatus = serializers.CharField(source='edit_choices')

    class Meta:
        model = Leave
        fields = '__all__'

    def get_user(self, obj):
        return {
            'id': obj.user.id, 
            'name': obj.user.long_name(), 
            'designation': obj.user.designation, 
            'profilePicture': obj.user.profile_image
        }

    def get_approver(self, obj):
        return {
            'id': obj.approver.id, 
            'name': obj.approver.long_name(), 
            'designation': obj.approver.designation, 
            'profilePicture': obj.approver.profile_image
        }


class LeaveUtilSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.SerializerMethodField()
    profilePicture = serializers.CharField(source='user.profile_image', read_only=True)
    leave_type = serializers.CharField(source='leave_type.name', read_only=True)
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)
    day_details = DayDetailsUtilSerializer(many=True, read_only=True)
    
    def get_name(self, obj):
        return obj.user.long_name()
    

class LeaveListSerializer(serializers.ModelSerializer):
    requestedBy = serializers.SerializerMethodField('get_requestedBy')
    leaveType = serializers.CharField(source='leave_type.name')
    leaveStatus = serializers.CharField(source='status')
    startDate = serializers.DateField(source='start_date')
    endDate = serializers.DateField(source='end_date')
    modifiedOn = serializers.SerializerMethodField('get_modifiedOn')
    editStatus = serializers.CharField(source='edit_choices')

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
    editStatus = serializers.CharField(source='edit_choices')
    
    class Meta:
        model = Leave
        fields = ['id', 'leaveType', 'leaveStatus', 'startDate', 'endDate', 'updatedOn', 'editStatus']
    
    def get_updatedOn(self, obj):
        latest_status = obj.status_reasons.order_by('-created_at').first()
        return latest_status.created_at.date() if latest_status else obj.updated_at.date()
    
    