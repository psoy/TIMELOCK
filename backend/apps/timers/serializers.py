"""
Serializers for timers app
"""

from rest_framework import serializers
from .models import TimerSession
from apps.plans.models import TimeBlock


class TimerSessionSerializer(serializers.ModelSerializer):
    """Serializer for TimerSession model"""

    completion_percentage = serializers.ReadOnlyField()
    remaining_time = serializers.ReadOnlyField()
    time_block_title = serializers.CharField(
        source='time_block.title',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = TimerSession
        fields = [
            'id',
            'user',
            'time_block',
            'time_block_title',
            'scheduled_duration',
            'elapsed_time',
            'status',
            'completion_percentage',
            'remaining_time',
            'started_at',
            'paused_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'completion_percentage',
            'remaining_time',
            'time_block_title',
            'created_at',
            'updated_at',
        ]


class TimerSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a timer session"""

    time_block_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = TimerSession
        fields = [
            'scheduled_duration',
            'time_block_id',
        ]

    def validate_scheduled_duration(self, value):
        """Validate scheduled duration (must be > 0)"""
        if value <= 0:
            raise serializers.ValidationError('Scheduled duration must be greater than 0')
        return value

    def validate_time_block_id(self, value):
        """Validate time block exists and belongs to user"""
        if value:
            request = self.context.get('request')
            try:
                time_block = TimeBlock.objects.get(
                    id=value,
                    daily_plan__user=request.user
                )
                return time_block
            except TimeBlock.DoesNotExist:
                raise serializers.ValidationError('Time block not found')
        return None

    def create(self, validated_data):
        """Create timer session with current user and started_at"""
        from django.utils import timezone

        request = self.context.get('request')
        time_block = validated_data.pop('time_block_id', None)

        timer_session = TimerSession.objects.create(
            user=request.user,
            time_block=time_block,
            scheduled_duration=validated_data['scheduled_duration'],
            started_at=timezone.now(),
            status=TimerSession.Status.RUNNING
        )

        return timer_session


class TimerSessionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating timer session"""

    class Meta:
        model = TimerSession
        fields = ['elapsed_time', 'status']

    def validate_elapsed_time(self, value):
        """Validate elapsed time"""
        if value < 0:
            raise serializers.ValidationError('Elapsed time cannot be negative')
        return value


class TimerSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""

    completion_percentage = serializers.ReadOnlyField()
    time_block_title = serializers.CharField(
        source='time_block.title',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = TimerSession
        fields = [
            'id',
            'time_block_title',
            'scheduled_duration',
            'elapsed_time',
            'status',
            'completion_percentage',
            'started_at',
            'completed_at',
        ]
