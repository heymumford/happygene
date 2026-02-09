"""
Visualization Dashboard Tests - RED Phase

Tests define expected behavior for interactive dashboards.
"""

import tempfile
from pathlib import Path
from typing import List, Dict, Any

import pytest

from engine.visualization.dashboard import Dashboard, create_dashboard


class TestDashboard:
    """Test interactive dashboard creation."""

    @pytest.fixture
    def sample_results(self) -> List[Dict[str, Any]]:
        """Sample batch results for dashboard."""
        return [
            {
                "run_id": i,
                "completion_time": 0.1 * i,
                "final_repair_count": 90 + i,
                "dose_gy": 3.0,
                "status": "complete",
            }
            for i in range(1, 11)
        ]

    def test_create_dashboard_returns_dashboard(
        self, sample_results: List[Dict[str, Any]]
    ) -> None:
        """Dashboard factory function returns Dashboard object."""
        dashboard = create_dashboard(sample_results)

        assert isinstance(dashboard, Dashboard)

    def test_dashboard_has_multiple_plots(
        self, sample_results: List[Dict[str, Any]]
    ) -> None:
        """Dashboard contains multiple subplots."""
        dashboard = create_dashboard(sample_results)
        html = dashboard.to_html()

        assert "subplot" in html.lower() or len(html) > 1000

    def test_dashboard_includes_title(
        self, sample_results: List[Dict[str, Any]]
    ) -> None:
        """Dashboard has a descriptive title."""
        dashboard = create_dashboard(sample_results)
        html = dashboard.to_html()

        assert "batch" in html.lower() or "simulation" in html.lower()

    def test_dashboard_is_interactive(
        self, sample_results: List[Dict[str, Any]]
    ) -> None:
        """Dashboard includes interactive elements."""
        dashboard = create_dashboard(sample_results)
        html = dashboard.to_html()

        # Plotly dashboards include JavaScript
        assert "plotly" in html.lower()

    def test_dashboard_handles_large_dataset(self) -> None:
        """Dashboard can handle large result sets (100+ runs)."""
        results = [
            {
                "run_id": i,
                "completion_time": 0.1 * (i % 10),
                "final_repair_count": 90 + (i % 20),
            }
            for i in range(1, 101)
        ]

        dashboard = create_dashboard(results)
        assert dashboard is not None


class TestDashboardExport:
    """Test dashboard export functionality."""

    @pytest.fixture
    def sample_dashboard(self) -> Dashboard:
        """Sample dashboard for testing."""
        results = [
            {
                "run_id": i,
                "completion_time": 0.1 * i,
                "final_repair_count": 95,
            }
            for i in range(1, 6)
        ]
        return create_dashboard(results)

    def test_dashboard_export_to_html(self, sample_dashboard: Dashboard) -> None:
        """Dashboard can export to HTML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            sample_dashboard.save_html(output_path)

            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_dashboard_html_is_interactive(self, sample_dashboard: Dashboard) -> None:
        """Exported HTML contains interactive Plotly elements."""
        html = sample_dashboard.to_html()

        assert "plotly" in html.lower()
        assert "script" in html.lower()
