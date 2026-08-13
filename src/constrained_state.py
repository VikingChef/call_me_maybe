from src.json_state import JSONState
from src.schema_state import SchemaState


class ConstrainedState:
    def __init__(self, schema):
        self.json = JSONState()
        self.schema = SchemaState(schema)
        self.invalid = False

    @property
    def complete(self) -> bool:
        return self.json.complete

    def feed(self, char: str) -> None:
        if self.invalid:
            return

        was_in_string = self.json.in_string
        string_role = self.json.string_role
        escape_next = self.json.escape_next
        expecting = self.json.expecting
        had_literal = self.json.literal_target is not None
        had_number = bool(self.json.number_buffer)

        if not was_in_string and not had_literal and not had_number:
            if expecting in ("value", "value_or_end"):
                if char not in " \t\n\r]}":
                    if char not in self.schema.valid_value_starts():
                        self.invalid = True
                        return

                if char == "{":
                    self.schema.enter_object()

                elif char == "[":
                    self.schema.enter_array()

            elif expecting in ("key_or_end", "key") and char == '"':
                self.schema.start_key()

        if was_in_string and string_role == "key":
            if escape_next:
                self.schema.add_key_character(char)

            elif char == "\\":
                pass

            elif char == '"':
                self.schema.finish_key()

            else:
                self.schema.add_key_character(char)

            if self.schema.invalid:
                self.invalid = True
                return

        if (
            char == "}"
            and not was_in_string
            and not self.schema.required_keys_satisfied()
        ):
            self.invalid = True
            return

        self.json.feed(char)

        if self.json.invalid:
            self.invalid = True
            return

        if (
            was_in_string
            and string_role == "value"
            and not escape_next
            and char == '"'
        ):
            self.schema.finish_value()

        if had_literal and self.json.literal_target is None:
            self.schema.finish_value()

        if had_number and not self.json.number_buffer:
            self.schema.finish_value()

        if char in "}]" and not was_in_string:
            self.schema.exit_container()

        if self.schema.invalid:
            self.invalid = True
