import io

import httpx
import pytest
from PIL import Image

from newsagent.images import HOUSE_STYLE, ImageBrief, SupabaseStorage, add_images, to_webp

from .conftest import FakeLLM


def png(width=1024, height=1024, color=(30, 47, 74)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buf, "PNG")
    return buf.getvalue()


def records(*titles):
    return {"stories": [
        {"slug": f"2026-10-17-story-{i}", "title": t, "topic": "Climate", "region": "Global",
         "dek": "Something happened.", "image_url": None, "image_alt": None}
        for i, t in enumerate(titles)
    ]}


class FakeGenerator:
    def __init__(self, *results):
        self.results = list(results)
        self.prompts: list[str] = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class FakeStore:
    def __init__(self):
        self.saved: dict[str, tuple[bytes, str]] = {}

    def save(self, name, data, content_type):
        self.saved[name] = (data, content_type)
        return f"https://cdn.example/{name}"


def test_to_webp_crops_to_three_by_two():
    out = Image.open(io.BytesIO(to_webp(png(1024, 1024), width=600)))
    assert out.format == "WEBP"
    assert out.size == (600, 400)


def test_add_images_fills_each_story_and_keeps_going_after_a_failure():
    data = records("Treaty signed", "Talks resume", "Plant opens")
    llm = FakeLLM(
        ImageBrief(scene="Waves and a bottle.", alt="A bottle on waves."),
        ImageBrief(scene="A dove over a table.", alt="A dove."),
        ImageBrief(scene="A factory.", alt="A factory."),
    )
    generator = FakeGenerator(png(), RuntimeError("model refused"), png(1536, 1024))
    store = FakeStore()

    assert add_images(data, llm, generator, store) == 2

    first, failed, third = data["stories"]
    assert first["image_url"].startswith("https://cdn.example/2026-10-17-story-0-")
    assert first["image_url"].endswith(".webp")
    assert first["image_alt"] == "A bottle on waves."
    assert failed["image_url"] is None and failed["image_alt"] is None
    assert third["image_alt"] == "A factory."
    assert {ct for _, ct in store.saved.values()} == {"image/webp"}
    # The scene comes from Claude, the style is always appended.
    assert generator.prompts[0] == f"Waves and a bottle.\n\n{HOUSE_STYLE}"
    assert "Headline: Treaty signed" in llm.calls[0][1]


def test_supabase_storage_upserts_and_returns_public_url():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"Key": "story-images/a.webp"})

    store = SupabaseStorage("https://abc.supabase.co/", "sb_secret_x",
                            client=httpx.Client(transport=httpx.MockTransport(handler)))
    url = store.save("a.webp", b"img", "image/webp")

    assert url == "https://abc.supabase.co/storage/v1/object/public/story-images/a.webp"
    sent = requests[0]
    assert sent.method == "POST"
    assert str(sent.url) == "https://abc.supabase.co/storage/v1/object/story-images/a.webp"
    assert sent.headers["x-upsert"] == "true"
    assert sent.headers["content-type"] == "image/webp"
    assert sent.headers["authorization"] == "Bearer sb_secret_x"
    assert sent.content == b"img"


def test_supabase_storage_raises_on_error():
    store = SupabaseStorage(
        "https://abc.supabase.co", "k",
        client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(403))),
    )
    with pytest.raises(httpx.HTTPStatusError):
        store.save("a.webp", b"img", "image/webp")
