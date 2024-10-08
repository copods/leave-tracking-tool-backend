from django.conf import settings
from LeaveTrackingApp.models import Leave, LeaveType, RuleSet, DayDetails, StatusReason
from rest_framework import serializers
from django.db import transaction
import boto3


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
    type_id = serializers.UUIDField(source='type.id')

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

    @transaction.atomic
    def create(self, validated_data):
        day_details_data = validated_data.pop('day_details', [])
        status_reasons_data = validated_data.pop('status_reasons', [])
        leave = Leave.objects.create(**validated_data)
        leave.status_reasons.set(status_reasons_data)
        for day_detail_data in day_details_data:
            day_detail = DayDetails.objects.create(**day_detail_data)
            leave.day_details.add(day_detail)
        return leave

    @transaction.atomic
    def update(self, instance, validated_data):
        day_details_data = validated_data.pop('day_details', [])
        if validated_data.get('start_date'):
            instance.start_date = validated_data.pop('start_date')
        if validated_data.get('end_date'):
            instance.end_date = validated_data.pop('end_date')
        instance.editStatus = 'edited'
        instance.save()

        if day_details_data:
            provided_days_ids = [str(day_data.get('id')) for day_data in day_details_data if day_data.get('id')]
            existing_days = {str(day.id): day for day in instance.day_details.all()}
            
            for day_data in day_details_data:
                day_id = day_data.get('id')
                if day_data.get('type'):
                    day_data['type'] = day_data['type'].id
                if day_id and str(day_id) in existing_days:
                    day_instance = existing_days[str(day_id)]
                    day_serializer = DayDetailSerializer(instance=day_instance, data=day_data, partial=True)
                    if day_serializer.is_valid(raise_exception=True):
                        day_serializer.save()
                else:
                    day_serializer = DayDetailSerializer(data=day_data)
                    if day_serializer.is_valid(raise_exception=True):
                        day_instance = day_serializer.save()
                        instance.day_details.add(day_instance)
            
            for day_id in existing_days:
                if day_id not in provided_days_ids:
                    existing_days[day_id].delete()

        return instance

class LeaveDetailSerializer(serializers.ModelSerializer):
    day_details = DayDetailsUtilSerializer(many=True)
    status_reasons = StatusReasonSerializer(many=True, required=False)
    # status_reasons = StatusReasonUtilSerializer(many=True, required=False)  # TODO: use this in second phase
    user = serializers.SerializerMethodField('get_user')
    approver = serializers.SerializerMethodField('get_approver')
    leave_type = serializers.CharField(source='leave_type.name')
    leave_type_id = serializers.UUIDField(source='leave_type.id')
    editStatus = serializers.CharField(source='edit_choices')
    assets_documents = serializers.SerializerMethodField('get_assets_documents')

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

    def get_assets_documents(self, obj):
        assets_documents = obj.assets_documents
        if assets_documents:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            return s3_client.generate_presigned_url('get_object', Params={'Bucket': assets_documents.storage.bucket_name, 'Key':assets_documents.name}, ExpiresIn=600)
        return ""
        
        

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
    
    