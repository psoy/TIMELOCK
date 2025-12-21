"""
URL configuration for timers app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TimerSessionViewSet

# Create router
router = DefaultRouter()
router.register(r'sessions', TimerSessionViewSet, basename='timer-session')

urlpatterns = [
    path('', include(router.urls)),
]
