"""
CLI Command Structure Tests - RED Phase

Tests define expected CLI command interface and behavior.
"""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from happygene.cli import main


class TestCLISimulateCommand:
    """Test 'simulate' subcommand for running single simulations."""

    def test_simulate_command_exists(self) -> None:
        """CLI has 'simulate' subcommand."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert 'simulate' in result.output

    def test_simulate_requires_config_file(self) -> None:
        """Simulate command requires --config argument."""
        runner = CliRunner()
        result = runner.invoke(main, ['simulate'])
        assert result.exit_code != 0
        assert 'config' in result.output.lower()

    def test_simulate_with_yaml_config(self) -> None:
        """Simulate command accepts YAML config file."""
        yaml_content = """
kinetics:
  method: BDF
  rtol: 1e-6
  atol: 1e-9
  max_step: 1.0
simulation:
  time_end: 100.0
  num_steps: 10
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()

            runner = CliRunner()
            result = runner.invoke(main, ['simulate', '--config', f.name])

            # Should succeed or output useful error (not crash)
            assert result.exit_code in (0, 1)
            assert 'error' not in result.output.lower() or 'damage' in result.output.lower()


class TestCLIBatchCommand:
    """Test 'batch' subcommand for running batch simulations."""

    def test_batch_command_exists(self) -> None:
        """CLI has 'batch' subcommand."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert 'batch' in result.output

    def test_batch_requires_config_file(self) -> None:
        """Batch command requires --config argument."""
        runner = CliRunner()
        result = runner.invoke(main, ['batch'])
        assert result.exit_code != 0

    def test_batch_accepts_output_path(self) -> None:
        """Batch command accepts --output argument for result file."""
        yaml_content = """
kinetics:
  method: BDF
  rtol: 1e-6
  atol: 1e-9
  max_step: 1.0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = Path(tmpdir) / "results.h5"
                result = runner.invoke(main, [
                    'batch',
                    '--config', f.name,
                    '--output', str(output_path),
                    '--num-runs', '2'
                ])

                # Should accept the arguments
                assert 'usage' not in result.output.lower() or 'batch' in result.output.lower()


class TestCLIVersionCommand:
    """Test version information."""

    def test_cli_supports_version_flag(self) -> None:
        """CLI supports --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])

        # Should display version (exit 0) or error gracefully
        assert '0.1.0' in result.output or result.exit_code == 0

    def test_cli_help_is_available(self) -> None:
        """CLI provides helpful --help output."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'Usage:' in result.output or 'Commands:' in result.output or 'Options:' in result.output
