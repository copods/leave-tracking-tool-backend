from rest_framework import serializers
from .models import User

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ApproverListSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name')
    dept_name = serializers.CharField(source='department.dept_name')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role_name', 'dept_name']