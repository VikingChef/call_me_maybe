import pytest

from src.errors import (
    InputFileError,
    InputJSONError,
    InputValidationError,
)
from src.input_loader import (
    load_function_definition,
    load_function_definitions,
    load_json_file,
    load_prompt_input,
    load_prompt_inputs,
)


def test_load_json_file_valid(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text('{"prompt": "Hello"}')
    data = load_json_file(file_path)
    assert data == {"prompt": "Hello"}


def test_json_file_malformed(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text('{"prompt": "Hello"')

    with pytest.raises(InputJSONError):
        load_json_file(file_path)


def test_json_file_rejects_duplicate_keys(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text(
        '{"prompt": "Hello", "prompt": "Goodbye"}'
    )
    with pytest.raises(InputJSONError):
        load_json_file(file_path)


def test_loaded_json_can_become_promptinput(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text('{"prompt": "Hello"}')

    prompt = load_prompt_input(file_path)
    assert prompt.prompt == "Hello"


def test_loaded_json_can_become_functiondefinition(tmp_path) -> None:
    file_path = tmp_path / "input.json"

    file_path.write_text(
        """
        {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string"
                    }
                },
                "required": ["city"]
            },
            "returns": {
                "type": "string"
            }
        }
        """
    )
    function = load_function_definition(file_path)
    assert function.name == "get_weather"
    assert function.parameters.properties["city"].type == "string"
    assert function.returns.type == "string"


def test_loaded_json_rejects_invalid_functiondefinition(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text(
        """
        {
            "name": "get_weather",
            "description": "Get weather for a city",
            "returns": {
                "type": "string"
            }
        }
        """
    )
    with pytest.raises(InputValidationError):
        load_function_definition(file_path)


def test_missing_json_file_is_rejected(tmp_path) -> None:
    file_path = tmp_path / "missing.json"

    with pytest.raises(InputFileError):
        load_json_file(file_path)


def test_load_prompt_inputs(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text(
        """
        [
            {"prompt": "Hello"},
            {"prompt": "Goodbye"}
        ]
        """
    )

    prompts = load_prompt_inputs(file_path)

    assert [prompt.prompt for prompt in prompts] == [
        "Hello",
        "Goodbye",
    ]


def test_load_function_definitions(tmp_path) -> None:
    file_path = tmp_path / "functions.json"
    file_path.write_text(
        """
        [
            {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "returns": {
                    "type": "string"
                }
            },
            {
                "name": "get_age",
                "description": "Get an age",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "returns": {
                    "type": "number"
                }
            }
        ]
        """
    )

    functions = load_function_definitions(file_path)

    assert [function.name for function in functions] == [
        "get_weather",
        "get_age",
    ]


def test_prompt_inputs_must_be_list(tmp_path) -> None:
    file_path = tmp_path / "input.json"
    file_path.write_text('{"prompt": "Hello"}')

    with pytest.raises(InputValidationError):
        load_prompt_inputs(file_path)


def test_function_definitions_must_be_list(tmp_path) -> None:
    file_path = tmp_path / "functions.json"
    file_path.write_text(
        """
        {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            },
            "returns": {
                "type": "string"
            }
        }
        """
    )

    with pytest.raises(InputValidationError):
        load_function_definitions(file_path)
