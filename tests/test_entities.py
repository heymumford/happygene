"""Tests for Gene and Individual entities."""

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
