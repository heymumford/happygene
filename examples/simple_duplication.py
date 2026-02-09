#!/usr/bin/env python3
"""Simple gene duplication example: Basic simulation workflow.

This example demonstrates the core happygene workflow:
1. Create a population of individuals with genes
2. Set up expression, selection, and mutation models
3. Run the simulation
4. Collect and display results

This is a minimal example designed to take ~5 minutes to understand.
No external visualization required (optional matplotlib visualization included).
"""

import sys

from happygene.datacollector import DataCollector
from happygene.entities import Gene, Individual
from happygene.expression import ConstantExpression
from happygene.model import GeneNetwork
from happygene.mutation import PointMutation
from happygene.selection import ProportionalSelection


def main():
    """Run simple gene duplication simulation."""
    print("=" * 70)
    print("HAPPYGENE: Simple Gene Duplication Example")
    print("=" * 70)

    # Step 1: Create population
    print("\n[1/5] Creating population...")
    num_individuals = 100
    num_genes = 10
    initial_expression = 1.0

    individuals = [
        Individual([Gene(f"gene_{j}", initial_expression) for j in range(num_genes)])
        for i in range(num_individuals)
    ]
    print(f"  ✓ Created {num_individuals} individuals with {num_genes} genes each")

    # Step 2: Set up models
    print("\n[2/5] Configuring models...")
    expr_model = ConstantExpression(level=initial_expression)
    select_model = ProportionalSelection()
    mutate_model = PointMutation(rate=0.3, magnitude=0.05)
    print("  ✓ Expression: ConstantExpression (level=1.0)")
    print("  ✓ Selection: ProportionalSelection (fitness = mean expression)")
    print("  ✓ Mutation: PointMutation (rate=0.3, magnitude=0.05)")

    # Step 3: Create network and collector
    print("\n[3/5] Creating simulation network...")
    network = GeneNetwork(
        individuals=individuals,
        expression_model=expr_model,
        selection_model=select_model,
        mutation_model=mutate_model,
        seed=42,  # Reproducible results
    )

    collector = DataCollector(
        model_reporters={"mean_fitness": lambda m: m.compute_mean_fitness()},
        individual_reporters={"fitness": lambda ind: ind.fitness},
        gene_reporters={"expression_level": lambda gene: gene.expression_level},
    )
    print("  ✓ GeneNetwork created with DataCollector")
    print("  ✓ Reproducible seed: 42")

    # Step 4: Run simulation
    print("\n[4/5] Running simulation...")
    num_generations = 200
    network.run(num_generations)
    print(f"  ✓ Completed {num_generations} generations")

    # Collect final generation data
    collector.collect(network)

    # Step 5: Display results
    print("\n[5/5] Analyzing results...")

    # Get DataFrames
    model_df = collector.get_model_dataframe()
    individual_df = collector.get_individual_dataframe()
    gene_df = collector.get_gene_dataframe()

    # Compute statistics
    initial_fitness = model_df["mean_fitness"].iloc[0] if len(model_df) > 0 else 0.0
    final_fitness = model_df["mean_fitness"].iloc[-1] if len(model_df) > 0 else 0.0
    max_fitness = model_df["mean_fitness"].max() if len(model_df) > 0 else 0.0
    min_fitness = model_df["mean_fitness"].min() if len(model_df) > 0 else 0.0

    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)
    print("\nPopulation Statistics:")
    print(f"  Population size:        {num_individuals} individuals")
    print(f"  Genes per individual:   {num_genes} genes")
    print(f"  Generations simulated:  {num_generations}")

    print("\nFitness Summary (ProportionalSelection):")
    print(f"  Initial mean fitness:   {initial_fitness:.4f}")
    print(f"  Final mean fitness:     {final_fitness:.4f}")
    print(f"  Maximum fitness:        {max_fitness:.4f}")
    print(f"  Minimum fitness:        {min_fitness:.4f}")

    print("\nData Collection Summary:")
    print(f"  Model-level records:    {len(model_df)}")
    print(f"  Individual records:     {len(individual_df)}")
    print(f"  Gene records:           {len(gene_df)}")

    # Optional: Try to visualize with matplotlib
    try:
        import matplotlib.pyplot as plt

        print("\n[OPTIONAL] Generating visualization...")
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Plot 1: Mean fitness over time
        if len(model_df) > 0:
            axes[0].plot(model_df["generation"], model_df["mean_fitness"], linewidth=2)
            axes[0].set_xlabel("Generation")
            axes[0].set_ylabel("Mean Fitness")
            axes[0].set_title("Population Mean Fitness Over Time")
            axes[0].grid(True, alpha=0.3)

        # Plot 2: Gene expression distribution in final generation
        if len(gene_df) > 0:
            final_gen_genes = gene_df[gene_df["generation"] == num_generations]
            if len(final_gen_genes) > 0:
                axes[1].hist(
                    final_gen_genes["expression_level"],
                    bins=30,
                    edgecolor="black",
                    alpha=0.7,
                )
                axes[1].set_xlabel("Gene Expression Level")
                axes[1].set_ylabel("Frequency")
                axes[1].set_title(
                    f"Gene Expression Distribution (Gen {num_generations})"
                )
                axes[1].grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        output_file = "simple_duplication_results.png"
        plt.savefig(output_file, dpi=100)
        print(f"  ✓ Saved visualization to: {output_file}")
        plt.close()

    except ImportError:
        print("\n[INFO] matplotlib not installed (optional dependency)")
        print("       To visualize results, install: pip install matplotlib")

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  - Try modifying num_individuals, num_genes, or num_generations")
    print("  - Experiment with different expression/selection/mutation models")
    print("  - See happygene documentation for advanced examples")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
