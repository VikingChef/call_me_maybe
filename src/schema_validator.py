import math

from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)


def value_matches_schema(
    value: object,
    schema: (
        StringSchema
        | NumberSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema
    ),
) -> bool:
    """Return whether a Python value matches the given schema."""
    if isinstance(schema, StringSchema):
        return isinstance(value, str)

    if isinstance(schema, NumberSchema):
        if isinstance(value, bool):
            return False

        if isinstance(value, int):
            return True

        if isinstance(value, float):
            return math.isfinite(value)

        return False

    if isinstance(schema, BooleanSchema):
        return isinstance(value, bool)

    if isinstance(schema, NullSchema):
        return value is None

    if isinstance(schema, ArraySchema):
        if not isinstance(value, list):
            return False

        return all(
            value_matches_schema(item, schema.items)
            for item in value
        )

    if isinstance(schema, ObjectSchema):
        if not isinstance(value, dict):
            return False

        for required_name in schema.required:
            if required_name not in value:
                return False

        for name, item in value.items():
            if name not in schema.properties:
                return False

            if not value_matches_schema(
                item,
                schema.properties[name],
            ):
                return False

        return True

    return False
