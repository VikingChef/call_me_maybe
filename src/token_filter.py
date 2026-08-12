import copy

from src.json_state import JSONState
from src.tokenizer import Tokenizer


def is_valid_json_continuation(state: JSONState, text: str) -> bool:
    candidate_state = copy.deepcopy(state)

    for char in text:
        candidate_state.feed(char)

        if candidate_state.invalid:
            return False

    return True


def is_valid_token(
    state: JSONState,
    tokenizer: Tokenizer,
    token_id: int,
) -> bool:
    text = tokenizer.decode([token_id])
    return is_valid_json_continuation(state, text)
