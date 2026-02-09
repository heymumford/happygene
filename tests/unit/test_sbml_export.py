"""
RED Phase: SBML Export Tests (Currently Failing)

These tests define the contract for SBML export. They will fail until
engine/io/sbml_export.py is implemented.

Tests verify:
- Valid SBML XML structure (COPASI-compatible, Level 3 Version 2)
- All damage types present as species
- All repair pathways present as reactions
- Initial conditions match DamageProfile
- Kinetics parameters exported correctly
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from engine.domain.models import (
    DamageType, RepairPathway, CellCyclePhase, Lesion, DamageProfile
)
from engine.domain.config import HappyGeneConfig, SimulationConfig, KineticsConfig


class TestSBMLExportBasics:
    """Basic SBML export structure tests."""

    def test_sbml_export_creates_valid_file(self):
        """SBML export creates a valid, readable XML file."""
        # Arrange
        from engine.io.sbml_export import export_to_sbml

        config = HappyGeneConfig()
        damage_profile = DamageProfile(
            lesions=(Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0),),
            dose_gy=4.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"

            # Act
            result = export_to_sbml(config, damage_profile, output_path)

            # Assert
            assert result.exists()
            assert result.suffix == ".xml"

            # Verify XML is well-formed
            tree = ET.parse(result)
            root = tree.getroot()
            assert root.tag.endswith("sbml")

    def test_sbml_export_includes_root_namespace(self):
        """SBML document includes proper SBML namespace."""
        from engine.io.sbml_export import export_to_sbml

        config = HappyGeneConfig()
        damage_profile = DamageProfile(
            lesions=tuple(),
            dose_gy=2.0,
            population_size=50,
            cell_cycle_phase=CellCyclePhase.S
        )

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            result = export_to_sbml(config, damage_profile, output_path)

            tree = ET.parse(result)
            root = tree.getroot()

            # SBML namespace should be present
            assert "sbml.org" in root.tag or "sbml" in root.tag.lower()

    def test_sbml_export_includes_all_damage_types(self):
        """SBML export includes all damage types as species."""
        from engine.io.sbml_export import export_to_sbml

        config = HappyGeneConfig()
        lesions = tuple(
            Lesion(position_bp=i*1000, damage_type=dt, time_seconds=0.0)
            for i, dt in enumerate(DamageType)
        )
        damage_profile = DamageProfile(
            lesions=lesions,
            dose_gy=1.0,
            population_size=10,
            cell_cycle_phase=CellCyclePhase.G2
        )

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            result = export_to_sbml(config, damage_profile, output_path)

            tree = ET.parse(result)
            root = tree.getroot()

            # Find all species elements (damage types as unrepaired/repaired pairs)
            namespaces = {"sbml": "http://www.sbml.org/sbml/level3/version2"}
            species_list = root.findall(".//sbml:listOfSpecies/sbml:species", namespaces)

            # Should have at least 2 species per damage type (unrepaired, repaired)
            assert len(species_list) >= len(DamageType) * 2

    def test_sbml_export_includes_all_repair_pathways(self):
        """SBML export includes all repair pathways as reactions."""
        from engine.io.sbml_export import export_to_sbml

        config = HappyGeneConfig()
        damage_profile = DamageProfile(
            lesions=tuple(),
            dose_gy=3.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.M
        )

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            result = export_to_sbml(config, damage_profile, output_path)

            tree = ET.parse(result)
            root = tree.getroot()

            # Find all reaction elements
            namespaces = {"sbml": "http://www.sbml.org/sbml/level3/version2"}
            reactions = root.findall(".//sbml:listOfReactions/sbml:reaction", namespaces)

            # Should have reactions for all repair pathways
            assert len(reactions) >= len(RepairPathway)

    def test_sbml_export_initial_conditions_match_damage_profile(self):
        """SBML species initialConcentration values match DamageProfile."""
        from engine.io.sbml_export import export_to_sbml

        config = HappyGeneConfig()
        # Create specific damage profile: 10 DSB, 20 SSB
        damage_profile = DamageProfile(
            lesions=(
                *[Lesion(position_bp=i*100, damage_type=DamageType.DSB, time_seconds=0.0)
                  for i in range(10)],
                *[Lesion(position_bp=i*100+5000, damage_type=DamageType.SSB, time_seconds=0.0)
                  for i in range(20)],
            ),
            dose_gy=2.0,
            population_size=100,
            cell_cycle_phase=CellCyclePhase.G1
        )

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            result = export_to_sbml(config, damage_profile, output_path)

            tree = ET.parse(result)
            root = tree.getroot()

            # Find DSB_unrepaired species
            namespaces = {"sbml": "http://www.sbml.org/sbml/level3/version2"}
            species = root.findall(".//sbml:species", namespaces)

            dsb_unrepaired = None
            ssb_unrepaired = None
            for s in species:
                spec_id = s.get("id")
                if spec_id and "DSB" in spec_id and "unrepaired" in spec_id:
                    dsb_unrepaired = s
                if spec_id and "SSB" in spec_id and "unrepaired" in spec_id:
                    ssb_unrepaired = s

            assert dsb_unrepaired is not None, "DSB_unrepaired species not found"
            assert ssb_unrepaired is not None, "SSB_unrepaired species not found"

            # Check initial concentrations (lesion counts)
            assert float(dsb_unrepaired.get("initialConcentration")) == 10.0
            assert float(ssb_unrepaired.get("initialConcentration")) == 20.0

    def test_sbml_export_kinetics_parameters_match_config(self):
        """SBML kinetic law parameters match KineticsConfig."""
        from engine.io.sbml_export import export_to_sbml

        kinetics_config = KineticsConfig(rtol=1e-7, atol=1e-10, method="RK45")
        config = HappyGeneConfig(kinetics=kinetics_config)
        damage_profile = DamageProfile(
            lesions=tuple(),
            dose_gy=1.0,
            population_size=10,
            cell_cycle_phase=CellCyclePhase.G1
        )

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            result = export_to_sbml(config, damage_profile, output_path)

            tree = ET.parse(result)
            root = tree.getroot()

            # Find model parameters
            namespaces = {"sbml": "http://www.sbml.org/sbml/level3/version2"}
            parameters = root.findall(".//sbml:parameter", namespaces)

            # Should have at least rtol, atol parameters
            param_ids = {p.get("id") for p in parameters}
            assert "rtol" in param_ids or "relative_tolerance" in param_ids
            assert "atol" in param_ids or "absolute_tolerance" in param_ids
