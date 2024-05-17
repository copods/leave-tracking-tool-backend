from rest_framework.views import APIView
from rest_framework import status
from .models import User
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return JsonResponse(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return JsonResponse({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class ApproverListView(APIView):

    def get(self, request):
        approvers = User.objects.filter(role__role_name='team lead')
        serializer = ApproverListSerializer(approvers, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
