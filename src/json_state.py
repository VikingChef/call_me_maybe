class JSONState:
    """Track whether generated characters still form valid JSON syntax."""

    def __init__(self):
        """Create a fresh JSON parser state."""
        self.stack = []
        self.in_string = False
        self.escape_next = False
        self.complete = False
        self.invalid = False
        self.expecting = "value"
        self.string_role = None
        self.literal_target = None
        self.literal_index = 0
        self.number_buffer = ""

    def number_status(self, text: str) -> tuple[bool, bool]:
        """Return whether text is a valid JSON number prefix
        and a complete number.
        """
        index = 0
        length = len(text)

        if length == 0:
            return False, False

        if text[index] == "-":
            index += 1
            if index == length:
                return True, False

        if text[index] == "0":
            index += 1
            if index < length and text[index].isdigit():
                return False, False

        elif text[index] in "123456789":
            index += 1
            while index < length and text[index].isdigit():
                index += 1

        else:
            return False, False

        if index == length:
            return True, True

        if text[index] == ".":
            index += 1

            if index == length:
                return True, False

            if not text[index].isdigit():
                return False, False

            while index < length and text[index].isdigit():
                index += 1

        if index == length:
            return True, True

        if text[index] in "eE":
            index += 1

            if index == length:
                return True, False

            if text[index] in "+-":
                index += 1
                if index == length:
                    return True, False

            if not text[index].isdigit():
                return False, False

            while index < length and text[index].isdigit():
                index += 1

        if index == length:
            return True, True

        return False, False

    def feed(self, char: str) -> None:
        """Feed one character into the JSON syntax state machine."""
        if self.invalid:
            return

        if self.in_string:
            if self.escape_next:
                self.escape_next = False
                return

            if char == "\\":
                self.escape_next = True
                return

            if char == '"':
                self.in_string = False

                if self.string_role == "key":
                    self.expecting = "colon"
                elif self.string_role == "value":
                    self.expecting = "comma_or_end"

                self.string_role = None
                return

            return

        if self.literal_target is not None:
            if char != self.literal_target[self.literal_index]:
                self.invalid = True
                return

            self.literal_index += 1

            if self.literal_index == len(self.literal_target):
                self.literal_target = None
                self.literal_index = 0
                self.expecting = "comma_or_end"

            return

        if self.number_buffer:
            if char in "0123456789.eE+-":
                self.number_buffer += char
                valid_prefix, _ = self.number_status(self.number_buffer)

                if not valid_prefix:
                    self.invalid = True

                return

            _, complete = self.number_status(self.number_buffer)

            if not complete:
                self.invalid = True
                return

            self.number_buffer = ""
            self.expecting = "comma_or_end"
            self.feed(char)
            return

        if char in "-0123456789":
            if self.expecting not in ("value", "value_or_end"):
                self.invalid = True
                return

            self.number_buffer = char
            valid_prefix, _ = self.number_status(self.number_buffer)

            if not valid_prefix:
                self.invalid = True

            return

        if char in " \t\n\r":
            return

        if char == '"':
            if self.expecting in ("key_or_end", "key"):
                self.string_role = "key"
            elif self.expecting in ("value", "value_or_end"):
                self.string_role = "value"
            else:
                self.invalid = True
                return

            self.in_string = True
            return

        if char in "tfn":
            if self.expecting not in ("value", "value_or_end"):
                self.invalid = True
                return

            if char == "t":
                self.literal_target = "true"
            elif char == "f":
                self.literal_target = "false"
            else:
                self.literal_target = "null"

            self.literal_index = 1
            return

        if char == ":":
            if self.expecting != "colon":
                self.invalid = True
                return

            self.expecting = "value"
            return

        if char == ",":
            if self.expecting != "comma_or_end":
                self.invalid = True
                return

            if not self.stack:
                self.invalid = True
                return

            if self.stack[-1][0] == "{":
                self.expecting = "key"
            else:
                self.expecting = "value"

            return

        if char == "{":
            if self.expecting not in ("value", "value_or_end"):
                self.invalid = True
                return

            self.stack.append(("{", self.expecting))
            self.expecting = "key_or_end"
            return

        if char == "[":
            if self.expecting not in ("value", "value_or_end"):
                self.invalid = True
                return

            self.stack.append(("[", self.expecting))
            self.expecting = "value_or_end"
            return

        if char in "}]":
            if not self.stack:
                self.invalid = True
                return

            if char == "}":
                if self.stack[-1][0] != "{":
                    self.invalid = True
                    return

                if self.expecting not in ("key_or_end", "comma_or_end"):
                    self.invalid = True
                    return

            if char == "]":
                if self.stack[-1][0] != "[":
                    self.invalid = True
                    return

                if self.expecting not in ("value_or_end", "comma_or_end"):
                    self.invalid = True
                    return

            self.stack.pop()

            if not self.stack:
                self.complete = True
            else:
                self.expecting = "comma_or_end"

            return

        self.invalid = True
