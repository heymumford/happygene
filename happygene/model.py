"""GeneNetwork: the main simulation model."""
from typing import List
from happygene.base import SimulationModel
from happygene.entities import Individual


class GeneNetwork(SimulationModel):
    """Main simulation model for gene network evolution.

    Concrete subclass of SimulationModel providing population management
    and fitness computation.

    Parameters
    ----------
    individuals : List[Individual]
        List of individuals in the population.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(self, individuals: List[Individual], seed: int | None = None):
        super().__init__(seed=seed)
        self.individuals: List[Individual] = individuals

    def step(self) -> None:
        """Advance the simulation by one generation.

        Increments generation counter. Population dynamics (selection,
        mutation, etc.) will be added in later phases.
        """
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
