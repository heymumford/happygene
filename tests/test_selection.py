"""Tests for selection models."""
import pytest
import numpy as np
from happygene.entities import Gene, Individual
from happygene.selection import (
    SelectionModel,
    ProportionalSelection,
    ThresholdSelection,
    SexualReproduction,
    AsexualReproduction,
    EpistaticFitness,
    MultiObjectiveSelection,
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


class TestSexualReproduction:
    """Tests for SexualReproduction model (crossover + mating)."""

    def test_sexual_reproduction_creation(self):
        """SexualReproduction can be instantiated with crossover_rate."""
        selector = SexualReproduction(crossover_rate=0.5)
        assert selector is not None
        assert selector.crossover_rate == 0.5

    def test_sexual_reproduction_default_crossover_rate(self):
        """SexualReproduction defaults to 0.5 crossover rate."""
        selector = SexualReproduction()
        assert selector.crossover_rate == 0.5

    def test_sexual_reproduction_crossover_rate_stored(self):
        """SexualReproduction stores provided crossover_rate."""
        selector = SexualReproduction(crossover_rate=0.8)
        assert selector.crossover_rate == 0.8

    def test_sexual_reproduction_mate_produces_offspring(self):
        """mate() produces offspring with genes from both parents."""
        selector = SexualReproduction(crossover_rate=0.5)
        parent1 = Individual([Gene("g1", 1.0), Gene("g2", 2.0)])
        parent2 = Individual([Gene("g1", 0.5), Gene("g2", 1.5)])

        offspring = selector.mate(parent1, parent2, rng=__import__("numpy").random.default_rng(42))

        # Offspring should have same number of genes as parents
        assert len(offspring.genes) == 2
        # Each gene should have a name and expression
        assert all(gene.name in ["g1", "g2"] for gene in offspring.genes)
        # Expression levels should be non-negative
        assert all(gene.expression_level >= 0 for gene in offspring.genes)

    def test_sexual_reproduction_mate_with_zero_crossover(self):
        """mate() with crossover_rate=0 produces exact copy of parent1."""
        selector = SexualReproduction(crossover_rate=0.0)
        parent1 = Individual([Gene("g1", 1.0), Gene("g2", 2.0)])
        parent2 = Individual([Gene("g1", 0.5), Gene("g2", 1.5)])

        offspring = selector.mate(parent1, parent2, rng=__import__("numpy").random.default_rng(42))

        # With 0 crossover, offspring should match parent1 exactly
        assert len(offspring.genes) == len(parent1.genes)
        for i, gene in enumerate(offspring.genes):
            assert gene.name == parent1.genes[i].name
            assert gene.expression_level == parent1.genes[i].expression_level

    def test_sexual_reproduction_mate_with_full_crossover(self):
        """mate() with crossover_rate=1.0 produces combination from both parents."""
        selector = SexualReproduction(crossover_rate=1.0)
        parent1 = Individual([Gene("g1", 1.0), Gene("g2", 2.0)])
        parent2 = Individual([Gene("g1", 0.5), Gene("g2", 1.5)])

        offspring = selector.mate(parent1, parent2, rng=__import__("numpy").random.default_rng(42))

        # With 1.0 crossover, offspring should have genes mixed from both
        assert len(offspring.genes) == 2
        # Expression levels should come from either parent (0.5 or 1.0 for g1, 1.5 or 2.0 for g2)
        assert all(gene.expression_level >= 0 for gene in offspring.genes)

    def test_sexual_reproduction_mate_multiple_genes(self):
        """mate() handles multiple genes correctly."""
        selector = SexualReproduction(crossover_rate=0.5)
        parent1 = Individual([Gene(f"g{i}", float(i + 1)) for i in range(5)])
        parent2 = Individual([Gene(f"g{i}", float(i + 0.5)) for i in range(5)])

        offspring = selector.mate(parent1, parent2, rng=__import__("numpy").random.default_rng(42))

        assert len(offspring.genes) == 5
        assert all(offspring.genes[i].name == f"g{i}" for i in range(5))

    def test_sexual_reproduction_repr(self):
        """SexualReproduction has informative repr."""
        selector = SexualReproduction(crossover_rate=0.7)
        repr_str = repr(selector)
        assert "SexualReproduction" in repr_str
        assert "0.7" in repr_str


class TestAsexualReproduction:
    """Tests for AsexualReproduction model (cloning)."""

    def test_asexual_reproduction_creation(self):
        """AsexualReproduction can be instantiated."""
        reproducer = AsexualReproduction()
        assert reproducer is not None

    def test_asexual_reproduction_clone_produces_copy(self):
        """clone() produces an exact copy of parent."""
        reproducer = AsexualReproduction()
        parent = Individual([Gene("g1", 1.0), Gene("g2", 2.0)])

        offspring = reproducer.clone(parent)

        # Offspring should be a different object
        assert offspring is not parent
        # But have same genes and expression levels
        assert len(offspring.genes) == len(parent.genes)
        for i, gene in enumerate(offspring.genes):
            assert gene.name == parent.genes[i].name
            assert gene.expression_level == parent.genes[i].expression_level

    def test_asexual_reproduction_clone_single_gene(self):
        """clone() handles single gene correctly."""
        reproducer = AsexualReproduction()
        parent = Individual([Gene("g1", 3.5)])

        offspring = reproducer.clone(parent)

        assert len(offspring.genes) == 1
        assert offspring.genes[0].name == "g1"
        assert offspring.genes[0].expression_level == 3.5

    def test_asexual_reproduction_clone_multiple_genes(self):
        """clone() handles multiple genes correctly."""
        reproducer = AsexualReproduction()
        parent = Individual([Gene(f"g{i}", float(i + 1)) for i in range(5)])

        offspring = reproducer.clone(parent)

        assert len(offspring.genes) == 5
        for i in range(5):
            assert offspring.genes[i].name == f"g{i}"
            assert offspring.genes[i].expression_level == float(i + 1)

    def test_asexual_reproduction_clone_zero_expression(self):
        """clone() handles zero expression levels."""
        reproducer = AsexualReproduction()
        parent = Individual([Gene("g1", 0.0), Gene("g2", 0.0)])

        offspring = reproducer.clone(parent)

        assert offspring.genes[0].expression_level == 0.0
        assert offspring.genes[1].expression_level == 0.0

    def test_asexual_reproduction_clone_empty_individual(self):
        """clone() handles empty individual (no genes)."""
        reproducer = AsexualReproduction()
        parent = Individual([])

        offspring = reproducer.clone(parent)

        assert len(offspring.genes) == 0
        assert offspring is not parent

    def test_asexual_reproduction_repr(self):
        """AsexualReproduction has informative repr."""
        reproducer = AsexualReproduction()
        repr_str = repr(reproducer)
        assert "AsexualReproduction" in repr_str


class TestEpistaticFitness:
    """Tests for EpistaticFitness model (gene-gene interactions)."""

    def test_epistatic_fitness_creation(self):
        """EpistaticFitness can be instantiated with interaction matrix."""
        interactions = np.array([[0.5, 0.3], [0.2, -0.1]])  # 2x2 matrix
        selector = EpistaticFitness(interaction_matrix=interactions)
        assert selector is not None
        assert selector.interaction_matrix.shape == (2, 2)

    def test_epistatic_fitness_requires_square_matrix(self):
        """EpistaticFitness rejects non-square interaction matrices."""
        interactions = np.array([[0.5, 0.3, 0.1], [0.2, -0.1, 0.4]])  # 2x3
        with pytest.raises(ValueError, match="square"):
            EpistaticFitness(interaction_matrix=interactions)

    def test_epistatic_fitness_matrix_size_matches_genes(self):
        """EpistaticFitness validates matrix size matches gene count."""
        genes = [Gene("g0", 1.0), Gene("g1", 0.5)]
        individual = Individual(genes)

        # 3x3 matrix for 2 genes = mismatch
        interactions = np.eye(3)
        selector = EpistaticFitness(interaction_matrix=interactions)

        with pytest.raises(ValueError, match="size"):
            selector.compute_fitness(individual)

    def test_epistatic_fitness_additive_base_plus_interactions(self):
        """EpistaticFitness: fitness = base + epistatic term."""
        # 2 genes, no interactions
        interactions = np.zeros((2, 2))
        selector = EpistaticFitness(interaction_matrix=interactions)

        genes = [Gene("g0", 1.0), Gene("g1", 0.5)]
        individual = Individual(genes)

        # Base fitness = mean(1.0, 0.5) = 0.75, no epistasis = 0
        # Total = 0.75
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(0.75)

    def test_epistatic_fitness_interaction_bonus(self):
        """EpistaticFitness includes gene-gene interaction term."""
        # 2x2 interaction matrix
        interactions = np.array([
            [0.1, 0.2],  # g0-g0 bonus=0.1, g0-g1 bonus=0.2
            [0.2, 0.1],  # g1-g0 bonus=0.2, g1-g1 bonus=0.1
        ])
        selector = EpistaticFitness(interaction_matrix=interactions)

        genes = [Gene("g0", 1.0), Gene("g1", 1.0)]
        individual = Individual(genes)

        # Base = 1.0
        # Epistasis = sum of all pairwise products weighted by interaction matrix
        # = (1.0*1.0*0.1 + 1.0*1.0*0.2 + 1.0*1.0*0.2 + 1.0*1.0*0.1) / 2 = 0.6 / 2 = 0.3
        # Total = 1.0 + 0.3 = 1.3
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(1.3)

    def test_epistatic_fitness_synergistic_interaction(self):
        """EpistaticFitness models synergistic interactions (g0 AND g1 high)."""
        interactions = np.array([
            [0.1, 0.4],
            [0.4, 0.1],
        ])
        selector = EpistaticFitness(interaction_matrix=interactions)

        # Both genes high
        genes = [Gene("g0", 1.0), Gene("g1", 1.0)]
        individual = Individual(genes)

        # Base = 1.0
        # Epistasis = (1.0*1.0*0.1 + 1.0*1.0*0.4 + 1.0*1.0*0.4 + 1.0*1.0*0.1) / 2 = 1.0 / 2 = 0.5
        # Total = 1.0 + 0.5 = 1.5
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(1.5)

    def test_epistatic_fitness_repr(self):
        """EpistaticFitness has informative repr."""
        interactions = np.array([[0.5, 0.3], [0.2, -0.1]])
        selector = EpistaticFitness(interaction_matrix=interactions)
        repr_str = repr(selector)
        assert "EpistaticFitness" in repr_str


class TestMultiObjectiveSelection:
    """Tests for MultiObjectiveSelection model (weighted objectives)."""

    def test_multi_objective_selection_creation(self):
        """MultiObjectiveSelection can be instantiated with objective weights."""
        weights = [1.0, 1.0, 0.5]  # Three objectives
        selector = MultiObjectiveSelection(objective_weights=weights)
        assert selector is not None
        assert len(selector.objective_weights) == 3

    def test_multi_objective_selection_requires_non_negative_weights(self):
        """MultiObjectiveSelection rejects negative weights."""
        weights = [1.0, -0.5, 0.5]  # Negative weight invalid
        with pytest.raises(ValueError, match="non-negative"):
            MultiObjectiveSelection(objective_weights=weights)

    def test_multi_objective_selection_single_objective(self):
        """MultiObjectiveSelection with one objective: fitness = expr."""
        weights = [1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        genes = [Gene("g0", 0.5)]
        individual = Individual(genes)

        # Single objective = expr value
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(0.5)

    def test_multi_objective_selection_equal_weights(self):
        """MultiObjectiveSelection with equal weights: fitness = mean expression."""
        weights = [1.0, 1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        genes = [Gene("g0", 0.6), Gene("g1", 0.4)]
        individual = Individual(genes)

        # Weighted mean = (1.0*0.6 + 1.0*0.4) / 2.0 = 0.5
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(0.5)

    def test_multi_objective_selection_weighted_objectives(self):
        """MultiObjectiveSelection applies weights to objectives."""
        # g0 twice as important as g1
        weights = [2.0, 1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        genes = [Gene("g0", 1.0), Gene("g1", 0.0)]
        individual = Individual(genes)

        # Weighted mean = (2.0*1.0 + 1.0*0.0) / (2.0 + 1.0) = 2.0/3.0
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(2.0 / 3.0)

    def test_multi_objective_selection_three_objectives(self):
        """MultiObjectiveSelection handles three objectives correctly."""
        weights = [1.0, 1.0, 1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        genes = [Gene("g0", 0.3), Gene("g1", 0.5), Gene("g2", 0.7)]
        individual = Individual(genes)

        # Weighted mean = (0.3 + 0.5 + 0.7) / 3 = 1.5 / 3 = 0.5
        fitness = selector.compute_fitness(individual)
        assert fitness == pytest.approx(0.5)

    def test_multi_objective_selection_all_zero_expression(self):
        """MultiObjectiveSelection handles all-zero individual."""
        weights = [1.0, 1.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        genes = [Gene("g0", 0.0), Gene("g1", 0.0)]
        individual = Individual(genes)

        fitness = selector.compute_fitness(individual)
        assert fitness == 0.0

    def test_multi_objective_selection_zero_weights(self):
        """MultiObjectiveSelection with all-zero weights returns 0."""
        weights = [0.0, 0.0]
        selector = MultiObjectiveSelection(objective_weights=weights)

        genes = [Gene("g0", 1.0), Gene("g1", 1.0)]
        individual = Individual(genes)

        fitness = selector.compute_fitness(individual)
        assert fitness == 0.0

    def test_multi_objective_selection_repr(self):
        """MultiObjectiveSelection has informative repr."""
        weights = [1.0, 1.0, 0.5]
        selector = MultiObjectiveSelection(objective_weights=weights)
        repr_str = repr(selector)
        assert "MultiObjectiveSelection" in repr_str
