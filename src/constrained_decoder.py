from src.generated_output import generated_json_matches_schema
from src.constrained_state import ConstrainedState
from src.language_model import LanguageModel
from src.token_filter import choose_best_valid_token
from src.tokenizer import Tokenizer


def generate_constrained_json(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    schema,
    max_new_tokens: int = 100,
) -> list[int]:
    state = ConstrainedState(schema)
    generated_token_ids = []
    generated_count = 0

    while not state.complete:
        if generated_count >= max_new_tokens:
            raise RuntimeError("maximum token limit reached")

        scores = model.next_token_scores(token_ids)
        token_id = choose_best_valid_token(state, tokenizer, scores)

        token_ids.append(token_id)
        generated_token_ids.append(token_id)
        generated_count += 1

        text = tokenizer.decode([token_id])
        for char in text:
            state.feed(char)

    generated_text = tokenizer.decode(generated_token_ids)

    if not generated_json_matches_schema(generated_text, schema):
        raise ValueError("generated JSON does not match schema")

    return token_ids
