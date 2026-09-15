"""Pydantic models for prompts, function definitions, and JSON schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)


class StrictModel(BaseModel):
    """Base model using strict types and rejecting unexpected fields."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )


class StringSchema(StrictModel):
    """Represent a JSON string schema."""

    type: Literal["string"]


class NumberSchema(StrictModel):
    """Represent a JSON number schema."""

    type: Literal["number"]


class IntegerSchema(StrictModel):
    """Represent a JSON integer schema."""

    type: Literal["integer"]


class BooleanSchema(StrictModel):
    """Represent a JSON boolean schema."""

    type: Literal["boolean"]


class NullSchema(StrictModel):
    """Represent a JSON null schema."""

    type: Literal["null"]


class ArraySchema(StrictModel):
    """Represent a JSON array schema and its item schema."""

    type: Literal["array"]
    items: (
        StringSchema
        | NumberSchema
        | IntegerSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema
    )


class ObjectSchema(StrictModel):
    """Represent a JSON object schema with properties and required keys."""

    type: Literal["object"]
    properties: dict[
        str,
        StringSchema
        | NumberSchema
        | IntegerSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema,
    ]
    required: list[str]

    @model_validator(mode="after")
    def validate_required_properties(self) -> ObjectSchema:
        """Ensure required keys exist, are unique, and names are non-empty."""
        missing = set(self.required) - set(self.properties)

        if missing:
            raise ValueError("required property is missing from properties")

        if len(self.required) != len(set(self.required)):
            raise ValueError("required properties must not contain duplicates")

        for property_name in self.properties:
            if property_name == "":
                raise ValueError("property names must not be empty")

        return self


class FunctionDefinition(StrictModel):
    """Represent a callable function and its parameter and return schemas."""

    name: str
    description: str
    parameters: ObjectSchema
    returns: (
        StringSchema
        | NumberSchema
        | IntegerSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema
    )

    @field_validator("parameters", mode="before")
    @classmethod
    def normalize_parameters(cls, value: object) -> object:
        """Normalize flat parameter definitions into an object schema."""
        if isinstance(value, ObjectSchema):
            return value

        if (
            isinstance(value, dict)
            and value.get("type") == "object"
            and isinstance(value.get("properties"), dict)
            and isinstance(value.get("required"), list)
        ):
            return value

        if isinstance(value, dict):
            return {
                "type": "object",
                "properties": value,
                "required": list(value),
            }

        return value


class PromptInput(StrictModel):
    """Represent one validated user prompt from the input data."""

    prompt: str
