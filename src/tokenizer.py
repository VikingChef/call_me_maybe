from typing import Protocol


class Tokenizer(Protocol):
    """Define the tokenizer interface used by the generation pipeline."""

    def encode(self, text: str) -> list[int]:
        """Convert text into a list of token IDs."""
        ...

    def decode(self, token_ids: list[int]) -> str:
        """Convert token IDs back into text."""
        ...
