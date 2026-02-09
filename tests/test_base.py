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


def test_simulation_model_run_multiple_generations():
    """run(n) should call step() n times and advance generation."""
    model = ConcreteModel(seed=42)
    model.run(5)
    assert model.generation == 5


def test_simulation_model_run_stops_when_not_running():
    """run() should stop early if running flag becomes False."""
    model = ConcreteModel(seed=42)

    # Override step to set running=False after 3 calls
    call_count = [0]

    original_step = model.step

    def patched_step():
        original_step()
        call_count[0] += 1
        if call_count[0] >= 3:
            model._running = False

    model.step = patched_step

    # Try to run 10 generations but should stop at 3
    model.run(10)
    assert model.generation == 3
    assert call_count[0] == 3
