import os
import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from decouple import config

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": config('FIREBASE_PROJECT_ID'),
    "private_key_id": config('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": config('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": config('FIREBASE_CLIENT_EMAIL'),
    "client_id": config('FIREBASE_CLIENT_ID'),
    "auth_uri": config('FIREBASE_AUTH_URI'),
    "token_uri": config('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": config('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": config('FIREBASE_CLIENT_X509_CERT_URL'),
})
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

class FirebaseAuthentication(ModelBackend):
    def authenticate(self, request, token=None, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', f'firebase_user_{uid}')
            
            # Try to find or create a Django user
            user, created = User.objects.get_or_create(
                username=email.split('@')[0] if '@' in email else uid,
                defaults={'email': email, 'is_active': True}
            )
            return user
        except Exception as e:
            print(f"Firebase auth error: {str(e)}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None