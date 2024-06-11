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

class RoleBasedListSerializer(serializers.ModelSerializer):
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
    
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_name','role_key']

class UserDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_name','department_key']

class UserListSerializer(serializers.ModelSerializer):
    role= UserRoleSerializer(read_only=True)
    department= UserDepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'department','id','work_location','date_of_joining']


# class UserProfileSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField('get_name')
#     profilePicture = serializers.CharField(source='profile_image')
#     workType = serializers.CharField(source='work_type')
#     dateOfJoining = serializers.DateField(source='date_of_joining')
#     contactNumber = serializers.CharField(source='phone_number')
#     emergencyContact = serializers.SerializerMethodField('get_emergencyContact')
#     currentAddress = serializers.CharField(source='current_address_line')
#     permanentAddress = serializers.CharField(source='permanent_address_line')
#     # leave_summary = serializers.SerializerMethodField('get_leave_summary')

#     class Meta:
#         model = User
#         fields = ['profilePicture', 'name', 'designation', 'workType', 'dateOfJoining', 
#                     'contactNumber', 'emergencyContact', 'currentAddress', 'permanentAddress']

#     def get_name(self, obj):
#         return obj.long_name()
    
#     def get_emergencyContact(self, obj):
#         return {
#             "name" : obj.emergency_contact_name,
#             "number" : obj.emergency_contact_number,
#             "relation" : obj.emergency_contact_relation
#         } 
    
#     # def get_leave_summary(self, obj):
#     #     return getYearLeaveStats(obj.id, self.context.get('year'))

