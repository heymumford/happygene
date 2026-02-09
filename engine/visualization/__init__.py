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

"""Visualization module for HappyGene simulation results.

Provides interactive Plotly-based visualizations for batch simulation results,
including time series plots, distribution analysis, dashboards, and export capabilities.

Examples:
    Create and display plots from batch results::

        from engine.visualization.plotter import plot_repair_time_series
        results = batch_simulator.run_batch(num_runs=50)
        fig = plot_repair_time_series(results)
        fig.show()

    Export dashboard to HTML::

        from engine.visualization.dashboard import create_dashboard
        dashboard = create_dashboard(results)
        dashboard.save_html("results.html")

    Export to multiple formats::

        from engine.visualization.exporter import Exporter, ExportFormat
        exporter = Exporter(ExportFormat.PDF)
        exporter.export(fig, "plot.pdf")
"""
