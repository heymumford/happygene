"""GeneNetwork: the main simulation model."""
from typing import List, Optional

import numpy as np

from happygene.base import SimulationModel
from happygene.conditions import Conditions
from happygene.entities import Individual
from happygene.expression import ExpressionModel
from happygene.mutation import MutationModel
from happygene.regulatory_network import RegulatoryNetwork
from happygene.selection import SelectionModel


class GeneNetwork(SimulationModel):
    """Main simulation model for gene network evolution.

    Concrete subclass of SimulationModel providing population management,
    gene expression computation, fitness evaluation, and mutation.

    Parameters
    ----------
    individuals : List[Individual]
        List of individuals in the population.
    expression_model : ExpressionModel
        Model for computing gene expression levels.
    selection_model : SelectionModel
        Model for computing individual fitness.
    mutation_model : MutationModel
        Model for introducing genetic variation.
    seed : int or None
        Random seed for reproducibility.
    conditions : Conditions or None
        Environmental conditions (default: Conditions()).
    """

    def __init__(
        self,
        individuals: List[Individual],
        expression_model: ExpressionModel,
        selection_model: SelectionModel,
        mutation_model: MutationModel,
        seed: int | None = None,
        conditions: Conditions | None = None,
        regulatory_network: Optional[RegulatoryNetwork] = None,
    ):
        super().__init__(seed=seed)
        self.individuals: List[Individual] = individuals
        self.expression_model: ExpressionModel = expression_model
        self.selection_model: SelectionModel = selection_model
        self.mutation_model: MutationModel = mutation_model
        self.conditions: Conditions = conditions or Conditions()
        self._regulatory_network: Optional[RegulatoryNetwork] = regulatory_network

    def step(self) -> None:
        """Advance the simulation by one generation.

        Implements the full life cycle with vectorized expression computation:
        1. Expression: Compute gene expression using expression_model (VECTORIZED)
           - Build expression_matrix: (n_individuals, n_genes) NumPy array
           - If regulatory_network provided, compute TF inputs via sparse matrix
           - Use NumPy broadcasting for efficient computation
           - Update genes in-place from matrix
        2. Selection: Evaluate fitness using selection_model
        3. Mutation: Introduce variation using mutation_model
        4. Increment: Advance generation counter
        """
        # Phase 1: Vectorized expression computation
        n_indiv = len(self.individuals)

        if n_indiv == 0:
            self._generation += 1
            return

        # Determine n_genes from first individual
        n_genes = len(self.individuals[0].genes)

        # Initialize expression matrix
        expr_matrix = np.zeros((n_indiv, n_genes))

        if self._regulatory_network is not None:
            # Vectorized regulatory computation
            for ind_idx, individual in enumerate(self.individuals):
                # Get current expression for this individual
                prev_expr = np.array([g.expression_level for g in individual.genes])
                # Compute TF inputs: adjacency @ expression (sparse matrix operations)
                tf_inputs = self._regulatory_network.compute_tf_inputs(prev_expr)

                # Check if model is composite (has regulatory_model)
                if hasattr(self.expression_model, 'regulatory_model'):
                    # Apply expression model with TF inputs for each gene
                    for gene_idx in range(n_genes):
                        expr = self.expression_model.compute(
                            self.conditions,
                            tf_inputs=tf_inputs[gene_idx]
                        )
                        expr_matrix[ind_idx, gene_idx] = max(0.0, expr)
                else:
                    # Fallback: compute base model without TF inputs
                    for gene_idx in range(n_genes):
                        expr = self.expression_model.compute(self.conditions)
                        expr_matrix[ind_idx, gene_idx] = max(0.0, expr)
        else:
            # No regulation: vectorize across all individuals and genes
            # Compute single expression value and broadcast to all
            expr_val = self.expression_model.compute(self.conditions)
            expr_matrix[:, :] = max(0.0, expr_val)

        # Update individuals from expression matrix (in-place)
        for ind_idx, individual in enumerate(self.individuals):
            for gene_idx, gene in enumerate(individual.genes):
                gene._expression_level = expr_matrix[ind_idx, gene_idx]

        # Phase 2: Evaluate fitness (vectorized via batch methods)
        # Use selection_model.compute_fitness_batch for vectorized fitness computation
        # All selection models support batch computation
        if n_genes > 0:
            fitness_values = self.selection_model.compute_fitness_batch(expr_matrix)
            for ind_idx, individual in enumerate(self.individuals):
                individual.fitness = fitness_values[ind_idx]
        else:
            # Empty genes: use per-individual computation
            for individual in self.individuals:
                fitness = self.selection_model.compute_fitness(individual)
                individual.fitness = fitness

        # Phase 3: Apply mutations
        for individual in self.individuals:
            self.mutation_model.mutate(individual, self.rng)

        # Phase 4: Increment generation
        self._generation += 1

    @property
    def regulatory_network(self) -> Optional[RegulatoryNetwork]:
        """Access to regulatory network (if provided).

        Returns
        -------
        Optional[RegulatoryNetwork]
            Regulatory network for gene-to-gene interactions, or None.
        """
        return self._regulatory_network

    @regulatory_network.setter
    def regulatory_network(self, value: Optional[RegulatoryNetwork]) -> None:
        """Set regulatory network (optional).

        Parameters
        ----------
        value : Optional[RegulatoryNetwork]
            Regulatory network to set, or None.
        """
        self._regulatory_network = value

    def compute_mean_fitness(self) -> float:
        """Compute mean fitness across all individuals.

        Returns
        -------
        float
            Mean fitness. Returns 0.0 if population is empty.
        """
        if not self.individuals:
            return 0.0
        return sum(ind.fitness for ind in self.individuals) / len(self.individuals)
