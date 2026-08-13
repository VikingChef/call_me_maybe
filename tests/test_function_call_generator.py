from src.function_call_generator import generate_function_call
from src.models import (
    FunctionDefinition,
    NumberSchema,
    ObjectSchema,
)


class FakeTokenizer:
    def decode(self, token_ids: list[int]) -> str:
        token_map = {
            0: "banana",
            1: "get_age",
            2: "{",
            3: '"age"',
            4: ":",
            5: "45",
            6: "}",
        }

        return "".join(token_map[token_id] for token_id in token_ids)


class FakeModel:
    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        score_sets = {
            0: [10.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            1: [0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0],
            2: [0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0],
            3: [0.0, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0],
            4: [0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0],
            5: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0],
        }

        return score_sets[len(token_ids)]


def test_generate_function_call_selects_function_and_parameters() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()

    function = FunctionDefinition(
        name="get_age",
        description="Return an age.",
        parameters=ObjectSchema(
            type="object",
            properties={
                "age": NumberSchema(type="number"),
            },
            required=["age"],
        ),
        returns=NumberSchema(type="number"),
    )

    result = generate_function_call(
        model,
        tokenizer,
        [],
        [function],
    )

    assert result == ("get_age", {"age": 45})
