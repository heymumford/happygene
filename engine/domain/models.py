
# Copyright (C) 2026 Eric C. Mumford <ericmumford@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Domain Model: Immutable Data Boundaries

Frozen dataclasses define the core data structures across the DNA repair simulation
pipeline. These are inputs/outputs at system boundaries, ensuring immutability
and type safety.

Principle: Data objects are immutable. Transformation functions are pure.
No side effects. Stateless.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
from datetime import datetime


# ============================================================================
# Enums: Type-Safe Domain Values
# ============================================================================

class DamageType(str, Enum):
    """DNA damage classification (extensible)."""
    DSB = "double_strand_break"           # Highly lethal
    SSB = "single_strand_break"           # Usually repaired
    CROSSLINK = "crosslink"               # Interstrand/protein
    OXIDATIVE = "oxidative"               # Reactive oxygen species
    DEPURINATION = "depurination"         # Purine loss
    DEAMINATION = "deamination"           # Cytosine → Uracil
    THYMINE_DIMER = "thymine_dimer"       # UV-induced


class RepairPathway(str, Enum):
    """DNA repair mechanism (extensible via plugin system)."""
    NHEJ = "non_homologous_end_joining"   # Fast, error-prone
    HR = "homologous_recombination"       # Accurate, slow
    BER = "base_excision_repair"          # Small lesions
    NER = "nucleotide_excision_repair"    # Bulky lesions
    MMR = "mismatch_repair"               # Strand mismatches
    TLS = "translesion_synthesis"         # Bypass (mutagenic)
    DIRECT = "direct_reversal"            # Photolyase, AlkB
    ALTEJ = "alternative_end_joining"     # NHEJ variant


class CellFateStatus(str, Enum):
    """Cell outcome post-repair."""
    VIABLE = "viable"                     # Repaired, survives
    APOPTOSIS = "apoptosis"               # Programmed death
    SENESCENCE = "senescence"             # Permanent cycle arrest
    MITOTIC_DEATH = "mitotic_death"       # Dies at mitosis
    TRANSFORMATION = "transformation"    # Becomes cancerous


class CellCyclePhase(str, Enum):
    """Cell cycle phase during damage."""
    G1 = "G1"      # Gap 1 (unreplicated)
    S = "S"        # Synthesis (replication fork)
    G2 = "G2"      # Gap 2 (replicated)
    M = "M"        # Mitosis


# ============================================================================
# Domain Model: Immutable Dataclasses
# ============================================================================

@dataclass(frozen=True)
class Lesion:
    """
    Single DNA damage site (immutable).

    Examples:
        >>> lesion = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0)
        >>> lesion.position_bp
        1000
        >>> lesion.position_bp = 2000  # TypeError: frozen
    """
    position_bp: int              # 0-indexed genomic position
    damage_type: DamageType       # Type of damage
    time_seconds: float           # When damage occurred
    severity: float = 1.0         # 0-1 scale (0=none, 1=lethal)
    protein_bound: bool = False   # Is a protein bound?

    def __post_init__(self):
        """Validate lesion invariants."""
        if self.position_bp < 0:
            raise ValueError(f"position_bp must be >= 0, got {self.position_bp}")
        if not 0 <= self.severity <= 1:
            raise ValueError(f"severity must be in [0, 1], got {self.severity}")
        if self.time_seconds < 0:
            raise ValueError(f"time_seconds must be >= 0, got {self.time_seconds}")


@dataclass(frozen=True)
class DamageProfile:
    """
    Immutable damage state at simulation start.

    Represents the initial condition: what DNA damage exists before repair begins.
    Used as input to repair kinetics solver.

    Invariants:
        - lesions ordered by time (temporal causality)
        - dose_gy in [0, 10] (biological relevance)
        - population_size in [1, 1,000,000]
        - All lesions present at t=0 (static profile)
    """
    lesions: Tuple[Lesion, ...]                    # Immutable tuple
    dose_gy: float                                 # Radiation dose (Gray)
    population_size: int                           # Cells in population
    cell_cycle_phase: CellCyclePhase               # When damage occurred
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate damage profile invariants."""
        # Dose range
        if not 0 <= self.dose_gy <= 10:
            raise ValueError(f"dose_gy must be in [0, 10], got {self.dose_gy}")

        # Population range
        if not 1 <= self.population_size <= 1_000_000:
            raise ValueError(f"population_size must be in [1, 1M], got {self.population_size}")

        # Lesions temporal ordering
        for i in range(len(self.lesions) - 1):
            if self.lesions[i].time_seconds > self.lesions[i + 1].time_seconds:
                raise ValueError(
                    f"Lesions must be ordered temporally: "
                    f"lesion[{i}].time={self.lesions[i].time_seconds} > "
                    f"lesion[{i+1}].time={self.lesions[i + 1].time_seconds}"
                )

    def lesion_count(self) -> int:
        """
        Total lesions in this damage profile.

        Returns:
            Count of lesions (0 if no damage).
        """
        return len(self.lesions)


@dataclass(frozen=True)
class RepairEvent:
    """
    Single repair event (immutable).

    Represents one repair action: which pathway, when, success?
    """
    pathway: RepairPathway                # NHEJ, HR, BER, etc.
    start_time: float                     # When repair began
    end_time: float                       # When repair completed
    lesions_repaired: int                 # Count of lesions fixed
    lesions_unrepaired: int               # Count remaining
    fidelity: float = 1.0                 # 0=error-prone, 1=perfect

    def __post_init__(self):
        """Validate repair event invariants."""
        if self.start_time > self.end_time:
            raise ValueError(
                f"start_time > end_time: {self.start_time} > {self.end_time}"
            )
        if self.start_time < 0 or self.end_time < 0:
            raise ValueError(f"Repair times cannot be negative")
        if not 0 <= self.fidelity <= 1:
            raise ValueError(f"fidelity must be in [0, 1], got {self.fidelity}")
        if self.lesions_repaired < 0 or self.lesions_unrepaired < 0:
            raise ValueError(f"Lesion counts cannot be negative")

    @property
    def duration_seconds(self) -> float:
        """
        Repair event duration (end_time - start_time).

        Returns:
            Duration in seconds (≥ 0).
        """
        return self.end_time - self.start_time


@dataclass(frozen=True)
class RepairOutcome:
    """
    Immutable repair kinetics result.

    Output from ODE solver: what happened during repair phase?

    Invariants:
        - repair_events ordered temporally (t0 < t1 < t2)
        - total_repaired <= initial_lesions
    """
    repair_events: Tuple[RepairEvent, ...] = field(default_factory=tuple)
    initial_lesions: int = 0
    total_repaired: int = 0
    total_unrepaired: int = 0
    completion_time: float = 0.0
    success: bool = False                  # All lesions repaired?
    ode_rmse: float = 0.0                  # ODE solver RMSE

    def __post_init__(self):
        """Validate repair outcome invariants."""
        # Temporal ordering
        for i in range(len(self.repair_events) - 1):
            if self.repair_events[i].end_time > self.repair_events[i + 1].start_time:
                raise ValueError(
                    f"Repair events must not overlap: "
                    f"event[{i}].end_time={self.repair_events[i].end_time} > "
                    f"event[{i+1}].start_time={self.repair_events[i + 1].start_time}"
                )

        # Lesion count consistency
        if self.total_repaired > self.initial_lesions:
            raise ValueError(
                f"total_repaired > initial_lesions: "
                f"{self.total_repaired} > {self.initial_lesions}"
            )

        # Success criteria
        if self.success and self.total_unrepaired > 0:
            raise ValueError(f"success=True but unrepaired lesions remain")

    def outcome_summary(self) -> dict:
        """
        Repair outcome as dict (for logging/serialization).

        Returns:
            Dict with keys: initial_lesions, repaired, unrepaired, success,
            events, time_seconds, rmse.
        """
        return {
            "initial_lesions": self.initial_lesions,
            "repaired": self.total_repaired,
            "unrepaired": self.total_unrepaired,
            "success": self.success,
            "events": len(self.repair_events),
            "time_seconds": self.completion_time,
            "rmse": self.ode_rmse,
        }


@dataclass(frozen=True)
class CellFate:
    """
    Immutable cell outcome post-repair.

    What happened to the cell? Viable, dead, senescent?
    """
    status: CellFateStatus
    time_determined: float                 # When fate decided
    markers: dict = field(default_factory=dict)  # Biomarkers (γ-H2AX, p21, etc.)

    def __post_init__(self):
        """Validate cell fate invariants."""
        if self.time_determined < 0:
            raise ValueError(f"time_determined must be >= 0, got {self.time_determined}")


@dataclass(frozen=True)
class PopulationOutcome:
    """
    Immutable population-level simulation result.

    Output from complete pipeline: damage → repair → fate for entire population.

    Invariants:
        - len(repair_outcomes) == len(cell_fates) == population_size
        - survival_rate in [0, 1]
    """
    damage_profile: DamageProfile
    repair_outcomes: Tuple[RepairOutcome, ...]
    cell_fates: Tuple[CellFate, ...]
    elapsed_time: float                    # Simulation wall-clock time (seconds)
    random_seed: int = 42

    def __post_init__(self):
        """Validate population outcome invariants."""
        pop_size = self.damage_profile.population_size

        if len(self.repair_outcomes) != pop_size:
            raise ValueError(
                f"repair_outcomes size {len(self.repair_outcomes)} != "
                f"population_size {pop_size}"
            )
        if len(self.cell_fates) != pop_size:
            raise ValueError(
                f"cell_fates size {len(self.cell_fates)} != "
                f"population_size {pop_size}"
            )

    @property
    def survival_rate(self) -> float:
        """
        Fraction of cells surviving (viable).

        Returns:
            Value in [0, 1] representing survival rate.
        """
        viable = sum(1 for fate in self.cell_fates if fate.status == CellFateStatus.VIABLE)
        return viable / len(self.cell_fates) if self.cell_fates else 0.0

    @property
    def apoptosis_rate(self) -> float:
        """
        Fraction of cells undergoing apoptosis.

        Returns:
            Value in [0, 1] representing apoptosis rate.
        """
        apoptotic = sum(1 for fate in self.cell_fates if fate.status == CellFateStatus.APOPTOSIS)
        return apoptotic / len(self.cell_fates) if self.cell_fates else 0.0

    @property
    def senescence_rate(self) -> float:
        """
        Fraction of cells senescing.

        Returns:
            Value in [0, 1] representing senescence rate.
        """
        senescent = sum(1 for fate in self.cell_fates if fate.status == CellFateStatus.SENESCENCE)
        return senescent / len(self.cell_fates) if self.cell_fates else 0.0

    def summary(self) -> dict:
        """
        Population outcome as dict (for logging/export).

        Returns:
            Dict with keys: dose_gy, population_size, survival_rate,
            apoptosis_rate, senescence_rate, elapsed_time, seed.
        """
        return {
            "dose_gy": self.damage_profile.dose_gy,
            "population_size": self.damage_profile.population_size,
            "survival_rate": self.survival_rate,
            "apoptosis_rate": self.apoptosis_rate,
            "senescence_rate": self.senescence_rate,
            "elapsed_time": self.elapsed_time,
            "seed": self.random_seed,
        }
