"""
GitHub-style contribution heatmap generator
"""

from datetime import datetime, timedelta
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from django.db.models import Sum

from apps.timers.models import TimerSession


def generate_github_heatmap(user, year):
    """
    Generate GitHub-style heatmap for user's focus time

    Args:
        user: User instance
        year: Year to generate heatmap for

    Returns:
        BytesIO: PNG image buffer
    """
    # Calculate date range (52 weeks)
    end_date = datetime(year, 12, 31).date()
    start_date = end_date - timedelta(days=364)  # ~52 weeks

    # Adjust to start from Monday
    while start_date.weekday() != 0:  # 0 = Monday
        start_date -= timedelta(days=1)

    # Get all timer sessions for the year
    sessions = TimerSession.objects.filter(
        user=user,
        started_at__date__gte=start_date,
        started_at__date__lte=end_date,
        status='completed'
    ).values('started_at__date').annotate(
        total_seconds=Sum('elapsed_time')
    )

    # Create dictionary of date -> focus_time (minutes)
    focus_data = {}
    for session in sessions:
        date = session['started_at__date']
        minutes = (session['total_seconds'] or 0) // 60
        focus_data[date] = minutes

    # Create 7x52 matrix (weeks x days)
    num_weeks = 52
    data_matrix = np.zeros((7, num_weeks))

    current_date = start_date
    for week in range(num_weeks):
        for day in range(7):
            if current_date <= end_date:
                focus_time = focus_data.get(current_date, 0)
                data_matrix[day, week] = focus_time
                current_date += timedelta(days=1)

    # Create figure
    fig, ax = plt.subplots(figsize=(15, 3))

    # Define GitHub-like colors
    colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
    n_bins = 5
    cmap = LinearSegmentedColormap.from_list('github', colors, N=n_bins)

    # Define focus time levels (minutes)
    # 0: no activity
    # 1-60: light green
    # 61-180: medium green
    # 181-300: dark green
    # 301+: darkest green
    def get_level(minutes):
        if minutes == 0:
            return 0
        elif minutes <= 60:
            return 1
        elif minutes <= 180:
            return 2
        elif minutes <= 300:
            return 3
        else:
            return 4

    # Convert data to levels
    level_matrix = np.vectorize(get_level)(data_matrix)

    # Plot heatmap
    im = ax.imshow(level_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=4)

    # Configure axes
    ax.set_yticks(range(7))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=8)

    # Set month labels
    month_positions = []
    month_labels = []
    current_date = start_date

    for week in range(num_weeks):
        if current_date.day <= 7 or week == 0:
            month_positions.append(week)
            month_labels.append(current_date.strftime('%b'))
        current_date += timedelta(days=7)

    ax.set_xticks(month_positions)
    ax.set_xticklabels(month_labels, fontsize=8)

    # Remove tick marks
    ax.tick_params(length=0)

    # Add grid
    ax.set_xticks(np.arange(num_weeks) - 0.5, minor=True)
    ax.set_yticks(np.arange(7) - 0.5, minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)

    # Add title
    ax.set_title(f'{year} Focus Time Heatmap', fontsize=12, pad=10)

    # Add legend
    legend_labels = [
        'No activity',
        '< 1h',
        '1-3h',
        '3-5h',
        '5h+'
    ]
    legend_colors = [colors[i] for i in range(5)]
    patches = [mpatches.Patch(color=legend_colors[i], label=legend_labels[i])
               for i in range(5)]
    ax.legend(handles=patches, loc='upper left', bbox_to_anchor=(1, 1),
              fontsize=8, frameon=False)

    # Tight layout
    plt.tight_layout()

    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)

    return buffer
