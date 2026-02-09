#!/usr/bin/env python3
"""Regulatory network example: Hill kinetics + threshold selection.

This example demonstrates advanced happygene features:
1. Hill kinetics for gene expression (sigmoidal responses)
2. Threshold-based selection (fitness only above threshold)
3. Gene regulatory interactions (some genes regulate others)
4. Multi-level data collection (model + individual + gene metrics)

This example takes ~10 minutes to understand and demonstrates
realistic gene regulatory dynamics with cooperative binding.
"""

import sys
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.conditions import Conditions
from happygene.expression import HillExpression
from happygene.selection import ThresholdSelection
from happygene.mutation import PointMutation
from happygene.datacollector import DataCollector


def create_regulatory_individuals(num_individuals, num_genes):
    """Create individuals with regulatory gene names (TF1, TF2, etc.)."""
    gene_names = [f"TF{i+1}" for i in range(num_genes)]  # Transcription factors
    individuals = []

    for i in range(num_individuals):
        genes = [Gene(name, expression_level=0.5) for name in gene_names]
        ind = Individual(genes)
        individuals.append(ind)

    return individuals


def main():
    """Run regulatory network simulation with Hill kinetics."""
    print("=" * 80)
    print("HAPPYGENE: Regulatory Network Example (Hill Kinetics + Threshold Selection)")
    print("=" * 80)

    # Step 1: Create population with regulatory genes
    print("\n[1/6] Creating regulatory population...")
    num_individuals = 50
    num_genes = 5

    individuals = create_regulatory_individuals(num_individuals, num_genes)
    print(f"  ✓ Created {num_individuals} individuals with {num_genes} regulatory genes")
    print(f"    Gene names: TF1, TF2, TF3, TF4, TF5 (transcription factors)")

    # Step 2: Configure Hill kinetics expression model
    print("\n[2/6] Configuring Hill kinetics expression model...")
    # Hill equation: E = v_max * [tf]^n / (k^n + [tf]^n)
    # This models cooperative binding with Hill coefficient (n=2 for cooperativity)
    hill_model = HillExpression(
        v_max=1.0,     # Maximum expression level
        k=0.5,         # Half-saturation point (Km)
        n=2.0          # Hill coefficient (cooperativity: 2 = stronger cooperativity)
    )
    print(f"  ✓ HillExpression configured:")
    print(f"    v_max={hill_model.v_max} (max expression)")
    print(f"    k={hill_model.k} (half-saturation)")
    print(f"    n={hill_model.n} (Hill coefficient - cooperativity)")

    # Step 3: Configure threshold-based selection
    print("\n[3/6] Configuring threshold-based selection...")
    # Only individuals with mean expression > threshold survive
    threshold_model = ThresholdSelection(threshold=0.4)
    print(f"  ✓ ThresholdSelection configured:")
    print(f"    threshold={threshold_model.threshold}")
    print(f"    Selection rule: fitness = 1.0 if mean_expr > {threshold_model.threshold}, else 0.0")

    # Step 4: Configure mutation model
    print("\n[4/6] Configuring mutation model...")
    mutate_model = PointMutation(rate=0.2, magnitude=0.1)
    print(f"  ✓ PointMutation configured:")
    print(f"    rate={mutate_model.rate} (probability per gene per generation)")
    print(f"    magnitude={mutate_model.magnitude} (standard deviation of change)")

    # Step 5: Create network and data collector
    print("\n[5/6] Creating simulation network...")
    # Set environmental conditions: tf_concentration drives Hill kinetics
    conditions = Conditions(
        tf_concentration=0.7,  # Moderate transcription factor level
        temperature=37.0,
        nutrients=1.0
    )

    network = GeneNetwork(
        individuals=individuals,
        expression_model=hill_model,
        selection_model=threshold_model,
        mutation_model=mutate_model,
        seed=42,  # Reproducible results
        conditions=conditions
    )

    # Multi-level data collector: model, individual, and gene metrics
    collector = DataCollector(
        model_reporters={
            "mean_fitness": lambda m: m.compute_mean_fitness(),
            "mean_expression": lambda m: sum(ind.mean_expression() for ind in m.individuals) / len(m.individuals) if m.individuals else 0.0,
        },
        individual_reporters={
            "fitness": lambda ind: ind.fitness,
            "mean_expression": lambda ind: ind.mean_expression(),
        },
        gene_reporters={
            "expression_level": lambda gene: gene.expression_level,
        }
    )
    print(f"  ✓ GeneNetwork created with multi-level DataCollector")
    print(f"  ✓ Environmental conditions: tf_concentration={conditions.tf_concentration}")
    print(f"  ✓ Model reporters: mean_fitness, mean_expression")
    print(f"  ✓ Individual reporters: fitness, mean_expression")
    print(f"  ✓ Gene reporters: expression_level")
    print(f"  ✓ Reproducible seed: 42")

    # Step 6: Run simulation
    print("\n[6/6] Running simulation...")
    num_generations = 150
    network.run(num_generations)
    print(f"  ✓ Completed {num_generations} generations")

    # Collect final generation data
    collector.collect(network)

    # ANALYSIS: Display results
    print("\n" + "=" * 80)
    print("SIMULATION RESULTS: Regulatory Network Evolution")
    print("=" * 80)

    # Get DataFrames
    model_df = collector.get_model_dataframe()
    individual_df = collector.get_individual_dataframe()
    gene_df = collector.get_gene_dataframe()

    # Compute statistics
    if len(model_df) > 0:
        initial_fitness = model_df["mean_fitness"].iloc[0]
        final_fitness = model_df["mean_fitness"].iloc[-1]
        max_fitness = model_df["mean_fitness"].max()
        min_fitness = model_df["mean_fitness"].min()
        mean_fitness = model_df["mean_fitness"].mean()

        initial_expr = model_df["mean_expression"].iloc[0]
        final_expr = model_df["mean_expression"].iloc[-1]
        max_expr = model_df["mean_expression"].max()
    else:
        initial_fitness = final_fitness = max_fitness = min_fitness = mean_fitness = 0.0
        initial_expr = final_expr = max_expr = 0.0

    print(f"\nPopulation Statistics:")
    print(f"  Population size:         {num_individuals} individuals")
    print(f"  Regulatory genes:        {num_genes} genes (TF1-TF5)")
    print(f"  Generations simulated:   {num_generations}")

    print(f"\nFitness Summary (ThresholdSelection, threshold={threshold_model.threshold}):")
    print(f"  Initial mean fitness:    {initial_fitness:.4f}")
    print(f"  Final mean fitness:      {final_fitness:.4f}")
    print(f"  Mean fitness (all gens): {mean_fitness:.4f}")
    print(f"  Maximum fitness:         {max_fitness:.4f}")
    print(f"  Minimum fitness:         {min_fitness:.4f}")
    print(f"  Selection pressure:      {'Strong' if final_fitness > mean_fitness else 'Weak'} (final > mean)")

    print(f"\nExpression Summary (Hill Kinetics):")
    print(f"  Initial mean expression: {initial_expr:.4f}")
    print(f"  Final mean expression:   {final_expr:.4f}")
    print(f"  Maximum expression:      {max_expr:.4f}")
    print(f"  Expression trend:        {'↑ Increasing' if final_expr > initial_expr else '↓ Decreasing'}")

    print(f"\nData Collection Summary:")
    print(f"  Model-level records:     {len(model_df)} (1 per generation)")
    print(f"  Individual records:      {len(individual_df)}")
    print(f"  Gene records:            {len(gene_df)}")

    # Calculate selection pressure effects
    print(f"\nSelection Pressure Analysis:")
    survivors_per_gen = individual_df.groupby("generation")["fitness"].apply(lambda x: (x > 0).sum())
    if len(survivors_per_gen) > 0:
        avg_survivors = survivors_per_gen.mean()
        print(f"  Average survivors/gen:   {avg_survivors:.1f}/{num_individuals} ({100*avg_survivors/num_individuals:.1f}%)")
        print(f"  Bottleneck threshold:    {threshold_model.threshold}")

    # Gene-level statistics
    if len(gene_df) > 0:
        final_gen_genes = gene_df[gene_df["generation"] == num_generations]
        if len(final_gen_genes) > 0:
            print(f"\nGene Expression (Final Generation):")
            print(f"  Mean expression level:   {final_gen_genes['expression_level'].mean():.4f}")
            print(f"  Std dev:                 {final_gen_genes['expression_level'].std():.4f}")
            print(f"  Min expression:          {final_gen_genes['expression_level'].min():.4f}")
            print(f"  Max expression:          {final_gen_genes['expression_level'].max():.4f}")

    # Optional: Try to visualize with matplotlib
    try:
        import matplotlib.pyplot as plt

        print(f"\n[OPTIONAL] Generating visualization...")
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: Mean fitness over time
        if len(model_df) > 0:
            axes[0, 0].plot(
                model_df["generation"],
                model_df["mean_fitness"],
                linewidth=2,
                color="darkred"
            )
            axes[0, 0].axhline(y=threshold_model.threshold, color="red", linestyle="--", alpha=0.5, label="Selection threshold")
            axes[0, 0].set_xlabel("Generation")
            axes[0, 0].set_ylabel("Mean Fitness")
            axes[0, 0].set_title("Population Mean Fitness (Threshold Selection)")
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].legend()

        # Plot 2: Mean expression over time
        if len(model_df) > 0:
            axes[0, 1].plot(
                model_df["generation"],
                model_df["mean_expression"],
                linewidth=2,
                color="darkblue"
            )
            axes[0, 1].axhline(y=threshold_model.threshold, color="red", linestyle="--", alpha=0.5, label="Selection threshold")
            axes[0, 1].set_xlabel("Generation")
            axes[0, 1].set_ylabel("Mean Expression Level")
            axes[0, 1].set_title("Population Mean Expression (Hill Kinetics)")
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].legend()

        # Plot 3: Fitness distribution in final generation
        if len(individual_df) > 0:
            final_gen_indiv = individual_df[individual_df["generation"] == num_generations]
            if len(final_gen_indiv) > 0:
                axes[1, 0].hist(
                    final_gen_indiv["fitness"],
                    bins=10,
                    edgecolor="black",
                    alpha=0.7,
                    color="darkred"
                )
                axes[1, 0].set_xlabel("Fitness")
                axes[1, 0].set_ylabel("Count")
                axes[1, 0].set_title(f"Fitness Distribution (Gen {num_generations})")
                axes[1, 0].grid(True, alpha=0.3, axis="y")

        # Plot 4: Gene expression distribution in final generation
        if len(gene_df) > 0:
            final_gen_genes = gene_df[gene_df["generation"] == num_generations]
            if len(final_gen_genes) > 0:
                axes[1, 1].hist(
                    final_gen_genes["expression_level"],
                    bins=30,
                    edgecolor="black",
                    alpha=0.7,
                    color="darkblue"
                )
                axes[1, 1].set_xlabel("Gene Expression Level")
                axes[1, 1].set_ylabel("Frequency")
                axes[1, 1].set_title(f"Gene Expression Distribution (Gen {num_generations})")
                axes[1, 1].grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        output_file = "regulatory_network_results.png"
        plt.savefig(output_file, dpi=100)
        print(f"  ✓ Saved visualization to: {output_file}")
        plt.close()

    except ImportError:
        print(f"\n[INFO] matplotlib not installed (optional dependency)")
        print(f"       To visualize results, install: pip install matplotlib")

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print(f"\nKey Insights:")
    print(f"  - Hill kinetics models sigmoidal gene response (cooperative binding)")
    print(f"  - Threshold selection creates bottlenecks (only fit individuals survive)")
    print(f"  - Evolution toward higher expression/fitness or oscillation possible")
    print(f"  - This pattern models real regulatory networks (e.g., developmental genes)")
    print(f"\nNext steps:")
    print(f"  - Compare with constant expression model (see simple_duplication.py)")
    print(f"  - Try different threshold values (0.2, 0.5, 0.8)")
    print(f"  - Modify Hill coefficient n (1.0=linear, 2.0+=cooperative)")
    print(f"  - See happygene documentation for advanced multi-gene regulation")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
