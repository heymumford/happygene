"""
HappyGene - Multi-scale DNA Repair Simulation

Interdependent, parameterized simulations modeling DNA repair mechanisms.
"""

__version__ = "0.1.0-dev"
__author__ = "Eric C. Mumford"
__license__ = "GPL-3.0-or-later"

# Re-export main entry point
from happygene.cli import main

__all__ = ["main", "__version__"]
