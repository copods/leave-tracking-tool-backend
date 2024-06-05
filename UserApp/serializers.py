from rest_framework import serializers
from UserApp.models import User, Department, Role

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ApproverListSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.role_name')
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'role', 'profile_image']

    def get_name(self, obj):
        return obj.long_name()