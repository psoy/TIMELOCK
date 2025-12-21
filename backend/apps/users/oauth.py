"""
OAuth 2.0 authentication helpers for Google and Kakao
"""

import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed


class GoogleOAuth:
    """Google OAuth 2.0 authentication handler"""

    @staticmethod
    def verify_token(token):
        """
        Verify Google ID token and return user info

        Args:
            token (str): Google ID token from frontend

        Returns:
            dict: User information from Google

        Raises:
            AuthenticationFailed: If token is invalid
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            # Verify token issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise AuthenticationFailed('Invalid token issuer')

            # Extract user information
            user_data = {
                'email': idinfo.get('email'),
                'username': idinfo.get('name', idinfo.get('email').split('@')[0]),
                'oauth_id': idinfo.get('sub'),
                'profile_image': idinfo.get('picture'),
                'oauth_provider': 'google',
            }

            # Verify email is present
            if not user_data['email']:
                raise AuthenticationFailed('Email not provided by Google')

            return user_data

        except ValueError as e:
            raise AuthenticationFailed(f'Invalid Google token: {str(e)}')
        except Exception as e:
            raise AuthenticationFailed(f'Google authentication failed: {str(e)}')


class KakaoOAuth:
    """Kakao OAuth 2.0 authentication handler"""

    KAKAO_USER_INFO_URL = 'https://kapi.kakao.com/v2/user/me'

    @staticmethod
    def verify_token(access_token):
        """
        Verify Kakao access token and return user info

        Args:
            access_token (str): Kakao access token from frontend

        Returns:
            dict: User information from Kakao

        Raises:
            AuthenticationFailed: If token is invalid
        """
        try:
            # Request user info from Kakao API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
            }

            response = requests.get(
                KakaoOAuth.KAKAO_USER_INFO_URL,
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                raise AuthenticationFailed('Invalid Kakao token')

            user_info = response.json()

            # Extract user information
            kakao_account = user_info.get('kakao_account', {})
            profile = kakao_account.get('profile', {})

            email = kakao_account.get('email')
            if not email:
                raise AuthenticationFailed('Email not provided by Kakao')

            user_data = {
                'email': email,
                'username': profile.get('nickname', email.split('@')[0]),
                'oauth_id': str(user_info.get('id')),
                'profile_image': profile.get('profile_image_url'),
                'oauth_provider': 'kakao',
            }

            return user_data

        except requests.RequestException as e:
            raise AuthenticationFailed(f'Kakao API request failed: {str(e)}')
        except Exception as e:
            raise AuthenticationFailed(f'Kakao authentication failed: {str(e)}')


def get_or_create_oauth_user(user_data):
    """
    Get or create user from OAuth provider data

    Args:
        user_data (dict): User data from OAuth provider

    Returns:
        User: User instance
    """
    from .models import User, NotificationPreferences

    oauth_provider = user_data['oauth_provider']
    oauth_id = user_data['oauth_id']
    email = user_data['email']

    # Try to find user by OAuth provider and ID
    user = User.objects.filter(
        oauth_provider=oauth_provider,
        oauth_id=oauth_id
    ).first()

    if user:
        # Update existing user's profile image if changed
        if user_data.get('profile_image') and user.profile_image != user_data['profile_image']:
            user.profile_image = user_data['profile_image']
            user.save(update_fields=['profile_image', 'updated_at'])
        return user

    # Try to find user by email (for linking existing accounts)
    user = User.objects.filter(email=email).first()

    if user:
        # Link existing account to OAuth provider
        user.oauth_provider = oauth_provider
        user.oauth_id = oauth_id
        if user_data.get('profile_image'):
            user.profile_image = user_data['profile_image']
        user.save(update_fields=['oauth_provider', 'oauth_id', 'profile_image', 'updated_at'])
        return user

    # Create new user
    user = User.objects.create(
        email=email,
        username=user_data['username'],
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
        profile_image=user_data.get('profile_image'),
    )

    # Create default notification preferences
    NotificationPreferences.objects.create(user=user)

    return user
