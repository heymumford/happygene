# Example: Regulatory Network

Advanced example demonstrating realistic gene regulatory dynamics with Hill kinetics and threshold selection.

**Files**: `examples/regulatory_network.py`

**Scenario**: 50 individuals, 5 genes, Hill kinetics (sigmoidal response), threshold-based selection, 150 generations

## What it demonstrates

- Advanced expression model: `HillExpression` (cooperative binding)
- Advanced selection model: `ThresholdSelection` (fitness bottleneck)
- Environmental conditions: transcription factor concentration
- Multi-level data collection (model, individual, gene)
- Selection pressure analysis
- Gene expression statistics

## Key features

- **Gene names**: TF1, TF2, TF3, TF4, TF5 (transcription factors)
- **Expression Model**: `HillExpression(v_max=1.0, k=0.5, n=2.0)`
  - Sigmoidal response with cooperativity (n=2)
  - Half-saturation at k=0.5
- **Selection Model**: `ThresholdSelection(threshold=0.4)`
  - Binary fitness: 1.0 if mean_expr > 0.4, else 0.0
  - Creates a fitness bottleneck
- **Environmental Conditions**: `tf_concentration=0.7` (moderate TF level)
- **Mutation Model**: `PointMutation(rate=0.2, magnitude=0.1)`
- **Population**: 50 individuals, 5 genes each
- **Duration**: 150 generations

## Run it

```bash
python examples/regulatory_network.py
```

## Expected output

- Population and gene setup
- Hill kinetics and threshold selection configuration
- Environmental conditions (tf_concentration=0.7)
- Simulation for 150 generations
- Fitness and expression statistics
- Selection pressure analysis (survivors per generation)
- Gene expression distribution
- (Optional) 4-panel visualization if matplotlib is installed

## Typical results

With Hill kinetics (cooperative binding) and tf_concentration=0.7:

- **Initial mean fitness**: ~1.0 (most individuals above threshold initially)
- **Initial mean expression**: ~0.66 (Hill equation at tf=0.7 with k=0.5, n=2)
- **Final mean fitness**: ~1.0 (threshold maintained)
- **Final mean expression**: Similar to initial (no strong selection pressure upward)
- **Survivors/generation**: 100% (all exceed threshold)
- **Gene expression variation**: Low variation within population

## Biological interpretation

This model represents a **developmental gene network** where:
- Genes require moderate transcription factor activation to express
- Expression follows a sigmoidal curve (Hill kinetics with cooperativity)
- Threshold selection models developmental thresholds or fitness cliffs
- Environmental conditions represent cellular/tissue TF levels

## Try modifying

### Different TF levels

```python
conditions = Conditions(tf_concentration=0.3)  # Low TF → low expression
# or
conditions = Conditions(tf_concentration=0.9)  # High TF → high expression
```

### Different Hill coefficients

```python
hill_model = HillExpression(v_max=1.0, k=0.5, n=1.0)  # n=1: linear response
# or
hill_model = HillExpression(v_max=1.0, k=0.5, n=3.0)  # n=3: sharp switch
```

### Different selection thresholds

```python
threshold_model = ThresholdSelection(threshold=0.2)  # Easier to survive
# or
threshold_model = ThresholdSelection(threshold=0.8)  # Harder to survive
```

### Stronger mutations

```python
mutate_model = PointMutation(rate=0.3, magnitude=0.2)  # More variation
```

## Visualization

The script generates a 4-panel PNG:

1. **Top Left**: Mean fitness over time (shows threshold line)
2. **Top Right**: Mean expression over time (shows threshold line)
3. **Bottom Left**: Fitness distribution in final generation
4. **Bottom Right**: Gene expression distribution in final generation

## Key insights

- **Hill kinetics** models realistic sigmoidal gene responses
- **Threshold selection** creates distinct "fit" vs "unfit" groups
- **Cooperativity** (n>1) creates switch-like behavior
- **tf_concentration** drives expression level (environmental effect)
- **Selection pressure** depends on how many individuals exceed threshold

## Next steps

- Modify to use `LinearExpression` to see difference from Hill kinetics
- Try `ProportionalSelection` to see continuous selection pressure instead of bottleneck
- Create custom expression model (subclass `ExpressionModel`)
- Add multiple expression models for different genes
- Implement more complex regulatory networks with gene-gene interactions

## Biological applications

This pattern models:
- **Developmental switches**: Threshold-based gene activation
- **Regulatory networks**: Sigmoidal response to transcription factors
- **Cooperative binding**: Multiple TFs binding same promoter
- **Canalization**: Developmental buffering via selection
