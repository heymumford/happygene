"""Mutation models for genetic variation introduction."""

from abc import ABC, abstractmethod
from happygene.entities import Individual
import numpy as np


class MutationModel(ABC):
    """Abstract base class for mutation models.

    Mutation models introduce genetic variation into individuals by
    modifying gene expression levels. Subclasses implement specific
    mutation mechanisms.
    """

    @abstractmethod
    def mutate(self, individual: Individual, rng: np.random.Generator) -> None:
        """Apply mutations to an individual.

        Parameters
        ----------
        individual : Individual
            The individual to mutate (modified in-place).
        rng : np.random.Generator
            Random number generator for stochastic mutations.
        """
        ...


class PointMutation(MutationModel):
    """Point mutation: random Gaussian perturbations to gene expression.

    Each gene has a probability (rate) of being mutated. When a gene
    mutates, its expression level is modified by a random Gaussian
    perturbation with standard deviation = magnitude.

    Parameters
    ----------
    rate : float
        Mutation rate per gene. Must be in [0, 1].
    magnitude : float
        Standard deviation of Gaussian perturbation. Must be >= 0.

    Raises
    ------
    ValueError
        If rate not in [0, 1] or magnitude < 0.
    """

    def __init__(self, rate: float, magnitude: float):
        if rate < 0.0 or rate > 1.0:
            raise ValueError(f"rate must be in [0, 1], got {rate}")
        if magnitude < 0.0:
            raise ValueError(f"magnitude must be >= 0, got {magnitude}")

        self.rate: float = rate
        self.magnitude: float = magnitude

    def mutate(self, individual: Individual, rng: np.random.Generator) -> None:
        """Apply point mutations to individual's genes.

        For each gene:
        - With probability rate: apply Gaussian perturbation with std=magnitude
        - Result clamped to [0, inf)

        Parameters
        ----------
        individual : Individual
            Individual to mutate (modified in-place).
        rng : np.random.Generator
            Random number generator.
        """
        for gene in individual.genes:
            # Mutate with probability rate
            if rng.random() < self.rate:
                # Add Gaussian noise
                perturbation = rng.normal(0.0, self.magnitude)
                new_level = gene._expression_level + perturbation
                # Clamp to [0, inf)
                gene._expression_level = max(0.0, new_level)

    def __repr__(self) -> str:
        return f"PointMutation(rate={self.rate}, magnitude={self.magnitude})"
