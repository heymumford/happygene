"""
Configuration Schema: Pydantic v2 Validation

YAML → Pydantic → Python dataclasses
Ensures configuration is valid before simulation starts.

Principle: All user input validated at boundaries. Clear error messages.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum


# ============================================================================
# Enums for Config Options
# ============================================================================

class SolverMethod(str, Enum):
    """ODE solver selection (ADR-001)."""
    BDF = "BDF"           # Stiff ODE solver (default)
    RK45 = "RK45"         # Runge-Kutta 4/5
    RK23 = "RK23"         # Runge-Kutta 2/3 (low precision)


class OutputFormat(str, Enum):
    """Output serialization format."""
    HDF5 = "hdf5"         # Hierarchical Data Format
    SBML = "sbml"         # Systems Biology Markup Language (COPASI compatible)
    JSON = "json"         # JSON (debugging)


# ============================================================================
# Pydantic Configuration Schemas
# ============================================================================

class KineticsConfig(BaseModel):
    """
    ODE Solver Configuration (SciPy BDF, ADR-001)

    Tolerances determine accuracy vs. speed trade-off:
    - rtol=1e-6: Relative tolerance (6 significant figures)
    - atol=1e-9: Absolute tolerance (for near-zero values)

    Publication-grade defaults per ADR-001.

    Example:
        >>> config = KineticsConfig(rtol=1e-6, atol=1e-9)
        >>> config.method
        <SolverMethod.BDF: 'BDF'>
    """
    model_config = ConfigDict(frozen=True)

    method: SolverMethod = Field(
        default=SolverMethod.BDF,
        description="ODE solver method (BDF for stiff systems)"
    )
    rtol: float = Field(
        default=1e-6,
        ge=1e-9,
        le=1e-3,
        description="Relative tolerance [1e-9, 1e-3]"
    )
    atol: float = Field(
        default=1e-9,
        ge=1e-12,
        le=1e-6,
        description="Absolute tolerance [1e-12, 1e-6]"
    )
    max_step: float = Field(
        default=1.0,
        gt=0,
        description="Maximum ODE integrator step (seconds)"
    )
    jacobian: str = Field(
        default="analytical",
        pattern="^(analytical|numerical)$",
        description="Jacobian computation method"
    )

    @field_validator("rtol", "atol")
    @classmethod
    def validate_tolerances(cls, v: float, info) -> float:
        """Ensure rtol >= atol (relative >= absolute)."""
        if "atol" in info.data and v < info.data.get("atol", 0):
            raise ValueError(f"{info.field_name} must be >= atol")
        return v


class RepairPathwayConfig(BaseModel):
    """
    Configuration for individual repair pathway.

    Example:
        >>> config = RepairPathwayConfig(enabled=True, relative_rate=0.8)
        >>> config.parameters = {"k_on": 0.01}
    """
    model_config = ConfigDict(frozen=True)

    enabled: bool = Field(default=True, description="Is this pathway active?")
    relative_rate: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Relative rate vs. WT [0.1, 10.0]"
    )
    parameters: Dict[str, float] = Field(
        default_factory=dict,
        description="Pathway-specific parameters (k_on, k_off, etc.)"
    )


class SimulationConfig(BaseModel):
    """
    Top-level simulation configuration (from YAML).

    Example YAML:
        ```yaml
        simulation:
          type: "radiation_dna_repair"
          population_size: 1000
          dose_gy: 4.0
          repair_pathways:
            - name: "NHEJ"
              enabled: true
              relative_rate: 1.0
            - name: "HR"
              enabled: true
              relative_rate: 0.5
          cell_cycle_phase: "G1"
          random_seed: 42
        ```

    Example Python:
        >>> config = SimulationConfig(dose_gy=4.0, population_size=100)
        >>> config.dose_gy
        4.0
    """
    model_config = ConfigDict(frozen=True)
    type: str = Field(
        default="radiation_dna_repair",
        pattern="^[a-z_]+$",
        description="Simulation type identifier"
    )
    population_size: int = Field(
        default=100,
        ge=1,
        le=1_000_000,
        description="Cells to simulate [1, 1M]"
    )
    dose_gy: float = Field(
        default=4.0,
        ge=0.0,
        le=10.0,
        description="Radiation dose in Gray [0, 10]"
    )
    time_hours: float = Field(
        default=24.0,
        gt=0,
        le=1000,
        description="Simulation duration (hours)"
    )
    repair_pathways: List[RepairPathwayConfig] = Field(
        default_factory=lambda: [
            RepairPathwayConfig(enabled=True)  # NHEJ
        ],
        description="Active repair pathways"
    )
    cell_cycle_phase: str = Field(
        default="G1",
        pattern="^(G1|S|G2|M)$",
        description="Cell cycle phase during damage"
    )
    random_seed: int = Field(
        default=42,
        ge=0,
        description="Random seed for reproducibility"
    )

    @field_validator("repair_pathways")
    @classmethod
    def validate_pathways(cls, v: List[RepairPathwayConfig]) -> List[RepairPathwayConfig]:
        """Ensure at least one pathway enabled."""
        if not any(p.enabled for p in v):
            raise ValueError("At least one repair pathway must be enabled")
        return v


class OutputConfig(BaseModel):
    """
    Output format and storage configuration.

    Example:
        >>> config = OutputConfig(format=OutputFormat.SBML, compress=True)
        >>> config.format
        <OutputFormat.SBML: 'sbml'>
    """
    model_config = ConfigDict(frozen=True)

    format: OutputFormat = Field(
        default=OutputFormat.HDF5,
        description="Output serialization format"
    )
    compress: bool = Field(
        default=True,
        description="Enable gzip compression"
    )
    compression_level: int = Field(
        default=9,
        ge=1,
        le=9,
        description="Compression level [1-9]"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include config, git commit, seed in output"
    )


class HappyGeneConfig(BaseModel):
    """
    Root configuration object (entire simulation setup).

    Loaded from YAML via: `HappyGeneConfig.from_yaml("config.yaml")`

    Example:
        >>> config = HappyGeneConfig()
        >>> config.simulation.dose_gy
        4.0
        >>> hash_val = config.config_hash()
        >>> len(hash_val)
        16
    """
    model_config = ConfigDict(frozen=True)

    simulation: SimulationConfig = Field(
        default_factory=SimulationConfig,
        description="Simulation parameters"
    )
    kinetics: KineticsConfig = Field(
        default_factory=KineticsConfig,
        description="ODE solver configuration"
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="Output format"
    )

    @classmethod
    def from_yaml(cls, path: str) -> "HappyGeneConfig":
        """
        Load configuration from YAML file (not implemented yet).

        Raises:
            NotImplementedError: Implementation deferred to Phase 5.
        """
        raise NotImplementedError("YAML loading implemented in Phase 5")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to nested dict (for serialization).

        Returns:
            Dict with keys: simulation, kinetics, output.
        """
        return self.model_dump()

    def config_hash(self) -> str:
        """
        Compute stable config hash (reproducibility, caching).

        Same input → same hash (deterministic).
        Uses SHA256, returns 16-char hex (64-bit).

        Returns:
            16-character hex string (lowercase).
        """
        import hashlib
        import json

        # Serialize deterministically
        config_json = json.dumps(self.model_dump(), sort_keys=True, indent=0)
        hash_bytes = hashlib.sha256(config_json.encode()).digest()
        return hash_bytes.hex()[:16]  # 64-bit hex string
