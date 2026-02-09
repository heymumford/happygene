# Phase 5: Cross-Validation (SBML Export + COPASI Round-Trip)

**Goal**: Verify domain models are correct via SBML export and COPASI validation. <0.1% RMSE on round-trip.

**Duration**: 1-2 days

---

## Problem

Domain models are theoretically sound (82 passing tests), but are they *semantically correct* for DNA repair simulations?

**Validation strategy**: Export to SBML (Systems Biology Markup Language), load into COPASI reference implementation, verify round-trip fidelity.

**Success threshold**: RMSE < 0.1% (0.001 relative error)

---

## Architecture

### SBML Structure (COPASI-Compatible)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2" level="3" version="2">
  <model id="dna_repair" name="DNA Repair Model">
    <!-- Species: Lesions (DSB, SSB, etc.) -->
    <listOfCompartments>
      <compartment id="nucleus" spatialDimensions="3" size="1"/>
    </listOfCompartments>

    <listOfSpecies>
      <species id="DSB_unrepaired" compartment="nucleus" initialConcentration="10"
               hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="DSB_repaired" compartment="nucleus" initialConcentration="0"
               hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <!-- SSB, Crosslinks, etc. -->
    </listOfSpecies>

    <!-- Reactions: Repair pathways (NHEJ, HR, BER, etc.) -->
    <listOfReactions>
      <!-- NHEJ: DSB → repaired (fast, error-prone) -->
      <reaction id="NHEJ_DSB_repair" reversible="false" fast="false">
        <listOfReactants>
          <speciesReference species="DSB_unrepaired" stoichiometry="1"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="DSB_repaired" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply><times/>
              <ci>k_NHEJ</ci>
              <ci>DSB_unrepaired</ci>
            </apply>
          </math>
          <listOfParameters>
            <parameter id="k_NHEJ" value="0.1"/>
          </listOfParameters>
        </kineticLaw>
      </reaction>
      <!-- HR, BER, NER, MMR, TLS, altEJ -->
    </listOfReactions>
  </model>
</sbml>
```

### Round-Trip Validation

```
HappyGeneConfig (Pydantic)
    ↓
DomainModel (frozen dataclasses)
    ↓
SBML Export
    ↓
SBML File
    ↓
COPASI Load
    ↓
COPASI Simulation
    ↓
Results JSON
    ↓
Compare to HappyGene Results
    ↓
RMSE < 0.1% ✓
```

---

## Week 2 Breakdown

### Day 1: RED Phase (Failing Tests)

**Tests to create** (all expecting NotImplementedError or AssertionError):

1. **SBML Export Tests** (`tests/unit/test_sbml_export.py`)
   - test_sbml_export_creates_valid_file
   - test_sbml_export_includes_all_damage_types
   - test_sbml_export_includes_all_repair_pathways
   - test_sbml_export_kinetics_parameters_match_config
   - test_sbml_export_boundary_conditions_set
   - test_sbml_export_initial_conditions_match_damage_profile

2. **SBML Import Tests** (`tests/unit/test_sbml_import.py`)
   - test_sbml_import_reads_valid_file
   - test_sbml_import_extracts_species
   - test_sbml_import_extracts_reactions
   - test_sbml_import_extracts_parameters
   - test_sbml_import_validates_schema

3. **Round-Trip Tests** (`tests/unit/test_sbml_roundtrip.py`)
   - test_roundtrip_config_to_sbml_to_config
   - test_roundtrip_damage_profile_preserved
   - test_roundtrip_kinetics_parameters_preserved
   - test_roundtrip_species_counts_match

**Test fixtures**:
   - Sample DamageProfile (10 DSB, 20 SSB)
   - Sample KineticsConfig (BDF, rtol=1e-6)
   - Sample SBML file (valid, COPASI-compatible)

### Day 2: GREEN Phase (Implementation)

**Code to create**:

1. **SBML Export** (`engine/io/sbml_export.py`)
   - `export_to_sbml(config, damage_profile, output_path) -> Path`
   - Generates SBML from domain models
   - Includes all repair pathways (NHEJ, HR, BER, NER, MMR, TLS, altEJ)
   - Sets initial conditions from DamageProfile
   - Exports kinetics parameters (rtol, atol, solver method)

2. **SBML Import** (`engine/io/sbml_import.py`)
   - `import_from_sbml(sbml_path) -> Tuple[DamageProfile, KineticsConfig]`
   - Parses SBML, extracts species and reactions
   - Reconstructs domain models
   - Validates schema (SBML v3 level 2)

3. **Validation** (`engine/io/sbml_validator.py`)
   - `validate_sbml(sbml_path) -> bool`
   - Checks well-formedness
   - Checks required elements (compartments, species, reactions)
   - Checks numerical consistency

**Dependencies to add**:
   - `libsbml` (Python bindings for SBML)
   - `lxml` (XML parsing, validation)

### Day 3: BLUE Phase (Refactoring)

- Type hints: 100%
- Docstrings: 100%
- Error messages: Publication-grade
- Tests: 100% passing

---

## Implementation Details

### SBML Export Algorithm

```python
def export_to_sbml(config: HappyGeneConfig, damage_profile: DamageProfile, path: Path) -> Path:
    """
    Export simulation config to SBML (COPASI-compatible).

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
    """
    pass
```

### SBML Import Algorithm

```python
def import_from_sbml(sbml_path: Path) -> Tuple[DamageProfile, KineticsConfig]:
    """
    Import SBML file and reconstruct domain models.

    Algorithm:
    1. Parse SBML document
    2. Extract compartments
    3. Extract species:
       - Group by damage type (DSB_unrepaired, SSB_unrepaired, ...)
       - Reconstruct Lesions with initialConcentration
    4. Extract reactions and kinetic laws
    5. Extract parameters (rtol, atol, solver)
    6. Reconstruct DamageProfile and KineticsConfig
    7. Validate schema
    """
    pass
```

### Validation Metrics

```python
def compute_rmse(original: RepairOutcome, exported: RepairOutcome) -> float:
    """
    Compute RMSE between original and round-trip exported outcomes.

    Metrics:
    - lesion_count: abs(original.initial_lesions - exported.initial_lesions)
    - repair_events: len(original.repair_events) vs len(exported.repair_events)
    - fidelity: max(original.fidelity) vs max(exported.fidelity)
    - timing: sum(abs(t_orig - t_export)) / len(times)

    Return: relative RMSE (0.001 = 0.1%)
    """
    pass
```

---

## File Structure

```
engine/
├── domain/
│   ├── models.py           ✅ (Phase 4)
│   └── config.py           ✅ (Phase 4)
├── io/
│   ├── __init__.py
│   ├── sbml_export.py      ← NEW
│   ├── sbml_import.py      ← NEW
│   └── sbml_validator.py   ← NEW
└── tests/
    ├── unit/
    │   ├── test_sbml_export.py     ← NEW (RED)
    │   ├── test_sbml_import.py     ← NEW (RED)
    │   └── test_sbml_roundtrip.py  ← NEW (RED)
    └── fixtures/
        └── sample.sbml             ← Reference file
```

---

## Success Criteria

- [ ] 20+ unit tests (all passing)
- [ ] SBML export: Valid, COPASI-loadable
- [ ] SBML import: Reconstructs domain models accurately
- [ ] Round-trip: RMSE < 0.1% (0.001 relative error)
- [ ] Type hints: 100%
- [ ] Docstrings: 100%
- [ ] Error handling: Publication-grade

---

## Dependencies

Add to `pyproject.toml`:

```toml
[project.optional-dependencies]
io = [
    "python-libsbml>=5.20",
    "lxml>=4.9",
]
```

---

## References

- [SBML Specification](http://sbml.org/documents/specifications/)
- [libsbml Python API](https://sbml.org/software/libsbml/)
- [COPASI User Manual](http://copasi.org/Support/User%20Manual/)
- [SBML Best Practices](http://sbml.org/Documents/Specifications/SBML_Level_3/Recommended_Practices_for_SBML_Level_3)

---

## Status

**NOT STARTED** - Ready for Phase 5 (RED)
