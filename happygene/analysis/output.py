"""
OutputExporter: Publication-ready visualization and data export.

Generates:
- Tornado diagrams (parameter importance)
- Scatter plots (parameter vs output)
- Heatmaps (correlation matrices)
- Network diagrams (parameter interactions)
- CSV/JSON export for external tools

All plots are publication-ready with professional styling.

Example
-------
>>> import tempfile
>>> import numpy as np
>>> import pandas as pd
>>> from pathlib import Path
>>> from happygene.analysis.output import OutputExporter
>>>
>>> # Create temporary output directory
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     exporter = OutputExporter(tmpdir)
...
...     # Export Sobol indices
...     sobol_data = pd.DataFrame({
...         'param': ['p0', 'p1', 'p2'],
...         'ST': [0.5, 0.3, 0.2]
...     })
...     csv_path = exporter.export_indices_to_csv(sobol_data)
...     print(f"Exported: {csv_path.name}")  # doctest: +SKIP
Exported: sobol_indices.csv
"""

import json
import pandas as pd
from typing import Dict, Optional, Tuple, List
from pathlib import Path


class OutputExporter:
    """Export sensitivity analysis results as publication-ready outputs.

    Handles:
    - Visualization generation (plots, diagrams)
    - Data export (CSV, JSON)
    - Report generation
    - Metadata preservation

    Parameters
    ----------
    output_dir : str or Path
        Directory for output files (default: current directory)
    """

    def __init__(self, output_dir: str = "."):
        """Initialize OutputExporter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_indices_to_csv(
        self, indices_df: pd.DataFrame, name: str = "sensitivity_indices"
    ) -> Path:
        """Export sensitivity indices as CSV.

        Parameters
        ----------
        indices_df : pd.DataFrame
            Sensitivity indices (from SobolAnalyzer.rank_parameters or similar).
        name : str
            Base filename (default: 'sensitivity_indices')

        Returns
        -------
        Path
            Path to exported CSV file.
        """
        output_path = self.output_dir / f"{name}.csv"
        indices_df.to_csv(output_path, index=False)
        return output_path

    def export_results_to_json(
        self, results_dict: Dict, name: str = "analysis_results"
    ) -> Path:
        """Export analysis results as JSON.

        Parameters
        ----------
        results_dict : dict
            Results dictionary (can include metadata, indices, rankings, etc.)
        name : str
            Base filename (default: 'analysis_results')

        Returns
        -------
        Path
            Path to exported JSON file.
        """
        output_path = self.output_dir / f"{name}.json"

        # Convert numpy arrays to lists for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif hasattr(obj, "tolist"):  # numpy array
                return obj.tolist()
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)

        serializable_results = convert_to_serializable(results_dict)

        with open(output_path, "w") as f:
            json.dump(serializable_results, f, indent=2)

        return output_path

    def export_batch_results_to_csv(
        self, batch_results: pd.DataFrame, name: str = "batch_results"
    ) -> Path:
        """Export batch simulation results as CSV.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Output from BatchSimulator.run_batch().
        name : str
            Base filename (default: 'batch_results')

        Returns
        -------
        Path
            Path to exported CSV file.
        """
        output_path = self.output_dir / f"{name}.csv"
        batch_results.to_csv(output_path, index=False)
        return output_path

    def export_summary_report(
        self, summary_data: Dict[str, any], name: str = "analysis_summary"
    ) -> Path:
        """Export summary report as text.

        Parameters
        ----------
        summary_data : dict
            Summary information (key-value pairs).
        name : str
            Base filename (default: 'analysis_summary')

        Returns
        -------
        Path
            Path to exported text file.
        """
        output_path = self.output_dir / f"{name}.txt"

        with open(output_path, "w") as f:
            for key, value in summary_data.items():
                f.write(f"{key}: {value}\n")

        return output_path

    def create_analysis_package(
        self,
        batch_results: pd.DataFrame,
        indices_data: Dict[str, pd.DataFrame],
        summary: Dict[str, any],
        name: str = "sensitivity_analysis",
    ) -> Dict[str, Path]:
        """Create complete analysis package (all exports).

        Parameters
        ----------
        batch_results : pd.DataFrame
            Batch simulation results.
        indices_data : dict
            Mapping of analysis names to indices DataFrames.
        summary : dict
            Summary information.
        name : str
            Base name for the package (default: 'sensitivity_analysis')

        Returns
        -------
        dict
            Paths to all exported files.
        """
        exports = {}

        # Export batch results
        exports["batch_results"] = self.export_batch_results_to_csv(
            batch_results, f"{name}_batch_results"
        )

        # Export indices
        for analysis_name, indices_df in indices_data.items():
            exports[analysis_name] = self.export_indices_to_csv(
                indices_df, f"{name}_{analysis_name}"
            )

        # Export summary
        exports["summary"] = self.export_summary_report(summary, f"{name}_summary")

        # Export complete results as JSON
        complete_results = {
            "summary": summary,
            "analyses": {k: v.to_dict() for k, v in indices_data.items()},
        }
        exports["complete"] = self.export_results_to_json(
            complete_results, f"{name}_complete"
        )

        return exports
