import pytest
from pydantic import ValidationError

from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
    FunctionDefinition,
    PromptInput
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
            items="number",
        )


def test_stringschema_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        StringSchema(
            type="string",
            dragon="red",
        )


def test_arrayschema_with_number_items() -> None:
    schema = ArraySchema(
        type="array",
        items=NumberSchema(type="number"),
    )
    assert schema.type == "array"
    assert schema.items.type == "number"


def test_arrayschema_with_boolean_items() -> None:
    schema = ArraySchema(
        type="array",
        items=BooleanSchema(type="boolean"),
    )
    assert schema.type == "array"
    assert schema.items.type == "boolean"


def test_arrayschema_with_null_items() -> None:
    schema = ArraySchema(
        type="array",
        items=NullSchema(type="null"),
    )
    assert schema.type == "array"
    assert schema.items.type == "null"


def test_arrayschema_with_nested_array() -> None:
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
    with pytest.raises(ValidationError):
        ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
            },
            required=["age"],
        )


def test_objectschema_rejects_duplicate_required_properties() -> None:
    with pytest.raises(ValidationError):
        ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
            },
            required=["name", "name"],
        )


def test_objectschema_with_nested_object() -> None:
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
    with pytest.raises(ValidationError):
        ObjectSchema(
            type="object",
            properties={
                "": StringSchema(type="string"),
            },
            required=[],
        )


def test_functiondefinition_valid() -> None:
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
    input_data = PromptInput(
        prompt="What is the weather in Berlin?"
    )
    assert input_data.prompt == "What is the weather in Berlin?"


def test_functiondefinition_accepts_source_parameter_format() -> None:
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
