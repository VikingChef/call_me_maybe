from typing import Literal

from pydantic import BaseModel, ConfigDict


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
    items: StringSchema
