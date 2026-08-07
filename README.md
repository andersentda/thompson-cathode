# Cathode-ray testbed

An agent is given a kit of parts — tube, pump, cathode, plates, coils, screen,
collector cup, paddlewheel, thermopile — and a world with a hidden physics. It
is given no instruments, no variables, and no target. It has to work out that
something is being carried across the tube, that the something is charged, how
to measure its charge-to-mass ratio, and that the ratio belongs to no particular
electrode.

```
python run_cathode.py                  # the full investigation
python run_cathode.py --ablate-duhem   # the control (see below)
```

Result: **1.85e11 C/kg against a true 1.76e11 (5.0% error), from 17 apparatus
builds**, with the ether-wave and charged-molecule theories refuted on different
grounds and the surviving theory carrying one amortised auxiliary.

---

## What is actually automated, and what is not

This matters more than the result, so it goes first.

### Genuinely searched or derived

- **Which apparatus to build, for discrimination.** The agent enumerates 4,860
  assemblable configurations and picks by *qualitative* disagreement between
  live theories — signs and presences only, no magnitudes. That is how design
  reasoning actually works: you know a charged beam bends toward a positive
  plate without knowing any number.
- **The crossed-field experiment.** This is not hardcoded anywhere. The
  charged-corpuscle theory has two unknowns (charge-to-mass ratio, beam speed)
  and every single deflection mixes them. The agent computes the Jacobian of
  predicted readings against unknowns for each candidate build and finds every
  single-deflection apparatus has **rank 1 of 2** — underdetermined no matter
  how precisely built. Only a build carrying both an electric and a magnetic
  deflection reaches full rank. The crossed-field tube falls out of that
  determinant, which is the one place in this project where an experiment was
  invented rather than chosen from a list.
- **The asymmetry between the two ways a prediction can fail.** Seeing an effect
  a theory forbids is decisive — no apparatus fault manufactures an effect from
  nothing. *Not* seeing an effect a theory requires is weak, because any number
  of faults suppress a real one. Only the first kind kills a theory. This single
  rule is what stands between the agent and Hertz's error.
- **Auxiliary bookkeeping.** An auxiliary hypothesis is admitted at a stated
  cost in bits and only while it carries an unpaid debt: an independent, testable
  consequence. "Residual gas screens the field" predicts the deflection must
  *return* as the pump improves. The agent designs that sweep, runs it, and the
  auxiliary is either amortised or refuted — taking the theory with it. It also
  attaches to every theory that made the same failed prediction, since it is a
  claim about the tube, not about anyone's favourite.

### Three more mechanisms, all non-empirical theory assessment

These answer a different question than the ones above: not "does this fit the
data" but "was there ever a principled, non-empirical reason to prefer this
theory before, or independent of, the data that eventually confirms it." The
Higgs mechanism is the motivating case — the reasons to take it seriously in
1964 were real and mostly arrived before the boson itself did in 2012.

- **Precedent** (`Precedent` in `theory.py`, attached in `abduce.py`). When the
  `carried-substance` schema fires, it doesn't just propose two competing
  theories blind — it notices that one of them, charge carried by matter in
  discrete units, is not new physics at all: electrolysis already established
  it, at a known ratio, decades earlier. That gets stated as an explicit
  discount on the theory's description length, the same units everything else
  in the MDL ledger is measured in. The discount is a lower bar, never a veto:
  when charged-molecule is refuted, the transcript prints the ledger with and
  without the discount side by side — 25 bits instead of 30 — and the mismatch
  in magnitude costs far more than the discount ever saved. A precedent that
  could block a strong-enough refutation would be unfalsifiable; this one
  can't.
- **Overidentification** (`coherence.py`). The toy-world analogue of 't Hooft
  proving electroweak theory renormalizable in 1971 — years before any Higgs
  data, on pure internal consistency. Here: solve the same two unknowns from
  three independently-built crossed-field apparatus and check they agree with
  *each other*, not with any known answer. They do, to 1.6%. This turned out to
  sharpen the actual measurement as a side effect of checking rigor rather than
  chasing precision — **0.33% error, down from 5.03% on a single shot** — which
  is the right kind of surprise for a consistency check to produce.
- **Retrodiction** (`coherence.py`, `Theory.scaling_signature`). Once the
  charged-corpuscle theory's parameters are pinned down by deflection, its
  *form* — not the fitted numbers — makes a parameter-free prediction: a paddle
  wheel's push should scale as (accelerating volts)^0.5, a thermopile's heat as
  volts^1, because kinetic energy is eV and momentum goes as its square root.
  Neither apparatus was used to find e/m or the speed. Measured: 0.51 and 1.00
  against predictions of 0.5 and 1. This is Higgs solving the Goldstone problem
  he wasn't trying to solve, made checkable — Dawid's "unexpected explanatory
  coherence" as an actual number instead of a philosophical description.

### Still hand-written

- **The schema library.** Three explanatory moves (`carried-substance`,
  `intervening-medium`, `universal-constituent`), written by hand. This is the
  honest limitation: the schemas *are* the "experience" from which new ideas get
  built, and here that experience was supplied rather than learned. The interface
  in `abduce.py` is deliberately the shape a learned proposal distribution would
  have to satisfy — `fires_on(anomaly) -> propose(anomaly)`.
- **The phase ordering.** The runner calls explore → abduce → discriminate →
  Duhem → identify → unify in sequence. A real meta-controller would select each
  step by expected information gain; the mode-switch argument is implemented in
  the reasoning but not yet in the control flow.
- **The theory space.** Three theories, written out. The system chooses among
  and modifies them; it does not invent a fourth.
- **The final inversion.** Solving two equations for two unknowns is an analytic
  step I wrote, not one the agent derived.

So: the *experiment design* and the *epistemology* are real; the *idea
generation* is scaffolded. That is roughly the opposite of where LLM-based "AI
scientist" systems sit, which generate ideas fluently and design experiments
poorly.

---

## The control

`--ablate-duhem` changes exactly one thing: the agent may no longer blame its own
apparatus. The schema library, the design search and the identifiability analysis
are untouched.

It then reproduces Hertz's 1883 result. It builds the electrostatic deflection
experiment, sees nothing, correctly deduces that nothing carrying charge can
survive, concludes the rays are an uncharged disturbance in the ether, and stops.

Every step of that reasoning is valid. The conclusion is wrong. The gap is not
logic and not data — it is the willingness to suspect the instrument, and the
discipline to make that suspicion pay a debt before accepting it. Fourteen years
separated Hertz's answer from Thomson's, and the difference was a better pump
plus the judgement to go looking for one.

That control is the point of the whole testbed. A capability you can ablate and
watch fail is a capability you have actually implemented.

---

## Layout

```
cathode/
  world.py       parts catalogue, apparatus configs, hidden physics (the trap lives here)
  theory.py      theories as programs: qualitative signatures, parameters, auxiliaries, MDL, precedent
  abduce.py      schema library — the proposal step, including precedent attachment
  design.py      discrimination search + identifiability (Jacobian rank) analysis
  coherence.py   overidentification (internal consistency) + retrodiction (unexpected coherence)
  agent.py       the loop, the ledger, the mode-switch argument
run_cathode.py
```

Requires Python 3.10+ and numpy.

## Where to push next, in order of value

1. **Learn the proposal distribution.** Replace the hand-written schemas with a
   proposer trained on a corpus of historical explanations, keeping the same
   interface. This is the single change that would move the system from
   "scaffolded abduction" to abduction.
2. **Make the meta-controller real.** Let expected information gain choose the
   phase, so tinkering is entered because designed experiments have stopped
   paying, not because the script says so.
3. **Let theories be edited, not just selected.** Program synthesis over theory
   space, so a fourth theory can be built from parts of the first three.
4. **Grow the parts catalogue past the point where enumeration works.** 4,860
   configs can be brute-forced; 10^8 cannot, and that is where the design search
   stops being a loop and starts needing to be a search with a heuristic.
