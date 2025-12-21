"""
Django admin configuration for plans app
"""

from django.contrib import admin
from .models import DailyPlan, TimeBlock


class TimeBlockInline(admin.TabularInline):
    """Inline admin for TimeBlock"""
    model = TimeBlock
    extra = 0
    fields = ('period', 'hour', 'title', 'category', 'planned_duration', 'actual_duration', 'is_completed')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    """DailyPlan admin with inline TimeBlocks"""

    list_display = ('user', 'date', 'completion_rate', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('user__email', 'user__username', 'brain_dump')
    date_hierarchy = 'date'
    ordering = ('-date',)

    fieldsets = (
        (None, {'fields': ('user', 'date')}),
        ('Priorities', {'fields': ('priorities',)}),
        ('Brain Dump', {'fields': ('brain_dump',)}),
        ('Statistics', {'fields': ('completion_rate',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('completion_rate', 'created_at', 'updated_at')
    inlines = [TimeBlockInline]

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(TimeBlock)
class TimeBlockAdmin(admin.ModelAdmin):
    """TimeBlock admin"""

    list_display = ('daily_plan', 'period', 'hour', 'title', 'category', 'is_completed', 'execution_rate')
    list_filter = ('period', 'is_completed', 'category', 'created_at')
    search_fields = ('title', 'description', 'daily_plan__user__email')
    ordering = ('daily_plan__date', 'period', 'hour')

    fieldsets = (
        (None, {'fields': ('daily_plan',)}),
        ('Time', {'fields': ('period', 'hour')}),
        ('Details', {'fields': ('title', 'description', 'category')}),
        ('Duration', {'fields': ('planned_duration', 'actual_duration')}),
        ('Status', {'fields': ('is_completed',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('daily_plan', 'daily_plan__user')
