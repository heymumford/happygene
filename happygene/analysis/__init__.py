"""
HappyGene Sensitivity Analysis Module

Provides global sensitivity analysis (Sobol indices, Morris screening),
parameter interaction analysis, and publication-ready output generation.

Quick Start
-----------
```python
from happygene.analysis.batch import BatchSimulator
from happygene.analysis.sobol import SobolAnalyzer

# Create batch simulator
sim = BatchSimulator(model_factory, param_space, seed=42)
samples = sim.generate_samples(256, sampler='sobol')
results = sim.run_batch(samples, n_generations=100)

# Analyze with Sobol indices
sobol = SobolAnalyzer(param_names, param_space)
indices = sobol.analyze(results, output_col='survival')
ranked = sobol.rank_parameters(indices, by='ST')
print(ranked)
```

Modules
-------
- batch : BatchSimulator for reproducible batch execution
- sobol : SobolAnalyzer for global sensitivity analysis
- morris : MorrisAnalyzer for fast parameter screening
- correlation : CorrelationAnalyzer for parameter interactions
- response : ResponseSurfaceModel for surrogate modeling
- output : OutputExporter for publication-ready plots/exports
"""

from .batch import BatchSimulator
from .sobol import SobolAnalyzer, SobolIndices
from .morris import MorrisAnalyzer, MorrisIndices
from .correlation import CorrelationAnalyzer
from .response import ResponseSurfaceModel
from .output import OutputExporter

__all__ = [
    "BatchSimulator",
    "SobolAnalyzer",
    "SobolIndices",
    "MorrisAnalyzer",
    "MorrisIndices",
    "CorrelationAnalyzer",
    "ResponseSurfaceModel",
    "OutputExporter",
]
