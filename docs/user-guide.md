# User Guide

Comprehensive guide to using HappyGene for DNA repair simulations.

## Table of Contents
1. [Configuration](#configuration)
2. [Running Simulations](#running-simulations)
3. [Output Analysis](#output-analysis)
4. [Visualization](#visualization)
5. [COPASI Integration](#copasi-integration)
6. [Performance Tips](#performance-tips)

## Configuration

### File Formats

HappyGene supports YAML and JSON configuration files.

**YAML Format** (recommended):
```yaml
# config.yaml
damage:
  dose_gy: 3.0
  population_size: 1000
  lesion_distribution:
    DSB: 0.30
    SSB: 0.40
    BER: 0.30

kinetics:
  recognition_rate: 0.1
  repair_rate: 0.05
  misrepair_rate: 0.01
  recovery_rate: 0.02
```

**JSON Format**:
```json
{
  "damage": {
    "dose_gy": 3.0,
    "population_size": 1000,
    "lesion_distribution": {
      "DSB": 0.30,
      "SSB": 0.40,
      "BER": 0.30
    }
  },
  "kinetics": {
    "recognition_rate": 0.1,
    "repair_rate": 0.05,
    "misrepair_rate": 0.01,
    "recovery_rate": 0.02
  }
}
```

### Configuration Parameters

#### Damage Profile
- `dose_gy`: Radiation dose in Gray (0-10 typical range)
- `population_size`: Initial cell population (100-100,000)
- `lesion_distribution`: Fraction of each lesion type (must sum to 1.0)

#### Kinetics
- `recognition_rate`: Rate of damage recognition per second (0.01-1.0)
- `repair_rate`: Base repair rate (0.01-0.5)
- `misrepair_rate`: Probability of unsuccessful repair (0-0.1)
- `recovery_rate`: Post-repair recovery rate (0.001-0.1)

### Loading Configuration Programmatically

```python
from engine.config.loaders import load_config_from_file

config = load_config_from_file("config.yaml")
# or
config = load_config_from_file("config.json")
```

## Running Simulations

### CLI: Single Simulation

```bash
happygene simulate --config config.yaml
```

Output includes:
- Final repair count
- Completion time
- Repair statistics

### CLI: Batch Simulations

```bash
happygene batch \
    --config config.yaml \
    --num-runs 100 \
    --output results.h5
```

Saves HDF5 file with:
- Individual run results
- Aggregated statistics
- Metadata (timestamp, config hash)

### Programmatic: Single Run

```python
from engine.simulator.runner import SimulationRunner
from engine.config.loaders import load_config_from_file

config = load_config_from_file("config.yaml")
runner = SimulationRunner(config)

results = runner.run()
# results: {
#     'run_id': 1,
#     'completion_time': 0.125,
#     'final_repair_count': 945,
#     'status': 'complete',
#     'damage_profile': {...},
#     'kinetics': {...}
# }
```

### Programmatic: Batch Runs

```python
from engine.simulator.batch import BatchSimulator

batch = BatchSimulator(config)
results = batch.run_batch(num_runs=100)

# Save results
batch.save_results(results, "output.h5")

# Get statistics
stats = BatchSimulator.compute_statistics(results)
print(f"Mean repair time: {stats['mean_repair_time']:.3f}s")
print(f"Mean repairs: {stats['mean_repair_count']:.0f}")
```

## Output Analysis

### Understanding Results

Each run produces:
```python
{
    'run_id': int,
    'completion_time': float,  # seconds
    'final_repair_count': int,  # lesions repaired
    'status': str,              # 'complete' or 'timeout'
    'damage_profile': {...},    # Initial configuration
    'kinetics': {...}           # Rate constants used
}
```

### Computing Statistics

```python
from engine.simulator.batch import BatchSimulator

stats = BatchSimulator.compute_statistics(results)

# Access statistics
mean_time = stats['mean_repair_time']
std_time = stats['std_repair_time']
min_time = stats['min_repair_time']
max_time = stats['max_repair_time']

mean_repairs = stats['mean_repair_count']
std_repairs = stats['std_repair_count']
```

### Loading Saved Results

```python
from engine.simulator.batch import BatchSimulator

# Load from HDF5
results = BatchSimulator.load_results("output.h5")

# Load from JSON
import json
results = json.load(open("output.json"))
```

## Visualization

### Interactive Dashboard

```python
from engine.visualization.dashboard import create_dashboard

dashboard = create_dashboard(batch_results)
dashboard.save_html("dashboard.html")
```

Includes:
- Time series plot
- Distribution histogram
- Statistics summary
- Interactive Plotly elements

### Individual Plots

```python
from engine.visualization.plotter import (
    plot_repair_time_series,
    plot_repair_distribution,
    plot_statistics_summary
)

# Time series
fig1 = plot_repair_time_series(results)
fig1.show()

# Distribution
fig2 = plot_repair_distribution(results)
fig2.show()

# Statistics
fig3 = plot_statistics_summary(stats)
fig3.show()
```

### Exporting Plots

```python
from engine.visualization.exporter import Exporter, ExportFormat

exporter = Exporter(ExportFormat.PDF)
exporter.export(fig1, "plot.pdf")

# Also supports HTML and PNG
```

## COPASI Integration

### Export to SBML

```python
from engine.io.sbml_export import export_to_sbml

export_to_sbml(config, "simulation.xml")
```

Creates SBML Level 3 v2 file compatible with COPASI.

### Import from COPASI

```python
from engine.io.sbml_import import import_from_sbml

config = import_from_sbml("copasi_export.xml")
```

Recovers damage profile and kinetics parameters.

### Round-Trip Validation

```python
from engine.io.sbml_export import export_to_sbml
from engine.io.sbml_import import import_from_sbml

# Export
export_to_sbml(original_config, "temp.xml")

# Import
recovered_config = import_from_sbml("temp.xml")

# Verify
assert original_config == recovered_config
```

## Performance Tips

### Batch Size Optimization

```python
# Good: Let HappyGene optimize
batch.run_batch(num_runs=1000)

# Avoid: Too small batches
for i in range(1000):
    batch.run_batch(num_runs=1)  # Slow!
```

### Memory Usage

```python
# For large batches, process in chunks
batch_size = 100
all_results = []

for i in range(0, 10000, batch_size):
    results = batch.run_batch(num_runs=batch_size)
    all_results.extend(results)
    # Process and save before next chunk
```

### Parameter Sweeps

```python
# Avoid nested loops
for dose in doses:
    for repair_rate in rates:
        config = update_config(dose, repair_rate)
        batch.run_batch(num_runs=10)  # Repeats config loading

# Instead: Use batch processing with different configs
configs = [update_config(d, r) for d in doses for r in rates]
all_results = {}
for cfg in configs:
    all_results[cfg_key] = BatchSimulator(cfg).run_batch(100)
```

## Troubleshooting

### Simulation Too Slow

1. Check recognition_rate (lower = longer)
2. Reduce population_size for testing
3. Use smaller batch size for memory

### High Misrepair Rate

Increase recovery_rate or decrease misrepair_rate in kinetics config.

### COPASI Import Fails

Verify SBML file is valid:
```bash
python -c "from engine.io.sbml_import import import_from_sbml; import_from_sbml('file.xml')"
```

## Next Steps

- [API Reference](api-reference.md) - Detailed function documentation
- [Tutorials](tutorials/) - Step-by-step workflows
- [Examples](examples/) - Jupyter notebooks
