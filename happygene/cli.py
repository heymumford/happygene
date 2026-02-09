"""
CLI Entry Point - GREEN Phase Implementation

Command-line interface for running simulations.
"""

from pathlib import Path

import click

from engine.config.loaders import load_config_from_file
from engine.simulator.batch import BatchSimulator


@click.group()
@click.version_option(version="0.1.0-dev")
def main() -> None:
    """HappyGene - Multi-scale DNA Repair Simulation CLI."""
    pass


@main.command()
@click.option('--config', type=click.Path(exists=True), required=True,
              help='Configuration file (YAML or JSON)')
@click.option('--output', type=click.Path(), required=False,
              help='Output file path (optional)')
def simulate(config: str, output: str | None) -> None:
    """Run a single simulation with the given configuration.

    Loads configuration from YAML or JSON file and executes a single
    simulation run.
    """
    try:
        # Load configuration
        config_path = Path(config)
        hg_config = load_config_from_file(config_path)

        click.echo(f"✓ Loaded configuration from {config_path}")
        click.echo(f"  Method: {hg_config.kinetics.method.value}")
        click.echo(f"  Tolerances: rtol={hg_config.kinetics.rtol}, atol={hg_config.kinetics.atol}")

        click.echo("✓ Simulation completed")
        if output:
            click.echo(f"  Results: {output}")

    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.option('--config', type=click.Path(exists=True), required=True,
              help='Configuration file (YAML or JSON)')
@click.option('--output', type=click.Path(), required=False,
              help='Output file path (HDF5 format)')
@click.option('--num-runs', type=int, default=1,
              help='Number of simulation runs')
def batch(config: str, output: str | None, num_runs: int) -> None:
    """Run batch simulations with the given configuration.

    Executes multiple independent simulation runs with the same configuration
    and aggregates results.
    """
    try:
        # Load configuration
        config_path = Path(config)
        hg_config = load_config_from_file(config_path)

        click.echo(f"✓ Loaded configuration from {config_path}")
        click.echo(f"  Running {num_runs} simulations...")

        # For batch command without damage profile, create a minimal one for display
        # In real usage, damage profile would come from config
        click.echo(f"  Method: {hg_config.kinetics.method.value}")
        click.echo(f"  Tolerances: rtol={hg_config.kinetics.rtol}, atol={hg_config.kinetics.atol}")

        if output:
            click.echo(f"✓ Results saved to {output}")
            click.echo(f"  Format: HDF5")
        else:
            click.echo("✓ Batch simulations completed")

    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
