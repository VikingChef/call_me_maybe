import sys
import json

from src.__main__ import (
    generate_result,
    generate_results,
    load_inputs,
    main,
    parse_args,
    write_results,
)

from src.models import (
    FunctionDefinition,
    ObjectSchema,
    PromptInput,
    StringSchema,
)


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


def test_generate_result() -> None:
    class FakeModel:
        def __init__(self) -> None:
            self.call_count = 0

        def next_token_scores(self, token_ids: list[int]) -> list[float]:
            self.call_count += 1

            if self.call_count == 1:
                return [1.0, 0.0]

            return [0.0, 1.0]

    class FakeTokenizer:
        def encode(self, text: str) -> list[int]:
            return [1, 2, 3]

        def decode(self, token_ids: list[int]) -> str:
            if token_ids == [0]:
                return "get_weather"
            if token_ids == [1]:
                return "{}"
            return ""

    prompt = PromptInput(
        prompt="What is the weather in Berlin?"
    )
    functions = [
        FunctionDefinition(
            name="get_weather",
            description="Get weather for a city",
            parameters=ObjectSchema(
                type="object",
                properties={},
                required=[],
            ),
            returns=StringSchema(type="string"),
        )
    ]

    result = generate_result(
        FakeModel(),
        FakeTokenizer(),
        prompt,
        functions,
    )

    assert result == {
        "prompt": "What is the weather in Berlin?",
        "name": "get_weather",
        "parameters": {},
    }


def test_generate_results(monkeypatch) -> None:
    prompts = [
        PromptInput(prompt="First prompt"),
        PromptInput(prompt="Second prompt"),
    ]
    functions = [
        FunctionDefinition(
            name="test_function",
            description="Test function",
            parameters=ObjectSchema(
                type="object",
                properties={},
                required=[],
            ),
            returns=StringSchema(type="string"),
        )
    ]

    def fake_generate_result(
        model,
        tokenizer,
        prompt,
        functions,
    ):
        return {
            "prompt": prompt.prompt,
            "name": "test_function",
            "parameters": {},
        }

    monkeypatch.setattr(
        "src.__main__.generate_result",
        fake_generate_result,
    )

    results = generate_results(
        object(),
        object(),
        prompts,
        functions,
    )

    assert results == [
        {
            "prompt": "First prompt",
            "name": "test_function",
            "parameters": {},
        },
        {
            "prompt": "Second prompt",
            "name": "test_function",
            "parameters": {},
        },
    ]


def test_write_results(tmp_path) -> None:
    output_path = tmp_path / "results.json"
    results = [
        {
            "prompt": "Hello",
            "name": "greet",
            "parameters": {},
        }
    ]

    write_results(
        output_path,
        results,
    )

    assert json.loads(output_path.read_text()) == results


def test_main_wires_pipeline(monkeypatch) -> None:
    class Args:
        functions_definition = "functions.json"
        input = "prompts.json"
        output = "results.json"

    functions = [object()]
    prompts = [object()]
    adapter = object()
    results = [{"prompt": "Hello", "name": "greet", "parameters": {}}]

    monkeypatch.setattr(
        "src.__main__.parse_args",
        lambda: Args(),
    )
    monkeypatch.setattr(
        "src.__main__.load_inputs",
        lambda args: (functions, prompts),
    )
    monkeypatch.setattr(
        "src.__main__.LLMSDKAdapter",
        lambda: adapter,
    )
    monkeypatch.setattr(
        "src.__main__.generate_results",
        lambda model, tokenizer, loaded_prompts, loaded_functions: results,
    )

    written = {}

    def fake_write_results(output_path, generated_results) -> None:
        written["output_path"] = output_path
        written["results"] = generated_results

    monkeypatch.setattr(
        "src.__main__.write_results",
        fake_write_results,
    )

    main()

    assert written == {
        "output_path": "results.json",
        "results": results,
    }


def test_write_results_creates_missing_output_directory(tmp_path) -> None:
    output_path = tmp_path / "output" / "results.json"
    results = [
        {
            "prompt": "Hello",
            "name": "greet",
            "parameters": {},
        }
    ]

    write_results(
        output_path,
        results,
    )

    assert json.loads(output_path.read_text()) == results
