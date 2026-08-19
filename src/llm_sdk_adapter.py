from typing import cast

from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]


class LLMSDKAdapter:
    """Adapt the supplied LLM SDK to the interfaces used by this project."""

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        """Create the supplied SDK model using the requested model name."""
        self.model = Small_LLM_Model(model_name)

    def encode(self, text: str) -> list[int]:
        """Encode text and return its token IDs as a plain Python list."""
        token_tensor = self.model.encode(text)
        return cast(list[int], token_tensor[0].tolist())

    def decode(self, token_ids: list[int]) -> str:
        """Decode a list of token IDs back into text."""
        return cast(str, self.model.decode(token_ids))

    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        """Return the model scores for every possible next token."""
        return cast(
            list[float],
            self.model.get_logits_from_input_ids(token_ids),
        )
