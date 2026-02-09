#!/usr/bin/env python3
"""Quick profiling with smaller scenario to test cProfile early."""

import sys
import time
import cProfile
import pstats
import io
from typing import Dict, List
import numpy as np
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression
from happygene.selection import ThresholdSelection
from happygene.mutation import PointMutation


def create_population(n_individuals: int, n_genes: int, seed: int = 42) -> List[Individual]:
    """Create a population of individuals with genes."""
    np.random.seed(seed)
    individuals = [
        Individual([Gene(f"g{i}", np.random.uniform(0.3, 0.7)) for i in range(n_genes)])
        for _ in range(n_individuals)
    ]
    return individuals


def main() -> int:
    """Run small profiling scenario with cProfile."""
    print("=" * 70)
    print("Quick Performance Profile (5k × 100 × 100)")
    print("=" * 70)

    # Create population
    individuals = create_population(5000, 100, seed=42)

    # Create network
    network = GeneNetwork(
        individuals=individuals,
        expression_model=LinearExpression(slope=1.0, intercept=0.0),
        selection_model=ThresholdSelection(threshold=0.4),
        mutation_model=PointMutation(rate=0.1, magnitude=0.05),
        seed=42
    )

    # Run with cProfile
    print("\nRunning 100 generations with cProfile instrumentation...")
    profiler = cProfile.Profile()
    start_time = time.perf_counter()

    profiler.enable()
    network.run(100)
    profiler.disable()

    elapsed = time.perf_counter() - start_time

    print(f"✓ Completed in {elapsed:.3f}s")
    print(f"  Individuals: 5000")
    print(f"  Genes: 100")
    print(f"  Generations: 100")
    print(f"  Ops/sec: {(5000*100*100)/elapsed:.0f}")

    # Print top functions
    print("\n" + "=" * 70)
    print("Top 20 Functions by Cumulative Time")
    print("=" * 70)
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
