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
