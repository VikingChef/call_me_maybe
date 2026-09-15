"""Tests for combined JSON-syntax and schema-constrained state."""

from src.constrained_state import ConstrainedState
from src.models import (
    ArraySchema,
    IntegerSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)


def test_constrained_state_accepts_matching_object() -> None:
    """Accept an object whose value matches the required schema."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": NumberSchema(type="number"),
        },
        required=["age"],
    )

    state = ConstrainedState(schema)

    for char in '{"age":45}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_constrained_state_rejects_wrong_value_type() -> None:
    """Reject an object value with the wrong schema type."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": NumberSchema(type="number"),
        },
        required=["age"],
    )

    state = ConstrainedState(schema)

    for char in '{"age":"forty-five"}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_constrained_state_rejects_unknown_key() -> None:
    """Reject object keys that are not defined by the schema."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": NumberSchema(type="number"),
        },
        required=["age"],
    )

    state = ConstrainedState(schema)

    for char in '{"name":"Rasmus"}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_constrained_state_rejects_missing_required_key() -> None:
    """Reject an object closed before all required keys are generated."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
            "age": NumberSchema(type="number"),
        },
        required=["name", "age"],
    )

    state = ConstrainedState(schema)

    for char in '{"name":"Rasmus"}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_brace_inside_string_does_not_close_container() -> None:
    """Treat braces inside strings as text rather than container syntax."""
    schema = ObjectSchema(
        type="object",
        properties={
            "text": StringSchema(type="string"),
        },
        required=["text"],
    )

    state = ConstrainedState(schema)

    for char in '{"text":"hello } there"}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_array_accepts_matching_item_types() -> None:
    """Accept array items that match the configured item schema."""
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    state = ConstrainedState(schema)

    for char in "[1,2,3]":
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_constrained_state_accepts_integer_value() -> None:
    """Accept whole-number values for integer schemas."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": IntegerSchema(type="integer"),
        },
        required=["age"],
    )

    state = ConstrainedState(schema)

    for char in '{"age":45}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_constrained_state_rejects_decimal_for_integer() -> None:
    """Reject decimal notation when an integer value is required."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": IntegerSchema(type="integer"),
        },
        required=["age"],
    )

    state = ConstrainedState(schema)

    for char in '{"age":45.5}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_constrained_state_rejects_exponent_for_integer() -> None:
    """Reject exponent notation when an integer value is required."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": IntegerSchema(type="integer"),
        },
        required=["age"],
    )

    state = ConstrainedState(schema)

    for char in '{"age":45e2}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_array_rejects_wrong_item_type() -> None:
    """Reject array items that violate the configured item schema."""
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    state = ConstrainedState(schema)

    for char in '[1,"two",3]':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False


def test_nested_object_accepts_matching_schema() -> None:
    """Accept nested objects whose values match the nested schema."""
    schema = ObjectSchema(
        type="object",
        properties={
            "person": ObjectSchema(
                type="object",
                properties={
                    "age": NumberSchema(type="number"),
                },
                required=["age"],
            ),
        },
        required=["person"],
    )

    state = ConstrainedState(schema)

    for char in '{"person":{"age":45}}':
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_nested_object_rejects_wrong_nested_type() -> None:
    """Reject nested values that violate the nested property schema."""
    schema = ObjectSchema(
        type="object",
        properties={
            "person": ObjectSchema(
                type="object",
                properties={
                    "age": NumberSchema(type="number"),
                },
                required=["age"],
            ),
        },
        required=["person"],
    )

    state = ConstrainedState(schema)

    for char in '{"person":{"age":"forty-five"}}':
        state.feed(char)

    assert state.invalid is True
    assert state.complete is False
