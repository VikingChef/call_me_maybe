"""Track schema requirements while constrained JSON is generated."""

from typing import TypedDict

from src.models import (
    ArraySchema,
    BooleanSchema,
    IntegerSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)


Schema = (
    StringSchema
    | NumberSchema
    | IntegerSchema
    | BooleanSchema
    | NullSchema
    | ArraySchema
    | ObjectSchema
)


class SchemaFrame(TypedDict):
    """Represent one object or array frame in the schema stack."""

    schema: Schema
    seen_keys: set[str] | None


class SchemaState:
    """Track whether generated JSON remains compatible with its schema."""

    def __init__(self, schema: Schema) -> None:
        """Initialize schema tracking for constrained generation."""
        self.schema = schema
        self.current_schema: Schema = schema
        self.stack: list[SchemaFrame] = []
        self.key_buffer = ""
        self.invalid = False

    def valid_value_starts(self) -> set[str]:
        """Return characters that may start the current schema's value."""
        schema = self.current_schema

        if isinstance(schema, StringSchema):
            return {'"'}

        if isinstance(schema, NumberSchema):
            return set("-0123456789")

        if isinstance(schema, IntegerSchema):
            return set("-0123456789")

        if isinstance(schema, BooleanSchema):
            return {"t", "f"}

        if isinstance(schema, NullSchema):
            return {"n"}

        if isinstance(schema, ArraySchema):
            return {"["}

        if isinstance(schema, ObjectSchema):
            return {"{"}

        return set()

    def enter_object(self) -> None:
        """Enter an object and begin tracking its generated keys."""
        if not isinstance(self.current_schema, ObjectSchema):
            self.invalid = True
            return

        self.stack.append(
            {
                "schema": self.current_schema,
                "seen_keys": set(),
            }
        )
        self.key_buffer = ""

    def enter_array(self) -> None:
        """Enter an array and switch to its item schema."""
        if not isinstance(self.current_schema, ArraySchema):
            self.invalid = True
            return

        self.stack.append(
            {
                "schema": self.current_schema,
                "seen_keys": None,
            }
        )
        self.current_schema = self.current_schema.items

    def finish_value(self) -> None:
        """Restore the schema expected after finishing the current value."""
        if not self.stack:
            return

        frame = self.stack[-1]
        parent_schema = frame["schema"]

        if isinstance(parent_schema, ArraySchema):
            self.current_schema = parent_schema.items
            return

        if isinstance(parent_schema, ObjectSchema):
            self.current_schema = parent_schema

    def exit_container(self) -> None:
        """Leave the current container and restore its parent schema."""
        if not self.stack:
            self.invalid = True
            return

        self.stack.pop()

        if not self.stack:
            self.current_schema = self.schema
            return

        parent_schema = self.stack[-1]["schema"]

        if isinstance(parent_schema, ArraySchema):
            self.current_schema = parent_schema.items
        elif isinstance(parent_schema, ObjectSchema):
            self.current_schema = parent_schema

    def valid_key_prefix(self, prefix: str) -> bool:
        """Return whether a prefix can become an unused object property."""
        if not self.stack:
            return False

        frame = self.stack[-1]
        schema = frame["schema"]
        seen_keys = frame["seen_keys"]

        if not isinstance(schema, ObjectSchema):
            return False

        assert seen_keys is not None

        return any(
            property_name.startswith(prefix)
            and property_name not in seen_keys
            for property_name in schema.properties
        )

    def start_key(self) -> None:
        """Begin collecting a property name for the current object."""
        if not self.stack:
            self.invalid = True
            return

        frame = self.stack[-1]

        if not isinstance(frame["schema"], ObjectSchema):
            self.invalid = True
            return

        self.key_buffer = ""

    def add_key_character(self, char: str) -> None:
        """Add one character and validate the resulting key prefix."""
        self.key_buffer += char

        if not self.valid_key_prefix(self.key_buffer):
            self.invalid = True

    def finish_key(self) -> None:
        """Finish a key and switch to the schema for its property value."""
        if not self.stack:
            self.invalid = True
            return

        frame = self.stack[-1]
        schema = frame["schema"]
        seen_keys = frame["seen_keys"]

        if not isinstance(schema, ObjectSchema):
            self.invalid = True
            return

        assert seen_keys is not None

        if self.key_buffer not in schema.properties:
            self.invalid = True
            return

        if self.key_buffer in seen_keys:
            self.invalid = True
            return

        seen_keys.add(self.key_buffer)
        self.current_schema = schema.properties[self.key_buffer]
        self.key_buffer = ""

    def required_keys_satisfied(self) -> bool:
        """Return whether every required property has been generated."""
        if not self.stack:
            return True

        frame = self.stack[-1]
        schema = frame["schema"]
        seen_keys = frame["seen_keys"]

        if not isinstance(schema, ObjectSchema):
            return True

        assert seen_keys is not None

        return set(schema.required).issubset(seen_keys)
