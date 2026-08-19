class CallMeMaybeError(Exception):
    """Base exception for errors raised by Call Me Maybe."""


class GenerationError(CallMeMaybeError):
    """Base exception for failures during constrained generation."""


class NoValidTokenError(GenerationError):
    """Raised when no possible next token satisfies the constraints."""


class TokenLimitError(GenerationError):
    """Raised when generation reaches its maximum token limit."""


class SchemaMismatchError(GenerationError):
    """Raised when generated data does not match the required schema."""


class FunctionSelectionError(CallMeMaybeError):
    """Raised when the model cannot select a valid function."""


class InputError(CallMeMaybeError):
    """Base exception for errors while reading or validating input."""


class InputFileError(InputError):
    """Raised when an input file cannot be read."""


class InputJSONError(InputError):
    """Raised when an input file does not contain valid JSON."""


class InputValidationError(InputError):
    """Raised when parsed input does not match the expected models."""
