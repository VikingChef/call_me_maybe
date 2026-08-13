from src.errors import (
    CallMeMaybeError,
    FunctionSelectionError,
    GenerationError,
    NoValidTokenError,
    SchemaMismatchError,
    TokenLimitError,
)


def test_generation_errors_share_base_class() -> None:
    assert issubclass(GenerationError, CallMeMaybeError)
    assert issubclass(NoValidTokenError, GenerationError)
    assert issubclass(TokenLimitError, GenerationError)
    assert issubclass(SchemaMismatchError, GenerationError)


def test_function_selection_error_uses_project_base() -> None:
    assert issubclass(FunctionSelectionError, CallMeMaybeError)
