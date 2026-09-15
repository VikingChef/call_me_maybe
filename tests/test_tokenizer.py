"""Tests for the tokenizer protocol used by the generation pipeline."""

from src.tokenizer import Tokenizer


class FakeTokenizer:
    """Minimal tokenizer implementation used to test the protocol."""

    def encode(self, text: str) -> list[int]:
        """Represent text by a token containing its length."""
        return [len(text)]

    def decode(self, token_ids: list[int]) -> str:
        """Decode the stored length into a repeated placeholder string."""
        return "x" * token_ids[0]


def round_trip_length(tokenizer: Tokenizer, text: str) -> str:
    """Encode and decode text through any compatible tokenizer."""
    token_ids = tokenizer.encode(text)
    return tokenizer.decode(token_ids)


def test_fake_tokenizer_satisfies_protocol() -> None:
    """Accept a compatible tokenizer through the Tokenizer protocol."""
    tokenizer = FakeTokenizer()
    result = round_trip_length(tokenizer, "abc")

    assert result == "xxx"
