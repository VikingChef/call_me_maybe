from src.errors import FunctionSelectionError
from src.function_call_generator import (
    generate_function_call,
    generate_function_call_with_retries,
)
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


class RetryThenSucceedModel:
    def __init__(self):
        self.call_count = 0
        self.success_model = FakeModel()

    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        self.call_count += 1

        if self.call_count == 1:
            return [10.0]

        return self.success_model.next_token_scores(token_ids)


class AlwaysFailModel:
    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        return [10.0]


def test_retry_succeeds_after_first_failure() -> None:
    model = RetryThenSucceedModel()
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

    result = generate_function_call_with_retries(
        model,
        tokenizer,
        [],
        [function],
    )

    assert result == ("get_age", {"age": 45})


def test_repeated_failure_raises_final_error() -> None:
    model = AlwaysFailModel()
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

    try:
        generate_function_call_with_retries(
            model,
            tokenizer,
            [],
            [function],
        )
    except FunctionSelectionError as error:
        assert str(error) == "no valid function-name tokens available"
    else:
        assert False


def test_retry_does_not_change_original_token_ids() -> None:
    model = RetryThenSucceedModel()
    tokenizer = FakeTokenizer()
    token_ids = []

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

    generate_function_call_with_retries(
        model,
        tokenizer,
        token_ids,
        [function],
    )

    assert token_ids == []


def test_retry_rejects_invalid_max_attempts() -> None:
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

    try:
        generate_function_call_with_retries(
            model,
            tokenizer,
            [],
            [function],
            max_attempts=0,
        )
    except ValueError as error:
        assert str(error) == "max_attempts must be at least 1"
    else:
        assert False
