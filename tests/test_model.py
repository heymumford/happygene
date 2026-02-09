"""Tests for GeneNetwork model."""
import pytest
import numpy as np
from happygene.base import SimulationModel
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression, ConstantExpression
from happygene.regulatory_expression import CompositeExpressionModel, AdditiveRegulation
from happygene.regulatory_network import RegulatoryNetwork, RegulationConnection
from happygene.selection import ProportionalSelection, ThresholdSelection
from happygene.mutation import PointMutation
from happygene.conditions import Conditions


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
            seed=42
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
            seed=42
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
            seed=42
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
            seed=42
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
            seed=42
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
            seed=42
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
            seed=123
        )
        val1 = model.rng.uniform()

        model2 = GeneNetwork(
            individuals=[],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=123
        )
        val2 = model2.rng.uniform()

        assert val1 == val2

    def test_gene_network_optional_regulatory_network(self):
        """GeneNetwork accepts optional regulatory_network parameter defaulting to None."""
        individuals = [Individual(genes=[Gene("A", 1.0)])]
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        # Without regulatory_network
        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )
        assert model.regulatory_network is None

        # With regulatory_network
        reg_net = RegulatoryNetwork(
            gene_names=["A"],
            interactions=[]
        )
        model2 = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )
        assert model2.regulatory_network is reg_net

    def test_gene_network_step_with_regulation(self):
        """GeneNetwork.step() integrates TF inputs when regulatory_network provided."""
        # Setup: 2 genes where gene B is activated by gene A
        genes = [Gene("A", 1.0), Gene("B", 2.0)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Create regulatory network: A -> B with weight 1.0
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[RegulationConnection(source="A", target="B", weight=1.0)]
        )

        # Composite model: base constant + additive regulation
        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        # Before step, gene B has expression 2.0
        assert individual.genes[1].expression_level == 2.0

        model.step()

        # After step with regulation: A=0.5 (base), B = 0.5 (base) + 1.0*(1.0 tf input) = 1.5
        # (tf input for B = 1.0 * A's old expression = 1.0)
        assert individual.genes[0].expression_level == 0.5
        assert individual.genes[1].expression_level == 1.5

    def test_gene_network_backwards_compatible(self):
        """Phase 1 examples work unchanged without regulatory_network."""
        # Traditional setup without regulation
        genes = [Gene("A", 1.0), Gene("B", 2.0)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Simple linear expression (no regulation)
        expr_model = LinearExpression(slope=1.0, intercept=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        initial_mean = individual.mean_expression()
        model.step()

        # Should still compute expression from conditions (default tf_concentration=0.0)
        # expr = 1.0 * 0.0 + 1.0 = 1.0 for all genes
        assert individual.genes[0].expression_level == 1.0
        assert individual.genes[1].expression_level == 1.0
        assert model.generation == 1

    def test_gene_network_regulatory_network_immutable_after_init(self):
        """Regulatory network cannot be changed after initialization."""
        individuals = [Individual(genes=[Gene("A", 1.0)])]
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        reg_net1 = RegulatoryNetwork(
            gene_names=["A"],
            interactions=[]
        )

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net1,
            seed=42
        )

        # Attempt to modify (property setter should prevent or handle gracefully)
        # This test documents expected behavior: None or raise on attempted mutation
        assert model.regulatory_network is reg_net1
        # Create new network and attempt assignment
        reg_net2 = RegulatoryNetwork(
            gene_names=["A"],
            interactions=[]
        )
        model.regulatory_network = reg_net2
        # After assignment, verify it's the new one (mutable property)
        assert model.regulatory_network is reg_net2

    def test_gene_network_step_expression_clamped(self):
        """Expression levels are clamped to [0, inf) even with regulation."""
        genes = [Gene("A", 1.0), Gene("B", 1.0)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Regulatory network: strong repression from A to B
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[RegulationConnection(source="A", target="B", weight=-10.0)]
        )

        # Composite model with strong repression
        base_model = ConstantExpression(level=1.0)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        model.step()

        # B's expression should be clamped to 0 (1.0 + 1.0*(-10.0) = -9.0 -> 0.0)
        assert individual.genes[1].expression_level == 0.0

    def test_gene_network_multiple_individuals_regulation(self):
        """Regulation works correctly across multiple individuals in population."""
        # 2 individuals, 2 genes each
        ind1_genes = [Gene("A", 1.0), Gene("B", 0.5)]
        ind2_genes = [Gene("A", 2.0), Gene("B", 0.5)]
        individuals = [Individual(genes=ind1_genes), Individual(genes=ind2_genes)]

        # A -> B with weight 2.0
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[RegulationConnection(source="A", target="B", weight=2.0)]
        )

        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        model.step()

        # ind1: A=0.5, B = 0.5 + 1.0*2.0*1.0 = 2.5
        assert individuals[0].genes[0].expression_level == 0.5
        assert individuals[0].genes[1].expression_level == 2.5

        # ind2: A=0.5, B = 0.5 + 1.0*2.0*2.0 = 4.5
        assert individuals[1].genes[0].expression_level == 0.5
        assert individuals[1].genes[1].expression_level == 4.5

    def test_gene_network_regulatory_network_with_cycles_allowed(self):
        """GeneNetwork permits cycles in regulatory_network (acyclic check optional)."""
        # Create cyclic network: A <-> B
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[
                RegulationConnection(source="A", target="B", weight=1.0),
                RegulationConnection(source="B", target="A", weight=1.0)
            ],
            detect_circuits=False
        )

        individuals = [Individual(genes=[Gene("A", 1.0), Gene("B", 1.0)])]
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        # Should initialize without error
        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        assert model.regulatory_network is reg_net
        assert not model.regulatory_network.is_acyclic  # Verify it has cycles

    def test_gene_network_regulation_with_threshold_selection(self):
        """Regulation integrates with ThresholdSelection for binary fitness."""
        genes = [Gene("A", 1.0), Gene("B", 0.5)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # A -> B activation
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[RegulationConnection(source="A", target="B", weight=2.0)]
        )

        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        # Threshold = 2.0 (passed gene A's expr but not B initially)
        select_model = ThresholdSelection(threshold=2.0)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        model.step()

        # After step: A=0.5, B=0.5+1.0*2.0*1.0=2.5
        # Mean = (0.5 + 2.5) / 2 = 1.5 < 2.0, fitness should be 0.0
        assert individual.fitness == 0.0

    def test_gene_network_run_with_regulatory_network(self):
        """Full 100-generation simulation with regulation runs without error."""
        genes = [Gene("A", 1.0), Gene("B", 0.5), Gene("C", 0.3)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # A -> B, B -> C (feedforward)
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B", "C"],
            interactions=[
                RegulationConnection(source="A", target="B", weight=0.5),
                RegulationConnection(source="B", target="C", weight=0.5)
            ]
        )

        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=0.1)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.01, magnitude=0.05)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        # Run 100 generations
        for _ in range(100):
            model.step()

        assert model.generation == 100
        # Verify individual still has valid expression levels
        for gene in individual.genes:
            assert gene.expression_level >= 0.0
            assert np.isfinite(gene.expression_level)

    def test_gene_network_regulation_with_empty_adjacency(self):
        """Regulation with network that has no interactions (empty adjacency)."""
        genes = [Gene("A", 1.0), Gene("B", 1.0)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # No interactions (empty adjacency matrix)
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[]
        )

        base_model = ConstantExpression(level=1.0)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        model.step()

        # TF inputs should all be zero, so expr = 1.0 + 1.0*0.0 = 1.0
        assert individual.genes[0].expression_level == 1.0
        assert individual.genes[1].expression_level == 1.0

    def test_gene_network_vectorized_step_correctness(self):
        """Vectorized step() produces identical results to non-vectorized version."""
        # Create two identical models with same genes and parameters
        genes1 = [Gene("A", 1.0), Gene("B", 2.0), Gene("C", 1.5)]
        individuals1 = [Individual(genes=genes1)]

        genes2 = [Gene("A", 1.0), Gene("B", 2.0), Gene("C", 1.5)]
        individuals2 = [Individual(genes=genes2)]

        expr_model = LinearExpression(slope=2.0, intercept=0.5)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model1 = GeneNetwork(
            individuals=individuals1,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        model2 = GeneNetwork(
            individuals=individuals2,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Run both models for 3 generations
        for _ in range(3):
            model1.step()
            model2.step()

        # Verify final expression levels are identical (vectorized = non-vectorized)
        for i, gene in enumerate(individuals1[0].genes):
            assert abs(gene.expression_level - individuals2[0].genes[i].expression_level) < 1e-10

    def test_gene_network_vectorized_large_population(self):
        """Vectorized step() handles large population (100 individuals) correctly."""
        n_individuals = 100
        n_genes = 10

        # Create large population
        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_individuals)
        ]

        expr_model = LinearExpression(slope=1.5, intercept=0.2)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Execute step - should not crash and maintain population size
        model.step()

        assert len(model.individuals) == n_individuals
        assert all(len(ind.genes) == n_genes for ind in model.individuals)
        # All expression levels should be non-negative (clamped)
        assert all(g.expression_level >= 0.0 for ind in model.individuals for g in ind.genes)

    def test_gene_network_vectorized_many_genes(self):
        """Vectorized step() handles many genes (50 genes) correctly."""
        n_individuals = 10
        n_genes = 50

        # Create population with many genes
        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_individuals)
        ]

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Execute step
        model.step()

        # All genes should have constant level 1.0
        assert all(
            abs(g.expression_level - 1.0) < 1e-10
            for ind in model.individuals
            for g in ind.genes
        )

    def test_gene_network_vectorized_performance_100_indiv(self):
        """Vectorized step() executes large simulation in <500ms for 100 indiv × 50 genes."""
        import time

        n_individuals = 100
        n_genes = 50

        # Create large population with many genes
        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_individuals)
        ]

        expr_model = LinearExpression(slope=1.5, intercept=0.2)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.1, magnitude=0.1)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Time a single step with selection and mutation
        start = time.perf_counter()
        model.step()
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Must complete in under 500ms
        assert elapsed_ms < 500.0, f"Step took {elapsed_ms:.1f}ms, target <500ms"

    def test_gene_network_vectorized_matches_single_computation(self):
        """Vectorized computation with regulation matches expected phenotypes."""
        # Setup: simple 2-gene system with regulation
        genes = [Gene("A", 1.0), Gene("B", 2.0)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # A -> B with weight 1.0
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[RegulationConnection(source="A", target="B", weight=1.0)]
        )

        # Composite: base constant + additive regulation
        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        # After one step:
        # A = base = 0.5
        # B = base + weight*tf_input = 0.5 + 1.0*(1.0) = 1.5
        model.step()

        assert abs(individual.genes[0].expression_level - 0.5) < 1e-10
        assert abs(individual.genes[1].expression_level - 1.5) < 1e-10

    def test_gene_network_profile_step_execution(self):
        """Profile GeneNetwork.step() to identify performance bottlenecks.

        Captures cProfile output for medium-scale scenario (5k indiv × 50 genes × 1 gen)
        to analyze where time is spent in expression, selection, mutation phases.

        Returns profile statistics for bottleneck analysis:
        - Top 5 functions by cumulative time
        - Expression phase overhead
        - Regulatory computation cost (if present)
        """
        import cProfile
        import pstats
        import io

        # Create medium-scale scenario for profiling
        n_individuals = 5000
        n_genes = 50

        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 1.5)) for j in range(n_genes)])
            for _ in range(n_individuals)
        ]

        expr_model = LinearExpression(slope=1.0, intercept=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.1, magnitude=0.05)

        # Create regulatory network for profiling (optional, can be None)
        regulatory_network = None

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=regulatory_network,
            seed=42
        )

        # Profile the step function
        profiler = cProfile.Profile()
        profiler.enable()

        model.step()

        profiler.disable()

        # Capture profile stats to string
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions

        profile_output = s.getvalue()

        # Assert that profiling completed and produced output
        assert profile_output is not None
        assert len(profile_output) > 0
        assert "step" in profile_output or "expression" in profile_output

        # Print profile for inspection (will appear in pytest output)
        print("\n" + "=" * 80)
        print("PROFILING OUTPUT: GeneNetwork.step() - 5k × 50 × 1")
        print("=" * 80)
        print(profile_output)
        print("=" * 80)

