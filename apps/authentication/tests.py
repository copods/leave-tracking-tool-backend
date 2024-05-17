from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone

class GoogleSignInViewTest(APITestCase):

    #(WIP) failing coz of token
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_sign_in_success(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.return_value = {'email': 'chandani.mourya@copods.co'}
        url = reverse('googleSignIn')
        data = {'token': 'here we need to pass token', 'email': 'chandani.mourya@copods.co'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_sign_in_email_mismatch(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.return_value = {'email': 'chandani.mourya@copods.co'}
        url = reverse('googleSignIn')
        data = {'token': 'here we need to pass token', 'email': 'mismatch@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid Credentials.')

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
        data = {'token': 'here we need to pass token', 'email': 'chandani.mourya@copods.co'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Other exception')



class AccessTokenValidateViewTest(APITestCase):
# (WIP) Test case fialing
    # def test_access_token_validation_success(self):
    #     url = reverse('validate_token')
    #     data = {'access_token': 'have to add access token'}
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['valid'], True)

    def test_access_token_expired(self):
        url = reverse('validate_token')
        data = {'access_token': 'have to add access token'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valid'], False)
        self.assertEqual(response.data['error'], 'Token is invalid or expired')

    def test_invalid_access_token(self):
        url = reverse('validate_token')
        data = {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBl'} #invalid access token 
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
        data = {'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXB'} #invalid refresh token
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token is invalid or expired')

#(WIP) refresh token is needed
    def test_valid_refresh_token(self):
        # Assuming a valid refresh token is provided
        valid_refresh_token = ''  # Replace with actual valid refresh token
        url = reverse('refresh_token')
        data = {'refresh_token': valid_refresh_token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)