from django.test import TestCase
from PushNotificationApp.utils import fcm_token_list

class TestUtils(TestCase):
    def test_fcm_token_list(self):
        user_id = "e7ad3e77-f31e-4557-a147-9ced3740541c"  # Example user ID
        fcm_tokens = fcm_token_list(user_id)
        print(fcm_tokens)
        self.assertIsInstance(fcm_tokens, list)
        # Add more assertions as needed