"""
Batch Simulator Tests - RED Phase

Tests define expected behavior for batch simulation runner.
"""

import tempfile
from pathlib import Path

import pytest

from engine.domain.config import HappyGeneConfig, KineticsConfig, SolverMethod
from engine.domain.models import DamageProfile, Lesion, DamageType, CellCyclePhase
from engine.simulator.batch import BatchSimulator


class TestBatchSimulator:
    """Test batch simulation runner."""

    @pytest.fixture
    def config(self) -> HappyGeneConfig:
        """Standard test configuration."""
        kinetics = KineticsConfig(
            method=SolverMethod.BDF,
            rtol=1e-6,
            atol=1e-9,
            max_step=1.0
        )
        return HappyGeneConfig(kinetics=kinetics)

    @pytest.fixture
    def damage_profile(self) -> DamageProfile:
        """Standard test damage profile."""
        lesion = Lesion(
            position_bp=1000,
            damage_type=DamageType.DSB,
            time_seconds=0.0,
            severity=1.0
        )
        return DamageProfile(
            lesions=(lesion,),
            dose_gy=3.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )

    def test_batch_simulator_runs_multiple_simulations(
        self, config: HappyGeneConfig, damage_profile: DamageProfile
    ) -> None:
        """Batch simulator can run multiple simulations with same config."""
        simulator = BatchSimulator(config, damage_profile)

        # Run 5 simulations
        results = simulator.run_batch(num_runs=5)

        assert len(results) == 5
        assert all(isinstance(r, dict) for r in results)

    def test_batch_simulator_results_have_required_fields(
        self, config: HappyGeneConfig, damage_profile: DamageProfile
    ) -> None:
        """Each batch result contains required fields."""
        simulator = BatchSimulator(config, damage_profile)
        results = simulator.run_batch(num_runs=2)

        required_fields = {'run_id', 'completion_time', 'status', 'final_repair_count'}

        for result in results:
            assert required_fields.issubset(set(result.keys()))

    def test_batch_simulator_saves_results_to_hdf5(
        self, config: HappyGeneConfig, damage_profile: DamageProfile
    ) -> None:
        """Batch simulator can save results to HDF5 file."""
        simulator = BatchSimulator(config, damage_profile)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.h5"

            # Run and save
            results = simulator.run_batch(num_runs=3)
            simulator.save_results(results, output_path)

            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_batch_simulator_can_load_hdf5_results(
        self, config: HappyGeneConfig, damage_profile: DamageProfile
    ) -> None:
        """Batch simulator can load results from HDF5 file."""
        simulator = BatchSimulator(config, damage_profile)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.h5"

            # Run, save, and load
            results = simulator.run_batch(num_runs=2)
            simulator.save_results(results, output_path)
            loaded_results = BatchSimulator.load_results(output_path)

            assert len(loaded_results) == len(results)
            assert loaded_results[0].keys() == results[0].keys()

    def test_batch_simulator_aggregates_statistics(
        self, config: HappyGeneConfig, damage_profile: DamageProfile
    ) -> None:
        """Batch simulator can compute aggregate statistics."""
        simulator = BatchSimulator(config, damage_profile)
        results = simulator.run_batch(num_runs=10)

        stats = simulator.compute_statistics(results)

        assert 'mean_repair_time' in stats
        assert 'std_repair_time' in stats
        assert 'min_repair_time' in stats
        assert 'max_repair_time' in stats
        assert stats['num_runs'] == 10

    def test_batch_simulator_handles_empty_results(
        self, config: HappyGeneConfig, damage_profile: DamageProfile
    ) -> None:
        """Batch simulator handles empty result set gracefully."""
        simulator = BatchSimulator(config, damage_profile)

        stats = simulator.compute_statistics([])

        assert stats['num_runs'] == 0
