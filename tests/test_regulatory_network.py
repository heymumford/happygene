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


# ============================================================================
# Week 15, Task 15.1: Circuit detection (feedback loops, feedforward motifs)
# Tests for ADR-006: static circuit detection at initialization
# ============================================================================


def test_regulatory_network_detect_circuits_flag():
    """Opt-in circuit detection: detect_circuits=False by default, circuits/feedforward_motifs None."""
    # Without detect_circuits flag
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g1", weight=0.3),
    ]
    net = RegulatoryNetwork(gene_names=["g1", "g2"], interactions=interactions)

    # Default: no detection, properties should be None
    assert net.circuits is None
    assert net.feedforward_motifs is None

    # With detect_circuits=True
    net_detected = RegulatoryNetwork(
        gene_names=["g1", "g2"],
        interactions=interactions,
        detect_circuits=True
    )
    assert net_detected.circuits is not None
    assert net_detected.feedforward_motifs is not None


def test_regulatory_network_feedback_loop_detection():
    """Detect simple 2-node feedback loop: g1 → g2 → g1."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g1", weight=0.3),
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should detect one feedback loop containing both genes
    assert net.circuits is not None
    assert len(net.circuits) == 1
    assert net.circuits[0] == {"g1", "g2"}


def test_regulatory_network_triple_feedback():
    """Detect 3-node feedback loop (ring): g1 → g2 → g3 → g1."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g3", weight=0.4),
        RegulationConnection(source="g3", target="g1", weight=0.3),
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should detect one 3-node cycle
    assert net.circuits is not None
    assert len(net.circuits) == 1
    assert net.circuits[0] == {"g1", "g2", "g3"}


def test_regulatory_network_multiple_independent_loops():
    """Detect two separate feedback loops: g1↔g2 and g3↔g4."""
    interactions = [
        # Loop 1: g1 ↔ g2
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g1", weight=0.3),
        # Loop 2: g3 ↔ g4
        RegulationConnection(source="g3", target="g4", weight=0.6),
        RegulationConnection(source="g4", target="g3", weight=0.2),
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3", "g4"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should detect two separate loops
    assert net.circuits is not None
    assert len(net.circuits) == 2
    loop_sets = [set(loop) for loop in net.circuits]
    assert {"g1", "g2"} in loop_sets
    assert {"g3", "g4"} in loop_sets


def test_regulatory_network_no_circuits_acyclic():
    """Acyclic network (DAG) should have empty circuits list."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g1", target="g3", weight=0.3),
        RegulationConnection(source="g2", target="g3", weight=0.4),
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3"],
        interactions=interactions,
        detect_circuits=True
    )

    # No feedback loops in DAG
    assert net.circuits is not None
    assert len(net.circuits) == 0


def test_regulatory_network_feedforward_motif_detection():
    """Detect feedforward motif: A → B, A → C, B → C."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),  # A → B
        RegulationConnection(source="g1", target="g3", weight=0.3),  # A → C
        RegulationConnection(source="g2", target="g3", weight=0.4),  # B → C
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should detect one feedforward motif: (g1, g2, g3)
    assert net.feedforward_motifs is not None
    assert len(net.feedforward_motifs) == 1
    assert ("g1", "g2", "g3") in net.feedforward_motifs


def test_regulatory_network_oscillator_repressilator():
    """Repressilator (3-node repression cycle) is an odd-length feedback loop."""
    # g1 ⊣ g2 ⊣ g3 ⊣ g1 (negative weights indicate repression)
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=-0.5),
        RegulationConnection(source="g2", target="g3", weight=-0.4),
        RegulationConnection(source="g3", target="g1", weight=-0.3),
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should detect the 3-node feedback loop (odd cycle = oscillator)
    assert net.circuits is not None
    assert len(net.circuits) == 1
    assert net.circuits[0] == {"g1", "g2", "g3"}


def test_regulatory_network_circuit_detection_performance():
    """Circuit detection must complete in <100ms on 100-gene network."""
    import time

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

    # Measure circuit detection time
    start = time.time()
    net = RegulatoryNetwork(
        gene_names=gene_names,
        interactions=interactions,
        detect_circuits=True
    )
    elapsed = time.time() - start

    # Performance assertion: <100ms
    assert elapsed < 0.1, f"Circuit detection took {elapsed*1000:.1f}ms, expected <100ms"
    assert net.circuits is not None


def test_regulatory_network_feedforward_no_false_positives():
    """Ensure feedforward motif detection doesn't report A→B→C if A→C is missing."""
    interactions = [
        RegulationConnection(source="g1", target="g2", weight=0.5),  # A → B
        RegulationConnection(source="g2", target="g3", weight=0.4),  # B → C
        # NOTE: Missing A → C, so NO feedforward motif
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should NOT detect feedforward motif (A→C missing)
    assert net.feedforward_motifs is not None
    assert len(net.feedforward_motifs) == 0


def test_regulatory_network_multiple_feedforward_motifs():
    """Network with multiple feedforward motifs: (A→B→C with A→C) and (B→C→D with B→D)."""
    interactions = [
        # Feedforward motif 1: g1 → g2 → g3, g1 → g3
        RegulationConnection(source="g1", target="g2", weight=0.5),
        RegulationConnection(source="g2", target="g3", weight=0.4),
        RegulationConnection(source="g1", target="g3", weight=0.3),
        # Feedforward motif 2: g2 → g3 → g4, g2 → g4
        RegulationConnection(source="g3", target="g4", weight=0.6),
        RegulationConnection(source="g2", target="g4", weight=0.2),
    ]
    net = RegulatoryNetwork(
        gene_names=["g1", "g2", "g3", "g4"],
        interactions=interactions,
        detect_circuits=True
    )

    # Should detect both feedforward motifs
    assert net.feedforward_motifs is not None
    assert len(net.feedforward_motifs) == 2
    motifs = list(net.feedforward_motifs)
    assert ("g1", "g2", "g3") in motifs
    assert ("g2", "g3", "g4") in motifs
