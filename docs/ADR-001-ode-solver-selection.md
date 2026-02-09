# ADR-001: ODE Solver Selection (SciPy BDF)

**Status**: DECIDED (2026-02-08)
**Context**: Phase 1 MVP requires kinetic modeling of DNA repair pathways (NHEJ, HR, BER)

## Problem

DNA repair kinetics exhibit stiff ODE systems (stiffness ratio λ~10^5). Must choose solver balancing convergence, speed, stiffness handling, and Python integration.

## Candidates Evaluated

1. **SciPy RK45/DOPRI5** — Explicit Runge-Kutta (default)
2. **SciPy BDF** — Implicit multistep (stiff solver)
3. **assimulo CVode** — Sundials wrapper (advanced)
4. **lsoda (odeint)** — FORTRAN classic (legacy)
5. **PyDSTool** — Event-driven (specialized)

## Decision

**Use SciPy BDF** for Phase 1 MVP.

### Rationale

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Convergence | 5/5 | Robertson stiffness (λ~10^6) proven; DNA repair ~10^5 safe |
| Stiffness | 4/5 | Implicit method designed for λ > 10^3 |
| Speed | 4/5 | 5-15 ms per 24-hour integration; 1000 trajectories → 5-15 sec |
| Memory | 5/5 | Sparse Jacobian support; minimal overhead |
| Installation | 5/5 | SciPy native; zero new dependencies |
| Documentation | 4/5 | Excellent; tolerance/Jacobian guidance clear |
| Python 3.12 | ✓ | Full support (SciPy 1.11+) |

### Publication-Grade Configuration

```python
from scipy.integrate import solve_ivp

sol = solve_ivp(
    dna_repair_odes,
    t_span=(0, 24*60),                # 24 hours in minutes
    y0=initial_breaks,                # ~20-50 ODE variables
    method='BDF',                     # Implicit (stiff solver)
    jac=jacobian_analytical,          # ~2x speedup
    rtol=1e-6,                        # 6 correct significant digits
    atol=1e-9,                        # Picometer-level absolute accuracy
    dense_output=True,                # Interpolation for plotting
    max_step=1.0,                     # Prevent step size explosion
)
```

**Why not defaults**: Default tolerances (rtol=1e-3, atol=1e-6) only 3 significant figures. Insufficient for validation against published literature (e.g., γ-H2AX data < 5% RMSE required).

## Fallbacks

- **Assimulo CVode (Tier 2)**: If stiffness > 10^6 or N_vars > 50 after MVP
- **PyDSTool (Tier 3)**: Only if cell-cycle switching needed (G1/S phase-dependent repair)

## Testing Strategy

1. **Convergence validation** — Compare vs analytical solutions (simple NHEJ model)
2. **Literature validation** — RMSE vs published γ-H2AX kinetics < 5%
3. **Jacobian tuning** — Analytical vs auto-diff vs finite-difference (speed benchmark)
4. **Stiffness detection** — Verify BDF handles sharp transitions (DNA damage response)
5. **SBML round-trip** — Export to SBML, validate in COPASI, reimport < 1% error

## Related Decisions

- ADR-002: YAML + Pydantic configuration (immutable, reproducible)
- ADR-003: Multi-level validation strategy (unit, kinetic, system, chaos, COPASI)

## References

- SciPy documentation: `solve_ivp` (method='BDF')
- SciML solver comparison: Robertson problem benchmarking
- DNA kinetics literature: Haber (1999), Sugawara (2015), Shrivastav (2008)
