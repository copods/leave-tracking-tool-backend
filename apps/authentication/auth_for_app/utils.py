from rest_framework.response import Response
from apps.user.models import User
from ..common_auth_utils import generate_tokens, verify_google_id_token
from django.http import JsonResponse

def sign_in_app(request):
    google_token = request.data.get('token')
    user_info = verify_google_id_token(google_token)

    if user_info != '':
        try:
            user = User.objects.get(email=user_info['email'])
            access_token, refresh_token = generate_tokens(user)
            return JsonResponse({
                'access_token': str(access_token), 
                'refresh_token': str(refresh_token),
                'user_role': user.role.role_name
            })
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    else:
        return JsonResponse({'error': 'Invalid token'}, status=498)
    