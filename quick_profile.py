#!/usr/bin/env python3
"""Quick profiling with phase breakdown for medium scenario."""

import sys
import time
import numpy as np
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import LinearExpression
from happygene.selection import ThresholdSelection
from happygene.mutation import PointMutation
from happygene.regulatory_network import RegulatoryNetwork, RegulationConnection


class ProfilingGeneNetwork(GeneNetwork):
    """GeneNetwork with phase timing instrumentation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phase_times = {
            "Expression": [],
            "Selection": [],
            "Mutation": [],
            "Update": [],
        }

    def step(self) -> None:
        """Advance simulation with phase timing."""
        n_indiv = len(self.individuals)
        if n_indiv == 0:
            self._generation += 1
            return

        n_genes = len(self.individuals[0].genes)

        # Phase 1: Expression
        t0 = time.perf_counter()
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

        for ind_idx, individual in enumerate(self.individuals):
            for gene_idx, gene in enumerate(individual.genes):
                gene._expression_level = expr_matrix[ind_idx, gene_idx]

        self.phase_times["Expression"].append(time.perf_counter() - t0)

        # Phase 2: Selection
        t0 = time.perf_counter()
        if type(self.selection_model).__name__ == 'ProportionalSelection' and n_genes > 0:
            fitness_values = np.mean(expr_matrix, axis=1)
            for ind_idx, individual in enumerate(self.individuals):
                individual.fitness = fitness_values[ind_idx]
        else:
            for individual in self.individuals:
                fitness = self.selection_model.compute_fitness(individual)
                individual.fitness = fitness
        self.phase_times["Selection"].append(time.perf_counter() - t0)

        # Phase 3: Mutation
        t0 = time.perf_counter()
        for individual in self.individuals:
            self.mutation_model.mutate(individual, self.rng)
        self.phase_times["Mutation"].append(time.perf_counter() - t0)

        # Phase 4: Update
        t0 = time.perf_counter()
        self._generation += 1
        self.phase_times["Update"].append(time.perf_counter() - t0)


def create_regulatory_network(n_genes: int, density: float = 0.05, seed: int = 42) -> RegulatoryNetwork:
    """Create a sparse regulatory network."""
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


def profile_scenario(n_indiv: int, n_genes: int, n_gen: int, use_reg: bool = False) -> dict:
    """Run scenario with phase profiling."""
    np.random.seed(42)
    individuals = [
        Individual([Gene(f"g{i}", np.random.uniform(0.3, 0.7)) for i in range(n_genes)])
        for _ in range(n_indiv)
    ]

    regulatory_network = None
    if use_reg and n_genes >= 3:
        regulatory_network = create_regulatory_network(n_genes, density=0.05, seed=42)

    network = ProfilingGeneNetwork(
        individuals=individuals,
        expression_model=LinearExpression(slope=1.0, intercept=0.0),
        selection_model=ThresholdSelection(threshold=0.4),
        mutation_model=PointMutation(rate=0.1, magnitude=0.05),
        regulatory_network=regulatory_network,
        seed=42
    )

    start = time.perf_counter()
    network.run(n_gen)
    total_time = time.perf_counter() - start

    # Compute statistics
    result = {
        "scenario": f"{n_indiv}×{n_genes}×{n_gen}" + (" +reg" if use_reg else ""),
        "total_time": total_time,
        "ops_per_sec": (n_indiv * n_genes * n_gen) / total_time,
        "phases": {},
    }

    for phase in ["Expression", "Selection", "Mutation", "Update"]:
        times = network.phase_times[phase]
        result["phases"][phase] = {
            "total": sum(times),
            "count": len(times),
            "mean": sum(times) / len(times) if times else 0,
            "pct": (sum(times) / total_time * 100) if total_time > 0 else 0,
        }

    return result


def main() -> int:
    """Run profiling and print results."""
    print("=" * 80)
    print("HAPPYGENE Quick Performance Profile")
    print("=" * 80)

    # Scenario 1: 1000×50×100
    print("\n[1/3] Profiling 1000×50×100 (baseline)...")
    result1 = profile_scenario(1000, 50, 100, use_reg=False)
    print(f"  Time: {result1['total_time']:.3f}s, Ops/sec: {result1['ops_per_sec']:.0f}")

    # Scenario 2: 1000×50×100 with regulation
    print("[2/3] Profiling 1000×50×100 (with regulation)...")
    result2 = profile_scenario(1000, 50, 100, use_reg=True)
    print(f"  Time: {result2['total_time']:.3f}s, Ops/sec: {result2['ops_per_sec']:.0f}")

    # Scenario 3: 2000×100×100 (closer to real workload)
    print("[3/3] Profiling 2000×100×100 (baseline)...")
    result3 = profile_scenario(2000, 100, 100, use_reg=False)
    print(f"  Time: {result3['total_time']:.3f}s, Ops/sec: {result3['ops_per_sec']:.0f}")

    # Print detailed results
    for result in [result1, result2, result3]:
        print("\n" + "=" * 80)
        print(f"Scenario: {result['scenario']}")
        print("=" * 80)
        print(f"Total time:      {result['total_time']:.3f}s")
        print(f"Ops/sec:         {result['ops_per_sec']:.0f}")
        print("\nPhase Breakdown:")
        print(f"  {'Phase':<15} {'Total (s)':>12} {'% of total':>12} {'Mean/gen (ms)':>15}")
        print("  " + "─" * 56)
        for phase in ["Expression", "Selection", "Mutation", "Update"]:
            p = result["phases"][phase]
            mean_ms = p["mean"] * 1000
            print(f"  {phase:<15} {p['total']:>12.3f} {p['pct']:>11.1f}% {mean_ms:>15.3f}")

    # Overhead analysis
    print("\n" + "=" * 80)
    print("Regulation Overhead Analysis")
    print("=" * 80)
    overhead = result2["total_time"] - result1["total_time"]
    overhead_pct = (overhead / result1["total_time"] * 100)
    print(f"Baseline (1000×50×100):      {result1['total_time']:.3f}s")
    print(f"With regulation:             {result2['total_time']:.3f}s")
    print(f"Absolute overhead:           {overhead:+.3f}s")
    print(f"Relative overhead:           {overhead_pct:+.1f}%")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
