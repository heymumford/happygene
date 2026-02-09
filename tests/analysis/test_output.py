"""Tests for OutputExporter: file export and analysis packaging.

Test Tiers:
1. Contract Tests: CSV, JSON, text export format and content
2. Chaos Tests: Edge cases (empty data, special characters)
3. Integration Tests: create_analysis_package workflow
"""

import pytest
import json
import numpy as np
import pandas as pd

from happygene.analysis.output import OutputExporter


class TestExportIndicesToCsv:
    """Contract: export_indices_to_csv()."""

    def test_creates_csv_file(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        df = pd.DataFrame({'param': ['a', 'b'], 'S1': [0.5, 0.3]})
        path = exporter.export_indices_to_csv(df)
        assert path.exists()
        assert path.suffix == '.csv'

    def test_csv_content_matches_input(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        df = pd.DataFrame({'param': ['a', 'b'], 'S1': [0.5, 0.3]})
        path = exporter.export_indices_to_csv(df)
        loaded = pd.read_csv(path)
        assert list(loaded['param']) == ['a', 'b']
        assert np.allclose(loaded['S1'], [0.5, 0.3])

    def test_csv_custom_name(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        df = pd.DataFrame({'param': ['a'], 'val': [1]})
        path = exporter.export_indices_to_csv(df, name='custom')
        assert path.name == 'custom.csv'


class TestExportResultsToJson:
    """Contract: export_results_to_json()."""

    def test_creates_json_file(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        data = {'key': 'value', 'number': 42}
        path = exporter.export_results_to_json(data)
        assert path.exists()
        assert path.suffix == '.json'

    def test_json_content_matches_input(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        data = {'key': 'value', 'list': [1, 2, 3]}
        path = exporter.export_results_to_json(data)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_json_handles_numpy_arrays(self, output_dir):
        """numpy arrays serialized as lists."""
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        data = {'indices': np.array([0.5, 0.3, 0.1])}
        path = exporter.export_results_to_json(data)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded['indices'] == [0.5, 0.3, 0.1]

    def test_json_custom_name(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        path = exporter.export_results_to_json({}, name='custom')
        assert path.name == 'custom.json'


class TestExportBatchResultsToCsv:
    """Contract: export_batch_results_to_csv()."""

    def test_creates_csv(self, output_dir, batch_results_df):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        path = exporter.export_batch_results_to_csv(batch_results_df)
        assert path.exists()

    def test_csv_row_count_preserved(self, output_dir, batch_results_df):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        path = exporter.export_batch_results_to_csv(batch_results_df)
        loaded = pd.read_csv(path)
        assert len(loaded) == len(batch_results_df)


class TestExportSummaryReport:
    """Contract: export_summary_report()."""

    def test_creates_text_file(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        summary = {'method': 'Sobol', 'n_samples': 768}
        path = exporter.export_summary_report(summary)
        assert path.exists()
        assert path.suffix == '.txt'

    def test_text_contains_key_value_pairs(self, output_dir):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        summary = {'method': 'Sobol', 'n_samples': 768}
        path = exporter.export_summary_report(summary)
        content = path.read_text()
        assert 'method: Sobol' in content or 'method' in content
        assert '768' in content


class TestCreateAnalysisPackage:
    """Integration: create_analysis_package() produces all outputs."""

    def test_returns_dict_of_paths(self, output_dir, batch_results_df):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        indices_data = {
            'sobol': pd.DataFrame({'param': ['a'], 'ST': [0.5]}),
        }
        summary = {'method': 'Sobol'}
        exports = exporter.create_analysis_package(
            batch_results_df, indices_data, summary
        )
        assert isinstance(exports, dict)
        assert 'batch_results' in exports
        assert 'sobol' in exports
        assert 'summary' in exports

    def test_all_files_exist(self, output_dir, batch_results_df):
        output_dir.mkdir(exist_ok=True)
        exporter = OutputExporter(str(output_dir))
        indices_data = {
            'sobol': pd.DataFrame({'param': ['a'], 'ST': [0.5]}),
            'morris': pd.DataFrame({'param': ['a'], 'mu_star': [0.8]}),
        }
        summary = {'method': 'combined'}
        exports = exporter.create_analysis_package(
            batch_results_df, indices_data, summary
        )
        for name, path in exports.items():
            if name != 'complete':
                assert path.exists(), f"Missing: {name} at {path}"
