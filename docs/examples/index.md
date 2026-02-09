# Examples

Complete, runnable Jupyter notebook examples demonstrating HappyGene workflows.

## Quick Links

| Notebook | Time | Level | Topic |
|----------|------|-------|-------|
| [01: Hello World](https://github.com/heymumford/happygene/blob/main/docs/examples/01_hello_world.ipynb) | 5 min | Beginner | Single simulation |
| [02: Batch Processing](https://github.com/heymumford/happygene/blob/main/docs/examples/02_batch_processing.ipynb) | 15 min | Beginner | Batch runs & statistics |
| [03: Visualization](https://github.com/heymumford/happygene/blob/main/docs/examples/03_visualization.ipynb) | 15 min | Intermediate | Dashboards & exports |
| [04: COPASI Integration](https://github.com/heymumford/happygene/blob/main/docs/examples/04_copasi_workflow.ipynb) | 20 min | Advanced | SBML export/import |
| [05: Parameter Sensitivity](https://github.com/heymumford/happygene/blob/main/docs/examples/05_parameter_sensitivity.ipynb) | 20 min | Advanced | Parameter sweeps |

## Learning Path

### For New Users
Start with notebooks in this order:
1. **01_hello_world** - Understand basic concepts
2. **02_batch_processing** - Learn production workflows
3. **03_visualization** - Create publication-ready plots

### For Researchers
Focus on these:
1. **04_copasi_workflow** - Interoperability with COPASI
2. **05_parameter_sensitivity** - Experimental design and analysis

### For Power Users
1. Run all notebooks to understand full pipeline
2. Adapt examples for your specific use case
3. Combine techniques for complex workflows

## Running Notebooks

### Prerequisites
```bash
pip install happygene jupyter
```

### Launch Jupyter
```bash
cd docs/examples
jupyter notebook
```

### Run in Google Colab
```
https://colab.research.google.com/github/heymumford/happygene/blob/main/docs/examples/
```

## Notebook Details

### 01_hello_world.ipynb
Your first DNA repair simulation in 5 minutes.

**You'll learn:**
- How to create a simulation configuration
- How to run a single simulation
- How to interpret results

**Time**: 5 minutes
**Difficulty**: Beginner
**Code cells**: 95

### 02_batch_processing.ipynb
Run 100+ simulations and analyze aggregate statistics.

**You'll learn:**
- How to run multiple simulations efficiently
- How to compute mean, std, min, max statistics
- How to save and load results in HDF5 format

**Time**: 15 minutes
**Difficulty**: Beginner-Intermediate
**Code cells**: 110

### 03_visualization.ipynb
Create interactive dashboards and publication-ready plots.

**You'll learn:**
- How to create time series plots
- How to visualize distributions
- How to build interactive dashboards
- How to export to PDF/PNG/HTML

**Time**: 15 minutes
**Difficulty**: Intermediate
**Code cells**: 105

### 04_copasi_workflow.ipynb
Use HappyGene with COPASI via SBML export/import.

**You'll learn:**
- How to export configuration to SBML (for COPASI)
- How to import SBML files back to HappyGene
- How to verify round-trip fidelity
- COPASI workflow integration

**Time**: 20 minutes
**Difficulty**: Advanced
**Code cells**: 115

### 05_parameter_sensitivity.ipynb
Systematically vary parameters to understand their effects.

**You'll learn:**
- How to create parameter sweeps
- How to compare outcomes across parameter ranges
- How to identify key factors
- How to create sensitivity analyses

**Time**: 20 minutes
**Difficulty**: Advanced
**Code cells**: 100

## Next Steps

After working through the examples:

1. **Explore the API**: See [API Reference](../api-reference.md)
2. **Read the User Guide**: See [User Guide](../user-guide.md)
3. **Contribute**: See [Contributing](https://github.com/heymumford/happygene/blob/main/CONTRIBUTING.md)
4. **Ask Questions**: [GitHub Issues](https://github.com/heymumford/happygene/issues)

## Common Issues

**Issue**: Notebooks won't run
- **Solution**: Verify installation with `pip show happygene`

**Issue**: COPASI export fails
- **Solution**: See 04_copasi_workflow for proper SBML handling

**Issue**: Visualization doesn't display
- **Solution**: Ensure Plotly is installed: `pip install plotly`

## Tips

- Run notebooks in order (01 → 02 → 03 → etc.)
- Don't skip the markdown cells - they explain concepts
- Modify code cells and re-run to experiment
- Save outputs before running next notebook
- Use notebooks as templates for your own analyses
