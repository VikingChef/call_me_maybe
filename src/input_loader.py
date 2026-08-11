import json

from src.models import FunctionDefinition, PromptInput


def load_json_file(path):
    with open(path) as file:
        data = json.load(file, object_pairs_hook=reject_duplicate_keys)
    return data


def reject_duplicate_keys(pairs):
    seen = set()
    result = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key: {key}")
        seen.add(key)
        result[key] = value
    return result


def load_prompt_input(path):
    data = load_json_file(path)
    return PromptInput.model_validate(data)


def load_function_definition(path):
    data = load_json_file(path)
    return FunctionDefinition.model_validate(data)
