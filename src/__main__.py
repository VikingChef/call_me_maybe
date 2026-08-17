import argparse

from src.input_loader import (
    load_function_definitions,
    load_prompt_inputs,
)


def parse_args():
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
    functions = load_function_definitions(
        args.functions_definition
    )
    prompts = load_prompt_inputs(args.input)

    return functions, prompts


if __name__ == "__main__":
    parse_args()
