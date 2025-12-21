"""
URL configuration for users app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    NotificationPreferencesViewSet,
    GoogleLoginView,
    KakaoLoginView,
)

# Create router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'notifications', NotificationPreferencesViewSet, basename='notification')

urlpatterns = [
    # JWT authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # OAuth endpoints
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('kakao/', KakaoLoginView.as_view(), name='kakao_login'),

    # Router URLs
    path('', include(router.urls)),
]
