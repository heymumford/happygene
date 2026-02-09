"""GeneNetwork: the main simulation model."""

from typing import List

from happygene.base import SimulationModel
from happygene.conditions import Conditions
from happygene.entities import Individual
from happygene.expression import ExpressionModel
from happygene.mutation import MutationModel
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
    ):
        super().__init__(seed=seed)
        self.individuals: List[Individual] = individuals
        self.expression_model: ExpressionModel = expression_model
        self.selection_model: SelectionModel = selection_model
        self.mutation_model: MutationModel = mutation_model
        self.conditions: Conditions = conditions or Conditions()

    def step(self) -> None:
        """Advance the simulation by one generation.

        Implements the full life cycle:
        1. Expression: Compute gene expression using expression_model
        2. Selection: Evaluate fitness using selection_model
        3. Mutation: Introduce variation using mutation_model
        4. Increment: Advance generation counter
        """
        # Phase 1: Compute expression for all genes
        for individual in self.individuals:
            for gene in individual.genes:
                expr_level = self.expression_model.compute(self.conditions)
                gene._expression_level = expr_level

        # Phase 2: Evaluate fitness
        for individual in self.individuals:
            fitness = self.selection_model.compute_fitness(individual)
            individual.fitness = fitness

        # Phase 3: Apply mutations
        for individual in self.individuals:
            self.mutation_model.mutate(individual, self.rng)

        # Phase 4: Increment generation
        self._generation += 1

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
