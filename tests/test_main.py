import sys

from src.__main__ import load_inputs, parse_args


def test_parse_args_uses_default_paths(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["src"])

    args = parse_args()

    assert args.functions_definition == (
        "data/input/functions_definition.json"
    )
    assert args.input == "data/input/function_calling_tests.json"
    assert args.output == "data/output/function_calling_results.json"


def test_parse_args_accepts_custom_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "src",
            "--functions_definition",
            "custom/functions.json",
            "--input",
            "custom/prompts.json",
            "--output",
            "custom/results.json",
        ],
    )

    args = parse_args()

    assert args.functions_definition == "custom/functions.json"
    assert args.input == "custom/prompts.json"
    assert args.output == "custom/results.json"


def test_load_inputs(tmp_path) -> None:
    functions_path = tmp_path / "functions.json"
    prompts_path = tmp_path / "prompts.json"

    functions_path.write_text(
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
            }
        ]
        """
    )

    prompts_path.write_text(
        """
        [
            {"prompt": "What is the weather?"}
        ]
        """
    )

    class Args:
        functions_definition = functions_path
        input = prompts_path

    functions, prompts = load_inputs(Args())

    assert functions[0].name == "get_weather"
    assert prompts[0].prompt == "What is the weather?"
