"""Tests for the project's custom exception hierarchy."""

from src.errors import (
    CallMeMaybeError,
    FunctionSelectionError,
    GenerationError,
    InputError,
    InputFileError,
    InputJSONError,
    InputValidationError,
    NoValidTokenError,
    SchemaMismatchError,
    TokenLimitError,
)


def test_generation_errors_share_base_class() -> None:
    """Ensure constrained-generation errors share the generation base."""
    assert issubclass(GenerationError, CallMeMaybeError)
    assert issubclass(NoValidTokenError, GenerationError)
    assert issubclass(TokenLimitError, GenerationError)
    assert issubclass(SchemaMismatchError, GenerationError)


def test_function_selection_error_uses_project_base() -> None:
    """Ensure function-selection failures use the project base error."""
    assert issubclass(FunctionSelectionError, CallMeMaybeError)


def test_input_errors_share_base_class() -> None:
    """Ensure input failures share the input-error hierarchy."""
    assert issubclass(InputError, CallMeMaybeError)
    assert issubclass(InputFileError, InputError)
    assert issubclass(InputJSONError, InputError)
    assert issubclass(InputValidationError, InputError)
