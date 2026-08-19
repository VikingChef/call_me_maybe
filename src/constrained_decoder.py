from src.generated_output import generated_json_matches_schema
from src.constrained_state import ConstrainedState
from src.language_model import LanguageModel
from src.token_filter import choose_best_valid_token
from src.tokenizer import Tokenizer
from src.errors import SchemaMismatchError, TokenLimitError
from src.schema_state import Schema


def generate_constrained_json(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    schema: Schema,
    max_new_tokens: int = 100,
) -> list[int]:
    """Generate schema-valid JSON by choosing one valid token at a time."""
    state = ConstrainedState(schema)
    generated_token_ids = []
    generated_count = 0

    while not state.complete:
        if generated_count >= max_new_tokens:
            raise TokenLimitError("maximum token limit reached")

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
        raise SchemaMismatchError("generated JSON does not match schema")

    return token_ids
