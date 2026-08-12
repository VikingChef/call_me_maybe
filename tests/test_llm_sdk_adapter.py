from src.llm_sdk_adapter import LLMSDKAdapter


def test_llm_sdk_adapter() -> None:
    adapter = LLMSDKAdapter()

    token_ids = adapter.encode("Hello")
    assert isinstance(token_ids, list)
    assert token_ids
    assert all(isinstance(token_id, int) for token_id in token_ids)

    decoded = adapter.decode(token_ids)
    assert isinstance(decoded, str)

    scores = adapter.next_token_scores(token_ids)
    assert isinstance(scores, list)
    assert scores
    assert all(isinstance(score, float) for score in scores)
