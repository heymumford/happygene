"""
MorrisAnalyzer: Fast parameter screening via Morris one-at-a-time (OAT).

Performs Morris screening as an economical alternative to Sobol,
suitable for high-dimensional problems where full factorial methods
are computationally expensive.

Produces:
- μ (mean effect): Parameter importance
- σ (std dev of effect): Parameter interaction
- μ* (mean absolute effect): Robustness to parameter range
- Parameter classification: Important, Interaction, Insignificant
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from SALib.analyze import morris as morris_analyze
    SALIB_AVAILABLE = True
except ImportError:
    SALIB_AVAILABLE = False


@dataclass
class MorrisIndices:
    """Container for Morris screening results.

    Attributes
    ----------
    mu : np.ndarray
        Mean effect (parameter importance)
    sigma : np.ndarray
        Std dev of effect (interaction/nonlinearity)
    mu_star : np.ndarray
        Mean absolute effect (robustness)
    param_names : list[str]
        Parameter names in order
    """

    mu: np.ndarray
    sigma: np.ndarray
    mu_star: np.ndarray
    param_names: List[str]

    def to_dataframe(self) -> pd.DataFrame:
        """Export indices as DataFrame for analysis and plotting.

        Returns
        -------
        pd.DataFrame
            Columns: param, mu, sigma, mu_star, classification
        """
        # Classify parameters
        classifications = []
        for i in range(len(self.param_names)):
            if self.mu_star[i] > 0.5:
                if self.sigma[i] > 0.5:
                    cls = "Interaction"
                else:
                    cls = "Important"
            else:
                cls = "Insignificant"
            classifications.append(cls)

        df = pd.DataFrame(
            {
                "param": self.param_names,
                "mu": self.mu,
                "sigma": self.sigma,
                "mu_star": self.mu_star,
                "classification": classifications,
            }
        )
        return df.sort_values("mu_star", ascending=False)


class MorrisAnalyzer:
    """Morris screening wrapper for sensitivity analysis.

    Orchestrates:
    - Morris OAT sampling strategy
    - Index computation via SALib
    - Parameter classification (important/interaction/insignificant)
    - Convergence diagnostics

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
        """Initialize MorrisAnalyzer."""
        if not SALIB_AVAILABLE:
            raise ImportError("SALib required: pip install SALib")

        self.param_names = param_names
        self.param_space = param_space or {}
        self.n_params = len(param_names)

    def analyze(
        self, batch_results: pd.DataFrame, output_col: str = "survival"
    ) -> MorrisIndices:
        """Compute Morris indices from batch simulation results.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Output from BatchSimulator.run_batch() with parameter and output columns.
        output_col : str
            Name of output column to analyze (default: 'survival').

        Returns
        -------
        MorrisIndices
            Computed indices.

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

        X = batch_results[param_cols].values
        Y = batch_results[output_col].values

        # Define problem for SALib
        problem = {
            "num_vars": self.n_params,
            "names": self.param_names,
            "bounds": self._get_bounds_from_results(batch_results),
        }

        # Compute Morris indices
        Si = morris_analyze(problem, X, Y, conf_level=0.95, seed=42)

        # Extract indices
        indices = MorrisIndices(
            mu=Si["mu"],
            sigma=Si["sigma"],
            mu_star=Si["mu_star"],
            param_names=self.param_names,
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

    def rank_parameters(self, indices: MorrisIndices, by: str = "mu_star") -> pd.DataFrame:
        """Rank parameters by Morris index.

        Parameters
        ----------
        indices : MorrisIndices
            Computed indices.
        by : {'mu', 'sigma', 'mu_star'}
            Index to rank by (default: 'mu_star').

        Returns
        -------
        pd.DataFrame
            Parameters ranked by index, descending.
        """
        df = indices.to_dataframe()

        if by == "mu":
            df["rank"] = df["mu"].rank(ascending=False, method="min")
            return df.sort_values("mu", ascending=False)
        elif by == "sigma":
            df["rank"] = df["sigma"].rank(ascending=False, method="min")
            return df.sort_values("sigma", ascending=False)
        elif by == "mu_star":
            df["rank"] = df["mu_star"].rank(ascending=False, method="min")
            return df.sort_values("mu_star", ascending=False)
        else:
            raise ValueError(f"Unknown index: {by}")

    def classify_parameters(
        self, indices: MorrisIndices, mu_threshold: float = 0.1, sigma_threshold: float = 0.1
    ) -> Dict[str, List[str]]:
        """Classify parameters into importance categories.

        Parameters
        ----------
        indices : MorrisIndices
            Computed indices.
        mu_threshold : float
            Threshold for mu_star to identify important parameters.
        sigma_threshold : float
            Threshold for sigma to identify interaction parameters.

        Returns
        -------
        dict
            Keys: 'Important', 'Interaction', 'Insignificant'
            Values: Lists of parameter names in each category.
        """
        important = []
        interaction = []
        insignificant = []

        for i, pname in enumerate(self.param_names):
            mu_star_val = indices.mu_star[i]
            sigma_val = indices.sigma[i]

            if mu_star_val < mu_threshold:
                insignificant.append(pname)
            elif sigma_val > sigma_threshold:
                interaction.append(pname)
            else:
                important.append(pname)

        return {
            "Important": sorted(important),
            "Interaction": sorted(interaction),
            "Insignificant": sorted(insignificant),
        }
