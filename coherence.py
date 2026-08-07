"""Abduction: proposing an explanation, rather than enumerating one.

The mechanics agent searched a grammar exhaustively, so it could only ever
find what was put in the grammar. That is not abduction, it is lookup with
extra steps.

What is here instead is a small library of SCHEMAS -- abstract explanatory
moves, each of which fires on a characteristic shape of anomaly and proposes a
specific new theory or auxiliary. This is the operational form of "one uses
what one has experience with to devise something new": the schemas are the
experience, carried across domains, and binding one to an anomaly is the
creative step.

They are hand-written, and that is the honest limitation of this stage. The
next version of this component learns its proposal distribution from a corpus
of successful explanations rather than being handed one; the interface below is
deliberately the shape a learned proposer would have to satisfy.

Note what each schema costs. A schema that fires on everything explains
nothing, so each carries a precondition sharp enough to stay silent most of the
time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .theory import (ChargedCorpuscle, ChargedMolecule, EtherWave, Precedent,
                     ScreeningAuxiliary, Theory)


@dataclass
class Anomaly:
    """Something the leading theory got wrong, or could not speak to."""

    kind: str                 # unexplained-transport | failed-prediction | invariance
    observable: str
    detail: str
    context: dict


@dataclass
class Proposal:
    schema: str
    reasoning: str
    new_theories: list = None
    auxiliary: object = None


class Schema:
    name = "schema"
    description = ""

    def fires_on(self, anomaly: Anomaly) -> bool:
        return False

    def propose(self, anomaly: Anomaly) -> Proposal | None:
        return None


class CarriedSubstance(Schema):
    """Something arrives somewhere and deposits a property there.

    Transported effect -> posit a carrier with per-unit properties. This is the
    move behind atoms, ions, quanta, and germs; it is the most reusable schema
    in the library.
    """

    name = "carried-substance"
    description = ("an effect that travels and is deposited implies something "
                   "doing the carrying")

    def fires_on(self, a):
        return a.kind == "unexplained-transport"

    def propose(self, a):
        molecule = ChargedMolecule()
        # This is the Anderson move: the mechanism this theory needs -- charge
        # carried in discrete units by matter -- is not new. Electrolysis
        # already established it decades earlier, with a known, measured
        # charge-to-mass ratio. That is a real, principled reason to prefer
        # this theory before any tube is even built -- so it is stated as a
        # discount on what the theory costs to hold, not smuggled in as an
        # assumption about the answer.
        molecule.precedent = Precedent(
            name="electrolytic-ion",
            source_domain="electrolysis (Faraday's laws)",
            rationale=("charge is already known to be carried by matter in "
                      "discrete units, at a known ratio, in a completely "
                      "different apparatus"),
            discount_bits=5.0)
        return Proposal(
            schema=self.name,
            reasoning=(f"Something crosses the tube and delivers {a.observable} "
                       f"at the far end. Either the disturbance itself travels "
                       f"with no substance to it, or a stream of bodies is being "
                       f"carried across. Those differ in what a magnet or a "
                       f"charged plate should do to them, so both are worth "
                       f"keeping until an experiment separates them. Worth "
                       f"noting before either is tested: electrolysis already "
                       f"showed charge moves in exactly this carried-by-matter "
                       f"way, at a specific known ratio — if that is what is "
                       f"happening here too, it is not a new kind of physics, "
                       f"just a familiar one in an unfamiliar tube."),
            new_theories=[EtherWave(), ChargedCorpuscle(), molecule])


class InterveningMedium(Schema):
    """A predicted effect is missing where the theory says it should appear.

    Posit something in the path absorbing or cancelling it -- but only with the
    independent consequence attached: remove more of the medium and the effect
    must come back. Without that consequence this schema is a licence to
    explain away any failure, which is precisely the abuse it has to avoid.
    """

    name = "intervening-medium"
    description = ("a predicted effect that is absent may be screened rather "
                   "than nonexistent")

    def fires_on(self, a):
        return (a.kind == "failed-prediction"
                and a.detail == "predicted-present-observed-absent")

    def propose(self, a):
        return Proposal(
            schema=self.name,
            reasoning=(f"The theory says {a.observable} should be there and it "
                       f"is not. Before giving the theory up: the tube is not "
                       f"empty. If what remains in it conducts, it would gather "
                       f"at the plates and cancel the field inside, and the "
                       f"beam would feel nothing. That is testable rather than "
                       f"convenient — it says the deflection must COME BACK as "
                       f"the pump improves. If it doesn't, this excuse dies and "
                       f"takes the theory with it."),
            auxiliary=ScreeningAuxiliary(
                name="residual-gas-screening",
                cost_bits=6.0,
                rationale="gas left in the tube conducts and cancels the plate field",
                independent_test="deflection must grow as the vacuum improves"))


class UniversalConstituent(Schema):
    """A measured ratio is the same across every substrate you try.

    Invariance across substrates that ought to differ implies the thing being
    measured does not belong to the substrate. This is the move that turns a
    number into a discovery.
    """

    name = "universal-constituent"
    description = ("a quantity invariant across substrates belongs to none of "
                   "them, so it belongs to something they share")

    def fires_on(self, a):
        return a.kind == "invariance"

    def propose(self, a):
        return Proposal(
            schema=self.name,
            reasoning=(f"{a.detail} The cathode metal makes no difference and "
                       f"neither does the residual gas. If this were matter "
                       f"torn from the electrode, the number would follow the "
                       f"electrode. It does not, so whatever is being measured "
                       f"is not a property of any of these substances — it is "
                       f"something they all contain."))


LIBRARY: list[Schema] = [CarriedSubstance(), InterveningMedium(),
                         UniversalConstituent()]


def abduce(anomaly: Anomaly) -> list[Proposal]:
    """Bind whichever schemas fire. Silence is a valid outcome."""
    out = []
    for sch in LIBRARY:
        if sch.fires_on(anomaly):
            p = sch.propose(anomaly)
            if p:
                out.append(p)
    return out
