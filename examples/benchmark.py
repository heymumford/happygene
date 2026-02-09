#!/usr/bin/env python3
"""Benchmark harness for happygene performance validation and profiling.

This script measures performance across multiple scenarios to validate that
happygene meets performance targets and to identify optimization opportunities.

Scenarios tested:
- Small (baseline): 100 indiv × 10 genes × 100 gen
- Medium: 1k indiv × 50 genes × 500 gen
- Large: 5k indiv × 100 genes × 1k gen
- Aggressive (Phase 2 target): 10k indiv × 100 genes × 1k gen
- With regulation: 5k indiv × 100 genes × 1k gen + RegulatoryNetwork

Usage:
    python examples/benchmark.py --individuals 10000 --genes 100 --generations 1000
    python examples/benchmark.py --all-scenarios
    python examples/benchmark.py --individuals 5000 --genes 100 --generations 1000 --regulation
"""

import argparse
import sys
import time
import numpy as np
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression, HillExpression
from happygene.selection import ProportionalSelection, ThresholdSelection
from happygene.mutation import PointMutation
from happygene.regulatory_network import RegulatoryNetwork, RegulationConnection


def create_population(n_individuals: int, n_genes: int, seed: int = 42) -> list:
    """Create a population of individuals with genes.

    Parameters
    ----------
    n_individuals : int
        Number of individuals in the population.
    n_genes : int
        Number of genes per individual.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    list
        List of Individual objects.
    """
    np.random.seed(seed)
    individuals = [
        Individual([Gene(f"g{i}", np.random.uniform(0.3, 0.7)) for i in range(n_genes)])
        for _ in range(n_individuals)
    ]
    return individuals


def create_regulatory_network(n_genes: int, density: float = 0.05, seed: int = 42) -> RegulatoryNetwork:
    """Create a sparse regulatory network.

    Parameters
    ----------
    n_genes : int
        Number of genes.
    density : float
        Connection density (probability of edge between any two genes).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    RegulatoryNetwork
        Regulatory network with TF interactions.
    """
    np.random.seed(seed)
    interactions = []
    for src_idx in range(n_genes):
        for tgt_idx in range(n_genes):
            if src_idx != tgt_idx and np.random.random() < density:
                interactions.append(
                    RegulationConnection(
                        source=f"g{src_idx}",
                        target=f"g{tgt_idx}",
                        weight=np.random.uniform(-0.5, 0.5)
                    )
                )
    gene_names = [f"g{i}" for i in range(n_genes)]
    return RegulatoryNetwork(gene_names, interactions)


def benchmark(
    n_individuals: int,
    n_genes: int,
    n_generations: int,
    use_regulation: bool = False,
    use_hill: bool = False,
    seed: int = 42
) -> dict:
    """Run a benchmark scenario and return timing results.

    Parameters
    ----------
    n_individuals : int
        Number of individuals.
    n_genes : int
        Number of genes per individual.
    n_generations : int
        Number of generations to simulate.
    use_regulation : bool
        Whether to include regulatory network.
    use_hill : bool
        Whether to use Hill expression model instead of Linear.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict
        Benchmark results including timing and operations per second.
    """
    # Create population
    individuals = create_population(n_individuals, n_genes, seed=seed)

    # Expression model
    if use_hill:
        expr_model = HillExpression(v_max=1.0, k=0.5, n=2.0)
    else:
        expr_model = LinearExpression(slope=1.0, intercept=0.0)

    # Regulatory network (optional)
    regulatory_network = None
    if use_regulation and n_genes >= 3:
        regulatory_network = create_regulatory_network(n_genes, density=0.05, seed=seed)

    # Create network
    network = GeneNetwork(
        individuals=individuals,
        expression_model=expr_model,
        selection_model=ThresholdSelection(threshold=0.4),
        mutation_model=PointMutation(rate=0.1, magnitude=0.05),
        regulatory_network=regulatory_network,
        seed=seed
    )

    # Benchmark: measure execution time
    start_time = time.perf_counter()
    network.run(n_generations)
    elapsed_seconds = time.perf_counter() - start_time

    # Compute operations metric: individuals * genes * generations
    total_operations = n_individuals * n_genes * n_generations
    ops_per_second = total_operations / elapsed_seconds if elapsed_seconds > 0 else 0.0

    return {
        "n_individuals": n_individuals,
        "n_genes": n_genes,
        "n_generations": n_generations,
        "regulation": use_regulation,
        "hill": use_hill,
        "elapsed_seconds": elapsed_seconds,
        "ops_per_second": ops_per_second,
        "total_operations": total_operations,
    }


def print_results_table(results: list) -> None:
    """Print benchmark results in a formatted table.

    Parameters
    ----------
    results : list
        List of benchmark result dictionaries.
    """
    print("\nBenchmark Results:")
    print("─" * 95)
    print(f"{'Individuals':>12} {'Genes':>8} {'Gens':>8} {'Reg':>5} {'Hill':>5} {'Time (s)':>12} {'Ops/sec':>15}")
    print("─" * 95)

    for result in results:
        regulation_flag = "Y" if result["regulation"] else "N"
        hill_flag = "Y" if result["hill"] else "N"
        print(
            f"{result['n_individuals']:>12} "
            f"{result['n_genes']:>8} "
            f"{result['n_generations']:>8} "
            f"{regulation_flag:>5} "
            f"{hill_flag:>5} "
            f"{result['elapsed_seconds']:>12.3f} "
            f"{result['ops_per_second']:>15.0f}"
        )

    print("─" * 95)


def main() -> int:
    """Run benchmark scenarios and report results.

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Benchmark happygene performance across multiple scenarios"
    )
    parser.add_argument(
        "--individuals",
        type=int,
        default=100,
        help="Number of individuals (default: 100)"
    )
    parser.add_argument(
        "--genes",
        type=int,
        default=10,
        help="Number of genes per individual (default: 10)"
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=100,
        help="Number of generations to simulate (default: 100)"
    )
    parser.add_argument(
        "--regulation",
        action="store_true",
        help="Enable regulatory network with TF interactions"
    )
    parser.add_argument(
        "--hill",
        action="store_true",
        help="Use Hill expression model instead of Linear"
    )
    parser.add_argument(
        "--all-scenarios",
        action="store_true",
        help="Run all predefined benchmark scenarios"
    )

    args = parser.parse_args()

    # Define scenarios
    if args.all_scenarios:
        scenarios = [
            (100, 10, 100, False, False, "Small (baseline)"),
            (1000, 50, 500, False, False, "Medium"),
            (5000, 100, 1000, False, False, "Large"),
            (10000, 100, 1000, False, False, "Aggressive (Phase 2)"),
            (5000, 100, 1000, True, False, "Large + Regulation"),
        ]
    else:
        scenarios = [
            (args.individuals, args.genes, args.generations, args.regulation, args.hill, "Custom")
        ]

    # Run benchmarks
    results = []
    print("=" * 95)
    print("HAPPYGENE Performance Benchmark")
    print("=" * 95)

    for n_indiv, n_genes, n_gen, use_reg, use_hill, scenario_name in scenarios:
        print(
            f"\n[{len(results) + 1}/{len(scenarios)}] Running: {scenario_name}",
            end=" "
        )
        print(
            f"({n_indiv} indiv × {n_genes} genes × {n_gen} gen, "
            f"regulation={use_reg}, hill={use_hill})...",
            end=" ",
            flush=True
        )

        try:
            result = benchmark(n_indiv, n_genes, n_gen, use_reg, use_hill)
            results.append(result)
            print(f"✓ {result['elapsed_seconds']:.3f}s")
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return 1

    # Print results table
    print_results_table(results)

    # Print summary
    print("\nBenchmark Summary:")
    print("─" * 95)
    if results:
        total_time = sum(r["elapsed_seconds"] for r in results)
        min_time = min(r["elapsed_seconds"] for r in results)
        max_time = max(r["elapsed_seconds"] for r in results)
        avg_time = total_time / len(results)

        print(f"Total benchmark time:    {total_time:.3f}s")
        print(f"Average scenario time:   {avg_time:.3f}s")
        print(f"Fastest scenario:        {min_time:.3f}s")
        print(f"Slowest scenario:        {max_time:.3f}s")
        print(f"Scenarios completed:     {len(results)}/{len(scenarios)}")

        # Phase 2 target check
        phase2_target = 5.0  # seconds for 10k individuals × 100 genes × 1k generations
        aggressive_results = [r for r in results if r["n_individuals"] == 10000]
        if aggressive_results:
            aggressive = aggressive_results[0]
            print(f"\nPhase 2 Target Check (10k × 100 × 1000):")
            print(f"  Actual time:             {aggressive['elapsed_seconds']:.3f}s")
            print(f"  Target time:             {phase2_target:.3f}s")
            status = "✓ PASS" if aggressive['elapsed_seconds'] <= phase2_target else "✗ MISS"
            print(f"  Status:                  {status}")

    print("─" * 95)
    print("\n✓ All benchmarks completed successfully!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
