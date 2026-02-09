# Ecosystem Integration Checklist for HappyGene

**Purpose**: Ensure HappyGene achieves researcher-grade ecosystem integration (not just core features)
**Target**: Reach Level 4 ecosystem maturity by month 12
**Success Metric**: Researchers can use HappyGene in 90% of their workflows without custom code

---

## TIER 0: FOUNDATION (Weeks 1-4)

These are table-stakes. Without them, researchers will abandon your tool in the first 5 minutes.

### Data Format Export

- [ ] **pandas DataFrame export**
  - [ ] `model.to_dataframe()` method (agent state at each step)
  - [ ] Index: generation (row), columns: agent_id, fitness, genes, phenotype
  - [ ] Test: `assert isinstance(df, pd.DataFrame)`
  - [ ] Test: `assert df.shape[0] > 0`
  - **Why**: 95% of researchers analyze with pandas
  - **Time**: 2 hours
  - **Example**:
    ```python
    import happygene
    model = happygene.GeneModel(n_agents=100)
    model.simulate(steps=50)
    df = model.to_dataframe()
    df.groupby("generation").fitness.mean().plot()
    ```

- [ ] **CSV export**
  - [ ] `model.to_csv("output.csv")` method
  - [ ] Compatible with Excel, R, Excel
  - [ ] Test: `os.path.exists("output.csv")`
  - **Why**: Collaborators who don't use Python
  - **Time**: 1 hour

- [ ] **JSON export**
  - [ ] `model.to_json()` for metadata + config
  - [ ] Supports reproducibility sharing
  - **Why**: Reproducibility + documentation
  - **Time**: 1 hour

### NumPy/SciPy Compatibility

- [ ] **Internal state as NumPy arrays**
  - [ ] Agent genome: `np.ndarray(n_agents, n_genes)`
  - [ ] Fitness: `np.ndarray(n_agents)`
  - [ ] Expression: `np.ndarray(n_agents, n_genes)`
  - [ ] Test: `assert isinstance(agent.genome, np.ndarray)`
  - **Why**: SciPy operations (optimize, stats) need NumPy
  - **Time**: Structural (probably already done)

- [ ] **scipy.optimize integration**
  - [ ] Parameters are scipy-compatible
  - [ ] Loss function accepts scipy format
  - [ ] Example: `scipy.optimize.minimize(loss, x0, bounds=bounds)`
  - **Why**: Parameter fitting (critical for credibility)
  - **Time**: 3 hours

### Logging & Reproducibility

- [ ] **Seed control**
  - [ ] `model = GeneModel(seed=42)`
  - [ ] `np.random.seed(42)` internally
  - [ ] Test: Run twice, get identical results
  - [ ] Test: Different seeds, different results
  - **Why**: Reviewers require reproducibility
  - **Time**: 2 hours

- [ ] **History tracking**
  - [ ] Store all agent states + parameters each step
  - [ ] `model.history` = list of snapshots
  - [ ] Efficient storage (don't store redundant data)
  - [ ] Test: `assert len(model.history) == n_steps`
  - **Why**: Researchers analyze convergence, fitness curves
  - **Time**: 2 hours

---

## TIER 1: DATA INTEROPERABILITY (Weeks 5-8)

These are "expected" by researchers who use your tool seriously.

### Standard File Formats

- [ ] **HDF5 export** (for large populations)
  - [ ] `model.to_hdf5("output.h5")` method
  - [ ] Chunked I/O (efficient for 100K+ agents)
  - [ ] Metadata (parameters, timestamps)
  - [ ] Test: File size scales linearly with agents
  - [ ] Test: Can reload and verify
  - **Why**: 100K+ agents = RAM issues without chunking
  - **Time**: 4 hours
  - **Library**: `h5py` or `tables`

- [ ] **SBML gene network export** (for collaborators)
  - [ ] `model.gene_network.to_sbml("grn.xml")`
  - [ ] Readable by COPASI, Tellurium, other tools
  - [ ] Include parameters (reaction rates, etc.)
  - [ ] Test: Can reload in another tool
  - **Why**: SBML is the bioinformatics standard
  - **Time**: 6 hours
  - **Library**: `libsbml` Python bindings

- [ ] **CSV with metadata**
  - [ ] `model.to_csv("output.csv", include_metadata=True)`
  - [ ] Header: parameters, timestamp, seed
  - [ ] Rows: simulation results
  - **Why**: R users, Excel users need this
  - **Time**: 1 hour

### Visualization Integration

- [ ] **matplotlib-ready output**
  - [ ] `model.plot_fitness()` → matplotlib Figure
  - [ ] `model.plot_genotype_frequency()` → matplotlib Figure
  - [ ] `model.plot_grn()` → network graph
  - [ ] All plots are publication-quality (high DPI, labels, legend)
  - [ ] Test: Plots save to PNG/PDF without error
  - **Why**: Researchers need plots for papers
  - **Time**: 5 hours
  - **Library**: `matplotlib`, `networkx`

- [ ] **Seaborn integration**
  - [ ] Results compatible with seaborn styling
  - [ ] Example: `sns.heatmap(gene_expression_matrix)`
  - **Why**: Researchers expect professional-looking plots
  - **Time**: 2 hours

### Parallel Batch Execution

- [ ] **Batch runner for ensemble simulations**
  - [ ] `runner = BatchRunner(model_class, param_dict, n_runs=100)`
  - [ ] Run 100 simulations with same parameters in parallel
  - [ ] Collect results into single DataFrame
  - [ ] Test: `results_df.shape[0] == n_runs * n_steps`
  - [ ] Test: All replicates are independent (verify via seed)
  - **Why**: Confidence intervals require ensemble runs
  - **Time**: 4 hours
  - **Library**: `multiprocessing` or `joblib`

- [ ] **Parameter sweep**
  - [ ] Vary mutation_rate (0.0 to 0.1, step 0.01)
  - [ ] Vary population_size (100 to 1000)
  - [ ] Combinatorial grid of all parameters
  - [ ] Test: Verify all combinations were run
  - **Why**: Sensitivity analysis
  - **Time**: 3 hours

---

## TIER 2: SCIENTIFIC VALIDATION (Months 2-3)

These build trust. Researchers will cite your tool in papers if validation is solid.

### Population Genetics Tests

- [ ] **Hardy-Weinberg Equilibrium test**
  - [ ] Under no selection, allele frequencies should be constant
  - [ ] Run model with `selection_pressure=0.0`
  - [ ] Measure allele frequency at step 0, 100, 500
  - [ ] Test: Frequency changes < 5% (statistical noise)
  - **Why**: Fundamental validation; if this fails, your genetics is wrong
  - **Time**: 3 hours
  - **Reference**: [HW Testing](https://ww2.amstat.org/meetings/proceedings/2017/data/assets/pdf/593864.pdf)

- [ ] **Genetic drift quantification**
  - [ ] Small population should show random allele frequency changes
  - [ ] Run with N=50, measure allele frequency over time
  - [ ] Calculate drift rate: Δ frequency / Δ time
  - [ ] Compare to theoretical prediction: σ² = p(1-p) / 2N
  - [ ] Test: Observed drift within confidence interval of theory
  - **Why**: Researchers trust your simulator if it matches Wright-Fisher
  - **Time**: 5 hours
  - **Reference**: Population genetics textbooks (Hartl & Clark)

- [ ] **Fixation time test**
  - [ ] Small population + one new allele
  - [ ] Measure time to fixation (frequency → 100%)
  - [ ] Compare to theoretical: E[T_fix] ≈ -4N * ln(1-p) / p for p << 1
  - [ ] Test: Mean fixation time matches prediction (±50%)
  - **Why**: Shows your simulator samples correctly
  - **Time**: 4 hours

- [ ] **Selection response test**
  - [ ] Set `selection_pressure=0.5`
  - [ ] Trait controlled by single gene (genotype frequency)
  - [ ] Measure response to selection: ΔZ = h² S
  - [ ] Compare to breeder's equation
  - [ ] Test: Observed response within 20% of prediction
  - **Why**: Validates selection implementation
  - **Time**: 4 hours

### Documentation of Validation

- [ ] **Write validation suite as Jupyter notebook**
  - [ ] Each test is a cell
  - [ ] Includes plots + interpretation
  - [ ] Readable for paper reviewers
  - **Time**: 2 hours

---

## TIER 3: JUPYTER & INTERACTIVE FEATURES (Months 3-4)

These delight researchers. They're not essential, but they're huge for adoption.

### Jupyter Integration

- [ ] **ipywidgets parameter sliders**
  - [ ] `@interact` decorator for parameters
  - [ ] mutation_rate slider (0.0 to 0.1)
  - [ ] population_size slider (100 to 10000)
  - [ ] Rerun simulation with new params
  - [ ] Live plot update (within 1 sec)
  - [ ] Test: Works in Jupyter + JupyterLab
  - **Why**: Researchers want to explore "what if?"
  - **Time**: 3 hours
  - **Library**: `ipywidgets`

- [ ] **Progress bar**
  - [ ] `tqdm` for long simulations
  - [ ] Shows ETA + percentage
  - [ ] Test: Works in Jupyter + terminal
  - **Why**: Reassurance that simulation is running
  - **Time**: 1 hour

- [ ] **Inline plotting**
  - [ ] `%matplotlib inline` compatible
  - [ ] Plots appear below code cells
  - [ ] Test: Plots render without `plt.show()`
  - **Why**: Standard Jupyter workflow
  - **Time**: 1 hour (automatic if using matplotlib)

- [ ] **Rich repr for agents**
  - [ ] `print(agent)` shows genome + fitness
  - [ ] `repr(model)` shows summary stats
  - [ ] Pretty-printed DataFrames in Jupyter
  - **Why**: Debugging + exploration
  - **Time**: 2 hours

### Visualization

- [ ] **Population spatial visualization**
  - [ ] Plot agents in 2D space (if ContinuousSpace)
  - [ ] Color by fitness, genotype, or phenotype
  - [ ] Show GRN connections
  - [ ] Test: Renders within 1 second for 1000 agents
  - **Why**: Qualitative understanding of dynamics
  - **Time**: 6 hours
  - **Library**: `matplotlib` or `plotly`

- [ ] **GRN (Gene Regulatory Network) visualization**
  - [ ] Graph: nodes = genes, edges = regulatory relationships
  - [ ] Color nodes by expression level
  - [ ] Test: Handles 20-100 genes without lag
  - **Why**: Understand which genes are active
  - **Time**: 4 hours
  - **Library**: `networkx` + `matplotlib` / `plotly`

- [ ] **Fitness landscape animation** (optional)
  - [ ] Show evolution of fitness over generations
  - [ ] Histogram + line plot
  - [ ] Save as MP4
  - **Time**: 5 hours
  - **Library**: `matplotlib.animation`

---

## TIER 4: PUBLICATION & REPRODUCIBILITY (Months 5-6)

These unlock academic credibility.

### Citation & DOI

- [ ] **BibTeX entry generator**
  - [ ] `model.to_bibtex()` → ready-to-paste citation
  - [ ] Includes version + GitHub URL
  - **Time**: 1 hour
  - **Example**:
    ```bibtex
    @software{happygene2026,
      author = {Your Name},
      title = {HappyGene: Population-Scale Gene Evolution Simulator},
      year = {2026},
      url = {https://github.com/yourname/happygene},
      doi = {10.5281/zenodo.XXXXX}
    }
    ```

- [ ] **Zenodo integration** (automatic DOI)
  - [ ] Each release gets a DOI via Zenodo
  - [ ] Test: DOI resolves correctly
  - **Why**: Permanent reference + citable
  - **Time**: 1 hour (configuration)

### Metadata & Versioning

- [ ] **Model metadata tracking**
  - [ ] Store in JSON: version, seed, parameters, timestamp
  - [ ] Export with results: `results.to_json(include_metadata=True)`
  - [ ] Restore model from metadata: `GeneModel.from_metadata("metadata.json")`
  - **Why**: Reproducibility across time + machines
  - **Time**: 2 hours

- [ ] **Version pinning in requirements**
  - [ ] `requirements.txt` with exact versions
  - [ ] Test: Same requirements → same results (with same seed)
  - **Why**: Reviewers can reproduce exactly
  - **Time**: 1 hour

---

## TIER 5: ADVANCED ECOSYSTEM (Months 7-12)

These are "differentiators" — nice-to-have but not critical.

### Parameter Fitting

- [ ] **Basic grid search**
  - [ ] `fitter = ParameterGridSearch(model, param_ranges, metric='fitness')`
  - [ ] Tries all combinations
  - [ ] Returns best parameters
  - [ ] Test: Finds global optimum on toy problem
  - **Why**: Researchers need to fit to experiments
  - **Time**: 3 hours

- [ ] **scipy.optimize backend**
  - [ ] `minimize(loss, bounds=bounds, method='L-BFGS-B')`
  - [ ] Gradient-free + gradient-based options
  - [ ] Test: Finds optimum faster than grid search
  - **Why**: Handles continuous parameter spaces
  - **Time**: 4 hours

### GPU Acceleration (Optional, Year 2)

- [ ] **JAX backend** (optional path)
  - [ ] `GeneModel(backend='jax')` → GPU acceleration
  - [ ] 10-100x speedup for 100K+ agents
  - [ ] Test: Same seed → same results as NumPy
  - **Why**: Researchers with 1M agents
  - **Time**: 20+ hours (major undertaking)
  - **Library**: `jax`

### Rule-Based Network Definition (Optional)

- [ ] **Simple rule syntax**
  - [ ] Define GRN via rules (like BioNetGen)
  - [ ] Avoid combinatorial explosion
  - [ ] Example: `model.add_rule("TF_X → activate Gene_Y if conc > 0.5")`
  - **Time**: 10+ hours (lower priority)

---

## INTEGRATION TESTING (CRITICAL)

### End-to-End Workflow

- [ ] **Test: Researcher's typical workflow**
  ```python
  # 1. Create + run simulation
  model = happygene.GeneModel(n_agents=1000, seed=42)
  model.simulate(steps=100)

  # 2. Export to DataFrame
  df = model.to_dataframe()

  # 3. Analyze with pandas
  df.groupby("generation").fitness.mean().plot()

  # 4. Export for paper
  model.to_csv("results.csv")
  model.to_hdf5("results.h5")

  # 5. Validate results
  assert validation.hardy_weinberg(model.final_state)

  # 6. Get citation
  cite = model.to_bibtex()
  print(cite)
  ```
  - [ ] All steps complete without error
  - [ ] Results are reproducible (same seed)
  - [ ] Plots are publication-quality
  - **Time**: 2 hours testing

---

## DOCUMENTATION INTEGRATION

For each feature, write:

- [ ] **Docstring** (API level)
  ```python
  def to_dataframe(self):
      """Export simulation history to pandas DataFrame.

      Returns:
          pd.DataFrame: Rows=steps, Columns=agent_id, fitness, genes, ...

      Example:
          model.simulate(steps=100)
          df = model.to_dataframe()
          df.groupby("generation").fitness.mean().plot()
      """
  ```

- [ ] **Usage notebook** (for researchers)
  - Concrete example
  - Expected output
  - Interpretation tips

- [ ] **API reference** (auto-generated)
  - Parameter descriptions
  - Return types
  - Exceptions

---

## COMPLETION CHECKLIST

### Phase 1 (Foundation) — Weeks 1-10

- [ ] All Tier 0 features complete (8 items)
- [ ] ≥80% test coverage
- [ ] CI/CD passing on 3+ platforms (Linux, macOS, Windows)
- [ ] README works for first-time users
- [ ] Installation is one command: `pip install happygene`

**Go/No-Go Decision**: Can researchers run their first simulation in <5 minutes?

### Phase 2 (Stability) — Months 3-6

- [ ] All Tier 1 features complete (9 items)
- [ ] Tier 2 validation tests complete (8 items)
- [ ] 5+ realistic example notebooks
- [ ] API fully documented
- [ ] Jupyter integration working

**Go/No-Go Decision**: Can researchers use HappyGene in their research without writing custom code?

### Phase 3 (Ecosystem) — Months 7-12

- [ ] Tier 3 (Jupyter) features complete (6 items)
- [ ] Tier 4 (Publication) features complete (4 items)
- [ ] JOSS paper submitted + under review
- [ ] Bioconda package released
- [ ] 10+ community-contributed examples

**Go/No-Go Decision**: Is HappyGene trusted enough to cite in papers?

---

## SUCCESS METRICS (Quarterly Check)

| Metric | Phase 1 | Phase 2 | Phase 3 | Measurement |
|--------|---------|---------|---------|-------------|
| Test Coverage | ≥80% | ≥85% | ≥90% | `coverage.py` |
| Jupyter Works | Basic | Advanced | Polished | Notebooks run without error |
| Pandas Compat | ✓ | ✓ | ✓ | `df = model.to_dataframe()` works |
| Export Formats | CSV | +HDF5, SBML | +Zarr | File I/O tests pass |
| Validation Tests | 0 | ≥8 | ≥15 | Population genetics validated |
| Example Notebooks | 2-3 | 5+ | 10+ | `docs/examples/` directory |
| Documentation | 50% | 90% | 100% | API + usage covered |
| Downloads/Month | <100 | 500+ | 2000+ | PyPI stats |
| GitHub Stars | <50 | 50-200 | 200+ | Community interest |
| Citations | 0 | 1-5 | 10+ | Google Scholar |

---

## QUICK REFERENCE: What Researchers Need Most

**Priority Ranking** (by adoption impact):

1. **pandas DataFrame export** — 90% of researchers will use this
2. **Seed control + reproducibility** — 85% require this
3. **CSV export** — 70% need non-Python sharing
4. **Jupyter compatibility** — 70% use notebooks
5. **Validation tests** — 50% check results against theory
6. **HDF5 export** — 30% have large populations
7. **SBML import** — 20% collaborate on GRN models
8. **GPU acceleration** — 10% have massive populations

Focus on #1-4 first. Everything else is "nice-to-have."

---

## FINAL CHECKLIST

Before saying "feature complete," verify:

- [ ] All exports work (to_dataframe, to_csv, to_json, to_hdf5)
- [ ] All imports work (from_sbml, from_config, from_metadata)
- [ ] Jupyter notebooks work without errors
- [ ] Matplotlib/seaborn plots look publication-quality
- [ ] Validation tests pass (HW, drift, fixation, selection)
- [ ] Seed control verified (same seed = same results)
- [ ] Large population (100K agents) runs in <1 minute
- [ ] Small population (50 agents) shows genetic drift
- [ ] Docstrings complete + examples working
- [ ] Citation metadata embedded in results

**Document Status**: Actionable implementation checklist for ecosystem maturity
**Next Step**: Map each item to dev tasks + assign owners

