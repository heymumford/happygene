"""
RED Phase Tests: Domain Model Immutability & Invariants

All tests expected to FAIL initially (RED phase). GREEN phase implements code to pass.

Test categories:
1. Immutability (frozen dataclasses)
2. Temporal ordering (event chains)
3. Boundary validation (dose, population, etc.)
4. Enum validation
5. Property-based invariants
"""

import pytest
from datetime import datetime
from engine.domain.models import (
    DamageType, RepairPathway, CellFateStatus, CellCyclePhase,
    Lesion, DamageProfile, RepairEvent, RepairOutcome, CellFate, PopulationOutcome
)


# ============================================================================
# Immutability Tests (frozen dataclasses)
# ============================================================================

class TestImmutability:
    """Frozen dataclasses reject mutation."""

    def test_lesion_frozen_rejects_field_mutation(self):
        """Cannot modify lesion.position_bp after creation."""
        lesion = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0)
        with pytest.raises((TypeError, Exception), match="cannot assign"):
            lesion.position_bp = 2000

    def test_damage_profile_frozen_rejects_mutation(self):
        """Cannot modify damage_profile.dose_gy after creation."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=4.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )
        with pytest.raises((TypeError, Exception), match="cannot assign"):
            dp.dose_gy = 5.0

    def test_repair_event_frozen_rejects_mutation(self):
        """Cannot modify repair_event.pathway after creation."""
        event = RepairEvent(
            pathway=RepairPathway.NHEJ,
            start_time=0.0,
            end_time=1.0,
            lesions_repaired=5,
            lesions_unrepaired=0
        )
        with pytest.raises((TypeError, Exception), match="cannot assign"):
            event.pathway = RepairPathway.HR

    def test_repair_outcome_frozen_rejects_mutation(self):
        """Cannot modify repair_outcome.success after creation."""
        outcome = RepairOutcome(initial_lesions=10, total_repaired=10, success=True)
        with pytest.raises((TypeError, Exception), match="cannot assign"):
            outcome.success = False

    def test_cell_fate_frozen_rejects_mutation(self):
        """Cannot modify cell_fate.status after creation."""
        fate = CellFate(status=CellFateStatus.VIABLE, time_determined=10.0)
        with pytest.raises((TypeError, Exception), match="cannot assign"):
            fate.status = CellFateStatus.APOPTOSIS

    def test_population_outcome_frozen_rejects_mutation(self):
        """Cannot modify population_outcome.elapsed_time after creation."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=0.0,
            population_size=1,
            cell_cycle_phase=CellCyclePhase.G1
        )
        outcome = RepairOutcome()
        fate = CellFate(status=CellFateStatus.VIABLE, time_determined=0.0)
        pop = PopulationOutcome(
            damage_profile=dp,
            repair_outcomes=(outcome,),
            cell_fates=(fate,),
            elapsed_time=10.0
        )
        with pytest.raises((TypeError, Exception), match="cannot assign"):
            pop.elapsed_time = 20.0

    def test_frozen_dataclass_is_hashable(self):
        """Frozen dataclasses can be used in sets/dicts."""
        lesion1 = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0)
        lesion2 = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0)
        assert hash(lesion1) == hash(lesion2)
        assert {lesion1, lesion2} == {lesion1}  # Same hash = same set element


# ============================================================================
# Validation Tests: Boundary Values & Constraints
# ============================================================================

class TestDamageProfileValidation:
    """DamageProfile enforces dose and population constraints."""

    def test_dose_gy_negative_rejected(self):
        """dose_gy < 0 raises ValueError."""
        with pytest.raises(ValueError, match="dose_gy must be in"):
            DamageProfile(
                lesions=(),
                dose_gy=-1.0,
                population_size=100,
                cell_cycle_phase=CellCyclePhase.G1
            )

    def test_dose_gy_exceeds_max_rejected(self):
        """dose_gy > 10 raises ValueError."""
        with pytest.raises(ValueError, match="dose_gy must be in"):
            DamageProfile(
                lesions=(),
                dose_gy=11.0,
                population_size=100,
                cell_cycle_phase=CellCyclePhase.G1
            )

    def test_dose_gy_boundary_0_accepted(self):
        """dose_gy = 0 (no damage) accepted."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=0.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )
        assert dp.dose_gy == 0.0

    def test_dose_gy_boundary_10_accepted(self):
        """dose_gy = 10 accepted."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=10.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )
        assert dp.dose_gy == 10.0

    def test_population_size_zero_rejected(self):
        """population_size < 1 raises ValueError."""
        with pytest.raises(ValueError, match="population_size must be in"):
            DamageProfile(
                lesions=(),
                dose_gy=4.0,
                population_size=0,
                cell_cycle_phase=CellCyclePhase.G1
            )

    def test_population_size_exceeds_max_rejected(self):
        """population_size > 1M raises ValueError."""
        with pytest.raises(ValueError, match="population_size must be in"):
            DamageProfile(
                lesions=(),
                dose_gy=4.0,
                population_size=1_000_001,
                cell_cycle_phase=CellCyclePhase.G1
            )

    def test_population_size_boundary_1_accepted(self):
        """population_size = 1 accepted (single cell)."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=4.0,
            population_size=1,
            cell_cycle_phase=CellCyclePhase.G1
        )
        assert dp.population_size == 1

    def test_population_size_boundary_1m_accepted(self):
        """population_size = 1M accepted."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=4.0,
            population_size=1_000_000,
            cell_cycle_phase=CellCyclePhase.G1
        )
        assert dp.population_size == 1_000_000


# ============================================================================
# Temporal Ordering Tests
# ============================================================================

class TestTemporalOrdering:
    """Events must chain temporally (t0 < t1 < t2)."""

    def test_lesion_negative_time_rejected(self):
        """Lesion with time_seconds < 0 raises ValueError."""
        with pytest.raises(ValueError, match="time_seconds must be >= 0"):
            Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=-1.0)

    def test_repair_events_inverted_times_rejected(self):
        """start_time > end_time raises ValueError."""
        with pytest.raises(ValueError, match="start_time > end_time"):
            RepairEvent(
                pathway=RepairPathway.NHEJ,
                start_time=2.0,
                end_time=1.0,
                lesions_repaired=5,
                lesions_unrepaired=0
            )

    def test_repair_events_equal_times_accepted(self):
        """start_time == end_time (instantaneous repair) accepted."""
        event = RepairEvent(
            pathway=RepairPathway.NHEJ,
            start_time=1.0,
            end_time=1.0,
            lesions_repaired=1,
            lesions_unrepaired=0
        )
        assert event.duration_seconds == 0.0

    def test_damage_profile_lesions_not_ordered_rejected(self):
        """Lesions out of temporal order rejected."""
        lesion1 = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=2.0)
        lesion2 = Lesion(position_bp=2000, damage_type=DamageType.SSB, time_seconds=1.0)
        with pytest.raises(ValueError, match="ordered temporally"):
            DamageProfile(
                lesions=(lesion1, lesion2),  # Out of order
                dose_gy=4.0,
                population_size=100,
                cell_cycle_phase=CellCyclePhase.G1
            )

    def test_repair_outcome_events_overlap_rejected(self):
        """Overlapping repair events rejected."""
        event1 = RepairEvent(
            pathway=RepairPathway.NHEJ,
            start_time=0.0,
            end_time=2.0,
            lesions_repaired=5,
            lesions_unrepaired=0
        )
        event2 = RepairEvent(
            pathway=RepairPathway.HR,
            start_time=1.0,
            end_time=3.0,
            lesions_repaired=5,
            lesions_unrepaired=0
        )
        with pytest.raises(ValueError, match="must not overlap"):
            RepairOutcome(
                repair_events=(event1, event2),
                initial_lesions=10,
                total_repaired=10,
                success=True
            )


# ============================================================================
# Consistency Tests: Repair Counts
# ============================================================================

class TestRepairConsistency:
    """Repair counts must be consistent (repaired <= initial)."""

    def test_repair_outcome_repaired_exceeds_initial_rejected(self):
        """total_repaired > initial_lesions raises ValueError."""
        with pytest.raises(ValueError, match="total_repaired > initial_lesions"):
            RepairOutcome(
                initial_lesions=10,
                total_repaired=15,  # More than started with!
                success=False
            )

    def test_repair_outcome_success_with_unrepaired_rejected(self):
        """success=True but unrepaired > 0 raises ValueError."""
        with pytest.raises(ValueError, match="success=True but unrepaired"):
            RepairOutcome(
                initial_lesions=10,
                total_repaired=8,
                total_unrepaired=2,
                success=True  # Contradiction!
            )

    def test_repair_outcome_negative_counts_rejected(self):
        """Negative lesion counts rejected."""
        with pytest.raises(ValueError, match="cannot be negative"):
            RepairEvent(
                pathway=RepairPathway.NHEJ,
                start_time=0.0,
                end_time=1.0,
                lesions_repaired=-5,  # Invalid
                lesions_unrepaired=0
            )


# ============================================================================
# Population Outcome Consistency Tests
# ============================================================================

class TestPopulationOutcome:
    """Population outcomes must have consistent sizes."""

    def test_population_outcome_mismatched_repair_size_rejected(self):
        """repair_outcomes size != population_size raises ValueError."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=4.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )
        outcome = RepairOutcome()
        fate = CellFate(status=CellFateStatus.VIABLE, time_determined=0.0)

        with pytest.raises(ValueError, match="repair_outcomes size"):
            PopulationOutcome(
                damage_profile=dp,
                repair_outcomes=(outcome,),  # Only 1, but population=100
                cell_fates=(fate,) * 100,
                elapsed_time=10.0
            )

    def test_population_outcome_mismatched_fate_size_rejected(self):
        """cell_fates size != population_size raises ValueError."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=4.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )
        outcome = RepairOutcome()
        fate = CellFate(status=CellFateStatus.VIABLE, time_determined=0.0)

        with pytest.raises(ValueError, match="cell_fates size"):
            PopulationOutcome(
                damage_profile=dp,
                repair_outcomes=(outcome,) * 100,
                cell_fates=(fate,),  # Only 1, but population=100
                elapsed_time=10.0
            )

    def test_population_outcome_survival_rate_calculation(self):
        """survival_rate computed correctly."""
        dp = DamageProfile(
            lesions=(),
            dose_gy=4.0,
            population_size=4,
            cell_cycle_phase=CellCyclePhase.G1
        )
        outcomes = (RepairOutcome(),) * 4
        fates = (
            CellFate(status=CellFateStatus.VIABLE, time_determined=0.0),
            CellFate(status=CellFateStatus.VIABLE, time_determined=0.0),
            CellFate(status=CellFateStatus.APOPTOSIS, time_determined=0.0),
            CellFate(status=CellFateStatus.SENESCENCE, time_determined=0.0),
        )
        pop = PopulationOutcome(
            damage_profile=dp,
            repair_outcomes=outcomes,
            cell_fates=fates,
            elapsed_time=10.0
        )
        assert pop.survival_rate == 0.5  # 2 viable / 4 total


# ============================================================================
# Enum Validation Tests
# ============================================================================

class TestEnumValidation:
    """Enums enforce type safety."""

    def test_all_damage_types_present(self):
        """All damage types defined."""
        assert DamageType.DSB.value == "double_strand_break"
        assert DamageType.SSB.value == "single_strand_break"
        assert DamageType.CROSSLINK.value == "crosslink"

    def test_all_repair_pathways_present(self):
        """All repair pathways defined."""
        assert RepairPathway.NHEJ.value == "non_homologous_end_joining"
        assert RepairPathway.HR.value == "homologous_recombination"
        assert RepairPathway.BER.value == "base_excision_repair"

    def test_all_cell_fates_present(self):
        """All cell fates defined."""
        assert CellFateStatus.VIABLE.value == "viable"
        assert CellFateStatus.APOPTOSIS.value == "apoptosis"
        assert CellFateStatus.SENESCENCE.value == "senescence"

    def test_all_cell_cycle_phases_present(self):
        """All cell cycle phases defined."""
        assert CellCyclePhase.G1.value == "G1"
        assert CellCyclePhase.S.value == "S"
        assert CellCyclePhase.G2.value == "G2"
        assert CellCyclePhase.M.value == "M"


# ============================================================================
# Property-Based Tests (using hypothesis)
# ============================================================================

def test_lesion_count_matches_profile_tuple_length():
    """DamageProfile.lesion_count() == len(lesions)."""
    lesion1 = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0)
    lesion2 = Lesion(position_bp=2000, damage_type=DamageType.SSB, time_seconds=1.0)
    dp = DamageProfile(
        lesions=(lesion1, lesion2),
        dose_gy=4.0,
        population_size=100,
        cell_cycle_phase=CellCyclePhase.G1
    )
    assert dp.lesion_count() == 2


def test_repair_event_duration_positive_or_zero():
    """duration_seconds >= 0 always."""
    event = RepairEvent(
        pathway=RepairPathway.NHEJ,
        start_time=1.5,
        end_time=3.5,
        lesions_repaired=5,
        lesions_unrepaired=0
    )
    assert event.duration_seconds == 2.0
    assert event.duration_seconds >= 0


def test_population_outcome_rates_sum_close_to_1():
    """survival_rate + apoptosis_rate + senescence_rate ≈ 1."""
    dp = DamageProfile(
        lesions=(),
        dose_gy=4.0,
        population_size=100,
        cell_cycle_phase=CellCyclePhase.G1
    )
    outcomes = (RepairOutcome(),) * 100
    # 30 viable, 40 apoptosis, 30 senescence
    fates = (
        (CellFate(status=CellFateStatus.VIABLE, time_determined=0.0),) * 30 +
        (CellFate(status=CellFateStatus.APOPTOSIS, time_determined=0.0),) * 40 +
        (CellFate(status=CellFateStatus.SENESCENCE, time_determined=0.0),) * 30
    )
    pop = PopulationOutcome(
        damage_profile=dp,
        repair_outcomes=outcomes,
        cell_fates=fates,
        elapsed_time=10.0
    )
    total_rate = pop.survival_rate + pop.apoptosis_rate + pop.senescence_rate
    assert abs(total_rate - 1.0) < 0.01  # Within 1%
