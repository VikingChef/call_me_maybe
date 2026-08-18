from src.models import FunctionDefinition, PromptInput


def build_model_prompt(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> str:
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
    parameters = ", ".join(
        f"{name}:{schema.type}"
        for name, schema in function.parameters.properties.items()
    )

    return (
        f"User request:\n{prompt.prompt}\n\n"
        "Selected function:\n"
        f"{function.name}: {function.description}\n"
        f"Parameters: {parameters}\n\n"
        "Parameter values:"
    )
