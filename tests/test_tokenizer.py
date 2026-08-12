from src.tokenizer import Tokenizer


class FakeTokenizer:
    def encode(self, text: str) -> list[int]:
        return [len(text)]

    def decode(self, token_ids: list[int]) -> str:
        return "x" * token_ids[0]


def round_trip_length(tokenizer: Tokenizer, text: str) -> str:
    token_ids = tokenizer.encode(text)
    return tokenizer.decode(token_ids)


def test_fake_tokenizer_satisfies_protocol() -> None:
    tokenizer = FakeTokenizer()
    result = round_trip_length(tokenizer, "abc")
    assert result == "xxx"
