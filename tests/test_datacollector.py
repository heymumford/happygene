"""Tests for DataCollector (3-tier reporting)."""

import pytest
import pandas as pd
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.conditions import Conditions
from happygene.expression import LinearExpression
from happygene.selection import ProportionalSelection
from happygene.mutation import PointMutation
from happygene.datacollector import DataCollector


class TestDataCollector:
    """Tests for DataCollector with 3-tier reporters."""

    def test_datacollector_creation_empty(self):
        """DataCollector can be created with empty reporters."""
        collector = DataCollector()
        assert collector is not None

    def test_datacollector_creation_with_reporters(self):
        """DataCollector can be created with reporter dicts."""
        model_reporters = {"generation": lambda m: m.generation}
        individual_reporters = {"fitness": lambda i: i.fitness}
        gene_reporters = {"expression": lambda g: g.expression_level}

        collector = DataCollector(
            model_reporters=model_reporters,
            individual_reporters=individual_reporters,
            gene_reporters=gene_reporters,
        )
        assert collector is not None

    def test_datacollector_collect_model_data(self):
        """collect() records model-level data."""
        model_reporters = {"generation": lambda m: m.generation}
        collector = DataCollector(model_reporters=model_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Collect at generation 0
        collector.collect(network)
        assert len(collector._model_data) == 1

    def test_datacollector_collect_multiple_generations(self):
        """collect() accumulates data across multiple generations."""
        model_reporters = {"generation": lambda m: m.generation}
        collector = DataCollector(model_reporters=model_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Collect over 5 generations
        for _ in range(5):
            collector.collect(network)
            network.step()

        # Should have 5 data points
        assert len(collector._model_data) == 5

    def test_datacollector_get_model_dataframe(self):
        """get_model_dataframe() returns pandas DataFrame."""
        model_reporters = {"generation": lambda m: m.generation}
        collector = DataCollector(model_reporters=model_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        for _ in range(3):
            collector.collect(network)
            network.step()

        df = collector.get_model_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "generation" in df.columns

    def test_datacollector_empty_model_dataframe(self):
        """get_model_dataframe() returns empty DataFrame if no data collected."""
        collector = DataCollector()
        df = collector.get_model_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_datacollector_collect_individual_data(self):
        """collect() records individual-level data."""
        individual_reporters = {"fitness": lambda i: i.fitness}
        collector = DataCollector(individual_reporters=individual_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        collector.collect(network)
        assert len(collector._individual_data) == 1

    def test_datacollector_get_individual_dataframe(self):
        """get_individual_dataframe() returns pandas DataFrame."""
        individual_reporters = {"fitness": lambda i: i.fitness}
        collector = DataCollector(individual_reporters=individual_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        for _ in range(3):
            collector.collect(network)
            network.step()

        df = collector.get_individual_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "fitness" in df.columns

    def test_datacollector_collect_gene_data(self):
        """collect() records gene-level data."""
        gene_reporters = {"expression": lambda g: g.expression_level}
        collector = DataCollector(gene_reporters=gene_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        collector.collect(network)
        assert len(collector._gene_data) == 1

    def test_datacollector_get_gene_dataframe(self):
        """get_gene_dataframe() returns pandas DataFrame."""
        gene_reporters = {"expression": lambda g: g.expression_level}
        collector = DataCollector(gene_reporters=gene_reporters)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        for _ in range(3):
            collector.collect(network)
            network.step()

        df = collector.get_gene_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "expression" in df.columns

    def test_datacollector_max_history_limits_rows(self):
        """max_history parameter limits DataFrame rows to most recent."""
        model_reporters = {"generation": lambda m: m.generation}
        collector = DataCollector(model_reporters=model_reporters, max_history=5)

        genes = [Gene("geneA", 1.0)]
        individual = Individual(genes)
        expr_model = LinearExpression(slope=1.0, intercept=0.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        network = GeneNetwork(
            individuals=[individual],
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Collect 10 times, but max_history=5
        for _ in range(10):
            collector.collect(network)
            network.step()

        df = collector.get_model_dataframe()
        # Should only have last 5 rows
        assert len(df) == 5
