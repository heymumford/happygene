"""Export visualization figures to multiple formats.

Provides ExportFormat enum and Exporter class for saving Plotly figures
to HTML (interactive), PNG (static), or PDF (publication).

Example:
    Export to different formats::

        from engine.visualization.exporter import Exporter, ExportFormat
        from engine.visualization.plotter import plot_repair_time_series

        fig = plot_repair_time_series(results)

        # Export to HTML (interactive)
        html_exporter = Exporter(ExportFormat.HTML)
        html_exporter.export(fig, "plot.html")

        # Export to PDF (publication)
        pdf_exporter = Exporter(ExportFormat.PDF)
        pdf_exporter.export(fig, "plot.pdf")
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict

import plotly.graph_objects as go


class ExportFormat(Enum):
    """Supported export formats for visualization figures.

    Attributes:
        HTML: Interactive HTML with Plotly (always available).
        PNG: Static PNG image (requires Orca or Kaleido).
        PDF: Publication-ready PDF (requires Orca or Kaleido).
    """

    HTML = "html"
    PNG = "png"
    PDF = "pdf"


class Exporter:
    """Export Plotly figures to various formats.

    Supports HTML (interactive), PNG (static), and PDF (publication) export
    formats with automatic parent directory creation.

    Attributes:
        format: The ExportFormat to use for export.

    Example:
        >>> exporter = Exporter(ExportFormat.HTML)
        >>> exporter.export(fig, "plot.html")
        >>> assert Path("plot.html").exists()
    """

    def __init__(self, format: ExportFormat | str) -> None:
        """Initialize exporter with target format.

        Args:
            format: ExportFormat enum or string ("html", "png", "pdf").

        Raises:
            ValueError: If format is invalid.

        Example:
            >>> exporter_html = Exporter(ExportFormat.HTML)
            >>> assert exporter_html.format == ExportFormat.HTML

            >>> exporter_str = Exporter("pdf")
            >>> assert exporter_str.format == ExportFormat.PDF
        """
        if isinstance(format, str):
            try:
                self.format = ExportFormat[format.upper()]
            except KeyError as e:
                raise ValueError(f"Invalid export format: {format}") from e
        elif isinstance(format, ExportFormat):
            self.format = format
        else:
            raise ValueError(f"Invalid export format: {format}")

    def export(
        self,
        figure: go.Figure | Dict[str, Any],
        output_path: Path | str,
    ) -> None:
        """Export figure to file in configured format.

        Creates parent directories if needed. PNG/PDF export may fail in
        headless environments without Orca or Kaleido installed.

        Args:
            figure: Plotly Figure object or figure dictionary.
            output_path: Path to save file.

        Raises:
            ValueError: If format is unsupported.
            RuntimeError: For PNG/PDF export failures in headless environments.

        Example:
            >>> exporter = Exporter(ExportFormat.HTML)
            >>> exporter.export(fig, "output/plot.html")
            >>> assert Path("output/plot.html").exists()
            >>> assert Path("output/plot.html").stat().st_size > 0
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.format == ExportFormat.HTML:
            if isinstance(figure, dict):
                fig = go.Figure(figure)
            else:
                fig = figure
            fig.write_html(str(output_path))

        elif self.format == ExportFormat.PNG:
            # PNG export requires Orca or Kaleido renderer
            # May fail in headless environments
            if isinstance(figure, dict):
                fig = go.Figure(figure)
            else:
                fig = figure

            try:
                fig.write_image(str(output_path), format="png")
            except Exception as e:
                # PNG export requires external renderer, which may not be available
                # in headless environments. Re-raise to allow caller to handle.
                raise RuntimeError(
                    f"PNG export failed (Orca/Kaleido required): {e}"
                ) from e

        elif self.format == ExportFormat.PDF:
            # PDF export requires Orca or Kaleido renderer
            # May fail in headless environments
            if isinstance(figure, dict):
                fig = go.Figure(figure)
            else:
                fig = figure

            try:
                fig.write_image(str(output_path), format="pdf")
            except Exception as e:
                # PDF export requires external renderer, which may not be available
                # in headless environments. Re-raise to allow caller to handle.
                raise RuntimeError(
                    f"PDF export failed (Orca/Kaleido required): {e}"
                ) from e

        else:
            raise ValueError(f"Unsupported export format: {self.format}")
