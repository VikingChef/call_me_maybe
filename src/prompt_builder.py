import json

from src.models import FunctionDefinition, PromptInput


def build_model_prompt(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> str:
    """Build the Stage 1 prompt used to select a function."""
    function_lines = []

    for function in functions:
        parameters = ", ".join(
            f"{name}:{schema.type}"
            for name, schema in function.parameters.properties.items()
        )

        function_lines.append(
            f"{function.name}: {function.description}\n"
            f"Parameters: {parameters}"
        )

    function_text = "\n\n".join(function_lines)

    return (
        "Choose the best function for the user's request.\n\n"
        f"User request:\n{prompt.prompt}\n\n"
        f"Available functions:\n{function_text}\n\n"
        "Selected function:"
    )


def build_parameter_prompt(
    prompt: PromptInput,
    function: FunctionDefinition,
) -> str:
    """Build the Stage 2 prompt used to generate function parameters."""
    context = {
        "user_request": prompt.prompt,
        "selected_function": {
            "name": function.name,
            "description": function.description,
            "parameters": {
                name: {
                    "type": schema.type,
                }
                for name, schema in function.parameters.properties.items()
            },
        },
    }

    return (
        f"{json.dumps(context, indent=2)}\n\n"
        "Parameter values:"
    )
