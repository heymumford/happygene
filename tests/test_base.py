"""Tests for SimulationModel abstract base class."""
import pytest
from happygene.base import SimulationModel


class ConcreteModel(SimulationModel):
    """Minimal concrete subclass for testing."""

    def step(self):
        self._generation += 1


def test_simulation_model_cannot_instantiate():
    """SimulationModel is abstract; direct instantiation must raise TypeError."""
    with pytest.raises(TypeError):
        SimulationModel(seed=42)


def test_concrete_model_step_increments_generation():
    """Calling step() on a concrete subclass advances the generation counter."""
    model = ConcreteModel(seed=42)
    assert model.generation == 0
    model.step()
    assert model.generation == 1
