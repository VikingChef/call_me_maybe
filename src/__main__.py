import argparse
import json
from pathlib import Path

from src.input_loader import (
    load_function_definitions,
    load_prompt_inputs,
)

from src.llm_sdk_adapter import LLMSDKAdapter

from src.function_call_generator import generate_prompt_function_call
from src.language_model import LanguageModel
from src.errors import CallMeMaybeError
from src.models import FunctionDefinition, PromptInput
from src.tokenizer import Tokenizer


def parse_args():
    """Parse command-line arguments for input and output file paths."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
    )
    return parser.parse_args()


def load_inputs(args):
    """Load and validate function definitions and prompt inputs."""
    functions = load_function_definitions(
        args.functions_definition
    )
    prompts = load_prompt_inputs(args.input)

    return functions, prompts


def generate_result(
    model: LanguageModel,
    tokenizer: Tokenizer,
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> dict[str, object]:
    """Generate one output result for a prompt."""
    name, parameters = generate_prompt_function_call(
        model,
        tokenizer,
        prompt,
        functions,
    )

    return {
        "prompt": prompt.prompt,
        "name": name,
        "parameters": parameters,
    }


def generate_results(
    model: LanguageModel,
    tokenizer: Tokenizer,
    prompts: list[PromptInput],
    functions: list[FunctionDefinition],
) -> list[dict[str, object]]:
    """Generate output results for all prompts."""
    return [
        generate_result(
            model,
            tokenizer,
            prompt,
            functions,
        )
        for prompt in prompts
    ]


def write_results(
    output_path,
    results: list[dict[str, object]],
) -> None:
    """Write generated results to the requested JSON output file."""
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(output_path, "w") as file:
        json.dump(
            results,
            file,
            indent=2,
        )


def main() -> None:
    """Run the Call Me Maybe command-line application."""
    try:
        args = parse_args()

        functions, prompts = load_inputs(args)

        adapter = LLMSDKAdapter()

        results = generate_results(
            adapter,
            adapter,
            prompts,
            functions,
        )

        write_results(
            args.output,
            results,
        )

    except CallMeMaybeError as error:
        raise SystemExit(f"Error: {error}") from error


if __name__ == "__main__":
    main()
