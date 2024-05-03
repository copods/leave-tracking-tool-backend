from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Role
from .serializers import RoleSerializers

class GetPostRoles(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers

class GetPutDeleteRole(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers

    def delete(self, request, *args, **kwargs):
        return self.get_object().delete() and Response({"message": "Role deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
