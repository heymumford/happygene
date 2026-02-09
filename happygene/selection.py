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


class AsexualReproduction:
    """Asexual reproduction model with cloning.

    Produces genetically identical offspring via cloning (no genetic recombination).
    Useful for studying neutral evolution and drift without selection.
    """

    def clone(self, parent: Individual) -> Individual:
        """Produce offspring via cloning (exact genetic copy).

        Creates a new Individual with genes that are exact copies of the parent.
        Expression levels preserved. Gene objects are new instances, not references.

        Parameters
        ----------
        parent : Individual
            Parent individual to clone.

        Returns
        -------
        Individual
            Offspring individual (genetically identical to parent).
        """
        # Create new gene objects with same names and expression levels
        offspring_genes = [
            Gene(gene.name, gene.expression_level) for gene in parent.genes
        ]
        return Individual(offspring_genes)

    def __repr__(self) -> str:
        return "AsexualReproduction()"


class EpistaticFitness(SelectionModel):
    """Epistatic fitness model: fitness depends on gene-gene interactions.

    Models fitness as: base_fitness + epistatic_bonus
    where:
    - base_fitness = mean gene expression
    - epistatic_bonus = sum of pairwise gene interaction terms

    The interaction matrix defines how expression of gene i modulates
    fitness effects of gene j. Symmetric interactions model synergy.

    Parameters
    ----------
    interaction_matrix : np.ndarray
        Square matrix of shape (n_genes, n_genes).
        interaction_matrix[i,j] = interaction strength between genes i and j.
        Can be positive (synergy), negative (antagonism), or zero (independence).

    Example
    -------
    >>> interactions = np.array([
    ...     [0.1, 0.3],  # g0 auto-interaction 0.1, g0-g1 synergy 0.3
    ...     [0.3, 0.1],  # g1-g0 synergy 0.3, g1 auto-interaction 0.1
    ... ])
    >>> selector = EpistaticFitness(interaction_matrix=interactions)
    >>> individual = Individual([Gene("g0", 1.0), Gene("g1", 0.8)])
    >>> fitness = selector.compute_fitness(individual)
    """

    def __init__(self, interaction_matrix: np.ndarray):
        """Initialize epistatic fitness model.

        Parameters
        ----------
        interaction_matrix : np.ndarray
            Square matrix of interaction strengths.

        Raises
        ------
        ValueError
            If matrix is not square.
        """
        interaction_matrix = np.asarray(interaction_matrix, dtype=float)

        if interaction_matrix.ndim != 2:
            raise ValueError(f"interaction_matrix must be 2D, got {interaction_matrix.ndim}D")

        n_rows, n_cols = interaction_matrix.shape
        if n_rows != n_cols:
            raise ValueError(
                f"interaction_matrix must be square, got {n_rows}x{n_cols}"
            )

        self.interaction_matrix = interaction_matrix.copy()
        self._n_genes = n_rows

    def compute_fitness(self, individual: Individual) -> float:
        """Compute fitness with epistatic interactions.

        Fitness = base + epistatic_bonus
        base = mean expression across genes
        epistatic_bonus = sum of pairwise interaction terms weighted by expression

        Parameters
        ----------
        individual : Individual
            Individual to evaluate.

        Returns
        -------
        float
            Fitness value (can exceed 1.0 if interactions are strongly positive).

        Raises
        ------
        ValueError
            If individual gene count doesn't match interaction matrix size.
        """
        expr_vector = np.array([gene.expression_level for gene in individual.genes])

        if len(expr_vector) != self._n_genes:
            raise ValueError(
                f"Individual has {len(expr_vector)} genes, "
                f"but interaction_matrix size is {self._n_genes}x{self._n_genes}"
            )

        # Base fitness: mean expression
        base_fitness = np.mean(expr_vector)

        # Epistatic bonus: weighted sum of interaction terms
        # For each pair (i, j), contribution = expr[i] * expr[j] * interaction[i,j]
        # This captures how expression of one gene affects fitness through interaction
        epistatic_bonus = np.sum(expr_vector[:, np.newaxis] * expr_vector[np.newaxis, :]
                                 * self.interaction_matrix)

        # Normalize epistatic bonus by number of genes (scale down as n_genes increases)
        if self._n_genes > 1:
            epistatic_bonus /= self._n_genes

        return base_fitness + epistatic_bonus

    def __repr__(self) -> str:
        return f"EpistaticFitness({self._n_genes}x{self._n_genes})"


class MultiObjectiveSelection(SelectionModel):
    """Multi-objective selection based on weighted aggregate fitness.

    Computes fitness as a weighted aggregate of individual gene expression levels,
    effectively implementing a multi-objective fitness function where each gene
    is an objective to maximize.

    For populations with conflicting objectives (e.g., maximize g0 and g1 which
    may trade off), this model ranks individuals by weighted objectives, with
    lower-ranked (dominated) individuals receiving proportionally lower fitness.

    Parameters
    ----------
    objective_weights : list of float
        Weights for each objective (one per gene). Non-negative values.
        Weights are normalized: fitness = sum(expr_i * weight_i) / sum(weight_i)

    Example
    -------
    >>> # Three objectives: maximize all equally
    >>> weights = [1.0, 1.0, 1.0]
    >>> selector = MultiObjectiveSelection(objective_weights=weights)
    >>> individual = Individual([Gene("g0", 0.5), Gene("g1", 0.3), Gene("g2", 0.8)])
    >>> fitness = selector.compute_fitness(individual)  # (0.5+0.3+0.8)/3 = 0.533
    """

    def __init__(self, objective_weights: list):
        """Initialize multi-objective selection model.

        Parameters
        ----------
        objective_weights : list of float
            Non-negative weights for each objective.

        Raises
        ------
        ValueError
            If any weight is negative.
        """
        weights = np.asarray(objective_weights, dtype=float)

        if np.any(weights < 0):
            raise ValueError(
                f"All weights must be non-negative, got {objective_weights}"
            )

        self.objective_weights = weights.copy()
        self._sum_weights = np.sum(weights)
        self._n_objectives = len(weights)

    def compute_fitness(self, individual: Individual) -> float:
        """Compute fitness as weighted aggregate of objectives.

        Fitness = sum(weight_i * objective_i) / sum(weights)
        where objective_i = expression level of gene i.

        Parameters
        ----------
        individual : Individual
            Individual to evaluate.

        Returns
        -------
        float
            Weighted aggregate fitness (typically in [0, 1] if expressions are).

        Raises
        ------
        ValueError
            If individual gene count doesn't match number of objectives.
        """
        expr_vector = np.array([gene.expression_level for gene in individual.genes])

        if len(expr_vector) != self._n_objectives:
            raise ValueError(
                f"Individual has {len(expr_vector)} genes, "
                f"but model expects {self._n_objectives} objectives"
            )

        # Weighted aggregate fitness
        if self._sum_weights > 0:
            weighted_sum = np.sum(expr_vector * self.objective_weights)
            return weighted_sum / self._sum_weights
        else:
            # All weights are zero (edge case)
            return 0.0

    def __repr__(self) -> str:
        return f"MultiObjectiveSelection({self._n_objectives} objectives)"
