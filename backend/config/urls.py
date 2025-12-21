"""
TIME BLOCK URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """API root endpoint - shows available endpoints"""
    return JsonResponse({
        'message': 'Welcome to TIMELOCK API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'login': '/api/auth/token/',
                'refresh': '/api/auth/token/refresh/',
                'user_profile': '/api/auth/users/me/',
                'notifications': '/api/auth/users/notifications/',
            },
            'plans': {
                'daily_plans': '/api/plans/daily-plans/',
                'today': '/api/plans/daily-plans/today/',
                'time_blocks': '/api/plans/time-blocks/',
            },
            'timer': {
                'sessions': '/api/timer/sessions/',
                'active': '/api/timer/sessions/active/',
                'today': '/api/timer/sessions/today/',
            },
            'statistics': {
                'daily': '/api/stats/daily/',
                'weekly': '/api/stats/weekly/',
                'monthly': '/api/stats/monthly/',
                'heatmap': '/api/stats/heatmap/',
            },
            'admin': '/admin/',
        },
        'documentation': '/api/docs/',
        'status': 'online'
    })


urlpatterns = [
    # Root endpoint
    path('', api_root, name='api-root'),

    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/plans/', include('apps.plans.urls')),
    path('api/timer/', include('apps.timers.urls')),
    path('api/stats/', include('apps.statistics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
