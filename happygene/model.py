"""GeneNetwork: the main simulation model."""
from typing import List, Optional
import numpy as np
from happygene.base import SimulationModel
from happygene.entities import Individual
from happygene.conditions import Conditions
from happygene.expression import ExpressionModel
from happygene.selection import SelectionModel
from happygene.mutation import MutationModel
from happygene.regulatory_network import RegulatoryNetwork


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

        Implements the full life cycle:
        1. Expression: Compute gene expression using expression_model
           - If regulatory_network provided, compute TF inputs via sparse matrix multiplication
           - Pass TF inputs to CompositeExpressionModel if applicable
        2. Selection: Evaluate fitness using selection_model
        3. Mutation: Introduce variation using mutation_model
        4. Increment: Advance generation counter
        """
        # Phase 1: Compute expression for all genes
        for individual in self.individuals:
            # If regulatory network provided, compute TF inputs from current expression
            if self._regulatory_network is not None:
                expr_vector = np.array([g.expression_level for g in individual.genes])
                tf_inputs = self._regulatory_network.compute_tf_inputs(expr_vector)
            else:
                tf_inputs = None

            for gene_idx, gene in enumerate(individual.genes):
                if tf_inputs is not None:
                    # CompositeExpressionModel accepts tf_inputs parameter
                    if hasattr(self.expression_model, 'regulatory_model'):
                        expr_level = self.expression_model.compute(
                            self.conditions, tf_inputs=tf_inputs[gene_idx]
                        )
                    else:
                        # Fallback for non-composite models (ignore tf_inputs)
                        expr_level = self.expression_model.compute(self.conditions)
                else:
                    # No regulation: standard behavior
                    expr_level = self.expression_model.compute(self.conditions)

                gene._expression_level = max(0.0, expr_level)

        # Phase 2: Evaluate fitness
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
