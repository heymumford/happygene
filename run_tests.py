#!/usr/bin/env python3
"""Run tests and capture coverage metrics."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/", "-v", "--tb=short",
     "--cov=happygene", "--cov-report=term-missing"],
    cwd="/Users/vorthruna/ProjectsWATTS/happygene"
)

sys.exit(result.returncode)
