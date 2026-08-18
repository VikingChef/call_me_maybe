from src.models import (
    FunctionDefinition,
    ObjectSchema,
    PromptInput,
    StringSchema,
)
from src.prompt_builder import build_model_prompt


def test_build_model_prompt_includes_request_and_function_data() -> None:
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
