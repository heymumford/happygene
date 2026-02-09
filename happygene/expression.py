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


class HillExpression(ExpressionModel):
    """Hill expression model: sigmoidal response via Hill equation.

    Models gene regulation with cooperative binding using the Hill equation:
    E = v_max * (tf^n) / (k^n + tf^n)

    Parameters
    ----------
    v_max : float
        Maximum expression level. Must be >= 0.
    k : float
        Half-saturation coefficient (tf at 50% response). Must be > 0.
    n : float
        Hill coefficient (cooperativity). Must be > 0.
        n=1: Michaelis-Menten kinetics
        n>1: Positive cooperativity (switch-like)

    Raises
    ------
    ValueError
        If v_max < 0, k <= 0, or n <= 0.
    """

    def __init__(self, v_max: float, k: float, n: float):
        if v_max < 0.0:
            raise ValueError(f"v_max must be >= 0, got {v_max}")
        if k <= 0.0:
            raise ValueError(f"k must be > 0, got {k}")
        if n <= 0.0:
            raise ValueError(f"n must be > 0, got {n}")

        self.v_max: float = v_max
        self.k: float = k
        self.n: float = n

    def compute(self, conditions: Conditions) -> float:
        """Compute Hill equation response.

        E = v_max * (tf^n) / (k^n + tf^n)

        Result is always in range [0, v_max].
        """
        tf = conditions.tf_concentration
        tf_power = tf ** self.n
        k_power = self.k ** self.n
        result = self.v_max * tf_power / (k_power + tf_power)
        return max(0.0, result)

    def __repr__(self) -> str:
        return f"HillExpression(v_max={self.v_max}, k={self.k}, n={self.n})"
