"""What the reader sees instead of internal variable names.

`spot_y` and `spot_z` mean nothing on the page -- they're what the code calls
two directions on a glowing screen, and nothing anywhere told the reader that.
Every place the transcript names an observable or a parameter goes through
here, once, so there's a single spot to fix if a label is unclear rather than
four call sites that can drift out of sync with each other.
"""

from __future__ import annotations

#: (short label, unit) for every observable a detector can report. Short on
#: purpose -- these repeat on every reading line, so the full explanation of
#: what "plate-shift" physically means lives once, in the SETUP note the
#: agent gives the first time it matters, not re-stated dozens of times.
OBSERVABLE_GLOSS: dict[str, tuple[str, str]] = {
    "spot_y":      ("plate-shift", ""),
    "spot_z":      ("magnet-shift", ""),
    "glow":        ("screen lit", ""),
    "sharpness":   ("focus", ""),
    "charge_rate": ("current caught by the cup", "amps"),
    "caught_beam": ("cup is catching the beam", ""),
    "paddle_rate": ("push on the paddle wheel", ""),
    "heat_rate":   ("heat in the thermopile", ""),
}

#: keys whose float value (0.0 / 1.0) is really a yes/no, not a quantity
YES_NO_KEYS = {"glow", "caught_beam"}

PARAM_GLOSS: dict[str, str] = {
    "e_over_m": "the charge-to-mass ratio",
    "speed_coeff": "the beam's speed (per root-volt)",
}


def label(key: str) -> str:
    return OBSERVABLE_GLOSS.get(key, (key, ""))[0]


def param_label(key: str) -> str:
    return PARAM_GLOSS.get(key, key)


def param_list(keys) -> str:
    return " and ".join(param_label(k) for k in keys)


def format_reading(key: str, value) -> str:
    """One observable, formatted for the transcript: label, then value."""
    lbl = label(key)
    if key in YES_NO_KEYS or isinstance(value, bool):
        return f"{lbl}: {'yes' if value else 'no'}"
    if isinstance(value, float):
        unit = OBSERVABLE_GLOSS.get(key, ("", ""))[1]
        return f"{lbl}: {value:.4g}{(' ' + unit) if unit else ''}"
    return f"{lbl}: {value}"


def format_readings(obs: dict) -> str:
    return ", ".join(format_reading(k, v) for k, v in obs.items())


def label_list(keys) -> str:
    """A sorted set of observable keys, e.g. from a discrimination search."""
    return ", ".join(label(k) for k in sorted(keys))
