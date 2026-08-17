import json

from pydantic import ValidationError

from src.errors import (
    InputFileError,
    InputJSONError,
    InputValidationError,
)
from src.models import FunctionDefinition, PromptInput


def load_json_file(path):
    try:
        with open(path) as file:
            return json.load(
                file,
                object_pairs_hook=reject_duplicate_keys,
            )
    except json.JSONDecodeError as error:
        raise InputJSONError("invalid JSON") from error
    except OSError as error:
        raise InputFileError(f"cannot read file: {path}") from error


def reject_duplicate_keys(pairs):
    seen = set()
    result = {}
    for key, value in pairs:
        if key in seen:
            raise InputJSONError(f"duplicate key: {key}")
        seen.add(key)
        result[key] = value
    return result


def load_prompt_input(path):
    data = load_json_file(path)

    try:
        return PromptInput.model_validate(data)
    except ValidationError as error:
        raise InputValidationError(
            "invalid prompt input"
        ) from error


def load_prompt_inputs(path):
    data = load_json_file(path)

    if not isinstance(data, list):
        raise InputValidationError(
            "prompt input must be a list"
        )

    try:
        return [
            PromptInput.model_validate(item)
            for item in data
        ]
    except ValidationError as error:
        raise InputValidationError(
            "invalid prompt input"
        ) from error


def load_function_definition(path):
    data = load_json_file(path)

    try:
        return FunctionDefinition.model_validate(data)
    except ValidationError as error:
        raise InputValidationError(
            "invalid function definition"
        ) from error


def load_function_definitions(path):
    data = load_json_file(path)

    if not isinstance(data, list):
        raise InputValidationError(
            "function definitions must be a list"
        )

    try:
        return [
            FunctionDefinition.model_validate(item)
            for item in data
        ]
    except ValidationError as error:
        raise InputValidationError(
            "invalid function definition"
        ) from error
