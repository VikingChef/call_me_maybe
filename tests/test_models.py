"""Tests for Pydantic models and supported JSON-schema structures."""

import pytest
from pydantic import ValidationError

from src.models import (
    ArraySchema,
    BooleanSchema,
    FunctionDefinition,
    IntegerSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    PromptInput,
    StringSchema,
)


def test_stringschema() -> None:
    """Create a valid string schema."""
    schema = StringSchema(type="string")

    assert schema.type == "string"


def test_stringschema_rejects_invalid_type() -> None:
    """Reject a string schema with the wrong type discriminator."""
    with pytest.raises(ValidationError):
        StringSchema.model_validate(
            {
                "type": "banana",
            }
        )


def test_numberschema() -> None:
    """Create a valid number schema."""
    schema = NumberSchema(type="number")

    assert schema.type == "number"


def test_numberschema_rejects_invalid_type() -> None:
    """Reject a number schema with the wrong type discriminator."""
    with pytest.raises(ValidationError):
        NumberSchema.model_validate(
            {
                "type": "mimic",
            }
        )


def test_integerschema() -> None:
    """Create a valid integer schema."""
    schema = IntegerSchema(type="integer")

    assert schema.type == "integer"


def test_integerschema_rejects_invalid_type() -> None:
    """Reject an integer schema with a non-integer discriminator."""
    with pytest.raises(ValidationError):
        IntegerSchema.model_validate(
            {
                "type": "number",
            }
        )


def test_booleanschema() -> None:
    """Create a valid boolean schema."""
    schema = BooleanSchema(type="boolean")

    assert schema.type == "boolean"


def test_booleanschema_rejects_invalid_type() -> None:
    """Reject a boolean schema with the wrong type discriminator."""
    with pytest.raises(ValidationError):
        BooleanSchema.model_validate(
            {
                "type": "bagofholding",
            }
        )


def test_nullschema() -> None:
    """Create a valid null schema."""
    schema = NullSchema(type="null")

    assert schema.type == "null"


def test_nullschema_rejects_invalid_type() -> None:
    """Reject a null schema with the wrong type discriminator."""
    with pytest.raises(ValidationError):
        NullSchema.model_validate(
            {
                "type": "D20dice",
            }
        )


def test_arrayschema_with_string_items() -> None:
    """Create an array schema containing strings."""
    schema = ArraySchema(
        type="array",
        items=StringSchema(type="string"),
    )

    assert schema.type == "array"
    assert schema.items.type == "string"


def test_arrayschema_rejects_invalid_type() -> None:
    """Reject an array schema with the wrong type discriminator."""
    with pytest.raises(ValidationError):
        ArraySchema.model_validate(
            {
                "type": "vestigeofdivergence",
                "items": {
                    "type": "string",
                },
            }
        )


def test_arrayschema_rejects_invalid_items() -> None:
    """Reject an array whose item definition is not a schema."""
    with pytest.raises(ValidationError):
        ArraySchema.model_validate(
            {
                "type": "array",
                "items": "number",
            }
        )


def test_stringschema_rejects_extra_field() -> None:
    """Reject unexpected fields because schema models forbid extras."""
    with pytest.raises(ValidationError):
        StringSchema.model_validate(
            {
                "type": "string",
                "dragon": "red",
            }
        )


def test_arrayschema_with_number_items() -> None:
    """Create an array schema containing numbers."""
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )

    assert schema.type == "array"
    assert schema.items.type == "number"


def test_arrayschema_with_boolean_items() -> None:
    """Create an array schema containing booleans."""
    schema = ArraySchema(
        type="array",
        items=BooleanSchema(type="boolean"),
    )

    assert schema.type == "array"
    assert schema.items.type == "boolean"


def test_arrayschema_with_null_items() -> None:
    """Create an array schema containing null values."""
    schema = ArraySchema(
        type="array",
        items=NullSchema(type="null"),
    )

    assert schema.type == "array"
    assert schema.items.type == "null"


def test_arrayschema_with_nested_array() -> None:
    """Create an array schema containing nested arrays."""
    schema = ArraySchema(
        type="array",
        items=ArraySchema(
            type="array",
            items=StringSchema(type="string"),
        ),
    )

    assert schema.type == "array"
    assert schema.items.type == "array"
    assert schema.items.items.type == "string"


def test_objectschema_with_string_and_number_properties() -> None:
    """Create an object schema with mixed property types."""
    schema = ObjectSchema(
        type="object",
        properties={
            "name": StringSchema(type="string"),
            "age": NumberSchema(type="number"),
        },
        required=["name"],
    )

    assert schema.type == "object"
    assert schema.properties["name"].type == "string"
    assert schema.properties["age"].type == "number"
    assert schema.required == ["name"]


def test_objectschema_rejects_unknown_required_property() -> None:
    """Reject required names that are absent from object properties."""
    with pytest.raises(ValidationError):
        ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
            },
            required=["age"],
        )


def test_objectschema_rejects_duplicate_required_properties() -> None:
    """Reject duplicate entries in the required-property list."""
    with pytest.raises(ValidationError):
        ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
            },
            required=["name", "name"],
        )


def test_objectschema_with_nested_object() -> None:
    """Create an object schema containing another object."""
    schema = ObjectSchema(
        type="object",
        properties={
            "address": ObjectSchema(
                type="object",
                properties={
                    "city": StringSchema(type="string"),
                },
                required=["city"],
            ),
        },
        required=["address"],
    )

    assert schema.type == "object"
    assert schema.properties["address"].type == "object"
    assert schema.properties["address"].properties["city"].type == "string"


def test_arrayschema_with_object_items() -> None:
    """Create an array schema containing object items."""
    schema = ArraySchema(
        type="array",
        items=ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
            },
            required=["name"],
        ),
    )

    assert schema.type == "array"
    assert schema.items.type == "object"
    assert schema.items.properties["name"].type == "string"


def test_objectschema_with_array_property() -> None:
    """Create an object schema with an array-valued property."""
    schema = ObjectSchema(
        type="object",
        properties={
            "tags": ArraySchema(
                type="array",
                items=StringSchema(type="string"),
            ),
        },
        required=["tags"],
    )

    assert schema.type == "object"
    assert schema.properties["tags"].type == "array"
    assert schema.properties["tags"].items.type == "string"


def test_objectschema_rejects_empty_property_name() -> None:
    """Reject object schemas containing an empty property name."""
    with pytest.raises(ValidationError):
        ObjectSchema(
            type="object",
            properties={
                "": StringSchema(type="string"),
            },
            required=[],
        )


def test_functiondefinition_valid() -> None:
    """Create a valid function definition."""
    function = FunctionDefinition(
        name="get_weather",
        description="Get weather for a city",
        parameters=ObjectSchema(
            type="object",
            properties={
                "city": StringSchema(type="string"),
            },
            required=["city"],
        ),
        returns=StringSchema(type="string"),
    )

    assert function.name == "get_weather"
    assert function.parameters.properties["city"].type == "string"
    assert function.returns.type == "string"


def test_promptinput_valid() -> None:
    """Create a valid prompt input."""
    input_data = PromptInput(
        prompt="What is the weather in Berlin?"
    )

    assert input_data.prompt == "What is the weather in Berlin?"


def test_functiondefinition_accepts_source_parameter_format() -> None:
    """Convert source-format parameter dictionaries into an object schema."""
    function = FunctionDefinition.model_validate(
        {
            "name": "fn_add_numbers",
            "description": (
                "Add two numbers together and return their sum."
            ),
            "parameters": {
                "a": {
                    "type": "number",
                },
                "b": {
                    "type": "number",
                },
            },
            "returns": {
                "type": "number",
            },
        }
    )

    assert function.parameters.type == "object"
    assert set(function.parameters.properties) == {"a", "b"}
    assert function.parameters.properties["a"].type == "number"
    assert function.parameters.properties["b"].type == "number"
    assert function.parameters.required == ["a", "b"]


def test_functiondefinition_accepts_integer_parameter() -> None:
    """Accept integer parameters in source-format function definitions."""
    function = FunctionDefinition.model_validate(
        {
            "name": "fn_is_even",
            "description": "Check whether an integer is even.",
            "parameters": {
                "n": {
                    "type": "integer",
                },
            },
            "returns": {
                "type": "boolean",
            },
        }
    )

    assert function.parameters.type == "object"
    assert function.parameters.properties["n"].type == "integer"
    assert function.parameters.required == ["n"]
