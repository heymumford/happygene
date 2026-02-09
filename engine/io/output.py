
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
Result Output Formatting

Saves simulation results to disk in multiple formats with automatic
parent directory creation and format detection.

Supported Formats:
- HDF5 (.h5): Binary format with compression for large datasets
- JSON (.json): Human-readable format for interoperability
- CSV (.csv): Spreadsheet format for Excel compatibility

Examples:
    >>> writer = OutputWriter(OutputFormat.HDF5)
    >>> writer.write(results, Path("output.h5"))
"""

import csv
import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict

import h5py
import numpy as np


class OutputFormat(Enum):
    """Supported output formats."""

    HDF5 = "hdf5"
    JSON = "json"
    CSV = "csv"


class OutputWriter:
    """Writes simulation results to files."""

    def __init__(self, format: OutputFormat) -> None:
        """
        Initialize output writer.

        Args:
            format: Output format to use

        Raises:
            ValueError: If format invalid
        """
        if not isinstance(format, OutputFormat):
            raise ValueError(f"Invalid format: {format}")
        self.format = format

    def write(self, data: Dict[str, Any], output_path: Path) -> None:
        """
        Write data to output file.

        Creates parent directories if needed.

        Args:
            data: Data dictionary to write
            output_path: Path to write file to

        Raises:
            ValueError: If format unsupported
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.format == OutputFormat.HDF5:
            self._write_hdf5(data, output_path)
        elif self.format == OutputFormat.JSON:
            self._write_json(data, output_path)
        elif self.format == OutputFormat.CSV:
            self._write_csv(data, output_path)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    @staticmethod
    def _write_hdf5(data: Dict[str, Any], output_path: Path) -> None:
        """Write data to HDF5 file."""
        with h5py.File(output_path, "w") as f:
            for key, value in data.items():
                try:
                    # Handle lists and arrays
                    if isinstance(value, (list, np.ndarray)):
                        f.create_dataset(key, data=np.array(value))
                    elif isinstance(value, (int, float)):
                        f.create_dataset(key, data=value)
                    else:
                        # Store as string for complex types
                        f.create_dataset(key, data=str(value))
                except (TypeError, ValueError):
                    # Fallback for complex types
                    f.create_dataset(key, data=str(value))

    @staticmethod
    def _write_json(data: Dict[str, Any], output_path: Path) -> None:
        """Write data to JSON file."""
        # Convert numpy types to Python types for JSON serialization
        json_data: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                json_data[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                json_data[key] = float(value)
            else:
                json_data[key] = value

        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=2)

    @staticmethod
    def _write_csv(data: Dict[str, Any], output_path: Path) -> None:
        """Write data to CSV file."""
        # Convert data to rows (handles both scalar and array values)
        rows: list[dict[str, Any]] = []

        # Find the maximum number of rows (for list/array values)
        max_rows = 1
        for value in data.values():
            if isinstance(value, (list, np.ndarray)):
                max_rows = max(max_rows, len(value))

        # Build rows
        for i in range(max_rows):
            row: dict[str, Any] = {}
            for key, value in data.items():
                if isinstance(value, (list, np.ndarray)):
                    row[key] = value[i] if i < len(value) else ""
                else:
                    row[key] = value if i == 0 else ""
            rows.append(row)

        # Write CSV
        if rows:
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                writer.writeheader()
                writer.writerows(rows)
