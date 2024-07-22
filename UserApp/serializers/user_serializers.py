from rest_framework import serializers
from UserApp.serializers import UserRoleSerializer, UserDepartmentSerializer
from UserApp.models import User


class UserSerializer(serializers.ModelSerializer):
    work_type = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        if 'work_type' in data:
            work_type = data['work_type']
            work_types = dict(User.WORK_TYPE_CHOICES)
            if work_type in work_types.values():
                data['work_type'] = next((k for k, v in work_types.items() if v == work_type), None)
            else:
                raise serializers.ValidationError({'work_type': f"Invalid choice: {work_type}. Expected one of {list(work_types.values())}."})
        return data
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['work_type'] = dict(User.WORK_TYPE_CHOICES).get(instance.work_type)
        return representation

class UserAppProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    emergency_contact = serializers.SerializerMethodField()
    work_type = serializers.CharField(source='work_type_choices')
    
    class Meta:
        model = User
        fields = [
            'name', 
            'profile_image', 
            'designation',
            'work_type',
            'date_of_joining', 
            'phone_number', 
            'emergency_contact',
            'current_address_line',
            'permanent_address_line',
            'is_current_address_same',
            'points'
        ]

    def get_name(self, obj):
        return obj.long_name()
    
    def get_emergency_contact(self, obj):
        return {
            'name': obj.emergency_contact_name,
            'relation': obj.emergency_contact_relation,
            'contact_no': obj.emergency_contact_number
        }

class ApproverListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profilePicture = serializers.CharField(source='profile_image')
    role = serializers.SerializerMethodField('get_role')
    class Meta:
        model = User
        fields = ['id', 'name', 'designation','role', 'profilePicture']

    def get_name(self, obj):
        return obj.long_name()
    
    def get_role(self, obj):
        return obj.role.role_key
    

class UserListSerializer(serializers.ModelSerializer):
    role= UserRoleSerializer(read_only=True)
    department= UserDepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_image', 'designation', 'role', 'department', 'id', 'work_location', 'work_type', 'date_of_joining', 'app_registration_status']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['work_type'] = dict(User.WORK_TYPE_CHOICES).get(instance.work_type)
        return representation