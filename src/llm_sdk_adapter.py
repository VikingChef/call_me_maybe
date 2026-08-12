from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]


class LLMSDKAdapter:
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        self.model = Small_LLM_Model(model_name)

    def encode(self, text: str) -> list[int]:
        token_tensor = self.model.encode(text)
        return token_tensor[0].tolist()

    def decode(self, token_ids: list[int]) -> str:
        return self.model.decode(token_ids)

    def next_token_scores(self, token_ids: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(token_ids)
