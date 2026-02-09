"""Performance benchmarks for large-scale simulations."""

import pytest

from happygene.datacollector import DataCollector
from happygene.entities import Gene, Individual
from happygene.expression import ConstantExpression
from happygene.model import GeneNetwork
from happygene.mutation import PointMutation
from happygene.selection import ProportionalSelection


class TestPerformanceBenchmarks:
    """Benchmarks for simulation performance at scale."""

    @pytest.mark.slow
    def test_benchmark_500k_gene_rows(self):
        """Benchmark: 100 individuals, 50 genes, 100 generations → 500k rows.

        Rationale: Verify that DataCollector can handle large-scale data
        collection without performance degradation.

        Target: Completes without memory issues.
        """
        # Setup: 100 individuals, 50 genes each
        individuals = [
            Individual([Gene(f"gene_{i}_{j}", 1.0) for j in range(50)])
            for i in range(100)
        ]

        # Models
        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.3, magnitude=0.1)

        # Create network with data collection
        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # DataCollector with full 3-tier reporters
        collector = DataCollector(
            model_reporters={"generation": lambda m: m.generation},
            individual_reporters={"fitness": lambda ind: ind.fitness},
            gene_reporters={"expression_level": lambda gene: gene.expression_level},
        )

        # Run simulation: 100 individuals, 50 genes, 100 generations
        # Expected gene records: 100 indiv * 50 genes * 100 gen = 500,000 rows
        for gen in range(100):
            network.step()
            collector.collect(network)

        # Verify data was collected
        gene_df = collector.get_gene_dataframe()
        assert len(gene_df) == 500000, f"Expected 500k gene records, got {len(gene_df)}"

        # Verify DataFrames are non-empty
        model_df = collector.get_model_dataframe()
        individual_df = collector.get_individual_dataframe()
        assert len(model_df) == 100, f"Expected 100 model rows, got {len(model_df)}"
        assert (
            len(individual_df) == 10000
        ), f"Expected 10k individual rows, got {len(individual_df)}"

    @pytest.mark.slow
    def test_max_history_bounds_memory(self):
        """Test that max_history parameter prevents memory explosion.

        Rationale: DataCollector.max_history should limit rows to most recent N.

        Setup: Large population, many generations, verify max_history enforcement.
        """
        # Setup: 50 individuals, 20 genes each, 200 generations
        individuals = [
            Individual([Gene(f"gene_{i}_{j}", 1.0) for j in range(20)])
            for i in range(50)
        ]

        expr_model = ConstantExpression(level=1.0)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.2, magnitude=0.1)

        network = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42,
        )

        # Create collector with max_history=1000 (limit memory)
        collector = DataCollector(
            model_reporters={"generation": lambda m: m.generation},
            individual_reporters={"fitness": lambda ind: ind.fitness},
            gene_reporters={"expression_level": lambda gene: gene.expression_level},
            max_history=1000,
        )

        # Run 200 generations
        # Each generation: 1 model + 50 indiv + 1000 genes = 1051 rows
        # If max_history works: rows should be capped at ~1000
        for _ in range(200):
            network.step()
            collector.collect(network)

        # Check that gene dataframe respects max_history
        gene_df = collector.get_gene_dataframe()
        # With max_history=1000, we should have <= 1000 rows per collection
        # Actually max_history limits the total history, so check it's bounded
        assert (
            len(gene_df) <= 1000
        ), f"max_history not enforced: got {len(gene_df)} rows, max should be 1000"

        # Verify generation column shows recent generations
        if len(gene_df) > 0:
            max_gen = gene_df["generation"].max()
            min_gen = gene_df["generation"].min()
            # Should only contain recent generations, not all 200
            gen_span = max_gen - min_gen
            assert (
                gen_span < 200
            ), f"max_history not working: generation span {gen_span} is too large"
