"""Thin wrapper around the Claude API for structured (pydantic) responses."""

from __future__ import annotations

import base64
import logging
from typing import Protocol, TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


class StructuredLLM(Protocol):
    def ask(self, system: str, prompt: str, schema: type[T], image: bytes | None = None) -> T:
        """Answer in the schema's shape; `image` (WebP bytes) is shown before the prompt."""
        ...


class ClaudeLLM:
    def __init__(self, model: str, client: anthropic.Anthropic | None = None) -> None:
        self.model = model
        self.client = client or anthropic.Anthropic()

    def ask(self, system: str, prompt: str, schema: type[T], image: bytes | None = None) -> T:
        content: str | list[dict] = prompt
        if image is not None:
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/webp",
                        "data": base64.b64encode(image).decode(),
                    },
                },
                {"type": "text", "text": prompt},
            ]
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=16000,
                system=system,
                messages=[{"role": "user", "content": content}],
                output_config={
                    "format": {
                        "type": "json_schema",
                        "schema": anthropic.transform_schema(schema.model_json_schema()),
                    }
                },
                # If a safety classifier declines, retry server-side on the recommended model.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except anthropic.RateLimitError as exc:
            raise LLMError(f"Rate limited by the Claude API: {exc.message}") from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Claude API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError("Could not reach the Claude API") from exc

        if response.stop_reason == "refusal":
            category = response.stop_details.category if response.stop_details else None
            raise LLMError(f"Claude declined the request (category: {category})")
        if response.stop_reason == "max_tokens":
            raise LLMError("Claude's response was cut off at max_tokens")
        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise LLMError("Claude returned no structured output")
        log.debug("Claude usage: %s", response.usage)
        try:
            return schema.model_validate_json(text)
        except ValidationError as exc:
            raise LLMError(f"Claude's output did not match {schema.__name__}: {exc}") from exc
