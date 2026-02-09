# API Reference

Complete function and class documentation for HappyGene.

## Core Simulation

### SimulationRunner
Engine for single simulation execution.

```python
from engine.simulator.runner import SimulationRunner
from engine.domain.config import HappyGeneConfig

runner = SimulationRunner(config: HappyGeneConfig)
results = runner.run() -> Dict[str, Any]
```

**Parameters**:
- `config`: HappyGeneConfig with damage profile and kinetics

**Returns**: Dictionary with keys:
- `run_id`: Unique run identifier
- `completion_time`: Seconds elapsed
- `final_repair_count`: Total lesions repaired
- `status`: 'complete' or 'timeout'

**Example**:
```python
runner = SimulationRunner(config)
results = runner.run()
print(f"Repairs: {results['final_repair_count']}")
```

### BatchSimulator
Execute multiple independent simulations with aggregation.

```python
from engine.simulator.batch import BatchSimulator

batch = BatchSimulator(config: HappyGeneConfig)
results = batch.run_batch(num_runs: int) -> List[Dict]
```

**Methods**:
- `run_batch(num_runs)` - Run N independent simulations
- `save_results(results, output_path)` - Write to HDF5/JSON/CSV
- `load_results(output_path)` - Read results file
- `compute_statistics(results)` - Calculate aggregated stats

**Example**:
```python
batch = BatchSimulator(config)
results = batch.run_batch(num_runs=100)
stats = BatchSimulator.compute_statistics(results)
```

## Configuration

### HappyGeneConfig
Top-level simulation configuration.

```python
from engine.domain.config import HappyGeneConfig

config = HappyGeneConfig(
    damage_profile: DamageProfile,
    kinetics: KineticsConfig
)
```

### DamageProfile
Initial damage state.

```python
from engine.domain.config import DamageProfile

profile = DamageProfile(
    dose_gy: float,              # Radiation dose
    population_size: int,        # Initial cells
    lesion_distribution: Dict    # Type percentages
)
```

### KineticsConfig
Rate constants for damage-repair kinetics.

```python
from engine.domain.config import KineticsConfig

kinetics = KineticsConfig(
    recognition_rate: float,     # Damage recognition
    repair_rate: float,          # Repair completion
    misrepair_rate: float,       # Unsuccessful repair
    recovery_rate: float         # Post-repair recovery
)
```

## Configuration Loading

### load_config_from_file
Auto-detect and load config (YAML or JSON).

```python
from engine.config.loaders import load_config_from_file

config = load_config_from_file(path: str | Path) -> HappyGeneConfig
```

### load_config_from_yaml
Load from YAML file.

```python
config = load_config_from_yaml(path: str | Path) -> HappyGeneConfig
```

### load_config_from_json
Load from JSON file.

```python
config = load_config_from_json(path: str | Path) -> HappyGeneConfig
```

## Visualization

### plot_repair_time_series
Time series of repair count vs. completion time.

```python
from engine.visualization.plotter import plot_repair_time_series

fig = plot_repair_time_series(results: List[Dict]) -> go.Figure
```

### plot_repair_distribution
Histogram of repair count distribution.

```python
from engine.visualization.plotter import plot_repair_distribution

fig = plot_repair_distribution(results: List[Dict]) -> go.Figure
```

### plot_statistics_summary
Bar charts of aggregated statistics.

```python
from engine.visualization.plotter import plot_statistics_summary

fig = plot_statistics_summary(stats: Dict[str, float]) -> go.Figure
```

### create_dashboard
Multi-plot interactive dashboard.

```python
from engine.visualization.dashboard import create_dashboard

dashboard = create_dashboard(results: List[Dict]) -> Dashboard
```

**Dashboard Methods**:
- `to_html()` - Export to HTML string
- `save_html(path)` - Save to HTML file

### Exporter
Export plots to multiple formats.

```python
from engine.visualization.exporter import Exporter, ExportFormat

exporter = Exporter(format: ExportFormat)
exporter.export(figure: go.Figure, output_path: Path)
```

**Formats**:
- `ExportFormat.HTML` - Interactive web visualization
- `ExportFormat.PNG` - Static raster image
- `ExportFormat.PDF` - Publication-ready vector

## SBML I/O

### export_to_sbml
Export configuration to SBML Level 3 v2 (COPASI compatible).

```python
from engine.io.sbml_export import export_to_sbml

export_to_sbml(
    config: HappyGeneConfig,
    output_path: Path | str
) -> None
```

### import_from_sbml
Import configuration from SBML file.

```python
from engine.io.sbml_import import import_from_sbml

config = import_from_sbml(sbml_path: Path | str) -> HappyGeneConfig
```

### validate_sbml
Validate SBML file for compliance.

```python
from engine.io.sbml_validator import validate_sbml

is_valid, errors = validate_sbml(sbml_path: Path | str) -> Tuple[bool, List[str]]
```

## Output I/O

### OutputWriter
Write results to various formats.

```python
from engine.io.output import OutputWriter, OutputFormat

writer = OutputWriter()
writer.write(
    data: Dict[str, Any],
    output_path: Path,
    format: OutputFormat = OutputFormat.HDF5
)
```

**Formats**:
- `OutputFormat.HDF5` - Binary with compression (recommended)
- `OutputFormat.JSON` - Human-readable, interoperable
- `OutputFormat.CSV` - Spreadsheet format (Excel compatible)

## Domain Models

### DamageType
Enumeration of lesion types.

```python
from engine.domain.models import DamageType

# Available types:
DamageType.DSB   # Double-strand break
DamageType.SSB   # Single-strand break
DamageType.BER   # Base excision repair
DamageType.NER   # Nucleotide excision repair
DamageType.MMR   # Mismatch repair
```

### RepairPathway
Enumeration of repair mechanisms.

```python
from engine.domain.models import RepairPathway

# Available pathways:
RepairPathway.NHEJ           # Non-homologous end joining
RepairPathway.HR             # Homologous recombination
RepairPathway.BER            # Base excision repair
RepairPathway.MMR            # Mismatch repair
```

## CLI

### simulate
Run single simulation from command line.

```bash
happygene simulate --config CONFIG_FILE

Options:
  --config PATH  Configuration file (YAML/JSON) [required]
```

### batch
Run batch simulations from command line.

```bash
happygene batch --config CONFIG_FILE --num-runs N [--output OUTPUT]

Options:
  --config CONFIG_FILE   Configuration file [required]
  --num-runs N          Number of simulations [default: 1]
  --output OUTPUT       Output file (HDF5/JSON/CSV) [optional]
```

## Complete Examples

See [Examples](examples/) directory for runnable Jupyter notebooks:
- `01_hello_world.ipynb` - Basic usage
- `02_batch_processing.ipynb` - Batch simulations
- `03_visualization.ipynb` - Dashboards and plots
- `04_copasi_workflow.ipynb` - SBML round-trip
- `05_parameter_sensitivity.ipynb` - Parameter sweeps
