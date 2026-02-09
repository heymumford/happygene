"""
I/O Module: SBML Export, Import, Validation

This module handles serialization/deserialization of domain models to SBML format
for COPASI cross-validation and round-trip fidelity testing.

Implementations:
- sbml_export: HappyGeneConfig → SBML (XML)
- sbml_import: SBML (XML) → HappyGeneConfig
- sbml_validator: SBML schema and content validation
"""
