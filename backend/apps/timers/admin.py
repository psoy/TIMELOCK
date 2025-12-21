"""
Django admin configuration for timers app
"""

from django.contrib import admin
from .models import TimerSession


@admin.register(TimerSession)
class TimerSessionAdmin(admin.ModelAdmin):
    """TimerSession admin"""

    list_display = ('user', 'status', 'scheduled_duration_display', 'elapsed_time_display',
                   'completion_percentage', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('user__email', 'user__username', 'time_block__title')
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)

    fieldsets = (
        (None, {'fields': ('user', 'time_block')}),
        ('Duration', {'fields': ('scheduled_duration', 'elapsed_time')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {
            'fields': ('started_at', 'paused_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'completion_percentage')

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'time_block', 'time_block__daily_plan')

    def scheduled_duration_display(self, obj):
        """Display scheduled duration in minutes"""
        minutes = obj.scheduled_duration // 60
        seconds = obj.scheduled_duration % 60
        return f'{minutes}m {seconds}s'
    scheduled_duration_display.short_description = 'Scheduled'

    def elapsed_time_display(self, obj):
        """Display elapsed time in minutes"""
        minutes = obj.elapsed_time // 60
        seconds = obj.elapsed_time % 60
        return f'{minutes}m {seconds}s'
    elapsed_time_display.short_description = 'Elapsed'
