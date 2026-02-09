#!/usr/bin/env python
"""Benchmark vectorization improvements in selection phase.

Measures performance of different selection models before/after vectorization.
"""
import time
import numpy as np
from happygene.model import GeneNetwork
from happygene.entities import Individual, Gene
from happygene.selection import (
    ProportionalSelection,
    ThresholdSelection,
    EpistaticFitness,
    MultiObjectiveSelection,
)
from happygene.expression import ConstantExpression
from happygene.mutation import PointMutation


def benchmark_selection_model(
    selection_model, n_individuals=1000, n_genes=100, n_steps=100
):
    """Benchmark a specific selection model over multiple steps.

    Parameters
    ----------
    selection_model : SelectionModel
        The selection model to benchmark.
    n_individuals : int
        Number of individuals in population.
    n_genes : int
        Number of genes per individual.
    n_steps : int
        Number of simulation steps to run.

    Returns
    -------
    dict
        Dictionary with timing metrics.
    """
    # Create population
    individuals = [
        Individual([Gene(f"g{j}", np.random.uniform(0, 1)) for j in range(n_genes)])
        for _ in range(n_individuals)
    ]

    # Create model
    model = GeneNetwork(
        individuals=individuals,
        expression_model=ConstantExpression(level=0.5),
        selection_model=selection_model,
        mutation_model=PointMutation(rate=0.01, magnitude=0.1),
        seed=42,
    )

    # Warm up
    for _ in range(5):
        model.step()

    # Benchmark
    start = time.perf_counter()
    for _ in range(n_steps):
        model.step()
    elapsed = time.perf_counter() - start

    avg_step_time = elapsed / n_steps
    steps_per_sec = n_steps / elapsed

    return {
        "model": selection_model.__class__.__name__,
        "n_individuals": n_individuals,
        "n_genes": n_genes,
        "n_steps": n_steps,
        "total_time": elapsed,
        "avg_step_time_ms": avg_step_time * 1000,
        "steps_per_sec": steps_per_sec,
    }


def main():
    """Run benchmarks for all selection models."""
    print("=" * 80)
    print("VECTORIZATION CYCLE 3: Selection Phase Performance")
    print("=" * 80)
    print()

    results = []

    # Benchmark each selection model
    selectors = [
        ProportionalSelection(),
        ThresholdSelection(threshold=0.5),
        EpistaticFitness(np.eye(100) * 0.1),
        MultiObjectiveSelection([1.0] * 100),
    ]

    for selector in selectors:
        print(f"Benchmarking {selector.__class__.__name__}...")
        result = benchmark_selection_model(selector, n_individuals=1000, n_genes=100, n_steps=100)
        results.append(result)
        print(f"  {result['avg_step_time_ms']:.2f} ms/step ({result['steps_per_sec']:.1f} steps/sec)")

    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()

    # Print table
    print(f"{'Model':<30} {'Avg Step Time (ms)':<25} {'Steps/sec':<15}")
    print("-" * 70)
    for result in results:
        print(
            f"{result['model']:<30} {result['avg_step_time_ms']:<25.2f} {result['steps_per_sec']:<15.1f}"
        )

    # Calculate improvement vs ProportionalSelection (baseline)
    baseline = results[0]["avg_step_time_ms"]
    print()
    print("Relative to ProportionalSelection (baseline):")
    print("-" * 70)
    for result in results:
        ratio = result["avg_step_time_ms"] / baseline
        pct = (ratio - 1) * 100
        direction = "slower" if pct > 0 else "faster"
        print(f"{result['model']:<30} {ratio:.2f}x ({pct:+.1f}% {direction})")

    print()
    print("Note: All selection models now use compute_fitness_batch().")
    print("      This is a uniform vectorization across all types.")


if __name__ == "__main__":
    main()
