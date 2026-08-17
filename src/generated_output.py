import json

from src.schema_validator import value_matches_schema


def reject_duplicate_keys(pairs):
    seen = set()
    result = {}

    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key: {key}")

        seen.add(key)
        result[key] = value

    return result


def generated_json_matches_schema(text: str, schema) -> bool:
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
        )
    except (json.JSONDecodeError, ValueError):
        return False

    return value_matches_schema(value, schema)
