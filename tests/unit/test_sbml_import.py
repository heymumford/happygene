"""
RED Phase: SBML Import Tests (Currently Failing)

These tests define the contract for SBML import. They will fail until
engine/io/sbml_import.py is implemented.

Tests verify:
- Reads valid SBML files
- Extracts species and reconstructs DamageProfile
- Extracts reactions and reconstructs repair events
- Extracts parameters and reconstructs KineticsConfig
- Validates SBML schema (Level 3 Version 2)
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from engine.domain.models import DamageProfile, DamageType, CellCyclePhase
from engine.domain.config import KineticsConfig


class TestSBMLImportBasics:
    """Basic SBML import structure tests."""

    def test_sbml_import_reads_valid_file(self):
        """SBML import can read a valid SBML file."""
        from engine.io.sbml_import import import_from_sbml

        # Create a minimal valid SBML file for testing
        sbml_content = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2" level="3" version="2">
  <model id="test_model">
    <listOfCompartments>
      <compartment id="nucleus" spatialDimensions="3" size="1"/>
    </listOfCompartments>
    <listOfSpecies>
      <species id="DSB_unrepaired" compartment="nucleus" initialConcentration="10"
               hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="DSB_repaired" compartment="nucleus" initialConcentration="0"
               hasOnlySubstanceUnits="false" boundaryCondition="false"/>
    </listOfSpecies>
    <listOfReactions>
    </listOfReactions>
  </model>
</sbml>"""

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "test.xml"
            sbml_path.write_text(sbml_content)

            # Act
            damage_profile, kinetics_config = import_from_sbml(sbml_path)

            # Assert
            assert isinstance(damage_profile, DamageProfile)
            assert isinstance(kinetics_config, KineticsConfig)

    def test_sbml_import_extracts_species(self):
        """SBML import extracts species and reconstructs lesion counts."""
        from engine.io.sbml_import import import_from_sbml

        sbml_content = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2" level="3" version="2">
  <model id="dna_repair">
    <listOfCompartments>
      <compartment id="nucleus" size="1"/>
    </listOfCompartments>
    <listOfSpecies>
      <species id="DSB_unrepaired" compartment="nucleus" initialConcentration="10"/>
      <species id="DSB_repaired" compartment="nucleus" initialConcentration="0"/>
      <species id="SSB_unrepaired" compartment="nucleus" initialConcentration="20"/>
      <species id="SSB_repaired" compartment="nucleus" initialConcentration="0"/>
    </listOfSpecies>
    <listOfReactions>
    </listOfReactions>
  </model>
</sbml>"""

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "test.xml"
            sbml_path.write_text(sbml_content)

            # Act
            damage_profile, _ = import_from_sbml(sbml_path)

            # Assert
            assert damage_profile.lesion_count() == 30  # 10 DSB + 20 SSB

    def test_sbml_import_extracts_reactions(self):
        """SBML import extracts reactions (repair pathways)."""
        from engine.io.sbml_import import import_from_sbml

        sbml_content = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2" level="3" version="2">
  <model id="dna_repair">
    <listOfCompartments>
      <compartment id="nucleus" size="1"/>
    </listOfCompartments>
    <listOfSpecies>
      <species id="DSB_unrepaired" compartment="nucleus" initialConcentration="10"/>
      <species id="DSB_repaired" compartment="nucleus" initialConcentration="0"/>
    </listOfSpecies>
    <listOfReactions>
      <reaction id="NHEJ_repair" reversible="false">
        <listOfReactants>
          <speciesReference species="DSB_unrepaired"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="DSB_repaired"/>
        </listOfProducts>
      </reaction>
      <reaction id="HR_repair" reversible="false">
        <listOfReactants>
          <speciesReference species="DSB_unrepaired"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="DSB_repaired"/>
        </listOfProducts>
      </reaction>
    </listOfReactions>
  </model>
</sbml>"""

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "test.xml"
            sbml_path.write_text(sbml_content)

            # Act
            damage_profile, _ = import_from_sbml(sbml_path)

            # Assert - should have extracted reaction information
            assert isinstance(damage_profile, DamageProfile)

    def test_sbml_import_extracts_parameters(self):
        """SBML import extracts parameters and reconstructs KineticsConfig."""
        from engine.io.sbml_import import import_from_sbml

        sbml_content = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2" level="3" version="2">
  <model id="dna_repair">
    <listOfCompartments>
      <compartment id="nucleus" size="1"/>
    </listOfCompartments>
    <listOfSpecies>
      <species id="DSB_unrepaired" compartment="nucleus" initialConcentration="10"/>
    </listOfSpecies>
    <listOfParameters>
      <parameter id="rtol" value="1e-6"/>
      <parameter id="atol" value="1e-9"/>
      <parameter id="method" value="BDF"/>
    </listOfParameters>
    <listOfReactions>
    </listOfReactions>
  </model>
</sbml>"""

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "test.xml"
            sbml_path.write_text(sbml_content)

            # Act
            _, kinetics_config = import_from_sbml(sbml_path)

            # Assert
            assert kinetics_config.rtol == 1e-6
            assert kinetics_config.atol == 1e-9

    def test_sbml_import_validates_schema(self):
        """SBML import validates schema (SBML Level 3 Version 2)."""
        from engine.io.sbml_import import import_from_sbml

        # Invalid SBML (missing level/version)
        invalid_sbml = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2">
  <model id="test"/>
</sbml>"""

        with TemporaryDirectory() as tmpdir:
            sbml_path = Path(tmpdir) / "invalid.xml"
            sbml_path.write_text(invalid_sbml)

            # Act & Assert - should raise validation error
            with pytest.raises(Exception):  # ValidationError or similar
                import_from_sbml(sbml_path)
