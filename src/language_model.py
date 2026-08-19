from typing import Protocol


class LanguageModel(Protocol):
    """Define the language-model interface used during generation."""

    def next_token_scores(
        self,
        token_ids: list[int],
    ) -> list[float]:
        """Return model scores for the next possible token IDs."""
        ...
