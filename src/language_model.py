from typing import Protocol


class LanguageModel(Protocol):
    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        ...
