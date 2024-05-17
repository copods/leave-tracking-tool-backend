from rest_framework import serializers
from .models import User

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    department = serializers.CharField(source='department.dept_name')
    role = serializers.CharField(source='role.role_name')
    class Meta:
        model = User
        fields = ['name', 'profile_image', 'designation', 'role', 'work_type', 'department', 'doj'] #add user_status
    
    def get_name(self, obj):
        return obj.long_name()


class ApproverListSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name')
    dept_name = serializers.CharField(source='department.dept_name')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role_name', 'dept_name']