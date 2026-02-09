"""Smoke tests for example scripts."""
import subprocess
import sys
import pytest


class TestExamples:
    """Smoke tests to verify examples run without errors."""

    def test_simple_duplication_example_runs(self):
        """Test that simple_duplication.py example script runs successfully.

        Rationale: Verify that the example is executable and demonstrates
        the core workflow: create population → models → run → collect results.

        Success criteria:
        - Script exits with code 0
        - Produces output to stdout
        - No exceptions raised
        """
        result = subprocess.run(
            [sys.executable, "examples/simple_duplication.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should exit successfully
        assert result.returncode == 0, \
            f"Example script failed with code {result.returncode}\nstderr: {result.stderr}"

        # Should produce output
        assert len(result.stdout) > 0, "Example script produced no output"

        # Should contain key output markers
        assert "HAPPYGENE" in result.stdout, "Output missing HAPPYGENE header"
        assert "Creating population" in result.stdout, "Output missing population setup"
        assert "Running simulation" in result.stdout, "Output missing simulation"
        assert "SIMULATION RESULTS" in result.stdout, "Output missing results section"
        assert "SIMULATION COMPLETE" in result.stdout, "Output missing completion marker"

        # Should contain fitness statistics
        assert "mean fitness" in result.stdout, "Output missing fitness statistics"

    def test_simple_duplication_produces_data(self):
        """Test that simple_duplication.py actually collects data.

        Rationale: Verify that the example produces meaningful simulation output.
        """
        result = subprocess.run(
            [sys.executable, "examples/simple_duplication.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0

        # Should show data collection summary
        assert "Data Collection Summary" in result.stdout
        assert "Model-level records" in result.stdout
        assert "Individual records" in result.stdout
        assert "Gene records" in result.stdout

        # Should have collected data
        # 1 generation * 100 individuals = 100 individual records
        # 1 generation * 100 individuals * 10 genes = 1000 gene records
        assert "100" in result.stdout, "Should have 100 individual records"
        assert "1000" in result.stdout, "Should have 1000 gene records"
