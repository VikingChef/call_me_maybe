import json

from src.schema_validator import value_matches_schema


def generated_json_matches_schema(text: str, schema) -> bool:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return False

    return value_matches_schema(value, schema)
