import json

from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)
from src.schema_validator import value_matches_schema


Schema = (
    StringSchema
    | NumberSchema
    | BooleanSchema
    | NullSchema
    | ArraySchema
    | ObjectSchema
)


def reject_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    """Build a JSON object while rejecting duplicate keys."""
    seen: set[str] = set()
    result: dict[str, object] = {}

    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key: {key}")

        seen.add(key)
        result[key] = value

    return result


def generated_json_matches_schema(
    text: str,
    schema: Schema,
) -> bool:
    """Return whether generated text is valid JSON matching the schema."""
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
        )
    except (json.JSONDecodeError, ValueError):
        return False

    return value_matches_schema(value, schema)
