"""
CLI Config Loading Tests - RED Phase

Tests define expected behavior for loading simulation config from files.
All tests should fail initially (RED phase) until implementation complete.
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from engine.config.loaders import load_config_from_file, load_config_from_yaml, load_config_from_json
from engine.domain.config import HappyGeneConfig, KineticsConfig, SolverMethod


class TestYAMLConfigLoading:
    """Test YAML configuration file loading."""

    def test_load_config_from_yaml_file(self) -> None:
        """Config loader can read YAML file and return HappyGeneConfig."""
        yaml_content = """
kinetics:
  method: BDF
  rtol: 1e-6
  atol: 1e-9
  max_step: 1.0
simulation:
  time_end: 1000.0
  num_steps: 100
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()

            config = load_config_from_yaml(Path(f.name))

            assert isinstance(config, HappyGeneConfig)
            assert config.kinetics.method == SolverMethod.BDF
            assert config.kinetics.rtol == 1e-6
            assert config.kinetics.atol == 1e-9

    def test_load_config_from_file_with_yaml_extension(self) -> None:
        """Generic loader detects .yaml extension and delegates to YAML loader."""
        yaml_content = """
kinetics:
  method: RK45
  rtol: 1e-5
  atol: 1e-8
  max_step: 2.0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()

            config = load_config_from_file(Path(f.name))

            assert config.kinetics.method == SolverMethod.RK45

    def test_yaml_loader_raises_file_not_found(self) -> None:
        """YAML loader raises FileNotFoundError if file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config_from_yaml(Path("/nonexistent/config.yaml"))

    def test_yaml_loader_raises_on_invalid_syntax(self) -> None:
        """YAML loader raises ValueError on invalid YAML syntax."""
        invalid_yaml = """
kinetics:
  method: BDF
  rtol: [invalid yaml here
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()

            with pytest.raises(ValueError):
                load_config_from_yaml(Path(f.name))


class TestJSONConfigLoading:
    """Test JSON configuration file loading."""

    def test_load_config_from_json_file(self) -> None:
        """Config loader can read JSON file and return HappyGeneConfig."""
        json_content = {
            "kinetics": {
                "method": "BDF",
                "rtol": 1e-6,
                "atol": 1e-9,
                "max_step": 1.0
            },
            "simulation": {
                "time_end": 1000.0,
                "num_steps": 100
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_content, f)
            f.flush()

            config = load_config_from_json(Path(f.name))

            assert isinstance(config, HappyGeneConfig)
            assert config.kinetics.method == SolverMethod.BDF

    def test_load_config_from_file_with_json_extension(self) -> None:
        """Generic loader detects .json extension and delegates to JSON loader."""
        json_content = {
            "kinetics": {
                "method": "RK45",
                "rtol": 1e-5,
                "atol": 1e-8,
                "max_step": 2.0
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_content, f)
            f.flush()

            config = load_config_from_file(Path(f.name))

            assert config.kinetics.method == SolverMethod.RK45

    def test_json_loader_raises_file_not_found(self) -> None:
        """JSON loader raises FileNotFoundError if file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config_from_json(Path("/nonexistent/config.json"))

    def test_json_loader_raises_on_invalid_syntax(self) -> None:
        """JSON loader raises ValueError on invalid JSON syntax."""
        invalid_json = '{"kinetics": {"method": "BDF"'  # Incomplete JSON

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            f.flush()

            with pytest.raises(ValueError):
                load_config_from_json(Path(f.name))


class TestConfigFileFormatDetection:
    """Test format auto-detection for generic loader."""

    def test_unsupported_file_format_raises_error(self) -> None:
        """Generic loader raises ValueError for unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some text")
            f.flush()

            with pytest.raises(ValueError, match="Unsupported format"):
                load_config_from_file(Path(f.name))

    def test_config_validation_on_load(self) -> None:
        """Loaded config must pass validation (rtol > 0, atol > 0)."""
        invalid_yaml = """
kinetics:
  method: BDF
  rtol: -1e-6
  atol: 1e-9
  max_step: 1.0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()

            with pytest.raises(ValueError):
                load_config_from_yaml(Path(f.name))
