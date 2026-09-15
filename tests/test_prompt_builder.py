"""Tests for prompt construction used by both generation stages."""

from src.models import (
    FunctionDefinition,
    ObjectSchema,
    PromptInput,
    StringSchema,
)
from src.prompt_builder import (
    build_model_prompt,
    build_parameter_prompt,
)


def test_build_model_prompt_includes_request_and_function_data() -> None:
    """Include the request and available function metadata in Stage 1."""
    prompt = PromptInput(
        prompt="What is the weather in Berlin?"
    )
    function = FunctionDefinition(
        name="get_weather",
        description="Get weather for a city",
        parameters=ObjectSchema(
            type="object",
            properties={
                "city": StringSchema(type="string"),
            },
            required=["city"],
        ),
        returns=StringSchema(type="string"),
    )

    result = build_model_prompt(
        prompt,
        [function],
    )

    assert "What is the weather in Berlin?" in result
    assert "get_weather" in result
    assert "Get weather for a city" in result
    assert "city" in result
    assert "string" in result
    assert result.endswith("Selected function:")


def test_build_parameter_prompt_uses_only_selected_function() -> None:
    """Build Stage 2 context from only the selected function."""
    prompt = PromptInput(
        prompt="Greet shrek"
    )
    function = FunctionDefinition(
        name="fn_greet",
        description="Generate a greeting message for a person by name.",
        parameters=ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
            },
            required=["name"],
        ),
        returns=StringSchema(type="string"),
    )

    result = build_parameter_prompt(
        prompt,
        function,
    )

    assert "Greet shrek" in result
    assert "fn_greet" in result
    assert "Generate a greeting message for a person by name." in result
    assert '"name"' in result
    assert '"type": "string"' in result
    assert result.endswith("Parameter values:")
