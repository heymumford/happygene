"""Example 3: Advanced Regulatory Network with Epistatic Fitness.

Demonstrates:
- Complex gene regulatory network (5 genes with feedback)
- Epistatic fitness (gene-gene interaction effects)
- Evolution toward a stable regulatory motif
- Analysis of network structure and fitness landscape

Scenario:
  A synthetic oscillator network (repressilator-like) where:
  - Three core genes (g0, g1, g2) form a feedback loop
  - Two regulatory genes (g3, g4) modulate the core network
  - Fitness rewards balanced expression (no gene too dominant)
  - Epistasis rewards co-expression of specific gene pairs
"""

import numpy as np
from happygene import (
    GeneNetwork,
    Individual,
    Gene,
    LinearExpression,
    EpistaticFitness,
    PointMutation,
    RegulatoryNetwork,
    RegulationConnection,
    CompositeExpressionModel,
    AdditiveRegulation,
    Conditions,
)


def build_repressilator_network():
    """Build repressilator-like regulatory network.

    Core structure: g0 ⊣ g1 ⊣ g2 ⊣ g0 (mutual repression loop)
    Modulators: g3 → core network (activation), g4 → core (repression)

    Returns
    -------
    RegulatoryNetwork
        5-gene network with feedback structure.
    """
    gene_names = ["g0", "g1", "g2", "g3", "g4"]

    # Repressilator core: three genes repressing each other
    interactions = [
        # Core feedback loop (mutual repression)
        RegulationConnection("g0", "g1", weight=-0.5),  # g0 represses g1
        RegulationConnection("g1", "g2", weight=-0.5),  # g1 represses g2
        RegulationConnection("g2", "g0", weight=-0.5),  # g2 represses g0

        # Modulators: g3 activates, g4 represses
        RegulationConnection("g3", "g0", weight=0.3),   # g3 activates g0
        RegulationConnection("g3", "g1", weight=0.3),   # g3 activates g1
        RegulationConnection("g4", "g2", weight=-0.3),  # g4 represses g2
    ]

    return RegulatoryNetwork(
        gene_names=gene_names,
        interactions=interactions,
        detect_circuits=True  # Analyze network motifs
    )


def build_epistatic_fitness_model():
    """Build epistatic fitness rewarding balanced gene expression.

    Interactions:
    - Synergy between pairs that should co-express (g0+g3, g1+g3)
    - Antagonism between conflicting genes (g0+g1, g1+g2)

    Returns
    -------
    EpistaticFitness
        5x5 interaction matrix.
    """
    # 5x5 interaction matrix
    interactions = np.array([
        # g0    g1    g2    g3    g4
        [0.0, -0.2,  0.0,  0.2,  0.0],  # g0: synergy with g3, antagonism with g1
        [0.0,  0.0, -0.2,  0.2,  0.0],  # g1: synergy with g3, antagonism with g2
        [0.0,  0.0,  0.0,  0.0, -0.1],  # g2: antagonism with g4
        [0.0,  0.0,  0.0,  0.0,  0.0],  # g3: activator
        [0.0,  0.0,  0.0,  0.0,  0.0],  # g4: repressor
    ])

    return EpistaticFitness(interaction_matrix=interactions)


def main():
    """Run 100-generation evolution with regulatory network + epistatic fitness."""

    print("=" * 70)
    print("Example 3: Advanced Regulatory Network with Epistatic Fitness")
    print("=" * 70)

    # Build network and fitness model
    print("\n1. Building 5-gene repressilator-like regulatory network...")
    regulatory_net = build_repressilator_network()
    print(f"   - Gene count: {regulatory_net.n_genes}")
    print(f"   - Interactions: {regulatory_net.adjacency.nnz}")
    print(f"   - Is acyclic: {regulatory_net.is_acyclic}")
    if regulatory_net.circuits:
        print(f"   - Detected feedback loops: {len(regulatory_net.circuits)}")

    print("\n2. Building epistatic fitness model...")
    fitness_model = build_epistatic_fitness_model()
    print("   - 5x5 interaction matrix")
    print("   - Synergy: g0+g3, g1+g3")
    print("   - Antagonism: g0+g1, g1+g2, g2+g4")

    # Create initial population
    print("\n3. Initializing population (100 individuals)...")
    np.random.seed(42)
    individuals = []
    for i in range(100):
        genes = [
            Gene(f"g{j}", np.random.uniform(0.2, 0.8))
            for j in range(5)
        ]
        individuals.append(Individual(genes))

    # Create expression model (constant base + regulatory overlay)
    base_expr = CompositeExpressionModel(
        base_model=LinearExpression(slope=1.0, intercept=0.1),
        regulatory_model=AdditiveRegulation(weight=0.5)
    )

    # Create gene network
    network = GeneNetwork(
        individuals=individuals,
        expression_model=base_expr,
        selection_model=fitness_model,
        mutation_model=PointMutation(rate=0.05, magnitude=0.1),
        regulatory_network=regulatory_net,
        seed=42
    )

    # Run evolution
    print("\n4. Running 100 generations...")
    for generation in [10, 25, 50, 75, 100]:
        while network.generation < generation:
            network.step()

        # Sample statistics
        fitnesses = [fitness_model.compute_fitness(ind) for ind in network.individuals]
        mean_fit = np.mean(fitnesses)
        max_fit = np.max(fitnesses)

        print(f"   Gen {generation:3d}: mean_fitness={mean_fit:.4f}, max={max_fit:.4f}")

    # Final analysis
    print("\n5. Final population analysis:")
    fitnesses = np.array([fitness_model.compute_fitness(ind) for ind in network.individuals])
    expr_by_gene = [
        np.mean([ind.genes[j].expression_level for ind in network.individuals])
        for j in range(5)
    ]

    print(f"   - Mean fitness: {np.mean(fitnesses):.4f}")
    print(f"   - Max fitness: {np.max(fitnesses):.4f}")
    print(f"   - Std fitness: {np.std(fitnesses):.4f}")
    print(f"   - Gene expression (mean):")
    for j, expr in enumerate(expr_by_gene):
        print(f"     g{j}: {expr:.4f}")

    print("\n" + "=" * 70)
    print("Example 3 complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
