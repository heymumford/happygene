"""Comprehensive edge case tests - Cycle 2: Selection models, GeneNetwork integration."""
import pytest
import numpy as np
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import ConstantExpression, LinearExpression, HillExpression
from happygene.selection import (
    SexualReproduction,
    EpistaticFitness,
    MultiObjectiveSelection,
    ThresholdSelection,
    ProportionalSelection,
)
from happygene.mutation import PointMutation
from happygene.conditions import Conditions
from happygene.datacollector import DataCollector


class TestSexualReproductionEdgeCases:
    """Edge cases for sexual reproduction."""

    def test_mate_with_mismatched_gene_counts(self):
        """SexualReproduction.mate() should raise ValueError for mismatched gene counts.

        Rationale: Gene count mismatch breaks crossover logic.
        Expected: ValueError with clear message.
        """
        parent1 = Individual([Gene("g1", 1.0)])
        parent2 = Individual([Gene("g1", 1.0), Gene("g2", 2.0)])

        repro = SexualReproduction(crossover_rate=0.5)
        rng = np.random.default_rng(42)

        with pytest.raises(ValueError, match="Parent gene counts differ"):
            repro.mate(parent1, parent2, rng)

    def test_mate_with_empty_parents(self):
        """SexualReproduction.mate() with empty parents should produce empty offspring.

        Rationale: Edge case for iteration logic.
        """
        parent1 = Individual([])
        parent2 = Individual([])

        repro = SexualReproduction(crossover_rate=0.5)
        rng = np.random.default_rng(42)

        offspring = repro.mate(parent1, parent2, rng)
        assert len(offspring.genes) == 0

    def test_mate_crossover_rate_zero_clones_parent1(self):
        """SexualReproduction with crossover_rate=0 should clone parent1.

        Rationale: Boundary behavior for crossover probability.
        """
        parent1 = Individual([Gene("g1", 3.0), Gene("g2", 5.0)])
        parent2 = Individual([Gene("g1", 10.0), Gene("g2", 20.0)])

        repro = SexualReproduction(crossover_rate=0.0)
        rng = np.random.default_rng(42)

        offspring = repro.mate(parent1, parent2, rng)
        assert offspring.genes[0].expression_level == 3.0
        assert offspring.genes[1].expression_level == 5.0

    def test_mate_crossover_rate_one_clones_parent2(self):
        """SexualReproduction with crossover_rate=1 should clone parent2.

        Rationale: Boundary behavior for crossover probability.
        """
        parent1 = Individual([Gene("g1", 3.0), Gene("g2", 5.0)])
        parent2 = Individual([Gene("g1", 10.0), Gene("g2", 20.0)])

        repro = SexualReproduction(crossover_rate=1.0)
        rng = np.random.default_rng(42)

        offspring = repro.mate(parent1, parent2, rng)
        assert offspring.genes[0].expression_level == 10.0
        assert offspring.genes[1].expression_level == 20.0


class TestEpistaticFitnessEdgeCases:
    """Edge cases for epistatic fitness model."""

    def test_epistatic_fitness_with_1d_matrix_raises_error(self):
        """EpistaticFitness should reject 1D matrix.

        Rationale: Interactions must be 2D (gene x gene).
        Expected: ValueError.
        """
        with pytest.raises(ValueError, match="must be 2D"):
            EpistaticFitness(interaction_matrix=np.array([0.1, 0.2, 0.3]))

    def test_epistatic_fitness_with_non_square_matrix_raises_error(self):
        """EpistaticFitness should reject non-square matrices.

        Rationale: Interactions must form a square matrix.
        """
        with pytest.raises(ValueError, match="must be square"):
            EpistaticFitness(interaction_matrix=np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]))

    def test_epistatic_fitness_with_1_gene(self):
        """EpistaticFitness with 1x1 matrix and 1-gene individual.

        Rationale: Edge case for minimal epistasis.
        """
        interactions = np.array([[0.5]])
        selector = EpistaticFitness(interaction_matrix=interactions)

        individual = Individual([Gene("g1", 2.0)])
        fitness = selector.compute_fitness(individual)

        # base = 2.0, epistatic_bonus = 2.0 * 2.0 * 0.5 / 1 = 2.0
        # fitness = 2.0 + 2.0 = 4.0
        expected = 2.0 + (2.0 * 2.0 * 0.5 / 1)
        assert fitness == pytest.approx(expected)

    def test_epistatic_fitness_with_wrong_gene_count_raises_error(self):
        """EpistaticFitness should reject individuals with wrong gene count.

        Rationale: Gene count must match matrix size.
        """
        interactions = np.array([[0.1, 0.2], [0.2, 0.1]])
        selector = EpistaticFitness(interaction_matrix=interactions)

        # Individual has 3 genes, but matrix is 2x2
        individual = Individual([Gene("g1", 1.0), Gene("g2", 1.0), Gene("g3", 1.0)])

        with pytest.raises(ValueError, match="Individual has 3 genes"):
            selector.compute_fitness(individual)

    def test_epistatic_fitness_with_zero_expressions(self):
        """EpistaticFitness with all zero expressions.

        Rationale: Boundary condition for epistatic interactions.
        """
        interactions = np.array([[0.5, 0.3], [0.3, 0.5]])
        selector = EpistaticFitness(interaction_matrix=interactions)

        individual = Individual([Gene("g1", 0.0), Gene("g2", 0.0)])
        fitness = selector.compute_fitness(individual)

        # base = 0.0, epistatic_bonus = 0.0 (all zeros)
        assert fitness == 0.0

    def test_epistatic_fitness_with_negative_interactions(self):
        """EpistaticFitness with negative interactions (antagonism).

        Rationale: Should handle negative epistasis correctly.
        """
        interactions = np.array([[-0.1, 0.2], [0.2, -0.1]])
        selector = EpistaticFitness(interaction_matrix=interactions)

        individual = Individual([Gene("g1", 1.0), Gene("g2", 1.0)])
        fitness = selector.compute_fitness(individual)

        # base = 1.0
        # epistatic_bonus = (1*1*(-0.1) + 1*1*0.2 + 1*1*0.2 + 1*1*(-0.1)) / 2
        #                = (-0.1 + 0.2 + 0.2 - 0.1) / 2 = 0.2 / 2 = 0.1
        # fitness = 1.0 + 0.1 = 1.1
        assert fitness == pytest.approx(1.1)


class TestMultiObjectiveSelectionEdgeCases:
    """Edge cases for multi-objective selection."""

    def test_multi_objective_with_wrong_gene_count_raises_error(self):
        """MultiObjectiveSelection should reject individuals with wrong gene count.

        Rationale: Gene count must match number of objectives.
        """
        weights = [1.0, 1.0, 1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        # Individual has 2 genes, but model expects 3
        individual = Individual([Gene("g1", 1.0), Gene("g2", 1.0)])

        with pytest.raises(ValueError, match="Individual has 2 genes"):
            selector.compute_fitness(individual)

    def test_multi_objective_with_single_objective(self):
        """MultiObjectiveSelection with 1 objective.

        Rationale: Degenerate case.
        """
        weights = [1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        individual = Individual([Gene("g1", 3.5)])
        fitness = selector.compute_fitness(individual)

        # fitness = 3.5 * 1.0 / 1.0 = 3.5
        assert fitness == pytest.approx(3.5)

    def test_multi_objective_with_all_zero_weights(self):
        """MultiObjectiveSelection with all zero weights.

        Rationale: Edge case for weight normalization.
        """
        weights = [0.0, 0.0, 0.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        individual = Individual([Gene("g1", 1.0), Gene("g2", 2.0), Gene("g3", 3.0)])
        fitness = selector.compute_fitness(individual)

        # fitness = 0 (sum of weights is 0, so return 0.0 from else branch)
        assert fitness == 0.0

    def test_multi_objective_with_mixed_weights(self):
        """MultiObjectiveSelection with different weights for each objective.

        Rationale: Weighted aggregation correctness.
        """
        weights = [1.0, 2.0, 3.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        individual = Individual([Gene("g1", 1.0), Gene("g2", 2.0), Gene("g3", 3.0)])
        fitness = selector.compute_fitness(individual)

        # fitness = (1*1 + 2*2 + 3*3) / (1+2+3) = (1 + 4 + 9) / 6 = 14/6 ≈ 2.333
        expected = (1.0 * 1 + 2.0 * 2 + 3.0 * 3) / (1.0 + 2.0 + 3.0)
        assert fitness == pytest.approx(expected)

    def test_multi_objective_with_negative_weights_raises_error(self):
        """MultiObjectiveSelection should reject negative weights.

        Rationale: Weights must be non-negative.
        """
        with pytest.raises(ValueError, match="must be non-negative"):
            MultiObjectiveSelection(objective_weights=[1.0, -0.5, 1.0])


class TestGeneNetworkWithThresholdSelection:
    """Test GeneNetwork.step() with ThresholdSelection (exercises else branch)."""

    def test_network_step_with_threshold_selection_below_threshold(self):
        """GeneNetwork.step() with ThresholdSelection when mean expression < threshold.

        Rationale: Tests the else branch (fitness = 0.0).
        """
        individuals = [
            Individual([Gene("g1", 0.5), Gene("g2", 0.3)]),
            Individual([Gene("g1", 0.2), Gene("g2", 0.1)]),
        ]

        expr_model = ConstantExpression(level=0.2)
        select_model = ThresholdSelection(threshold=1.0)  # Mean expression < 1.0
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
        # All fitness values should be 0.0 (below threshold)
        for individual in network.individuals:
            assert individual.fitness == 0.0

    def test_network_step_with_threshold_selection_above_threshold(self):
        """GeneNetwork.step() with ThresholdSelection when mean expression >= threshold.

        Rationale: Tests the if branch (fitness = 1.0).
        """
        individuals = [
            Individual([Gene("g1", 2.0), Gene("g2", 2.0)]),
            Individual([Gene("g1", 1.5), Gene("g2", 1.5)]),
        ]

        expr_model = ConstantExpression(level=2.0)
        select_model = ThresholdSelection(threshold=1.0)  # Mean expression >= 1.0
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
        # All fitness values should be 1.0 (above threshold)
        for individual in network.individuals:
            assert individual.fitness == 1.0


class TestGeneNetworkWithEpistaticFitness:
    """Test GeneNetwork.step() with EpistaticFitness selection model."""

    def test_network_step_with_epistatic_fitness(self):
        """GeneNetwork.step() with EpistaticFitness model.

        Rationale: Integration test for epistatic fitness in full simulation.
        """
        individuals = [
            Individual([Gene("g1", 1.0), Gene("g2", 0.8)]),
            Individual([Gene("g1", 0.5), Gene("g2", 1.2)]),
        ]

        expr_model = ConstantExpression(level=1.0)
        interactions = np.array([[0.1, 0.3], [0.3, 0.1]])
        select_model = EpistaticFitness(interaction_matrix=interactions)
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
        # All individuals should have fitness > 0
        for individual in network.individuals:
            assert individual.fitness > 0.0


class TestGeneNetworkWithMultiObjectiveSelection:
    """Test GeneNetwork.step() with MultiObjectiveSelection model."""

    def test_network_step_with_multi_objective_selection(self):
        """GeneNetwork.step() with MultiObjectiveSelection model.

        Rationale: Integration test for multi-objective fitness in full simulation.
        """
        individuals = [
            Individual([Gene("g1", 0.5), Gene("g2", 0.3), Gene("g3", 0.8)]),
            Individual([Gene("g1", 1.0), Gene("g2", 0.2), Gene("g3", 0.4)]),
        ]

        expr_model = ConstantExpression(level=0.5)
        weights = [1.0, 2.0, 3.0]
        select_model = MultiObjectiveSelection(objective_weights=weights)
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
        # Fitness values should be in expected range
        for individual in network.individuals:
            assert 0.0 <= individual.fitness <= 1.0


class TestMutationClamping:
    """Test mutation behavior with negative values that get clamped."""

    def test_mutation_clamps_negative_expression_to_zero(self):
        """PointMutation should clamp negative expression values to 0.

        Rationale: Expression levels must be non-negative.
        Test strategy: Use large mutation magnitude and fixed seed to
        ensure we hit negative values.
        """
        individuals = [Individual([Gene("g1", 0.1)])]

        expr_model = ConstantExpression(level=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=1.0, magnitude=1.0)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Run multiple generations to trigger mutations
        network.run(20)

        # Check that all expression levels are >= 0
        for individual in network.individuals:
            for gene in individual.genes:
                assert gene.expression_level >= 0.0, \
                    f"Gene {gene.name} has negative expression: {gene.expression_level}"

    def test_mutation_with_large_negative_perturbation(self):
        """Mutation should handle large negative perturbations correctly.

        Rationale: Verify clamping works with extreme negative values.
        """
        gene = Gene("test_gene", 0.5)
        individual = Individual([gene])

        mutate_model = PointMutation(rate=1.0, magnitude=10.0)
        rng = np.random.default_rng(42)

        # Run mutation multiple times
        for _ in range(100):
            mutate_model.mutate(individual, rng)
            # Expression should never be negative
            assert gene.expression_level >= 0.0


class TestHillExpressionWithZeroTF:
    """Test HillExpression behavior with tf_concentration = 0."""

    def test_hill_expression_with_tf_zero(self):
        """HillExpression with tf_concentration=0 should give ~0 expression.

        Rationale: At tf=0, Hill equation yields: E = v_max * 0 / (k^n + 0) = 0
        Expected: Result very close to 0.
        """
        hill_model = HillExpression(v_max=1.0, k=0.5, n=2.0)
        conditions = Conditions(tf_concentration=0.0)

        expr = hill_model.compute(conditions)
        assert expr == pytest.approx(0.0, abs=1e-10)

    def test_hill_expression_with_tf_below_k(self):
        """HillExpression with tf << k should give low expression.

        Rationale: When tf is much smaller than k, denominator dominates.
        """
        hill_model = HillExpression(v_max=1.0, k=10.0, n=2.0)
        conditions = Conditions(tf_concentration=0.1)

        expr = hill_model.compute(conditions)
        # At tf=0.1, k=10, n=2: E = 1.0 * (0.1^2) / (10^2 + 0.1^2) ≈ very small
        assert 0.0 <= expr < 0.01

    def test_hill_expression_with_tf_equal_k(self):
        """HillExpression with tf = k should give v_max/2^n.

        Rationale: This is the definition of k (half-saturation).
        With n=1: E = v_max * k / (k + k) = v_max/2
        """
        hill_model = HillExpression(v_max=2.0, k=1.0, n=1.0)
        conditions = Conditions(tf_concentration=1.0)

        expr = hill_model.compute(conditions)
        # At tf=k, E = v_max/2^n = 2.0/2 = 1.0
        assert expr == pytest.approx(1.0)

    def test_hill_expression_with_tf_large(self):
        """HillExpression with tf >> k should give ~v_max.

        Rationale: Saturation behavior - high TF saturates the system.
        """
        hill_model = HillExpression(v_max=1.5, k=0.5, n=2.0)
        conditions = Conditions(tf_concentration=100.0)

        expr = hill_model.compute(conditions)
        # At very high tf, should approach v_max
        assert expr > 1.4  # Close to v_max=1.5


class TestDataCollectorWithMaxHistory:
    """Test DataCollector with max_history constraint."""

    def test_datacollector_respects_max_history_gene_level(self):
        """DataCollector with max_history should drop old gene data.

        Rationale: Memory management for long simulations.
        """
        individuals = [Individual([Gene("g1", 1.0)])]

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

        # Create collector with max_history=5
        collector = DataCollector(
            model_reporters={"mean_fitness": lambda m: m.compute_mean_fitness()},
            individual_reporters={"fitness": lambda ind: ind.fitness},
            gene_reporters={"expression": lambda gene: gene.expression_level},
            max_history=5,
        )

        # Run 10 generations and collect data
        for _ in range(10):
            collector.collect(network)
            network.step()

        # Gene data should be limited by max_history
        # Each generation has n_individuals * n_genes rows
        # So 10 generations with 1 individual and 1 gene = 10 rows
        # But max_history=5, so should keep only last 5 rows
        gene_df = collector.get_gene_dataframe()
        assert len(gene_df) <= 5

    def test_datacollector_with_max_history_model_data(self):
        """DataCollector max_history should also apply to model-level data.

        Rationale: Consistent history management across all tiers.
        """
        individuals = [Individual([Gene("g1", 1.0)])]

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

        collector = DataCollector(
            model_reporters={"mean_fitness": lambda m: m.compute_mean_fitness()},
            max_history=3,
        )

        # Collect for 8 generations
        for _ in range(8):
            collector.collect(network)
            network.step()

        model_df = collector.get_model_dataframe()
        assert len(model_df) <= 3

    def test_datacollector_with_max_history_preserves_last_n_rows(self):
        """DataCollector should preserve the LAST max_history rows.

        Rationale: Verify correct trimming behavior (not first N).
        """
        individuals = [Individual([Gene("g1", 1.0)])]

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

        collector = DataCollector(
            model_reporters={"gen": lambda m: m.generation},
            max_history=2,
        )

        # Collect for 5 generations
        for i in range(5):
            collector.collect(network)
            network.step()

        model_df = collector.get_model_dataframe()
        # Should have exactly 2 rows (max_history=2)
        assert len(model_df) == 2
        # Generations should be 3 and 4 (the last two before step() increments)
        # Actually: collect at gen 0,1,2,3,4 then step increments to 1,2,3,4,5
        # So we collect at generations 0,1,2,3,4 and keep last 2: gens 3,4
        generations = sorted(model_df["gen"].tolist())
        assert generations[-2:] == [3, 4]


class TestLinearExpressionEdgeCases:
    """Edge cases for linear expression model integration."""

    def test_linear_expression_negative_slope_with_positive_tf(self):
        """LinearExpression with negative slope and positive tf.

        Rationale: Negative slope means repression; should clamp to [0, inf).
        """
        linear_model = LinearExpression(slope=-1.0, intercept=0.5)
        conditions = Conditions(tf_concentration=1.0)

        expr = linear_model.compute(conditions)
        # Result = -1.0 * 1.0 + 0.5 = -0.5, clamped to 0.0
        assert expr == pytest.approx(0.0)

    def test_linear_expression_with_zero_intercept(self):
        """LinearExpression with zero intercept.

        Rationale: Basal expression is zero.
        """
        linear_model = LinearExpression(slope=2.0, intercept=0.0)
        conditions = Conditions(tf_concentration=3.0)

        expr = linear_model.compute(conditions)
        # Result = 2.0 * 3.0 + 0.0 = 6.0
        assert expr == pytest.approx(6.0)
