#!/usr/bin/env python3
"""Run the cathode-ray investigation end to end."""
import sys
from cathode.agent import CathodeAgent
from cathode.world import CathodeWorld, EM_TRUE, EM_HYDROGEN_ION

def main():
    ablate = "--ablate-duhem" in sys.argv
    world = CathodeWorld(seed=4)
    ag = CathodeAgent(world, echo="--quiet" not in sys.argv,
                      allow_auxiliaries=not ablate)
    anomaly = ag.explore()
    ag.form_theories(anomaly)
    anomalies = ag.discriminate()
    ag.duhem_episode(anomalies)
    if not [t for t in ag.theories if not t.dead]:
        ag.J.rule("SCORE — the run ended early")
        print("  Every theory that carried charge has been refuted.")
        print(f"  true value in the simulator   : {EM_TRUE:.4g} C/kg")
        print("  the agent measured            : nothing — it stopped at the null result")
        print("\n  This is the 1883 outcome. Hertz concluded cathode rays were")
        print("  uncharged from exactly this experiment. The result is wrong, and")
        print("  nothing about the reasoning above it is faulty: the deduction from")
        print("  the null result is valid. What is missing is the willingness to")
        print("  suspect the apparatus, which is the capability being ablated.")
        return
    em = ag.identify()
    if em:
        ag.check_coherence()
        final = ag.unify(em)
        ag.J.rule("SCORE — against ground truth the agent never saw")
        err = abs(final - EM_TRUE) / EM_TRUE
        print(f"  measured charge-to-mass ratio : {final:.4g} C/kg")
        print(f"  true value in the simulator   : {EM_TRUE:.4g} C/kg")
        print(f"  error                         : {err*100:.2f}%")
        print(f"  ratio to hydrogen ion         : {final/EM_HYDROGEN_ION:.0f}x")
        print(f"  apparatus builds fired        : {world.shots}")
        print(f"  bench time spent              : {world.bench_time:.1f}")
        live = [t for t in ag.theories if not t.dead]
        print(f"  surviving theory              : {live[0] if live else 'none'}")
        for t in ag.theories:
            if t.dead:
                print(f"    refuted: {t.name} — {t.death_reason}")

if __name__ == "__main__":
    main()
