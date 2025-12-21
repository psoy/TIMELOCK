"""
Views for users app
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import NotificationPreferences
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    NotificationPreferencesSerializer,
)
from .oauth import GoogleOAuth, KakaoOAuth, get_or_create_oauth_user

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    Provides CRUD operations for user management
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        """Return queryset with prefetch"""
        return User.objects.select_related('notification_preferences').all()

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """
        Get or update current user profile
        GET /api/users/me/ - Get current user
        PATCH /api/users/me/ - Update current user
        """
        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(user).data)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Change user password
        POST /api/users/change-password/
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get', 'patch'], url_path='notifications')
    def notification_preferences(self, request):
        """
        Get or update notification preferences
        GET /api/users/notifications/ - Get preferences
        PATCH /api/users/notifications/ - Update preferences
        """
        user = request.user

        # Get or create notification preferences
        prefs, created = NotificationPreferences.objects.get_or_create(user=user)

        if request.method == 'GET':
            serializer = NotificationPreferencesSerializer(prefs)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = NotificationPreferencesSerializer(
                prefs,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class NotificationPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for NotificationPreferences model
    Read-only access (use UserViewSet.notification_preferences for updates)
    """

    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only current user's preferences"""
        return NotificationPreferences.objects.filter(user=self.request.user)


class GoogleLoginView(APIView):
    """
    Google OAuth 2.0 login endpoint
    POST /api/auth/google/
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Authenticate user with Google ID token

        Request Body:
            {
                "id_token": "google_id_token_here"
            }

        Response:
            {
                "access": "jwt_access_token",
                "refresh": "jwt_refresh_token",
                "user": {...}
            }
        """
        id_token = request.data.get('id_token')

        if not id_token:
            return Response(
                {'error': 'id_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify Google token and get user data
            user_data = GoogleOAuth.verify_token(id_token)

            # Get or create user
            user = get_or_create_oauth_user(user_data)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class KakaoLoginView(APIView):
    """
    Kakao OAuth 2.0 login endpoint
    POST /api/auth/kakao/
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Authenticate user with Kakao access token

        Request Body:
            {
                "access_token": "kakao_access_token_here"
            }

        Response:
            {
                "access": "jwt_access_token",
                "refresh": "jwt_refresh_token",
                "user": {...}
            }
        """
        access_token = request.data.get('access_token')

        if not access_token:
            return Response(
                {'error': 'access_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify Kakao token and get user data
            user_data = KakaoOAuth.verify_token(access_token)

            # Get or create user
            user = get_or_create_oauth_user(user_data)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
