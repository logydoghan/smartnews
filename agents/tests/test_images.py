import json

import httpx
import pytest

from newsagent.config import Settings
from newsagent.images import (
    HOUSE_STYLE,
    ImageBrief,
    ImageCheck,
    ImageRejected,
    RecraftGenerator,
    SupabaseStorage,
    add_images,
    image_type,
    make_generator,
)

from .conftest import FakeLLM

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def webp(n: int = 0) -> bytes:
    return b"RIFF\x00\x00\x00\x00WEBPVP8 " + bytes([n]) * 16


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


def test_image_type_reads_magic_bytes():
    assert image_type(webp()) == "image/webp"
    assert image_type(PNG) == "image/png"
    assert image_type(b"\xff\xd8\xff\xe0rest") == "image/jpeg"
    with pytest.raises(ImageRejected):
        image_type(b"<html>error</html>")


OK = ImageCheck(has_text=False, looks_like_photo=False, shows_real_person=False, problem="")
HAS_TEXT = ImageCheck(has_text=True, looks_like_photo=False, shows_real_person=False,
                      problem="lettering on the sign")


def test_add_images_fills_each_story_and_keeps_going_after_a_failure():
    data = records("Treaty signed", "Talks resume", "Plant opens")
    llm = FakeLLM(
        ImageBrief(scene="Waves and a bottle.", alt="A bottle on waves."), OK,
        ImageBrief(scene="A dove over a table.", alt="A dove."),
        ImageBrief(scene="A factory.", alt="A factory."), OK,
    )
    generator = FakeGenerator(webp(1), RuntimeError("model refused"), PNG)
    store = FakeStore()

    assert add_images(data, llm, generator, store) == 2

    first, failed, third = data["stories"]
    assert first["image_url"].startswith("https://cdn.example/2026-10-17-story-0-")
    assert first["image_url"].endswith(".webp")
    assert first["image_alt"] == "A bottle on waves."
    assert failed["image_url"] is None and failed["image_alt"] is None
    assert third["image_url"].endswith(".png")
    assert third["image_alt"] == "A factory."
    # Files are stored exactly as the image service made them.
    assert sorted(store.saved.values()) == sorted([(webp(1), "image/webp"), (PNG, "image/png")])
    # The scene comes from Claude, the style is always appended.
    assert generator.prompts[0] == f"Waves and a bottle.\n\n{HOUSE_STYLE}"
    assert "Headline: Treaty signed" in llm.calls[0][1]
    # Claude looks at the finished WebP before it is saved.
    assert llm.calls[1][2] is ImageCheck
    assert llm.images[1] == store.saved[first["image_url"].rsplit("/", 1)[1]][0]


def test_rejected_image_is_redrawn_once_then_dropped():
    data = records("Redrawn", "Never passes")
    llm = FakeLLM(
        ImageBrief(scene="A sign.", alt="A sign."), HAS_TEXT, OK,
        ImageBrief(scene="A poster.", alt="A poster."), HAS_TEXT, HAS_TEXT,
    )
    generator = FakeGenerator(webp(1), webp(2), webp(3), webp(4))
    store = FakeStore()

    assert add_images(data, llm, generator, store) == 1

    redrawn, dropped = data["stories"]
    assert redrawn["image_alt"] == "A sign."
    assert "Avoid: lettering on the sign" in generator.prompts[1]
    assert dropped["image_url"] is None
    assert len(store.saved) == 1


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


def test_recraft_generator_requests_a_landscape_image_and_downloads_it():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.host == "external.api.recraft.ai":
            return httpx.Response(200, json={"data": [{"url": "https://img.recraft.ai/abc.webp"}]})
        return httpx.Response(200, content=webp(7))

    generator = RecraftGenerator("rk", style_id="style-1",
                                 client=httpx.Client(transport=httpx.MockTransport(handler)))

    assert generator.generate("A dove.") == webp(7)
    create, download = requests
    assert create.headers["authorization"] == "Bearer rk"
    assert json.loads(create.content) == {
        "prompt": "A dove.", "model": "recraftv4_1", "size": "3:2", "style_id": "style-1",
    }
    assert str(download.url) == "https://img.recraft.ai/abc.webp"


def test_recraft_generator_raises_on_api_error():
    generator = RecraftGenerator(
        "rk", client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(402)))
    )
    with pytest.raises(httpx.HTTPStatusError):
        generator.generate("A dove.")


def test_make_generator_needs_a_recraft_key():
    assert make_generator(Settings()) is None
    generator = make_generator(Settings(recraft_api_key="rk", image_model="recraftv4_1_flash"))
    assert isinstance(generator, RecraftGenerator)
    assert generator.model == "recraftv4_1_flash"
