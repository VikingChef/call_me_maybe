from src.function_selector import FunctionNameState, choose_function_name


def test_valid_function_prefix_is_allowed() -> None:
    state = FunctionNameState(
        ["add_numbers", "add_text", "get_weather"]
    )

    state.feed("add_")

    assert state.invalid is False
    assert state.complete is False


def test_exact_function_name_completes() -> None:
    state = FunctionNameState(
        ["add_numbers", "add_text", "get_weather"]
    )

    state.feed("get_weather")

    assert state.invalid is False
    assert state.complete is True


def test_invalid_function_name_is_rejected() -> None:
    state = FunctionNameState(
        ["add_numbers", "add_text", "get_weather"]
    )

    state.feed("banana")

    assert state.invalid is True
    assert state.complete is False


def test_prefix_function_name_does_not_complete_early() -> None:
    state = FunctionNameState(
        ["get", "get_weather"]
    )

    state.feed("get")

    assert state.invalid is False
    assert state.complete is False


class FakeTokenizer:
    def decode(self, token_ids: list[int]) -> str:
        token_map = {
            0: "banana",
            1: "get_",
            2: "weather",
        }

        return "".join(token_map[token_id] for token_id in token_ids)


class FakeModel:
    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        if not token_ids:
            return [10.0, 5.0, 0.0]

        return [10.0, 0.0, 5.0]


def test_choose_function_name_filters_invalid_tokens() -> None:
    model = FakeModel()
    tokenizer = FakeTokenizer()

    result = choose_function_name(
        model,
        tokenizer,
        [],
        ["get_weather"],
    )

    assert result == "get_weather"
