"""
URL configuration for plans app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DailyPlanViewSet, TimeBlockViewSet

# Create router
router = DefaultRouter()
router.register(r'daily-plans', DailyPlanViewSet, basename='daily-plan')
router.register(r'time-blocks', TimeBlockViewSet, basename='time-block')

urlpatterns = [
    path('', include(router.urls)),
]
