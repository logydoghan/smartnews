"""Image agent: one AI illustration per story, saved to Supabase Storage.

Claude writes a short scene description for each story, an image model draws it in the
site's house style, Claude looks at the result to catch text, photo-like images and real
faces, and the image is stored as WebP in a public bucket. Illustrations are deliberately
not photo-like, so no one mistakes them for pictures of the real event.
"""

from __future__ import annotations

import hashlib
import io
import logging
from typing import Protocol

import httpx
from pydantic import BaseModel, Field

from .llm import StructuredLLM

log = logging.getLogger(__name__)

BUCKET = "story-images"
WIDTH = 1536  # pixels; images are 3:2 landscape
WEBP_QUALITY = 80
ATTEMPTS = 2  # a rejected image is redrawn once before the story goes without one

# Added to every scene so the front page reads as one set.
HOUSE_STYLE = (
    "Style: flat editorial illustration with a subtle paper-print texture, simple bold shapes "
    "and a limited palette of deep navy, warm off-white, muted brick red, slate blue-grey and a "
    "little ochre. Not a photograph and not photorealistic. No text, letters, numbers, logos or "
    "watermarks anywhere. No recognizable real people; any figures are small, faceless and generic."
)

SYSTEM = """You brief an illustrator for a world news website. Given one news story, describe \
a single symbolic scene that conveys its subject at a glance.

Rules:
- Show places, objects, symbols or small anonymous figures. Never depict a specific real \
person, and never stage the event as if it were a photo of what happened.
- No violence, injuries, bodies or weapons in use. For conflict or disaster stories, use \
calm symbols such as an empty table, a damaged bridge, a dove or a map outline.
- No text, signs with writing, logos, flags or national emblems.
- Describe only the subject and composition; the drawing style is added separately.
- Keep the scene under 60 words."""


CHECK_SYSTEM = """You check illustrations before they appear on a news website. Look at the \
whole image closely, including small details and backgrounds, and answer honestly."""

CHECK_PROMPT = "Does this illustration break any of the site's rules?"


class ImageBrief(BaseModel):
    scene: str = Field(description="What to draw, under 60 words, without style words.")
    alt: str = Field(description="One sentence describing the illustration for screen readers.")


class ImageCheck(BaseModel):
    has_text: bool = Field(
        description="True if any letters, words, numbers, logos or watermarks appear, even garbled."
    )
    looks_like_photo: bool = Field(description="True if a reader could mistake it for a photograph.")
    shows_real_person: bool = Field(
        description="True if it shows a recognizable real person or a detailed realistic face."
    )
    problem: str = Field(description="What to avoid when redrawing, in a few words; empty if none.")

    @property
    def ok(self) -> bool:
        return not (self.has_text or self.looks_like_photo or self.shows_real_person)


class ImageRejected(RuntimeError):
    pass


class ImageGenerator(Protocol):
    def generate(self, prompt: str) -> bytes:
        """Return one landscape image (PNG, JPEG or WebP bytes) for the prompt."""
        ...


class ImageStore(Protocol):
    def save(self, name: str, data: bytes, content_type: str) -> str:
        """Store the file and return its public URL."""
        ...


class SupabaseStorage:
    """Uploads to a public Supabase Storage bucket with the project's secret key."""

    def __init__(self, url: str, key: str, bucket: str = BUCKET, client: httpx.Client | None = None):
        self.base = url.rstrip("/")
        self.bucket = bucket
        self.client = client or httpx.Client(timeout=60)
        self.headers = {"apikey": key, "Authorization": f"Bearer {key}"}

    def save(self, name: str, data: bytes, content_type: str) -> str:
        response = self.client.post(
            f"{self.base}/storage/v1/object/{self.bucket}/{name}",
            content=data,
            headers={
                **self.headers,
                "Content-Type": content_type,
                # Names include a content hash, so a file never changes once uploaded.
                "Cache-Control": "max-age=31536000",
                "x-upsert": "true",
            },
        )
        response.raise_for_status()
        return f"{self.base}/storage/v1/object/public/{self.bucket}/{name}"


def to_webp(data: bytes, width: int = WIDTH) -> bytes:
    """Re-encode any image as a 3:2 WebP of the given width, cropping from the centre."""
    from PIL import Image, ImageOps

    with Image.open(io.BytesIO(data)) as img:
        out = ImageOps.fit(img.convert("RGB"), (width, width * 2 // 3), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "WEBP", quality=WEBP_QUALITY, method=6)
    return buf.getvalue()


def format_story(story: dict) -> str:
    return (
        f"Headline: {story['title']}\n"
        f"Topic: {story['topic']} · Region: {story['region']}\n"
        f"Summary: {story['dek']}"
    )


def illustrate(story: dict, llm: StructuredLLM, generator: ImageGenerator, store: ImageStore) -> None:
    brief = llm.ask(SYSTEM, format_story(story), ImageBrief)
    prompt = f"{brief.scene}\n\n{HOUSE_STYLE}"
    for attempt in range(1, ATTEMPTS + 1):
        data = to_webp(generator.generate(prompt))
        check = llm.ask(CHECK_SYSTEM, CHECK_PROMPT, ImageCheck, image=data)
        if check.ok:
            break
        log.warning("Redrawing image for %r (attempt %d): %s", story["title"], attempt, check.problem)
        prompt = f"{brief.scene}\n\nAvoid: {check.problem}\n\n{HOUSE_STYLE}"
    else:
        raise ImageRejected(f"every attempt failed the check, last: {check.problem}")
    name = f"{story['slug']}-{hashlib.sha256(data).hexdigest()[:10]}.webp"
    story["image_url"] = store.save(name, data, "image/webp")
    story["image_alt"] = brief.alt


def add_images(records: dict, llm: StructuredLLM, generator: ImageGenerator, store: ImageStore) -> int:
    """Give each story an illustration in place; returns how many got one."""
    made = 0
    for story in records["stories"]:
        try:
            illustrate(story, llm, generator, store)
            made += 1
        except Exception:
            # Images are a bonus: a story without one is still published.
            log.exception("No image for %r", story["title"])
    return made


def make_generator(settings) -> ImageGenerator | None:
    """The configured image service, or None when its key is not set."""
    return None  # Placeholder until an image service is chosen.
