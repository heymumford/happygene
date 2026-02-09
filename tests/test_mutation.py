"""Tests for mutation models."""
import pytest
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
