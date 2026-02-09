"""Tests for RegulatoryExpressionModel and CompositeExpressionModel (ADR-005)."""
import pytest
from happygene.conditions import Conditions
from happygene.expression import LinearExpression, HillExpression, ConstantExpression
from happygene.regulatory_expression import (
    RegulatoryExpressionModel,
    AdditiveRegulation,
    MultiplicativeRegulation,
    CompositeExpressionModel,
)


class TestAdditiveRegulation:
    """Test AdditiveRegulation: expr = base + weight*tf_inputs."""

    def test_additive_regulation_no_tf(self):
        """Zero TF input returns base expression unchanged."""
        reg = AdditiveRegulation(weight=2.0)
        base_expr = 5.0
        result = reg.compute(base_expr, tf_inputs=0.0)
        assert result == pytest.approx(5.0)

    def test_additive_regulation_with_positive_tf(self):
        """Positive TF input adds weight*tf_inputs to base."""
        reg = AdditiveRegulation(weight=2.0)
        base_expr = 5.0
        result = reg.compute(base_expr, tf_inputs=3.0)
        # 5.0 + 2.0*3.0 = 11.0
        assert result == pytest.approx(11.0)

    def test_additive_regulation_clamps_negative(self):
        """Result clamped to >= 0."""
        reg = AdditiveRegulation(weight=-2.0)
        base_expr = 1.0
        result = reg.compute(base_expr, tf_inputs=5.0)
        # 1.0 + (-2.0)*5.0 = -9.0 → 0.0
        assert result == pytest.approx(0.0)

    def test_additive_regulation_with_negative_weight(self):
        """Negative weight implements repression."""
        reg = AdditiveRegulation(weight=-1.5)
        base_expr = 10.0
        result = reg.compute(base_expr, tf_inputs=2.0)
        # 10.0 + (-1.5)*2.0 = 7.0
        assert result == pytest.approx(7.0)

    def test_additive_regulation_zero_base(self):
        """Works with zero base expression."""
        reg = AdditiveRegulation(weight=3.0)
        base_expr = 0.0
        result = reg.compute(base_expr, tf_inputs=2.0)
        # 0.0 + 3.0*2.0 = 6.0
        assert result == pytest.approx(6.0)

    def test_additive_regulation_large_values(self):
        """Works with large expression levels."""
        reg = AdditiveRegulation(weight=1.5)
        base_expr = 1000.0
        result = reg.compute(base_expr, tf_inputs=100.0)
        # 1000.0 + 1.5*100.0 = 1150.0
        assert result == pytest.approx(1150.0)


class TestMultiplicativeRegulation:
    """Test MultiplicativeRegulation: expr = base*(1+weight*tf_inputs)."""

    def test_multiplicative_regulation_no_tf(self):
        """Zero TF input returns base unchanged."""
        reg = MultiplicativeRegulation(weight=0.5)
        base_expr = 10.0
        result = reg.compute(base_expr, tf_inputs=0.0)
        # 10.0 * (1 + 0.5*0.0) = 10.0
        assert result == pytest.approx(10.0)

    def test_multiplicative_regulation_amplification(self):
        """Positive TF with positive weight amplifies base."""
        reg = MultiplicativeRegulation(weight=0.5)
        base_expr = 10.0
        result = reg.compute(base_expr, tf_inputs=2.0)
        # 10.0 * (1 + 0.5*2.0) = 10.0 * 2.0 = 20.0
        assert result == pytest.approx(20.0)

    def test_multiplicative_regulation_repression(self):
        """Negative weight or TF implements inhibition."""
        reg = MultiplicativeRegulation(weight=-0.5)
        base_expr = 10.0
        result = reg.compute(base_expr, tf_inputs=1.0)
        # 10.0 * (1 + (-0.5)*1.0) = 10.0 * 0.5 = 5.0
        assert result == pytest.approx(5.0)

    def test_multiplicative_regulation_clamps_negative(self):
        """Result clamped to >= 0."""
        reg = MultiplicativeRegulation(weight=-2.0)
        base_expr = 10.0
        result = reg.compute(base_expr, tf_inputs=1.0)
        # 10.0 * (1 + (-2.0)*1.0) = 10.0 * (-1.0) = -10.0 → 0.0
        assert result == pytest.approx(0.0)

    def test_multiplicative_regulation_complete_inhibition(self):
        """Complete inhibition when (1 + weight*tf) == 0."""
        reg = MultiplicativeRegulation(weight=-1.0)
        base_expr = 8.0
        result = reg.compute(base_expr, tf_inputs=1.0)
        # 8.0 * (1 + (-1.0)*1.0) = 8.0 * 0.0 = 0.0
        assert result == pytest.approx(0.0)

    def test_multiplicative_regulation_zero_base(self):
        """With zero base, result is always zero."""
        reg = MultiplicativeRegulation(weight=5.0)
        base_expr = 0.0
        result = reg.compute(base_expr, tf_inputs=10.0)
        # 0.0 * anything = 0.0
        assert result == pytest.approx(0.0)


class TestCompositeExpressionModel:
    """Test CompositeExpressionModel: wraps base model + regulatory layer."""

    def test_composite_expression_linear_base_additive_reg(self):
        """CompositeExpressionModel with Linear base and Additive regulation."""
        base_model = LinearExpression(slope=2.0, intercept=3.0)
        reg_model = AdditiveRegulation(weight=1.0)
        composite = CompositeExpressionModel(base_model, reg_model)

        conditions = Conditions(tf_concentration=2.0)
        # base = 2.0*2.0 + 3.0 = 7.0
        # result = 7.0 + 1.0*2.0 = 9.0
        result = composite.compute(conditions, tf_inputs=2.0)
        assert result == pytest.approx(9.0)

    def test_composite_expression_compute_no_regulatory_input(self):
        """CompositeExpressionModel with zero TF inputs."""
        base_model = LinearExpression(slope=1.0, intercept=5.0)
        reg_model = AdditiveRegulation(weight=2.0)
        composite = CompositeExpressionModel(base_model, reg_model)

        conditions = Conditions(tf_concentration=3.0)
        # base = 1.0*3.0 + 5.0 = 8.0
        # result = 8.0 + 2.0*0.0 = 8.0
        result = composite.compute(conditions, tf_inputs=0.0)
        assert result == pytest.approx(8.0)

    def test_composite_expression_model_properties_inspectable(self):
        """base_model and regulatory_model properties are accessible."""
        base_model = LinearExpression(slope=2.0, intercept=1.0)
        reg_model = AdditiveRegulation(weight=0.5)
        composite = CompositeExpressionModel(base_model, reg_model)

        assert composite.base_model is base_model
        assert composite.regulatory_model is reg_model

    def test_composite_expression_nested(self):
        """CompositeExpressionModel can wrap another CompositeExpressionModel."""
        # Inner composite: Linear + Additive
        base_linear = LinearExpression(slope=1.0, intercept=2.0)
        inner_reg = AdditiveRegulation(weight=0.5)
        inner_composite = CompositeExpressionModel(base_linear, inner_reg)

        # Outer composite: CompositeExpressionModel + Multiplicative
        outer_reg = MultiplicativeRegulation(weight=0.2)
        outer_composite = CompositeExpressionModel(inner_composite, outer_reg)

        conditions = Conditions(tf_concentration=1.0)
        # Inner base = 1.0*1.0 + 2.0 = 3.0
        # Inner result = 3.0 + 0.5*0.0 = 3.0 (inner regulatory layer gets no tf_inputs)
        # Outer result = 3.0 * (1 + 0.2*2.0) = 3.0 * 1.4 = 4.2
        result = outer_composite.compute(conditions, tf_inputs=2.0)
        assert result == pytest.approx(4.2)

    def test_composite_expression_hill_base_multiplicative_reg(self):
        """CompositeExpressionModel with Hill base and Multiplicative regulation."""
        base_model = HillExpression(v_max=100.0, k=1.0, n=2.0)
        reg_model = MultiplicativeRegulation(weight=0.5)
        composite = CompositeExpressionModel(base_model, reg_model)

        conditions = Conditions(tf_concentration=1.0)
        # Hill: 100.0 * 1^2 / (1^2 + 1^2) = 100.0 * 1 / 2 = 50.0
        # result = 50.0 * (1 + 0.5*1.5) = 50.0 * 1.75 = 87.5
        result = composite.compute(conditions, tf_inputs=1.5)
        assert result == pytest.approx(87.5)

    def test_composite_expression_constant_base_additive_reg(self):
        """CompositeExpressionModel with Constant base."""
        base_model = ConstantExpression(level=4.0)
        reg_model = AdditiveRegulation(weight=2.0)
        composite = CompositeExpressionModel(base_model, reg_model)

        conditions = Conditions()
        # base = 4.0 (constant)
        # result = 4.0 + 2.0*3.0 = 10.0
        result = composite.compute(conditions, tf_inputs=3.0)
        assert result == pytest.approx(10.0)

    def test_composite_expression_repr(self):
        """CompositeExpressionModel has readable repr."""
        base_model = LinearExpression(slope=1.0, intercept=0.0)
        reg_model = AdditiveRegulation(weight=1.0)
        composite = CompositeExpressionModel(base_model, reg_model)

        repr_str = repr(composite)
        assert "CompositeExpressionModel" in repr_str
        assert "LinearExpression" in repr_str
        assert "AdditiveRegulation" in repr_str

    def test_composite_expression_negative_regulation_clamping(self):
        """CompositeExpressionModel clamps to >= 0 through regulatory layer."""
        base_model = LinearExpression(slope=1.0, intercept=2.0)
        reg_model = AdditiveRegulation(weight=-1.0)
        composite = CompositeExpressionModel(base_model, reg_model)

        conditions = Conditions(tf_concentration=1.0)
        # base = 1.0*1.0 + 2.0 = 3.0
        # regulatory input = 5.0
        # result = 3.0 + (-1.0)*5.0 = -2.0 → 0.0
        result = composite.compute(conditions, tf_inputs=5.0)
        assert result == pytest.approx(0.0)

    def test_composite_expression_high_amplification(self):
        """CompositeExpressionModel with high amplification factors."""
        base_model = LinearExpression(slope=2.0, intercept=5.0)
        reg_model = MultiplicativeRegulation(weight=2.0)
        composite = CompositeExpressionModel(base_model, reg_model)

        conditions = Conditions(tf_concentration=3.0)
        # base = 2.0*3.0 + 5.0 = 11.0
        # result = 11.0 * (1 + 2.0*4.0) = 11.0 * 9.0 = 99.0
        result = composite.compute(conditions, tf_inputs=4.0)
        assert result == pytest.approx(99.0)
