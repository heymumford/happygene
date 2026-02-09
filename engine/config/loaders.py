"""
Configuration Loaders - RED Phase Placeholder

Loads HappyGeneConfig from YAML or JSON files.
Implementation will be done in GREEN phase.
"""

from pathlib import Path
from typing import Union

from engine.domain.config import HappyGeneConfig


def load_config_from_file(config_path: Union[str, Path]) -> HappyGeneConfig:
    """
    Load configuration from file.

    Detects format (.yaml, .json) and delegates to appropriate loader.

    Args:
        config_path: Path to configuration file

    Returns:
        HappyGeneConfig parsed from file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If format unsupported or file invalid
    """
    raise NotImplementedError("load_config_from_file not yet implemented")


def load_config_from_yaml(yaml_path: Union[str, Path]) -> HappyGeneConfig:
    """
    Load configuration from YAML file.

    Args:
        yaml_path: Path to YAML configuration file

    Returns:
        HappyGeneConfig parsed from YAML

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML invalid or validation fails
    """
    raise NotImplementedError("load_config_from_yaml not yet implemented")


def load_config_from_json(json_path: Union[str, Path]) -> HappyGeneConfig:
    """
    Load configuration from JSON file.

    Args:
        json_path: Path to JSON configuration file

    Returns:
        HappyGeneConfig parsed from JSON

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON invalid or validation fails
    """
    raise NotImplementedError("load_config_from_json not yet implemented")
