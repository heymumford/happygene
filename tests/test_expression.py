"""Tests for expression models and conditions."""
import pytest
from happygene.conditions import Conditions
from happygene.expression import ExpressionModel, LinearExpression, ConstantExpression


class TestConditions:
    """Tests for Conditions dataclass."""

    def test_conditions_creation_defaults(self):
        """Conditions can be created with default values."""
        cond = Conditions()
        assert cond.tf_concentration == 0.0
        assert cond.temperature == 37.0
        assert cond.nutrients == 1.0
        assert cond.extra == {}

    def test_conditions_creation_with_values(self):
        """Conditions can be created with specific values."""
        cond = Conditions(tf_concentration=2.5, temperature=25.0, nutrients=0.8)
        assert cond.tf_concentration == 2.5
        assert cond.temperature == 25.0
        assert cond.nutrients == 0.8

    def test_conditions_extra_dict(self):
        """Conditions can store arbitrary extra parameters."""
        cond = Conditions(extra={"pH": 7.4, "pressure": 1.0})
        assert cond.extra["pH"] == 7.4
        assert cond.extra["pressure"] == 1.0


class TestExpressionModel:
    """Tests for ExpressionModel ABC."""

    def test_expression_model_cannot_instantiate(self):
        """ExpressionModel is abstract; cannot instantiate directly."""
        with pytest.raises(TypeError):
            ExpressionModel()

    def test_expression_model_subclass_must_implement_compute(self):
        """Subclass must implement compute() method."""
        class BrokenExpression(ExpressionModel):
            pass

        with pytest.raises(TypeError):
            BrokenExpression()


class TestLinearExpression:
    """Tests for LinearExpression model."""

    def test_linear_expression_creation(self):
        """LinearExpression can be created with valid parameters."""
        expr = LinearExpression(slope=2.0, intercept=1.0)
        assert expr.slope == 2.0
        assert expr.intercept == 1.0

    def test_linear_expression_compute_basic(self):
        """LinearExpression computes E = slope * tf + intercept."""
        expr = LinearExpression(slope=2.0, intercept=1.0)
        cond = Conditions(tf_concentration=3.0)
        result = expr.compute(cond)
        # E = 2.0 * 3.0 + 1.0 = 7.0
        assert result == 7.0

    def test_linear_expression_compute_zero_slope(self):
        """LinearExpression with slope=0 gives constant intercept."""
        expr = LinearExpression(slope=0.0, intercept=5.0)
        cond = Conditions(tf_concentration=100.0)
        result = expr.compute(cond)
        assert result == 5.0

    def test_linear_expression_clamped_to_zero(self):
        """LinearExpression result clamped to >= 0."""
        expr = LinearExpression(slope=-2.0, intercept=3.0)
        cond = Conditions(tf_concentration=5.0)
        # E = -2.0 * 5.0 + 3.0 = -7.0 → clamped to 0.0
        result = expr.compute(cond)
        assert result == 0.0

    def test_linear_expression_negative_slope_allowed(self):
        """LinearExpression allows negative slopes (repression)."""
        expr = LinearExpression(slope=-1.0, intercept=5.0)
        cond = Conditions(tf_concentration=2.0)
        # E = -1.0 * 2.0 + 5.0 = 3.0
        result = expr.compute(cond)
        assert result == 3.0

    def test_linear_expression_negative_intercept_rejected(self):
        """LinearExpression rejects negative intercept."""
        with pytest.raises(ValueError):
            LinearExpression(slope=1.0, intercept=-1.0)

    def test_linear_expression_repr(self):
        """LinearExpression has informative repr."""
        expr = LinearExpression(slope=2.0, intercept=1.0)
        repr_str = repr(expr)
        assert "LinearExpression" in repr_str
        assert "2.0" in repr_str
        assert "1.0" in repr_str


class TestConstantExpression:
    """Tests for ConstantExpression model."""

    def test_constant_expression_creation(self):
        """ConstantExpression can be created with valid level."""
        expr = ConstantExpression(level=5.0)
        assert expr.level == 5.0

    def test_constant_expression_compute(self):
        """ConstantExpression always returns fixed level."""
        expr = ConstantExpression(level=3.5)
        cond1 = Conditions(tf_concentration=0.0)
        cond2 = Conditions(tf_concentration=100.0)
        assert expr.compute(cond1) == 3.5
        assert expr.compute(cond2) == 3.5

    def test_constant_expression_zero_level(self):
        """ConstantExpression can have level=0."""
        expr = ConstantExpression(level=0.0)
        cond = Conditions()
        assert expr.compute(cond) == 0.0

    def test_constant_expression_high_level(self):
        """ConstantExpression can have high level."""
        expr = ConstantExpression(level=100.0)
        cond = Conditions()
        assert expr.compute(cond) == 100.0

    def test_constant_expression_negative_level_rejected(self):
        """ConstantExpression rejects negative level."""
        with pytest.raises(ValueError):
            ConstantExpression(level=-1.0)

    def test_constant_expression_repr(self):
        """ConstantExpression has informative repr."""
        expr = ConstantExpression(level=5.0)
        repr_str = repr(expr)
        assert "ConstantExpression" in repr_str
        assert "5.0" in repr_str
