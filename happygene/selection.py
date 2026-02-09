"""Selection models for population fitness evaluation."""
from abc import ABC, abstractmethod
from happygene.entities import Individual


class SelectionModel(ABC):
    """Abstract base class for selection models.

    Selection models compute fitness of individuals based on their gene
    expression patterns. Subclasses implement specific fitness functions.
    """

    @abstractmethod
    def compute_fitness(self, individual: Individual) -> float:
        """Compute fitness for an individual.

        Parameters
        ----------
        individual : Individual
            The individual to evaluate.

        Returns
        -------
        float
            Fitness value (typically in [0, 1] but model-dependent).
        """
        ...


class ProportionalSelection(SelectionModel):
    """Proportional selection: fitness = mean gene expression.

    Simple selector where fitness is directly proportional to the mean
    expression level across all genes in an individual.
    """

    def compute_fitness(self, individual: Individual) -> float:
        """Compute fitness as mean expression level.

        Parameters
        ----------
        individual : Individual
            The individual to evaluate.

        Returns
        -------
        float
            Mean expression level across all genes.
        """
        return individual.mean_expression()

    def __repr__(self) -> str:
        return "ProportionalSelection()"


class ThresholdSelection(SelectionModel):
    """Threshold selection: binary fitness based on expression threshold.

    Returns fitness=1.0 if mean expression >= threshold, else 0.0.

    Parameters
    ----------
    threshold : float
        Expression threshold for selection. Individuals with mean
        expression >= threshold get fitness 1.0, else 0.0.
    """

    def __init__(self, threshold: float):
        self.threshold: float = threshold

    def compute_fitness(self, individual: Individual) -> float:
        """Compute fitness as binary threshold function.

        Parameters
        ----------
        individual : Individual
            The individual to evaluate.

        Returns
        -------
        float
            1.0 if mean_expression >= threshold, else 0.0.
        """
        mean_expr = individual.mean_expression()
        return 1.0 if mean_expr >= self.threshold else 0.0

    def __repr__(self) -> str:
        return f"ThresholdSelection(threshold={self.threshold})"
