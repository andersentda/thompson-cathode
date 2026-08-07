"""Designing an experiment: searching the space of apparatus you could build.

Two different jobs, and conflating them is a mistake:

DISCRIMINATE -- when several theories are alive, find the apparatus whose
    QUALITATIVE signature differs across them. No numbers needed: "a charged
    beam bends toward a positive plate, a wave does not" settles the design
    without knowing any magnitude. Cheap to search, and it is how design
    reasoning actually proceeds.

IDENTIFY -- when one theory leads but its parameters are unknown, find the
    apparatus that pins them down. This is not information about WHICH theory
    is right; it is about whether the measurements you would get are even
    capable of determining the numbers you want.

The second is where the crossed-field experiment comes from, and it is not
hardcoded anywhere. With two unknowns (charge-to-mass ratio and beam speed),
any single deflection gives one equation in two unknowns -- the Jacobian has
rank 1 and the system is underdetermined no matter how precisely you measure.
Only an apparatus carrying BOTH an electric and a magnetic deflection has a
full-rank Jacobian. The designer discovers that by computing determinants over
candidate builds, and the crossed-field tube falls out as the answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np

from . import gloss
from .theory import PRESENT, ABSENT, UNCOMMITTED, Theory
from .world import Config, component_catalogue


def enumerate_configs(catalogue=None, cap: int | None = None) -> list[Config]:
    """Every apparatus the agent could assemble from the parts on hand."""
    cat = catalogue or component_catalogue()
    keys = list(cat.keys())
    out = []
    for combo in product(*[cat[k] for k in keys]):
        out.append(Config(**dict(zip(keys, combo))))
        if cap and len(out) >= cap:
            break
    return out


# ------------------------------------------------------------- discriminate


@dataclass
class Design:
    config: Config
    score: float
    rationale: str


def discriminating_design(theories: list[Theory], configs: list[Config],
                          top: int = 1) -> list[Design]:
    """Find the build whose outcome the live theories most disagree about."""
    live = [t for t in theories if not t.dead]
    if len(live) < 2:
        return []

    scored: list[Design] = []
    for cfg in configs:
        sigs = [t.qualitative(cfg) for t in live]
        keys = set().union(*[set(s.keys()) for s in sigs])
        splits, detail = 0, []
        for k in keys:
            vals = {s.get(k, UNCOMMITTED) for s in sigs}
            vals.discard(UNCOMMITTED)
            if len(vals) > 1:
                splits += 1
                detail.append(k)
        if not splits:
            continue
        score = splits / cfg.cost()
        who = " vs ".join(t.name for t in live)
        scored.append(Design(cfg, score,
                             f"{gloss.label_list(detail)} would differ between {who}"))

    scored.sort(key=lambda d: -d.score)
    return scored[:top]


# ---------------------------------------------------------------- identify


def jacobian(theory: Theory, cfg: Config, obs_keys: list[str]) -> np.ndarray:
    """d(observable) / d(parameter), by central differences on the theory."""
    names = list(theory.param_names)
    J = np.zeros((len(obs_keys), len(names)))
    base = dict(theory.params)
    for j, nm in enumerate(names):
        h = abs(base[nm]) * 1e-4 or 1e-6
        up, dn = dict(base), dict(base)
        up[nm], dn[nm] = base[nm] + h, base[nm] - h
        pu, pd = theory.predict(cfg, up), theory.predict(cfg, dn)
        for i, k in enumerate(obs_keys):
            J[i, j] = (pu.get(k, 0.0) - pd.get(k, 0.0)) / (2 * h)
    return J


def identifiability(theory: Theory, cfg: Config) -> tuple[float, int, list[str]]:
    """Can this single build determine the theory's parameters at all?

    Returns (conditioning, rank, observables). Rank below the parameter count
    means underdetermined: the measurements constrain only some combination of
    the unknowns, and no amount of precision will separate them.
    """
    pred = theory.predict(cfg)
    keys = [k for k, v in pred.items()
            if isinstance(v, (int, float)) and abs(v) > 1e-12 and k != "glow"]
    if not keys:
        return 0.0, 0, []
    J = jacobian(theory, cfg, keys)
    # scale each row by its own magnitude so units don't dominate
    scale = np.array([abs(pred[k]) for k in keys])[:, None]
    Jn = J / np.where(scale < 1e-30, 1.0, scale)
    if Jn.shape[0] < Jn.shape[1]:
        return 0.0, int(np.linalg.matrix_rank(Jn, tol=1e-8)), keys
    sv = np.linalg.svd(Jn, compute_uv=False)
    rank = int(np.sum(sv > sv[0] * 1e-8)) if sv[0] > 0 else 0
    cond = float(sv[-1] / sv[0]) if sv[0] > 0 else 0.0
    return cond, rank, keys


def identifying_design(theory: Theory, configs: list[Config],
                       top: int = 3) -> list[Design]:
    """Search for a build that actually determines the unknowns."""
    n_par = len(theory.param_names)
    out: list[Design] = []
    for cfg in configs:
        cond, rank, keys = identifiability(theory, cfg)
        if rank < n_par:
            continue                       # underdetermined, skip
        out.append(Design(cfg, cond / cfg.cost(),
                          f"measures {gloss.label_list(keys)}: rank {rank} of "
                          f"{n_par} unknowns, so both are separable"))
    out.sort(key=lambda d: -d.score)
    return out[:top]


def underdetermined_report(theory: Theory, configs: list[Config],
                           n: int = 4) -> list[str]:
    """Why the obvious single-measurement builds are not enough."""
    lines, seen = [], set()
    for cfg in configs:
        cond, rank, keys = identifiability(theory, cfg)
        if rank == 0 or rank >= len(theory.param_names):
            continue
        sig = tuple(keys)
        if sig in seen:
            continue
        seen.add(sig)
        lines.append(f"{gloss.label_list(keys)} alone -> rank {rank} of "
                     f"{len(theory.param_names)}: fixes only a combination of "
                     f"{gloss.param_list(theory.param_names)}, never each separately")
        if len(lines) >= n:
            break
    return lines
