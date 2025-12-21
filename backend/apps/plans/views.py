"""
Views for plans app
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, date

from .models import DailyPlan, TimeBlock
from .serializers import (
    DailyPlanSerializer,
    DailyPlanListSerializer,
    DailyPlanUpdateSerializer,
    TimeBlockSerializer,
    TimeBlockCreateSerializer,
)


class DailyPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DailyPlan model
    Provides CRUD operations for daily plans
    """

    serializer_class = DailyPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only current user's plans with prefetch"""
        queryset = DailyPlan.objects.filter(
            user=self.request.user
        ).prefetch_related('time_blocks').order_by('-date')

        # Filter by date if provided
        date_param = self.request.query_params.get('date')
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                queryset = queryset.filter(date=filter_date)
            except ValueError:
                pass

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return DailyPlanListSerializer
        elif self.action in ['update', 'partial_update']:
            return DailyPlanUpdateSerializer
        return DailyPlanSerializer

    def perform_create(self, serializer):
        """Create plan with current user"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate_completion(self, request, pk=None):
        """
        Recalculate and update completion rate
        POST /api/plans/{id}/recalculate/
        """
        plan = self.get_object()
        plan.update_completion_rate()

        return Response({
            'completion_rate': str(plan.completion_rate),
            'detail': 'Completion rate updated'
        })

    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        """
        Get today's plan
        GET /api/plans/today/
        """
        today = date.today()
        plan = DailyPlan.objects.filter(
            user=request.user,
            date=today
        ).prefetch_related('time_blocks').first()

        if not plan:
            return Response(
                {'detail': 'No plan found for today'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DailyPlanSerializer(plan)
        return Response(serializer.data)


class TimeBlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TimeBlock model
    Provides CRUD operations for time blocks
    """

    serializer_class = TimeBlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return time blocks for current user's plans"""
        queryset = TimeBlock.objects.filter(
            daily_plan__user=self.request.user
        ).select_related('daily_plan').order_by('period', 'hour')

        # Filter by daily_plan if provided
        plan_id = self.request.query_params.get('daily_plan')
        if plan_id:
            queryset = queryset.filter(daily_plan_id=plan_id)

        # Filter by date if provided
        date_param = self.request.query_params.get('date')
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                queryset = queryset.filter(daily_plan__date=filter_date)
            except ValueError:
                pass

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'create':
            return TimeBlockCreateSerializer
        return TimeBlockSerializer

    def perform_create(self, serializer):
        """Create time block for a daily plan"""
        daily_plan_id = self.request.data.get('daily_plan_id')

        if not daily_plan_id:
            raise serializers.ValidationError({'daily_plan_id': 'This field is required'})

        # Get the daily plan (must belong to current user)
        daily_plan = get_object_or_404(
            DailyPlan,
            id=daily_plan_id,
            user=self.request.user
        )

        serializer.save(daily_plan=daily_plan)

    @action(detail=True, methods=['post'], url_path='mark-completed')
    def mark_completed(self, request, pk=None):
        """
        Mark time block as completed
        POST /api/time-blocks/{id}/mark-completed/
        """
        time_block = self.get_object()
        time_block.mark_completed()

        return Response({
            'is_completed': time_block.is_completed,
            'detail': 'Time block marked as completed'
        })

    @action(detail=True, methods=['post'], url_path='add-time')
    def add_time(self, request, pk=None):
        """
        Add actual time to time block
        POST /api/time-blocks/{id}/add-time/
        Body: {"minutes": 30}
        """
        time_block = self.get_object()
        minutes = request.data.get('minutes')

        if not minutes or not isinstance(minutes, (int, float)):
            return Response(
                {'detail': 'Invalid minutes value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        time_block.add_actual_time(int(minutes))

        return Response({
            'actual_duration': time_block.actual_duration,
            'execution_rate': time_block.execution_rate,
            'detail': f'Added {minutes} minutes to actual duration'
        })
