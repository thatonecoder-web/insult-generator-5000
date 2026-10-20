from insultgen.generation.templates import FRAMES, PLACEHOLDER, Frame, SlotKind, attributive_slots
from insultgen.models import Register


def test_frame_ids_are_unique() -> None:
    ids = [frame.id for frame in FRAMES]
    assert len(set(ids)) == len(ids)


def test_every_placeholder_has_a_slot_and_every_slot_is_used() -> None:
    for frame in FRAMES:
        used = {name for _, name in PLACEHOLDER.findall(frame.text)}
        assert used == set(frame.slots), frame.id


def test_slot_kinds_are_valid() -> None:
    for frame in FRAMES:
        assert all(isinstance(kind, SlotKind) for kind in frame.slots.values())


def test_frames_are_complete_sentences() -> None:
    for frame in FRAMES:
        assert frame.text[-1] in ".!?", frame.id
        assert frame.text.count("{") == frame.text.count("}"), frame.id


def test_every_register_has_its_own_frames() -> None:
    for register in Register:
        specific = [f for f in FRAMES if register in f.registers]
        assert len(specific) >= 5, register


def test_frame_ids_start_with_their_register() -> None:
    prefixes = {"any": set(), "cas": {Register.CASUAL}, "for": {Register.FORMAL}}
    prefixes |= {"arc": {Register.ARCHAIC}, "aca": {Register.ACADEMIC}}
    prefixes |= {"leg": {Register.LEGAL}, "vul": {Register.VULGAR}}
    for frame in FRAMES:
        assert set(frame.registers) == prefixes[frame.id[:3]], frame.id


def _frame(frame_id: str) -> Frame:
    return next(frame for frame in FRAMES if frame.id == frame_id)


def test_attributive_slots_are_adjectives_directly_before_a_noun() -> None:
    assert attributive_slots(_frame("vul-01")) == {"adj1"}
    assert attributive_slots(_frame("any-01")) == {"adj1"}
    assert attributive_slots(_frame("arc-02")) == {"adj1", "adj2"}
    assert attributive_slots(_frame("any-12")) == {"adj1", "adj2"}


def test_predicate_adjectives_are_not_attributive() -> None:
    for frame_id in ("cas-02", "any-03", "any-04", "any-05", "leg-02", "for-03"):
        assert attributive_slots(_frame(frame_id)) == frozenset(), frame_id


def test_slot_names_follow_the_convention() -> None:
    adjectives = {SlotKind.PERSON_ADJECTIVE, SlotKind.THING_ADJECTIVE, SlotKind.BOTH_ADJECTIVE}
    for frame in FRAMES:
        for name, kind in frame.slots.items():
            if kind in adjectives:
                assert name.startswith("adj"), (frame.id, name)
