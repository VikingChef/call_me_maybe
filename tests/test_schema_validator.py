from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)
from src.schema_validator import value_matches_schema


def test_string_schema() -> None:
    schema = StringSchema(type="string")

    assert value_matches_schema("hello", schema) is True
    assert value_matches_schema(42, schema) is False


def test_number_schema() -> None:
    schema = NumberSchema(type="number")

    assert value_matches_schema(42, schema) is True
    assert value_matches_schema(3.14, schema) is True
    assert value_matches_schema(True, schema) is False


def test_boolean_schema() -> None:
    schema = BooleanSchema(type="boolean")

    assert value_matches_schema(True, schema) is True
    assert value_matches_schema(1, schema) is False


def test_null_schema() -> None:
    schema = NullSchema(type="null")

    assert value_matches_schema(None, schema) is True
    assert value_matches_schema("null", schema) is False


def test_array_schema() -> None:
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    assert value_matches_schema([1, 2, 3], schema) is True
    assert value_matches_schema([1, "two", 3], schema) is False


def test_object_schema() -> None:
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
            "age": NumberSchema(type="number"),
        },
        required=["name"],
    )

    assert value_matches_schema(
        {"name": "Rasmus", "age": 45},
        schema,
    ) is True

    assert value_matches_schema(
        {"age": 45},
        schema,
    ) is False

    assert value_matches_schema(
        {"name": "Rasmus", "unknown": True},
        schema,
    ) is False


def test_nested_schema() -> None:
    schema = ObjectSchema(
        type="object",
        properties={
            "values": ArraySchema(
                type="array",
                items=BooleanSchema(type="boolean"),
            ),
        },
        required=["values"],
    )

    assert value_matches_schema(
        {"values": [True, False]},
        schema,
    ) is True

    assert value_matches_schema(
        {"values": [True, 1]},
        schema,
    ) is False
