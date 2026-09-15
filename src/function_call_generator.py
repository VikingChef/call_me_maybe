"""Generate schema-valid function calls from model output."""

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
from src.models import (
    ArraySchema,
    FunctionDefinition,
    IntegerSchema,
    NumberSchema,
    ObjectSchema,
    PromptInput,
    StringSchema,
)
from src.prompt_builder import (
    build_model_prompt,
    build_parameter_prompt,
)
from src.tokenizer import Tokenizer


def normalize_generated_value(
    value: object,
    schema: object,
) -> object:
    """Normalize generated values according to their parameter schema."""
    if isinstance(schema, NumberSchema):
        if isinstance(value, int) and not isinstance(value, bool):
            return float(value)

        return value

    if isinstance(schema, IntegerSchema):
        return value

    if isinstance(schema, ArraySchema):
        if not isinstance(value, list):
            return value

        return [
            normalize_generated_value(item, schema.items)
            for item in value
        ]

    if isinstance(schema, ObjectSchema):
        if not isinstance(value, dict):
            return value

        return {
            key: normalize_generated_value(
                item,
                schema.properties[key],
            )
            if key in schema.properties
            else item
            for key, item in value.items()
        }

    return value


def preserve_explicit_string_parameter(
    prompt: PromptInput,
    function: FunctionDefinition,
    parameters: dict,
) -> dict:
    """Preserve a single explicit string value supplied after a colon."""
    properties = function.parameters.properties

    if len(properties) != 1:
        return parameters

    parameter_name, schema = next(iter(properties.items()))

    if not isinstance(schema, StringSchema):
        return parameters

    if ":" not in prompt.prompt:
        return parameters

    value = prompt.prompt.split(":", 1)[1].strip()

    if value == "":
        return parameters

    parameters[parameter_name] = value

    return parameters


def generate_function_call(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    functions: list[FunctionDefinition],
) -> tuple[str, dict]:
    """Generate a function name and schema-valid parameter object."""
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
    parameters = normalize_generated_value(
        parameters,
        selected_function.parameters,
    )

    if not isinstance(parameters, dict):
        raise SchemaMismatchError("generated parameters are not an object")

    return selected_name, parameters


def generate_function_call_with_retries(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    functions: list[FunctionDefinition],
    max_attempts: int = 3,
) -> tuple[str, dict]:
    """Retry token-based generation after recoverable generation errors."""
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
    """Select a function, then generate its schema-valid parameters."""
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
    parameters = normalize_generated_value(
        parameters,
        selected_function.parameters,
    )

    if not isinstance(parameters, dict):
        raise SchemaMismatchError("generated parameters are not an object")

    parameters = preserve_explicit_string_parameter(
        prompt,
        selected_function,
        parameters,
    )

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
