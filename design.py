"""The cathode-ray sandbox: a world with a hidden physics and a kit of parts.

The agent never sees anything in this file. It sees a catalogue of components it
may assemble, and whatever its chosen detector reports back.

This is the deliberate difference from the mechanics sandbox. There, five
finished instruments were handed over and the only decision left was where to
point them. Here there are no instruments -- only parts, and the whole problem
is working out what to build.

THE TRAP
--------
Electrostatic deflection is screened by residual gas: the beam ionises it, the
ions migrate to the plates and cancel the field inside the tube. So a charged
beam shows NO electrostatic deflection in a mediocre vacuum, while showing
magnetic deflection perfectly well. This is not a simulation artefact -- it is
why Hertz concluded in 1883 that cathode rays were uncharged, and why Thomson
in 1897 got the opposite answer with a better pump.

An agent that treats the null result as decisive evidence against charge will
reproduce Hertz's error. Getting past it requires blaming the apparatus, which
is the capability under test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

# ---------------------------------------------------------------- constants
# ground truth, never exposed
EM_TRUE = 1.76e11          # C/kg for the ray carrier
EM_HYDROGEN_ION = 9.58e7   # C/kg, known to the agent from electrolysis
L_PLATE = 0.050            # m, length of the deflecting plates
D_PLATE = 0.015            # m, plate separation
L_DRIFT = 0.20             # m, plates to screen
K_COIL = 1.4e-3            # tesla per amp
GAS_CRITICAL = 0.02        # screening scale
# calibrated so a 200V shot reads paddle_rate=0.9, heat_rate=1.3 -- matching
# the numbers already seen in Phase 1 of every transcript so far
PADDLE_K = 0.9 / math.sqrt(200.0)
HEAT_K = 1.3 / 200.0
SPOT_THRESHOLD = 0.0015    # m; a smaller shift than this cannot be seen at all
NOISE = 0.02

CATHODES = ["aluminium", "iron", "platinum"]
GASES = ["air", "hydrogen", "carbon dioxide"]


@dataclass(frozen=True)
class Config:
    """One assembled apparatus. This is the object the agent searches over."""

    detector: str = "screen"        # screen | collector | paddle | thermopile
    vacuum: float = 0.30            # 0 = crude pump, 1 = best achievable
    accel_volts: float = 200.0
    plate_volts: float = 0.0        # deflecting plates; 0 = not fitted
    coil_amps: float = 0.0          # magnet coils; 0 = not fitted
    cathode: str = "aluminium"
    gas: str = "air"

    def cost(self) -> float:
        """Pumping harder and fitting more parts costs bench time."""
        c = 1.0 + 6.0 * self.vacuum ** 3
        if self.plate_volts:
            c += 0.6
        if self.coil_amps:
            c += 0.6
        if self.detector in ("collector", "thermopile"):
            c += 0.8
        return c

    def label(self) -> str:
        bits = [f"{self.detector}", f"vac={self.vacuum:.2f}",
                f"V={self.accel_volts:.0f}"]
        if self.plate_volts:
            bits.append(f"plates={self.plate_volts:.0f}V")
        if self.coil_amps:
            bits.append(f"coils={self.coil_amps:.2f}A")
        if self.cathode != "aluminium":
            bits.append(self.cathode)
        if self.gas != "air":
            bits.append(self.gas)
        return "  ".join(bits)


# ---------------------------------------------------------------- the world


class CathodeWorld:
    """Ground truth. Answers what a given apparatus actually shows."""

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)
        self.shots = 0
        self.bench_time = 0.0

    # -- hidden physics -----------------------------------------------

    def _gas_density(self, cfg: Config) -> float:
        return (1.0 - cfg.vacuum) ** 2

    def _screen_factor(self, cfg: Config) -> float:
        """Fraction of the applied plate field that survives inside the tube.

        Sharp, not gradual: the ions only need to reach the plates to cancel
        the field, so a mediocre vacuum kills the effect almost entirely rather
        than merely weakening it. That sharpness is what made the historical
        null result look decisive.
        """
        n = self._gas_density(cfg)
        return 1.0 / (1.0 + (n / GAS_CRITICAL) ** 2)

    def _speed(self, cfg: Config) -> float:
        return math.sqrt(2.0 * EM_TRUE * cfg.accel_volts)

    def _noisy(self, x: float) -> float:
        return float(x * np.exp(self.rng.normal(0.0, NOISE)))

    # -- what the detector reports ------------------------------------

    def run(self, cfg: Config) -> dict:
        """Assemble and fire. Returns only what this detector can report."""
        self.shots += 1
        self.bench_time += cfg.cost()

        v = self._speed(cfg)
        out: dict = {}

        if cfg.detector == "screen":
            # a visible spot; deflections are what move it
            E = (cfg.plate_volts / D_PLATE) * self._screen_factor(cfg)
            B = K_COIL * cfg.coil_amps
            # vertical deflection from the plates, horizontal from the coils
            y = EM_TRUE * E * L_PLATE * (L_PLATE / 2 + L_DRIFT) / (v ** 2)
            z = EM_TRUE * B * L_PLATE * (L_PLATE / 2 + L_DRIFT) / v
            # below the threshold the spot simply does not visibly move
            out["spot_y"] = self._noisy(y) if abs(y) > SPOT_THRESHOLD else 0.0
            out["spot_z"] = self._noisy(z) if abs(z) > SPOT_THRESHOLD else 0.0
            out["glow"] = 1.0
            # in a poor vacuum the beam scatters and the spot smears
            out["sharpness"] = float(np.clip(cfg.vacuum * 1.4, 0.05, 1.0))

        elif cfg.detector == "collector":
            # a cup off the straight-through axis: only catches the beam if
            # the beam can be bent into it, which needs the coils
            B = K_COIL * cfg.coil_amps
            z = EM_TRUE * B * L_PLATE * (L_PLATE / 2 + L_DRIFT) / v
            caught = abs(z) > 0.012
            out["charge_rate"] = self._noisy(2.4e-9) if caught else 0.0
            out["caught_beam"] = 1.0 if caught else 0.0

        elif cfg.detector == "paddle":
            # momentum transfer per particle is proportional to v; total
            # transfer rate (flux held fixed) therefore goes as v ~ sqrt(volts).
            # This is a genuine, checkable consequence of the corpuscle
            # picture that nothing in Phase 1-5 was ever fit to.
            out["paddle_rate"] = self._noisy(PADDLE_K * math.sqrt(cfg.accel_volts))

        elif cfg.detector == "thermopile":
            # kinetic energy per particle goes as v^2 ~ volts -- LINEAR in the
            # accelerating potential, a different exponent than the paddle.
            # A wave with no charge to accelerate has no reason to tie its
            # energy content to this voltage at all.
            out["heat_rate"] = self._noisy(HEAT_K * cfg.accel_volts)

        return out

    # -- for scoring only; the agent never calls these -----------------

    def truth(self) -> dict:
        return {"e_over_m": EM_TRUE, "hydrogen_ion_e_over_m": EM_HYDROGEN_ION}


# ---------------------------------------------------------------- catalogue


def component_catalogue() -> dict:
    """What the agent knows it can build with, and nothing more."""
    return {
        "detector": ["screen", "collector", "paddle", "thermopile"],
        "vacuum": [0.10, 0.30, 0.55, 0.80, 0.95],
        "accel_volts": [120.0, 200.0, 400.0],
        "plate_volts": [0.0, 60.0, 140.0],
        "coil_amps": [0.0, 0.35, 0.80],
        "cathode": CATHODES,
        "gas": GASES,
    }
