"""Tests for MorrisAnalyzer: fast parameter screening via Morris OAT.

Test Tiers:
1. Contract Tests: MorrisIndices data, MorrisAnalyzer interface
2. Property Tests: Classification consistency
3. Chaos Tests: Invalid inputs, edge cases
"""

import pytest
import numpy as np
import pandas as pd

from happygene.analysis.morris import MorrisAnalyzer, MorrisIndices


class TestMorrisIndicesDataclass:
    """Contract: MorrisIndices stores and exports indices."""

    def test_to_dataframe_columns(self):
        """to_dataframe returns param, mu, sigma, mu_star, classification."""
        indices = MorrisIndices(
            mu=np.array([0.5, 0.1]),
            sigma=np.array([0.3, 0.05]),
            mu_star=np.array([0.6, 0.15]),
            param_names=['a', 'b'],
        )
        df = indices.to_dataframe()
        assert set(df.columns) == {'param', 'mu', 'sigma', 'mu_star', 'classification'}

    def test_to_dataframe_classification_logic(self):
        """Classification: mu_star>0.5 + sigma>0.5 = Interaction."""
        indices = MorrisIndices(
            mu=np.array([0.8, 0.7, 0.1]),
            sigma=np.array([0.2, 0.8, 0.1]),
            mu_star=np.array([0.9, 0.8, 0.3]),
            param_names=['important', 'interaction', 'insignificant'],
        )
        df = indices.to_dataframe()
        classes = dict(zip(df['param'], df['classification']))
        assert classes['important'] == 'Important'
        assert classes['interaction'] == 'Interaction'
        assert classes['insignificant'] == 'Insignificant'

    def test_to_dataframe_sorted_by_mu_star(self):
        """Sorted by mu_star descending."""
        indices = MorrisIndices(
            mu=np.array([0.1, 0.9]),
            sigma=np.array([0.1, 0.1]),
            mu_star=np.array([0.2, 0.95]),
            param_names=['low', 'high'],
        )
        df = indices.to_dataframe()
        assert df.iloc[0]['param'] == 'high'


class TestMorrisAnalyzerCreation:
    """Contract: MorrisAnalyzer construction."""

    def test_creation_with_param_names(self, param_names):
        analyzer = MorrisAnalyzer(param_names)
        assert analyzer.n_params == len(param_names)

    def test_creation_without_salib_raises(self, param_names, monkeypatch):
        import happygene.analysis.morris as morris_mod
        monkeypatch.setattr(morris_mod, 'SALIB_AVAILABLE', False)
        with pytest.raises(ImportError):
            MorrisAnalyzer(param_names)


class TestMorrisAnalyze:
    """Contract: analyze() computes Morris indices."""

    def test_analyze_returns_morris_indices(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results, output_col='survival')
        assert isinstance(indices, MorrisIndices)

    def test_analyze_mu_star_shape(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        assert len(indices.mu_star) == len(param_names)

    def test_analyze_mu_star_non_negative(self, param_names, morris_batch_results):
        """mu_star is absolute mean -- always non-negative."""
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        assert np.all(indices.mu_star >= 0)

    def test_analyze_missing_output_col_raises(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        with pytest.raises(ValueError, match="not found"):
            analyzer.analyze(morris_batch_results, output_col='nonexistent')

    def test_analyze_missing_param_raises(self, morris_batch_results):
        analyzer = MorrisAnalyzer(['missing_1', 'missing_2'])
        with pytest.raises(ValueError, match="Expected"):
            analyzer.analyze(morris_batch_results)


class TestMorrisRankParameters:
    """Contract: rank_parameters() ranking by mu, sigma, mu_star."""

    def test_rank_by_mu_star_default(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        ranked = analyzer.rank_parameters(indices)
        assert 'rank' in ranked.columns

    def test_rank_by_mu(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        ranked = analyzer.rank_parameters(indices, by='mu')
        mu_vals = ranked['mu'].values
        assert all(mu_vals[i] >= mu_vals[i+1] for i in range(len(mu_vals)-1))

    def test_rank_by_sigma(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        ranked = analyzer.rank_parameters(indices, by='sigma')
        sigma_vals = ranked['sigma'].values
        assert all(sigma_vals[i] >= sigma_vals[i+1] for i in range(len(sigma_vals)-1))

    def test_rank_invalid_by_raises(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        with pytest.raises(ValueError, match="Unknown index"):
            analyzer.rank_parameters(indices, by='invalid')


class TestMorrisClassifyParameters:
    """Contract: classify_parameters() groups into categories."""

    def test_classify_returns_three_categories(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        classified = analyzer.classify_parameters(indices)
        assert set(classified.keys()) == {'Important', 'Interaction', 'Insignificant'}

    def test_classify_all_params_accounted_for(self, param_names, morris_batch_results):
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        classified = analyzer.classify_parameters(indices)
        all_classified = classified['Important'] + classified['Interaction'] + classified['Insignificant']
        assert set(all_classified) == set(param_names)

    def test_classify_custom_thresholds(self, param_names, morris_batch_results):
        """Very high threshold classifies everything as Insignificant."""
        analyzer = MorrisAnalyzer(param_names)
        indices = analyzer.analyze(morris_batch_results)
        classified = analyzer.classify_parameters(indices, mu_threshold=999.0)
        assert len(classified['Insignificant']) == len(param_names)
