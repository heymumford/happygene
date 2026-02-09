"""
Morris Screening Workflow

Complete example showing:
1. Batch simulation setup and execution
2. Morris one-at-a-time screening
3. Parameter classification (Important/Interaction/Insignificant)
4. Parameter ranking by effect metrics
5. Results export and interpretation
"""

import numpy as np
import pandas as pd
from pathlib import Path

from happygene.model import Model
from happygene.analysis.batch import BatchSimulator
from happygene.analysis.morris import MorrisAnalyzer
from happygene.analysis.output import OutputExporter


class DummyModel(Model):
    """Simple model for Morris screening demonstration."""

    def compute(self, conditions):
        """Compute survival based on parameters."""
        p0 = conditions.get('p0', 0.5)  # Important
        p1 = conditions.get('p1', 0.5)  # Important
        p2 = conditions.get('p2', 0.5)  # Interaction (nonlinear)
        p3 = conditions.get('p3', 0.5)  # Minor
        p4 = conditions.get('p4', 0.5)  # Negligible

        # Structure: p0, p1 are important; p2 has nonlinear interaction; p3, p4 minor/negligible
        survival = (
            0.5 * p0 +
            0.3 * p1 +
            0.2 * p2 * p0 +  # Interaction: high sigma, moderate mu
            0.05 * p3 +
            0.01 * p4
        )
        return survival


def main():
    """Run complete Morris sensitivity analysis workflow."""

    # Step 1: Define parameter space
    param_space = {
        'p0': (0.01, 0.99),  # Important parameter
        'p1': (0.01, 0.99),  # Important parameter
        'p2': (0.01, 0.99),  # Interaction parameter
        'p3': (0.01, 0.99),  # Minor parameter
        'p4': (0.1, 10.0),   # Negligible parameter
    }

    # Step 2: Create batch simulator
    print("Step 1: Setting up batch simulator...")
    batch_sim = BatchSimulator(param_space, DummyModel)

    # Step 3: Generate Morris samples
    # For 5 params with N=20 trajectories: creates 20*(5+1) = 120 samples
    print("Step 2: Generating Morris samples (N=20 trajectories)...")
    samples = batch_sim.generate_samples('morris', 20)
    print(f"  Generated {len(samples)} samples")

    # Step 4: Run batch simulation
    print("Step 3: Running batch simulation (100 generations)...")
    results = batch_sim.run_batch(samples, generations=100, seed=42)
    print(f"  Executed {len(results)} simulations")

    # Step 5: Analyze with Morris indices
    print("\nStep 4: Computing Morris indices...")
    analyzer = MorrisAnalyzer(list(param_space.keys()))
    indices = analyzer.analyze(results, output_col='survival')

    print("\nMorris Index Summary:")
    print(f"  μ (mean effect, importance): {indices.mu}")
    print(f"  σ (std dev, interaction):    {indices.sigma}")
    print(f"  μ* (mean absolute effect):   {indices.mu_star}")

    # Step 6: Classify parameters
    print("\nStep 5: Classifying parameters...")
    classified = analyzer.classify_parameters(indices)

    print("\nParameter Classification:")
    for category, params in classified.items():
        print(f"  {category:15s}: {params}")

    # Step 7: Rank parameters
    print("\nStep 6: Ranking parameters...")

    # Rank by mu (overall importance)
    ranked_mu = analyzer.rank_parameters(indices, by='mu')
    print("\nRanking by μ (importance):")
    print(ranked_mu[['param', 'mu', 'sigma', 'rank']])

    # Step 8: Export results
    print("\nStep 7: Exporting results...")
    output_dir = Path(__file__).parent / 'morris_output'
    output_dir.mkdir(exist_ok=True)

    exporter = OutputExporter(str(output_dir))

    # Export indices to CSV
    indices_df = indices.to_dataframe()
    csv_path = exporter.export_indices_to_csv(indices_df, name='morris_indices')
    print(f"  Indices exported to: {csv_path}")

    # Export summary report
    summary = {
        'method': 'Morris (One-At-A-Time Screening)',
        'trajectories': 20,
        'generations': 100,
        'important_params': len(classified['Important']),
        'interaction_params': len(classified['Interaction']),
        'insignificant_params': len(classified['Insignificant']),
    }
    report_path = exporter.export_summary_report(summary, name='morris_summary')
    print(f"  Summary report: {report_path}")

    # Export batch results
    results_path = exporter.export_batch_results_to_csv(results, name='morris_batch_results')
    print(f"  Batch results: {results_path}")

    # Step 9: Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)

    print("\nParameter types (from Morris classification):")
    print("• IMPORTANT: High μ, low σ → robust strong effect")
    print("• INTERACTION: High μ, high σ → strong effect BUT nonlinear/interactive")
    print("• INSIGNIFICANT: Low μ, low σ → negligible effect")

    print("\nYour results:")
    for param in ranked_mu['param'].values[:3]:
        mu_val = indices.mu[indices.param_names.index(param)]
        sigma_val = indices.sigma[indices.param_names.index(param)]
        mu_star_val = indices.mu_star[indices.param_names.index(param)]
        print(f"  {param}: μ={mu_val:.3f}, σ={sigma_val:.3f}, μ*={mu_star_val:.3f}")

    print(f"\n✓ Morris workflow complete!")
    print(f"  Output directory: {output_dir}")


if __name__ == '__main__':
    main()
