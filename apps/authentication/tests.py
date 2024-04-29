from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone

class GoogleSignInViewTest(APITestCase):

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_sign_in_success(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.return_value = {'email': 'chandani.mourya@copods.co'}
        url = reverse('googleSignIn')
        data = {'token': 'valid_token', 'email': 'chandani.mourya@copods.co'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_sign_in_email_mismatch(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.return_value = {'email': 'chandani.mourya@copods.co'}
        url = reverse('googleSignIn')
        data = {'token': 'valid_token', 'email': 'mismatch@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Email mismatch')

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_sign_in_invalid_token(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.side_effect = ValueError('Invalid token')
        url = reverse('googleSignIn')
        data = {'token': 'udfkghcnsfjxldkmljsvlcfd', 'email': 'chandani.mourya@copods.co'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid token')

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_sign_in_other_exception(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.side_effect = Exception('Other exception')
        url = reverse('googleSignIn')
        data = {'token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImUxYjkzYzY0MDE0NGI4NGJkMDViZjI5NmQ2NzI2MmI2YmM2MWE0ODciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIzNTczMTkyNTAzMDgtcTQ1NDlwMWYydGs4NmIzM3FiNWpnNWxxcjg4NzRlZGIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIzNTczMTkyNTAzMDgtM20yMjI4cGE1a3E2NGtjb29pNjVlaGVqNXNucjBzdmcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTEzNDczMTcyNTgyNjA1MDEyOTYiLCJoZCI6ImNvcG9kcy5jbyIsImVtYWlsIjoiY2hhbmRhbmkubW91cnlhQGNvcG9kcy5jbyIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoibDlHMExYM1cxMGd1TFI2VF9kUE5CdyIsIm5vbmNlIjoiYTc4VnFJeDZoUWgwVlJxejR6LWphRFVvRnk3WU04OEcyOEZUQ1dKamNIOCIsIm5hbWUiOiJDaGFuZGFuaSBNb3VyeWEiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSTJJSkp4UU5XWEh6b2xGT2RvVVdYbHFnTzFvQklncVBSOFJ0WHZKTkdfNHBCS1J3PXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6IkNoYW5kYW5pIiwiZmFtaWx5X25hbWUiOiJNb3VyeWEiLCJpYXQiOjE3MTQzODM5MjIsImV4cCI6MTcxNDM4NzUyMn0.oPJ6iYHYUeT3Cl0P0y15XEBRk5nHD_cwO8zCB1IV_RulzLEsFFoaWX93AhwKeCDF_0ZsqIsTOV0LGmKXfDmqniHFjIF9xJ3-IfVBePT5f9brGZE4CpCh70J1SBFQNDzPUyldvAs5pFtwjqT5Zd2ynABbWBOUfCq2Pa-OT18Iqgch1QIBDtfQvBAsZRYvcH-LqHVzLkDuvROhEsQjO8VZwzKs2G_6MRwJjx4ASIrzItM2AvCo44E9VF54s7zPiJBz3fYeRVzezTab8xaGEMpGUnb8nSn7zxxVqYNniGuAmyMmOEAkThGhGnW9wR4aO_IimfIqvbdDREVKcJxnus1PWQ', 'email': 'chandani.mourya@copods.co'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Other exception')



class AccessTokenValidateViewTest(APITestCase):

    # def test_access_token_validation_success(self):
    #     url = reverse('validate_token')
    #     data = {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0MzkwNzc4LCJpYXQiOjE3MTQzOTA3MTgsImp0aSI6ImE0YzMwYTUzNWE1YjRmY2RiMTA3ZTAzOGNlMmQ1OWQ1IiwidXNlcl9pZCI6MX0.fhwp646q3x4byxQdMS1-csSCUUYTPIst3LMfNsHac3A'}
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['valid'], True)

    def test_access_token_expired(self):
        url = reverse('validate_token')
        data = {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0Mzg5MzEzLCJpYXQiOjE3MTQzODkzMDgsImp0aSI6IjU5ZTBhYjkxNjRjNTRjNWM4ODE0ZDQ3ZWUxY2ExMmU1IiwidXNlcl9pZCI6MX0.PwOQlkvrHwgHqlYq7rMQvJVSVo_DnMw9mLTHxmABLbM'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valid'], False)
        self.assertEqual(response.data['error'], 'Token is invalid or expired')

    def test_invalid_access_token(self):
        url = reverse('validate_token')
        data = {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBl'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valid'], False)
        self.assertEqual(response.data['error'], 'Token is invalid or expired')



class RefreshTokenViewTest(APITestCase):

    def test_missing_refresh_token(self):
        url = reverse('refresh_token')
        data = {}  # No refresh token provided
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Refresh token is missing')

    def test_invalid_refresh_token(self):
        url = reverse('refresh_token')
        data = {'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNDQ3NzExOCwiaWF0IjoxNzE0MzkwNzE4LCJqdGkiOiI1MWRlZWUxNDU2NjA0MDM0YTdmNzcyMWE5ZWVkNWI5ZCIsInVzZXJfaWQiOjF9.qJ1IowJD1_fxaGwPxf6IELBrSIg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token is invalid or expired')

    def test_valid_refresh_token(self):
        # Assuming a valid refresh token is provided
        valid_refresh_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNDQ3NzExOCwiaWF0IjoxNzE0MzkwNzE4LCJqdGkiOiI1MWRlZWUxNDU2NjA0MDM0YTdmNzcyMWE5ZWVkNWI5ZCIsInVzZXJfaWQiOjF9.qJ1IowJD1_fxaGwPxf6IELBrSIgx9hFbEIXmmnltd1Y'  # Replace with actual valid refresh token
        url = reverse('refresh_token')
        data = {'refresh_token': valid_refresh_token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)