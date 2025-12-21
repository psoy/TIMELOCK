"""
Views for timers app
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from .models import TimerSession
from .serializers import (
    TimerSessionSerializer,
    TimerSessionCreateSerializer,
    TimerSessionUpdateSerializer,
    TimerSessionListSerializer,
)


class TimerSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TimerSession model
    Provides CRUD operations for timer sessions
    """

    serializer_class = TimerSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only current user's timer sessions"""
        queryset = TimerSession.objects.filter(
            user=self.request.user
        ).select_related('time_block', 'time_block__daily_plan').order_by('-started_at')

        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by date if provided
        date_param = self.request.query_params.get('date')
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                queryset = queryset.filter(started_at__date=filter_date)
            except ValueError:
                pass

        # Filter by time_block if provided
        time_block_id = self.request.query_params.get('time_block')
        if time_block_id:
            queryset = queryset.filter(time_block_id=time_block_id)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'list':
            return TimerSessionListSerializer
        elif self.action == 'create':
            return TimerSessionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TimerSessionUpdateSerializer
        return TimerSessionSerializer

    @action(detail=True, methods=['post'], url_path='pause')
    def pause(self, request, pk=None):
        """
        Pause a running timer session
        POST /api/timer-sessions/{id}/pause/
        """
        timer_session = self.get_object()

        if timer_session.status != TimerSession.Status.RUNNING:
            return Response(
                {'detail': 'Timer is not running'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timer_session.pause()

        return Response({
            'status': timer_session.status,
            'paused_at': timer_session.paused_at,
            'detail': 'Timer paused successfully'
        })

    @action(detail=True, methods=['post'], url_path='resume')
    def resume(self, request, pk=None):
        """
        Resume a paused timer session
        POST /api/timer-sessions/{id}/resume/
        """
        timer_session = self.get_object()

        if timer_session.status != TimerSession.Status.PAUSED:
            return Response(
                {'detail': 'Timer is not paused'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timer_session.resume()

        return Response({
            'status': timer_session.status,
            'detail': 'Timer resumed successfully'
        })

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Mark timer session as completed
        POST /api/timer-sessions/{id}/complete/
        """
        timer_session = self.get_object()

        if timer_session.status == TimerSession.Status.COMPLETED:
            return Response(
                {'detail': 'Timer already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timer_session.complete()

        return Response({
            'status': timer_session.status,
            'completed_at': timer_session.completed_at,
            'detail': 'Timer completed successfully'
        })

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Cancel a timer session
        POST /api/timer-sessions/{id}/cancel/
        """
        timer_session = self.get_object()

        if timer_session.status in [TimerSession.Status.COMPLETED, TimerSession.Status.CANCELLED]:
            return Response(
                {'detail': 'Timer already finished'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timer_session.cancel()

        return Response({
            'status': timer_session.status,
            'detail': 'Timer cancelled successfully'
        })

    @action(detail=True, methods=['post'], url_path='update-elapsed')
    def update_elapsed(self, request, pk=None):
        """
        Update elapsed time
        POST /api/timer-sessions/{id}/update-elapsed/
        Body: {"elapsed_seconds": 120}
        """
        timer_session = self.get_object()
        elapsed_seconds = request.data.get('elapsed_seconds')

        if elapsed_seconds is None or not isinstance(elapsed_seconds, (int, float)):
            return Response(
                {'detail': 'Invalid elapsed_seconds value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timer_session.update_elapsed_time(int(elapsed_seconds))

        return Response({
            'elapsed_time': timer_session.elapsed_time,
            'completion_percentage': timer_session.completion_percentage,
            'remaining_time': timer_session.remaining_time,
            'detail': f'Elapsed time updated to {elapsed_seconds} seconds'
        })

    @action(detail=False, methods=['get'], url_path='active')
    def active(self, request):
        """
        Get active (running or paused) timer sessions
        GET /api/timer-sessions/active/
        """
        active_sessions = self.get_queryset().filter(
            status__in=[TimerSession.Status.RUNNING, TimerSession.Status.PAUSED]
        )

        serializer = TimerSessionListSerializer(active_sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        """
        Get today's timer sessions
        GET /api/timer-sessions/today/
        """
        from datetime import date

        today_sessions = self.get_queryset().filter(started_at__date=date.today())

        serializer = TimerSessionListSerializer(today_sessions, many=True)
        return Response(serializer.data)
