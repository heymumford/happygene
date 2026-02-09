
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
I/O Module: SBML Export, Import, Validation

This module handles serialization/deserialization of domain models to SBML format
for COPASI cross-validation and round-trip fidelity testing.

Implementations:
- sbml_export: HappyGeneConfig → SBML (XML)
- sbml_import: SBML (XML) → HappyGeneConfig
- sbml_validator: SBML schema and content validation
"""
