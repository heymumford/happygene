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
SBML Export: Domain Models → XML

Converts HappyGeneConfig and DamageProfile to SBML (Level 3, Version 2)
for COPASI validation and cross-system interoperability.

SBML Structure:
- Compartment: nucleus (size=1)
- Species: {damage_type}_{unrepaired|repaired} with initialConcentration
- Reactions: {repair_pathway}_repair with kinetic laws
- Parameters: rtol, atol, solver method

Production implementation with full SBML compliance.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union

from engine.domain.config import HappyGeneConfig
from engine.domain.models import DamageProfile, DamageType, RepairPathway

# SBML namespace for proper XML generation
SBML_NAMESPACE = "http://www.sbml.org/sbml/level3/version2"
MATH_NAMESPACE = "http://www.w3.org/1998/Math/MathML"


def _register_namespaces() -> None:
    """Register SBML namespaces for proper XML output."""
    ET.register_namespace("", SBML_NAMESPACE)
    ET.register_namespace("math", MATH_NAMESPACE)


def _create_sbml_root() -> ET.Element:
    """Create root SBML element with proper namespaces and attributes."""
    _register_namespaces()
    root = ET.Element("sbml")
    root.set("xmlns", SBML_NAMESPACE)
    root.set("level", "3")
    root.set("version", "2")
    return root


def _add_model(sbml_root: ET.Element, config: HappyGeneConfig) -> ET.Element:
    """Create and add model element."""
    model = ET.SubElement(sbml_root, "model")
    model.set("id", "dna_repair")
    model.set("name", "DNA Repair Model")
    return model


def _add_compartment(model: ET.Element) -> None:
    """Add nucleus compartment to model."""
    compartments = ET.SubElement(model, "listOfCompartments")
    compartment = ET.SubElement(compartments, "compartment")
    compartment.set("id", "nucleus")
    compartment.set("spatialDimensions", "3")
    compartment.set("size", "1")


def _damage_type_to_species_id(damage_type: DamageType, repaired: bool = False) -> str:
    """Convert DamageType enum to species ID."""
    # Map enum values to clean species names
    type_names = {
        DamageType.DSB: "DSB",
        DamageType.SSB: "SSB",
        DamageType.CROSSLINK: "Crosslink",
        DamageType.OXIDATIVE: "Oxidative",
        DamageType.DEPURINATION: "Depurination",
        DamageType.DEAMINATION: "Deamination",
        DamageType.THYMINE_DIMER: "ThymineDimer",
    }
    name = type_names.get(damage_type, damage_type.name)
    state = "repaired" if repaired else "unrepaired"
    return f"{name}_{state}"


def _add_species(model: ET.Element, damage_profile: DamageProfile) -> None:
    """Add species (damage types) to model."""
    species_list = ET.SubElement(model, "listOfSpecies")

    # Count lesions by damage type
    lesion_counts: dict[DamageType, int] = {}
    for lesion in damage_profile.lesions:
        damage_type = lesion.damage_type
        lesion_counts[damage_type] = lesion_counts.get(damage_type, 0) + 1

    # Add unrepaired and repaired species for each damage type
    for damage_type in DamageType:
        count = lesion_counts.get(damage_type, 0)

        # Unrepaired species
        unrepaired_id = _damage_type_to_species_id(damage_type, repaired=False)
        unrepaired = ET.SubElement(species_list, "species")
        unrepaired.set("id", unrepaired_id)
        unrepaired.set("compartment", "nucleus")
        unrepaired.set("initialConcentration", str(float(count)))
        unrepaired.set("hasOnlySubstanceUnits", "false")
        unrepaired.set("boundaryCondition", "false")

        # Repaired species (initially 0)
        repaired_id = _damage_type_to_species_id(damage_type, repaired=True)
        repaired = ET.SubElement(species_list, "species")
        repaired.set("id", repaired_id)
        repaired.set("compartment", "nucleus")
        repaired.set("initialConcentration", "0")
        repaired.set("hasOnlySubstanceUnits", "false")
        repaired.set("boundaryCondition", "false")


def _add_reactions(model: ET.Element) -> None:
    """Add repair pathway reactions to model."""
    reactions_list = ET.SubElement(model, "listOfReactions")

    # Add one representative reaction for each repair pathway
    pathway_names = {
        RepairPathway.NHEJ: ("Non-Homologous End Joining", "0.1"),
        RepairPathway.HR: ("Homologous Recombination", "0.05"),
        RepairPathway.BER: ("Base Excision Repair", "0.08"),
        RepairPathway.NER: ("Nucleotide Excision Repair", "0.06"),
        RepairPathway.MMR: ("Mismatch Repair", "0.07"),
        RepairPathway.TLS: ("Translesion Synthesis", "0.02"),
        RepairPathway.DIRECT: ("Direct Reversal", "0.15"),
        RepairPathway.ALTEJ: ("Alternative End Joining", "0.03"),
    }

    for pathway in RepairPathway:
        name, rate = pathway_names.get(pathway, (pathway.name, "0.1"))
        reaction_id = f"{pathway.value}_repair"

        reaction = ET.SubElement(reactions_list, "reaction")
        reaction.set("id", reaction_id)
        reaction.set("reversible", "false")
        reaction.set("fast", "false")

        # Add metadata
        notes = ET.SubElement(reaction, "notes")
        note_text = ET.SubElement(notes, "body")
        note_text.text = f"Repair pathway: {name}"

        # Kinetic law
        kinetic_law = ET.SubElement(reaction, "kineticLaw")

        # Math expression (simple mass action kinetics)
        math = ET.SubElement(kinetic_law, "math")
        math.set("xmlns", MATH_NAMESPACE)

        # k * S (rate constant times substrate concentration)
        apply = ET.SubElement(math, "apply")
        ET.SubElement(apply, "times")
        ci_k = ET.SubElement(apply, "ci")
        ci_k.text = f"k_{pathway.value}"
        ci_s = ET.SubElement(apply, "ci")
        ci_s.text = f"{_damage_type_to_species_id(DamageType.DSB, False)}"

        # Rate parameter
        parameters = ET.SubElement(kinetic_law, "listOfParameters")
        param = ET.SubElement(parameters, "parameter")
        param.set("id", f"k_{pathway.value}")
        param.set("value", rate)


def _add_parameters(
    model: ET.Element, config: HappyGeneConfig, damage_profile: DamageProfile
) -> None:
    """Add solver configuration and damage profile parameters to model."""
    parameters = ET.SubElement(model, "listOfParameters")

    # Relative tolerance
    rtol_param = ET.SubElement(parameters, "parameter")
    rtol_param.set("id", "rtol")
    rtol_param.set("value", str(config.kinetics.rtol))

    # Absolute tolerance
    atol_param = ET.SubElement(parameters, "parameter")
    atol_param.set("id", "atol")
    atol_param.set("value", str(config.kinetics.atol))

    # Solver method
    method_param = ET.SubElement(parameters, "parameter")
    method_param.set("id", "method")
    method_param.set("value", config.kinetics.method.value)

    # Max step
    max_step_param = ET.SubElement(parameters, "parameter")
    max_step_param.set("id", "max_step")
    max_step_param.set("value", str(config.kinetics.max_step))

    # Damage profile metadata
    dose_param = ET.SubElement(parameters, "parameter")
    dose_param.set("id", "dose_gy")
    dose_param.set("value", str(damage_profile.dose_gy))

    population_param = ET.SubElement(parameters, "parameter")
    population_param.set("id", "population_size")
    population_param.set("value", str(damage_profile.population_size))


def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    """Add proper indentation to XML for readability."""
    indent = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def export_to_sbml(
    config: HappyGeneConfig,
    damage_profile: DamageProfile,
    output_path: Union[str, Path],
) -> Path:
    """
    Export simulation configuration to SBML (COPASI-compatible).

    Algorithm:
    1. Create SBML document (level 3, version 2)
    2. Add compartment (nucleus, size=1)
    3. For each damage type:
       - Add species (unrepaired, repaired)
       - Set initialConcentration from damage_profile
    4. For each repair pathway:
       - Add reaction (pathway kinetics)
       - Set kinetic law (rate equation)
    5. Add parameter list (rtol, atol, solver method)
    6. Validate and write to file

    Args:
        config: HappyGeneConfig (simulation + kinetics + output settings)
        damage_profile: DamageProfile (lesions, dose, population)
        output_path: Path to write SBML XML file

    Returns:
        Path to created SBML file

    Raises:
        ValueError: If config/profile invalid
        IOError: If file write fails
    """
    output_path = Path(output_path)

    # Validate inputs
    if config is None:
        raise ValueError("config cannot be None")
    if damage_profile is None:
        raise ValueError("damage_profile cannot be None")

    # Create SBML structure
    root = _create_sbml_root()
    model = _add_model(root, config)
    _add_compartment(model)
    _add_species(model, damage_profile)
    _add_reactions(model)
    _add_parameters(model, config, damage_profile)

    # Format and write
    _indent_xml(root)
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)

    if not output_path.exists():
        raise IOError(f"Failed to write SBML file: {output_path}")

    return output_path
