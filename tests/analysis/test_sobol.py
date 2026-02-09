"""Tests for SobolAnalyzer: global sensitivity analysis via Sobol indices.

Test Tiers:
1. Contract Tests: SobolIndices data, SobolAnalyzer interface
2. Property Tests: Index bounds, ranking consistency
3. Chaos Tests: Invalid inputs, missing columns
4. Integration Tests: Full analyze → rank → detect workflow
"""

import pytest
import numpy as np
import pandas as pd

from happygene.analysis.sobol import SobolAnalyzer, SobolIndices


class TestSobolIndicesDataclass:
    """Contract: SobolIndices stores and exports indices correctly."""

    def test_to_dataframe_columns(self):
        """to_dataframe returns param, S1, S1_conf, ST, ST_conf columns."""
        indices = SobolIndices(
            S1=np.array([0.5, 0.3, 0.1]),
            S1_conf=np.array([0.02, 0.02, 0.02]),
            ST=np.array([0.6, 0.35, 0.12]),
            ST_conf=np.array([0.03, 0.03, 0.03]),
            param_names=['a', 'b', 'c'],
        )
        df = indices.to_dataframe()
        assert set(df.columns) == {'param', 'S1', 'S1_conf', 'ST', 'ST_conf'}

    def test_to_dataframe_sorted_by_ST_descending(self):
        """to_dataframe sorts by ST descending."""
        indices = SobolIndices(
            S1=np.array([0.1, 0.5, 0.3]),
            S1_conf=np.array([0.02, 0.02, 0.02]),
            ST=np.array([0.12, 0.6, 0.35]),
            ST_conf=np.array([0.03, 0.03, 0.03]),
            param_names=['a', 'b', 'c'],
        )
        df = indices.to_dataframe()
        assert df.iloc[0]['param'] == 'b'  # Highest ST
        assert df.iloc[-1]['param'] == 'a'  # Lowest ST

    def test_to_dataframe_row_count_matches_params(self):
        """One row per parameter."""
        names = ['p1', 'p2', 'p3', 'p4']
        indices = SobolIndices(
            S1=np.zeros(4), S1_conf=np.zeros(4),
            ST=np.zeros(4), ST_conf=np.zeros(4),
            param_names=names,
        )
        assert len(indices.to_dataframe()) == 4


class TestSobolAnalyzerCreation:
    """Contract: SobolAnalyzer construction."""

    def test_creation_with_param_names(self, param_names):
        """Creates with param_names list."""
        analyzer = SobolAnalyzer(param_names)
        assert analyzer.n_params == len(param_names)

    def test_creation_without_salib_raises(self, param_names, monkeypatch):
        """Raises ImportError when SALib unavailable."""
        import happygene.analysis.sobol as sobol_mod
        monkeypatch.setattr(sobol_mod, 'SALIB_AVAILABLE', False)
        with pytest.raises(ImportError):
            SobolAnalyzer(param_names)


class TestSobolAnalyze:
    """Contract: analyze() computes Sobol indices from batch results."""

    def test_analyze_returns_sobol_indices(self, param_names, sobol_batch_results):
        """analyze() returns SobolIndices dataclass."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results, output_col='survival')
        assert isinstance(indices, SobolIndices)

    def test_analyze_s1_shape_matches_params(self, param_names, sobol_batch_results):
        """S1 array length equals number of parameters."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results)
        assert len(indices.S1) == len(param_names)

    def test_analyze_st_shape_matches_params(self, param_names, sobol_batch_results):
        """ST array length equals number of parameters."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results)
        assert len(indices.ST) == len(param_names)

    def test_analyze_st_gte_s1(self, param_names, sobol_batch_results):
        """Total effect >= first-order effect (Sobol property)."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results)
        # ST >= S1 for well-conditioned problems (with tolerance for numerical noise)
        assert np.all(indices.ST >= indices.S1 - 0.05)

    def test_analyze_missing_output_col_raises(self, param_names, sobol_batch_results):
        """Raises ValueError for nonexistent output column."""
        analyzer = SobolAnalyzer(param_names)
        with pytest.raises(ValueError, match="not found"):
            analyzer.analyze(sobol_batch_results, output_col='nonexistent')

    def test_analyze_missing_param_col_raises(self, sobol_batch_results):
        """Raises ValueError when param columns missing from data."""
        analyzer = SobolAnalyzer(['missing_param_1', 'missing_param_2'])
        with pytest.raises(ValueError, match="Expected"):
            analyzer.analyze(sobol_batch_results)

    def test_analyze_with_second_order(self, param_names, sobol_batch_results_second_order):
        """calc_second_order=True populates S2 matrix."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results_second_order, calc_second_order=True)
        assert indices.S2 is not None
        assert indices.S2.shape == (len(param_names), len(param_names))


class TestSobolRankParameters:
    """Contract: rank_parameters() orders by specified index."""

    def test_rank_by_st_default(self, param_names, sobol_batch_results):
        """Default ranking by ST, descending."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results)
        ranked = analyzer.rank_parameters(indices)

        assert 'rank' in ranked.columns
        # First row should have highest ST
        st_values = ranked['ST'].values
        assert all(st_values[i] >= st_values[i+1] for i in range(len(st_values)-1))

    def test_rank_by_s1(self, param_names, sobol_batch_results):
        """Ranking by S1 orders by first-order effect."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results)
        ranked = analyzer.rank_parameters(indices, by='S1')

        s1_values = ranked['S1'].values
        assert all(s1_values[i] >= s1_values[i+1] for i in range(len(s1_values)-1))

    def test_rank_invalid_by_raises(self, param_names, sobol_batch_results):
        """Invalid 'by' parameter raises ValueError."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results)
        with pytest.raises(ValueError, match="Unknown index"):
            analyzer.rank_parameters(indices, by='invalid')


class TestSobolDetectInteractions:
    """Contract: detect_interactions() finds parameter pairs with high S2."""

    def test_detect_requires_s2(self, param_names, sobol_batch_results):
        """Raises ValueError when S2 not computed."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results, calc_second_order=False)
        with pytest.raises(ValueError, match="Second-order"):
            analyzer.detect_interactions(indices)

    def test_detect_returns_list_of_tuples(self, param_names, sobol_batch_results_second_order):
        """Returns list of (param1, param2, s2_value) tuples."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results_second_order, calc_second_order=True)
        interactions = analyzer.detect_interactions(indices, threshold=0.0)

        assert isinstance(interactions, list)
        if len(interactions) > 0:
            assert len(interactions[0]) == 3  # (name1, name2, value)

    def test_detect_high_threshold_filters(self, param_names, sobol_batch_results_second_order):
        """High threshold returns fewer interactions."""
        analyzer = SobolAnalyzer(param_names)
        indices = analyzer.analyze(sobol_batch_results_second_order, calc_second_order=True)
        all_interactions = analyzer.detect_interactions(indices, threshold=0.0)
        few_interactions = analyzer.detect_interactions(indices, threshold=0.5)

        assert len(few_interactions) <= len(all_interactions)
