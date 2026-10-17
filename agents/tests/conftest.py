from __future__ import annotations

from datetime import datetime, timezone

import pytest

from newsagent.models import Article


class FakeLLM:
    """Returns canned structured outputs and records the prompts it was given."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls: list[tuple[str, str, type]] = []
        self.images: list[bytes | None] = []

    def ask(self, system, prompt, schema, image=None, image_type="image/webp"):
        self.calls.append((system, prompt, schema))
        self.images.append(image)
        return self.responses.pop(0)


def make_article(n: int, outlet: str, leaning: str | None = "center") -> Article:
    return Article(
        url=f"https://{outlet.lower().replace(' ', '')}.example/{n}",
        title=f"Headline {n}",
        outlet=outlet,
        country="Testland",
        leaning=leaning,
        summary=f"Summary {n}",
        published_at=datetime(2026, 10, 16, 5, tzinfo=timezone.utc),
    )


@pytest.fixture
def articles() -> list[Article]:
    return [
        make_article(0, "Left Daily", "left"),
        make_article(1, "Right Times", "right"),
        make_article(2, "Center Wire", "center"),
        make_article(3, "Left Daily", "left"),
    ]
