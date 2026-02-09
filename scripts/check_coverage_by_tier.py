#!/usr/bin/env python
"""
Enforce tier-based coverage thresholds for happygene.

Tiers:
- Tier 1 (Critical): 100% coverage required
  Examples: datacollector.py, regulatory_network.py, entities.py
- Tier 2 (Computation): 90% coverage required
  Examples: expression.py, selection.py, mutation.py
- Tier 3 (Utility): 70% coverage required
  Examples: analysis/*.py, base.py helpers
- Tier 4 (Legacy): 50% coverage acceptable
  Examples: deprecated code

This script reads coverage.json and enforces thresholds per tier.
Fails with non-zero exit if any file falls below its tier threshold.
"""

import json
import sys
import re
from pathlib import Path


# Define tier classification
TIER_RULES = {
    "tier1": {
        "coverage_target": 100,
        "patterns": [
            "datacollector.py",
            "regulatory_network.py",
            "entities.py",
            "base.py",  # Core simulation base
        ],
        "description": "Critical (Persistence/Domain Model)",
    },
    "tier2": {
        "coverage_target": 90,
        "patterns": [
            "expression.py",
            "selection.py",
            "mutation.py",
            "conditions.py",
            "regulatory_expression.py",
        ],
        "description": "Computation (Gene Models)",
    },
    "tier3": {
        "coverage_target": 70,
        "patterns": [
            "analysis/",
            "model.py",
        ],
        "description": "Utility (Analysis/Helpers)",
    },
    "tier4": {
        "coverage_target": 50,
        "patterns": [
            "deprecated/",
            "legacy/",
        ],
        "description": "Legacy (Pending Refactor)",
    },
}


def classify_file(file_path: str) -> tuple[str, int, str]:
    """
    Classify file by tier and return (tier_name, threshold, description).

    Args:
        file_path: Path to Python file

    Returns:
        (tier_name, coverage_threshold, description)
    """
    file_path = file_path.lower()

    # Check each tier in order
    for tier_name, tier_config in TIER_RULES.items():
        for pattern in tier_config["patterns"]:
            if pattern.lower() in file_path:
                return (
                    tier_name,
                    tier_config["coverage_target"],
                    tier_config["description"],
                )

    # Default to Tier 3 if not classified
    return ("tier3", 70, "Utility (Default)")


def main():
    """Load coverage.json and enforce tier-based thresholds."""
    coverage_file = Path("coverage.json")

    if not coverage_file.exists():
        print("ERROR: coverage.json not found. Run pytest with --cov-report=json first.")
        sys.exit(1)

    with open(coverage_file) as f:
        coverage_data = json.load(f)

    failures = []
    warnings = []
    passes = []

    print("\n" + "=" * 80)
    print("TIER-BASED COVERAGE ENFORCEMENT")
    print("=" * 80 + "\n")

    # Check each file
    for file_path, file_coverage in coverage_data["files"].items():
        coverage_percent = file_coverage["summary"]["percent_covered"]
        tier_name, threshold, description = classify_file(file_path)

        # Format output
        status = "✓" if coverage_percent >= threshold else "✗"
        file_short = file_path.replace("happygene/", "")

        if coverage_percent >= threshold:
            passes.append((file_short, coverage_percent, tier_name, description))
            print(f"{status} {file_short:45} {coverage_percent:6.1f}% ({tier_name}: {description})")
        else:
            failures.append(
                (
                    file_short,
                    coverage_percent,
                    threshold,
                    tier_name,
                    description,
                )
            )
            print(
                f"{status} {file_short:45} {coverage_percent:6.1f}% "
                f"(FAIL: need {threshold}% for {tier_name})"
            )

    # Summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(passes)} passed, {len(failures)} FAILED")
    print("=" * 80 + "\n")

    if failures:
        print("FAILURES (below tier threshold):\n")
        for file_short, actual, threshold, tier_name, description in failures:
            print(f"  {file_short}")
            print(f"    Tier: {tier_name} ({description})")
            print(f"    Coverage: {actual:.1f}% (need {threshold}%)")
            print(f"    Gap: {threshold - actual:.1f} percentage points\n")

        print(f"FIX: Increase coverage for {len(failures)} file(s) to meet thresholds.")
        sys.exit(1)

    print("✓ All files meet tier-based coverage requirements!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
