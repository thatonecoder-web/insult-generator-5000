"""Sentence frames.

A frame is a sentence with typed slots. ``{name}`` inserts the slot's word and
``{a name}`` inserts it preceded by the right indefinite article. The slot kind decides
which vocabulary entries may fill it, which is how the generator avoids sentences such as
"You are fallacious" (an adjective that only describes arguments) or "a balderdash"
(a mass noun).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from insultgen.models import Register

PLACEHOLDER = re.compile(r"\{(?:(a) )?(\w+)\}")

THING_NOUNS = ("argument", "claim", "position", "theory")


class SlotKind(StrEnum):
    """What may fill a slot."""

    PERSON_ADJECTIVE = "person_adjective"
    THING_ADJECTIVE = "thing_adjective"
    BOTH_ADJECTIVE = "both_adjective"
    PERSON_NOUN = "person_noun"
    ABSTRACT_NOUN = "abstract_noun"
    LACK_NOUN = "lack_noun"
    THING_NOUN = "thing_noun"


PA = SlotKind.PERSON_ADJECTIVE
TA = SlotKind.THING_ADJECTIVE
BA = SlotKind.BOTH_ADJECTIVE
PN = SlotKind.PERSON_NOUN
AN = SlotKind.ABSTRACT_NOUN
LN = SlotKind.LACK_NOUN
TN = SlotKind.THING_NOUN


@dataclass(frozen=True, slots=True)
class Frame:
    """A sentence pattern. An empty ``registers`` set means it suits any register."""

    id: str
    text: str
    slots: Mapping[str, SlotKind]
    registers: frozenset[Register] = frozenset()


def _frame(id_: str, text: str, register: Register | None = None, **slots: SlotKind) -> Frame:
    registers = frozenset({register}) if register else frozenset()
    return Frame(id=id_, text=text, slots=slots, registers=registers)


CASUAL, FORMAL, ARCHAIC = Register.CASUAL, Register.FORMAL, Register.ARCHAIC
ACADEMIC, LEGAL, VULGAR = Register.ACADEMIC, Register.LEGAL, Register.VULGAR

FRAMES: tuple[Frame, ...] = (
    _frame("any-01", "You are {a adj1} {person}.", adj1=PA, person=PN),
    _frame("any-02", "What {a adj1} {person} you are.", adj1=PA, person=PN),
    _frame("any-03", "I have rarely met anyone so {adj1} and so {adj2}.", adj1=PA, adj2=PA),
    _frame("any-04", "You are not merely {adj1}; you are {adj2}.", adj1=PA, adj2=PA),
    _frame(
        "any-05",
        "You are {adj1}, {adj2}, and, worst of all, {adj3}.",
        adj1=PA,
        adj2=PA,
        adj3=PA,
    ),
    _frame("any-06", "You are entirely devoid of {lack}.", lack=LN),
    _frame("any-07", "There is not a trace of {lack} in you.", lack=LN),
    _frame("any-08", "That is {abstract}, plain and simple.", abstract=AN),
    _frame("any-09", "Nothing but {abstract} ever comes out of your mouth.", abstract=AN),
    _frame("any-10", "Your {thing} is {adj1} and {adj2}.", thing=TN, adj1=TA, adj2=TA),
    _frame("any-11", "What {a adj1} {thing}.", adj1=TA, thing=TN),
    _frame(
        "any-12",
        "{a adj1} {thing}, offered by {a adj2} {person}.",
        adj1=TA,
        thing=TN,
        adj2=PA,
        person=PN,
    ),
    _frame("any-13", "That {thing} is {adj1}, and so are you.", thing=TN, adj1=BA),
    _frame("cas-01", "You're such {a adj1} {person}.", CASUAL, adj1=PA, person=PN),
    _frame("cas-02", "Honestly? You're {adj1}.", CASUAL, adj1=PA),
    _frame("cas-03", "Wow, you're {adj1} and {adj2}.", CASUAL, adj1=PA, adj2=PA),
    _frame(
        "cas-04",
        "Nobody likes {a adj1} {person}, and yet here you are.",
        CASUAL,
        adj1=PA,
        person=PN,
    ),
    _frame("cas-05", "You absolute {person}.", CASUAL, person=PN),
    _frame("cas-06", "Congratulations, you're officially {adj1}.", CASUAL, adj1=PA),
    _frame("cas-07", "Don't be {a adj1} {person}.", CASUAL, adj1=PA, person=PN),
    _frame("cas-08", "That's {abstract}, and you know it.", CASUAL, abstract=AN),
    _frame("cas-09", "Only {a adj1} {person} would say that.", CASUAL, adj1=PA, person=PN),
    _frame(
        "for-01",
        "It is difficult to imagine a more {adj1} {person}.",
        FORMAL,
        adj1=PA,
        person=PN,
    ),
    _frame("for-02", "You are, regrettably, {adj1} and {adj2}.", FORMAL, adj1=PA, adj2=PA),
    _frame("for-03", "One cannot help observing that you are {adj1}.", FORMAL, adj1=PA),
    _frame("for-04", "Your {thing} is, to put it kindly, {adj1}.", FORMAL, thing=TN, adj1=TA),
    _frame(
        "for-05",
        "I find you {adj1}, and I find your {thing} {adj2}.",
        FORMAL,
        adj1=PA,
        thing=TN,
        adj2=TA,
    ),
    _frame("for-06", "You are devoid of {lack}, and it shows.", FORMAL, lack=LN),
    _frame(
        "for-07",
        "Allow me to observe that you are {a adj1} {person}.",
        FORMAL,
        adj1=PA,
        person=PN,
    ),
    _frame("arc-01", "Thou art {a adj1} {person}!", ARCHAIC, adj1=PA, person=PN),
    _frame("arc-02", "Thou {adj1}, {adj2} {person}!", ARCHAIC, adj1=PA, adj2=PA, person=PN),
    _frame("arc-03", "Out upon thee, thou {adj1} {person}!", ARCHAIC, adj1=PA, person=PN),
    _frame("arc-04", "I do despise thee, thou {adj1} {person}.", ARCHAIC, adj1=PA, person=PN),
    _frame("arc-05", "Thou art {adj1}, and {a person} withal.", ARCHAIC, adj1=PA, person=PN),
    _frame("arc-06", "There is no {lack} in thee.", ARCHAIC, lack=LN),
    _frame("arc-07", "Thy speech is naught but {abstract}.", ARCHAIC, abstract=AN),
    _frame("arc-08", "Fie upon thee, thou {person}!", ARCHAIC, person=PN),
    _frame("arc-09", "I know no {person} so {adj1} as thee.", ARCHAIC, person=PN, adj1=PA),
    _frame("aca-01", "This is not analysis; it is {abstract}.", ACADEMIC, abstract=AN),
    _frame("aca-02", "Your thesis suffers from {abstract}.", ACADEMIC, abstract=AN),
    _frame("aca-03", "To call that {thing} {adj1} would be generous.", ACADEMIC, thing=TN, adj1=TA),
    _frame("aca-04", "Your reasoning lacks {lack}.", ACADEMIC, lack=LN),
    _frame(
        "aca-05",
        "You are {a adj1} {person}, and this {thing} proves it.",
        ACADEMIC,
        adj1=PA,
        person=PN,
        thing=TN,
    ),
    _frame(
        "aca-06",
        "One would expect more {lack} from {a adj1} {person}.",
        ACADEMIC,
        lack=LN,
        adj1=PA,
        person=PN,
    ),
    _frame(
        "leg-01",
        "Objection: the {thing} is {adj1} and {adj2}.",
        LEGAL,
        thing=TN,
        adj1=TA,
        adj2=TA,
    ),
    _frame("leg-02", "The court finds you {adj1}.", LEGAL, adj1=PA),
    _frame(
        "leg-03",
        "Counsel's {thing} is {adj1}, and the record so reflects.",
        LEGAL,
        thing=TN,
        adj1=TA,
    ),
    _frame("leg-04", "Your Honor, the witness is {adj1} and {adj2}.", LEGAL, adj1=PA, adj2=PA),
    _frame(
        "leg-05",
        "This {thing} is {adj1}, {adj2}, and wholly without merit.",
        LEGAL,
        thing=TN,
        adj1=TA,
        adj2=TA,
    ),
    _frame(
        "leg-06",
        "You are {a adj1} {person}, and this court knows it.",
        LEGAL,
        adj1=PA,
        person=PN,
    ),
    _frame("leg-07", "I put it to you that you are {adj1}.", LEGAL, adj1=PA),
    _frame("leg-08", "The record will show {abstract} on your part.", LEGAL, abstract=AN),
    _frame("vul-01", "You {adj1} {person}.", VULGAR, adj1=PA, person=PN),
    _frame("vul-02", "What {a adj1} {person}.", VULGAR, adj1=PA, person=PN),
    _frame("vul-03", "That is utter {abstract}.", VULGAR, abstract=AN),
    _frame("vul-04", "Shut up, you {adj1} {person}.", VULGAR, adj1=PA, person=PN),
    _frame(
        "vul-05",
        "You're {a adj1} {person}, and everyone knows it.",
        VULGAR,
        adj1=PA,
        person=PN,
    ),
    _frame("vul-06", "Go on, then, be {a adj1} {person}.", VULGAR, adj1=PA, person=PN),
)


def attributive_slots(frame: Frame) -> frozenset[str]:
    """Adjective slots that modify a noun directly, as in "a {adj1} {person}".

    Adjectives marked ``attributive_only`` ("bloody", "damned") may only fill these.
    Adjective slots must be named ``adj1``, ``adj2``, and so on, and noun slots ``person``
    or ``thing``.
    """
    found: set[str] = set()
    for name, kind in frame.slots.items():
        if kind not in (PA, TA, BA):
            continue
        pattern = r"\{(?:a )?" + name + r"\}(?:,? \{adj\d+\})*,? \{(?:a )?(?:person|thing)\}"
        if re.search(pattern, frame.text):
            found.add(name)
    return frozenset(found)
