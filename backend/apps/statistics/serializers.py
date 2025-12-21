"""
Serializers for statistics app
"""

from rest_framework import serializers


class DailyStatsSerializer(serializers.Serializer):
    """Serializer for daily statistics"""
    date = serializers.DateField()
    total_focus_time = serializers.IntegerField(help_text="Total focus time in minutes")
    total_blocks = serializers.IntegerField(help_text="Total number of time blocks")
    completed_blocks = serializers.IntegerField(help_text="Number of completed blocks")
    block_completion_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentage of blocks completed"
    )
    execution_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentage of planned time executed"
    )
    category_breakdown = serializers.DictField(
        child=serializers.IntegerField(), help_text="Focus time by category (minutes)"
    )
    hourly_breakdown = serializers.ListField(
        child=serializers.DictField(), help_text="Focus time by hour"
    )


class WeeklyStatsSerializer(serializers.Serializer):
    """Serializer for weekly statistics"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_focus_time = serializers.IntegerField(help_text="Total focus time in minutes")
    average_daily_focus = serializers.IntegerField(help_text="Average daily focus time in minutes")
    total_blocks = serializers.IntegerField()
    completed_blocks = serializers.IntegerField()
    block_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    execution_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    daily_breakdown = serializers.ListField(child=serializers.DictField())
    category_breakdown = serializers.DictField(child=serializers.IntegerField())


class MonthlyStatsSerializer(serializers.Serializer):
    """Serializer for monthly statistics"""
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    total_focus_time = serializers.IntegerField(help_text="Total focus time in minutes")
    average_daily_focus = serializers.IntegerField(help_text="Average daily focus time in minutes")
    total_blocks = serializers.IntegerField()
    completed_blocks = serializers.IntegerField()
    block_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    execution_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    weekly_breakdown = serializers.ListField(child=serializers.DictField())
    category_breakdown = serializers.DictField(child=serializers.IntegerField())
    most_productive_day = serializers.CharField(allow_null=True)
    most_productive_hour = serializers.IntegerField(allow_null=True)
