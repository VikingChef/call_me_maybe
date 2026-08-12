from src.json_state import JSONState
from src.token_filter import is_valid_json_continuation, is_valid_token


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
