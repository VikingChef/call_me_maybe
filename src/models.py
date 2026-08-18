from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )


class StringSchema(StrictModel):
    type: Literal["string"]


class NumberSchema(StrictModel):
    type: Literal["number"]


class BooleanSchema(StrictModel):
    type: Literal["boolean"]


class NullSchema(StrictModel):
    type: Literal["null"]


class ArraySchema(StrictModel):
    type: Literal["array"]
    items: (
        StringSchema
        | NumberSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema
    )


class ObjectSchema(StrictModel):
    type: Literal["object"]
    properties: dict[
        str,
        StringSchema
        | NumberSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema,
    ]
    required: list[str]

    @model_validator(mode="after")
    def validate_required_properties(self) -> ObjectSchema:
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
    name: str
    description: str
    parameters: ObjectSchema
    returns: (
        StringSchema
        | NumberSchema
        | BooleanSchema
        | NullSchema
        | ArraySchema
        | ObjectSchema
    )

    @field_validator("parameters", mode="before")
    @classmethod
    def normalize_parameters(cls, value):
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
    prompt: str
