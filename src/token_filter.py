import copy
import json

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


def current_string_fragment(generated_text: str) -> str:
    """Return the raw contents of the currently open JSON string."""
    in_string = False
    escape_next = False
    fragment = ""

    for char in generated_text:
        if not in_string:
            if char == '"':
                in_string = True
                fragment = ""

            continue

        if escape_next:
            fragment += char
            escape_next = False
            continue

        if char == "\\":
            fragment += char
            escape_next = True
            continue

        if char == '"':
            in_string = False
            fragment = ""
            continue

        fragment += char

    if in_string:
        return fragment

    return ""


def continues_source_text(
    generated_text: str,
    candidate_text: str,
    source_text: str,
) -> bool:
    """Return whether a candidate continues literal text from the source."""
    escaped_source = json.dumps(source_text)[1:-1]
    generated_value = current_string_fragment(generated_text)

    if generated_value == "":
        return False

    maximum = min(
        len(generated_value),
        len(escaped_source),
    )

    for length in range(maximum, 0, -1):
        suffix = generated_value[-length:]

        positions = []
        start = 0

        while True:
            position = escaped_source.find(suffix, start)

            if position == -1:
                break

            positions.append(position)
            start = position + 1

        if not positions:
            continue

        return any(
            escaped_source.startswith(
                candidate_text,
                position + length,
            )
            for position in positions
        )

    return False


def choose_best_valid_token(
    state: ConstrainedState,
    tokenizer: Tokenizer,
    scores: list[float],
    source_text: str | None = None,
    generated_text: str = "",
) -> int:
    """Return the best valid token, preferring source text when available."""
    ranked_token_ids = sorted(
        range(len(scores)),
        key=lambda token_id: scores[token_id],
        reverse=True,
    )

    use_copy_bias = (
        source_text is not None
        and generated_text != ""
        and state.json.in_string
        and state.json.string_role == "value"
    )

    best_valid_token: int | None = None
    valid_checked = 0

    for token_id in ranked_token_ids:
        if not is_valid_token(state, tokenizer, token_id):
            continue

        if best_valid_token is None:
            best_valid_token = token_id

        if not use_copy_bias:
            return token_id

        candidate_text = tokenizer.decode([token_id])

        if (
            source_text is not None
            and ("\\" in candidate_text or '"' in candidate_text)
            and continues_source_text(
                generated_text,
                candidate_text,
                source_text,
            )
        ):
            return token_id

        valid_checked += 1

        if valid_checked >= 64:
            break

    if best_valid_token is None:
        raise NoValidTokenError("no valid tokens available")

    return best_valid_token
