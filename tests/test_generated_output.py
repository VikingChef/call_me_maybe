"""Tests for validating completed generated JSON against schemas."""

from src.generated_output import generated_json_matches_schema
from src.models import NumberSchema, ObjectSchema, StringSchema


def test_generated_json_matches_schema() -> None:
    """Accept valid generated JSON that matches the required schema."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
        },
        required=["name"],
    )

    assert generated_json_matches_schema(
        '{"name":"Rasmus"}',
        schema,
    ) is True


def test_malformed_generated_json_is_rejected() -> None:
    """Reject generated text that is not valid JSON."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
        },
        required=["name"],
    )

    assert generated_json_matches_schema(
        '{"name":"Rasmus"',
        schema,
    ) is False


def test_generated_json_with_wrong_schema_is_rejected() -> None:
    """Reject valid JSON whose values violate the required schema."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": NumberSchema(type="number"),
        },
        required=["age"],
    )

    assert generated_json_matches_schema(
        '{"age":"forty-five"}',
        schema,
    ) is False


def test_generated_json_rejects_duplicate_keys() -> None:
    """Reject generated objects containing duplicate JSON keys."""
    schema = ObjectSchema(
        type="object",
        properties={
            "age": NumberSchema(type="number"),
        },
        required=["age"],
    )

    assert generated_json_matches_schema(
        '{"age":45,"age":46}',
        schema,
    ) is False
