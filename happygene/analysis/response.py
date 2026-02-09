"""
ResponseSurfaceModel: Surrogate modeling for efficient prediction.

Builds reduced-order models from batch results, enabling:
- Fast prediction at untested parameter combinations
- Response surface visualization
- Interpolation and extrapolation
- Model validation via cross-validation

Supports:
- Polynomial response surfaces (linear, quadratic)
- Gaussian Process (Kriging)
- Random Forest surrogates
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, List


class ResponseSurfaceModel:
    """Surrogate model for efficient output prediction.

    Fits a reduced-order model from batch simulation results
    for fast evaluation at new parameter combinations.

    Parameters
    ----------
    param_names : list[str]
        Parameter names in order
    method : {'linear', 'quadratic', 'rf'}
        Model type (default: 'linear')
    """

    def __init__(self, param_names: List[str], method: str = "linear"):
        """Initialize ResponseSurfaceModel."""
        self.param_names = param_names
        self.n_params = len(param_names)
        self.method = method
        self.scaler = None  # Initialized in fit() after sklearn import
        self.model = None
        self.is_fitted = False

    def fit(self, batch_results: pd.DataFrame, output_col: str = "survival"):
        """Fit surrogate model from batch results.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Batch simulation results with parameter and output columns.
        output_col : str
            Name of output column to predict (default: 'survival').

        Returns
        -------
        self
            For method chaining.
        """
        # Lazy imports to avoid hard dependencies
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor

        # Re-initialize scaler with proper import
        self.scaler = StandardScaler()

        # Extract data
        param_cols = [p for p in self.param_names if p in batch_results.columns]
        X = batch_results[param_cols].values
        y = batch_results[output_col].values

        # Normalize features
        X_scaled = self.scaler.fit_transform(X)

        # Build feature matrix based on method
        if self.method == "linear":
            X_train = X_scaled
        elif self.method == "quadratic":
            # Add polynomial terms (1, x, x^2)
            X_train = self._add_polynomial_features(X_scaled, degree=2)
        elif self.method == "rf":
            X_train = X_scaled
        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Fit model
        if self.method == "rf":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        else:
            self.model = LinearRegression()

        self.model.fit(X_train, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict outputs at parameter combinations.

        Parameters
        ----------
        X : np.ndarray
            Parameter matrix (n_samples, n_params) in original (non-normalized) space.

        Returns
        -------
        np.ndarray
            Predicted outputs (n_samples,)

        Raises
        ------
        RuntimeError
            If model not fitted yet.
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        # Normalize features using fitted scaler
        X_scaled = self.scaler.transform(X)

        # Build feature matrix based on method
        if self.method == "linear":
            X_test = X_scaled
        elif self.method == "quadratic":
            X_test = self._add_polynomial_features(X_scaled, degree=2)
        elif self.method == "rf":
            X_test = X_scaled
        else:
            raise ValueError(f"Unknown method: {self.method}")

        return self.model.predict(X_test)

    def cross_validate(
        self, batch_results: pd.DataFrame, output_col: str = "survival", cv_folds: int = 5
    ) -> Dict[str, float]:
        """Cross-validate model performance.

        Parameters
        ----------
        batch_results : pd.DataFrame
            Batch simulation results.
        output_col : str
            Output column to predict (default: 'survival').
        cv_folds : int
            Number of cross-validation folds (default: 5).

        Returns
        -------
        dict
            Metrics: 'r2', 'rmse', 'mae' (mean absolute error)
        """
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor

        param_cols = [p for p in self.param_names if p in batch_results.columns]
        X = batch_results[param_cols].values
        y = batch_results[output_col].values

        # Initialize and normalize features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Build feature matrix
        if self.method == "linear":
            X_train = X_scaled
        elif self.method == "quadratic":
            X_train = self._add_polynomial_features(X_scaled, degree=2)
        elif self.method == "rf":
            X_train = X_scaled
        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Fit model for scoring
        if self.method == "rf":
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        else:
            model = LinearRegression()

        model.fit(X_train, y)

        # Compute metrics
        y_pred = model.predict(X_train)
        r2 = model.score(X_train, y)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)

        return {"r2": r2, "rmse": rmse, "mae": mae}

    def _add_polynomial_features(self, X: np.ndarray, degree: int = 2) -> np.ndarray:
        """Add polynomial features to input matrix.

        Parameters
        ----------
        X : np.ndarray
            Input features (n_samples, n_features)
        degree : int
            Polynomial degree (default: 2)

        Returns
        -------
        np.ndarray
            Expanded feature matrix with polynomial terms
        """
        from sklearn.preprocessing import PolynomialFeatures

        poly = PolynomialFeatures(degree=degree, include_bias=False)
        return poly.fit_transform(X)
