from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import json
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt 
@api_view(['POST'])
def googleSignIn(request):
    if request.method == 'POST':
        # print(request.body)  # Check post data

        # data = json.loads(request.body.decode('utf-8'))
        # token = data.get('token')
        # email = data.get('email')

        token = request.data.get('token')
        email = request.data.get('email')

        print("Token:", token)
        print("email", email)

        try:
            CLIENT_ID = '357319250308-3m2228pa5kq64kcooi65ehej5snr0svg.apps.googleusercontent.com'
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            print(id_info)
            if id_info['email'] == email:
                request.session['user_email'] = email
                # return JsonResponse({'message': 'Authentication successful'})
                #after successfull validation, retrieve or create user
                
                # query users by email
                users = User.objects.filter(email = email)

                #if multiple
                if users.count() >1:
                    user = users.first()
                else:
                    user, created = User.objects.get_or_create(email = email)



                #generate JWT token
                access_token =AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)

                return Response({
                    'access_token': str(access_token),
                    'refresh_token': str(refresh_token),
                })

            else:
                return Response({'error': 'Email mismatch'}, status=400)
            
            
        except ValueError as e:
            # Invalid token
            return Response({'error': 'Invalid token'}, status=400)
        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=400)
        
        
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    


@api_view(['POST'])
def validate_token(request):
    token = request.data.get('access_token')
    try:
        AccessToken(token) #will give error if not valid token
        return Response({'valid' : True})

    except Exception as e:
        return Response({'valid' : False, 'error':str(e)})