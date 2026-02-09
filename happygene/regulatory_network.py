"""RegulatoryNetwork: gene-to-gene interactions via sparse adjacency matrix (ADR-004).

Circuit detection (ADR-006): Optional feedback loop and feedforward motif detection
at initialization time. Disabled by default for performance.
"""
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple
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

    Optional circuit detection (ADR-006): Feedback loops and feedforward motifs can be
    detected at initialization time (disabled by default for performance).

    Parameters
    ----------
    gene_names : List[str]
        Names of all genes in network (defines indexing).
    interactions : List[RegulationConnection]
        List of regulatory edges (source → target with weight).
    detect_circuits : bool, optional
        If True, detect feedback loops and feedforward motifs at init.
        Default is False (opt-in for performance).

    Attributes
    ----------
    adjacency : scipy.sparse.csr_matrix
        Read-only (n_genes, n_genes) sparse adjacency matrix. Entry [i,j] = weight
        of interaction from gene i to gene j.
    circuits : List[Set[str]] or None
        Feedback loops (strongly connected components, SCC size > 1).
        None if detect_circuits=False.
    feedforward_motifs : List[Tuple[str, str, str]] or None
        Feedforward motifs (A→B→C with A→C).
        None if detect_circuits=False.
    """

    def __init__(
        self,
        gene_names: List[str],
        interactions: List[RegulationConnection],
        detect_circuits: bool = False
    ):
        """Initialize regulatory network.

        Validates:
        - No self-loops
        - All genes referenced exist in gene_names
        - Adjacency matrix built in CSR format (efficient matrix-vector multiply)
        - Optional: Detect feedback loops and feedforward motifs (ADR-006)
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

        # Optional circuit detection (ADR-006): disabled by default
        if detect_circuits:
            self._circuits = self._find_feedback_loops()
            self._feedforward_motifs = self._find_feedforward_motifs()
        else:
            self._circuits = None
            self._feedforward_motifs = None

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

    @property
    def circuits(self) -> Optional[List[Set[str]]]:
        """Feedback loops (strongly connected components with size > 1).

        Returns
        -------
        List[Set[str]] or None
            List of feedback loops (each is a set of gene names forming a cycle).
            None if detect_circuits=False.
        """
        return self._circuits

    @property
    def feedforward_motifs(self) -> Optional[List[Tuple[str, str, str]]]:
        """Feedforward motifs (A→B→C with A→C).

        Returns
        -------
        List[Tuple[str, str, str]] or None
            List of feedforward motifs (A, B, C) where A→B, B→C, A→C all exist.
            None if detect_circuits=False.
        """
        return self._feedforward_motifs

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

    def _build_networkx_digraph(self) -> nx.DiGraph:
        """Build NetworkX directed graph from sparse adjacency matrix.

        Returns
        -------
        nx.DiGraph
            Directed graph with nodes for each gene and edges from sparse matrix.
        """
        G = nx.DiGraph()
        G.add_nodes_from(range(self._n_genes))

        # Add edges from sparse matrix
        cx = self._adjacency.tocoo()
        for i, j, v in zip(cx.row, cx.col, cx.data):
            if v != 0:
                G.add_edge(j, i)  # j → i (reverse of adjacency storage)

        return G

    def _compute_is_acyclic(self) -> bool:
        """Detect cycles in regulatory network using networkx."""
        G = self._build_networkx_digraph()

        try:
            # If no cycle found, is_acyclic returns True
            return nx.is_directed_acyclic_graph(G)
        except Exception:
            return False

    def _find_feedback_loops(self) -> List[Set[str]]:
        """Detect feedback loops using strongly connected components (ADR-006).

        Returns
        -------
        List[Set[str]]
            List of feedback loops (SCCs with size > 1), each as a set of gene names.
            Empty list if network is acyclic.
        """
        G = self._build_networkx_digraph()

        # Find strongly connected components
        sccs = nx.strongly_connected_components(G)

        # Filter to SCCs with size > 1 (feedback loops)
        feedback_loops = []
        for scc in sccs:
            if len(scc) > 1:
                # Convert indices back to gene names
                gene_set = {self._gene_names[idx] for idx in scc}
                feedback_loops.append(gene_set)

        return feedback_loops

    def _find_feedforward_motifs(self) -> List[Tuple[str, str, str]]:
        """Detect feedforward motifs (A→B→C with A→C) using triple enumeration (ADR-006).

        Returns
        -------
        List[Tuple[str, str, str]]
            List of feedforward motifs (A, B, C) where A→B, B→C, A→C all exist.
            Empty list if no motifs present.

        Algorithm
        ---------
        Brute-force O(n³) enumeration of all gene triples, checking for:
        - Edge A → B
        - Edge B → C
        - Edge A → C
        Acceptable for typical networks (O(n³) on ~100 genes ≈ 1M checks ≈ 1ms).
        """
        motifs = []

        # Convert adjacency to COO format for fast lookup
        cx = self._adjacency.tocoo()
        edges = set()
        for i, j, v in zip(cx.row, cx.col, cx.data):
            if v != 0:
                # Store edge as (source_idx, target_idx)
                # Remember: adjacency[target, source] = weight
                # So edge is from j (source) to i (target)
                edges.add((j, i))

        # Triple enumeration: check all (A, B, C) triples
        for a_idx in range(self._n_genes):
            for b_idx in range(self._n_genes):
                if a_idx == b_idx:
                    continue
                # Check A → B
                if (a_idx, b_idx) not in edges:
                    continue

                for c_idx in range(self._n_genes):
                    if c_idx == a_idx or c_idx == b_idx:
                        continue
                    # Check B → C and A → C
                    if (b_idx, c_idx) in edges and (a_idx, c_idx) in edges:
                        a_name = self._gene_names[a_idx]
                        b_name = self._gene_names[b_idx]
                        c_name = self._gene_names[c_idx]
                        motifs.append((a_name, b_name, c_name))

        return motifs
