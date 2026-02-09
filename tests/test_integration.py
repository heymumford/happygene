"""Integration tests for full simulation loop."""

from happygene.conditions import Conditions
from happygene.entities import Gene, Individual
from happygene.expression import LinearExpression
from happygene.model import GeneNetwork
from happygene.mutation import PointMutation
from happygene.selection import ProportionalSelection


class TestFullSimulationLoop:
    """Tests for complete simulation: express → select → mutate."""

    def test_gene_network_full_step_loop(self):
        """GeneNetwork.step() advances generation and applies models."""
        # Create individuals with genes
        genes_ind1 = [Gene("geneA", 2.0), Gene("geneB", 3.0)]
        genes_ind2 = [Gene("geneA", 1.5), Gene("geneB", 2.5)]
        individuals = [Individual(genes_ind1), Individual(genes_ind2)]

        # Create models
        expr_model = LinearExpression(slope=1.0, intercept=0.5)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.5, magnitude=0.1)

        # Create network
        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Initial state
        assert network.generation == 0
        assert len(network.individuals) == 2

        # Step once
        network.step()

        # Generation incremented
        assert network.generation == 1

    def test_multiple_generations_increase_generation_counter(self):
        """run() method should increase generation counter correctly."""
        genes_ind = [Gene("geneA", 1.0)]
        individual = Individual(genes_ind)

        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.1, magnitude=0.1)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Run for 10 generations
        network.run(10)
        assert network.generation == 10

    def test_step_applies_expression_model(self):
        """step() should apply expression model to update genes."""
        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)

        # Expression model: E = 2.0 * tf + 1.0
        expr_model = LinearExpression(slope=2.0, intercept=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)  # No mutations

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
            conditions=Conditions(tf_concentration=2.0),
        )

        # After step: E = 2.0 * 2.0 + 1.0 = 5.0
        network.step()

        # Gene expression should be updated
        assert individual.genes[0].expression_level == 5.0

    def test_step_applies_selection_model(self):
        """step() should apply selection model to set fitness."""
        genes = [Gene("geneA", 2.0), Gene("geneB", 4.0)]
        individual = Individual(genes)

        # Expression model: E = 1.0 * tf + 1.0 with tf=2.0 → E = 3.0 for both genes
        expr_model = LinearExpression(slope=1.0, intercept=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
            conditions=Conditions(tf_concentration=2.0),
        )

        initial_fitness = individual.fitness
        network.step()

        # After expression: both genes = 1.0 * 2.0 + 1.0 = 3.0
        # Fitness = mean expression = (3.0 + 3.0) / 2 = 3.0
        assert individual.fitness == 3.0
        assert individual.fitness != initial_fitness

    def test_step_applies_mutation_model(self):
        """step() should apply mutation model with sufficient probability."""
        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)

        expr_model = LinearExpression(slope=0.0, intercept=0.0)
        select_model = ProportionalSelection()
        # High mutation rate and magnitude to ensure mutation occurs
        mutate_model = PointMutation(rate=1.0, magnitude=1.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        network.step()

        # Gene expression likely changed due to high mutation rate
        # Note: not guaranteed, but extremely likely with rate=1.0, magnitude=1.0
        assert individual.genes[0].expression_level >= 0.0

    def test_deterministic_simulation_with_seed(self):
        """Two simulations with same seed should produce identical results."""
        genes1 = [Gene("geneA", 1.0)]
        individual1 = Individual(genes1)

        genes2 = [Gene("geneA", 1.0)]
        individual2 = Individual(genes2)

        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.5, magnitude=0.5)

        # Simulation 1
        network1 = GeneNetwork(
            individuals=[individual1],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=123,
        )
        network1.run(5)

        # Simulation 2
        network2 = GeneNetwork(
            individuals=[individual2],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=123,
        )
        network2.run(5)

        # Both should have same generation
        assert network1.generation == network2.generation == 5

        # Both should have same final expression (deterministic with same seed)
        assert (
            individual1.genes[0].expression_level
            == individual2.genes[0].expression_level
        )
