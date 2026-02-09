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

    def test_regulatory_network_example_runs(self):
        """Test that regulatory_network.py example script runs successfully.

        Rationale: Verify that the advanced example with Hill kinetics and
        threshold selection runs without errors and demonstrates realistic
        gene regulatory dynamics.

        Success criteria:
        - Script exits with code 0
        - Produces output to stdout
        - Demonstrates Hill kinetics and threshold selection
        - Collects multi-level data (model, individual, gene)
        """
        result = subprocess.run(
            [sys.executable, "examples/regulatory_network.py"],
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
        assert "Regulatory Network Example" in result.stdout, "Output missing title"
        assert "Creating regulatory population" in result.stdout, "Output missing population setup"
        assert "Hill kinetics expression model" in result.stdout, "Output missing Hill expression config"
        assert "ThresholdSelection configured" in result.stdout, "Output missing threshold selection config"
        assert "Running simulation" in result.stdout, "Output missing simulation"
        assert "SIMULATION RESULTS" in result.stdout, "Output missing results section"
        assert "SIMULATION COMPLETE" in result.stdout, "Output missing completion marker"

        # Should show fitness statistics
        assert "Fitness Summary" in result.stdout, "Output missing fitness statistics"

        # Should show selection pressure analysis
        assert "Selection Pressure Analysis" in result.stdout, "Output missing selection analysis"

    def test_regulatory_network_produces_data(self):
        """Test that regulatory_network.py actually collects multi-level data.

        Rationale: Verify that the example produces meaningful simulation output
        with model-level, individual-level, and gene-level data collection.
        """
        result = subprocess.run(
            [sys.executable, "examples/regulatory_network.py"],
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
        # 50 individuals, 5 genes per individual
        assert "50" in result.stdout, "Should have 50 individual records"
        assert "250" in result.stdout, "Should have 250 gene records"

        # Should show gene expression statistics
        assert "Gene Expression" in result.stdout, "Output missing gene expression stats"

    def test_benchmark_script_runs_basic_scenario(self):
        """Test that benchmark.py runs with basic scenario parameters.

        Rationale: Verify that the benchmark script executes without errors
        for a small scenario (100 individuals, 10 genes, 50 generations).

        Success criteria:
        - Script exits with code 0
        - Produces benchmark results table
        - Contains timing information
        - All expected columns present in output
        """
        result = subprocess.run(
            [sys.executable, "examples/benchmark.py",
             "--individuals", "100",
             "--genes", "10",
             "--generations", "50"],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Should exit successfully
        assert result.returncode == 0, \
            f"Benchmark script failed with code {result.returncode}\nstderr: {result.stderr}"

        # Should produce output
        assert len(result.stdout) > 0, "Benchmark script produced no output"

        # Should contain results table header
        assert "Benchmark Results" in result.stdout, "Output missing benchmark header"

        # Should contain timing information
        assert "Time (s)" in result.stdout, "Output missing timing column"
        assert "Ops/sec" in result.stdout, "Output missing ops/sec column"

        # Should contain results
        assert "100" in result.stdout, "Output should contain individual count"
        assert "10" in result.stdout, "Output should contain gene count"

    def test_benchmark_script_with_regulation(self):
        """Test that benchmark.py runs with regulatory network enabled.

        Rationale: Verify that the benchmark script correctly handles the
        --regulation flag and executes complex scenarios with TF interactions.

        Success criteria:
        - Script exits with code 0
        - Produces benchmark results table
        - Shows timing for regulatory network computation
        - Contains results for the regulated scenario
        """
        result = subprocess.run(
            [sys.executable, "examples/benchmark.py",
             "--individuals", "100",
             "--genes", "20",
             "--generations", "50",
             "--regulation"],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Should exit successfully
        assert result.returncode == 0, \
            f"Benchmark script with regulation failed: {result.stderr}"

        # Should produce output
        assert len(result.stdout) > 0, "Benchmark script produced no output"

        # Should contain results table
        assert "Benchmark Results" in result.stdout, "Output missing benchmark header"
        assert "Time (s)" in result.stdout, "Output missing timing column"

        # Should show the scenario was run (Y indicates regulation=true in table)
        assert "Y" in result.stdout, "Output should show regulation flag"
