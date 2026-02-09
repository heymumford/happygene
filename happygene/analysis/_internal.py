"""
Shared utilities for sensitivity analysis module.

Provides:
- SeedManager: Deterministic sub-seed generation
- ParameterValidator: Input validation
- Helper functions: denormalize, generate_run_id, etc.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from pathlib import Path


class SeedManager:
    """Generate deterministic sub-seeds from master seed.

    Ensures reproducibility while providing unique seed per simulation.

    Parameters
    ----------
    master_seed : int
        Master random seed (0 to 2^31-1).
    """

    def __init__(self, master_seed: int):
        """Initialize with master seed."""
        self.master_seed = master_seed
        self.rng = np.random.default_rng(master_seed)

    def get_seed(self, sample_idx: int) -> int:
        """Get deterministic seed for sample index.

        Parameters
        ----------
        sample_idx : int
            Sample index (0-based).

        Returns
        -------
        int
            Deterministic seed for this sample.
        """
        # Generate unique seed for this index (deterministic from master)
        sub_rng = np.random.default_rng(self.master_seed + sample_idx)
        return int(sub_rng.integers(0, 2**31 - 1))


class ParameterValidator:
    """Validate parameter bounds and sample arrays."""

    @staticmethod
    def validate_param_space(param_space: Dict[str, Tuple[float, float]]) -> None:
        """Validate parameter space dictionary.

        Parameters
        ----------
        param_space : dict[str, tuple[float, float]]
            Parameter bounds. Example: {'rate': (0.0, 1.0)}

        Raises
        ------
        ValueError
            If invalid (empty, bounds reversed, negative).
        """
        if not param_space:
            raise ValueError("param_space cannot be empty")

        for pname, (low, high) in param_space.items():
            if low >= high:
                raise ValueError(
                    f"Parameter '{pname}': lower bound ({low}) must be < upper bound ({high})"
                )
            if low < 0 or high < 0:
                raise ValueError(
                    f"Parameter '{pname}': bounds must be non-negative"
                )

    @staticmethod
    def validate_samples(samples: np.ndarray, n_params: int) -> None:
        """Validate sample array.

        Parameters
        ----------
        samples : np.ndarray
            Sample matrix (n_samples, n_params).
        n_params : int
            Expected number of parameters.

        Raises
        ------
        ValueError
            If shape/values invalid.
        """
        if samples.ndim != 2:
            raise ValueError(f"samples must be 2D, got {samples.ndim}D")

        if samples.shape[1] != n_params:
            raise ValueError(
                f"samples has {samples.shape[1]} params, expected {n_params}"
            )

        if not np.all(np.isfinite(samples)):
            raise ValueError("samples contains NaN or inf values")

        if not (np.all(samples >= 0.0) and np.all(samples <= 1.0)):
            raise ValueError("samples must be in [0, 1] (normalized)")


def denormalize_samples(
    samples_norm: np.ndarray,
    param_space: Dict[str, Tuple[float, float]],
    param_names: list,
) -> np.ndarray:
    """Convert normalized [0, 1] samples to actual parameter ranges.

    Parameters
    ----------
    samples_norm : np.ndarray
        Normalized samples (n_samples, n_params) with values in [0, 1].
    param_space : dict[str, tuple]
        Parameter bounds.
    param_names : list[str]
        Parameter names in column order.

    Returns
    -------
    np.ndarray
        Denormalized samples (n_samples, n_params) in actual ranges.
    """
    denorm = np.zeros_like(samples_norm, dtype=np.float64)

    for i, pname in enumerate(param_names):
        low, high = param_space[pname]
        denorm[:, i] = samples_norm[:, i] * (high - low) + low

    return denorm


def generate_run_id(sample_idx: int, seed: int) -> str:
    """Create unique run identifier for traceability.

    Parameters
    ----------
    sample_idx : int
        Sample index (0-based).
    seed : int
        Random seed for this run.

    Returns
    -------
    str
        Unique run identifier (e.g., 'run_0042_seed_12345').
    """
    return f"run_{sample_idx:05d}_seed_{seed}"
