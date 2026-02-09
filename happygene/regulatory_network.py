"""RegulatoryNetwork: gene-to-gene interactions via sparse adjacency matrix (ADR-004)."""
from dataclasses import dataclass
from typing import List
import numpy as np
import scipy.sparse
import networkx as nx


@dataclass
class RegulationConnection:
    """Edge in regulatory network: source gene → target gene with interaction weight."""

    source: str
    target: str
    weight: float

    def __post_init__(self):
        """Validate weight is finite."""
        if not np.isfinite(self.weight):
            raise ValueError(f"weight must be finite, got {self.weight}")


class RegulatoryNetwork:
    """Immutable gene regulatory network with static sparse adjacency matrix (ADR-004).

    Represents interactions as scipy.sparse.csr_matrix for fast TF input computation.
    Immutable post-initialization (fail-loud philosophy: catch errors before simulation).

    Parameters
    ----------
    gene_names : List[str]
        Names of all genes in network (defines indexing).
    interactions : List[RegulationConnection]
        List of regulatory edges (source → target with weight).

    Attributes
    ----------
    adjacency : scipy.sparse.csr_matrix
        Read-only (n_genes, n_genes) sparse adjacency matrix. Entry [i,j] = weight
        of interaction from gene i to gene j.
    """

    def __init__(self, gene_names: List[str], interactions: List[RegulationConnection]):
        """Initialize regulatory network.

        Validates:
        - No self-loops
        - All genes referenced exist in gene_names
        - Adjacency matrix built in CSR format (efficient matrix-vector multiply)
        """
        self._gene_names = list(gene_names)
        self._n_genes = len(self._gene_names)
        self._gene_to_idx = {name: idx for idx, name in enumerate(self._gene_names)}

        # Validate interactions
        for conn in interactions:
            if conn.source == conn.target:
                raise ValueError(f"self-loop rejected: {conn.source} → {conn.target}")
            if conn.source not in self._gene_to_idx:
                raise ValueError(f"unknown gene (source): {conn.source}")
            if conn.target not in self._gene_to_idx:
                raise ValueError(f"unknown gene (target): {conn.target}")

        # Build sparse CSR matrix
        rows, cols, data = [], [], []
        for conn in interactions:
            src_idx = self._gene_to_idx[conn.source]
            tgt_idx = self._gene_to_idx[conn.target]
            rows.append(tgt_idx)  # Row = target (TF input to target)
            cols.append(src_idx)  # Column = source (producer of TF)
            data.append(conn.weight)

        self._adjacency = scipy.sparse.csr_matrix(
            (data, (rows, cols)), shape=(self._n_genes, self._n_genes)
        )
        # Make sparse matrix immutable by storing as copy and preventing modification
        self._adjacency.setflags(write=False) if hasattr(self._adjacency, 'setflags') else None
        # Convert to CSR format with copy to ensure immutability via copy-on-write pattern
        self._adjacency = self._adjacency.copy()
        self._adjacency.data.flags.writeable = False

        # Detect cycles (networkx)
        self._is_acyclic = self._compute_is_acyclic()

    @property
    def gene_names(self) -> List[str]:
        """Read-only gene names."""
        return self._gene_names.copy()

    @property
    def n_genes(self) -> int:
        """Number of genes in network."""
        return self._n_genes

    @property
    def adjacency(self) -> scipy.sparse.csr_matrix:
        """Read-only sparse adjacency matrix (CSR format)."""
        return self._adjacency

    @property
    def is_acyclic(self) -> bool:
        """True if network contains no feedback loops."""
        return self._is_acyclic

    def compute_tf_inputs(self, expression_vector: np.ndarray) -> np.ndarray:
        """Compute transcription factor input levels for each gene.

        TF inputs = adjacency @ expression_vector
        where adjacency[i,j] = weight of j → i interaction.

        Parameters
        ----------
        expression_vector : np.ndarray
            Shape (n_genes,) with expression level for each gene.

        Returns
        -------
        np.ndarray
            Shape (n_genes,) with TF input level for each gene (>= 0, can be negative).
        """
        if expression_vector.shape[0] != self._n_genes:
            raise ValueError(
                f"expression_vector shape {expression_vector.shape[0]} "
                f"does not match n_genes {self._n_genes}"
            )

        # adjacency @ expr = TF inputs (sparse matrix multiplication)
        return self._adjacency @ expression_vector

    def _compute_is_acyclic(self) -> bool:
        """Detect cycles in regulatory network using networkx."""
        G = nx.DiGraph()
        G.add_nodes_from(range(self._n_genes))

        # Add edges from sparse matrix
        cx = self._adjacency.tocoo()
        for i, j, v in zip(cx.row, cx.col, cx.data):
            if v != 0:
                G.add_edge(j, i)  # j → i (reverse of adjacency storage)

        try:
            # If no cycle found, is_acyclic returns True
            return nx.is_directed_acyclic_graph(G)
        except Exception:
            return False
