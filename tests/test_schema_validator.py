"""Tests for validating Python values against JSON-schema models."""

from src.models import (
    ArraySchema,
    BooleanSchema,
    IntegerSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)
from src.schema_validator import value_matches_schema


def test_string_schema() -> None:
    """Accept strings and reject non-string values."""
    schema = StringSchema(type="string")

    assert value_matches_schema("hello", schema) is True
    assert value_matches_schema(42, schema) is False


def test_number_schema() -> None:
    """Accept integers and floats while rejecting booleans as numbers."""
    schema = NumberSchema(type="number")

    assert value_matches_schema(42, schema) is True
    assert value_matches_schema(3.14, schema) is True
    assert value_matches_schema(True, schema) is False


def test_integer_schema() -> None:
    """Accept integers while rejecting floats and booleans."""
    schema = IntegerSchema(type="integer")

    assert value_matches_schema(42, schema) is True
    assert value_matches_schema(3.14, schema) is False
    assert value_matches_schema(True, schema) is False


def test_boolean_schema() -> None:
    """Accept booleans and reject integer values."""
    schema = BooleanSchema(type="boolean")

    assert value_matches_schema(True, schema) is True
    assert value_matches_schema(1, schema) is False


def test_null_schema() -> None:
    """Accept None and reject the string form of null."""
    schema = NullSchema(type="null")

    assert value_matches_schema(None, schema) is True
    assert value_matches_schema("null", schema) is False


def test_array_schema() -> None:
    """Validate every item in an array against its item schema."""
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    assert value_matches_schema([1, 2, 3], schema) is True
    assert value_matches_schema([1, "two", 3], schema) is False


def test_object_schema() -> None:
    """Validate required keys, value types, and unknown properties."""
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
    """Validate nested arrays and their item schemas recursively."""
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
