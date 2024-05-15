from functools import wraps

from django.http import JsonResponse
from .permissions import *
from .utils import isJWTValid, getRole


def user_is_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({"message": "Authorization header missing"}, status=401)
        
        token = auth_header.split(' ')[1]

        user_email = isJWTValid(token)

        if user_email:
            request.user_email = user_email
            return view_func(request, *args, **kwargs)
        else:
            request.user_email = None
            return JsonResponse({"message": "Invalid token"}, status=401)
            
    return _wrapped_view


def user_has_permission(api_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            permission_list = get_permission_list()

            user_role = getRole(request.user_email)

            if(user_role and (api_name in permission_list[user_role])):
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({"message": "Permission denied"}, status=403)
            
        return _wrapped_view
    return decorator
