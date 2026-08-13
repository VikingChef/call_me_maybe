import copy

from src.constrained_state import ConstrainedState
from src.tokenizer import Tokenizer


def is_valid_continuation(
    state: ConstrainedState,
    text: str,
) -> bool:
    candidate_state = copy.deepcopy(state)

    for char in text:
        candidate_state.feed(char)

        if candidate_state.invalid:
            return False

    return True


def is_valid_token(
    state: ConstrainedState,
    tokenizer: Tokenizer,
    token_id: int,
) -> bool:
    text = tokenizer.decode([token_id])
    return is_valid_continuation(state, text)


def filter_valid_tokens(
    state: ConstrainedState,
    tokenizer: Tokenizer,
    scores: list[float],
) -> list[tuple[int, float]]:
    valid_tokens = []

    for token_id, score in enumerate(scores):
        if is_valid_token(state, tokenizer, token_id):
            valid_tokens.append((token_id, score))

    return valid_tokens


def choose_best_valid_token(
    state: ConstrainedState,
    tokenizer: Tokenizer,
    scores: list[float],
) -> int:
    valid_tokens = filter_valid_tokens(state, tokenizer, scores)

    if not valid_tokens:
        raise ValueError("no valid tokens available")

    best_token = max(valid_tokens, key=lambda item: item[1])
    token_id = best_token[0]

    return token_id
