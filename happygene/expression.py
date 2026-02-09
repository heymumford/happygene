"""Expression models for gene regulation."""
from abc import ABC, abstractmethod
from happygene.conditions import Conditions


class ExpressionModel(ABC):
    """Abstract base class for gene expression models.

    Expression models compute gene expression level given environmental
    conditions. Subclasses implement specific regulatory logic (linear,
    Hill, constant, etc.).
    """

    @abstractmethod
    def compute(self, conditions: Conditions) -> float:
        """Compute expression level given conditions.

        Parameters
        ----------
        conditions : Conditions
            Environmental conditions.

        Returns
        -------
        float
            Expression level (always >= 0).
        """
        ...


class LinearExpression(ExpressionModel):
    """Linear expression model: E = slope * tf_concentration + intercept.

    Parameters
    ----------
    slope : float
        Sensitivity coefficient (can be negative for repression).
    intercept : float
        Basal expression level. Must be >= 0.

    Raises
    ------
    ValueError
        If intercept < 0.
    """

    def __init__(self, slope: float, intercept: float):
        if intercept < 0.0:
            raise ValueError(f"intercept must be >= 0, got {intercept}")
        self.slope: float = slope
        self.intercept: float = intercept

    def compute(self, conditions: Conditions) -> float:
        """Compute linear expression: E = slope * tf_concentration + intercept.

        Result is clamped to [0, inf).
        """
        result = self.slope * conditions.tf_concentration + self.intercept
        return max(0.0, result)

    def __repr__(self) -> str:
        return f"LinearExpression(slope={self.slope}, intercept={self.intercept})"


class ConstantExpression(ExpressionModel):
    """Constant expression model: always returns fixed level.

    Parameters
    ----------
    level : float
        Fixed expression level. Must be >= 0.

    Raises
    ------
    ValueError
        If level < 0.
    """

    def __init__(self, level: float):
        if level < 0.0:
            raise ValueError(f"level must be >= 0, got {level}")
        self.level: float = level

    def compute(self, conditions: Conditions) -> float:
        """Return fixed expression level regardless of conditions."""
        return self.level

    def __repr__(self) -> str:
        return f"ConstantExpression(level={self.level})"
