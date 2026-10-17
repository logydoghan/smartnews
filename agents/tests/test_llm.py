import json

import anthropic
import httpx2
import pytest

from newsagent.llm import ClaudeLLM, LLMError
from newsagent.models import ClusterResult


def fake_client(captured: list, *, text: str, stop_reason: str = "end_turn", stop_details=None):
    def handler(request: httpx2.Request) -> httpx2.Response:
        captured.append(request)
        return httpx2.Response(200, json={
            "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-sonnet-5-5",
            "content": [{"type": "text", "text": text}],
            "stop_reason": stop_reason, "stop_sequence": None, "stop_details": stop_details,
            "usage": {"input_tokens": 10, "output_tokens": 5},
        })

    return anthropic.Anthropic(api_key="test", http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))


VALID = json.dumps({"stories": [{"title": "T", "topic": "Climate", "region": "Global",
                                 "article_ids": [0, 1], "why_it_matters": "W"}]})


def test_ask_sends_schema_and_fallbacks_and_parses():
    captured = []
    llm = ClaudeLLM("claude-sonnet-5-5", fake_client(captured, text=VALID))
    result = llm.ask("system", "prompt", ClusterResult)

    assert result.stories[0].article_ids == [0, 1]
    body = json.loads(captured[0].content)
    assert body["model"] == "claude-sonnet-5-5"
    assert body["fallbacks"] == "default"
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert "server-side-fallback-2026-07-01" in captured[0].headers["anthropic-beta"]


def test_ask_raises_on_refusal():
    llm = ClaudeLLM("m", fake_client([], text="", stop_reason="refusal",
                                     stop_details={"type": "refusal", "category": "general_harms", "explanation": None}))
    with pytest.raises(LLMError, match="general_harms"):
        llm.ask("s", "p", ClusterResult)


def test_ask_raises_on_truncation():
    llm = ClaudeLLM("m", fake_client([], text='{"stories": [', stop_reason="max_tokens"))
    with pytest.raises(LLMError):
        llm.ask("s", "p", ClusterResult)
