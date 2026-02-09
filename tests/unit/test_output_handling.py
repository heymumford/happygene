"""
Output File Handling Tests - RED Phase

Tests define expected behavior for saving and loading simulation results.
"""

import tempfile
from pathlib import Path

import pytest

from engine.io.output import OutputWriter, OutputFormat


class TestOutputWriter:
    """Test simulation result output handling."""

    def test_output_writer_supports_hdf5_format(self) -> None:
        """Output writer can save results in HDF5 format."""
        writer = OutputWriter(OutputFormat.HDF5)

        test_data = {
            'run_id': 1,
            'repair_times': [10.0, 20.0, 30.0],
            'final_status': 'complete'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.h5"
            writer.write(test_data, output_path)

            assert output_path.exists()

    def test_output_writer_supports_json_format(self) -> None:
        """Output writer can save results in JSON format."""
        writer = OutputWriter(OutputFormat.JSON)

        test_data = {
            'run_id': 1,
            'repair_times': [10.0, 20.0],
            'status': 'complete'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.json"
            writer.write(test_data, output_path)

            assert output_path.exists()

    def test_output_writer_creates_parent_directories(self) -> None:
        """Output writer creates parent directories if needed."""
        writer = OutputWriter(OutputFormat.HDF5)

        test_data = {'test': 'data'}

        with tempfile.TemporaryDirectory() as tmpdir:
            # Nested path that doesn't exist yet
            output_path = Path(tmpdir) / "results" / "batch_1" / "output.h5"
            writer.write(test_data, output_path)

            assert output_path.exists()

    def test_output_format_enum_values(self) -> None:
        """OutputFormat enum has expected values."""
        assert hasattr(OutputFormat, 'HDF5')
        assert hasattr(OutputFormat, 'JSON')
        assert hasattr(OutputFormat, 'CSV')

    def test_output_writer_handles_large_dataset(self) -> None:
        """Output writer can handle large result datasets."""
        writer = OutputWriter(OutputFormat.HDF5)

        # Large dataset: 1000 runs with 100 data points each
        test_data = {
            'run_id': list(range(1000)),
            'repair_times': [[i * 0.1 for i in range(100)] for _ in range(1000)],
            'final_count': [i * 10 for i in range(1000)]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "large_results.h5"
            writer.write(test_data, output_path)

            assert output_path.exists()
            # Should be reasonably sized (HDF5 compresses well)
            assert output_path.stat().st_size > 0

    def test_output_writer_raises_on_invalid_format(self) -> None:
        """Output writer raises error for unsupported format."""
        with pytest.raises(ValueError):
            # Invalid format value
            OutputWriter("INVALID_FORMAT")  # type: ignore
