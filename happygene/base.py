"""SimulationModel: abstract base for all happygene simulations (ADR-001)."""
from abc import ABC, abstractmethod

import numpy as np


class SimulationModel(ABC):
    """Abstract base class for gene network simulation models.

    Provides generation tracking, reproducible RNG, and a step() contract.
    Custom base (not Mesa.Model) per ADR-001: biology-first API.

    Parameters
    ----------
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(self, seed: int | None = None):
        self._generation: int = 0
        self._rng: np.random.Generator = np.random.default_rng(seed)
        self._running: bool = True

    @property
    def generation(self) -> int:
        """Current generation number (0-indexed)."""
        return self._generation

    @property
    def rng(self) -> np.random.Generator:
        """Reproducible random number generator."""
        return self._rng

    @property
    def running(self) -> bool:
        """Whether the simulation is still active."""
        return self._running

    @abstractmethod
    def step(self) -> None:
        """Advance the simulation by one generation. Subclasses must implement."""
        ...

    def run(self, generations: int) -> None:
        """Run simulation for a fixed number of generations.

        Parameters
        ----------
        generations : int
            Number of generations to simulate.
        """
        for _ in range(generations):
            if not self._running:
                break
            self.step()
