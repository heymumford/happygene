"""DataCollector for 3-tier data collection (model, individual, gene level)."""
from typing import Any, Callable, Dict, List

import pandas as pd

from happygene.model import GeneNetwork


class DataCollector:
    """Collects data from simulations at three reporting levels.

    The Mesa DataCollector pattern adapted for happygene:
    - Model-level reporters: aggregate simulation metrics
    - Individual-level reporters: per-individual metrics
    - Gene-level reporters: per-gene metrics

    Parameters
    ----------
    model_reporters : dict or None
        Dict mapping metric names to callables: f(model) -> value
    individual_reporters : dict or None
        Dict mapping metric names to callables: f(individual) -> value
    gene_reporters : dict or None
        Dict mapping metric names to callables: f(gene) -> value
    max_history : int or None
        Maximum number of generations to retain in memory.
        If exceeded, oldest data is dropped. None = unlimited.
    """

    def __init__(
        self,
        model_reporters: Dict[str, Callable[[GeneNetwork], Any]] | None = None,
        individual_reporters: Dict[str, Callable[[Any], Any]] | None = None,
        gene_reporters: Dict[str, Callable[[Any], Any]] | None = None,
        max_history: int | None = None,
    ):
        self.model_reporters: Dict[str, Callable] = model_reporters or {}
        self.individual_reporters: Dict[str, Callable] = individual_reporters or {}
        self.gene_reporters: Dict[str, Callable] = gene_reporters or {}
        self.max_history: int | None = max_history

        # Storage: list of dicts for each tier
        self._model_data: List[Dict[str, Any]] = []
        self._individual_data: List[Dict[str, Any]] = []
        self._gene_data: List[Dict[str, Any]] = []

    def collect(self, model: GeneNetwork) -> None:
        """Collect data from the model at current generation.

        Parameters
        ----------
        model : GeneNetwork
            The simulation model to collect data from.
        """
        # Collect model-level data
        if self.model_reporters:
            row = {"generation": model.generation}
            for name, reporter in self.model_reporters.items():
                row[name] = reporter(model)
            self._model_data.append(row)

        # Collect individual-level data
        if self.individual_reporters:
            for ind_idx, individual in enumerate(model.individuals):
                row = {"generation": model.generation, "individual": ind_idx}
                for name, reporter in self.individual_reporters.items():
                    row[name] = reporter(individual)
                self._individual_data.append(row)

        # Collect gene-level data
        if self.gene_reporters:
            for ind_idx, individual in enumerate(model.individuals):
                for gene_idx, gene in enumerate(individual.genes):
                    row = {
                        "generation": model.generation,
                        "individual": ind_idx,
                        "gene": gene.name,
                    }
                    for name, reporter in self.gene_reporters.items():
                        row[name] = reporter(gene)
                    self._gene_data.append(row)

        # Enforce max_history
        if self.max_history is not None:
            if len(self._model_data) > self.max_history:
                self._model_data = self._model_data[-self.max_history :]
            if len(self._individual_data) > self.max_history:
                self._individual_data = self._individual_data[-self.max_history :]
            if len(self._gene_data) > self.max_history:
                self._gene_data = self._gene_data[-self.max_history :]

    def get_model_dataframe(self) -> pd.DataFrame:
        """Get model-level data as pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: generation, [reporter names]
        """
        if not self._model_data:
            return pd.DataFrame()
        return pd.DataFrame(self._model_data)

    def get_individual_dataframe(self) -> pd.DataFrame:
        """Get individual-level data as pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: generation, individual, [reporter names]
        """
        if not self._individual_data:
            return pd.DataFrame()
        return pd.DataFrame(self._individual_data)

    def get_gene_dataframe(self) -> pd.DataFrame:
        """Get gene-level data as pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: generation, individual, gene, [reporter names]
        """
        if not self._gene_data:
            return pd.DataFrame()
        return pd.DataFrame(self._gene_data)
