import json

from src.errors import (
    FunctionSelectionError,
    NoValidTokenError,
    SchemaMismatchError,
    TokenLimitError,
)
from src.constrained_decoder import generate_constrained_json
from src.function_selector import choose_function_name
from src.language_model import LanguageModel
from src.models import FunctionDefinition, PromptInput
from src.prompt_builder import (
    build_model_prompt,
    build_parameter_prompt,
)
from src.tokenizer import Tokenizer


def generate_function_call(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    functions: list[FunctionDefinition],
) -> tuple[str, dict]:
    """Generate a function name and schema-valid parameters from token IDs."""
    if not functions:
        raise ValueError("at least one function definition is required")

    function_names = [function.name for function in functions]

    if len(function_names) != len(set(function_names)):
        raise ValueError("function names must be unique")

    if any(name == "" for name in function_names):
        raise ValueError("function names must not be empty")

    selected_name = choose_function_name(
        model,
        tokenizer,
        token_ids,
        function_names,
    )

    selected_function = next(
        function
        for function in functions
        if function.name == selected_name
    )

    parameter_start = len(token_ids)

    generate_constrained_json(
        model,
        tokenizer,
        token_ids,
        selected_function.parameters,
    )

    parameter_token_ids = token_ids[parameter_start:]
    parameter_text = tokenizer.decode(parameter_token_ids)
    parameters = json.loads(parameter_text)

    return selected_name, parameters


def generate_function_call_with_retries(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    functions: list[FunctionDefinition],
    max_attempts: int = 3,
) -> tuple[str, dict]:
    """Retry function-call generation after recoverable generation errors."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    retryable_errors = (
        FunctionSelectionError,
        NoValidTokenError,
        SchemaMismatchError,
        TokenLimitError,
    )

    last_error = None

    for _ in range(max_attempts):
        attempt_token_ids = token_ids.copy()

        try:
            return generate_function_call(
                model,
                tokenizer,
                attempt_token_ids,
                functions,
            )
        except retryable_errors as error:
            last_error = error

    assert last_error is not None
    raise last_error


def generate_prompt_function_call(
    model: LanguageModel,
    tokenizer: Tokenizer,
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> tuple[str, dict]:
    """Generate a function call in separate selection and parameter stages."""
    selection_prompt = build_model_prompt(
        prompt,
        functions,
    )
    selection_token_ids = tokenizer.encode(selection_prompt)

    function_names = [function.name for function in functions]

    selected_name = choose_function_name(
        model,
        tokenizer,
        selection_token_ids,
        function_names,
    )

    selected_function = next(
        function
        for function in functions
        if function.name == selected_name
    )

    parameter_prompt = build_parameter_prompt(
        prompt,
        selected_function,
    )
    parameter_token_ids = tokenizer.encode(parameter_prompt)
    parameter_start = len(parameter_token_ids)

    generate_constrained_json(
        model,
        tokenizer,
        parameter_token_ids,
        selected_function.parameters,
    )

    generated_parameter_ids = parameter_token_ids[parameter_start:]
    parameter_text = tokenizer.decode(generated_parameter_ids)
    parameters = json.loads(parameter_text)

    return selected_name, parameters


def generate_prompt_function_call_with_retries(
    model: LanguageModel,
    tokenizer: Tokenizer,
    prompt: PromptInput,
    functions: list[FunctionDefinition],
    max_attempts: int = 3,
) -> tuple[str, dict]:
    """Retry prompt-aware generation after recoverable generation errors."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    retryable_errors = (
        FunctionSelectionError,
        NoValidTokenError,
        SchemaMismatchError,
        TokenLimitError,
    )

    last_error = None

    for _ in range(max_attempts):
        try:
            return generate_prompt_function_call(
                model,
                tokenizer,
                prompt,
                functions,
            )
        except retryable_errors as error:
            last_error = error

    assert last_error is not None
    raise last_error
