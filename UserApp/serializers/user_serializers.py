from rest_framework import serializers
from UserApp.serializers import UserRoleSerializer, UserDepartmentSerializer
from UserApp.models import User


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

class UserAppProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    emergency_contact = serializers.SerializerMethodField()

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
        fields = ['first_name', 'last_name', 'email', 'profile_image', 'designation', 'role', 'department','id','work_location','date_of_joining']
