"""
URL configuration for statistics app
"""

from django.urls import path
from .views import DailyStatsView, WeeklyStatsView, MonthlyStatsView, HeatmapView

urlpatterns = [
    path('daily/', DailyStatsView.as_view(), name='daily_stats'),
    path('weekly/', WeeklyStatsView.as_view(), name='weekly_stats'),
    path('monthly/', MonthlyStatsView.as_view(), name='monthly_stats'),
    path('heatmap/', HeatmapView.as_view(), name='heatmap'),
]
