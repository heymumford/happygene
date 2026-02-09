"""Selection models for population fitness evaluation and reproduction."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import numpy as np

from happygene.entities import Individual, Gene

if TYPE_CHECKING:
    from numpy.random import Generator


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


class SexualReproduction:
    """Sexual reproduction model with genetic crossover and mating.

    Implements single-point or uniform crossover between two parent individuals
    to produce offspring with mixed genetic material.

    Parameters
    ----------
    crossover_rate : float, optional
        Probability of crossover at each gene locus (default 0.5).
        - 0.0: offspring is exact copy of parent1
        - 1.0: offspring is exact copy of parent2
        - 0.5: uniform mixing of both parents
    """

    def __init__(self, crossover_rate: float = 0.5):
        """Initialize sexual reproduction model.

        Parameters
        ----------
        crossover_rate : float, optional
            Crossover probability (default 0.5).
        """
        self.crossover_rate: float = float(crossover_rate)

    def mate(
        self,
        parent1: Individual,
        parent2: Individual,
        rng: "Generator",
    ) -> Individual:
        """Produce offspring from two parents via genetic crossover.

        For each gene locus, the offspring inherits the expression level from
        parent1 or parent2 based on crossover_rate.

        Parameters
        ----------
        parent1 : Individual
            First parent.
        parent2 : Individual
            Second parent.
        rng : numpy.random.Generator
            Random number generator for reproducibility.

        Returns
        -------
        Individual
            Offspring individual with mixed genes from both parents.
        """
        if len(parent1.genes) != len(parent2.genes):
            raise ValueError(
                f"Parent gene counts differ: {len(parent1.genes)} vs {len(parent2.genes)}"
            )

        offspring_genes = []
        for gene1, gene2 in zip(parent1.genes, parent2.genes):
            # Decide which parent's allele to inherit
            if rng.random() < self.crossover_rate:
                # Inherit from parent2
                inherited_expr = gene2.expression_level
            else:
                # Inherit from parent1
                inherited_expr = gene1.expression_level

            # Create new gene with inherited expression level
            offspring_genes.append(Gene(gene1.name, inherited_expr))

        return Individual(offspring_genes)

    def __repr__(self) -> str:
        return f"SexualReproduction(crossover_rate={self.crossover_rate})"
