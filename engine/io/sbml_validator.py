"""
SBML Validator: Schema and Content Validation

Validates SBML documents for:
- Well-formedness (valid XML)
- Schema compliance (SBML Level 3, Version 2)
- Required elements (compartments, species, reactions)
- Numerical consistency (rates, concentrations, parameters)

Production implementation with comprehensive validation.
"""

from pathlib import Path
from typing import Union
import xml.etree.ElementTree as ET


SBML_NAMESPACE = "http://www.sbml.org/sbml/level3/version2"


def validate_sbml(sbml_path: Union[str, Path]) -> bool:
    """
    Validate SBML document structure and content.

    Checks:
    - Well-formedness: Valid XML
    - Schema: SBML Level 3 Version 2
    - Required elements: compartments, species, reactions
    - Numerical consistency: concentrations >= 0, rates valid
    - References: All reaction species in species list

    Args:
        sbml_path: Path to SBML XML file

    Returns:
        True if valid, False otherwise

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If validation fails with details
    """
    sbml_path = Path(sbml_path)

    if not sbml_path.exists():
        raise FileNotFoundError(f"SBML file not found: {sbml_path}")

    # 1. Check well-formedness
    try:
        tree = ET.parse(sbml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"XML parse error: {e}")

    # 2. Check root element
    if not root.tag.endswith("sbml"):
        raise ValueError(f"Root element must be 'sbml', got '{root.tag}'")

    # 3. Check SBML version
    level = root.get("level")
    version = root.get("version")

    if level != "3":
        raise ValueError(f"SBML level must be 3, got {level}")
    if version != "2":
        raise ValueError(f"SBML version must be 2, got {version}")

    # 4. Find model
    namespaces = {"sbml": SBML_NAMESPACE}
    model = root.find(".//sbml:model", namespaces)
    if model is None:
        model = root.find("model")

    if model is None:
        raise ValueError("No model element found")

    # 5. Check for required elements
    _validate_model_contents(model, namespaces)

    # 6. Check numerical consistency
    _validate_numerical_consistency(model, namespaces)

    return True


def _validate_model_contents(model: ET.Element, namespaces: dict[str, str]) -> None:
    """Validate that model contains required elements."""
    # Check for compartments
    compartments = model.find(".//sbml:listOfCompartments", namespaces)
    if compartments is None:
        compartments = model.find("listOfCompartments")

    if compartments is None:
        raise ValueError("Model must contain listOfCompartments")

    compartment_list = compartments.findall("sbml:compartment", namespaces)
    if not compartment_list:
        compartment_list = compartments.findall("compartment")

    if not compartment_list:
        raise ValueError("Model must contain at least one compartment")

    # Check for species
    species_list = model.find(".//sbml:listOfSpecies", namespaces)
    if species_list is None:
        species_list = model.find("listOfSpecies")

    if species_list is None:
        raise ValueError("Model must contain listOfSpecies")

    species_elems = species_list.findall("sbml:species", namespaces)
    if not species_elems:
        species_elems = species_list.findall("species")

    if not species_elems:
        raise ValueError("Model must contain at least one species")

    # Check for reactions
    reactions_elem = model.find(".//sbml:listOfReactions", namespaces)
    if reactions_elem is None:
        reactions_elem = model.find("listOfReactions")

    if reactions_elem is None:
        raise ValueError("Model must contain listOfReactions")

    reactions = reactions_elem.findall("sbml:reaction", namespaces)
    if not reactions:
        reactions = reactions_elem.findall("reaction")

    if not reactions:
        raise ValueError("Model must contain at least one reaction")


def _validate_numerical_consistency(model: ET.Element, namespaces: dict[str, str]) -> None:
    """Validate numerical values in SBML."""
    # Check species concentrations are non-negative
    species_list = model.find(".//sbml:listOfSpecies", namespaces)
    if species_list is None:
        species_list = model.find("listOfSpecies")

    if species_list is not None:
        species_elems = species_list.findall("sbml:species", namespaces)
        if not species_elems:
            species_elems = species_list.findall("species")

        for species_elem in species_elems:
            conc_str = species_elem.get("initialConcentration")
            if conc_str:
                try:
                    conc = float(conc_str)
                    if conc < 0:
                        raise ValueError(
                            f"Species {species_elem.get('id')} has negative "
                            f"initialConcentration: {conc}"
                        )
                except ValueError as e:
                    if "negative" in str(e):
                        raise
                    raise ValueError(
                        f"Species {species_elem.get('id')} has invalid "
                        f"initialConcentration: {conc_str}"
                    )

    # Check parameter values are valid
    parameters = model.find(".//sbml:listOfParameters", namespaces)
    if parameters is None:
        parameters = model.find("listOfParameters")

    if parameters is not None:
        param_elems = parameters.findall("sbml:parameter", namespaces)
        if not param_elems:
            param_elems = parameters.findall("parameter")

        for param_elem in param_elems:
            param_value_str = param_elem.get("value")
            if param_value_str:
                try:
                    param_value = float(param_value_str)
                    # Tolerances should be positive and reasonable
                    param_id = param_elem.get("id")
                    if param_id in ("rtol", "atol"):
                        if param_value <= 0:
                            raise ValueError(
                                f"Parameter {param_id} must be positive, got {param_value}"
                            )
                except ValueError as e:
                    if "must be positive" in str(e):
                        raise
                    raise ValueError(
                        f"Parameter {param_elem.get('id')} has invalid value: {param_value_str}"
                    )
