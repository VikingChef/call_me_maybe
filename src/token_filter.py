import copy

from src.constrained_state import ConstrainedState
from src.tokenizer import Tokenizer
from src.errors import NoValidTokenError


def is_valid_continuation(
    state: ConstrainedState,
    text: str,
) -> bool:
    """Return whether text can be added without making the state invalid."""
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
    """Return whether one token is a valid continuation of the state."""
    text = tokenizer.decode([token_id])
    return is_valid_continuation(state, text)


def filter_valid_tokens(
    state: ConstrainedState,
    tokenizer: Tokenizer,
    scores: list[float],
) -> list[tuple[int, float]]:
    """Return every token and score that satisfies the current constraints."""
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
    """Return the highest-scoring token that satisfies the constraints."""
    ranked_token_ids = sorted(
        range(len(scores)),
        key=lambda token_id: scores[token_id],
        reverse=True,
    )

    for token_id in ranked_token_ids:
        if is_valid_token(state, tokenizer, token_id):
            return token_id

    raise NoValidTokenError("no valid tokens available")
