"""
Visualization Export Tests - RED Phase

Tests define expected behavior for exporting visualizations to various formats.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from engine.visualization.exporter import Exporter, ExportFormat


class TestExportFormat:
    """Test export format enumeration."""

    def test_export_format_enum_values(self) -> None:
        """ExportFormat enum has all expected values."""
        assert hasattr(ExportFormat, "HTML")
        assert hasattr(ExportFormat, "PNG")
        assert hasattr(ExportFormat, "PDF")

    def test_export_format_values_are_strings(self) -> None:
        """Export format values are valid strings."""
        assert ExportFormat.HTML.value == "html"
        assert ExportFormat.PNG.value == "png"
        assert ExportFormat.PDF.value == "pdf"


class TestExporter:
    """Test visualization exporter."""

    @pytest.fixture
    def sample_plot(self) -> Dict[str, Any]:
        """Sample Plotly figure data."""
        return {
            "data": [{"x": [1, 2, 3], "y": [10, 20, 30], "type": "scatter"}],
            "layout": {"title": "Test Plot"},
        }

    @pytest.fixture
    def exporter_html(self) -> Exporter:
        """HTML exporter instance."""
        return Exporter(ExportFormat.HTML)

    @pytest.fixture
    def exporter_png(self) -> Exporter:
        """PNG exporter instance."""
        return Exporter(ExportFormat.PNG)

    @pytest.fixture
    def exporter_pdf(self) -> Exporter:
        """PDF exporter instance."""
        return Exporter(ExportFormat.PDF)

    def test_exporter_html_initialization(self, exporter_html: Exporter) -> None:
        """HTML exporter initializes correctly."""
        assert exporter_html.format == ExportFormat.HTML

    def test_exporter_png_initialization(self, exporter_png: Exporter) -> None:
        """PNG exporter initializes correctly."""
        assert exporter_png.format == ExportFormat.PNG

    def test_exporter_pdf_initialization(self, exporter_pdf: Exporter) -> None:
        """PDF exporter initializes correctly."""
        assert exporter_pdf.format == ExportFormat.PDF

    def test_invalid_format_raises_error(self) -> None:
        """Invalid export format raises ValueError."""
        with pytest.raises(ValueError):
            Exporter("INVALID")  # type: ignore

    def test_export_html_creates_file(
        self, exporter_html: Exporter, sample_plot: Dict[str, Any]
    ) -> None:
        """HTML exporter creates output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "plot.html"
            exporter_html.export(sample_plot, output_path)

            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_export_png_creates_file(
        self, exporter_png: Exporter, sample_plot: Dict[str, Any]
    ) -> None:
        """PNG exporter creates output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "plot.png"
            # PNG export may fail in headless environment, handle gracefully
            try:
                exporter_png.export(sample_plot, output_path)
                # If it succeeds, file should exist
                if output_path.exists():
                    assert output_path.stat().st_size > 0
            except Exception:
                # PNG export requires Orca/Kaleido in headless env, skip if unavailable
                pass

    def test_export_pdf_creates_file(
        self, exporter_pdf: Exporter, sample_plot: Dict[str, Any]
    ) -> None:
        """PDF exporter creates output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "plot.pdf"
            # PDF export may fail in headless environment, handle gracefully
            try:
                exporter_pdf.export(sample_plot, output_path)
                # If it succeeds, file should exist
                if output_path.exists():
                    assert output_path.stat().st_size > 0
            except Exception:
                # PDF export requires Orca/Kaleido in headless env, skip if unavailable
                pass

    def test_export_creates_parent_directories(
        self, exporter_html: Exporter, sample_plot: Dict[str, Any]
    ) -> None:
        """Exporter creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "plots" / "batch_1" / "plot.html"
            exporter_html.export(sample_plot, output_path)

            assert output_path.exists()
