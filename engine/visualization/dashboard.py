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

"""Interactive dashboard creation for batch simulation results.

Provides Dashboard class for multi-plot layouts and create_dashboard factory
function for quick dashboard generation from batch results.

Example:
    Create dashboard from batch results::

        results = batch_simulator.run_batch(num_runs=100)
        dashboard = create_dashboard(results)
        dashboard.save_html("results_dashboard.html")
"""

from pathlib import Path
from typing import Any, Dict, List

import plotly.graph_objects as go
import plotly.subplots

from engine.visualization.plotter import (
    plot_repair_distribution,
    plot_repair_time_series,
    plot_statistics_summary,
)


class Dashboard:
    """Interactive dashboard for simulation results.

    Combines multiple Plotly plots into a cohesive dashboard layout with
    interactivity and export capabilities.

    Attributes:
        figure: The Plotly Figure object containing the dashboard.
    """

    def __init__(self, figure: go.Figure) -> None:
        """Initialize dashboard with a Plotly figure.

        Args:
            figure: Plotly Figure object to display as dashboard.
        """
        self.figure = figure

    def to_html(self) -> str:
        """Export dashboard to HTML string.

        Returns:
            HTML string with embedded Plotly visualization.

        Example:
            >>> dashboard = create_dashboard(results)
            >>> html = dashboard.to_html()
            >>> assert "plotly" in html.lower()
            >>> assert len(html) > 1000
        """
        return self.figure.to_html()

    def save_html(self, output_path: Path | str) -> None:
        """Save dashboard to HTML file.

        Creates parent directories if needed.

        Args:
            output_path: Path to save HTML file.

        Example:
            >>> dashboard = create_dashboard(results)
            >>> dashboard.save_html("dashboard.html")
            >>> assert Path("dashboard.html").exists()
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.figure.write_html(str(output_path))


def create_dashboard(results: List[Dict[str, Any]]) -> Dashboard:
    """Create interactive dashboard from batch simulation results.

    Combines time series, distribution, and statistics plots into a
    multi-subplot dashboard layout.

    Args:
        results: List of result dictionaries from batch simulation.
                Each dict should have: run_id, completion_time, final_repair_count.

    Returns:
        Dashboard object with interactive Plotly visualization.

    Example:
        >>> results = [
        ...     {"run_id": i, "completion_time": 0.1*i, "final_repair_count": 90+i}
        ...     for i in range(1, 11)
        ... ]
        >>> dashboard = create_dashboard(results)
        >>> assert isinstance(dashboard, Dashboard)
        >>> html = dashboard.to_html()
        >>> assert "plotly" in html.lower()
    """
    if not results:
        # Empty dataset dashboard
        fig = go.Figure()
        fig.add_annotation(
            text="No results available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=20),
        )
        fig.update_layout(
            title="Batch Simulation Results Dashboard",
            height=800,
            template="plotly_white",
        )
        return Dashboard(fig)

    # Compute statistics
    completion_times = [r.get("completion_time", 0) for r in results]
    repair_counts = [r.get("final_repair_count", 0) for r in results]

    import statistics

    stats = {
        "num_runs": len(results),
        "mean_repair_time": (
            statistics.mean(completion_times) if completion_times else 0
        ),
        "std_repair_time": (
            statistics.stdev(completion_times) if len(completion_times) > 1 else 0
        ),
        "min_repair_time": min(completion_times) if completion_times else 0,
        "max_repair_time": max(completion_times) if completion_times else 0,
        "mean_repair_count": statistics.mean(repair_counts) if repair_counts else 0,
        "std_repair_count": (
            statistics.stdev(repair_counts) if len(repair_counts) > 1 else 0
        ),
    }

    # Create subplot figure with 2x2 layout
    fig = plotly.subplots.make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Repair Count Over Time",
            "Repair Count Distribution",
            "Time Statistics",
            "Count Statistics",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "bar"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    # Plot 1: Time series (top-left)
    if results:
        times = [r.get("completion_time", 0) for r in results]
        counts = [r.get("final_repair_count", 0) for r in results]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=counts,
                mode="lines+markers",
                name="Repair Count",
                line=dict(color="rgb(31, 119, 180)", width=2),
                marker=dict(size=6),
            ),
            row=1,
            col=1,
        )

    # Plot 2: Distribution (top-right)
    fig.add_trace(
        go.Histogram(
            x=repair_counts,
            nbinsx=15,
            name="Distribution",
            marker=dict(color="rgb(55, 128, 191)"),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # Plot 3: Time statistics (bottom-left)
    time_metrics = ["Mean", "Std Dev", "Min", "Max"]
    time_values = [
        stats["mean_repair_time"],
        stats["std_repair_time"],
        stats["min_repair_time"],
        stats["max_repair_time"],
    ]

    fig.add_trace(
        go.Bar(
            x=time_metrics,
            y=time_values,
            name="Time Stats",
            marker=dict(color="rgb(99, 110, 250)"),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Plot 4: Count statistics (bottom-right)
    count_metrics = ["Mean", "Std Dev"]
    count_values = [
        stats["mean_repair_count"],
        stats["std_repair_count"],
    ]

    fig.add_trace(
        go.Bar(
            x=count_metrics,
            y=count_values,
            name="Count Stats",
            marker=dict(color="rgb(239, 85, 59)"),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # Update layout
    fig.update_layout(
        title=f"Batch Simulation Results Dashboard (n={len(results)} runs)",
        height=800,
        template="plotly_white",
        showlegend=False,
    )

    # Update axes labels
    fig.update_xaxes(title_text="Completion Time (s)", row=1, col=1)
    fig.update_yaxes(title_text="Repair Count", row=1, col=1)

    fig.update_xaxes(title_text="Repair Count", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)

    fig.update_yaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=2)

    return Dashboard(fig)
