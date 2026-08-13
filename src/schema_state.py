from src.models import (
    ArraySchema,
    BooleanSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
)


class SchemaState:
    def __init__(self, schema):
        self.schema = schema
        self.current_schema = schema
        self.stack = []
        self.key_buffer = ""
        self.invalid = False

    def valid_value_starts(self) -> set[str]:
        schema = self.current_schema

        if isinstance(schema, StringSchema):
            return {'"'}

        if isinstance(schema, NumberSchema):
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
        if not self.stack:
            return False

        frame = self.stack[-1]
        schema = frame["schema"]
        seen_keys = frame["seen_keys"]

        if not isinstance(schema, ObjectSchema):
            return False

        return any(
            property_name.startswith(prefix)
            and property_name not in seen_keys
            for property_name in schema.properties
        )

    def start_key(self) -> None:
        if not self.stack:
            self.invalid = True
            return

        frame = self.stack[-1]

        if not isinstance(frame["schema"], ObjectSchema):
            self.invalid = True
            return

        self.key_buffer = ""

    def add_key_character(self, char: str) -> None:
        self.key_buffer += char

        if not self.valid_key_prefix(self.key_buffer):
            self.invalid = True

    def finish_key(self) -> None:
        if not self.stack:
            self.invalid = True
            return

        frame = self.stack[-1]
        schema = frame["schema"]
        seen_keys = frame["seen_keys"]

        if not isinstance(schema, ObjectSchema):
            self.invalid = True
            return

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
        if not self.stack:
            return True

        frame = self.stack[-1]
        schema = frame["schema"]
        seen_keys = frame["seen_keys"]

        if not isinstance(schema, ObjectSchema):
            return True

        return set(schema.required).issubset(seen_keys)
