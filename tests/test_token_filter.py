from src.json_state import JSONState
from src.token_filter import (
    choose_best_valid_token,
    filter_valid_tokens,
    is_valid_json_continuation,
    is_valid_token,
)


def test_valid_continuation_is_allowed() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    assert is_valid_json_continuation(state, '"Rasmus"') is True


def test_invalid_continuation_is_rejected() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    assert is_valid_json_continuation(state, '}') is False


def test_candidate_does_not_change_original_state() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    is_valid_json_continuation(state, '"Rasmus"')

    assert state.expecting == "value"
    assert state.in_string is False
    assert state.complete is False


class FakeTokenizer:
    def decode(self, token_ids: list[int]) -> str:
        if token_ids == [1]:
            return '"Rasmus"'
        return "}"


def test_valid_token_is_allowed() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    tokenizer = FakeTokenizer()

    assert is_valid_token(state, tokenizer, 1) is True


def test_invalid_token_is_rejected() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    tokenizer = FakeTokenizer()

    assert is_valid_token(state, tokenizer, 2) is False


def test_filter_valid_tokens_keeps_only_legal_tokens() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    tokenizer = FakeTokenizer()
    scores = [0.1, 2.5, 1.7]

    result = filter_valid_tokens(state, tokenizer, scores)

    assert result == [(1, 2.5)]


def test_choose_best_valid_token_returns_highest_score() -> None:
    state = JSONState()

    for char in '{"name":':
        state.feed(char)

    tokenizer = FakeTokenizer()
    scores = [0.1, 2.5, 1.7]

    result = choose_best_valid_token(state, tokenizer, scores)

    assert result == 1


def test_choose_best_valid_token_raises_when_none_are_valid() -> None:
    state = JSONState()

    for char in '{"name":"Rasmus"}':
        state.feed(char)

    tokenizer = FakeTokenizer()
    scores = [0.1, 2.5, 1.7]

    try:
        choose_best_valid_token(state, tokenizer, scores)
    except ValueError as error:
        assert str(error) == "no valid tokens available"
    else:
        assert False
