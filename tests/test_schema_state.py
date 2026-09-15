"""Tests for schema-aware JSON generation state."""

from src.models import (
    ArraySchema,
    BooleanSchema,
    IntegerSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)
from src.schema_state import SchemaState


def test_string_schema_start() -> None:
    """Allow a quote as the start of a string value."""
    state = SchemaState(StringSchema(type="string"))

    assert state.valid_value_starts() == {'"'}


def test_number_schema_start() -> None:
    """Allow numeric characters as the start of a number value."""
    state = SchemaState(NumberSchema(type="number"))

    assert state.valid_value_starts() == set("-0123456789")


def test_integer_schema_start() -> None:
    """Allow numeric characters as the start of an integer value."""
    state = SchemaState(IntegerSchema(type="integer"))

    assert state.valid_value_starts() == set("-0123456789")


def test_boolean_schema_start() -> None:
    """Allow true or false as boolean value starts."""
    state = SchemaState(BooleanSchema(type="boolean"))

    assert state.valid_value_starts() == {"t", "f"}


def test_null_schema_start() -> None:
    """Allow null as a null value start."""
    state = SchemaState(NullSchema(type="null"))

    assert state.valid_value_starts() == {"n"}


def test_array_schema_start() -> None:
    """Allow an opening bracket as the start of an array."""
    state = SchemaState(
        ArraySchema(
            type="array",
            items=StringSchema(type="string"),
        )
    )

    assert state.valid_value_starts() == {"["}


def test_object_schema_start() -> None:
    """Allow an opening brace as the start of an object."""
    state = SchemaState(
        ObjectSchema(
            type="object",
            properties={},
            required=[],
        )
    )

    assert state.valid_value_starts() == {"{"}


def test_enter_object_tracks_schema() -> None:
    """Track an object schema and its initially empty seen-key set."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
            "age": NumberSchema(type="number"),
        },
        required=["name"],
    )

    state = SchemaState(schema)
    state.enter_object()

    assert state.invalid is False
    assert len(state.stack) == 1
    assert state.stack[-1]["schema"] == schema
    assert state.stack[-1]["seen_keys"] == set()


def test_valid_key_prefix_accepts_allowed_prefixes() -> None:
    """Accept prefixes that can still become valid object keys."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
            "age": NumberSchema(type="number"),
        },
        required=[],
    )

    state = SchemaState(schema)
    state.enter_object()

    assert state.valid_key_prefix("n") is True
    assert state.valid_key_prefix("na") is True
    assert state.valid_key_prefix("a") is True
    assert state.valid_key_prefix("x") is False


def test_valid_key_prefix_rejects_seen_key() -> None:
    """Reject an object key that has already been generated."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
            "age": NumberSchema(type="number"),
        },
        required=[],
    )

    state = SchemaState(schema)
    state.enter_object()

    seen_keys = state.stack[-1]["seen_keys"]
    assert seen_keys is not None
    seen_keys.add("name")

    assert state.valid_key_prefix("name") is False
    assert state.valid_key_prefix("age") is True


def test_finish_key_sets_property_schema() -> None:
    """Switch to the schema belonging to a completed object key."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": NumberSchema(type="number"),
        },
        required=["age"],
    )

    state = SchemaState(schema)
    state.enter_object()
    state.start_key()

    for char in "age":
        state.add_key_character(char)

    state.finish_key()

    assert state.invalid is False
    assert isinstance(state.current_schema, NumberSchema)

    seen_keys = state.stack[-1]["seen_keys"]
    assert seen_keys is not None
    assert "age" in seen_keys


def test_invalid_key_prefix_is_rejected() -> None:
    """Mark an impossible object-key prefix as invalid."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
        },
        required=[],
    )

    state = SchemaState(schema)
    state.enter_object()
    state.start_key()
    state.add_key_character("x")

    assert state.invalid is True


def test_incomplete_key_is_rejected_when_finished() -> None:
    """Reject a key that ends before matching a complete property name."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
        },
        required=[],
    )

    state = SchemaState(schema)
    state.enter_object()
    state.start_key()

    for char in "na":
        state.add_key_character(char)

    state.finish_key()

    assert state.invalid is True


def test_enter_array_sets_item_schema() -> None:
    """Use an array's item schema while generating its contents."""
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    state = SchemaState(schema)
    state.enter_array()

    assert state.invalid is False
    assert isinstance(state.current_schema, NumberSchema)
    assert len(state.stack) == 1


def test_finish_value_in_array_keeps_item_schema() -> None:
    """Keep the item schema ready for another array value."""
    schema = ArraySchema(
        type="array",
        items=StringSchema(type="string"),
    )

    state = SchemaState(schema)
    state.enter_array()
    state.finish_value()

    assert isinstance(state.current_schema, StringSchema)


def test_exit_nested_container_returns_to_parent_schema() -> None:
    """Restore the parent schema after leaving a nested container."""
    schema = ObjectSchema(
        type="object",
        properties={
            "values": ArraySchema(
                type="array",
                items=NumberSchema(type="number"),
            ),
        },
        required=["values"],
    )

    state = SchemaState(schema)
    state.enter_object()
    state.start_key()

    for char in "values":
        state.add_key_character(char)

    state.finish_key()
    state.enter_array()
    state.exit_container()

    assert state.invalid is False
    assert isinstance(state.current_schema, ObjectSchema)
    assert len(state.stack) == 1
