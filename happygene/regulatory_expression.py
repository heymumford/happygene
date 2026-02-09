"""RegulatoryExpressionModel: regulatory overlay on base expression (ADR-005).

This module implements the composition pattern for regulatory modulation:
- RegulatoryExpressionModel: Abstract base for regulatory layers
- AdditiveRegulation: Additive effect (expr = base + weight*tf)
- MultiplicativeRegulation: Multiplicative effect (expr = base*(1+weight*tf))
- CompositeExpressionModel: Wraps base model + regulatory layer

Design rationale (ADR-005):
- Separation of concerns: Base expression (what) vs regulatory modulation (how much)
- Composable: Can nest CompositeExpressionModel with arbitrary base models
- Inspectable: Both base_model and regulatory_model are accessible
- Immutable: Both models are stored as properties (no post-init modification)
"""
from abc import ABC, abstractmethod
from happygene.expression import ExpressionModel
from happygene.conditions import Conditions


class RegulatoryExpressionModel(ABC):
    """Abstract base class for regulatory layers that modulate expression.

    Regulatory models take a base expression level and modulate it based on
    transcription factor inputs. Subclasses implement specific regulatory
    logic (additive, multiplicative, etc.).

    Parameters
    ----------
    weight : float
        Regulatory strength. Sign and magnitude determine effect direction
        (positive = activation, negative = repression).
    """

    def __init__(self, weight: float):
        """Initialize regulatory model.

        Parameters
        ----------
        weight : float
            Regulatory weight (can be positive or negative).
        """
        self.weight: float = weight

    @abstractmethod
    def compute(self, base_expression: float, tf_inputs: float) -> float:
        """Compute regulated expression level.

        Parameters
        ----------
        base_expression : float
            Expression level from base model (>= 0).
        tf_inputs : float
            Transcription factor input level (can be negative).

        Returns
        -------
        float
            Regulated expression level (always >= 0, clamped).
        """
        ...


class AdditiveRegulation(RegulatoryExpressionModel):
    """Additive regulatory model: expr = base + weight*tf_inputs.

    Adds a linear correction term to base expression. Useful for modeling
    transcriptional cofactors with independent effect.

    Parameters
    ----------
    weight : float
        Additive strength. Positive = activation, negative = repression.

    Examples
    --------
    >>> reg = AdditiveRegulation(weight=2.0)
    >>> reg.compute(base_expression=5.0, tf_inputs=3.0)
    11.0  # 5.0 + 2.0*3.0

    >>> reg = AdditiveRegulation(weight=-1.0)
    >>> reg.compute(base_expression=1.0, tf_inputs=5.0)
    0.0  # max(1.0 + (-1.0)*5.0, 0) = max(-4, 0) = 0
    """

    def compute(self, base_expression: float, tf_inputs: float) -> float:
        """Compute additive regulatory effect.

        Result is clamped to [0, inf).

        Parameters
        ----------
        base_expression : float
            Base expression level.
        tf_inputs : float
            TF input level.

        Returns
        -------
        float
            base_expression + weight*tf_inputs, clamped >= 0.
        """
        result = base_expression + self.weight * tf_inputs
        return max(0.0, result)

    def __repr__(self) -> str:
        return f"AdditiveRegulation(weight={self.weight})"


class MultiplicativeRegulation(RegulatoryExpressionModel):
    """Multiplicative regulatory model: expr = base*(1+weight*tf_inputs).

    Multiplies base expression by (1 + weight*tf). Useful for modeling
    transcriptional enhancers with proportional effect.

    Parameters
    ----------
    weight : float
        Multiplicative strength. Positive = activation, negative = repression.

    Examples
    --------
    >>> reg = MultiplicativeRegulation(weight=0.5)
    >>> reg.compute(base_expression=10.0, tf_inputs=2.0)
    20.0  # 10.0 * (1 + 0.5*2.0) = 10.0 * 2.0

    >>> reg = MultiplicativeRegulation(weight=-1.0)
    >>> reg.compute(base_expression=10.0, tf_inputs=1.0)
    0.0  # max(10.0 * (1 + (-1.0)*1.0), 0) = max(0, 0) = 0
    """

    def compute(self, base_expression: float, tf_inputs: float) -> float:
        """Compute multiplicative regulatory effect.

        Result is clamped to [0, inf).

        Parameters
        ----------
        base_expression : float
            Base expression level.
        tf_inputs : float
            TF input level.

        Returns
        -------
        float
            base_expression * (1 + weight*tf_inputs), clamped >= 0.
        """
        multiplier = 1.0 + self.weight * tf_inputs
        result = base_expression * multiplier
        return max(0.0, result)

    def __repr__(self) -> str:
        return f"MultiplicativeRegulation(weight={self.weight})"


class CompositeExpressionModel(ExpressionModel):
    """Wraps base expression model + regulatory layer (ADR-005).

    Implements composition pattern: base_model computes expression,
    regulatory_model modulates it based on TF inputs.

    Design:
    - Inherits from ExpressionModel (compatible with existing code)
    - Both base_model and regulatory_model are inspectable properties
    - Arbitrary nesting: CompositeExpressionModel(Hill(Linear(...)), Additive(...))
    - Immutable: Models stored as properties, not modified post-init

    Parameters
    ----------
    base_model : ExpressionModel
        Base expression model (Linear, Hill, Constant, or another Composite).
    regulatory_model : RegulatoryExpressionModel
        Regulatory layer (Additive, Multiplicative, or custom).

    Examples
    --------
    >>> base = LinearExpression(slope=2.0, intercept=3.0)
    >>> reg = AdditiveRegulation(weight=1.0)
    >>> composite = CompositeExpressionModel(base, reg)
    >>> conditions = Conditions(tf_concentration=2.0)
    >>> composite.compute(conditions, tf_inputs=2.0)
    9.0  # base=7.0, regulated=7.0+1.0*2.0=9.0

    >>> # Nesting works
    >>> inner = CompositeExpressionModel(base, reg)
    >>> outer = CompositeExpressionModel(inner, MultiplicativeRegulation(weight=0.5))
    >>> outer.compute(conditions, tf_inputs=1.0)
    """

    def __init__(
        self, base_model: ExpressionModel, regulatory_model: RegulatoryExpressionModel
    ):
        """Initialize composite expression model.

        Parameters
        ----------
        base_model : ExpressionModel
            Base expression model.
        regulatory_model : RegulatoryExpressionModel
            Regulatory layer.
        """
        self._base_model = base_model
        self._regulatory_model = regulatory_model

    @property
    def base_model(self) -> ExpressionModel:
        """Read-only access to base model."""
        return self._base_model

    @property
    def regulatory_model(self) -> RegulatoryExpressionModel:
        """Read-only access to regulatory model."""
        return self._regulatory_model

    def compute(self, conditions: Conditions, tf_inputs: float = 0.0) -> float:
        """Compute expression with regulatory overlay.

        Pipeline:
        1. Compute base expression: base_expr = base_model.compute(conditions)
        2. Apply regulatory modulation: result = regulatory_model.compute(base_expr, tf_inputs)

        Parameters
        ----------
        conditions : Conditions
            Environmental conditions for base model.
        tf_inputs : float, optional
            TF input level for regulatory layer (default: 0.0).

        Returns
        -------
        float
            Regulated expression level (>= 0).
        """
        base_expr = self._base_model.compute(conditions)
        return self._regulatory_model.compute(base_expr, tf_inputs)

    def __repr__(self) -> str:
        return (
            f"CompositeExpressionModel("
            f"base_model={self._base_model!r}, "
            f"regulatory_model={self._regulatory_model!r})"
        )
