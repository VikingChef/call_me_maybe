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
        f"Available functions:\n{function_text}\n\n"
        f"User request:\n{prompt.prompt}\n\n"
        "Selected function:"
    )


def build_parameter_prompt(
    prompt: PromptInput,
    function: FunctionDefinition,
) -> str:
    """Build the Stage 2 prompt used to generate function parameters."""
    function_context = {
        "name": function.name,
        "description": function.description,
        "parameters": {
            name: {
                "type": schema.type,
            }
            for name, schema in function.parameters.properties.items()
        },
    }

    return (
        "Selected function:\n"
        f"{json.dumps(function_context, indent=2)}\n\n"
        "User request as JSON string:\n"
        f"{json.dumps(prompt.prompt)}\n\n"
        "Extract only the parameter values requested by the user. "
        "Do not include the operation or command prefix. "
        "Preserve the exact characters of values from the user request, "
        "including leading slashes, backslashes, quotes, braces, spaces, "
        "and punctuation.\n\n"
        "Parameter values:"
    )
