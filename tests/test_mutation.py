"""Tests for mutation models."""

import pytest
import numpy as np
from happygene.entities import Gene, Individual
from happygene.mutation import MutationModel, PointMutation


class TestMutationModel:
    """Tests for MutationModel ABC."""

    def test_mutation_model_cannot_instantiate(self):
        """MutationModel is abstract; cannot instantiate directly."""
        with pytest.raises(TypeError):
            MutationModel()

    def test_mutation_model_subclass_must_implement_mutate(self):
        """Subclass must implement mutate() method."""

        class BrokenMutation(MutationModel):
            pass

        with pytest.raises(TypeError):
            BrokenMutation()


class TestPointMutation:
    """Tests for PointMutation model."""

    def test_point_mutation_creation(self):
        """PointMutation can be created with valid parameters."""
        mutator = PointMutation(rate=0.1, magnitude=0.5)
        assert mutator.rate == 0.1
        assert mutator.magnitude == 0.5

    def test_point_mutation_rate_zero(self):
        """PointMutation with rate=0 is valid (no mutations)."""
        mutator = PointMutation(rate=0.0, magnitude=0.5)
        assert mutator.rate == 0.0

    def test_point_mutation_rate_one(self):
        """PointMutation with rate=1.0 is valid (all genes mutate)."""
        mutator = PointMutation(rate=1.0, magnitude=0.5)
        assert mutator.rate == 1.0

    def test_point_mutation_rate_below_zero_rejected(self):
        """PointMutation rejects rate < 0."""
        with pytest.raises(ValueError):
            PointMutation(rate=-0.1, magnitude=0.5)

    def test_point_mutation_rate_above_one_rejected(self):
        """PointMutation rejects rate > 1."""
        with pytest.raises(ValueError):
            PointMutation(rate=1.1, magnitude=0.5)

    def test_point_mutation_magnitude_zero_allowed(self):
        """PointMutation allows magnitude=0 (no effect)."""
        mutator = PointMutation(rate=0.5, magnitude=0.0)
        assert mutator.magnitude == 0.0

    def test_point_mutation_magnitude_negative_rejected(self):
        """PointMutation rejects magnitude < 0."""
        with pytest.raises(ValueError):
            PointMutation(rate=0.5, magnitude=-0.1)

    def test_point_mutation_repr(self):
        """PointMutation has informative repr."""
        mutator = PointMutation(rate=0.1, magnitude=0.5)
        repr_str = repr(mutator)
        assert "PointMutation" in repr_str

    def test_vectorized_mutation_respects_rate_and_magnitude(self):
        """Vectorized mutation respects rate and magnitude parameters.

        Tests that mutate() applies mutations according to the specified
        rate (probability) and magnitude (perturbation size) using vectorized
        RNG batch calls for improved performance.
        """
        n_genes = 100
        seed = 42
        rate = 0.5
        magnitude = 0.2

        # Create individual
        genes = [Gene(f"g{i}", 1.0) for i in range(n_genes)]
        individual = Individual(genes)
        rng = np.random.default_rng(seed)

        # Apply vectorized mutation
        mutator = PointMutation(rate=rate, magnitude=magnitude)
        mutator.mutate(individual, rng)

        # Verify mutations occurred
        final_levels = [g.expression_level for g in individual.genes]

        # Check that not all genes remained unchanged (rate=0.5 should mutate ~50%)
        unchanged_count = sum(1 for level in final_levels if np.isclose(level, 1.0))
        changed_count = n_genes - unchanged_count

        # With rate=0.5, expect approximately 50% mutations (allow ±20% margin)
        expected_mutations = n_genes * rate
        assert 30 <= changed_count <= 70, \
            f"Expected ~50 mutations, got {changed_count}"

        # Verify all expression levels are non-negative
        for level in final_levels:
            assert level >= 0.0, f"Negative expression level: {level}"

    def test_vectorized_mutation_with_zero_rate(self):
        """Vectorized mutation with rate=0 leaves genes unchanged."""
        n_genes = 50
        seed = 42

        genes = [Gene(f"g{i}", 1.0) for i in range(n_genes)]
        individual = Individual(genes)
        rng = np.random.default_rng(seed)

        mutator = PointMutation(rate=0.0, magnitude=0.5)
        mutator.mutate(individual, rng)

        # No genes should mutate with rate=0
        for gene in individual.genes:
            assert np.isclose(gene.expression_level, 1.0)

    def test_vectorized_mutation_with_rate_one(self):
        """Vectorized mutation with rate=1 mutates all genes."""
        n_genes = 50
        seed = 42

        genes = [Gene(f"g{i}", 1.0) for i in range(n_genes)]
        individual = Individual(genes)
        rng = np.random.default_rng(seed)

        mutator = PointMutation(rate=1.0, magnitude=0.5)
        mutator.mutate(individual, rng)

        # All genes should be mutated (differ from 1.0)
        mutated_count = sum(1 for g in individual.genes if not np.isclose(g.expression_level, 1.0))
        assert mutated_count == n_genes, \
            f"Expected all {n_genes} genes mutated, got {mutated_count}"

    def test_vectorized_mutation_clamps_negative(self):
        """Vectorized mutation clamps expression to [0, inf)."""
        genes = [Gene("g0", 0.1)]
        individual = Individual(genes)
        rng = np.random.default_rng(42)

        # Large negative perturbations with rate=1 should be clamped to 0
        mutator = PointMutation(rate=1.0, magnitude=10.0)

        # Run multiple times to increase chance of large negative perturbations
        for _ in range(10):
            rng = np.random.default_rng(np.random.randint(0, 1000000))
            mutator.mutate(individual, rng)
            assert individual.genes[0].expression_level >= 0.0, \
                f"Expression level not clamped: {individual.genes[0].expression_level}"
