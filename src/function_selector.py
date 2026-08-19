from src.language_model import LanguageModel
from src.tokenizer import Tokenizer
from src.errors import FunctionSelectionError, TokenLimitError


class FunctionNameState:
    """Track whether generated text can still become a valid function name."""

    def __init__(self, function_names: list[str]):
        """Create state for the available function names."""
        self.function_names = function_names
        self.text = ""
        self.invalid = False
        self.complete = False

    def feed(self, text: str) -> None:
        """Add generated text and update validity and completion state."""
        if self.invalid or self.complete:
            return

        self.text += text

        matches = [
            name
            for name in self.function_names
            if name.startswith(self.text)
        ]

        if not matches:
            self.invalid = True
            return

        if self.text in self.function_names:
            longer_matches = [
                name
                for name in matches
                if name != self.text
            ]

            if not longer_matches:
                self.complete = True


def choose_function_name(
    model: LanguageModel,
    tokenizer: Tokenizer,
    token_ids: list[int],
    function_names: list[str],
    max_new_tokens: int = 50,
) -> str:
    """Generate the highest-scoring valid function name token by token."""
    state = FunctionNameState(function_names)
    generated_count = 0

    while not state.complete:
        if generated_count >= max_new_tokens:
            raise TokenLimitError("maximum function-name token limit reached")

        scores = model.next_token_scores(token_ids)

        valid_tokens = []

        for token_id, score in enumerate(scores):
            text = tokenizer.decode([token_id])

            candidate_state = FunctionNameState(function_names)
            candidate_state.text = state.text
            candidate_state.invalid = state.invalid
            candidate_state.complete = state.complete
            candidate_state.feed(text)

            if not candidate_state.invalid:
                valid_tokens.append((token_id, score))

        if not valid_tokens:
            raise FunctionSelectionError(
                "no valid function-name tokens available"
            )

        best_token = max(valid_tokens, key=lambda item: item[1])
        token_id = best_token[0]

        token_ids.append(token_id)
        generated_count += 1

        state.feed(tokenizer.decode([token_id]))

    return state.text
