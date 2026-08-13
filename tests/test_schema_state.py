from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)
from src.schema_state import SchemaState


def test_string_schema_start() -> None:
    state = SchemaState(StringSchema(type="string"))

    assert state.valid_value_starts() == {'"'}


def test_number_schema_start() -> None:
    state = SchemaState(NumberSchema(type="number"))

    assert state.valid_value_starts() == set("-0123456789")


def test_boolean_schema_start() -> None:
    state = SchemaState(BooleanSchema(type="boolean"))

    assert state.valid_value_starts() == {"t", "f"}


def test_null_schema_start() -> None:
    state = SchemaState(NullSchema(type="null"))

    assert state.valid_value_starts() == {"n"}


def test_array_schema_start() -> None:
    state = SchemaState(
        ArraySchema(
            type="array",
            items=StringSchema(type="string"),
        )
    )

    assert state.valid_value_starts() == {"["}


def test_object_schema_start() -> None:
    state = SchemaState(
        ObjectSchema(
            type="object",
            properties={},
            required=[],
        )
    )

    assert state.valid_value_starts() == {"{"}


def test_enter_object_tracks_schema() -> None:
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
    state.stack[-1]["seen_keys"].add("name")

    assert state.valid_key_prefix("name") is False
    assert state.valid_key_prefix("age") is True


def test_finish_key_sets_property_schema() -> None:
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
    assert "age" in state.stack[-1]["seen_keys"]


def test_invalid_key_prefix_is_rejected() -> None:
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
    schema = ArraySchema(
        type="array",
        items=StringSchema(type="string"),
    )

    state = SchemaState(schema)
    state.enter_array()
    state.finish_value()

    assert isinstance(state.current_schema, StringSchema)


def test_exit_nested_container_returns_to_parent_schema() -> None:
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
