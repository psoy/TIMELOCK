"""
Serializers for plans app
"""

from rest_framework import serializers
from .models import DailyPlan, TimeBlock


class TimeBlockSerializer(serializers.ModelSerializer):
    """Serializer for TimeBlock model"""

    execution_rate = serializers.ReadOnlyField()

    class Meta:
        model = TimeBlock
        fields = [
            'id',
            'period',
            'hour',
            'title',
            'description',
            'category',
            'planned_duration',
            'actual_duration',
            'is_completed',
            'execution_rate',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'execution_rate', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate time block constraints"""
        period = data.get('period')
        hour = data.get('hour')

        # Validate hour range based on period
        if period == 'am' and hour not in range(4, 13):
            raise serializers.ValidationError({
                'hour': 'For AM period, hour must be between 4 and 12'
            })
        elif period == 'pm' and hour not in range(1, 13):
            raise serializers.ValidationError({
                'hour': 'For PM period, hour must be between 1 and 12'
            })

        return data


class TimeBlockCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TimeBlock"""

    class Meta:
        model = TimeBlock
        fields = [
            'period',
            'hour',
            'title',
            'description',
            'category',
            'planned_duration',
        ]


class DailyPlanSerializer(serializers.ModelSerializer):
    """Serializer for DailyPlan model with nested TimeBlocks"""

    time_blocks = TimeBlockSerializer(many=True, read_only=True)

    class Meta:
        model = DailyPlan
        fields = [
            'id',
            'user',
            'date',
            'priorities',
            'brain_dump',
            'completion_rate',
            'time_blocks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'completion_rate', 'created_at', 'updated_at']

    def validate_priorities(self, value):
        """Validate priorities array (max 3 items)"""
        if not isinstance(value, list):
            raise serializers.ValidationError('Priorities must be a list')

        if len(value) > 3:
            raise serializers.ValidationError('Maximum 3 priorities allowed')

        return value[:3]  # Ensure max 3 items

    def create(self, validated_data):
        """Create DailyPlan with current user"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class DailyPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""

    time_blocks_count = serializers.SerializerMethodField()
    completed_blocks_count = serializers.SerializerMethodField()

    class Meta:
        model = DailyPlan
        fields = [
            'id',
            'date',
            'priorities',
            'completion_rate',
            'time_blocks_count',
            'completed_blocks_count',
            'created_at',
        ]
        read_only_fields = ['id', 'completion_rate', 'created_at']

    def get_time_blocks_count(self, obj):
        """Get total time blocks count"""
        return obj.time_blocks.count()

    def get_completed_blocks_count(self, obj):
        """Get completed time blocks count"""
        return obj.time_blocks.filter(is_completed=True).count()


class DailyPlanUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating DailyPlan (auto-save)"""

    class Meta:
        model = DailyPlan
        fields = ['priorities', 'brain_dump']

    def validate_priorities(self, value):
        """Validate priorities array"""
        if not isinstance(value, list):
            raise serializers.ValidationError('Priorities must be a list')

        if len(value) > 3:
            raise serializers.ValidationError('Maximum 3 priorities allowed')

        return value[:3]
