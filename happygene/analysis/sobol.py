"""
SobolAnalyzer: Global sensitivity analysis via Sobol indices.

Computes first-order (S1) and total-effect (ST) Sobol indices using
SALib, providing insights into parameter importance and interactions.

Produces:
- Sobol indices with confidence intervals
- Parameter rankings (main effect, total effect, interaction)
- Convergence diagnostics
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from SALib.analyze import sobol as sobol_analyze
    SALIB_AVAILABLE = True
except ImportError:
    SALIB_AVAILABLE = False


@dataclass
class SobolIndices:
    """Container for Sobol sensitivity analysis results.

    Attributes
    ----------
    S1 : np.ndarray
        First-order (main effect) indices
    S1_conf : np.ndarray
        Confidence intervals for S1
    ST : np.ndarray
        Total-effect indices
    ST_conf : np.ndarray
        Confidence intervals for ST
    S2 : np.ndarray, optional
        Second-order interaction indices (if computed)
    param_names : list[str]
        Parameter names in order
    """

    S1: np.ndarray
    S1_conf: np.ndarray
    ST: np.ndarray
    ST_conf: np.ndarray
    param_names: List[str]
    S2: Optional[np.ndarray] = None

    def to_dataframe(self) -> pd.DataFrame:
        """Export indices as DataFrame for analysis and plotting.

        Returns
        -------
        pd.DataFrame
            Columns: param, S1, S1_conf, ST, ST_conf
        """
        df = pd.DataFrame(
            {
                "param": self.param_names,
                "S1": self.S1,
                "S1_conf": self.S1_conf,
                "ST": self.ST,
                "ST_conf": self.ST_conf,
            }
        )
        return df.sort_values("ST", ascending=False)


class SobolAnalyzer:
    """Sobol global sensitivity analysis wrapper.

    Orchestrates:
    - Sampling strategy (Sobol/Saltelli for Sobol analysis)
    - Index computation via SALib
    - Confidence interval estimation
    - Ranking and interaction detection

    Parameters
    ----------
    param_names : list[str]
        Parameter names in order
    param_space : dict[str, tuple]
        Parameter bounds (unused for analysis, kept for consistency)
    """

    def __init__(
        self, param_names: List[str], param_space: Optional[Dict] = None
    ):
        """Initialize SobolAnalyzer."""
        if not SALIB_AVAILABLE:
            raise ImportError("SALib required: pip install SALib")

        self.param_names = param_names
        self.param_space = param_space or {}
        self.n_params = len(param_names)

    def analyze(
        self,
        batch_results: pd.DataFrame,
        output_col: str = "survival",
        calc_second_order: bool = False,
    ) -> SobolIndices:
        """Compute Sobol indices from batch simulation results.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Output from BatchSimulator.run_batch() with parameter and output columns.
        output_col : str
            Name of output column to analyze (default: 'survival').
        calc_second_order : bool
            Whether to compute second-order indices (default: False).

        Returns
        -------
        SobolIndices
            Computed indices with confidence intervals.

        Raises
        ------
        ValueError
            If output_col not in batch_results or insufficient samples.
        """
        # Validate inputs
        if output_col not in batch_results.columns:
            raise ValueError(f"Output column '{output_col}' not found in results")

        # Extract parameter matrix and output vector
        param_cols = [p for p in self.param_names if p in batch_results.columns]
        if len(param_cols) != self.n_params:
            raise ValueError(
                f"Expected {self.n_params} params, found {len(param_cols)}"
            )

        Y = batch_results[output_col].values

        # Define problem for SALib
        problem = {
            "num_vars": self.n_params,
            "names": self.param_names,
            "bounds": self._get_bounds_from_results(batch_results),
        }

        # Compute Sobol indices
        Si = sobol_analyze(
            problem, Y, calc_second_order=calc_second_order, seed=42, conf_level=0.95
        )

        # Extract indices
        indices = SobolIndices(
            S1=Si["S1"],
            S1_conf=Si["S1_conf"],
            ST=Si["ST"],
            ST_conf=Si["ST_conf"],
            param_names=self.param_names,
            S2=Si.get("S2", None),
        )

        return indices

    def _get_bounds_from_results(self, batch_results: pd.DataFrame) -> List[Tuple]:
        """Extract parameter bounds from batch results (for SALib compatibility).

        Parameters
        ----------
        batch_results : pd.DataFrame
            Batch results with parameter columns.

        Returns
        -------
        list[tuple]
            Bounds as [(low, high), ...] for each parameter.
        """
        bounds = []
        for pname in self.param_names:
            if pname in batch_results.columns:
                min_val = float(batch_results[pname].min())
                max_val = float(batch_results[pname].max())
                bounds.append((min_val, max_val))
            else:
                # Default to [0, 1] if param not in results
                bounds.append((0.0, 1.0))

        return bounds

    def rank_parameters(
        self, indices: SobolIndices, by: str = "ST"
    ) -> pd.DataFrame:
        """Rank parameters by sensitivity index.

        Parameters
        ----------
        indices : SobolIndices
            Computed indices.
        by : {'S1', 'ST'}
            Index to rank by (default: 'ST' for total effect).

        Returns
        -------
        pd.DataFrame
            Parameters ranked by index, descending.
        """
        df = indices.to_dataframe()

        if by == "S1":
            df["rank"] = df["S1"].rank(ascending=False, method="min")
            return df.sort_values("S1", ascending=False)
        elif by == "ST":
            df["rank"] = df["ST"].rank(ascending=False, method="min")
            return df.sort_values("ST", ascending=False)
        else:
            raise ValueError(f"Unknown index: {by}")

    def detect_interactions(
        self, indices: SobolIndices, threshold: float = 0.1
    ) -> List[Tuple[str, str]]:
        """Detect significant parameter interactions from second-order indices.

        Parameters
        ----------
        indices : SobolIndices
            Computed indices with second-order (must have S2).
        threshold : float
            Minimum S2 value to consider significant (default: 0.1).

        Returns
        -------
        list[tuple]
            List of (param1, param2) pairs with significant interaction.

        Raises
        ------
        ValueError
            If S2 (second-order indices) not computed.
        """
        if indices.S2 is None:
            raise ValueError("Second-order indices not computed. Set calc_second_order=True")

        interactions = []
        for i in range(self.n_params):
            for j in range(i + 1, self.n_params):
                s2_val = indices.S2[i, j]
                if s2_val >= threshold:
                    interactions.append((self.param_names[i], self.param_names[j], s2_val))

        # Sort by S2 value descending
        interactions.sort(key=lambda x: x[2], reverse=True)
        return interactions
