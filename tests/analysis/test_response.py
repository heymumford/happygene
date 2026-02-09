"""Tests for ResponseSurfaceModel: surrogate modeling.

Test Tiers:
1. Contract Tests: fit/predict interface, model types
2. Property Tests: Prediction accuracy, method consistency
3. Chaos Tests: Predict before fit, invalid methods
"""

import numpy as np
import pandas as pd
import pytest

from happygene.analysis.response import ResponseSurfaceModel

sklearn = pytest.importorskip("sklearn")


@pytest.fixture
def response_data():
    """Generate known linear relationship for response surface testing."""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame(
        {
            "x1": np.random.uniform(0, 1, n),
            "x2": np.random.uniform(0, 1, n),
            "x3": np.random.uniform(0, 1, n),
        }
    )
    # Known linear relationship: y = 2*x1 + 3*x2 + 0.5*x3 + noise
    df["output"] = (
        2 * df["x1"] + 3 * df["x2"] + 0.5 * df["x3"] + np.random.normal(0, 0.1, n)
    )
    return df


class TestResponseSurfaceCreation:
    """Contract: ResponseSurfaceModel construction."""

    def test_creation_linear(self):
        model = ResponseSurfaceModel(["x1", "x2"], method="linear")
        assert model.method == "linear"
        assert not model.is_fitted

    def test_creation_quadratic(self):
        model = ResponseSurfaceModel(["x1", "x2"], method="quadratic")
        assert model.method == "quadratic"

    def test_creation_rf(self):
        model = ResponseSurfaceModel(["x1", "x2"], method="rf")
        assert model.method == "rf"


class TestResponseSurfaceFit:
    """Contract: fit() trains the surrogate model."""

    def test_fit_returns_self(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"])
        result = model.fit(response_data, output_col="output")
        assert result is model  # Method chaining

    def test_fit_sets_is_fitted(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"])
        model.fit(response_data, output_col="output")
        assert model.is_fitted is True

    def test_fit_linear(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="linear")
        model.fit(response_data, output_col="output")
        assert model.model is not None

    def test_fit_quadratic(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="quadratic")
        model.fit(response_data, output_col="output")
        assert model.model is not None

    def test_fit_rf(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="rf")
        model.fit(response_data, output_col="output")
        assert model.model is not None

    def test_fit_invalid_method_raises(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="invalid")
        with pytest.raises(ValueError, match="Unknown method"):
            model.fit(response_data, output_col="output")


class TestResponseSurfacePredict:
    """Contract: predict() returns predictions."""

    def test_predict_shape(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"])
        model.fit(response_data, output_col="output")
        X_new = np.array([[0.5, 0.5, 0.5], [0.1, 0.9, 0.3]])
        preds = model.predict(X_new)
        assert preds.shape == (2,)

    def test_predict_before_fit_raises(self):
        model = ResponseSurfaceModel(["x1", "x2"])
        with pytest.raises(RuntimeError, match="not fitted"):
            model.predict(np.array([[0.5, 0.5]]))

    def test_predict_linear_accuracy(self, response_data):
        """Linear model on linear data should have R^2 > 0.9."""
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="linear")
        model.fit(response_data, output_col="output")
        X = response_data[["x1", "x2", "x3"]].values
        preds = model.predict(X)
        y_true = response_data["output"].values
        # R^2 check
        ss_res = np.sum((y_true - preds) ** 2)
        ss_tot = np.sum((y_true - y_true.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot
        assert r2 > 0.9

    def test_predict_quadratic(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="quadratic")
        model.fit(response_data, output_col="output")
        preds = model.predict(response_data[["x1", "x2", "x3"]].values)
        assert len(preds) == len(response_data)

    def test_predict_rf(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="rf")
        model.fit(response_data, output_col="output")
        preds = model.predict(response_data[["x1", "x2", "x3"]].values)
        assert len(preds) == len(response_data)

    def test_predict_invalid_method_raises(self, response_data):
        """Predict with invalid method after manually setting it."""
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="linear")
        model.fit(response_data, output_col="output")
        model.method = "invalid"
        with pytest.raises(ValueError, match="Unknown method"):
            model.predict(response_data[["x1", "x2", "x3"]].values)


class TestResponseSurfaceCrossValidate:
    """Contract: cross_validate() returns metrics dict."""

    def test_cross_validate_returns_metrics(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"])
        metrics = model.cross_validate(response_data, output_col="output")
        assert "r2" in metrics
        assert "rmse" in metrics
        assert "mae" in metrics

    def test_cross_validate_r2_positive_for_good_data(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"], method="linear")
        metrics = model.cross_validate(response_data, output_col="output")
        assert metrics["r2"] > 0.5

    def test_cross_validate_rmse_non_negative(self, response_data):
        model = ResponseSurfaceModel(["x1", "x2", "x3"])
        metrics = model.cross_validate(response_data, output_col="output")
        assert metrics["rmse"] >= 0
        assert metrics["mae"] >= 0


class TestPolynomialFeatures:
    """Contract: _add_polynomial_features() expands feature matrix."""

    def test_quadratic_expansion_shape(self):
        model = ResponseSurfaceModel(["x1", "x2"])
        X = np.array([[1.0, 2.0], [3.0, 4.0]])
        # For 2 features, degree=2: x1, x2, x1^2, x1*x2, x2^2 = 5 features
        X_poly = model._add_polynomial_features(X, degree=2)
        assert X_poly.shape[0] == 2
        assert X_poly.shape[1] == 5  # 2 + 1 + 2 = 5 (no bias)
