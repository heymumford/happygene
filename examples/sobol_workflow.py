"""
Sobol Sensitivity Analysis Workflow

Complete example showing:
1. Batch simulation setup and execution
2. Sobol global sensitivity analysis
3. Parameter ranking by effects
4. Interaction detection
5. Results export
"""

import numpy as np
import pandas as pd
from pathlib import Path

from happygene.model import Model
from happygene.analysis.batch import BatchSimulator
from happygene.analysis.sobol import SobolAnalyzer
from happygene.analysis.output import OutputExporter


class DummyModel(Model):
    """Simple linear model for demonstration."""

    def compute(self, conditions):
        """Compute survival based on parameters with known sensitivity structure."""
        p0 = conditions.get("p0", 0.5)  # Most important
        p1 = conditions.get("p1", 0.5)  # Moderate
        p2 = conditions.get("p2", 0.5)  # Minor
        p3 = conditions.get("p3", 0.5)  # Interaction with p0
        p4 = conditions.get("p4", 0.5)  # Negligible

        # Known structure: Strong main effects for p0, p1; Interaction between p0*p3
        survival = 0.5 * p0 + 0.3 * p1 + 0.1 * p2 + 0.15 * (p0 * p3) + 0.02 * p4
        return survival


def main():
    """Run complete Sobol sensitivity analysis workflow."""

    # Step 1: Define parameter space
    param_space = {
        "p0": (0.01, 0.99),  # Parameter 0: high importance
        "p1": (0.01, 0.99),  # Parameter 1: moderate importance
        "p2": (0.01, 0.99),  # Parameter 2: low importance
        "p3": (0.01, 0.99),  # Parameter 3: interacts with p0
        "p4": (0.1, 10.0),  # Parameter 4: negligible
    }

    # Step 2: Create batch simulator
    print("Step 1: Setting up batch simulator...")
    batch_sim = BatchSimulator(param_space, DummyModel)

    # Step 3: Generate Sobol samples (Saltelli scheme)
    # For 5 params with N=64: creates 64*(2*5+2) = 768 samples
    print("Step 2: Generating Sobol samples (Saltelli scheme, N=64)...")
    samples = batch_sim.generate_samples("saltelli", 64, calc_second_order=False)
    print(f"  Generated {len(samples)} samples")

    # Step 4: Run batch simulation
    print("Step 3: Running batch simulation (100 generations)...")
    results = batch_sim.run_batch(samples, generations=100, seed=42)
    print(f"  Executed {len(results)} simulations")
    print(f"  Columns: {list(results.columns)}")

    # Step 5: Analyze with Sobol indices
    print("\nStep 4: Computing Sobol indices...")
    analyzer = SobolAnalyzer(list(param_space.keys()))
    indices = analyzer.analyze(results, output_col="survival", calc_second_order=False)
    print(f"  S1 (first-order): {indices.S1}")
    print(f"  ST (total): {indices.ST}")

    # Step 6: Rank parameters
    print("\nStep 5: Ranking parameters...")
    ranked = analyzer.rank_parameters(indices, by="ST")
    print("\nParameter rankings by total effect (ST):")
    print(ranked[["param", "ST", "rank"]])

    # Step 7: Export results
    print("\nStep 6: Exporting results...")
    output_dir = Path(__file__).parent / "sobol_output"
    output_dir.mkdir(exist_ok=True)

    exporter = OutputExporter(str(output_dir))

    # Export indices to CSV
    indices_df = indices.to_dataframe()
    csv_path = exporter.export_indices_to_csv(indices_df, name="sobol_indices")
    print(f"  Indices exported to: {csv_path}")

    # Export summary report
    summary = {
        "method": "Sobol (Global Sensitivity Analysis)",
        "samples": len(samples),
        "generations": 100,
        "most_important": ranked.iloc[0]["param"],
        "st_sum": float(indices.ST.sum()),
    }
    report_path = exporter.export_summary_report(summary, name="sobol_summary")
    print(f"  Summary report: {report_path}")

    # Export batch results
    results_path = exporter.export_batch_results_to_csv(
        results, name="sobol_batch_results"
    )
    print(f"  Batch results: {results_path}")

    # Step 8: Detect second-order interactions (optional)
    print("\nStep 7: Checking for second-order interactions (computing S2)...")
    print("  (Note: Re-computing with calc_second_order=True for S2 matrix)")

    # For second-order analysis, need to re-sample with calc_second_order=True
    samples_s2 = batch_sim.generate_samples("saltelli", 32, calc_second_order=True)
    results_s2 = batch_sim.run_batch(samples_s2, generations=100, seed=43)
    indices_s2 = analyzer.analyze(
        results_s2, output_col="survival", calc_second_order=True
    )

    # Detect high interactions
    interactions = analyzer.detect_interactions(indices_s2, threshold=0.05)
    if interactions:
        print(f"  Found {len(interactions)} significant interactions (S2 > 0.05):")
        for p1, p2, s2_val in interactions[:5]:
            print(f"    {p1} × {p2}: S2 = {s2_val:.4f}")
    else:
        print("  No significant interactions detected")

    print(f"\n✓ Sobol workflow complete!")
    print(f"  Output directory: {output_dir}")


if __name__ == "__main__":
    main()
