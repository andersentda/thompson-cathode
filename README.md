"""Theories as programs, and the ledger that keeps them honest.

A theory here is not a curve. It is a small program that, given an apparatus,
says what that apparatus would show -- including saying "nothing" and including
refusing to commit. That is what makes it possible to design an experiment
against it before running anything.

Two things matter for the capability under test:

`qualitative()` returns signs and presences only (+ / 0 / ?). Experiment design
    happens here, because you do not need numbers to know that a charged beam
    should bend toward a positive plate. Numbers come later, for the survivors.

`Auxiliary` is the Duhem machinery. When a prediction fails you may either drop
    the theory or add an auxiliary assumption -- but an auxiliary costs
    description length and is admissible only while it carries an INDEPENDENT
    testable consequence that has not yet been checked. If that consequence
    fails, the auxiliary dies. If it is confirmed, the auxiliary has paid for
    itself and is folded in. A system that can always blame the apparatus is
    unfalsifiable; one that never can will throw away correct theories.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

from .world import (Config, D_PLATE, K_COIL, L_DRIFT, L_PLATE,
                    EM_HYDROGEN_ION, SPOT_THRESHOLD)

PRESENT, ABSENT, UNCOMMITTED = "+", "0", "?"


@dataclass
class Auxiliary:
    """An assumption bolted onto a theory to save it from a failed prediction."""

    name: str
    cost_bits: float
    rationale: str
    #: the independent consequence that must be checked before this is honest
    independent_test: str
    status: str = "on probation"      # on probation | amortised | refuted

    def modifies(self, cfg: Config) -> float:
        return 1.0


@dataclass
class ScreeningAuxiliary(Auxiliary):
    """Residual gas conducts and cancels the field between the plates.

    Independent consequence: the missing deflection must REAPPEAR as the pump
    improves. That is a new, checkable prediction, which is exactly what
    separates this from an ad hoc rescue.
    """

    def modifies(self, cfg: Config) -> float:
        n = (1.0 - cfg.vacuum) ** 2
        return 1.0 / (1.0 + (n / 0.02) ** 2)


# ------------------------------------------------------------------ theories


@dataclass
class Precedent:
    """A structural transplant from an already-validated domain.

    This is Anderson pointing at superconductivity before Higgs existed: the
    SAME mechanism, already shown correct somewhere else, recognised as fitting
    a new problem. That recognition is a real, principled reason to prefer a
    theory before any new data comes in -- so it earns a genuine discount on
    the theory's description length.

    It must never become a veto. A precedent lowers the bar a theory has to
    clear; it cannot raise the bar for the evidence against it. If the fit
    penalty overwhelms the discount, the theory still falls -- see
    `Theory.description_bits`, where the discount and the misfit are both
    just nats, added on the same footing as everything else.
    """

    name: str
    source_domain: str
    rationale: str
    discount_bits: float


class Theory:
    name = "theory"
    prior_bits = 0.0
    params: dict[str, float] = {}
    param_names: tuple = ()

    def __init__(self):
        self.params = dict(self.params)
        self.auxiliaries: list[Auxiliary] = []
        self.precedent: Precedent | None = None
        self.dead = False
        self.death_reason = ""

    # -- design-time reasoning: signs only, no numbers ------------------

    def qualitative(self, cfg: Config) -> dict[str, str]:
        raise NotImplementedError

    # -- test-time: actual numbers -------------------------------------

    def predict(self, cfg: Config, params: dict | None = None) -> dict:
        raise NotImplementedError

    #: predicted power-law exponent of a reading against accel_volts, e.g.
    #: paddle_rate ~ volts^0.5 under the corpuscle picture. None = no claim.
    #: This is a structural consequence of the theory's FORM, checkable
    #: without ever solving for e_over_m or speed_coeff.
    def scaling_signature(self, detector: str) -> float | None:
        return None

    # -- bookkeeping ---------------------------------------------------

    def aux_factor(self, cfg: Config) -> float:
        f = 1.0
        for a in self.auxiliaries:
            if a.status != "refuted":
                f *= a.modifies(cfg)
        return f

    def description_bits(self) -> float:
        bits = (self.prior_bits + 8.0 * len(self.param_names)
                + sum(a.cost_bits for a in self.auxiliaries
                      if a.status != "refuted"))
        if self.precedent:
            bits -= self.precedent.discount_bits
        return max(bits, 0.5)     # never free -- every theory costs something

    def __repr__(self):
        aux = "".join(f" +{a.name}" for a in self.auxiliaries if a.status != "refuted")
        pr = f" [{self.precedent.name}]" if self.precedent else ""
        return f"<{self.name}{aux}{pr}>"


class EtherWave(Theory):
    """Cathode rays are a disturbance in the ether: no charge, no matter."""

    name = "ether-wave"
    prior_bits = 6.0
    param_names = ()

    def qualitative(self, cfg):
        q = {}
        if cfg.detector == "screen":
            q["spot_y"] = ABSENT          # a wave has no charge to push
            q["spot_z"] = ABSENT          # nor anything for a magnet to grip
            q["glow"] = PRESENT
        elif cfg.detector == "collector":
            q["charge_rate"] = ABSENT     # nothing is deposited
            q["caught_beam"] = ABSENT
        elif cfg.detector == "paddle":
            q["paddle_rate"] = PRESENT    # radiation pressure would do this
        elif cfg.detector == "thermopile":
            q["heat_rate"] = PRESENT
        return q

    def predict(self, cfg, params=None):
        if cfg.detector == "screen":
            return {"spot_y": 0.0, "spot_z": 0.0, "glow": 1.0}
        if cfg.detector == "collector":
            return {"charge_rate": 0.0, "caught_beam": 0.0}
        if cfg.detector == "paddle":
            return {"paddle_rate": 1.0}
        if cfg.detector == "thermopile":
            return {"heat_rate": 1.0}
        return {}


class ChargedCorpuscle(Theory):
    """The rays are a stream of charged bodies with some charge-to-mass ratio.

    TWO independent unknowns: `e_over_m`, and `speed_coeff` where the beam
    speed is speed_coeff * sqrt(accelerating volts). They are independent
    because the theory does NOT get to assume the bodies fall freely through
    the whole accelerating potential -- that is itself a claim about the
    mechanism, and assuming it would hand the agent the answer.

    This is the entire difficulty of the historical problem. Every single
    deflection mixes the two unknowns together, so no one measurement can
    separate them, and a second independent one is structurally required.
    """

    name = "charged-corpuscle"
    prior_bits = 10.0
    param_names = ("e_over_m", "speed_coeff")

    def __init__(self, e_over_m: float = 1e10, speed_coeff: float = 3.0e5):
        super().__init__()
        self.params = {"e_over_m": e_over_m, "speed_coeff": speed_coeff}

    def speed(self, cfg, em=None, k=None):
        k = self.params["speed_coeff"] if k is None else k
        return k * math.sqrt(cfg.accel_volts)

    def scaling_signature(self, detector):
        # a body accelerated through a potential V gains kinetic energy eV,
        # so v ~ sqrt(V): momentum transfer (paddle) inherits that exponent,
        # kinetic-energy transfer (heat) inherits its square. Neither number
        # needs e_over_m or speed_coeff -- it is a property of the STORY, not
        # of the fitted values, which is what makes it checkable so cheaply.
        return {"paddle": 0.5, "thermopile": 1.0}.get(detector)

    def qualitative(self, cfg):
        q = {}
        if cfg.detector == "screen":
            q["spot_y"] = PRESENT if cfg.plate_volts else ABSENT
            q["spot_z"] = PRESENT if cfg.coil_amps else ABSENT
            q["glow"] = PRESENT
        elif cfg.detector == "collector":
            # only reaches an off-axis cup if the coils bend it there
            q["caught_beam"] = PRESENT if cfg.coil_amps else ABSENT
            q["charge_rate"] = PRESENT if cfg.coil_amps else ABSENT
        elif cfg.detector == "paddle":
            q["paddle_rate"] = PRESENT
        elif cfg.detector == "thermopile":
            q["heat_rate"] = PRESENT
        return q

    def predict(self, cfg, params=None):
        pr = params or self.params
        em, k = pr["e_over_m"], pr["speed_coeff"]
        v = k * math.sqrt(cfg.accel_volts)
        lever = L_PLATE * (L_PLATE / 2 + L_DRIFT)
        if cfg.detector == "screen":
            E = (cfg.plate_volts / D_PLATE) * self.aux_factor(cfg)
            B = K_COIL * cfg.coil_amps
            y, z = em * E * lever / v ** 2, em * B * lever / v
            # the theory knows its own instrument's resolution
            return {"spot_y": y if abs(y) > SPOT_THRESHOLD else 0.0,
                    "spot_z": z if abs(z) > SPOT_THRESHOLD else 0.0,
                    "glow": 1.0}
        if cfg.detector == "collector":
            B = K_COIL * cfg.coil_amps
            z = em * B * lever / v
            caught = abs(z) > 0.012
            return {"charge_rate": 2.4e-9 if caught else 0.0,
                    "caught_beam": 1.0 if caught else 0.0}
        if cfg.detector == "paddle":
            return {"paddle_rate": 1.0}
        if cfg.detector == "thermopile":
            return {"heat_rate": 1.0}
        return {}


class ChargedMolecule(ChargedCorpuscle):
    """Charged gas molecules torn off the cathode.

    Same functional form as the corpuscle theory, but it is committed to a
    charge-to-mass ratio near that of an electrolytic ion -- so it is refuted
    not by its shape but by the SIZE of the number that comes out.
    """

    name = "charged-molecule"
    prior_bits = 8.0        # cheaper: posits nothing new in the world

    def __init__(self):
        super().__init__(e_over_m=EM_HYDROGEN_ION, speed_coeff=3.0e5)

    def plausible_range(self):
        return (EM_HYDROGEN_ION / 4.0, EM_HYDROGEN_ION * 4.0)


# ------------------------------------------------------------------ scoring


def discrepancy(pred: dict, obs: dict) -> float:
    """Log-space mismatch between a prediction and a reading."""
    total = 0.0
    for k, o in obs.items():
        if k not in pred:
            continue
        p = pred[k]
        if o == 0.0 and p == 0.0:
            continue
        if o == 0.0 or p == 0.0:
            total += 9.0                      # predicted presence, saw absence
            continue
        total += (math.log(abs(o)) - math.log(abs(p))) ** 2
    return total


def mdl_score(theory: Theory, record: list[tuple[Config, dict]]) -> float:
    """Lower is better: misfit in nats plus what the theory costs to state."""
    if theory.dead:
        return float("inf")
    fit = sum(discrepancy(theory.predict(c), o) for c, o in record)
    return fit + theory.description_bits() * math.log(2)
