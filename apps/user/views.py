from rest_framework.views import APIView
from apps.department.models import Department
from apps.role.models import Role
from .models import User
from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse



class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    
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
        

class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return JsonResponse(serializer.data, safe=False)
    
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return JsonResponse(serializer.data, safe=False)

    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return JsonResponse({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class ApproverListView(APIView):
    
    def get(self, request):
        approvers = User.objects.filter(role__role_name='team lead')
        serializer = ApproverListSerializer(approvers, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
