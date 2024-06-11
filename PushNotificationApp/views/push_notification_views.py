import firebase_admin
from firebase_admin import credentials, messaging

server_key = 'PushNotificationApp/views/leave-tracking-f2849-firebase-adminsdk-dcmyh-8bd39fbecf.json'

# Initialize Firebase app
firebase_cred = credentials.Certificate(server_key)
firebase_app = firebase_admin.initialize_app(firebase_cred)




print("Firebase app initialized")
print("Firebase app name: ", firebase_app.name)
print("Firebase app project_id: ", firebase_app.project_id)

# Function to send push notification to multiple tokens

def send_token_push(title, body, tokens):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=tokens
    )
    response = messaging.send_multicast(message)
    if response.failure_count > 0:
        print(f'Failed to send to {response.failure_count} tokens due to {list(map(lambda e: e.reason, response.responses))}')
    else:
        print(f'Successfully sent message to all tokens.')

# Example usage
tokens = ["c5x_tmvYRw-NvPtH2Kb_eK:APA91bGLplNOMOspkLpz8jpV9YN2iHJ17RWmztv0B_9Sht3IUJVvDxE9hen5OhqZg_XM2FbBOkH890oBYIDiiRZEmKH9k01Mx75Bs7rZbhfrmisoOP7xH0Lil9-a1DragTcS3pPVgVn4"]
# Replace with actual registration tokens

send_token_push("Hello", "frontend", tokens)