"""Two checks a theory has to pass that have nothing to do with fitting data.

`overidentification` is the toy-world analogue of a renormalizability proof.
't Hooft didn't test the electroweak theory against new data in 1971 -- he
proved that its OWN internal structure was consistent, that it didn't produce
contradictions regardless of how you probed it. The measurable version of that
here: solve for the same two unknowns from several INDEPENDENT builds. A
theory whose extracted parameters agree with themselves, shot to shot, has
passed a real consistency test that has nothing to do with ground truth --
you do not need to know the right answer to check whether your own method
keeps giving you the same one.

`retrodiction` is Higgs solving the Goldstone problem he wasn't trying to
solve. Once a theory's free parameters are pinned down by one kind of
apparatus, does its now-fully-specified form correctly describe a
DIFFERENT apparatus it was never fit to? A theory that only ever explains
the data used to build it is doing curve-fitting. One that explains
something else, unprompted, has bought itself real credence -- Dawid's
"unexpected explanatory coherence" made measurable.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .theory import Theory
from .world import D_PLATE, K_COIL, L_DRIFT, L_PLATE, Config


def _solve_em_speed(cfg: Config, obs: dict, theory: Theory) -> tuple[float, float]:
    lever = L_PLATE * (L_PLATE / 2 + L_DRIFT)
    y, z = obs["spot_y"], obs["spot_z"]
    E = cfg.plate_volts / D_PLATE * theory.aux_factor(cfg)
    B = K_COIL * cfg.coil_amps
    em = (z ** 2) * E / (y * B ** 2 * lever)
    v = em * B * lever / z
    return em, v / (cfg.accel_volts ** 0.5)


@dataclass
class OveridentificationReport:
    em_values: list
    speed_values: list
    em_spread: float          # coefficient of variation, unitless
    consistent: bool


def overidentification_check(theory: Theory,
                             shots: list[tuple[Config, dict]]) -> OveridentificationReport:
    """Solve the same two unknowns from every shot; they should agree with
    EACH OTHER, not with any ground truth this function never sees."""
    ems, speeds = [], []
    for cfg, obs in shots:
        em, k = _solve_em_speed(cfg, obs, theory)
        ems.append(em)
        speeds.append(k)
    ems = np.array(ems)
    spread = float(ems.std() / ems.mean()) if len(ems) > 1 else 0.0
    return OveridentificationReport(list(ems), list(speeds), spread, spread < 0.15)


@dataclass
class RetrodictionReport:
    detector: str
    predicted_exponent: float
    measured_exponent: float
    agrees: bool


def retrodiction_check(theory: Theory, world, detector: str,
                       volts: tuple[float, float] = (120.0, 400.0),
                       n_rep: int = 3) -> RetrodictionReport | None:
    """Does the theory's FORM predict apparatus it was never fit to?

    No solved parameter enters this at all -- `scaling_signature` is a claim
    about the theory's shape, checked against a log-log slope from data the
    identification phase never touched.
    """
    predicted = theory.scaling_signature(detector)
    if predicted is None:
        return None
    key = {"paddle": "paddle_rate", "thermopile": "heat_rate"}[detector]
    readings = []
    for vlt in volts:
        vals = [world.run(Config(detector=detector, accel_volts=vlt))[key]
                for _ in range(n_rep)]
        readings.append(float(np.mean(vals)))
    slope = (np.log(readings[1]) - np.log(readings[0])) / \
            (np.log(volts[1]) - np.log(volts[0]))
    return RetrodictionReport(detector, predicted, float(slope),
                              abs(slope - predicted) < 0.12)
