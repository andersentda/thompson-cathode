# Cathode-ray testbed — investigation transcript

Every reading is now labelled by what it physically is — "plate-shift" and
"magnet-shift" rather than `spot_y` and `spot_z` — with a one-time SETUP note
explaining the apparatus the first time the screen is used. No internal
variable name appears anywhere in the transcript below; verified by sweeping
the full output for every raw key the code uses internally.

Ground truth the agent never sees: charge-to-mass ratio 1.76e11 C/kg.

---

## Full run

```
======================================================================================
  PHASE 1 — tinkering: no theories yet, so nothing to test
======================================================================================
  [META] I have no hypotheses, so no experiment can discriminate between them and the
         expected information gain from any designed test is exactly zero. The right
         move is not to design; it is to poke at the thing cheaply and see what it
         does.
  [SETUP] The screen: a beam that survives to the far end of the tube leaves a glowing
          spot where it lands. If something bends the beam, the spot moves, and I read
          the two directions apart — plate-shift is how far it moves toward whichever
          plate is charged, magnet-shift is how far it moves the way the coils pull.
          Every reading from here on reports both separately, whether or not either one
          is doing anything yet.
  [BUILD] screen vac=0.30 V=200 (cheapest build that shows anything)
  [READS] plate-shift: 0, magnet-shift: 0, screen lit: yes, focus: 0.42
  [BUILD] paddle vac=0.30 V=200 (does it push?)
  [READS] push on the paddle wheel: 0.8883
  [BUILD] thermopile vac=0.30 V=200 (does it carry energy?)
  [READS] heat in the thermopile: 1.295
  [NOTICE] Something crosses the tube from the cathode: it lights the far wall, it warms
           a pile, and it turns a paddle. Whatever it is, it travels and it delivers
           something when it arrives.

======================================================================================
  PHASE 2 — abduction: what could be doing the carrying?
======================================================================================
  [SCHEMA] 'carried-substance' fires.
  [ABDUCE] Something crosses the tube and delivers momentum and heat at the far end.
           Either the disturbance itself travels with no substance to it, or a stream of
           bodies is being carried across. Those differ in what a magnet or a charged
           plate should do to them, so both are worth keeping until an experiment
           separates them. Worth noting before either is tested: electrolysis already
           showed charge moves in exactly this carried-by-matter way, at a specific known
           ratio — if that is what is happening here too, it is not a new kind of
           physics, just a familiar one in an unfamiliar tube.
  [POOL] Live theories: ether-wave, charged-corpuscle, charged-molecule

======================================================================================
  PHASE 3 — design an experiment that tells them apart
======================================================================================
  [DESIGN] Searched 4860 builds I could assemble. Best: plate-shift, magnet-shift would
           differ between ether-wave vs charged-corpuscle vs charged-molecule. Note this
           needed no numbers — only which effects each theory says are present or absent.
  [BUILD] screen vac=0.10 V=120 plates=60V coils=0.35A (designed to split the live
          theories)
  [READS] plate-shift: 0, magnet-shift: 0.1543, screen lit: yes, focus: 0.14
  [REFUTE] ether-wave is out: it forbade magnet-shift, which the apparatus plainly shows.
           An effect appearing where a theory says none can exist is decisive — no fault
           in my apparatus invents an effect from nothing.
  [FLAG] charged-corpuscle required plate-shift and I see nothing. I am NOT counting
         that as a refutation yet: an absent effect is exactly what a faulty apparatus
         also produces. Held as an open anomaly.
  [FLAG] charged-molecule required plate-shift and I see nothing. I am NOT counting
         that as a refutation yet: an absent effect is exactly what a faulty apparatus
         also produces. Held as an open anomaly.
  [POOL] Still standing: charged-corpuscle, charged-molecule

======================================================================================
  PHASE 4 — a prediction fails, and the theory may not be at fault
======================================================================================
  [DESIGN] charged-molecule says a charged stream must bend toward a charged plate, and
           the anomaly I set aside says it does not. Worth a clean, direct test before
           anything else.
  [BUILD] screen vac=0.30 V=200 plates=140V (electrostatic deflection, straight at the
          question)
  [READS] plate-shift: 0, magnet-shift: 0, screen lit: yes, focus: 0.42
  [ANOMALY] No deflection at all. Taken at face value this refutes the leading theory
            outright — the beam would have to be uncharged.
  [PAUSE] But this theory is not free-floating: it is the reason I already understand
          the magnet bending the beam and the cup collecting charge. Discarding it costs
          all of that. Before paying it, is there any way the prediction could fail
          while the theory stands?
  [SCHEMA] 'intervening-medium' fires.
  [ABDUCE] The theory says plate-shift should be there and it is not. Before giving the
           theory up: the tube is not empty. If what remains in it conducts, it would
           gather at the plates and cancel the field inside, and the beam would feel
           nothing. That is testable rather than convenient — it says the deflection must
           COME BACK as the pump improves. If it doesn't, this excuse dies and takes the
           theory with it.
  [LEDGER] This is a claim about the tube, not about any one theory, so it applies to
           every theory that predicted the deflection — I do not get to hand the excuse
           only to my favourite.
  [LEDGER] Auxiliary 'residual-gas-screening' admitted ON PROBATION at a cost of 6 bits.
           It is only honest while it carries a debt: deflection must grow as the vacuum
           improves. If that test fails, the auxiliary is refuted and I pay the full
           price for the theory as well.
  [DESIGN] The auxiliary makes a prediction the original theory never did, so it can be
           checked on its own. Sweep the pump and watch the deflection.
  [BUILD] screen vac=0.10 V=200 plates=140V (vacuum 0.10)
  [READS] plate-shift: 0, magnet-shift: 0, screen lit: yes, focus: 0.14
  [BUILD] screen vac=0.30 V=200 plates=140V (vacuum 0.30)
  [READS] plate-shift: 0, magnet-shift: 0, screen lit: yes, focus: 0.42
  [BUILD] screen vac=0.55 V=200 plates=140V (vacuum 0.55)
  [READS] plate-shift: 0.00257, magnet-shift: 0, screen lit: yes, focus: 0.77
  [BUILD] screen vac=0.80 V=200 plates=140V (vacuum 0.80)
  [READS] plate-shift: 0.0508, magnet-shift: 0, screen lit: yes, focus: 1
  [BUILD] screen vac=0.95 V=200 plates=140V (vacuum 0.95)
  [READS] plate-shift: 0.2584, magnet-shift: 0, screen lit: yes, focus: 1
  [SUPPORT] The deflection appears and grows as the tube is emptied, exactly as the
            auxiliary required. It has paid for itself: it bought a prediction of its own
            and the prediction held.
  [VERDICT] So the earlier null result was a fact about my apparatus, not about the beam.
            The theory stands, and I now know the tube must be pumped hard before any
            electrostatic measurement means anything.

======================================================================================
  PHASE 5 — design an apparatus that can measure the unknowns
======================================================================================
  [PROBLEM] charged-corpuscle has two unknowns I cannot separate: the charge-to-mass ratio
            and the beam speed. Every deflection I can produce depends on both.
  [RANK] magnet-shift alone -> rank 1 of 2: fixes only a combination of the
         charge-to-mass ratio and the beam's speed (per root-volt), never each
         separately
  [RANK] plate-shift alone -> rank 1 of 2: fixes only a combination of the
         charge-to-mass ratio and the beam's speed (per root-volt), never each
         separately
  [INSIGHT] So no single-deflection apparatus can ever do this, however carefully built. I
            need a build whose readings respond to the two unknowns in genuinely different
            proportions.
  [DESIGN] Found one: screen vac=0.80 V=120 plates=60V coils=0.35A — measures
           plate-shift, magnet-shift: rank 2 of 2 unknowns, so both are separable. Both
           fields acting at once, on the same beam, in the same shot.
  [DESIGN] One shot proves nothing about whether my own method is trustworthy — I could
           have hit a noisy reading. I'll take this measurement from several genuinely
           different builds and solve independently each time. If they don't agree with
           EACH OTHER, I have no business trusting any single one of them.
  [BUILD] screen vac=0.80 V=120 plates=60V coils=0.35A (crossed-field build 1/3)
  [READS] plate-shift: 0.03704, magnet-shift: 0.1497, screen lit: yes, focus: 1
  [BUILD] screen vac=0.80 V=120 plates=60V coils=0.35A hydrogen (crossed-field build
          2/3)
  [READS] plate-shift: 0.03631, magnet-shift: 0.15, screen lit: yes, focus: 1
  [BUILD] screen vac=0.80 V=120 plates=60V coils=0.35A carbon dioxide (crossed-field
          build 3/3)
  [READS] plate-shift: 0.03768, magnet-shift: 0.1541, screen lit: yes, focus: 1
  [SOLVE] e/m = 1.793e+11 | e/m = 1.835e+11 | e/m = 1.866e+11
  [CONSISTENT] Spread across independent solves: 1.6%. They agree with each other — not
               because I know the right answer, but because the method keeps giving the same
               one regardless of which build I use to ask. That is what I actually get to
               trust.
  [RESULT] Charge-to-mass ratio: 1.831e+11 C/kg, taken as the average of 3 independent,
           mutually consistent solves.

======================================================================================
  PHASE 5.5 — does this theory explain anything it wasn't built for?
======================================================================================
  [DESIGN] Every measurement so far went into pinning down the two unknowns. Before
           trusting the result, I want to know if the theory, now that it's fully
           specified, says anything correct about apparatus that had nothing to do with
           finding it.
  [CHECK] If these are accelerated charges, how hard the beam pushes should scale as
          (accelerating volts)^0.5 — a claim about the shape of the theory, not about
          the numbers I just solved for.
  [BUILD] paddle vac=0.30 V=120 (at 120V)
  [READS] push on the paddle wheel: 0.6926
  [BUILD] paddle vac=0.30 V=400 (at 400V)
  [READS] push on the paddle wheel: 1.251
  [SUPPORT] Measured exponent: 0.51 against a predicted 0.5. Nothing about this
            measurement was used to find e/m or the speed — the theory is explaining
            something it was never fit to.
  [CHECK] If these are accelerated charges, how much heat it deposits should scale as
          (accelerating volts)^1 — a claim about the shape of the theory, not about the
          numbers I just solved for.
  [BUILD] thermopile vac=0.30 V=120 (at 120V)
  [READS] heat in the thermopile: 0.78
  [BUILD] thermopile vac=0.30 V=400 (at 400V)
  [READS] heat in the thermopile: 2.554
  [SUPPORT] Measured exponent: 1.00 against a predicted 1. Nothing about this measurement
            was used to find e/m or the speed — the theory is explaining something it was
            never fit to.

======================================================================================
  PHASE 6 — is this a property of the cathode, or of everything?
======================================================================================
  [DESIGN] If these bodies are torn off the electrode, the number should change when I
           change the electrode. Cheapest possible test of the most important question.
  [BUILD] screen vac=0.95 V=400 plates=140V coils=0.80A (aluminium cathode in air)
  [READS] plate-shift: 0.1313, magnet-shift: 0.1791, screen lit: yes, focus: 1
  [BUILD] screen vac=0.95 V=400 plates=140V coils=0.80A hydrogen (aluminium cathode in
          hydrogen)
  [READS] plate-shift: 0.1283, magnet-shift: 0.1877, screen lit: yes, focus: 1
  [BUILD] screen vac=0.95 V=400 plates=140V coils=0.80A iron (iron cathode in air)
  [READS] plate-shift: 0.1255, magnet-shift: 0.1906, screen lit: yes, focus: 1
  [BUILD] screen vac=0.95 V=400 plates=140V coils=0.80A iron hydrogen (iron cathode in
          hydrogen)
  [READS] plate-shift: 0.1297, magnet-shift: 0.1907, screen lit: yes, focus: 1
  [BUILD] screen vac=0.95 V=400 plates=140V coils=0.80A platinum (platinum cathode in
          air)
  [READS] plate-shift: 0.1317, magnet-shift: 0.1833, screen lit: yes, focus: 1
  [BUILD] screen vac=0.95 V=400 plates=140V coils=0.80A platinum hydrogen (platinum
          cathode in hydrogen)
  [READS] plate-shift: 0.1272, magnet-shift: 0.1861, screen lit: yes, focus: 1
  [RESULT] aluminium/air: 1.59e+11 | aluminium/hydrogen: 1.79e+11 | iron/air: 1.89e+11 |
           iron/hydrogen: 1.83e+11 | platinum/air: 1.66e+11 | platinum/hydrogen: 1.77e+11
  [NOTICE] They agree to within 5.7%, which is my measurement scatter. Changing the
           electrode metal changes nothing. Changing the gas changes nothing.
  [SCHEMA] 'universal-constituent' fires.
  [ABDUCE] The ratio comes out the same (1.75e+11) for every cathode metal and every
           residual gas I have tried. The cathode metal makes no difference and neither
           does the residual gas. If this were matter torn from the electrode, the number
           would follow the electrode. It does not, so whatever is being measured is not
           a property of any of these substances — it is something they all contain.
  [COMPARE] Against the one charge-to-mass ratio I already knew — the hydrogen ion from
            electrolysis — this is 1831 times larger.
  [LEDGER] Its electrolysis precedent bought it a real discount — 25 bits instead of 30.
           That discount was honestly earned and I am not taking it away for convenience.
           It simply is not enough: the mismatch in magnitude costs far more than any
           prior ever saved.
  [REFUTE] charged-molecule is out: committed to a ratio near an ion's; measured value is
           1831x too large.
  [CONCLUDE] Either the charge is far bigger than an ion's or the mass is far smaller.
             Whichever it is, this is not a gas molecule and not a fragment of the
             electrode: it is the same thing whatever the tube is made of.

======================================================================================
  SCORE — against ground truth the agent never saw
======================================================================================
  measured charge-to-mass ratio : 1.754e+11 C/kg
  true value in the simulator   : 1.76e+11 C/kg
  error                         : 0.33%
  ratio to hydrogen ion         : 1831x
  apparatus builds fired        : 35
  bench time spent              : 110.5
  surviving theory              : <charged-corpuscle +residual-gas-screening>
    refuted: ether-wave — forbade magnet-shift, which the apparatus plainly shows
    refuted: charged-molecule — committed to a ratio near an ion's; measured value is 1831x too large
```

---

## Control: the same agent with auxiliary hypotheses disabled

```
======================================================================================
  PHASE 1 — tinkering: no theories yet, so nothing to test
======================================================================================
  [META] I have no hypotheses, so no experiment can discriminate between them and the
         expected information gain from any designed test is exactly zero. The right
         move is not to design; it is to poke at the thing cheaply and see what it
         does.
  [SETUP] The screen: a beam that survives to the far end of the tube leaves a glowing
          spot where it lands. If something bends the beam, the spot moves, and I read
          the two directions apart — plate-shift is how far it moves toward whichever
          plate is charged, magnet-shift is how far it moves the way the coils pull.
          Every reading from here on reports both separately, whether or not either one
          is doing anything yet.
  [BUILD] screen vac=0.30 V=200 (cheapest build that shows anything)
  [READS] plate-shift: 0, magnet-shift: 0, screen lit: yes, focus: 0.42
  [BUILD] paddle vac=0.30 V=200 (does it push?)
  [READS] push on the paddle wheel: 0.8883
  [BUILD] thermopile vac=0.30 V=200 (does it carry energy?)
  [READS] heat in the thermopile: 1.295
  [NOTICE] Something crosses the tube from the cathode: it lights the far wall, it warms
           a pile, and it turns a paddle. Whatever it is, it travels and it delivers
           something when it arrives.

======================================================================================
  PHASE 2 — abduction: what could be doing the carrying?
======================================================================================
  [SCHEMA] 'carried-substance' fires.
  [ABDUCE] Something crosses the tube and delivers momentum and heat at the far end.
           Either the disturbance itself travels with no substance to it, or a stream of
           bodies is being carried across. Those differ in what a magnet or a charged
           plate should do to them, so both are worth keeping until an experiment
           separates them. Worth noting before either is tested: electrolysis already
           showed charge moves in exactly this carried-by-matter way, at a specific known
           ratio — if that is what is happening here too, it is not a new kind of
           physics, just a familiar one in an unfamiliar tube.
  [POOL] Live theories: ether-wave, charged-corpuscle, charged-molecule

======================================================================================
  PHASE 3 — design an experiment that tells them apart
======================================================================================
  [DESIGN] Searched 4860 builds I could assemble. Best: plate-shift, magnet-shift would
           differ between ether-wave vs charged-corpuscle vs charged-molecule. Note this
           needed no numbers — only which effects each theory says are present or absent.
  [BUILD] screen vac=0.10 V=120 plates=60V coils=0.35A (designed to split the live
          theories)
  [READS] plate-shift: 0, magnet-shift: 0.1543, screen lit: yes, focus: 0.14
  [REFUTE] ether-wave is out: it forbade magnet-shift, which the apparatus plainly shows.
           An effect appearing where a theory says none can exist is decisive — no fault
           in my apparatus invents an effect from nothing.
  [FLAG] charged-corpuscle required plate-shift and I see nothing. I am NOT counting
         that as a refutation yet: an absent effect is exactly what a faulty apparatus
         also produces. Held as an open anomaly.
  [FLAG] charged-molecule required plate-shift and I see nothing. I am NOT counting
         that as a refutation yet: an absent effect is exactly what a faulty apparatus
         also produces. Held as an open anomaly.
  [POOL] Still standing: charged-corpuscle, charged-molecule

======================================================================================
  PHASE 4 — a prediction fails, and the theory may not be at fault
======================================================================================
  [DESIGN] charged-molecule says a charged stream must bend toward a charged plate, and
           the anomaly I set aside says it does not. Worth a clean, direct test before
           anything else.
  [BUILD] screen vac=0.30 V=200 plates=140V (electrostatic deflection, straight at the
          question)
  [READS] plate-shift: 0, magnet-shift: 0, screen lit: yes, focus: 0.42
  [ANOMALY] No deflection at all. Taken at face value this refutes the leading theory
            outright — the beam would have to be uncharged.
  [ABLATION] Auxiliary hypotheses are disabled for this run. A failed prediction can only
             count against the theory.
  [REFUTE] charged-corpuscle is out: required electrostatic deflection; none was
           observed.
  [REFUTE] charged-molecule is out: required electrostatic deflection; none was observed.
  [CONCLUDE] Nothing that carries charge survives. The rays must be uncharged — some
             disturbance in the ether after all. I record that as the finding and stop.

======================================================================================
  SCORE — the run ended early
======================================================================================
  Every theory that carried charge has been refuted.
  true value in the simulator   : 1.76e+11 C/kg
  the agent measured            : nothing — it stopped at the null result

  This is the 1883 outcome. Hertz concluded cathode rays were
  uncharged from exactly this experiment. The result is wrong, and
  nothing about the reasoning above it is faulty: the deduction from
  the null result is valid. What is missing is the willingness to
  suspect the apparatus, which is the capability being ablated.
```
