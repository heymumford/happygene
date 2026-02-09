
# Copyright (C) 2026 Eric C. Mumford <ericmumford@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Configuration File Loaders

Loads HappyGeneConfig from YAML or JSON configuration files with validation.

Supported Formats:
- YAML (.yaml, .yml): Human-readable configuration
- JSON (.json): Machine-readable configuration

Examples:
    >>> config = load_config_from_file("config.yaml")
    >>> kinetics = config.kinetics
"""

import json
from pathlib import Path
from typing import Any, Dict, Union

import yaml
from pydantic import ValidationError

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
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    suffix = config_path.suffix.lower()

    if suffix == ".yaml" or suffix == ".yml":
        return load_config_from_yaml(config_path)
    elif suffix == ".json":
        return load_config_from_json(config_path)
    else:
        raise ValueError(
            f"Unsupported format: {suffix}. Supported formats: .yaml, .json"
        )


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
    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    try:
        with open(yaml_path) as f:
            config_dict: Dict[str, Any] = yaml.safe_load(f)

        if config_dict is None:
            config_dict = {}

        return HappyGeneConfig(**config_dict)

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax: {e}") from e
    except ValidationError as e:
        raise ValueError(f"Configuration validation failed: {e}") from e


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
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    try:
        with open(json_path) as f:
            config_dict: Dict[str, Any] = json.load(f)

        return HappyGeneConfig(**config_dict)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON syntax: {e}") from e
    except ValidationError as e:
        raise ValueError(f"Configuration validation failed: {e}") from e
