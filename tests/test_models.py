import pytest
from pydantic import ValidationError

from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    StringSchema,
)


def test_stringschema() -> None:
    schema = StringSchema(type="string")
    assert schema.type == "string"


def test_stringschema_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        StringSchema(type="banana")


def test_numberschema() -> None:
    schema = NumberSchema(type="number")
    assert schema.type == "number"


def test_numberschema_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        NumberSchema(type="mimic")


def test_booleanschema() -> None:
    schema = BooleanSchema(type="boolean")
    assert schema.type == "boolean"


def test_booleanschema_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        BooleanSchema(type="bagofholding")


def test_nullschema() -> None:
    schema = NullSchema(type="null")
    assert schema.type == "null"


def test_nullschema_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        NullSchema(type="D20dice")


def test_arrayschema_with_string_items() -> None:
    schema = ArraySchema(
        type="array",
        items=StringSchema(type="string"),
    )
    assert schema.type == "array"
    assert schema.items.type == "string"


def test_arrayschema_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        ArraySchema(
            type="vestigeofdivergence",
            items=StringSchema(type="string"),
        )


def test_arrayschema_rejects_invalid_items() -> None:
    with pytest.raises(ValidationError):
        ArraySchema(
            type="array",
            items=NullSchema(type="null"),
        )


def test_stringschema_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        StringSchema(
            type="string",
            dragon="red",
        )
