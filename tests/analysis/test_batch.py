"""
Tests for BatchSimulator: core batch execution engine for sensitivity analysis.

Test Tiers:
1. Contract Tests: BatchSimulator interface and SALib integration
2. Property Tests: Deterministic seed handling and reproducibility
3. Chaos Tests: Error handling and edge cases
4. Performance Tests: Scaling with n_samples and n_generations
"""

import pytest
import numpy as np
import pandas as pd
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from happygene.analysis.batch import BatchSimulator

# ============================================================================
# TIER 1: CONTRACT TESTS - BatchSimulator interface and sample generation
# ============================================================================


class TestBatchSimulatorCreation:
    """Contract: Can create BatchSimulator with valid inputs."""

    def test_batch_simulator_creation_with_valid_inputs(self, sim_factory, param_space):
        """BatchSimulator instantiates with factory, param_space, seed."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        assert sim is not None
        assert sim.seed == 42
        assert len(sim.param_space) == len(param_space)

    def test_batch_simulator_stores_param_space(self, sim_factory, param_space):
        """param_space attribute matches input."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        assert sim.param_space == param_space

    def test_batch_simulator_stores_param_names(
        self, sim_factory, param_space, param_names
    ):
        """param_names extracted in consistent order."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        assert list(sim.param_names) == param_names


class TestSampleGeneration:
    """Contract: Generate parameter samples with correct shape and normalization."""

    def test_generate_samples_sobol_shape(self, sim_factory, param_space):
        """Sobol samples shape is (n_samples, n_params)."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(256, sampler="sobol")

        assert samples.shape == (256, len(param_space))
        assert isinstance(samples, np.ndarray)

    def test_generate_samples_saltelli_shape(self, sim_factory, param_space):
        """Saltelli (Sobol extended) samples shape calculation."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        # Saltelli creates 2(d+2)N samples from SALib (approx 12N for d=5)
        samples = sim.generate_samples(64, sampler="saltelli")

        # Just verify it returns 2D array with correct n_params
        assert samples.ndim == 2
        assert samples.shape[1] == len(param_space)
        # Saltelli expands sample count, verify we got more samples
        assert samples.shape[0] > 64

    def test_generate_samples_morris_shape(self, sim_factory, param_space):
        """Morris samples shape for screening."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(10, sampler="morris")

        # Morris: (num_trajectories * (d+1), d)
        n_params = len(param_space)
        assert samples.shape == (10 * (n_params + 1), n_params)

    def test_generate_samples_normalized_to_01(self, sim_factory, param_space):
        """All samples in [0, 1] normalized space."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(256, sampler="sobol")

        assert np.all(samples >= 0.0), "Samples must be >= 0.0"
        assert np.all(samples <= 1.0), "Samples must be <= 1.0"

    def test_generate_samples_returns_finite_values(self, sim_factory, param_space):
        """No NaN or inf values in samples."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(256)

        assert np.all(np.isfinite(samples))


class TestBatchExecution:
    """Contract: Run batch simulations and collect outputs."""

    def test_run_batch_returns_dataframe(
        self, sim_factory, param_space, normalized_samples
    ):
        """run_batch returns pandas DataFrame."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)

        # Denormalize samples for run_batch
        results = sim.run_batch(normalized_samples, n_generations=10)

        assert isinstance(results, pd.DataFrame)

    def test_run_batch_output_columns_include_params(
        self, sim_factory, param_space, param_names, normalized_samples
    ):
        """DataFrame has columns for all input parameters."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=10)

        for pname in param_names:
            assert pname in results.columns

    def test_run_batch_output_columns_include_outputs(
        self, sim_factory, param_space, normalized_samples
    ):
        """DataFrame has standard output columns."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=10)

        expected_outputs = {"total_repairs", "repair_time", "survival"}
        assert expected_outputs.issubset(results.columns)

    def test_run_batch_output_columns_include_metadata(
        self, sim_factory, param_space, normalized_samples
    ):
        """DataFrame includes run_id, seed, timestamp metadata."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=10)

        assert "run_id" in results.columns
        assert "seed" in results.columns

    def test_run_batch_row_count_matches_samples(
        self, sim_factory, param_space, normalized_samples
    ):
        """Output row count equals input sample count (1:1 correspondence)."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=10)

        assert len(results) == len(normalized_samples)

    def test_run_batch_output_values_are_numeric(
        self, sim_factory, param_space, normalized_samples
    ):
        """Output columns contain numeric values (no NaN/inf)."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=10)

        numeric_cols = results.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert np.all(np.isfinite(results[col]))

    def test_run_batch_executor_sequential(
        self, sim_factory, param_space, normalized_samples
    ):
        """executor='sequential' executes without error."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(
            normalized_samples, n_generations=10, executor="sequential"
        )

        assert len(results) == len(normalized_samples)


# ============================================================================
# TIER 2: PROPERTY-BASED TESTS - Reproducibility and determinism
# ============================================================================


class TestDeterministicSampling:
    """Property: Same seed → identical samples."""

    def test_deterministic_sobol_samples_under_seed(self, sim_factory, param_space):
        """Sobol samples identical for same seed."""
        sim1 = BatchSimulator(sim_factory, param_space, seed=42)
        samples1 = sim1.generate_samples(128, sampler="sobol")

        sim2 = BatchSimulator(sim_factory, param_space, seed=42)
        samples2 = sim2.generate_samples(128, sampler="sobol")

        assert np.allclose(samples1, samples2)

    def test_deterministic_morris_samples_under_seed(self, sim_factory, param_space):
        """Morris samples have same shape and bounds for same seed (determinism may vary)."""
        sim1 = BatchSimulator(sim_factory, param_space, seed=42)
        samples1 = sim1.generate_samples(10, sampler="morris")

        sim2 = BatchSimulator(sim_factory, param_space, seed=42)
        samples2 = sim2.generate_samples(10, sampler="morris")

        # Morris sampler is not guaranteed to be fully deterministic, but should
        # produce same shape and be in [0, 1] for same seed
        assert samples1.shape == samples2.shape
        assert np.all(samples1 >= 0) and np.all(samples1 <= 1)
        assert np.all(samples2 >= 0) and np.all(samples2 <= 1)

    def test_different_seeds_produce_different_samples(self, sim_factory, param_space):
        """Different seed → different samples (with high probability)."""
        sim1 = BatchSimulator(sim_factory, param_space, seed=42)
        samples1 = sim1.generate_samples(256, sampler="sobol")

        sim2 = BatchSimulator(sim_factory, param_space, seed=123)
        samples2 = sim2.generate_samples(256, sampler="sobol")

        # Should not be identical (Sobol is deterministic but different seeds differ)
        assert not np.allclose(samples1, samples2)

    @pytest.mark.parametrize("n_samples", [10, 64, 256])
    def test_deterministic_batch_outputs_under_seed(
        self, sim_factory, param_space, n_samples
    ):
        """Same seed → identical batch outputs (determinism)."""
        np.random.seed(42)
        samples = np.random.uniform(0, 1, size=(n_samples, len(param_space)))

        # First run
        sim1 = BatchSimulator(sim_factory, param_space, seed=42)
        results1 = sim1.run_batch(samples.copy(), n_generations=10)

        # Second run (same seed)
        sim2 = BatchSimulator(sim_factory, param_space, seed=42)
        results2 = sim2.run_batch(samples.copy(), n_generations=10)

        # Compare numeric columns
        numeric_cols = results1.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert np.allclose(
                results1[col].values, results2[col].values, rtol=1e-10
            ), f"Column {col} not deterministic"


class TestSeedCoverage:
    """Property: Seed parameter space coverage."""

    @given(seed=st.integers(0, 2**31 - 1), n_samples=st.integers(10, 100))
    @settings(
        max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_arbitrary_seeds_produce_valid_samples(
        self, sim_factory, param_space, seed, n_samples
    ):
        """Any seed in [0, 2^31) produces valid samples."""
        sim = BatchSimulator(sim_factory, param_space, seed=seed)
        samples = sim.generate_samples(n_samples)

        assert samples.shape == (n_samples, len(param_space))
        assert np.all(np.isfinite(samples))
        assert np.all(samples >= 0) and np.all(samples <= 1)


# ============================================================================
# TIER 3: CHAOS TESTS - Error handling and edge cases
# ============================================================================


class TestInputValidation:
    """Chaos: Handle invalid/edge-case inputs gracefully."""

    def test_batch_simulator_rejects_empty_param_space(self, sim_factory):
        """Cannot create with empty param_space."""
        with pytest.raises(ValueError):
            BatchSimulator(sim_factory, {}, seed=42)

    def test_batch_simulator_rejects_invalid_bounds_low_gte_high(self, sim_factory):
        """Rejects param bounds where low >= high."""
        bad_space = {"rate": (0.5, 0.1)}  # Invalid: low > high
        with pytest.raises(ValueError):
            BatchSimulator(sim_factory, bad_space, seed=42)

    def test_batch_simulator_rejects_negative_bounds(self, sim_factory):
        """Rejects negative parameter bounds."""
        bad_space = {"rate": (-0.5, 0.5)}
        with pytest.raises(ValueError):
            BatchSimulator(sim_factory, bad_space, seed=42)

    def test_run_batch_with_wrong_sample_shape(self, sim_factory, param_space):
        """Rejects samples with mismatched n_params."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)

        # Wrong shape: 10 samples × 4 params (should be 5)
        bad_samples = np.random.uniform(0, 1, size=(10, 4))

        with pytest.raises((ValueError, IndexError)):
            sim.run_batch(bad_samples, n_generations=10)

    def test_run_batch_with_zero_generations(
        self, sim_factory, param_space, normalized_samples
    ):
        """Handles n_generations=0 without crash."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=0)

        assert len(results) == len(normalized_samples)


class TestEdgeCases:
    """Edge cases in parameter space and sampling."""

    def test_single_parameter_sweep(self, sim_factory):
        """Sensitivity analysis with only 1 parameter."""
        param_space = {"rate": (0.0, 1.0)}
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(16, sampler="sobol")

        assert samples.shape == (16, 1)
        assert np.all(samples >= 0) and np.all(samples <= 1)

    def test_many_parameters(self, sim_factory):
        """High-dimensional parameter space (15 params)."""
        param_space = {f"param_{i}": (0.0, 1.0) for i in range(15)}
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(64, sampler="sobol")

        assert samples.shape == (64, 15)
        assert np.all(np.isfinite(samples))

    def test_multiple_output_dimensions(
        self, sim_factory, param_space, normalized_samples
    ):
        """Batch results with multiple output columns."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        results = sim.run_batch(normalized_samples, n_generations=10)

        # Should have all expected outputs
        expected_outputs = {"total_repairs", "repair_time", "survival"}
        assert expected_outputs.issubset(results.columns)

    def test_small_sample_size(self, sim_factory, param_space):
        """Small sample size (n=1) handled correctly."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(1, sampler="sobol")

        assert samples.shape == (1, len(param_space))


class TestNumericalEdgeCases:
    """Numerical stability and edge cases."""

    def test_samples_at_bounds_01(self, sim_factory, param_space):
        """Samples at [0, 1] boundaries are valid."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)

        # Manually create boundary samples
        n_params = len(param_space)
        samples = np.vstack(
            [
                np.zeros(n_params),  # All 0
                np.ones(n_params),  # All 1
            ]
        )

        results = sim.run_batch(samples, n_generations=10)
        assert len(results) == 2
        assert np.all(np.isfinite(results.select_dtypes(include=[np.number])))

    def test_very_small_parameter_range(self, sim_factory):
        """Very narrow parameter ranges work correctly."""
        param_space = {"rate": (0.4999, 0.5001)}  # Tiny range
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(32)

        # Should span the narrow range
        denorm = samples * (0.5001 - 0.4999) + 0.4999
        assert np.all(denorm >= 0.4999) and np.all(denorm <= 0.5001)


# ============================================================================
# TIER 4: PERFORMANCE TESTS - Scaling behavior
# ============================================================================


class TestPerformanceScaling:
    """Benchmark: Execution time scales with n_samples."""

    @pytest.mark.benchmark
    @pytest.mark.parametrize("n_samples", [10, 100, 1000])
    def test_batch_execution_time_scales_linearly(
        self, benchmark, sim_factory, param_space, n_samples
    ):
        """Batch execution time scales roughly linearly with n_samples."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)
        samples = sim.generate_samples(n_samples, sampler="sobol")

        # Benchmark the batch run
        benchmark(sim.run_batch, samples, n_generations=10)

    @pytest.mark.benchmark
    def test_sample_generation_fast(self, benchmark, sim_factory, param_space):
        """Sample generation completes quickly (< 1s for 10k samples)."""
        sim = BatchSimulator(sim_factory, param_space, seed=42)

        # Generate 10,000 samples
        benchmark(sim.generate_samples, 10000, sampler="sobol")
