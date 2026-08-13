from src.constrained_state import ConstrainedState
from src.models import (
    ArraySchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)


def test_constrained_state_accepts_matching_object() -> None:
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
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    state = ConstrainedState(schema)

    for char in "[1,2,3]":
        state.feed(char)

    assert state.invalid is False
    assert state.complete is True


def test_array_rejects_wrong_item_type() -> None:
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
