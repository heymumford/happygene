#!/usr/bin/env python3
"""Performance profiling for happygene with phase breakdown analysis.

This script profiles the 5k x 100 x 1000 scenario to identify bottlenecks
across the four simulation phases: expression, selection, mutation, and update.

It uses cProfile for detailed function-level profiling and timing decorators
for phase-level measurements.

Usage:
    python profile_performance.py
    python profile_performance.py --individuals 5000 --genes 100 --generations 100
    python profile_performance.py --regulation
"""

import argparse
import sys
import time
import cProfile
import pstats
import io
from typing import Dict, List, Tuple, Optional
import numpy as np
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression, HillExpression
from happygene.selection import ProportionalSelection, ThresholdSelection
from happygene.mutation import PointMutation
from happygene.regulatory_network import RegulatoryNetwork, RegulationConnection


class PhaseTimer:
    """Context manager for timing individual phases."""

    def __init__(self, phase_name: str, timings: Dict[str, List[float]]):
        """Initialize timer for a phase.

        Parameters
        ----------
        phase_name : str
            Name of the phase being timed.
        timings : Dict[str, List[float]]
            Dictionary to accumulate timings by phase.
        """
        self.phase_name = phase_name
        self.timings = timings
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and accumulate."""
        elapsed = time.perf_counter() - self.start_time
        if self.phase_name not in self.timings:
            self.timings[self.phase_name] = []
        self.timings[self.phase_name].append(elapsed)


class ProfilingGeneNetwork(GeneNetwork):
    """GeneNetwork subclass with per-phase timing instrumentation."""

    def __init__(self, *args, **kwargs):
        """Initialize with timing tracking."""
        super().__init__(*args, **kwargs)
        self.phase_timings: Dict[str, List[float]] = {}

    def step(self) -> None:
        """Advance simulation with phase-level timing.

        Overrides parent step() to instrument each phase:
        1. Expression computation
        2. Selection (fitness evaluation)
        3. Mutation
        4. Generation increment
        """
        n_indiv = len(self.individuals)

        if n_indiv == 0:
            self._generation += 1
            return

        n_genes = len(self.individuals[0].genes)

        # Phase 1: Expression
        with PhaseTimer("Expression", self.phase_timings):
            expr_matrix = np.zeros((n_indiv, n_genes))

            if self._regulatory_network is not None:
                for ind_idx, individual in enumerate(self.individuals):
                    prev_expr = np.array([g.expression_level for g in individual.genes])
                    tf_inputs = self._regulatory_network.compute_tf_inputs(prev_expr)

                    if hasattr(self.expression_model, 'regulatory_model'):
                        for gene_idx in range(n_genes):
                            expr = self.expression_model.compute(
                                self.conditions,
                                tf_inputs=tf_inputs[gene_idx]
                            )
                            expr_matrix[ind_idx, gene_idx] = max(0.0, expr)
                    else:
                        for gene_idx in range(n_genes):
                            expr = self.expression_model.compute(self.conditions)
                            expr_matrix[ind_idx, gene_idx] = max(0.0, expr)
            else:
                expr_val = self.expression_model.compute(self.conditions)
                expr_matrix[:, :] = max(0.0, expr_val)

            # Update individuals from expression matrix (in-place)
            for ind_idx, individual in enumerate(self.individuals):
                for gene_idx, gene in enumerate(individual.genes):
                    gene._expression_level = expr_matrix[ind_idx, gene_idx]

        # Phase 2: Selection
        with PhaseTimer("Selection", self.phase_timings):
            if type(self.selection_model).__name__ == 'ProportionalSelection' and n_genes > 0:
                fitness_values = np.mean(expr_matrix, axis=1)
                for ind_idx, individual in enumerate(self.individuals):
                    individual.fitness = fitness_values[ind_idx]
            else:
                for individual in self.individuals:
                    fitness = self.selection_model.compute_fitness(individual)
                    individual.fitness = fitness

        # Phase 3: Mutation
        with PhaseTimer("Mutation", self.phase_timings):
            for individual in self.individuals:
                self.mutation_model.mutate(individual, self.rng)

        # Phase 4: Update (generation increment)
        with PhaseTimer("Update", self.phase_timings):
            self._generation += 1

    def get_phase_summary(self) -> Dict[str, Dict[str, float]]:
        """Get aggregated phase timing statistics.

        Returns
        -------
        Dict[str, Dict[str, float]]
            Per-phase statistics: min, max, mean, total, count.
        """
        summary = {}
        for phase_name, times in self.phase_timings.items():
            if times:
                summary[phase_name] = {
                    "min": min(times),
                    "max": max(times),
                    "mean": sum(times) / len(times),
                    "total": sum(times),
                    "count": len(times),
                }
        return summary


def create_population(n_individuals: int, n_genes: int, seed: int = 42) -> List[Individual]:
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
    List[Individual]
        List of Individual objects.
    """
    np.random.seed(seed)
    individuals = [
        Individual([Gene(f"g{i}", np.random.uniform(0.3, 0.7)) for i in range(n_genes)])
        for _ in range(n_individuals)
    ]
    return individuals


def create_regulatory_network(
    n_genes: int, density: float = 0.05, seed: int = 42
) -> RegulatoryNetwork:
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


def profile_scenario(
    n_individuals: int,
    n_genes: int,
    n_generations: int,
    use_regulation: bool = False,
    use_profiler: bool = False,
    seed: int = 42
) -> Tuple[Dict, Optional[str]]:
    """Run a scenario with profiling enabled.

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
    use_profiler : bool
        Whether to use cProfile for function-level profiling.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    Tuple[Dict, Optional[str]]
        Profiling results and cProfile stats string (if enabled).
    """
    # Create population
    individuals = create_population(n_individuals, n_genes, seed=seed)

    # Expression model
    expr_model = LinearExpression(slope=1.0, intercept=0.0)

    # Regulatory network (optional)
    regulatory_network = None
    if use_regulation and n_genes >= 3:
        regulatory_network = create_regulatory_network(n_genes, density=0.05, seed=seed)

    # Create network with profiling instrumentation
    network = ProfilingGeneNetwork(
        individuals=individuals,
        expression_model=expr_model,
        selection_model=ThresholdSelection(threshold=0.4),
        mutation_model=PointMutation(rate=0.1, magnitude=0.05),
        regulatory_network=regulatory_network,
        seed=seed
    )

    # Run with optional cProfile
    profiler = cProfile.Profile() if use_profiler else None
    start_time = time.perf_counter()

    if use_profiler:
        profiler.enable()

    network.run(n_generations)

    if use_profiler:
        profiler.disable()

    elapsed_seconds = time.perf_counter() - start_time

    # Get phase summary
    phase_summary = network.get_phase_summary()

    # Format cProfile results
    stats_str = None
    if use_profiler:
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(15)  # Top 15 functions
        stats_str = s.getvalue()

    result = {
        "n_individuals": n_individuals,
        "n_genes": n_genes,
        "n_generations": n_generations,
        "regulation": use_regulation,
        "elapsed_seconds": elapsed_seconds,
        "phase_timings": phase_summary,
        "total_operations": n_individuals * n_genes * n_generations,
    }

    return result, stats_str


def print_phase_breakdown(result: Dict) -> None:
    """Print phase breakdown for a scenario.

    Parameters
    ----------
    result : Dict
        Profiling result dictionary with phase timings.
    """
    print("\nPhase Breakdown:")
    print("─" * 70)
    print(f"{'Phase':>15} {'Total (s)':>12} {'% of Total':>12} {'Mean (ms)':>12}")
    print("─" * 70)

    phase_timings = result.get("phase_timings", {})
    total_time = result["elapsed_seconds"]

    if not phase_timings:
        print("No phase timings available")
        return

    for phase_name in ["Expression", "Selection", "Mutation", "Update"]:
        if phase_name in phase_timings:
            stats = phase_timings[phase_name]
            total_phase = stats["total"]
            pct = (total_phase / total_time * 100) if total_time > 0 else 0
            mean_ms = stats["mean"] * 1000
            print(f"{phase_name:>15} {total_phase:>12.3f} {pct:>11.1f}% {mean_ms:>12.3f}")

    print("─" * 70)
    print(f"{'TOTAL':>15} {total_time:>12.3f} {'100.0%':>11} {(total_time/result['n_generations']*1000):>12.3f}")


def main() -> int:
    """Run performance profiling scenarios and generate report.

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Profile happygene performance with phase breakdown analysis"
    )
    parser.add_argument(
        "--individuals",
        type=int,
        default=5000,
        help="Number of individuals (default: 5000)"
    )
    parser.add_argument(
        "--genes",
        type=int,
        default=100,
        help="Number of genes per individual (default: 100)"
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=1000,
        help="Number of generations to simulate (default: 1000)"
    )
    parser.add_argument(
        "--regulation",
        action="store_true",
        help="Enable regulatory network with TF interactions"
    )
    parser.add_argument(
        "--cprofile",
        action="store_true",
        help="Enable cProfile for function-level profiling"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("HAPPYGENE Performance Profiler")
    print("=" * 70)

    # Profile baseline scenario
    print(
        f"\n[1/2] Profiling baseline: {args.individuals} indiv × {args.genes} genes × {args.generations} gen...",
        end=" ",
        flush=True
    )

    try:
        result_baseline, stats_baseline = profile_scenario(
            args.individuals,
            args.genes,
            args.generations,
            use_regulation=False,
            use_profiler=args.cprofile,
            seed=42
        )
        print(f"✓ {result_baseline['elapsed_seconds']:.3f}s")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Profile regulatory scenario (if requested)
    result_regulation = None
    stats_regulation = None
    if args.regulation and args.genes >= 3:
        print(
            f"[2/2] Profiling with regulation: {args.individuals} indiv × {args.genes} genes × {args.generations} gen...",
            end=" ",
            flush=True
        )

        try:
            result_regulation, stats_regulation = profile_scenario(
                args.individuals,
                args.genes,
                args.generations,
                use_regulation=True,
                use_profiler=args.cprofile,
                seed=42
            )
            print(f"✓ {result_regulation['elapsed_seconds']:.3f}s")
        except Exception as e:
            print(f"✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Print results
    print("\n" + "=" * 70)
    print("BASELINE SCENARIO (No Regulation)")
    print("=" * 70)
    print(f"Individuals:     {result_baseline['n_individuals']}")
    print(f"Genes:           {result_baseline['n_genes']}")
    print(f"Generations:     {result_baseline['n_generations']}")
    print(f"Total time:      {result_baseline['elapsed_seconds']:.3f}s")
    print(f"Ops/generation:  {result_baseline['total_operations']/result_baseline['n_generations']:.0f}")
    print(f"Ops/sec:         {result_baseline['total_operations']/result_baseline['elapsed_seconds']:.0f}")

    print_phase_breakdown(result_baseline)

    if result_regulation:
        print("\n" + "=" * 70)
        print("WITH REGULATION")
        print("=" * 70)
        print(f"Individuals:     {result_regulation['n_individuals']}")
        print(f"Genes:           {result_regulation['n_genes']}")
        print(f"Generations:     {result_regulation['n_generations']}")
        print(f"Total time:      {result_regulation['elapsed_seconds']:.3f}s")
        print(f"Ops/generation:  {result_regulation['total_operations']/result_regulation['n_generations']:.0f}")
        print(f"Ops/sec:         {result_regulation['total_operations']/result_regulation['elapsed_seconds']:.0f}")

        print_phase_breakdown(result_regulation)

        # Comparison
        overhead = result_regulation['elapsed_seconds'] - result_baseline['elapsed_seconds']
        pct_overhead = (overhead / result_baseline['elapsed_seconds'] * 100)
        print("\n" + "=" * 70)
        print("REGULATION OVERHEAD ANALYSIS")
        print("=" * 70)
        print(f"Baseline time:   {result_baseline['elapsed_seconds']:.3f}s")
        print(f"With regulation: {result_regulation['elapsed_seconds']:.3f}s")
        print(f"Absolute overhead: {overhead:.3f}s")
        print(f"Percentage overhead: {pct_overhead:.1f}%")

    if args.cprofile and stats_baseline:
        print("\n" + "=" * 70)
        print("FUNCTION-LEVEL PROFILING (cProfile - Top 15)")
        print("=" * 70)
        print(stats_baseline)

    print("=" * 70)
    print("✓ Profiling complete!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
