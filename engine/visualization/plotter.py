
# Copyright (C) 2026 Eric C. Mumford <ericmumford@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Plotly-based visualization functions for simulation results.

Provides time series, distribution, and statistics plotting functions for
interactive result exploration.

Example:
    Plot repair time series from batch results::

        results = [
            {"run_id": i, "completion_time": 0.1*i, "final_repair_count": 90+i}
            for i in range(1, 11)
        ]
        fig = plot_repair_time_series(results)
        fig.show()
"""

from typing import Any, Dict, List

import plotly.graph_objects as go
import plotly.subplots


def plot_repair_time_series(results: List[Dict[str, Any]]) -> go.Figure:
    """Create time series plot of repair count vs completion time.

    Args:
        results: List of result dictionaries from batch simulation.
                Each dict should have: run_id, completion_time, final_repair_count.

    Returns:
        Plotly Figure with time series visualization.

    Example:
        >>> results = [
        ...     {"run_id": i, "completion_time": 0.1*i, "final_repair_count": 90+i}
        ...     for i in range(1, 11)
        ... ]
        >>> fig = plot_repair_time_series(results)
        >>> assert fig is not None
        >>> assert hasattr(fig, "to_html")
    """
    if not results:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=[], y=[], mode="lines", name="Repair Count")
        )
        fig.update_layout(
            title="Repair Count Over Time (Empty Dataset)",
            xaxis_title="Completion Time (s)",
            yaxis_title="Final Repair Count",
        )
        return fig

    run_ids = [r.get("run_id") for r in results]
    times = [r.get("completion_time") for r in results]
    repair_counts = [r.get("final_repair_count") for r in results]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=repair_counts,
            mode="lines+markers",
            name="Repair Count",
            line=dict(color="rgb(31, 119, 180)", width=2),
            marker=dict(size=8),
        )
    )

    fig.update_layout(
        title="Repair Count Over Time",
        xaxis_title="Completion Time (s)",
        yaxis_title="Final Repair Count",
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )

    return fig


def plot_repair_distribution(results: List[Dict[str, Any]]) -> go.Figure:
    """Create histogram of repair count distribution.

    Args:
        results: List of result dictionaries from batch simulation.
                Each dict should have: final_repair_count, completion_time.

    Returns:
        Plotly Figure with distribution histogram.

    Example:
        >>> results = [
        ...     {"run_id": i, "final_repair_count": 90+i, "completion_time": 0.1}
        ...     for i in range(1, 51)
        ... ]
        >>> fig = plot_repair_distribution(results)
        >>> html = fig.to_html()
        >>> assert "histogram" in html.lower() or "distribution" in html.lower()
    """
    repair_counts = [r.get("final_repair_count") for r in results]

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=repair_counts,
            nbinsx=20,
            name="Distribution",
            marker=dict(color="rgb(55, 128, 191)"),
        )
    )

    # Add mean and std lines
    if repair_counts:
        import statistics

        mean = statistics.mean(repair_counts)
        stdev = statistics.stdev(repair_counts) if len(repair_counts) > 1 else 0

        fig.add_vline(
            x=mean,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean:.1f}",
            annotation_position="top right",
        )

        if stdev > 0:
            fig.add_vline(
                x=mean + stdev,
                line_dash="dot",
                line_color="orange",
                annotation_text=f"+1σ: {mean + stdev:.1f}",
            )
            fig.add_vline(
                x=mean - stdev,
                line_dash="dot",
                line_color="orange",
            )

    fig.update_layout(
        title="Repair Count Distribution",
        xaxis_title="Final Repair Count",
        yaxis_title="Frequency",
        template="plotly_white",
        height=500,
        showlegend=True,
    )

    return fig


def plot_statistics_summary(stats: Dict[str, float]) -> go.Figure:
    """Create summary visualization of simulation statistics.

    Args:
        stats: Dictionary with keys: num_runs, mean_repair_time, std_repair_time,
              min_repair_time, max_repair_time, mean_repair_count, std_repair_count.

    Returns:
        Plotly Figure with statistics summary display.

    Example:
        >>> stats = {
        ...     "num_runs": 50,
        ...     "mean_repair_time": 0.1,
        ...     "std_repair_time": 0.02,
        ...     "min_repair_time": 0.05,
        ...     "max_repair_time": 0.15,
        ...     "mean_repair_count": 95.0,
        ...     "std_repair_count": 5.0,
        ... }
        >>> fig = plot_statistics_summary(stats)
        >>> assert fig is not None
        >>> assert hasattr(fig, "to_html")
    """
    fig = go.Figure()

    # Create two subplots for time and count metrics
    fig = plotly.subplots.make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Repair Time Statistics", "Repair Count Statistics"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
    )

    # Repair time statistics
    time_metrics = ["Mean", "Std Dev", "Min", "Max"]
    time_values = [
        stats.get("mean_repair_time", 0),
        stats.get("std_repair_time", 0),
        stats.get("min_repair_time", 0),
        stats.get("max_repair_time", 0),
    ]

    fig.add_trace(
        go.Bar(
            x=time_metrics,
            y=time_values,
            name="Repair Time (s)",
            marker=dict(color="rgb(99, 110, 250)"),
        ),
        row=1,
        col=1,
    )

    # Repair count statistics
    count_metrics = ["Mean", "Std Dev"]
    count_values = [
        stats.get("mean_repair_count", 0),
        stats.get("std_repair_count", 0),
    ]

    fig.add_trace(
        go.Bar(
            x=count_metrics,
            y=count_values,
            name="Repair Count",
            marker=dict(color="rgb(239, 85, 59)"),
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        title=f"Simulation Statistics (n={int(stats.get('num_runs', 0))} runs)",
        height=400,
        template="plotly_white",
        showlegend=True,
    )

    fig.update_yaxes(title_text="Time (s)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)

    return fig
