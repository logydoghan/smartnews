"""Runtime settings, read from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Angle:
    key: str
    label: str
    guidance: str


# The viewpoints every story is analyzed from. "regional" lets the model name the
# region whose coverage differs most (for example "Global South" or "Europe").
DEFAULT_ANGLES: tuple[Angle, ...] = (
    Angle("left", "Left", "How left-leaning and progressive outlets frame the story."),
    Angle("center", "Center", "How centrist and wire-style outlets frame the story."),
    Angle("right", "Right", "How right-leaning and conservative outlets frame the story."),
    Angle(
        "regional",
        "Regional",
        "How outlets in the region most affected, or outside the US and Europe, see it. "
        "Use a label naming that region.",
    ),
    Angle("economic", "Economic", "Who gains and who loses financially, per business coverage."),
)


@dataclass(frozen=True)
class Settings:
    model: str = "claude-sonnet-5-5"
    max_stories: int = 12
    min_outlets_per_story: int = 2
    lookback_hours: int = 24
    max_articles_per_feed: int = 40
    use_gdelt: bool = True
    database_url: str | None = None
    angles: tuple[Angle, ...] = field(default=DEFAULT_ANGLES)
    # Image agent: runs when the Recraft key and Supabase Storage settings are set.
    images: bool = True
    image_model: str = "recraftv4_1"
    recraft_api_key: str | None = None
    recraft_style_id: str | None = None
    supabase_url: str | None = None
    supabase_secret_key: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model=os.environ.get("NEWSAGENT_MODEL", cls.model),
            max_stories=int(os.environ.get("NEWSAGENT_MAX_STORIES", cls.max_stories)),
            min_outlets_per_story=int(
                os.environ.get("NEWSAGENT_MIN_OUTLETS", cls.min_outlets_per_story)
            ),
            lookback_hours=int(os.environ.get("NEWSAGENT_LOOKBACK_HOURS", cls.lookback_hours)),
            use_gdelt=os.environ.get("NEWSAGENT_USE_GDELT", "1") != "0",
            database_url=os.environ.get("DATABASE_URL") or None,
            images=os.environ.get("NEWSAGENT_IMAGES", "1") != "0",
            image_model=os.environ.get("NEWSAGENT_IMAGE_MODEL", cls.image_model),
            recraft_api_key=os.environ.get("RECRAFT_API_KEY") or None,
            recraft_style_id=os.environ.get("RECRAFT_STYLE_ID") or None,
            supabase_url=os.environ.get("SUPABASE_URL") or None,
            supabase_secret_key=os.environ.get("SUPABASE_SECRET_KEY") or None,
        )
