.. _theory:

===============================================
Theory & Mathematical Background
===============================================

This section explains the biological and mathematical foundations of happygene.

--------

Gene Expression Models
======================

Gene expression is the process by which genetic information (DNA) is converted into functional gene products (proteins). happygene models expression as a scalar value (0 or higher).

Constant Expression
-------------------

The simplest model: all genes express at a constant level regardless of conditions.

.. math::

   E = L

where :math:`L` is the fixed expression level.

**Use case**: Simple baseline simulations where expression doesn't vary.

Linear Expression
-----------------

Gene expression proportional to transcription factor (TF) concentration:

.. math::

   E = m \cdot [TF] + b

where:
- :math:`m` is the slope (sensitivity)
- :math:`b` is the intercept (basal expression)

**Use case**: Simple regulatory interactions, repression (negative slope).

Hill Kinetics
-------------

The Hill equation models cooperative binding of transcription factors:

.. math::

   E = \frac{V_{max} \cdot [TF]^n}{K^n + [TF]^n}

where:

- :math:`V_{max}` is maximum expression level
- :math:`K` is the half-saturation constant (TF level at 50% response)
- :math:`n` is the Hill coefficient (cooperativity):

  - n=1: Michaelis-Menten kinetics (no cooperativity)
  - n>1: Positive cooperativity (switch-like response)
  - n<1: Negative cooperativity (hyperbolic)

**Use case**: Realistic gene regulation with sigmoidal response curves and cooperative binding.

--------

Selection Models
================

Selection determines which individuals survive to reproduce based on their fitness.

Proportional Selection
----------------------

Fitness equals mean gene expression:

.. math::

   w = \frac{1}{G} \sum_{i=1}^{G} E_i

where:
- :math:`w` is fitness
- :math:`G` is number of genes
- :math:`E_i` is expression level of gene i

**Effect**: Individuals with higher average expression have higher fitness. All survive with continuous variation.

**Use case**: Directional selection toward higher expression.

Threshold Selection
-------------------

Binary fitness based on whether mean expression exceeds threshold:

.. math::

   w = \begin{cases}
   1.0 & \text{if } \bar{E} > \theta \\
   0.0 & \text{if } \bar{E} \leq \theta
   \end{cases}

where:
- :math:`\bar{E}` is mean expression
- :math:`\theta` is the threshold

**Effect**: Creates a fitness bottleneck. Only individuals above threshold survive.

**Use case**: Disruptive selection, developmental thresholds, fitness cliffs.

--------

Mutation Models
===============

Mutations introduce genetic variation each generation.

Point Mutation
--------------

Random changes to gene expression levels:

.. math::

   E_{\text{new}} = E_{\text{old}} + \Delta E

where :math:`\Delta E \sim \mathcal{N}(0, \sigma^2)` is drawn from normal distribution with:

- **Rate** (per-gene probability): probability that each gene mutates in each generation
- **Magnitude** (:math:`\sigma`): standard deviation of the change

Expression is clamped to [0, ∞) after mutation.

**Use case**: Continuous variation in gene expression, evolutionary optimization.

--------

Population Genetics Theory
===========================

Neutral Drift
-------------

When selection is absent (fitness equal for all individuals), allele frequencies change randomly due to sampling effects (genetic drift).

**In happygene**: Set fitness to constant (e.g., ProportionalSelection with no expression variation, or all individuals at exactly threshold).

Selection Response
------------------

The mean fitness of a population changes over time due to selection:

.. math::

   R = h^2 \cdot S

where:
- :math:`R` is response to selection
- :math:`h^2` is heritability
- :math:`S` is selection differential

**In happygene**: Mutations provide variation (heritability). Selection pressure depends on SelectionModel and expression distribution.

Linkage Equilibrium
-------------------

happygene assumes genes are independent (no linkage disequilibrium). Each gene evolves independently.

--------

Reproducibility
================

All happygene simulations are deterministic when seeded:

.. math::

   \text{Simulation}_{\text{seed=s}} = \text{Simulation}_{\text{seed=s}} \quad \forall \text{ runs}

This makes happygene ideal for:
- Validation against theoretical predictions
- Comparison of alternative models
- Publication of reproducible results

--------

Mathematical Properties
=======================

**Expression bounds**: :math:`E \in [0, \infty)`

**Fitness bounds**: Depends on SelectionModel:
- ProportionalSelection: :math:`w \in [0, V_{max}]` (max depends on expression model)
- ThresholdSelection: :math:`w \in \{0, 1\}`

**Population size**: Constant across generations (no birth/death dynamics)

**Generations**: Discrete time steps (not continuous time ODEs)

--------

See Also
========

- Getting Started for implementation examples
- API Reference for class documentation
- GitHub examples for biological applications
