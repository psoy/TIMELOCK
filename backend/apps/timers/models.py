"""
TimerSession model for TIME BLOCK
Based on database_erd.md specifications
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from apps.plans.models import TimeBlock

User = get_user_model()


class TimerSession(models.Model):
    """
    Timer session tracking
    Records each timer execution with elapsed time and status
    Can optionally link to a TimeBlock
    """

    class Status(models.TextChoices):
        RUNNING = 'running', 'Running'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timer_sessions',
        verbose_name='User'
    )
    time_block = models.ForeignKey(
        TimeBlock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timer_sessions',
        verbose_name='Time Block (Optional)'
    )

    # Timer duration (in seconds)
    scheduled_duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Scheduled Duration (seconds)'
    )
    elapsed_time = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Elapsed Time (seconds)'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
        verbose_name='Status'
    )

    # Timestamps
    started_at = models.DateTimeField(verbose_name='Started At')
    paused_at = models.DateTimeField(null=True, blank=True, verbose_name='Paused At')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Completed At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        db_table = 'timer_sessions'
        verbose_name = 'Timer Session'
        verbose_name_plural = 'Timer Sessions'
        indexes = [
            models.Index(fields=['user', 'started_at'], name='idx_timer_user_date'),
            models.Index(fields=['time_block'], name='idx_timer_block'),
            models.Index(fields=['status'], name='idx_timer_status'),
            models.Index(fields=['completed_at'], name='idx_timer_completed'),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user.email} - {self.started_at.strftime("%Y-%m-%d %H:%M")} ({self.status})'

    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        if self.scheduled_duration == 0:
            return 0.00
        return min(round((self.elapsed_time / self.scheduled_duration) * 100, 2), 100.00)

    @property
    def remaining_time(self):
        """Calculate remaining time in seconds"""
        return max(self.scheduled_duration - self.elapsed_time, 0)

    def pause(self):
        """Pause the timer session"""
        from django.utils import timezone
        self.status = self.Status.PAUSED
        self.paused_at = timezone.now()
        self.save(update_fields=['status', 'paused_at', 'updated_at'])

    def resume(self):
        """Resume the timer session"""
        self.status = self.Status.RUNNING
        self.paused_at = None
        self.save(update_fields=['status', 'paused_at', 'updated_at'])

    def complete(self):
        """Mark timer session as completed"""
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

        # Update linked TimeBlock's actual_duration if exists
        if self.time_block:
            minutes = self.elapsed_time // 60
            self.time_block.add_actual_time(minutes)

    def cancel(self):
        """Cancel the timer session"""
        self.status = self.Status.CANCELLED
        self.save(update_fields=['status', 'updated_at'])

    def update_elapsed_time(self, elapsed_seconds):
        """Update elapsed time"""
        self.elapsed_time = min(elapsed_seconds, self.scheduled_duration)
        self.save(update_fields=['elapsed_time', 'updated_at'])
