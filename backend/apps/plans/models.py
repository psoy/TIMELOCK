"""
DailyPlan and TimeBlock models for TIME BLOCK
Based on database_erd.md specifications
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class DailyPlan(models.Model):
    """
    Daily plan with priorities and brain dump
    One plan per user per day (UNIQUE constraint)
    JSON priorities: array of 3 strings
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_plans',
        verbose_name='User'
    )
    date = models.DateField(verbose_name='Plan Date')

    # Priorities (JSON array of 3 strings)
    priorities = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Priorities',
        help_text='Array of 3 priority tasks for the day'
    )

    # Brain dump
    brain_dump = models.TextField(null=True, blank=True, verbose_name='Brain Dump')

    # Completion rate (0-100%)
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Completion Rate (%)'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        db_table = 'daily_plans'
        verbose_name = 'Daily Plan'
        verbose_name_plural = 'Daily Plans'
        indexes = [
            models.Index(fields=['user', 'date'], name='idx_daily_plan_user_date'),
            models.Index(fields=['date'], name='idx_daily_plan_date'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_user_date')
        ]
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.email} - {self.date}'

    def get_priorities(self):
        """Return priorities array (max 3 items)"""
        if isinstance(self.priorities, list):
            return self.priorities[:3]
        return []

    def set_priorities(self, priorities_list):
        """Set priorities (max 3 items)"""
        self.priorities = priorities_list[:3] if priorities_list else []

    def calculate_completion_rate(self):
        """Calculate completion rate based on time blocks"""
        time_blocks = self.time_blocks.all()
        if not time_blocks.exists():
            return 0.00

        total_blocks = time_blocks.count()
        completed_blocks = time_blocks.filter(is_completed=True).count()

        return round((completed_blocks / total_blocks) * 100, 2)

    def update_completion_rate(self):
        """Update and save completion rate"""
        self.completion_rate = self.calculate_completion_rate()
        self.save(update_fields=['completion_rate', 'updated_at'])


class TimeBlock(models.Model):
    """
    Individual time block within a daily plan
    Represents hourly blocks (4AM-12PM, 1PM-12AM)
    UNIQUE constraint: daily_plan + period + hour
    """

    class Period(models.TextChoices):
        AM = 'am', 'AM'
        PM = 'pm', 'PM'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_plan = models.ForeignKey(
        DailyPlan,
        on_delete=models.CASCADE,
        related_name='time_blocks',
        verbose_name='Daily Plan'
    )

    # Time period (AM: 4-12, PM: 1-12)
    period = models.CharField(max_length=2, choices=Period.choices, verbose_name='Period (AM/PM)')
    hour = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Hour (1-12)'
    )

    # Block details
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Block Title')
    description = models.TextField(null=True, blank=True, verbose_name='Description')
    category = models.CharField(max_length=50, null=True, blank=True, verbose_name='Category')

    # Duration (in minutes)
    planned_duration = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        verbose_name='Planned Duration (minutes)'
    )
    actual_duration = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Actual Duration (minutes)'
    )

    # Completion status
    is_completed = models.BooleanField(default=False, verbose_name='Completed')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        db_table = 'time_blocks'
        verbose_name = 'Time Block'
        verbose_name_plural = 'Time Blocks'
        indexes = [
            models.Index(fields=['daily_plan', 'period', 'hour'], name='idx_timeblock_plan_time'),
            models.Index(fields=['category'], name='idx_timeblock_category'),
            models.Index(fields=['is_completed'], name='idx_timeblock_completed'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['daily_plan', 'period', 'hour'],
                name='unique_timeblock_period_hour'
            )
        ]
        ordering = ['period', 'hour']

    def __str__(self):
        return f'{self.daily_plan.date} {self.period.upper()} {self.hour}:00 - {self.title or "Untitled"}'

    @property
    def execution_rate(self):
        """Calculate execution rate (actual / planned * 100)"""
        if self.planned_duration == 0:
            return 0.00
        return round((self.actual_duration / self.planned_duration) * 100, 2)

    def mark_completed(self):
        """Mark block as completed"""
        self.is_completed = True
        self.save(update_fields=['is_completed', 'updated_at'])

        # Update parent daily plan's completion rate
        self.daily_plan.update_completion_rate()

    def add_actual_time(self, minutes):
        """Add minutes to actual_duration"""
        self.actual_duration += minutes
        self.save(update_fields=['actual_duration', 'updated_at'])
