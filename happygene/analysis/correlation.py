"""
CorrelationAnalyzer: Parameter interaction and correlation analysis.

Detects parameter interactions through:
- Pearson correlation (linear relationships)
- Spearman rank correlation (monotonic relationships)
- Partial correlation (effect after accounting for other params)
- Sobol second-order indices (nonlinear interactions)

Produces:
- Correlation matrices
- Interaction networks

Example
-------
>>> from happygene.analysis.correlation import CorrelationAnalyzer
>>> import numpy as np
>>> import pandas as pd
>>>
>>> # Create sample batch results
>>> np.random.seed(42)
>>> params = ['p0', 'p1', 'p2', 'p3', 'p4']
>>> X = np.random.rand(100, 5)
>>> y = 0.5*X[:,0] + 0.3*X[:,1] + 0.1*np.random.rand(100)
>>> df = pd.DataFrame(X, columns=params)
>>> df['survival'] = y
>>>
>>> # Analyze correlations
>>> analyzer = CorrelationAnalyzer(params)
>>> corr_matrix = analyzer.compute_correlation_matrix(df)
>>> p0_survival_corr = analyzer.parameter_output_correlation(df, 'survival')
>>>
>>> # First result should be p0 (highest correlation)
>>> print(f"Top parameter: {p0_survival_corr.iloc[0]['param']}")  # doctest: +SKIP
Top parameter: p0

- Partial correlation analysis
"""

from typing import Dict, List

import numpy as np
import pandas as pd


class CorrelationAnalyzer:
    """Parameter correlation and interaction analyzer.

    Computes various correlation metrics between parameters
    and identifies significant interactions.

    Parameters
    ----------
    param_names : list[str]
        Parameter names in order
    """

    def __init__(self, param_names: List[str]):
        """Initialize CorrelationAnalyzer."""
        self.param_names = param_names
        self.n_params = len(param_names)

    def compute_correlation_matrix(
        self, batch_results: pd.DataFrame, method: str = "pearson"
    ) -> pd.DataFrame:
        """Compute correlation matrix between parameters.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Output from BatchSimulator.run_batch().
        method : {'pearson', 'spearman'}
            Correlation method (default: 'pearson').

        Returns
        -------
        pd.DataFrame
            Correlation matrix with param_names as index/columns.
        """
        param_cols = [p for p in self.param_names if p in batch_results.columns]
        X = batch_results[param_cols]

        if method == "pearson":
            corr = X.corr(method="pearson")
        elif method == "spearman":
            corr = X.corr(method="spearman")
        else:
            raise ValueError(f"Unknown method: {method}")

        return corr

    def parameter_output_correlation(
        self,
        batch_results: pd.DataFrame,
        output_col: str = "survival",
        method: str = "pearson",
    ) -> pd.DataFrame:
        """Compute correlation between parameters and output.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Batch simulation results.
        output_col : str
            Name of output column (default: 'survival').
        method : {'pearson', 'spearman'}
            Correlation method (default: 'pearson').

        Returns
        -------
        pd.DataFrame
            Correlation coefficients and p-values for each parameter.
        """
        from scipy.stats import pearsonr, spearmanr

        if output_col not in batch_results.columns:
            raise ValueError(f"Output column '{output_col}' not found")

        correlations = []
        for pname in self.param_names:
            if pname in batch_results.columns:
                if method == "pearson":
                    r, p = pearsonr(batch_results[pname], batch_results[output_col])
                elif method == "spearman":
                    r, p = spearmanr(batch_results[pname], batch_results[output_col])
                else:
                    raise ValueError(f"Unknown method: {method}")

                correlations.append({"param": pname, "correlation": r, "p_value": p})

        df = pd.DataFrame(correlations)
        return df.sort_values("correlation", ascending=False, key=abs)

    def detect_multicollinearity(
        self, batch_results: pd.DataFrame, vif_threshold: float = 5.0
    ) -> Dict[str, float]:
        """Detect parameter multicollinearity (correlation issues).

        Parameters
        ----------
        batch_results : pd.DataFrame
            Batch simulation results.
        vif_threshold : float
            Variance Inflation Factor threshold for concern (default: 5.0).

        Returns
        -------
        dict
            Parameter names and their VIF scores.
        """
        from statsmodels.stats.outliers_influence import variance_inflation_factor

        param_cols = [p for p in self.param_names if p in batch_results.columns]
        X = batch_results[param_cols].values

        vif_data = {}
        for i, pname in enumerate(param_cols):
            try:
                vif = variance_inflation_factor(X, i)
                vif_data[pname] = vif
            except Exception:
                # If VIF computation fails, set to NaN
                vif_data[pname] = np.nan

        return vif_data
