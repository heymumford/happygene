"""Tests for CorrelationAnalyzer: parameter interaction and correlation.

Test Tiers:
1. Contract Tests: Correlation matrix shape, output format
2. Property Tests: Symmetry, diagonal values, p-value bounds
3. Chaos Tests: Invalid methods, missing columns
"""

import pytest
import numpy as np
import pandas as pd

from happygene.analysis.correlation import CorrelationAnalyzer


class TestCorrelationMatrix:
    """Contract: compute_correlation_matrix()."""

    def test_returns_dataframe(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        corr = analyzer.compute_correlation_matrix(batch_results_df)
        assert isinstance(corr, pd.DataFrame)

    def test_matrix_is_square(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        corr = analyzer.compute_correlation_matrix(batch_results_df)
        assert corr.shape[0] == corr.shape[1] == len(param_names)

    def test_diagonal_is_one(self, param_names, batch_results_df):
        """Correlation of param with itself is 1.0."""
        analyzer = CorrelationAnalyzer(param_names)
        corr = analyzer.compute_correlation_matrix(batch_results_df)
        for p in param_names:
            assert abs(corr.loc[p, p] - 1.0) < 1e-10

    def test_values_in_neg1_to_1(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        corr = analyzer.compute_correlation_matrix(batch_results_df)
        assert np.all(corr.values >= -1.0 - 1e-10)
        assert np.all(corr.values <= 1.0 + 1e-10)

    def test_symmetric(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        corr = analyzer.compute_correlation_matrix(batch_results_df)
        assert np.allclose(corr.values, corr.values.T)

    def test_spearman_method(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        corr = analyzer.compute_correlation_matrix(batch_results_df, method='spearman')
        assert corr.shape == (len(param_names), len(param_names))

    def test_invalid_method_raises(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        with pytest.raises(ValueError, match="Unknown method"):
            analyzer.compute_correlation_matrix(batch_results_df, method='invalid')


class TestParameterOutputCorrelation:
    """Contract: parameter_output_correlation()."""

    def test_returns_dataframe_with_expected_columns(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        result = analyzer.parameter_output_correlation(batch_results_df, output_col='survival')
        assert set(result.columns) == {'param', 'correlation', 'p_value'}

    def test_one_row_per_param(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        result = analyzer.parameter_output_correlation(batch_results_df)
        assert len(result) == len(param_names)

    def test_sorted_by_abs_correlation(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        result = analyzer.parameter_output_correlation(batch_results_df)
        abs_corrs = result['correlation'].abs().values
        assert all(abs_corrs[i] >= abs_corrs[i+1] for i in range(len(abs_corrs)-1))

    def test_p_values_in_0_to_1(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        result = analyzer.parameter_output_correlation(batch_results_df)
        assert np.all(result['p_value'].values >= 0)
        assert np.all(result['p_value'].values <= 1)

    def test_missing_output_col_raises(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        with pytest.raises(ValueError, match="not found"):
            analyzer.parameter_output_correlation(batch_results_df, output_col='nonexistent')

    def test_spearman_method(self, param_names, batch_results_df):
        analyzer = CorrelationAnalyzer(param_names)
        result = analyzer.parameter_output_correlation(batch_results_df, method='spearman')
        assert len(result) == len(param_names)


class TestDetectMulticollinearity:
    """Contract: detect_multicollinearity()."""

    def test_returns_dict_with_param_names(self, param_names, batch_results_df):
        pytest.importorskip('statsmodels')
        analyzer = CorrelationAnalyzer(param_names)
        vif = analyzer.detect_multicollinearity(batch_results_df)
        assert isinstance(vif, dict)
        assert set(vif.keys()) == set(param_names)

    def test_vif_values_positive(self, param_names, batch_results_df):
        pytest.importorskip('statsmodels')
        analyzer = CorrelationAnalyzer(param_names)
        vif = analyzer.detect_multicollinearity(batch_results_df)
        for pname, value in vif.items():
            if not np.isnan(value):
                assert value > 0

    def test_uncorrelated_params_low_vif(self):
        """Uncorrelated parameters should have VIF near 1.0."""
        pytest.importorskip('statsmodels')
        np.random.seed(42)
        n = 200
        df = pd.DataFrame({
            'a': np.random.normal(0, 1, n),
            'b': np.random.normal(0, 1, n),
            'c': np.random.normal(0, 1, n),
        })
        analyzer = CorrelationAnalyzer(['a', 'b', 'c'])
        vif = analyzer.detect_multicollinearity(df)
        for v in vif.values():
            assert v < 2.0  # Uncorrelated should be near 1.0
