"""Tests for incremental JSON syntax tracking."""

from src.json_state import JSONState


def test_empty_object_completes() -> None:
    """Complete a valid empty object."""
    state = JSONState()

    state.feed("{")
    state.feed("}")

    assert state.complete is True
    assert state.stack == []


def test_nested_structures_complete() -> None:
    """Complete valid nested JSON containers."""
    state = JSONState()

    for char in '{"items":[]}':
        state.feed(char)

    assert state.complete is True
    assert state.stack == []


def test_structure_characters_inside_string_are_ignored() -> None:
    """Ignore structural characters that appear inside strings."""
    state = JSONState()

    for char in '{"text":"{[hello]}"}':
        state.feed(char)

    assert state.complete is True
    assert state.stack == []


def test_mismatched_closer_is_invalid() -> None:
    """Reject a closing delimiter that does not match the opener."""
    state = JSONState()

    state.feed("{")
    state.feed("]")

    assert state.invalid is True
    assert state.complete is False


def test_closer_without_opener_is_invalid() -> None:
    """Reject a closing delimiter without an open container."""
    state = JSONState()

    state.feed("}")

    assert state.invalid is True
    assert state.complete is False


def test_missing_colon_is_invalid() -> None:
    """Reject an object property without its required colon."""
    state = JSONState()

    for char in '{"name""Rasmus"}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_trailing_comma_is_invalid() -> None:
    """Reject a trailing comma before an object closes."""
    state = JSONState()

    for char in '{"name":"Rasmus",}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_true_literal_is_valid() -> None:
    """Accept the JSON true literal."""
    state = JSONState()

    for char in '{"active":true}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_false_literal_is_valid() -> None:
    """Accept the JSON false literal."""
    state = JSONState()

    for char in '{"active":false}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_null_literal_is_valid() -> None:
    """Accept the JSON null literal."""
    state = JSONState()

    for char in '{"value":null}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_invalid_literal_is_rejected() -> None:
    """Reject malformed JSON literals."""
    state = JSONState()

    for char in '{"active":truX}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_integer_number_is_valid() -> None:
    """Accept a valid integer-form JSON number."""
    state = JSONState()

    for char in '{"value":42}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_negative_decimal_is_valid() -> None:
    """Accept a valid negative decimal number."""
    state = JSONState()

    for char in '{"value":-12.5}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_exponent_number_is_valid() -> None:
    """Accept valid exponent notation."""
    state = JSONState()

    for char in '{"value":2.5e-3}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_leading_zero_number_is_invalid() -> None:
    """Reject a JSON number with an illegal leading zero."""
    state = JSONState()

    for char in '{"value":01}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_incomplete_decimal_is_invalid() -> None:
    """Reject a decimal number without digits after the decimal point."""
    state = JSONState()

    for char in '{"value":1.}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_whitespace_is_allowed() -> None:
    """Allow insignificant JSON whitespace."""
    state = JSONState()

    for char in '{ "value" : 42 }':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_unknown_character_is_invalid() -> None:
    """Reject characters that cannot legally continue the JSON value."""
    state = JSONState()

    for char in '{"value":truex}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False
