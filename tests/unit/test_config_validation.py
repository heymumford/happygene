"""
RED Phase Tests: Pydantic Configuration Validation

Configuration must be validated at load time. Invalid configs rejected with clear errors.

Test categories:
1. Pydantic schema validation
2. Boundary value validation (dose, population, tolerances)
3. YAML loading (round-trip fidelity)
4. Config hash stability
5. Enum validation
"""

import pytest
import json
from engine.domain.config import (
    SolverMethod, OutputFormat, KineticsConfig, RepairPathwayConfig,
    SimulationConfig, OutputConfig, HappyGeneConfig
)


# ============================================================================
# KineticsConfig Validation Tests
# ============================================================================

class TestKineticsConfig:
    """ODE solver configuration validation."""

    def test_kinetics_config_default_values(self):
        """Default kinetics config is valid."""
        config = KineticsConfig()
        assert config.method == SolverMethod.BDF
        assert config.rtol == 1e-6
        assert config.atol == 1e-9
        assert config.jacobian == "analytical"

    def test_kinetics_config_rtol_boundary_min(self):
        """rtol = 1e-9 (minimum) accepted."""
        config = KineticsConfig(rtol=1e-9)
        assert config.rtol == 1e-9

    def test_kinetics_config_rtol_boundary_max(self):
        """rtol = 1e-3 (maximum) accepted."""
        config = KineticsConfig(rtol=1e-3)
        assert config.rtol == 1e-3

    def test_kinetics_config_rtol_below_min_rejected(self):
        """rtol < 1e-9 rejected."""
        with pytest.raises(ValueError):
            KineticsConfig(rtol=1e-10)

    def test_kinetics_config_rtol_above_max_rejected(self):
        """rtol > 1e-3 rejected."""
        with pytest.raises(ValueError):
            KineticsConfig(rtol=1e-2)

    def test_kinetics_config_atol_boundary_min(self):
        """atol = 1e-12 (minimum) accepted."""
        config = KineticsConfig(atol=1e-12)
        assert config.atol == 1e-12

    def test_kinetics_config_atol_boundary_max(self):
        """atol = 1e-6 (maximum) accepted."""
        config = KineticsConfig(atol=1e-6)
        assert config.atol == 1e-6

    def test_kinetics_config_atol_below_min_rejected(self):
        """atol < 1e-12 rejected."""
        with pytest.raises(ValueError):
            KineticsConfig(atol=1e-13)

    def test_kinetics_config_atol_above_max_rejected(self):
        """atol > 1e-6 rejected."""
        with pytest.raises(ValueError):
            KineticsConfig(atol=1e-5)

    def test_kinetics_config_rtol_lt_atol_rejected(self):
        """rtol < atol rejected (must be rtol >= atol)."""
        with pytest.raises(ValueError):
            KineticsConfig(rtol=1e-10, atol=1e-9)

    def test_kinetics_config_jacobian_enum_validation(self):
        """jacobian must be 'analytical' or 'numerical'."""
        config_analytical = KineticsConfig(jacobian="analytical")
        assert config_analytical.jacobian == "analytical"

        config_numerical = KineticsConfig(jacobian="numerical")
        assert config_numerical.jacobian == "numerical"

    def test_kinetics_config_jacobian_invalid_rejected(self):
        """jacobian with invalid value rejected."""
        with pytest.raises(ValueError):
            KineticsConfig(jacobian="autodiff")

    def test_kinetics_config_frozen(self):
        """KineticsConfig is frozen (immutable)."""
        config = KineticsConfig()
        with pytest.raises((TypeError, Exception), match="frozen|cannot assign"):
            config.rtol = 1e-7


# ============================================================================
# RepairPathwayConfig Tests
# ============================================================================

class TestRepairPathwayConfig:
    """Individual repair pathway configuration."""

    def test_repair_pathway_config_default(self):
        """Default pathway config is valid."""
        config = RepairPathwayConfig()
        assert config.enabled is True
        assert config.relative_rate == 1.0

    def test_repair_pathway_config_relative_rate_boundary_min(self):
        """relative_rate = 0.1 (minimum) accepted."""
        config = RepairPathwayConfig(relative_rate=0.1)
        assert config.relative_rate == 0.1

    def test_repair_pathway_config_relative_rate_boundary_max(self):
        """relative_rate = 10.0 (maximum) accepted."""
        config = RepairPathwayConfig(relative_rate=10.0)
        assert config.relative_rate == 10.0

    def test_repair_pathway_config_relative_rate_below_min_rejected(self):
        """relative_rate < 0.1 rejected."""
        with pytest.raises(ValueError):
            RepairPathwayConfig(relative_rate=0.05)

    def test_repair_pathway_config_relative_rate_above_max_rejected(self):
        """relative_rate > 10.0 rejected."""
        with pytest.raises(ValueError):
            RepairPathwayConfig(relative_rate=11.0)

    def test_repair_pathway_config_custom_parameters(self):
        """Custom pathway parameters accepted."""
        params = {"k_on": 0.01, "k_off": 0.001}
        config = RepairPathwayConfig(parameters=params)
        assert config.parameters == params


# ============================================================================
# SimulationConfig Tests
# ============================================================================

class TestSimulationConfig:
    """Simulation parameter validation."""

    def test_simulation_config_default(self):
        """Default simulation config is valid."""
        config = SimulationConfig()
        assert config.type == "radiation_dna_repair"
        assert config.population_size == 100
        assert config.dose_gy == 4.0

    def test_simulation_config_population_boundary_min(self):
        """population_size = 1 (single cell) accepted."""
        config = SimulationConfig(population_size=1)
        assert config.population_size == 1

    def test_simulation_config_population_boundary_max(self):
        """population_size = 1M accepted."""
        config = SimulationConfig(population_size=1_000_000)
        assert config.population_size == 1_000_000

    def test_simulation_config_population_below_min_rejected(self):
        """population_size < 1 rejected."""
        with pytest.raises(ValueError):
            SimulationConfig(population_size=0)

    def test_simulation_config_population_above_max_rejected(self):
        """population_size > 1M rejected."""
        with pytest.raises(ValueError):
            SimulationConfig(population_size=1_000_001)

    def test_simulation_config_dose_gy_boundary_min(self):
        """dose_gy = 0.0 (no damage) accepted."""
        config = SimulationConfig(dose_gy=0.0)
        assert config.dose_gy == 0.0

    def test_simulation_config_dose_gy_boundary_max(self):
        """dose_gy = 10.0 accepted."""
        config = SimulationConfig(dose_gy=10.0)
        assert config.dose_gy == 10.0

    def test_simulation_config_dose_gy_below_min_rejected(self):
        """dose_gy < 0 rejected."""
        with pytest.raises(ValueError):
            SimulationConfig(dose_gy=-0.1)

    def test_simulation_config_dose_gy_above_max_rejected(self):
        """dose_gy > 10 rejected."""
        with pytest.raises(ValueError):
            SimulationConfig(dose_gy=10.1)

    def test_simulation_config_time_hours_positive_required(self):
        """time_hours must be > 0."""
        with pytest.raises(ValueError):
            SimulationConfig(time_hours=0.0)

    def test_simulation_config_cell_cycle_phase_enum(self):
        """cell_cycle_phase must be G1|S|G2|M."""
        config_g1 = SimulationConfig(cell_cycle_phase="G1")
        assert config_g1.cell_cycle_phase == "G1"

        config_s = SimulationConfig(cell_cycle_phase="S")
        assert config_s.cell_cycle_phase == "S"

    def test_simulation_config_cell_cycle_phase_invalid_rejected(self):
        """Invalid cell_cycle_phase rejected."""
        with pytest.raises(ValueError):
            SimulationConfig(cell_cycle_phase="X")

    def test_simulation_config_pathways_at_least_one_enabled(self):
        """At least one repair pathway must be enabled."""
        disabled_pathway = RepairPathwayConfig(enabled=False)
        with pytest.raises((ValueError, Exception), match="[Aa]t least one"):
            SimulationConfig(repair_pathways=[disabled_pathway])

    def test_simulation_config_random_seed_non_negative(self):
        """random_seed >= 0."""
        with pytest.raises(ValueError):
            SimulationConfig(random_seed=-1)


# ============================================================================
# OutputConfig Tests
# ============================================================================

class TestOutputConfig:
    """Output format configuration."""

    def test_output_config_default(self):
        """Default output config is valid."""
        config = OutputConfig()
        assert config.format == OutputFormat.HDF5
        assert config.compress is True

    def test_output_config_format_hdf5(self):
        """format = HDF5 accepted."""
        config = OutputConfig(format=OutputFormat.HDF5)
        assert config.format == OutputFormat.HDF5

    def test_output_config_format_sbml(self):
        """format = SBML accepted."""
        config = OutputConfig(format=OutputFormat.SBML)
        assert config.format == OutputFormat.SBML

    def test_output_config_compression_level_boundary_min(self):
        """compression_level = 1 accepted."""
        config = OutputConfig(compression_level=1)
        assert config.compression_level == 1

    def test_output_config_compression_level_boundary_max(self):
        """compression_level = 9 accepted."""
        config = OutputConfig(compression_level=9)
        assert config.compression_level == 9

    def test_output_config_compression_level_below_min_rejected(self):
        """compression_level < 1 rejected."""
        with pytest.raises(ValueError):
            OutputConfig(compression_level=0)

    def test_output_config_compression_level_above_max_rejected(self):
        """compression_level > 9 rejected."""
        with pytest.raises(ValueError):
            OutputConfig(compression_level=10)


# ============================================================================
# HappyGeneConfig (Root Configuration) Tests
# ============================================================================

class TestHappyGeneConfig:
    """Complete simulation configuration."""

    def test_happygene_config_default(self):
        """Default root config is valid."""
        config = HappyGeneConfig()
        assert isinstance(config.simulation, SimulationConfig)
        assert isinstance(config.kinetics, KineticsConfig)
        assert isinstance(config.output, OutputConfig)

    def test_happygene_config_nested_validation(self):
        """Nested config validation works."""
        sim = SimulationConfig(dose_gy=8.0)
        kinetics = KineticsConfig(rtol=1e-5)
        output = OutputConfig(format=OutputFormat.SBML)

        config = HappyGeneConfig(
            simulation=sim,
            kinetics=kinetics,
            output=output
        )
        assert config.simulation.dose_gy == 8.0
        assert config.kinetics.rtol == 1e-5
        assert config.output.format == OutputFormat.SBML

    def test_happygene_config_frozen(self):
        """Root config is frozen (immutable)."""
        config = HappyGeneConfig()
        with pytest.raises((TypeError, Exception), match="frozen|cannot assign"):
            config.simulation = SimulationConfig(dose_gy=2.0)

    def test_happygene_config_to_dict(self):
        """to_dict() serializes nested config."""
        config = HappyGeneConfig()
        d = config.to_dict()
        assert isinstance(d, dict)
        assert "simulation" in d
        assert "kinetics" in d
        assert "output" in d

    def test_happygene_config_hash_deterministic(self):
        """config_hash() is deterministic."""
        config1 = HappyGeneConfig()
        config2 = HappyGeneConfig()
        assert config1.config_hash() == config2.config_hash()

    def test_happygene_config_hash_changes_with_content(self):
        """config_hash() differs for different configs."""
        config1 = HappyGeneConfig(
            simulation=SimulationConfig(dose_gy=4.0)
        )
        config2 = HappyGeneConfig(
            simulation=SimulationConfig(dose_gy=8.0)
        )
        assert config1.config_hash() != config2.config_hash()

    def test_happygene_config_hash_order_invariant(self):
        """config_hash() is invariant to field order (JSON sorted keys)."""
        config1 = HappyGeneConfig(
            simulation=SimulationConfig(dose_gy=4.0),
            kinetics=KineticsConfig(rtol=1e-6)
        )
        config2 = HappyGeneConfig(
            kinetics=KineticsConfig(rtol=1e-6),
            simulation=SimulationConfig(dose_gy=4.0)
        )
        # Should have same hash despite field order
        assert config1.config_hash() == config2.config_hash()

    def test_happygene_config_hash_stable_64bit(self):
        """config_hash() returns 16-char hex (64-bit)."""
        config = HappyGeneConfig()
        hash_str = config.config_hash()
        assert len(hash_str) == 16
        assert all(c in "0123456789abcdef" for c in hash_str)


# ============================================================================
# YAML Loading Tests (placeholder for Phase 2)
# ============================================================================

class TestYAMLLoading:
    """YAML configuration loading (not implemented yet)."""

    def test_yaml_loading_not_implemented(self):
        """from_yaml() raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            HappyGeneConfig.from_yaml("config.yaml")

    # TODO: Implement YAML loading in Phase 2
    # - test_yaml_to_pydantic_round_trip
    # - test_yaml_unicode_preservation
    # - test_yaml_missing_required_field_error
