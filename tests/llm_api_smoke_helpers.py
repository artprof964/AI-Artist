from typing import Any

LLM_TEST_RESPONSE_ID = "resp_smoke_123"
LLM_TEST_RESPONSE_CONTENT = "Hello! How can I help you today?"


class RecordingChatCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return {
            "id": LLM_TEST_RESPONSE_ID,
            "model": kwargs["model"],
            "choices": [{"message": {"content": LLM_TEST_RESPONSE_CONTENT}}],
        }


class RecordingLLMClient:
    def __init__(self) -> None:
        self.completions = RecordingChatCompletions()
        self.chat = type("RecordingChat", (), {"completions": self.completions})()
