"""
Views for statistics app
"""

from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.timers.models import TimerSession
from apps.plans.models import DailyPlan, TimeBlock
from .serializers import DailyStatsSerializer, WeeklyStatsSerializer, MonthlyStatsSerializer


class DailyStatsView(APIView):
    """
    Get daily statistics
    GET /api/stats/daily/?date=YYYY-MM-DD
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get statistics for a specific date"""
        date_str = request.query_params.get('date')

        if not date_str:
            # Default to today
            target_date = timezone.now().date()
        else:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Get timer sessions for the date
        sessions = TimerSession.objects.filter(
            user=request.user,
            started_at__date=target_date,
            status__in=['completed', 'cancelled']
        )

        # Get time blocks for the date
        try:
            daily_plan = DailyPlan.objects.get(user=request.user, date=target_date)
            time_blocks = TimeBlock.objects.filter(daily_plan=daily_plan)
        except DailyPlan.DoesNotExist:
            daily_plan = None
            time_blocks = TimeBlock.objects.none()

        # Calculate total focus time (from completed sessions)
        completed_sessions = sessions.filter(status='completed')
        total_focus_seconds = completed_sessions.aggregate(
            total=Sum('elapsed_time')
        )['total'] or 0
        total_focus_time = total_focus_seconds // 60  # Convert to minutes

        # Calculate block statistics
        total_blocks = time_blocks.count()
        completed_blocks = time_blocks.filter(is_completed=True).count()

        if total_blocks > 0:
            block_completion_rate = (completed_blocks / total_blocks) * 100
        else:
            block_completion_rate = 0

        # Calculate execution rate (actual time vs planned time)
        planned_duration = time_blocks.aggregate(
            total=Sum('planned_duration')
        )['total'] or 0

        actual_duration = time_blocks.aggregate(
            total=Sum('actual_duration')
        )['total'] or 0

        if planned_duration > 0:
            execution_rate = (actual_duration / planned_duration) * 100
        else:
            execution_rate = 0

        # Category breakdown
        category_breakdown = {}
        for block in time_blocks:
            category = block.category or 'uncategorized'
            category_breakdown[category] = category_breakdown.get(category, 0) + (block.actual_duration or 0)

        # Hourly breakdown
        hourly_breakdown = []
        for hour in range(24):
            hour_blocks = time_blocks.filter(hour=hour)
            hour_focus = sum(block.actual_duration or 0 for block in hour_blocks)
            if hour_focus > 0:
                hourly_breakdown.append({
                    'hour': hour,
                    'focus_time': hour_focus,
                    'blocks': hour_blocks.count()
                })

        stats = {
            'date': target_date,
            'total_focus_time': total_focus_time,
            'total_blocks': total_blocks,
            'completed_blocks': completed_blocks,
            'block_completion_rate': round(block_completion_rate, 2),
            'execution_rate': round(execution_rate, 2),
            'category_breakdown': category_breakdown,
            'hourly_breakdown': hourly_breakdown
        }

        serializer = DailyStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeeklyStatsView(APIView):
    """
    Get weekly statistics
    GET /api/stats/weekly/?start_date=YYYY-MM-DD
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get statistics for a week starting from start_date"""
        start_date_str = request.query_params.get('start_date')

        if not start_date_str:
            # Default to current week (Monday)
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        end_date = start_date + timedelta(days=6)

        # Get all daily plans for the week
        daily_plans = DailyPlan.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )

        # Get all time blocks for the week
        time_blocks = TimeBlock.objects.filter(
            daily_plan__in=daily_plans
        )

        # Calculate totals
        total_blocks = time_blocks.count()
        completed_blocks = time_blocks.filter(is_completed=True).count()

        total_focus_time = sum(block.actual_duration or 0 for block in time_blocks)
        average_daily_focus = total_focus_time // 7 if total_focus_time > 0 else 0

        planned_duration = time_blocks.aggregate(total=Sum('planned_duration'))['total'] or 0
        actual_duration = time_blocks.aggregate(total=Sum('actual_duration'))['total'] or 0

        block_completion_rate = (completed_blocks / total_blocks * 100) if total_blocks > 0 else 0
        execution_rate = (actual_duration / planned_duration * 100) if planned_duration > 0 else 0

        # Daily breakdown
        daily_breakdown = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_blocks = time_blocks.filter(daily_plan__date=day)
            day_focus = sum(block.actual_duration or 0 for block in day_blocks)
            daily_breakdown.append({
                'date': day.isoformat(),
                'focus_time': day_focus,
                'blocks': day_blocks.count(),
                'completed_blocks': day_blocks.filter(is_completed=True).count()
            })

        # Category breakdown
        category_breakdown = {}
        for block in time_blocks:
            category = block.category or 'uncategorized'
            category_breakdown[category] = category_breakdown.get(category, 0) + (block.actual_duration or 0)

        stats = {
            'start_date': start_date,
            'end_date': end_date,
            'total_focus_time': total_focus_time,
            'average_daily_focus': average_daily_focus,
            'total_blocks': total_blocks,
            'completed_blocks': completed_blocks,
            'block_completion_rate': round(block_completion_rate, 2),
            'execution_rate': round(execution_rate, 2),
            'daily_breakdown': daily_breakdown,
            'category_breakdown': category_breakdown
        }

        serializer = WeeklyStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyStatsView(APIView):
    """
    Get monthly statistics
    GET /api/stats/monthly/?year=2025&month=12
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get statistics for a specific month"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not year or not month:
            # Default to current month
            now = timezone.now()
            year = now.year
            month = now.month
        else:
            try:
                year = int(year)
                month = int(month)
                if month < 1 or month > 12:
                    raise ValueError
            except ValueError:
                return Response(
                    {'error': 'Invalid year or month'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Get all daily plans for the month
        daily_plans = DailyPlan.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        )

        # Get all time blocks for the month
        time_blocks = TimeBlock.objects.filter(
            daily_plan__in=daily_plans
        )

        # Calculate totals
        total_blocks = time_blocks.count()
        completed_blocks = time_blocks.filter(is_completed=True).count()

        total_focus_time = sum(block.actual_duration or 0 for block in time_blocks)

        # Calculate days in month
        from calendar import monthrange
        days_in_month = monthrange(year, month)[1]
        average_daily_focus = total_focus_time // days_in_month if total_focus_time > 0 else 0

        planned_duration = time_blocks.aggregate(total=Sum('planned_duration'))['total'] or 0
        actual_duration = time_blocks.aggregate(total=Sum('actual_duration'))['total'] or 0

        block_completion_rate = (completed_blocks / total_blocks * 100) if total_blocks > 0 else 0
        execution_rate = (actual_duration / planned_duration * 100) if planned_duration > 0 else 0

        # Weekly breakdown
        weekly_breakdown = []
        start_date = datetime(year, month, 1).date()
        current_week_start = start_date - timedelta(days=start_date.weekday())

        for week_num in range(6):  # Max 6 weeks in a month
            week_start = current_week_start + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)

            # Only include if week overlaps with the month
            if week_start.month == month or week_end.month == month:
                week_blocks = time_blocks.filter(
                    daily_plan__date__gte=week_start,
                    daily_plan__date__lte=week_end
                )
                week_focus = sum(block.actual_duration or 0 for block in week_blocks)

                if week_focus > 0:
                    weekly_breakdown.append({
                        'week_start': week_start.isoformat(),
                        'week_end': week_end.isoformat(),
                        'focus_time': week_focus,
                        'blocks': week_blocks.count()
                    })

        # Category breakdown
        category_breakdown = {}
        for block in time_blocks:
            category = block.category or 'uncategorized'
            category_breakdown[category] = category_breakdown.get(category, 0) + (block.actual_duration or 0)

        # Find most productive day and hour
        most_productive_day = None
        most_productive_hour = None

        if daily_plans.exists():
            # Group by day of week
            from collections import defaultdict
            day_totals = defaultdict(int)
            hour_totals = defaultdict(int)

            for block in time_blocks:
                if block.actual_duration:
                    # Day of week (0=Monday, 6=Sunday)
                    day_of_week = block.daily_plan.date.weekday()
                    day_totals[day_of_week] += block.actual_duration

                    # Hour
                    hour_totals[block.hour] += block.actual_duration

            if day_totals:
                most_productive_day_num = max(day_totals, key=day_totals.get)
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                most_productive_day = days[most_productive_day_num]

            if hour_totals:
                most_productive_hour = max(hour_totals, key=hour_totals.get)

        stats = {
            'year': year,
            'month': month,
            'total_focus_time': total_focus_time,
            'average_daily_focus': average_daily_focus,
            'total_blocks': total_blocks,
            'completed_blocks': completed_blocks,
            'block_completion_rate': round(block_completion_rate, 2),
            'execution_rate': round(execution_rate, 2),
            'weekly_breakdown': weekly_breakdown,
            'category_breakdown': category_breakdown,
            'most_productive_day': most_productive_day,
            'most_productive_hour': most_productive_hour
        }

        serializer = MonthlyStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HeatmapView(APIView):
    """
    Get GitHub-style heatmap
    GET /api/stats/heatmap/?year=2025
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Generate and return heatmap image"""
        from django.http import HttpResponse
        from .heatmap import generate_github_heatmap

        year = request.query_params.get('year')

        if not year:
            # Default to current year
            year = timezone.now().year
        else:
            try:
                year = int(year)
                if year < 2000 or year > 2100:
                    raise ValueError
            except ValueError:
                return Response(
                    {'error': 'Invalid year'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            # Generate heatmap
            buffer = generate_github_heatmap(request.user, year)

            # Return PNG image
            return HttpResponse(buffer.getvalue(), content_type='image/png')

        except Exception as e:
            return Response(
                {'error': f'Failed to generate heatmap: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
