from src.generated_output import generated_json_matches_schema
from src.models import NumberSchema, ObjectSchema, StringSchema


def test_generated_json_matches_schema() -> None:
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
