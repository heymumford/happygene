"""Tests for GeneNetwork model."""

import pytest
from happygene.base import SimulationModel
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression
from happygene.selection import ProportionalSelection
from happygene.mutation import PointMutation


class TestGeneNetwork:
    """Tests for GeneNetwork simulation model."""

    def test_gene_network_creation(self):
        """GeneNetwork can be instantiated as a concrete SimulationModel."""
        individuals = [Individual(genes=[Gene("A", 2.0)])]
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )
        assert isinstance(model, SimulationModel)
        assert model.generation == 0

    def test_gene_network_has_individuals(self):
        """GeneNetwork stores and retrieves individuals."""
        genes1 = [Gene("A", 1.0), Gene("B", 2.0)]
        genes2 = [Gene("A", 3.0), Gene("B", 4.0)]
        individuals = [Individual(genes=genes1), Individual(genes=genes2)]
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )
        assert len(model.individuals) == 2
        assert model.individuals[0].mean_expression() == 1.5

    def test_gene_network_compute_mean_fitness(self):
        """compute_mean_fitness() returns average fitness across individuals."""
        individuals = [Individual(genes=[]), Individual(genes=[])]
        individuals[0].fitness = 1.0
        individuals[1].fitness = 3.0
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )
        assert model.compute_mean_fitness() == 2.0

    def test_gene_network_compute_mean_fitness_empty(self):
        """compute_mean_fitness() returns 0.0 for empty population."""
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=[],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )
        assert model.compute_mean_fitness() == 0.0

    def test_gene_network_step_increments_generation(self):
        """Calling step() advances generation counter."""
        individuals = [Individual(genes=[])]
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )
        assert model.generation == 0
        model.step()
        assert model.generation == 1

    def test_gene_network_empty_step(self):
        """step() works even with empty population."""
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=[],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )
        model.step()
        assert model.generation == 1

    def test_gene_network_has_rng(self):
        """GeneNetwork has reproducible random number generator."""
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)
        model = GeneNetwork(
            individuals=[],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=123,
        )
        val1 = model.rng.uniform()

        model2 = GeneNetwork(
            individuals=[],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=123,
        )
        val2 = model2.rng.uniform()

        assert val1 == val2
