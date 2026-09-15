"""Tests for constrained function-name selection."""

from src.errors import FunctionSelectionError, TokenLimitError
from src.function_selector import FunctionNameState, choose_function_name


def test_valid_function_prefix_is_allowed() -> None:
    """Allow prefixes that can still become a valid function name."""
    state = FunctionNameState(
        ["add_numbers", "add_text", "get_weather"]
    )

    state.feed("add_")

    assert state.invalid is False
    assert state.complete is False


def test_exact_function_name_completes() -> None:
    """Mark an exact unambiguous function name as complete."""
    state = FunctionNameState(
        ["add_numbers", "add_text", "get_weather"]
    )

    state.feed("get_weather")

    assert state.invalid is False
    assert state.complete is True


def test_invalid_function_name_is_rejected() -> None:
    """Reject text that cannot match any available function name."""
    state = FunctionNameState(
        ["add_numbers", "add_text", "get_weather"]
    )

    state.feed("banana")

    assert state.invalid is True
    assert state.complete is False


def test_prefix_function_name_does_not_complete_early() -> None:
    """Avoid completing while a longer valid function name remains possible."""
    state = FunctionNameState(
        ["get", "get_weather"]
    )

    state.feed("get")

    assert state.invalid is False
    assert state.complete is False


class FakeTokenizer:
    """Minimal tokenizer used by function-selection tests."""

    def encode(self, text: str) -> list[int]:
        """Satisfy the tokenizer protocol for tests that only decode."""
        return []

    def decode(self, token_ids: list[int]) -> str:
        """Decode predefined token IDs into function-name fragments."""
        token_map = {
            0: "banana",
            1: "get_",
            2: "weather",
        }

        return "".join(token_map[token_id] for token_id in token_ids)


class FakeModel:
    """Return deterministic token scores for function-selection tests."""

    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        """Return scores that favor invalid and then valid continuations."""
        if not token_ids:
            return [10.0, 5.0, 0.0]

        return [10.0, 0.0, 5.0]


def test_choose_function_name_filters_invalid_tokens() -> None:
    """Choose the best-scoring token that keeps the name valid."""
    model = FakeModel()
    tokenizer = FakeTokenizer()

    result = choose_function_name(
        model,
        tokenizer,
        [],
        ["get_weather"],
    )

    assert result == "get_weather"


def test_choose_function_name_stops_at_token_limit() -> None:
    """Raise when function-name generation exceeds its token limit."""
    model = FakeModel()
    tokenizer = FakeTokenizer()

    try:
        choose_function_name(
            model,
            tokenizer,
            [],
            ["get_weather"],
            max_new_tokens=1,
        )
    except TokenLimitError as error:
        assert str(error) == "maximum function-name token limit reached"
    else:
        assert False


def test_choose_function_name_raises_when_no_tokens_are_valid() -> None:
    """Raise when no candidate token can continue a valid function name."""
    model = FakeModel()
    tokenizer = FakeTokenizer()

    try:
        choose_function_name(
            model,
            tokenizer,
            [],
            ["send_email"],
        )
    except FunctionSelectionError as error:
        assert str(error) == "no valid function-name tokens available"
    else:
        assert False
