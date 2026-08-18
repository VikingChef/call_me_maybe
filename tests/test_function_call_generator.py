from src.errors import FunctionSelectionError
from src.function_call_generator import (
    generate_function_call,
    generate_function_call_with_retries,
    generate_prompt_function_call,
)
from src.models import (
    FunctionDefinition,
    NumberSchema,
    ObjectSchema,
    PromptInput,
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


def test_generate_function_call_rejects_empty_function_list() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()

    try:
        generate_function_call(
            model,
            tokenizer,
            [],
            [],
        )
    except ValueError as error:
        assert str(error) == "at least one function definition is required"
    else:
        assert False


def test_generate_function_call_rejects_duplicate_function_names() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()

    function_one = FunctionDefinition(
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

    function_two = FunctionDefinition(
        name="get_age",
        description="Return another age.",
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
        generate_function_call(
            model,
            tokenizer,
            [],
            [function_one, function_two],
        )
    except ValueError as error:
        assert str(error) == "function names must be unique"
    else:
        assert False


def test_generate_function_call_rejects_empty_function_name() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()

    function = FunctionDefinition(
        name="",
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
        generate_function_call(
            model,
            tokenizer,
            [],
            [function],
        )
    except ValueError as error:
        assert str(error) == "function names must not be empty"
    else:
        assert False


def test_generate_prompt_function_call_uses_separate_contexts(
    monkeypatch,
) -> None:
    class PromptTokenizer:
        def encode(self, text: str) -> list[int]:
            if text == "SELECTION":
                return [10]

            if text == "PARAMETERS":
                return [20]

            raise AssertionError(f"unexpected prompt: {text}")

        def decode(self, token_ids: list[int]) -> str:
            if token_ids == [99]:
                return '{"age":45}'

            return ""

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
    prompt = PromptInput(prompt="What age?")

    monkeypatch.setattr(
        "src.function_call_generator.build_model_prompt",
        lambda prompt, functions: "SELECTION",
    )
    monkeypatch.setattr(
        "src.function_call_generator.build_parameter_prompt",
        lambda prompt, function: "PARAMETERS",
    )

    def fake_choose_function_name(
        model,
        tokenizer,
        token_ids,
        function_names,
    ):
        assert token_ids == [10]
        assert function_names == ["get_age"]
        return "get_age"

    monkeypatch.setattr(
        "src.function_call_generator.choose_function_name",
        fake_choose_function_name,
    )

    def fake_generate_constrained_json(
        model,
        tokenizer,
        token_ids,
        schema,
    ):
        assert token_ids == [20]
        assert schema == function.parameters
        token_ids.append(99)

    monkeypatch.setattr(
        "src.function_call_generator.generate_constrained_json",
        fake_generate_constrained_json,
    )

    result = generate_prompt_function_call(
        object(),
        PromptTokenizer(),
        prompt,
        [function],
    )

    assert result == ("get_age", {"age": 45})
