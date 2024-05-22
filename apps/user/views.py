from rest_framework.views import APIView
from rest_framework.decorators import api_view
from apps.department.models import Department
from apps.role.models import Role
from .models import User
from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from apps.authorization.decorators import user_has_permission, user_is_authenticated
from django.utils.decorators import method_decorator
from django.db.models import Q

@method_decorator(user_is_authenticated, name='dispatch')
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]

    @method_decorator(user_has_permission('addEmployee'), name='dispatch')
    def post(self, request, *args, **kwargs):
        data = request.data
        
        role_name = data.get('role')
        dept_name = data.get('department')
            
        try:
            role = Role.objects.get(role_name=role_name)
            department = Department.objects.get(dept_name=dept_name)
            
            data['role'] = role.role_id
            data['department'] = department.dept_id

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            self.perform_create(serializer)

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, safe=False)
        
        except Role.DoesNotExist:
            return JsonResponse({"message": f"Role '{role_name}' does not exist."})
        except Department.DoesNotExist:
            return JsonResponse({"message": f"Department '{dept_name}' does not exist."})
        

@method_decorator(user_is_authenticated, name='dispatch')
class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]

    
    @method_decorator(user_has_permission('getEmployee'), name='dispatch')
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        try:
            user = User.objects.get(user_id=user_id)
            serializer = self.get_serializer(user)
            return JsonResponse(serializer.data, safe=False)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
    
    @method_decorator(user_has_permission('editEmployee'), name='dispatch')
    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        try:
            user = User.objects.get(user_id = user_id)
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return JsonResponse(serializer.data, safe=False)
        except User.DoesNotExist:
            return JsonResponse({"message": "User does not exists."}, status=status.HTTP_404_NOT_FOUND)

    @method_decorator(user_has_permission('deleteEmployee'), name='dispatch')
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        try:
            user = User.objects.get(user_id = user_id)
            self.perform_destroy(user)
            return JsonResponse({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return JsonResponse({"message": "User does not exists."}, status=status.HTTP_404_NOT_FOUND)
    

class ApproverListView(APIView):
    
    def get(self, request):
        approvers = User.objects.filter(role__role_name='team lead')
        serializer = ApproverListSerializer(approvers, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


# using POST API for getting user list to make query passing easy
@api_view(['POST'])
@user_is_authenticated
@user_has_permission('getEmployeeList')
def get_user_list(request):
    search_query = request.data.get('search', '')
    sort_params = request.data.get('sort_by', [])
    filter_params = request.data.get('filter', {})

    queryset = User.objects.all()
    mapping = {'role': 'role__role_name', 'department': 'department__dept_name'}

    if filter_params:
        filter_params = {mapping.get(key, key): value for key, value in filter_params.items()}
        filter_q_objects = Q()
        for key, value in filter_params.items():
            if isinstance(value, list):
                temp_q = Q()
                for val in value:
                    temp_q |= Q(**{key: val})
                filter_q_objects &= temp_q
            else:
                filter_q_objects &= Q(**{key: value})
        queryset = queryset.filter(filter_q_objects)

    if search_query:
        queryset = queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(role__role_name__icontains=search_query) | 
            Q(department__dept_name__icontains=search_query)
        )

    if sort_params:
        sort_params = [mapping.get(param, param) for param in sort_params]
        queryset = queryset.order_by(*sort_params)

    serializer = UserListSerializer(queryset, many=True)
    return JsonResponse(serializer.data, safe=False)