"""Edge case tests: boundary conditions and extreme parameters."""

from happygene.entities import Gene, Individual
from happygene.expression import ConstantExpression, HillExpression
from happygene.model import GeneNetwork
from happygene.mutation import PointMutation
from happygene.selection import ProportionalSelection


class TestEdgeCases:
    """Tests for boundary and extreme conditions."""

    def test_single_individual_population(self):
        """GeneNetwork should work with population size = 1.

        Rationale: Edge case that might break mean/aggregation logic.
        """
        individuals = [Individual([Gene("gene_A", 1.0)])]

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Should run without error
        network.step()
        assert network.generation == 1
        assert network.compute_mean_fitness() == 1.0

    def test_single_gene_individual(self):
        """Individual with single gene should work.

        Rationale: Edge case for mean expression calculation.
        """
        individuals = [Individual([Gene("gene_A", 2.5)]) for _ in range(10)]

        expr_model = ConstantExpression(level=2.5)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        network.step()
        assert network.generation == 1
        assert network.compute_mean_fitness() == 2.5

    def test_zero_genes_individual(self):
        """Individual with zero genes should work.

        Rationale: Edge case that might break gene iteration.
        Mean expression of empty list should be 0.0.
        """
        individuals = [Individual([]) for _ in range(5)]

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Should run without error
        network.step()
        assert network.generation == 1
        # Mean expression of empty gene list should be 0.0
        assert network.compute_mean_fitness() == 0.0

    def test_very_large_hill_coefficient(self):
        """HillExpression with very large n should work (steep sigmoid).

        Rationale: Numerical stability test for extreme cooperativity.
        """
        individuals = [Individual([Gene("gene_A", 1.0)]) for _ in range(10)]

        # Hill with n=100 (extremely steep sigmoid)
        expr_model = HillExpression(v_max=1.0, k=0.5, n=100)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Should run without error or numerical issues
        network.step()
        assert network.generation == 1
        # With TF=0 (conditions default), Hill result should be ~0
        mean_fitness = network.compute_mean_fitness()
        assert 0.0 <= mean_fitness <= 1.0

    def test_zero_mutation_rate(self):
        """Mutation rate = 0 should prevent all mutations.

        Rationale: Edge case for mutation application.
        """
        individuals = [Individual([Gene("gene_A", 1.0)]) for _ in range(10)]

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.1)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Record initial gene expression levels
        initial_values = [
            gene.expression_level for ind in network.individuals for gene in ind.genes
        ]

        # Run many generations
        network.run(100)

        # No gene values should have changed (rate=0 means no mutations)
        final_values = [
            gene.expression_level for ind in network.individuals for gene in ind.genes
        ]
        assert (
            initial_values == final_values
        ), f"Genes changed despite 0 mutation rate: initial={initial_values}, final={final_values}"

    def test_hundred_percent_mutation_rate(self):
        """Mutation rate = 1.0 should mutate all genes every generation.

        Rationale: Edge case for mutation application.
        """
        individuals = [Individual([Gene("gene_A", 0.5)]) for _ in range(10)]

        expr_model = ConstantExpression(level=0.5)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=1.0, magnitude=0.1)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Record initial gene expression levels
        initial_values = [
            gene.expression_level for ind in network.individuals for gene in ind.genes
        ]

        # Run a few generations
        network.run(5)

        # At least some genes should have changed (extremely unlikely to stay same with rate=1.0)
        final_values = [
            gene.expression_level for ind in network.individuals for gene in ind.genes
        ]
        changes = sum(1 for i, f in zip(initial_values, final_values) if i != f)
        assert changes > 0, "No genes changed despite 100% mutation rate"

    def test_very_large_population(self):
        """GeneNetwork should handle large populations (1000 individuals).

        Rationale: Performance and aggregation edge case.
        """
        individuals = [
            Individual([Gene(f"gene_{i}_{j}", 1.0) for j in range(5)])
            for i in range(1000)
        ]

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Should run without memory or performance issues
        network.run(10)
        assert network.generation == 10
        assert network.compute_mean_fitness() == 1.0

    def test_empty_population(self):
        """GeneNetwork with empty population should not crash.

        Rationale: Edge case that might break aggregation.
        """
        individuals = []

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Should run without error
        network.step()
        assert network.generation == 1
        # Mean fitness of empty population should be 0.0
        assert network.compute_mean_fitness() == 0.0
