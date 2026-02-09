"""Tests for selection models."""

import pytest

from happygene.entities import Gene, Individual
from happygene.selection import (
    ProportionalSelection,
    SelectionModel,
    ThresholdSelection,
)


class TestSelectionModel:
    """Tests for SelectionModel ABC."""

    def test_selection_model_cannot_instantiate(self):
        """SelectionModel is abstract; cannot instantiate directly."""
        with pytest.raises(TypeError):
            SelectionModel()

    def test_selection_model_subclass_must_implement_compute_fitness(self):
        """Subclass must implement compute_fitness() method."""

        class BrokenSelection(SelectionModel):
            pass

        with pytest.raises(TypeError):
            BrokenSelection()


class TestProportionalSelection:
    """Tests for ProportionalSelection model."""

    def test_proportional_selection_creation(self):
        """ProportionalSelection can be instantiated."""
        selector = ProportionalSelection()
        assert selector is not None

    def test_proportional_selection_fitness_equals_mean_expression(self):
        """ProportionalSelection: fitness = mean_expression."""
        selector = ProportionalSelection()
        genes = [Gene("geneA", 2.0), Gene("geneB", 4.0)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        # mean = (2.0 + 4.0) / 2 = 3.0
        assert fitness == 3.0

    def test_proportional_selection_single_gene(self):
        """ProportionalSelection with single gene."""
        selector = ProportionalSelection()
        genes = [Gene("geneX", 5.0)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        assert fitness == 5.0

    def test_proportional_selection_zero_expression(self):
        """ProportionalSelection with all zero expression."""
        selector = ProportionalSelection()
        genes = [Gene("geneA", 0.0), Gene("geneB", 0.0)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        assert fitness == 0.0

    def test_proportional_selection_no_genes(self):
        """ProportionalSelection with empty individual."""
        selector = ProportionalSelection()
        individual = Individual([])
        fitness = selector.compute_fitness(individual)
        assert fitness == 0.0

    def test_proportional_selection_repr(self):
        """ProportionalSelection has informative repr."""
        selector = ProportionalSelection()
        repr_str = repr(selector)
        assert "ProportionalSelection" in repr_str


class TestThresholdSelection:
    """Tests for ThresholdSelection model."""

    def test_threshold_selection_creation(self):
        """ThresholdSelection can be created with valid threshold."""
        selector = ThresholdSelection(threshold=3.0)
        assert selector.threshold == 3.0

    def test_threshold_selection_above_threshold(self):
        """ThresholdSelection: fitness=1.0 if mean_expr >= threshold."""
        selector = ThresholdSelection(threshold=3.0)
        genes = [Gene("geneA", 2.0), Gene("geneB", 4.0)]
        individual = Individual(genes)
        # mean = 3.0, threshold = 3.0 → should be 1.0
        fitness = selector.compute_fitness(individual)
        assert fitness == 1.0

    def test_threshold_selection_below_threshold(self):
        """ThresholdSelection: fitness=0.0 if mean_expr < threshold."""
        selector = ThresholdSelection(threshold=4.0)
        genes = [Gene("geneA", 2.0), Gene("geneB", 4.0)]
        individual = Individual(genes)
        # mean = 3.0, threshold = 4.0 → should be 0.0
        fitness = selector.compute_fitness(individual)
        assert fitness == 0.0

    def test_threshold_selection_exactly_at_threshold(self):
        """ThresholdSelection: fitness=1.0 at exactly threshold."""
        selector = ThresholdSelection(threshold=2.5)
        genes = [Gene("geneA", 2.5)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        assert fitness == 1.0

    def test_threshold_selection_zero_threshold(self):
        """ThresholdSelection with threshold=0."""
        selector = ThresholdSelection(threshold=0.0)
        genes = [Gene("geneA", 0.1)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        assert fitness == 1.0

    def test_threshold_selection_high_threshold(self):
        """ThresholdSelection with high threshold rejects low expression."""
        selector = ThresholdSelection(threshold=100.0)
        genes = [Gene("geneA", 5.0)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        assert fitness == 0.0

    def test_threshold_selection_negative_threshold_allowed(self):
        """ThresholdSelection allows negative thresholds."""
        selector = ThresholdSelection(threshold=-1.0)
        genes = [Gene("geneA", 0.0)]
        individual = Individual(genes)
        fitness = selector.compute_fitness(individual)
        # mean = 0.0, threshold = -1.0 → 0.0 >= -1.0 → 1.0
        assert fitness == 1.0

    def test_threshold_selection_repr(self):
        """ThresholdSelection has informative repr."""
        selector = ThresholdSelection(threshold=2.5)
        repr_str = repr(selector)
        assert "ThresholdSelection" in repr_str
        assert "2.5" in repr_str
