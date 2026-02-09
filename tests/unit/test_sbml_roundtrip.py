"""
RED Phase: SBML Round-Trip Tests (Currently Failing)

These tests define the contract for SBML round-trip fidelity. They will fail until
engine/io/sbml_export.py and engine/io/sbml_import.py are implemented.

Tests verify:
- Config round-trip preserves all fields (< 0.1% RMSE)
- Damage profile round-trip preserves lesion counts
- Kinetics parameters round-trip preserves tolerance values
- Species counts match before and after round-trip
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from engine.domain.models import (
    DamageType, CellCyclePhase, Lesion, DamageProfile
)
from engine.domain.config import HappyGeneConfig, SimulationConfig, KineticsConfig, SolverMethod


class TestSBMLRoundTrip:
    """SBML export→import round-trip fidelity tests."""

    def test_roundtrip_config_to_sbml_to_config(self):
        """HappyGeneConfig round-trip preserves all configuration."""
        from engine.io.sbml_export import export_to_sbml
        from engine.io.sbml_import import import_from_sbml

        # Arrange
        original_config = HappyGeneConfig(
            kinetics=KineticsConfig(
                method=SolverMethod.BDF,
                rtol=1e-6,
                atol=1e-9
            )
        )
        damage_profile = DamageProfile(
            lesions=(
                Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0),
            ),
            dose_gy=2.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "roundtrip.xml"

            # Act - Export
            export_to_sbml(original_config, damage_profile, sbml_path)

            # Act - Import
            reimported_profile, reimported_config = import_from_sbml(sbml_path)

            # Assert - Config preservation
            assert reimported_config.rtol == original_config.kinetics.rtol
            assert reimported_config.atol == original_config.kinetics.atol
            assert reimported_config.method == original_config.kinetics.method

    def test_roundtrip_damage_profile_preserved(self):
        """Damage profile round-trip preserves lesion counts and types."""
        from engine.io.sbml_export import export_to_sbml
        from engine.io.sbml_import import import_from_sbml

        # Arrange
        config = HappyGeneConfig()
        lesions = tuple(
            Lesion(position_bp=i*100, damage_type=DamageType.DSB, time_seconds=0.0)
            for i in range(5)
        ) + tuple(
            Lesion(position_bp=i*100+1000, damage_type=DamageType.SSB, time_seconds=0.0)
            for i in range(10)
        )
        original_profile = DamageProfile(
            lesions=lesions,
            dose_gy=3.0,
            population_size=200,
            cell_cycle_phase=CellCyclePhase.S
        )

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "profile.xml"

            # Act
            export_to_sbml(config, original_profile, sbml_path)
            reimported_profile, _ = import_from_sbml(sbml_path)

            # Assert - Lesion preservation
            assert reimported_profile.lesion_count() == original_profile.lesion_count()
            assert reimported_profile.dose_gy == original_profile.dose_gy
            assert reimported_profile.population_size == original_profile.population_size

    def test_roundtrip_kinetics_parameters_preserved(self):
        """Kinetics parameters round-trip with < 0.1% error."""
        from engine.io.sbml_export import export_to_sbml
        from engine.io.sbml_import import import_from_sbml

        # Arrange
        original_kinetics = KineticsConfig(
            rtol=1.5e-7,
            atol=2.5e-10,
            method=SolverMethod.RK45,
            max_step=0.5
        )
        config = HappyGeneConfig(kinetics=original_kinetics)
        damage_profile = DamageProfile(
            lesions=tuple(),
            dose_gy=1.0,
            population_size=10,
            cell_cycle_phase=CellCyclePhase.G2
        )

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "kinetics.xml"

            # Act
            export_to_sbml(config, damage_profile, sbml_path)
            _, reimported_kinetics = import_from_sbml(sbml_path)

            # Assert - Parameters preserved within 0.1% RMSE
            rtol_error = abs(reimported_kinetics.rtol - original_kinetics.rtol) / original_kinetics.rtol
            atol_error = abs(reimported_kinetics.atol - original_kinetics.atol) / original_kinetics.atol

            assert rtol_error < 0.001  # 0.1%
            assert atol_error < 0.001  # 0.1%
            assert reimported_kinetics.method == original_kinetics.method

    def test_roundtrip_species_counts_match(self):
        """Species counts (damage types) match before and after round-trip."""
        from engine.io.sbml_export import export_to_sbml
        from engine.io.sbml_import import import_from_sbml

        # Arrange - Create lesions for multiple damage types
        lesions = tuple(
            Lesion(position_bp=i*100, damage_type=dt, time_seconds=0.0)
            for i, dt in enumerate(DamageType)
            for _ in range(2)  # 2 lesions of each type
        )
        config = HappyGeneConfig()
        original_profile = DamageProfile(
            lesions=lesions,
            dose_gy=5.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.M
        )

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "species.xml"

            # Act
            export_to_sbml(config, original_profile, sbml_path)
            reimported_profile, _ = import_from_sbml(sbml_path)

            # Assert
            assert reimported_profile.lesion_count() == original_profile.lesion_count()
            # Both should have same number of lesions per type
            original_by_type = {}
            reimported_by_type = {}
            for lesion in original_profile.lesions:
                original_by_type[lesion.damage_type] = original_by_type.get(lesion.damage_type, 0) + 1
            for lesion in reimported_profile.lesions:
                reimported_by_type[lesion.damage_type] = reimported_by_type.get(lesion.damage_type, 0) + 1

            assert original_by_type == reimported_by_type
