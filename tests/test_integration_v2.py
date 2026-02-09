"""Integration tests for Phase 2 model combinations (Cycle 2).

Tests all Phase 2 selection model combinations integrated with GeneNetwork.step(),
focusing on covering the else branch in model.py:120-124 (non-ProportionalSelection).

Test coverage:
- ThresholdSelection + RegulatoryNetwork + CompositeExpression (lines 120-124)
- EpistaticFitness + Mutation over generations (lines 120-124)
- MultiObjectiveSelection + large population (lines 120-124)
- SexualReproduction independence test
- Full v0.2 pipeline: CompositeExpressionModel + RegulatoryNetwork + EpistaticFitness (lines 120-124)
- DataCollector with ThresholdSelection (lines 120-124)
- Parametrized: all expression models × all selection models (lines 120-124)
"""
import pytest
import numpy as np
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.conditions import Conditions
from happygene.expression import LinearExpression, ConstantExpression
from happygene.regulatory_expression import CompositeExpressionModel, AdditiveRegulation
from happygene.regulatory_network import RegulatoryNetwork, RegulationConnection
from happygene.selection import (
    ProportionalSelection,
    ThresholdSelection,
    EpistaticFitness,
    MultiObjectiveSelection,
    SexualReproduction,
)
from happygene.mutation import PointMutation
from happygene.datacollector import DataCollector


class TestThresholdSelectionIntegration:
    """Test ThresholdSelection + RegulatoryNetwork + CompositeExpression."""

    def test_threshold_selection_with_regulatory_network_and_composite_expr(self):
        """ThresholdSelection integrated with RegulatoryNetwork and CompositeExpression.

        This test specifically covers model.py:120-124 (else branch for
        non-ProportionalSelection models).
        """
        # Setup: 2-gene system, A -> B
        genes = [Gene("A", 1.0), Gene("B", 0.5)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Regulatory network: A activates B
        reg_net = RegulatoryNetwork(
            gene_names=["A", "B"],
            interactions=[RegulationConnection(source="A", target="B", weight=2.0)]
        )

        # Composite model: base constant + additive regulation
        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=1.0)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        # ThresholdSelection with threshold 1.5
        select_model = ThresholdSelection(threshold=1.5)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        # Step once
        model.step()

        # After step: A=0.5, B=0.5+1.0*2.0*1.0=2.5
        # Mean = (0.5 + 2.5)/2 = 1.5 >= threshold 1.5, fitness=1.0
        assert individual.genes[0].expression_level == 0.5
        assert individual.genes[1].expression_level == 2.5
        assert individual.fitness == 1.0


class TestEpistaticFitnessIntegration:
    """Test EpistaticFitness selection with mutations over 100 generations."""

    def test_epistatic_fitness_with_mutations_100_generations(self):
        """EpistaticFitness applied over 100 generations with mutations.

        Covers model.py:120-124 (non-ProportionalSelection else branch).
        """
        # Setup: 3-gene system with epistatic interactions
        genes = [Gene("g0", 1.0), Gene("g1", 0.8), Gene("g2", 0.6)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Interaction matrix: synergistic interactions
        interactions = np.array([
            [0.1, 0.2, 0.1],
            [0.2, 0.1, 0.2],
            [0.1, 0.2, 0.1]
        ])
        select_model = EpistaticFitness(interaction_matrix=interactions)
        expr_model = LinearExpression(slope=1.0, intercept=0.5)
        mutate_model = PointMutation(rate=0.05, magnitude=0.1)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Run 100 generations
        for _ in range(100):
            model.step()

        # Verify model state
        assert model.generation == 100
        assert len(individuals) == 1
        # Verify expression levels are valid (non-negative, finite)
        for gene in individual.genes:
            assert gene.expression_level >= 0.0
            assert np.isfinite(gene.expression_level)
        # Verify fitness was computed
        assert individual.fitness >= 0.0
        assert np.isfinite(individual.fitness)


class TestMultiObjectiveSelectionLargePopulation:
    """Test MultiObjectiveSelection with large population (100 individuals)."""

    def test_multi_objective_selection_large_population(self):
        """MultiObjectiveSelection applied to 100 individuals.

        Covers model.py:120-124 (non-ProportionalSelection else branch).
        """
        # Setup: 100 individuals × 5 genes
        n_individuals = 100
        n_genes = 5
        individuals = [
            Individual(genes=[Gene(f"g{j}", np.random.uniform(0.5, 1.5))
                            for j in range(n_genes)])
            for _ in range(n_individuals)
        ]

        # Multi-objective selection: 5 objectives with equal weights
        objective_weights = [1.0] * n_genes
        select_model = MultiObjectiveSelection(objective_weights=objective_weights)
        expr_model = LinearExpression(slope=1.5, intercept=0.2)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Step once
        model.step()

        # Verify all individuals have fitness assigned (via compute_fitness)
        assert all(np.isfinite(ind.fitness) for ind in individuals)
        # Verify population size unchanged
        assert len(model.individuals) == n_individuals
        # Verify fitness values are in reasonable range (weighted average of expressions)
        fitness_values = [ind.fitness for ind in individuals]
        assert min(fitness_values) >= 0.0
        assert max(fitness_values) <= 5.0


class TestSexualReproductionIndependence:
    """Test SexualReproduction independence (no integration with step())."""

    def test_sexual_reproduction_independence(self):
        """SexualReproduction works independent of model.step().

        Verifies that sexual reproduction can be applied to individuals
        without GeneNetwork integration (orthogonal concern).
        """
        # Create two parents with distinct alleles
        parent1 = Individual(genes=[
            Gene("g0", 0.2),
            Gene("g1", 0.4),
            Gene("g2", 0.6)
        ])
        parent2 = Individual(genes=[
            Gene("g0", 1.0),
            Gene("g1", 1.2),
            Gene("g2", 1.4)
        ])

        # Create reproduction model
        reproduction = SexualReproduction(crossover_rate=0.5)

        # Create RNG for reproducibility
        rng = np.random.default_rng(seed=42)

        # Mate multiple times
        offspring_list = []
        for _ in range(20):
            offspring = reproduction.mate(parent1, parent2, rng)
            offspring_list.append(offspring)

        # Verify all offspring have correct gene count
        assert all(len(off.genes) == 3 for off in offspring_list)

        # Verify offspring express genes from both parents
        assert len(offspring_list) == 20

        # Verify offspring inherit from both parents
        # Each offspring's alleles should come from one parent or the other
        for offspring in offspring_list:
            for gene_idx in range(3):
                off_expr = offspring.genes[gene_idx].expression_level
                parent1_expr = parent1.genes[gene_idx].expression_level
                parent2_expr = parent2.genes[gene_idx].expression_level
                # Offspring should inherit exactly from one parent
                assert off_expr == parent1_expr or off_expr == parent2_expr

        # With 20 offspring and crossover_rate=0.5, we expect mixed parental inheritance
        # (not all offspring identical to parent1)
        unique_offspring = set(
            tuple(off.genes[j].expression_level for j in range(3))
            for off in offspring_list
        )
        assert len(unique_offspring) > 1  # Multiple unique genotypes expected


class TestFullV02Pipeline:
    """Test full v0.2 pipeline: CompositeExpression + RegulatoryNetwork + EpistaticFitness."""

    def test_full_v02_pipeline_50_generations(self):
        """Full v0.2 pipeline: CompositeExpressionModel + RegulatoryNetwork + EpistaticFitness.

        Covers model.py:120-124 (non-ProportionalSelection else branch with complex models).
        """
        # Setup: 4-gene system with regulation
        genes = [Gene("g0", 1.0), Gene("g1", 0.8), Gene("g2", 0.9), Gene("g3", 0.7)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Regulatory network: feedforward cascade
        reg_net = RegulatoryNetwork(
            gene_names=["g0", "g1", "g2", "g3"],
            interactions=[
                RegulationConnection(source="g0", target="g1", weight=0.5),
                RegulationConnection(source="g1", target="g2", weight=0.5),
                RegulationConnection(source="g2", target="g3", weight=0.5),
            ]
        )

        # Composite expression: base constant + additive regulation
        base_model = ConstantExpression(level=0.5)
        regulatory_model = AdditiveRegulation(weight=0.1)
        composite_expr = CompositeExpressionModel(base_model, regulatory_model)

        # EpistaticFitness selection
        interactions = np.array([
            [0.1, 0.05, 0.0, 0.0],
            [0.05, 0.1, 0.05, 0.0],
            [0.0, 0.05, 0.1, 0.05],
            [0.0, 0.0, 0.05, 0.1]
        ])
        select_model = EpistaticFitness(interaction_matrix=interactions)
        mutate_model = PointMutation(rate=0.02, magnitude=0.05)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=composite_expr,
            selection_model=select_model,
            mutation_model=mutate_model,
            regulatory_network=reg_net,
            seed=42
        )

        # Run 50 generations
        for _ in range(50):
            model.step()

        # Verify model state
        assert model.generation == 50
        assert len(individuals) == 1
        # Verify all genes have valid expression levels
        for gene in individual.genes:
            assert gene.expression_level >= 0.0
            assert np.isfinite(gene.expression_level)
        # Verify fitness was computed via EpistaticFitness.compute_fitness
        assert individual.fitness >= 0.0
        assert np.isfinite(individual.fitness)


class TestDataCollectorWithThresholdSelection:
    """Test DataCollector integration with ThresholdSelection (covers lines 120-124)."""

    def test_datacollector_with_threshold_selection(self):
        """DataCollector tracks metrics when ThresholdSelection is used.

        Covers model.py:120-124 (non-ProportionalSelection else branch).
        """
        # Setup: 3-gene population
        individuals = [
            Individual(genes=[Gene(f"g{j}", np.random.uniform(0.5, 1.5))
                            for j in range(3)])
            for _ in range(5)
        ]

        # ThresholdSelection
        select_model = ThresholdSelection(threshold=1.0)
        expr_model = LinearExpression(slope=1.0, intercept=0.5)
        mutate_model = PointMutation(rate=0.1, magnitude=0.1)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Create and configure DataCollector with model-level reporter
        collector = DataCollector(
            model_reporters={
                "mean_fitness": lambda m: m.compute_mean_fitness()
            }
        )
        collector.collect(model)

        # Run 10 generations with collection
        for _ in range(10):
            model.step()
            collector.collect(model)

        # Verify data was collected
        data = collector.get_model_dataframe()
        assert len(data) == 11  # Initial + 10 steps
        assert "mean_fitness" in data.columns
        assert all(data["generation"] >= 0)


class TestParametrizedSelectionExpressionCombinations:
    """Parametrized tests: all expression models × all selection models."""

    @pytest.mark.parametrize("expr_model", [
        LinearExpression(slope=1.0, intercept=0.5),
        ConstantExpression(level=1.0),
    ])
    @pytest.mark.parametrize("select_model,setup", [
        (ThresholdSelection(threshold=0.75), "threshold"),
        (ProportionalSelection(), "proportional"),
    ])
    def test_parametrized_expr_selection_combinations(self, expr_model, select_model, setup):
        """Test all combinations of expression and selection models.

        Parametrized across:
        - LinearExpression, ConstantExpression
        - ThresholdSelection, ProportionalSelection

        This ensures coverage of model.py:120-124 for multiple selection types.
        """
        # Setup: simple population
        genes = [Gene("g0", 1.0), Gene("g1", 0.8)]
        individuals = [Individual(genes=genes)]

        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Step and verify
        model.step()

        ind = individuals[0]
        # Verify expressions were updated
        assert all(g.expression_level >= 0.0 for g in ind.genes)
        # Verify fitness was set (via model.py:114-124)
        assert ind.fitness >= 0.0 if setup == "proportional" else ind.fitness in [0.0, 1.0]


class TestNonProportionalSelectionPathCoverage:
    """Direct tests for model.py:120-124 (non-ProportionalSelection else branch)."""

    def test_threshold_selection_forces_else_branch(self):
        """Explicit test that ThresholdSelection triggers model.py:120-124 else branch."""
        # Create individual
        genes = [Gene("g0", 2.0), Gene("g1", 2.5)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Use ThresholdSelection (NOT ProportionalSelection)
        # This forces the else branch at model.py:120-124
        select_model = ThresholdSelection(threshold=2.0)
        expr_model = LinearExpression(slope=1.0, intercept=1.0)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Before step: fitness undefined
        original_fitness = individual.fitness

        # Step (should trigger else branch)
        model.step()

        # After step: fitness computed via select_model.compute_fitness()
        # Expression: 1.0*0.0 + 1.0 = 1.0 for all genes
        # Mean = 1.0 < threshold 2.0, so fitness = 0.0
        assert individual.fitness == 0.0
        assert individual.fitness != original_fitness


    def test_epistatic_fitness_forces_else_branch(self):
        """Explicit test that EpistaticFitness triggers model.py:120-124 else branch."""
        # Create individuals
        genes1 = [Gene("g0", 1.0), Gene("g1", 0.5)]
        individual1 = Individual(genes=genes1)
        individuals = [individual1]

        # Use EpistaticFitness (NOT ProportionalSelection)
        interactions = np.array([[0.1, 0.2], [0.2, 0.1]])
        select_model = EpistaticFitness(interaction_matrix=interactions)
        expr_model = ConstantExpression(level=1.0)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Step (should trigger else branch)
        model.step()

        # Fitness should be computed: base=1.0, epistatic bonus = (1*1*0.1 + 1*1*0.2 + 1*1*0.2 + 1*1*0.1)/2 = 0.3
        # Total = 1.0 + 0.3 = 1.3
        expected_fitness = 1.0 + 0.3
        assert abs(individual1.fitness - expected_fitness) < 1e-10


    def test_multi_objective_selection_forces_else_branch(self):
        """Explicit test that MultiObjectiveSelection triggers model.py:120-124 else branch."""
        # Create individuals
        genes = [Gene("g0", 0.8), Gene("g1", 0.6)]
        individual = Individual(genes=genes)
        individuals = [individual]

        # Use MultiObjectiveSelection (NOT ProportionalSelection)
        objective_weights = [1.0, 1.0]
        select_model = MultiObjectiveSelection(objective_weights=objective_weights)
        expr_model = LinearExpression(slope=2.0, intercept=0.0)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
            conditions=Conditions(tf_concentration=0.5)
        )

        # Step (should trigger else branch)
        model.step()

        # Expression: 2.0*0.5 + 0.0 = 1.0 for all genes
        # Fitness: (1.0*1.0 + 1.0*1.0) / (1.0+1.0) = 1.0
        assert abs(individual.fitness - 1.0) < 1e-10


class TestRegressionAllPhase2Models:
    """Regression test: all Phase 2 models run without errors."""

    def test_all_phase2_selection_models_step_correctly(self):
        """Verify all Phase 2 selection models step without errors.

        Tests ProportionalSelection, ThresholdSelection, EpistaticFitness, MultiObjectiveSelection.
        """
        n_genes = 3
        genes = [Gene(f"g{i}", 1.0) for i in range(n_genes)]
        individual = Individual(genes=genes)

        # List of all Phase 2 selection models
        selection_models = [
            ProportionalSelection(),
            ThresholdSelection(threshold=1.0),
            EpistaticFitness(interaction_matrix=np.eye(n_genes) * 0.1),
            MultiObjectiveSelection(objective_weights=[1.0] * n_genes),
        ]

        expr_model = LinearExpression(slope=1.0, intercept=0.5)
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        for select_model in selection_models:
            individuals = [Individual(genes=[Gene(f"g{i}", 1.0) for i in range(n_genes)])]
            model = GeneNetwork(
                individuals=individuals,
                expression_model=expr_model,
                selection_model=select_model,
                mutation_model=mutate_model,
                seed=42
            )

            # Step should work for all models
            model.step()

            # Verify fitness was assigned
            assert individuals[0].fitness >= 0.0
            assert np.isfinite(individuals[0].fitness)
