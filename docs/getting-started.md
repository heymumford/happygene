# Getting Started

Get HappyGene running in 5 minutes.

## Installation

### Requirements
- Python 3.12+
- pip or uv package manager

### Install from PyPI

```bash
pip install happygene
```

### Verify Installation

```bash
happygene --version
# Output: happygene, version 0.1.0
```

## Your First Simulation

### 1. Create a Configuration File

Save as `config.yaml`:

```yaml
damage:
  dose_gy: 3.0
  population_size: 1000

kinetics:
  recognition_rate: 0.1
  repair_rate: 0.05
  misrepair_rate: 0.01
```

### 2. Run a Simulation

```bash
happygene simulate --config config.yaml
```

Output:
```
Simulation completed:
- Final repair count: 945 of 1000 lesions
- Completion time: 0.125 seconds
```

### 3. Run Batch Simulations

```bash
happygene batch --config config.yaml --num-runs 100 --output results.h5
```

This runs 100 independent simulations and saves aggregated statistics.

## Programmatic Usage

### Single Simulation

```python
from engine.simulator.runner import SimulationRunner
from engine.domain.config import HappyGeneConfig, DamageProfile, KineticsConfig

# Create config
damage = DamageProfile(dose_gy=3.0, population_size=1000)
kinetics = KineticsConfig(
    recognition_rate=0.1,
    repair_rate=0.05,
    misrepair_rate=0.01
)
config = HappyGeneConfig(damage_profile=damage, kinetics=kinetics)

# Run simulation
runner = SimulationRunner(config)
results = runner.run()

print(f"Repairs: {results['final_repair_count']}")
print(f"Time: {results['completion_time']:.3f}s")
```

### Batch Simulations

```python
from engine.simulator.batch import BatchSimulator

batch = BatchSimulator(config)
results = batch.run_batch(num_runs=100)
stats = BatchSimulator.compute_statistics(results)

print(f"Mean repairs: {stats['mean_repair_count']:.1f}")
print(f"Std dev: {stats['std_repair_count']:.1f}")
```

### Visualization

```python
from engine.visualization.dashboard import create_dashboard

dashboard = create_dashboard(results)
dashboard.save_html("dashboard.html")
```

## Next Steps

- [User Guide](user-guide.md) - Detailed configuration options
- [Tutorials](tutorials/) - Domain-specific workflows
- [API Reference](api-reference.md) - Complete function reference
- [Examples](examples/) - Jupyter notebooks

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'happygene'`
- **Solution**: Verify installation with `pip show happygene`

**Issue**: Config file not found
- **Solution**: Use absolute path or verify file exists: `ls -la config.yaml`

**Issue**: Simulation too slow
- **Solution**: See [Performance Guide](performance.md) for optimization tips

## Getting Help

- Check the [FAQ](faq.md)
- Search [GitHub Issues](https://github.com/heymumford/happygene/issues)
- Ask in [GitHub Discussions](https://github.com/heymumford/happygene/discussions)
