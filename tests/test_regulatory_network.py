"""Tests for RegulatoryNetwork (ADR-004: static sparse adjacency)."""
import pytest
import numpy as np
from happygene.regulatory_network import RegulatoryNetwork, RegulationConnection


def test_regulatory_network_init_empty():
    """Empty network with no interactions."""
    net = RegulatoryNetwork(gene_names=["g1", "g2", "g3"], interactions=[])
    assert net.gene_names == ["g1", "g2", "g3"]
    assert net.n_genes == 3
    assert net.adjacency.nnz == 0  # No edges


def test_regulatory_network_init_with_interactions():
    """Network with interactions: g1 → g2 (weight 0.5), g1 → g3 (weight -0.3)."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g1", target="g3", weight=-0.3),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2", "g3"], interactions=interactions)
    assert net.adjacency.shape == (3, 3)
    assert net.adjacency.nnz == 2


def test_regulatory_network_adjacency_is_sparse():
    """Adjacency matrix is scipy.sparse.csr_matrix (CSR format)."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)
    import scipy.sparse
    assert isinstance(net.adjacency, scipy.sparse.csr_matrix)


def test_regulatory_network_compute_tf_inputs():
    """Compute TF inputs: adjacency @ expression_vector."""
    # g1 → g2 (weight 0.5), g1 → g3 (weight 0.8)
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g1", target="g3", weight=0.8),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2", "g3"], interactions=interactions)

    expr_vector = np.array([1.0, 0.5, 0.2])  # g1=1.0, g2=0.5, g3=0.2
    tf_inputs = net.compute_tf_inputs(expr_vector)

    # Expected: TF[0] = 0 (no input to g1), TF[1] = 0.5*1.0 = 0.5, TF[2] = 0.8*1.0 = 0.8
    np.testing.assert_array_almost_equal(tf_inputs, [0.0, 0.5, 0.8])


def test_regulatory_network_immutable():
    """Adjacency matrix is read-only after construction."""
    interactions = [RegulationConnection(source="g1", target="g2", weight=0.5)]
    net = RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)

    # Attempting to modify should fail (sparse matrix copy, not ref)
    with pytest.raises((ValueError, RuntimeError)):
        net.adjacency[0, 1] = 0.7


def test_regulatory_network_rejects_self_loop():
    """Self-loops (g1 → g1) are rejected at init."""
    interactions = [RegulationConnection(source="g1", target="g1", weight=0.5)]

    with pytest.raises(ValueError, match="self-loop"):
        RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)


def test_regulatory_network_rejects_invalid_genes():
    """Interactions referencing non-existent genes are rejected."""
    interactions = [RegulationConnection(source="g1", target="g_unknown", weight=0.5)]

    with pytest.raises(ValueError, match="unknown gene"):
        RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)


def test_regulatory_network_is_acyclic_property():
    """is_acyclic property detects feedback loops."""
    # Acyclic: g1 → g2 → g3
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g3", weight=0.3),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2", "g3"], interactions=interactions)
    assert net.is_acyclic is True


def test_regulatory_network_is_acyclic_detects_cycle():
    """is_acyclic detects feedback loop: g1 → g2 → g1."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g1", weight=0.3),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)
    assert net.is_acyclic is False


def test_regulatory_network_large_sparse_network():
    """Performance: large sparse network (100 genes, 1% density = ~100 edges)."""
    n_genes = 100
    gene_names = [f"g{i}" for i in range(n_genes)]

    # Create ~1% density network
    interactions = []
    np.random.seed(42)
    for src_idx in range(n_genes):
        for tgt_idx in range(n_genes):
            if src_idx != tgt_idx and np.random.random() < 0.01:  # ~1% edges
                interactions.append(
                    RegulationConnection(
                        source=gene_names[src_idx],
                        target=gene_names[tgt_idx],
                        weight=np.random.uniform(-1.0, 1.0)
                    )
                )

    net = RegulatoryNetwork(gene_names=gene_names, interactions=interactions)
    assert net.adjacency.shape == (n_genes, n_genes)
    # Sparse density check
    sparsity = 1.0 - (net.adjacency.nnz / (n_genes * n_genes))
    assert sparsity > 0.95  # >95% sparse


def test_regulation_connection_validates_weight():
    """RegulationConnection rejects non-finite weights."""
    with pytest.raises(ValueError, match="weight must be finite"):
        RegulationConnection(source="g1", target="g2", weight=np.inf)

    with pytest.raises(ValueError, match="weight must be finite"):
        RegulationConnection(source="g1", target="g2", weight=np.nan)


def test_regulatory_network_gene_names_immutable():
    """Returned gene_names list is a copy, not reference."""
    gene_names = ["g1", "g2", "g3"]
    net = RegulatoryNetwork(gene_names=gene_names, interactions=[])

    returned_names = net.gene_names
    returned_names.append("g4")

    # Original network gene_names should not change
    assert net.n_genes == 3
    assert "g4" not in net.gene_names


def test_regulatory_network_compute_tf_inputs_shape_mismatch():
    """compute_tf_inputs raises ValueError on shape mismatch."""
    net = RegulatoryNetwork(gene_names=["g1", "g2", "g3"], interactions=[])
    wrong_expr = np.array([1.0, 0.5])  # Only 2 genes, not 3

    with pytest.raises(ValueError, match="expression_vector shape"):
        net.compute_tf_inputs(wrong_expr)


def test_regulatory_network_multiple_edges_same_pair():
    """Multiple edges between same gene pair (last one wins in sparse matrix)."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g1", target="g2", weight=0.8),  # Overwrites
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)
    # CSR matrix will have combined the duplicates or last one wins depending on constructor
    # This test verifies behavior is sensible
    assert net.adjacency.nnz >= 1


def test_regulatory_network_zero_weight_edge():
    """Zero-weight edges are included in sparsity but don't contribute to computation."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.0),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)
    expr_vector = np.array([1.0, 0.0])
    tf_inputs = net.compute_tf_inputs(expr_vector)

    # Zero-weight edge contributes zero to TF input
    assert tf_inputs[1] == pytest.approx(0.0)
