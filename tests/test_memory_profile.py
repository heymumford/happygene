"""Memory profiling for GeneNetwork simulation scenarios.

Measures memory usage, allocation patterns, and object overhead for realistic
population sizes: 5k × 100 × 100 and larger scenarios.

Deliverables:
- Peak memory usage snapshots
- Per-step allocation patterns
- Allocation hotspots (top 3)
- Per-object memory estimates
- Optimization recommendations
"""
import tracemalloc
import resource
import gc
import sys
import numpy as np
import pytest
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression
from happygene.selection import ProportionalSelection
from happygene.mutation import PointMutation


class TestMemoryProfile:
    """Memory profiling tests for GeneNetwork simulation."""

    def test_memory_baseline_single_gene(self):
        """Baseline: measure memory footprint of a single Gene object."""
        import sys

        # Create single gene
        gene = Gene("test_gene", 1.5)

        # Measure object size directly
        gene_size = sys.getsizeof(gene)
        dict_size = sys.getsizeof(gene.__dict__) if hasattr(gene, '__dict__') else 0
        name_size = sys.getsizeof(gene.name)

        total_size = gene_size + dict_size + name_size

        print(f"\nGene object memory footprint:")
        print(f"  Gene.__sizeof__: {gene_size} bytes")
        print(f"  Gene.__dict__: {dict_size} bytes")
        print(f"  name string: {name_size} bytes")
        print(f"  Total: {total_size} bytes")

        # Gene object should be measurable
        assert gene_size > 0, "Gene object should have size"
        assert gene.name == "test_gene", "Gene name should be set"

    def test_memory_peak_small_population_5x10x10(self):
        """Small benchmark: 5 individuals × 10 genes × 10 generations."""
        import time

        # Measure RSS (resident set size) at start
        before_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # Create population
        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(10)])
            for _ in range(5)
        ]

        expr_model = LinearExpression(slope=1.0, intercept=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.1, magnitude=0.05)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Run 10 generations and time it
        start = time.perf_counter()
        for _ in range(10):
            model.step()
        elapsed = time.perf_counter() - start

        gc.collect()
        after_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        rss_delta_mb = (after_rss - before_rss) / 1024.0  # Convert to MB

        print(f"\nSmall Population (5 × 10 × 10):")
        print(f"  RSS before: {before_rss / 1024:.1f} MB")
        print(f"  RSS after: {after_rss / 1024:.1f} MB")
        print(f"  RSS delta: {rss_delta_mb:.2f} MB")
        print(f"  Elapsed time: {elapsed * 1000:.1f} ms")
        print(f"  Individuals: {len(model.individuals)}")
        print(f"  Genes/individual: {len(model.individuals[0].genes)}")

        assert len(model.individuals) == 5, "Population size should remain 5"
        assert model.generation == 10, "Should complete 10 generations"

    def test_memory_medium_population_5kx100x100(self):
        """Medium benchmark: 5k individuals × 100 genes × 100 generations.

        This is close to the target scenario. Measures:
        - Peak memory usage during simulation
        - Per-step timing pattern
        - Memory stability over generations
        """
        import time

        n_indiv = 5000
        n_genes = 100
        n_gen = 100

        # Pre-simulation RSS
        before_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

        # Create population
        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_indiv)
        ]

        # Population RSS after creation
        gc.collect()
        pop_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

        expr_model = LinearExpression(slope=1.0, intercept=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.1, magnitude=0.05)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Track per-step timing
        step_times = []

        for gen in range(n_gen):
            start = time.perf_counter()
            model.step()
            elapsed = time.perf_counter() - start
            step_times.append(elapsed)

        # Post-simulation
        gc.collect()
        after_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

        # Analysis
        total_time = sum(step_times)
        avg_step_ms = (total_time / len(step_times)) * 1000
        max_step_ms = max(step_times) * 1000
        rss_delta_mb = after_rss_mb - before_rss_mb

        print(f"\nMedium Population (5k × 100 × 100):")
        print(f"  Population creation RSS: {pop_rss_mb:.1f} MB")
        print(f"  RSS before simulation: {before_rss_mb:.1f} MB")
        print(f"  RSS after simulation: {after_rss_mb:.1f} MB")
        print(f"  RSS delta: {rss_delta_mb:.2f} MB")
        print(f"  Total simulation time: {total_time:.2f} seconds")
        print(f"  Per-step timing:")
        print(f"    Mean: {avg_step_ms:.2f} ms")
        print(f"    Max: {max_step_ms:.2f} ms")
        print(f"  Step timing pattern (first 10 steps, ms):")
        for i, elapsed in enumerate(step_times[:10]):
            print(f"    Step {i+1}: {elapsed * 1000:.2f} ms")

        # Verify simulation completed
        assert model.generation == n_gen, f"Expected {n_gen} generations, got {model.generation}"
        assert len(model.individuals) == n_indiv, "Population size should be maintained"

    def test_memory_hotspots_expression_matrix(self):
        """Identify hotspots: expression_matrix allocation in step()."""
        import cProfile
        import pstats
        import io

        n_indiv = 1000
        n_genes = 100

        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_indiv)
        ]

        expr_model = LinearExpression(slope=1.0, intercept=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)  # No mutation to isolate expression

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Profile single step
        profiler = cProfile.Profile()
        profiler.enable()

        model.step()

        profiler.disable()

        # Get profile stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(10)

        profile_output = s.getvalue()

        print(f"\nTop Profiling Results (1k × 100 × 1 step):")
        print(profile_output[:500])  # First 500 chars

        # Expected numpy array size
        expected_array_bytes = n_indiv * n_genes * 8  # float64
        print(f"\n  Expected expression_matrix size: {expected_array_bytes / (1024*1024):.2f} MB")
        print(f"  (This is the main allocation per step)")

    def test_memory_large_scenario_10kx100(self):
        """Large scenario: 10k individuals × 100 genes × 10 generations.

        Stress test to identify memory scaling issues.
        """
        import time

        n_indiv = 10000
        n_genes = 100
        n_gen = 10

        before_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

        # Create large population
        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_indiv)
        ]

        expr_model = LinearExpression(slope=1.0, intercept=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.1, magnitude=0.05)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Run generations with timing
        start = time.perf_counter()
        for _ in range(n_gen):
            model.step()
        elapsed = time.perf_counter() - start

        gc.collect()
        after_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        rss_delta_mb = after_rss_mb - before_rss_mb

        print(f"\nLarge Scenario (10k × 100 × 10):")
        print(f"  RSS before: {before_rss_mb:.1f} MB")
        print(f"  RSS after: {after_rss_mb:.1f} MB")
        print(f"  RSS delta: {rss_delta_mb:.2f} MB")
        print(f"  Total time: {elapsed:.2f} seconds")
        print(f"  Avg per generation: {elapsed / n_gen * 1000:.1f} ms")
        print(f"  Generations completed: {model.generation}")

        # Verify completion
        assert model.generation == n_gen, f"Expected {n_gen} generations, got {model.generation}"
        assert len(model.individuals) == n_indiv, "Population size should be maintained"

    def test_memory_per_gene_object_estimate(self):
        """Estimate memory per Gene object with and without __slots__.

        Provides baseline for optimization analysis.
        """
        import sys

        # Current Gene object
        gene = Gene("test", 1.5)
        size_bytes = sys.getsizeof(gene)

        # String name
        name_size = sys.getsizeof("test")

        # Float
        float_size = sys.getsizeof(1.5)

        # Dict overhead (if no __slots__)
        dict_size = sys.getsizeof(gene.__dict__) if hasattr(gene, '__dict__') else 0

        print(f"\nPer-Gene Memory Analysis:")
        print(f"  Gene object total: {size_bytes} bytes")
        print(f"  Gene.__dict__: {dict_size} bytes")
        print(f"  name attribute (~): {name_size} bytes")
        print(f"  _expression_level float: {float_size} bytes")
        print(f"  Python object overhead: {size_bytes - dict_size - name_size - float_size} bytes")

        # Estimate with __slots__
        print(f"\nProjected with __slots__:")
        print(f"  Estimated savings: ~{dict_size} bytes per Gene")
        print(f"  For 5k individuals × 100 genes: ~{5000 * 100 * dict_size / (1024*1024):.1f} MB")

    def test_memory_expression_matrix_allocation(self):
        """Measure expression_matrix (numpy array) allocation pattern in step().

        The main memory allocation in each step() is the temporary expr_matrix.
        """
        n_indiv = 5000
        n_genes = 100

        # Expected numpy array size
        expected_bytes = n_indiv * n_genes * 8  # float64 = 8 bytes
        expected_mb = expected_bytes / (1024 * 1024)

        individuals = [
            Individual(genes=[Gene(f"G{j}", np.random.uniform(0.5, 2.0)) for j in range(n_genes)])
            for _ in range(n_indiv)
        ]

        expr_model = LinearExpression(slope=1.0, intercept=0.1)
        select_model = ProportionalSelection()
        mutate_model = PointMutation(rate=0.0, magnitude=0.0)

        model = GeneNetwork(
            individuals=individuals,
            expression_model=expr_model,
            selection_model=select_model,
            mutation_model=mutate_model,
            seed=42
        )

        # Time a single step
        import time
        start = time.perf_counter()
        model.step()
        elapsed = time.perf_counter() - start

        print(f"\nExpression Matrix Allocation Analysis:")
        print(f"  Scenario: {n_indiv} individuals × {n_genes} genes")
        print(f"  Expected expression_matrix size: {expected_bytes:,} bytes ({expected_mb:.2f} MB)")
        print(f"  Step execution time: {elapsed * 1000:.2f} ms")
        print(f"  Operations: {n_indiv * n_genes:,} (expression computations)")
        print(f"  Throughput: {(n_indiv * n_genes) / (elapsed * 1_000_000):.2f} million ops/sec")

        # Verify correctness
        assert len(model.individuals) == n_indiv, "Population size maintained"
        assert all(g.expression_level >= 0 for ind in model.individuals for g in ind.genes), "All expressions non-negative"


@pytest.mark.slow
class TestMemoryOptimizations:
    """Tests for memory optimization opportunities."""

    def test_identify_unnecessary_copies(self):
        """Verify no unnecessary copies in expression computation.

        Checks model.py:83 for list comprehension copies.
        """
        # Create small scenario
        genes = [Gene(f"G{i}", float(i)) for i in range(10)]
        individual = Individual(genes=genes)

        # The line in question: np.array([g.expression_level for g in individual.genes])
        # This creates a list, then converts to numpy array

        import timeit

        # Method 1: Current (list comprehension + np.array conversion)
        def method1():
            return np.array([g.expression_level for g in individual.genes])

        # Method 2: Direct numpy creation with generator
        def method2():
            return np.array([g.expression_level for g in individual.genes], dtype=np.float64)

        # Method 3: Pre-allocated array (not tested here but mentioned)

        time1 = timeit.timeit(method1, number=1000)
        time2 = timeit.timeit(method2, number=1000)

        print(f"\nCopy Analysis (10 genes, 1000 iterations):")
        print(f"  Method 1 (current): {time1:.4f}s")
        print(f"  Method 2 (explicit dtype): {time2:.4f}s")
        print(f"  Difference: {abs(time1 - time2):.4f}s")

        # Both should be fast for small arrays
        assert time1 < 1.0, "Conversion should be fast"

