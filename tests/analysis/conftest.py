"""
Shared test fixtures for sensitivity analysis tests.

Provides:
- Simulation model factory
- Parameter space definitions
- Sample data generators
- Mock results for testing analyzers
"""


import numpy as np
import pandas as pd
import pytest

from engine.domain.config import KineticsConfig

# Import from main HappyGene engine (assumes in sys.path)


@pytest.fixture
def param_space():
    """Standard parameter space for DNA repair sensitivity analysis."""
    return {
        "recognition_rate": (0.01, 0.99),
        "repair_rate": (0.01, 0.99),
        "misrepair_rate": (0.01, 0.99),
        "recovery_rate": (0.01, 0.99),
        "dose_gy": (0.1, 10.0),
    }


@pytest.fixture
def sim_factory():
    """Factory function: params dict → configured simulation.

    Returns a callable that creates a HappyGeneConfig from parameter dict.
    For testing, returns a mock that stores parameters without full initialization.
    """

    def create_model(params):
        """Create HappyGeneConfig from parameter dictionary.

        Parameters
        ----------
        params : dict
            Keys: 'recognition_rate', 'repair_rate', 'misrepair_rate',
                  'recovery_rate', 'dose_gy'
            Values: actual parameter values (denormalized by BatchSimulator)

        Returns
        -------
        Mock or HappyGeneConfig
            Configured model ready for simulation.
        """
        # Create kinetics config
        kinetics = KineticsConfig(
            recognition_rate=params.get("recognition_rate", 0.1),
            repair_rate=params.get("repair_rate", 0.05),
            misrepair_rate=params.get("misrepair_rate", 0.01),
            recovery_rate=params.get("recovery_rate", 0.02),
        )

        # Create a minimal config (for testing batch interface, not simulation)
        # Store params as mock config for testing purposes
        class MockConfig:
            def __init__(self, dose_gy, kinetics, other_params):
                self.dose_gy = dose_gy
                self.kinetics = kinetics
                self.params = other_params
                self._is_mock = True

        # Separate dose_gy from other params to avoid duplicate keyword arg
        # Note: Don't modify original params dict as it's used downstream
        dose_gy_val = params.get("dose_gy", 3.0)
        other_params = {k: v for k, v in params.items() if k != "dose_gy"}

        config = MockConfig(
            dose_gy=dose_gy_val, kinetics=kinetics, other_params=other_params
        )
        return config

    return create_model


@pytest.fixture
def param_names(param_space):
    """List of parameter names in order."""
    return list(param_space.keys())


@pytest.fixture
def normalized_samples():
    """Generate 64 random samples normalized to [0, 1]."""
    np.random.seed(42)
    n_params = 5
    n_samples = 64
    return np.random.uniform(0, 1, size=(n_samples, n_params))


@pytest.fixture
def denormalized_samples(param_space, normalized_samples):
    """Convert normalized samples [0, 1] to actual parameter ranges."""
    param_names = list(param_space.keys())
    denorm = np.zeros_like(normalized_samples)

    for i, pname in enumerate(param_names):
        low, high = param_space[pname]
        denorm[:, i] = normalized_samples[:, i] * (high - low) + low

    return denorm


@pytest.fixture
def batch_results_df(param_names, normalized_samples):
    """Mock batch simulation results DataFrame.

    Simulates output from BatchSimulator.run_batch():
    - Parameter columns (denormalized values)
    - Output columns (total_repairs, repair_time, survival)
    - Metadata columns (run_id, seed, timestamp)
    """
    n_samples = len(normalized_samples)

    # Denormalize parameters
    param_space = {
        "recognition_rate": (0.01, 0.99),
        "repair_rate": (0.01, 0.99),
        "misrepair_rate": (0.01, 0.99),
        "recovery_rate": (0.01, 0.99),
        "dose_gy": (0.1, 10.0),
    }

    denorm = np.zeros_like(normalized_samples)
    for i, pname in enumerate(param_names):
        low, high = param_space[pname]
        denorm[:, i] = normalized_samples[:, i] * (high - low) + low

    # Create DataFrame
    df = pd.DataFrame(denorm, columns=param_names)

    # Add outputs (synthetic but realistic)
    np.random.seed(42)
    df["total_repairs"] = np.random.randint(50, 500, n_samples)
    df["repair_time"] = np.random.uniform(1.0, 100.0, n_samples)
    df["survival"] = np.random.uniform(0.0, 1.0, n_samples)

    # Add metadata
    df["run_id"] = [f"run_{i:03d}" for i in range(n_samples)]
    df["seed"] = [42 + i for i in range(n_samples)]
    df["timestamp"] = pd.Timestamp.now()

    return df


@pytest.fixture
def sobol_output_vector(normalized_samples):
    """Generate synthetic output vector for Sobol index testing.

    Creates a vector where sensitivity to parameters is known:
    - Param 0 (recognition_rate): high sensitivity (coefficient 0.5)
    - Param 1 (repair_rate): medium sensitivity (coefficient 0.3)
    - Param 2 (misrepair_rate): low sensitivity (coefficient 0.1)
    - Param 3 (recovery_rate): interaction effect with param 0
    - Param 4 (dose_gy): low sensitivity (coefficient 0.05)
    """
    # Linear + interaction model
    x0, x1, x2, x3, x4 = normalized_samples.T
    Y = (
        0.5 * x0
        + 0.3 * x1
        + 0.1 * x2
        + 0.2 * x3 * x0
        + 0.05 * x4
        + np.random.normal(0, 0.02, len(x0))
    )  # Add noise
    return Y


@pytest.fixture
def morris_output_vector(normalized_samples):
    """Generate output vector for Morris screening tests."""
    x0, x1, x2, x3, x4 = normalized_samples.T
    Y = 0.7 * x0 + 0.3 * x1 + 0.1 * x2 + np.random.normal(0, 0.01, len(x0))
    return Y


@pytest.fixture
def cache_dir(tmp_path):
    """Temporary directory for caching simulation results."""
    return tmp_path / "cache"


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Temporary directory for test data files."""
    return tmp_path / "data"


@pytest.fixture
def sobol_batch_results(param_names):
    """Batch results sized for Sobol analysis (Saltelli-structured).

    Saltelli scheme requires N*(D+2) rows for first-order only analysis.
    For 5 params with N=64: 64*(5+2) = 448 rows.
    Uses known sensitivity structure for testing.
    """
    from SALib.sample import saltelli

    problem = {
        "num_vars": len(param_names),
        "names": param_names,
        "bounds": [(0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.1, 10.0)],
    }
    X = saltelli.sample(problem, 64, calc_second_order=False)

    # Known sensitivity structure for testing
    np.random.seed(42)
    Y = (
        0.5 * X[:, 0]
        + 0.3 * X[:, 1]
        + 0.1 * X[:, 2]
        + 0.05 * X[:, 3]
        + 0.02 * X[:, 4]
        + np.random.normal(0, 0.01, len(X))
    )

    df = pd.DataFrame(X, columns=param_names)
    df["survival"] = Y
    df["total_repairs"] = np.random.randint(50, 500, len(X))
    df["repair_time"] = np.random.uniform(1.0, 100.0, len(X))
    df["run_id"] = [f"run_{i:05d}" for i in range(len(X))]
    df["seed"] = [42 + i for i in range(len(X))]

    return df


@pytest.fixture
def sobol_batch_results_second_order(param_names):
    """Batch results sized for Sobol second-order analysis.

    Saltelli scheme with second-order requires N*(2D+2) rows.
    For 5 params with N=64: 64*(2*5+2) = 768 rows.
    """
    from SALib.sample import saltelli

    problem = {
        "num_vars": len(param_names),
        "names": param_names,
        "bounds": [(0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.1, 10.0)],
    }
    X = saltelli.sample(problem, 64, calc_second_order=True)

    # Known sensitivity structure for testing
    np.random.seed(42)
    Y = (
        0.5 * X[:, 0]
        + 0.3 * X[:, 1]
        + 0.1 * X[:, 2]
        + 0.05 * X[:, 3]
        + 0.02 * X[:, 4]
        + np.random.normal(0, 0.01, len(X))
    )

    df = pd.DataFrame(X, columns=param_names)
    df["survival"] = Y
    df["total_repairs"] = np.random.randint(50, 500, len(X))
    df["repair_time"] = np.random.uniform(1.0, 100.0, len(X))
    df["run_id"] = [f"run_{i:05d}" for i in range(len(X))]
    df["seed"] = [42 + i for i in range(len(X))]

    return df


@pytest.fixture
def morris_batch_results(param_names):
    """Batch results sized for Morris analysis (Morris-structured).

    Morris sampling requires N*(D+1) rows where D=num_params and N=num_trajectories.
    For 5 params with N=20: 20*(5+1) = 120 rows.
    Uses known sensitivity structure for testing.
    """
    from SALib.sample import morris as morris_sample

    problem = {
        "num_vars": len(param_names),
        "names": param_names,
        "bounds": [(0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.1, 10.0)],
    }
    X = morris_sample.sample(problem, N=20, num_levels=10)

    np.random.seed(42)
    Y = (
        0.7 * X[:, 0]
        + 0.3 * X[:, 1]
        + 0.05 * X[:, 2]
        + np.random.normal(0, 0.01, len(X))
    )

    df = pd.DataFrame(X, columns=param_names)
    df["survival"] = Y
    df["total_repairs"] = np.random.randint(50, 500, len(X))
    df["repair_time"] = np.random.uniform(1.0, 100.0, len(X))
    df["run_id"] = [f"run_{i:05d}" for i in range(len(X))]
    df["seed"] = [42 + i for i in range(len(X))]

    return df


@pytest.fixture
def output_dir(tmp_path):
    """Temporary directory for OutputExporter tests."""
    return tmp_path / "output"
