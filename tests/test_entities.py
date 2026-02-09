"""Tests for Gene and Individual entities."""
import sys
import pytest
from happygene.entities import Gene, Individual


class TestGene:
    """Tests for Gene entity."""

    def test_gene_creation_with_valid_level(self):
        """Gene can be created with a valid expression level."""
        gene = Gene(name="BRCA1", expression_level=5.0)
        assert gene.name == "BRCA1"
        assert gene.expression_level == 5.0

    def test_gene_expression_level_clamped_to_zero(self):
        """Gene expression level cannot be negative; clamped to 0."""
        gene = Gene(name="TP53", expression_level=-2.5)
        assert gene.expression_level == 0.0

    def test_gene_zero_expression_is_valid(self):
        """Gene can have expression level of exactly 0."""
        gene = Gene(name="SILENT", expression_level=0.0)
        assert gene.expression_level == 0.0

    def test_gene_high_expression_is_valid(self):
        """Gene can have high expression level."""
        gene = Gene(name="LOUD", expression_level=100.0)
        assert gene.expression_level == 100.0


class TestIndividual:
    """Tests for Individual entity."""

    def test_individual_creation_empty(self):
        """Individual can be created with empty gene list."""
        ind = Individual(genes=[])
        assert ind.genes == []
        assert ind.fitness == 1.0

    def test_individual_creation_with_genes(self):
        """Individual can be created with genes."""
        genes = [Gene("A", 3.0), Gene("B", 7.0)]
        ind = Individual(genes=genes)
        assert len(ind.genes) == 2
        assert ind.genes[0].name == "A"

    def test_individual_fitness_default(self):
        """Individual fitness defaults to 1.0."""
        ind = Individual(genes=[])
        assert ind.fitness == 1.0

    def test_individual_fitness_settable(self):
        """Individual fitness can be set."""
        ind = Individual(genes=[])
        ind.fitness = 2.5
        assert ind.fitness == 2.5

    def test_individual_mean_expression_empty(self):
        """mean_expression() of individual with no genes returns 0."""
        ind = Individual(genes=[])
        assert ind.mean_expression() == 0.0

    def test_individual_mean_expression_single_gene(self):
        """mean_expression() of individual with one gene returns that level."""
        genes = [Gene("A", 4.0)]
        ind = Individual(genes=genes)
        assert ind.mean_expression() == 4.0

    def test_individual_mean_expression_multiple_genes(self):
        """mean_expression() returns average of all gene expression levels."""
        genes = [Gene("A", 2.0), Gene("B", 8.0), Gene("C", 10.0)]
        ind = Individual(genes=genes)
        assert ind.mean_expression() == 20.0 / 3.0


class TestMemoryOptimization:
    """Tests for memory usage before and after __slots__ optimization."""

    def test_gene_object_size_baseline(self):
        """Gene object baseline size can be measured."""
        gene = Gene("TEST", 1.5)
        size = sys.getsizeof(gene)
        # Before __slots__: typically ~300-400+ bytes depending on Python version
        # Just verify we can measure it and it's reasonable
        assert size > 0
        assert size < 1000  # Should be under 1KB

    def test_individual_object_size_baseline(self):
        """Individual object baseline size can be measured."""
        genes = [Gene(f"G{i}", float(i)) for i in range(100)]
        ind = Individual(genes=genes)
        size = sys.getsizeof(ind)
        # Before __slots__: typically several KB
        assert size > 0
        assert size < 100000  # Should be under 100KB per individual

    def test_gene_slots_defined(self):
        """Gene class has __slots__ defined."""
        assert hasattr(Gene, '__slots__')
        assert 'name' in Gene.__slots__
        assert '_expression_level' in Gene.__slots__

    def test_gene_no_dict_after_slots(self):
        """Gene instances do not have __dict__ after __slots__ optimization."""
        gene = Gene("TEST", 1.5)
        # With __slots__, instances should not have __dict__
        assert not hasattr(gene, '__dict__')

    def test_individual_slots_defined(self):
        """Individual class has __slots__ defined."""
        assert hasattr(Individual, '__slots__')
        assert 'genes' in Individual.__slots__
        assert 'fitness' in Individual.__slots__

    def test_individual_no_dict_after_slots(self):
        """Individual instances do not have __dict__ after __slots__ optimization."""
        ind = Individual(genes=[])
        # With __slots__, instances should not have __dict__
        assert not hasattr(ind, '__dict__')
