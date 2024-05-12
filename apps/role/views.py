from rest_framework import generics
from rest_framework import status
from .models import Role
from .serializers import RoleSerializers
from django.http import JsonResponse

class GetPostRoles(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers

class GetPutDeleteRole(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers

    def delete(self, request, *args, **kwargs):
        return self.get_object().delete() and JsonResponse({"message": "Role deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
