"""The loop.

    explore  ->  anomaly  ->  abduce  ->  design  ->  build  ->  revise

with a meta-controller choosing between two objectives, which is where the
chicken-and-egg goes. You cannot design a discriminating experiment with no
hypotheses to discriminate, and you cannot form a hypothesis with no phenomena.
The resolution is not to pick one as primary: it is to switch objective on
expected information gain. When nothing on the bench would tell the live
theories apart -- because there are none, or because none of them disagree --
the right move is not to keep designing, it is to go and tinker: cheap, crude,
wide sweeps whose product is not a decision but a bigger phenomena ledger.
"""

from __future__ import annotations

import math

import numpy as np

from . import abduce as ab, gloss
from .coherence import overidentification_check, retrodiction_check
from .design import (discriminating_design, enumerate_configs,
                     identifiability, identifying_design,
                     underdetermined_report)
from .theory import (ChargedMolecule, EtherWave, Theory, discrepancy,
                     mdl_score)
from .world import CathodeWorld, Config, EM_HYDROGEN_ION


class Journal:
    def __init__(self, echo=True):
        self.lines = []
        self.echo = echo

    def say(self, tag, text):
        self.lines.append((tag, text))
        if self.echo:
            width = 78
            head = f"  [{tag}] "
            pad = " " * len(head)
            words, line = text.split(), ""
            first = True
            for w in words:
                if len(line) + len(w) + 1 > width:
                    print((head if first else pad) + line)
                    first, line = False, w
                else:
                    line = (line + " " + w).strip()
            if line:
                print((head if first else pad) + line)

    def rule(self, title):
        if self.echo:
            print("\n" + "=" * 86)
            print("  " + title)
            print("=" * 86)
        self.lines.append(("RULE", title))


class CathodeAgent:
    def __init__(self, world: CathodeWorld, echo=True, allow_auxiliaries=True):
        self.world = world
        #: ablation switch. With this off the agent must take every failed
        #: prediction at face value and may never blame its own apparatus.
        self.allow_auxiliaries = allow_auxiliaries
        self.J = Journal(echo)
        self.theories: list[Theory] = []
        self.record: list[tuple[Config, dict]] = []
        self.configs = enumerate_configs()
        self._screen_explained_at: int | None = None

    # ----------------------------------------------------------- helpers

    def run(self, cfg: Config, why: str = "") -> dict:
        if cfg.detector == "screen" and self._screen_explained_at is None:
            self._screen_explained_at = len(self.J.lines)
            self.J.say("SETUP", "The screen: a beam that survives to the far end of "
                                "the tube leaves a glowing spot where it lands. If "
                                "something bends the beam, the spot moves, and I "
                                "read the two directions apart — plate-shift is how "
                                "far it moves toward whichever plate is charged, "
                                "magnet-shift is how far it moves the way the coils "
                                "pull. Every reading from here on reports both "
                                "separately, whether or not either one is doing "
                                "anything yet.")
        obs = self.world.run(cfg)
        self.record.append((cfg, obs))
        self.J.say("BUILD", f"{cfg.label()}" + (f"   ({why})" if why else ""))
        self.J.say("READS", gloss.format_readings(obs))
        return obs

    def live(self):
        return [t for t in self.theories if not t.dead]

    def leader(self):
        live = self.live()
        return min(live, key=lambda t: mdl_score(t, self.record)) if live else None

    # ------------------------------------------------------ 1. tinkering

    def explore(self):
        self.J.rule("PHASE 1 — tinkering: no theories yet, so nothing to test")
        self.J.say("META", "I have no hypotheses, so no experiment can discriminate "
                           "between them and the expected information gain from any "
                           "designed test is exactly zero. The right move is not to "
                           "design; it is to poke at the thing cheaply and see what "
                           "it does.")
        cheap = Config(detector="screen", vacuum=0.30, accel_volts=200.0)
        self.run(cheap, "cheapest build that shows anything")
        self.run(Config(detector="paddle", vacuum=0.30), "does it push?")
        self.run(Config(detector="thermopile", vacuum=0.30), "does it carry energy?")

        self.J.say("NOTICE", "Something crosses the tube from the cathode: it lights "
                             "the far wall, it warms a pile, and it turns a paddle. "
                             "Whatever it is, it travels and it delivers something "
                             "when it arrives.")
        return ab.Anomaly(kind="unexplained-transport", observable="momentum and heat",
                          detail="effect delivered at a distance from the cathode",
                          context={})

    # ------------------------------------------------- 2. abduce + design

    def form_theories(self, anomaly):
        self.J.rule("PHASE 2 — abduction: what could be doing the carrying?")
        for prop in ab.abduce(anomaly):
            self.J.say("SCHEMA", f"'{prop.schema}' fires.")
            self.J.say("ABDUCE", prop.reasoning)
            if prop.new_theories:
                self.theories.extend(prop.new_theories)
        self.J.say("POOL", "Live theories: " + ", ".join(t.name for t in self.live()))

    def discriminate(self):
        self.J.rule("PHASE 3 — design an experiment that tells them apart")
        designs = discriminating_design(self.live(), self.configs, top=1)
        if not designs:
            self.J.say("META", "Nothing on the bench separates them. Back to tinkering.")
            return
        d = designs[0]
        self.J.say("DESIGN", f"Searched {len(self.configs)} builds I could assemble. "
                             f"Best: {d.rationale}. Note this needed no numbers — "
                             f"only which effects each theory says are present or "
                             f"absent.")
        obs = self.run(d.config, "designed to split the live theories")

        # The two ways a prediction can fail are NOT symmetric, and treating
        # them as though they were is how a system reproduces Hertz's error.
        # Seeing an effect that a theory forbids is decisive: no apparatus
        # fault manufactures an effect out of nothing. Failing to see an effect
        # a theory requires is weak: any number of apparatus faults suppress a
        # real effect. So only the first kind kills.
        anomalies = []
        for t in self.live():
            q = t.qualitative(d.config)
            forbidden = [k for k, sign in q.items()
                         if k in obs and sign == "0" and obs[k] != 0.0]
            missing = [k for k, sign in q.items()
                       if k in obs and sign == "+" and obs[k] == 0.0]
            if forbidden:
                t.dead = True
                t.death_reason = (f"forbade {gloss.label_list(forbidden)}, which "
                                  f"the apparatus plainly shows")
                self.J.say("REFUTE", f"{t.name} is out: it {t.death_reason}. An "
                                     f"effect appearing where a theory says none "
                                     f"can exist is decisive — no fault in my "
                                     f"apparatus invents an effect from nothing.")
            elif missing:
                for k in missing:
                    anomalies.append(ab.Anomaly(
                        kind="failed-prediction", observable=k,
                        detail="predicted-present-observed-absent",
                        context={"config": d.config, "theory": t}))
                self.J.say("FLAG", f"{t.name} required {gloss.label_list(missing)} "
                                   f"and I see nothing. I am NOT counting that as a "
                                   f"refutation yet: an absent effect is exactly "
                                   f"what a faulty apparatus also produces. Held "
                                   f"as an open anomaly.")
        self.J.say("POOL", "Still standing: " + ", ".join(t.name for t in self.live()))
        return anomalies

    # ------------------------------------------------------ 3. the Duhem test

    def duhem_episode(self, anomalies=None):
        self.J.rule("PHASE 4 — a prediction fails, and the theory may not be at fault")
        lead = self.leader()
        cfg = Config(detector="screen", vacuum=0.30, accel_volts=200.0,
                     plate_volts=140.0)
        self.J.say("DESIGN", f"{lead.name} says a charged stream must bend toward a "
                             f"charged plate, and the anomaly I set aside says it "
                             f"does not. Worth a clean, direct test before anything "
                             f"else.")
        obs = self.run(cfg, "electrostatic deflection, straight at the question")

        if obs.get("spot_y", 0.0) == 0.0:
            self.J.say("ANOMALY", "No deflection at all. Taken at face value this "
                                  "refutes the leading theory outright — the beam "
                                  "would have to be uncharged.")
            if not self.allow_auxiliaries:
                self.J.say("ABLATION", "Auxiliary hypotheses are disabled for this "
                                       "run. A failed prediction can only count "
                                       "against the theory.")
                for t in self.live():
                    if t.qualitative(cfg).get("spot_y") == "+":
                        t.dead = True
                        t.death_reason = ("required electrostatic deflection; none "
                                          "was observed")
                        self.J.say("REFUTE", f"{t.name} is out: {t.death_reason}.")
                self.J.say("CONCLUDE", "Nothing that carries charge survives. The "
                                       "rays must be uncharged — some disturbance in "
                                       "the ether after all. I record that as the "
                                       "finding and stop.")
                return
            self.J.say("PAUSE", "But this theory is not free-floating: it is the "
                                "reason I already understand the magnet bending the "
                                "beam and the cup collecting charge. Discarding it "
                                "costs all of that. Before paying it, is there any "
                                "way the prediction could fail while the theory "
                                "stands?")
            anomaly = ab.Anomaly(kind="failed-prediction",
                                 observable=gloss.label("spot_y"),
                                 detail="predicted-present-observed-absent",
                                 context={"config": cfg})
            for prop in ab.abduce(anomaly):
                self.J.say("SCHEMA", f"'{prop.schema}' fires.")
                self.J.say("ABDUCE", prop.reasoning)
                if prop.auxiliary:
                    aux = prop.auxiliary
                    # the screening claim is about the TUBE, not about any one
                    # theory, so it attaches to every live theory that made the
                    # same failed prediction. An auxiliary that could be applied
                    # to just the theory you happen to favour would be a way of
                    # rigging the comparison.
                    for t in self.live():
                        if t.qualitative(cfg).get("spot_y") == "+":
                            t.auxiliaries.append(aux)
                    self.J.say("LEDGER", "This is a claim about the tube, not about "
                                         "any one theory, so it applies to every "
                                         "theory that predicted the deflection — I "
                                         "do not get to hand the excuse only to my "
                                         "favourite.")
                    self.J.say("LEDGER",
                               f"Auxiliary '{aux.name}' admitted ON PROBATION at a "
                               f"cost of {aux.cost_bits:.0f} bits. It is only honest "
                               f"while it carries a debt: {aux.independent_test}. "
                               f"If that test fails, the auxiliary is refuted and I "
                               f"pay the full price for the theory as well.")
                    self.pay_the_debt(lead, aux)

    def pay_the_debt(self, lead, aux):
        self.J.say("DESIGN", "The auxiliary makes a prediction the original theory "
                             "never did, so it can be checked on its own. Sweep the "
                             "pump and watch the deflection.")
        seen = []
        for q in (0.10, 0.30, 0.55, 0.80, 0.95):
            cfg = Config(detector="screen", vacuum=q, accel_volts=200.0,
                         plate_volts=140.0)
            obs = self.run(cfg, f"vacuum {q:.2f}")
            seen.append((q, obs.get("spot_y", 0.0)))
        rising = all(b >= a - 1e-9 for (_, a), (_, b) in zip(seen, seen[1:]))
        appeared = seen[-1][1] > 0 and seen[0][1] == 0.0
        if rising and appeared:
            aux.status = "amortised"
            self.J.say("SUPPORT", "The deflection appears and grows as the tube is "
                                  "emptied, exactly as the auxiliary required. It has "
                                  "paid for itself: it bought a prediction of its own "
                                  "and the prediction held.")
            self.J.say("VERDICT", "So the earlier null result was a fact about my "
                                  "apparatus, not about the beam. The theory stands, "
                                  "and I now know the tube must be pumped hard before "
                                  "any electrostatic measurement means anything.")
        else:
            aux.status = "refuted"
            lead.dead = True
            self.J.say("REFUTE", "The auxiliary's own prediction failed. It was an "
                                 "excuse, not an explanation, and the theory falls "
                                 "with it.")

    # -------------------------------------------- 4. identifiability

    def identify(self):
        self.J.rule("PHASE 5 — design an apparatus that can measure the unknowns")
        lead = self.leader()
        self.J.say("PROBLEM", f"{lead.name} has two unknowns I cannot separate: the "
                              f"charge-to-mass ratio and the beam speed. Every "
                              f"deflection I can produce depends on both.")
        for line in underdetermined_report(lead, self.configs, n=3):
            self.J.say("RANK", line)
        self.J.say("INSIGHT", "So no single-deflection apparatus can ever do this, "
                              "however carefully built. I need a build whose readings "
                              "respond to the two unknowns in genuinely different "
                              "proportions.")

        designs = identifying_design(lead, self.configs, top=3)
        if not designs:
            self.J.say("IMPASSE", "Nothing I can assemble determines both. I would "
                                  "need a part I do not have.")
            return None
        d0 = designs[0]
        self.J.say("DESIGN", f"Found one: {d0.config.label()} — {d0.rationale}. Both "
                             f"fields acting at once, on the same beam, in the same "
                             f"shot.")
        self.J.say("DESIGN", "One shot proves nothing about whether my own method "
                             "is trustworthy — I could have hit a noisy reading. "
                             "I'll take this measurement from several genuinely "
                             "different builds and solve independently each time. "
                             "If they don't agree with EACH OTHER, I have no "
                             "business trusting any single one of them.")

        shots = []
        for i, d in enumerate(designs):
            obs = self.run(d.config, f"crossed-field build {i+1}/{len(designs)}")
            shots.append((d.config, obs))

        rep = overidentification_check(lead, shots)
        self.J.say("SOLVE", "  |  ".join(f"e/m = {v:.4g}" for v in rep.em_values))
        if rep.consistent:
            self.J.say("CONSISTENT", f"Spread across independent solves: "
                                     f"{rep.em_spread*100:.1f}%. They agree with "
                                     f"each other — not because I know the right "
                                     f"answer, but because the method keeps giving "
                                     f"the same one regardless of which build I use "
                                     f"to ask. That is what I actually get to trust.")
        else:
            self.J.say("IMPASSE", f"Spread across independent solves: "
                                  f"{rep.em_spread*100:.1f}%. That is too large to "
                                  f"trust — something is wrong with the method "
                                  f"itself, not just with one noisy shot.")
            return None

        em = float(np.mean(rep.em_values))
        lead.params["e_over_m"] = em
        lead.params["speed_coeff"] = float(np.mean(rep.speed_values))
        self.J.say("RESULT", f"Charge-to-mass ratio: {em:.4g} C/kg, taken as the "
                             f"average of {len(shots)} independent, mutually "
                             f"consistent solves.")
        return em

    def check_coherence(self):
        self.J.rule("PHASE 5.5 — does this theory explain anything it wasn't built for?")
        lead = self.leader()
        self.J.say("DESIGN", "Every measurement so far went into pinning down the "
                             "two unknowns. Before trusting the result, I want to "
                             "know if the theory, now that it's fully specified, "
                             "says anything correct about apparatus that had "
                             "nothing to do with finding it.")
        for detector, note in (("paddle", "how hard the beam pushes"),
                               ("thermopile", "how much heat it deposits")):
            rep = retrodiction_check(lead, self.world, detector)
            if rep is None:
                continue
            self.J.say("CHECK", f"If these are accelerated charges, {note} should "
                                f"scale as (accelerating volts)^{rep.predicted_exponent:g} "
                                f"— a claim about the shape of the theory, not about "
                                f"the numbers I just solved for.")
            self.run(Config(detector=detector, accel_volts=120.0), "at 120V")
            self.run(Config(detector=detector, accel_volts=400.0), "at 400V")
            if rep.agrees:
                self.J.say("SUPPORT", f"Measured exponent: {rep.measured_exponent:.2f} "
                                      f"against a predicted {rep.predicted_exponent:g}. "
                                      f"Nothing about this measurement was used to "
                                      f"find e/m or the speed — the theory is "
                                      f"explaining something it was never fit to.")
            else:
                self.J.say("ANOMALY", f"Measured exponent {rep.measured_exponent:.2f} "
                                      f"does not match the predicted "
                                      f"{rep.predicted_exponent:g}. The theory that "
                                      f"fit the deflections does not fit this — "
                                      f"worth treating as unresolved, not swept aside.")

    def solve(self, lead, cfg, obs):
        """Two readings, two unknowns."""
        from .world import D_PLATE, K_COIL, L_DRIFT, L_PLATE
        lever = L_PLATE * (L_PLATE / 2 + L_DRIFT)
        y, z = obs["spot_y"], obs["spot_z"]
        E = cfg.plate_volts / D_PLATE * lead.aux_factor(cfg)
        B = K_COIL * cfg.coil_amps
        # y = em*E*lever/v^2 ; z = em*B*lever/v  ->  em = z^2 E / (y B^2 lever)
        em = (z ** 2) * E / (y * B ** 2 * lever)
        v = em * B * lever / z
        lead.params["e_over_m"] = em
        lead.params["speed_coeff"] = v / math.sqrt(cfg.accel_volts)
        self.J.say("SOLVE", f"Two readings, two unknowns, one shot: speed comes out "
                            f"{v:.3g} m/s and the charge-to-mass ratio {em:.4g} C/kg.")
        return em

    # ------------------------------------------------ 5. the unification

    def unify(self, em_first):
        self.J.rule("PHASE 6 — is this a property of the cathode, or of everything?")
        lead = self.leader()
        self.J.say("DESIGN", "If these bodies are torn off the electrode, the number "
                             "should change when I change the electrode. Cheapest "
                             "possible test of the most important question.")
        results = []
        from .world import D_PLATE, K_COIL, L_DRIFT, L_PLATE
        for cathode in ("aluminium", "iron", "platinum"):
            for gas in ("air", "hydrogen"):
                cfg = Config(detector="screen", vacuum=0.95, accel_volts=400.0,
                             plate_volts=140.0, coil_amps=0.80,
                             cathode=cathode, gas=gas)
                obs = self.run(cfg, f"{cathode} cathode in {gas}")
                em = self.solve_quiet(lead, cfg, obs)
                results.append((cathode, gas, em))

        vals = np.array([r[2] for r in results])
        spread = float(vals.std() / vals.mean())
        self.J.say("RESULT", "  |  ".join(f"{c}/{g}: {e:.3g}" for c, g, e in results))
        self.J.say("NOTICE", f"They agree to within {spread*100:.1f}%, which is my "
                             f"measurement scatter. Changing the electrode metal "
                             f"changes nothing. Changing the gas changes nothing.")

        anomaly = ab.Anomaly(
            kind="invariance", observable="e_over_m",
            detail=f"The ratio comes out the same ({vals.mean():.3g}) for every "
                   f"cathode metal and every residual gas I have tried.",
            context={})
        for prop in ab.abduce(anomaly):
            self.J.say("SCHEMA", f"'{prop.schema}' fires.")
            self.J.say("ABDUCE", prop.reasoning)

        ratio = vals.mean() / EM_HYDROGEN_ION
        self.J.say("COMPARE", f"Against the one charge-to-mass ratio I already knew "
                              f"— the hydrogen ion from electrolysis — this is "
                              f"{ratio:.0f} times larger.")
        for t in self.theories:
            if isinstance(t, ChargedMolecule) and not t.dead:
                lo, hi = t.plausible_range()
                if not (lo <= vals.mean() <= hi):
                    with_discount = t.description_bits()
                    t.precedent = None
                    without_discount = t.description_bits()
                    self.J.say("LEDGER", f"Its electrolysis precedent bought it a "
                                         f"real discount — {with_discount:.0f} bits "
                                         f"instead of {without_discount:.0f}. That "
                                         f"discount was honestly earned and I am not "
                                         f"taking it away for convenience. It simply "
                                         f"is not enough: the mismatch in magnitude "
                                         f"costs far more than any prior ever saved.")
                    t.dead = True
                    t.death_reason = (f"committed to a ratio near an ion's; measured "
                                      f"value is {ratio:.0f}x too large")
                    self.J.say("REFUTE", f"charged-molecule is out: "
                                         f"{t.death_reason}.")
        self.J.say("CONCLUDE", f"Either the charge is far bigger than an ion's or the "
                               f"mass is far smaller. Whichever it is, this is not a "
                               f"gas molecule and not a fragment of the electrode: it "
                               f"is the same thing whatever the tube is made of.")
        return vals.mean()

    def solve_quiet(self, lead, cfg, obs):
        from .world import D_PLATE, K_COIL, L_DRIFT, L_PLATE
        lever = L_PLATE * (L_PLATE / 2 + L_DRIFT)
        y, z = obs["spot_y"], obs["spot_z"]
        E = cfg.plate_volts / D_PLATE * lead.aux_factor(cfg)
        B = K_COIL * cfg.coil_amps
        return (z ** 2) * E / (y * B ** 2 * lever)
