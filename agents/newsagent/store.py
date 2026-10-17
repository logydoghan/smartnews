"""Save a finished briefing to Postgres (Supabase) or to a JSON file."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .cluster import Story
from .models import StoryAnalysis


@dataclass
class AnalyzedStory:
    story: Story
    analysis: StoryAnalysis


def slugify(text: str, max_len: int = 60) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "story"


def story_slug(day: date, title: str) -> str:
    return f"{day.isoformat()}-{slugify(title)}"


def to_records(day: date, items: list[AnalyzedStory]) -> dict:
    """The briefing as plain data, shaped like the database tables."""
    outlets = {a.outlet for item in items for a in item.story.articles}
    stories = []
    used_slugs: set[str] = set()
    for rank, item in enumerate(items, start=1):
        s, a = item.story, item.analysis
        # Slugs are unique in the database; titles can repeat or share a long prefix.
        base = slug = story_slug(day, s.title)
        n = 2
        while slug in used_slugs:
            slug, n = f"{base}-{n}", n + 1
        used_slugs.add(slug)
        stories.append(
            {
                "rank": rank,
                "slug": slug,
                "title": s.title,
                "topic": s.topic,
                "region": s.region,
                "dek": a.dek,
                "why_it_matters": s.why_it_matters,
                "agree": a.agree,
                "disagree": a.disagree,
                "agreement_level": a.agreement_level,
                "facts": [f.model_dump() for f in a.facts],
                # Filled in by the image agent when it runs.
                "image_url": None,
                "image_alt": None,
                "sources": [
                    {
                        "ref": n,
                        "url": art.url,
                        "title": art.title,
                        "outlet": art.outlet,
                        "country": art.country,
                        "leaning": art.leaning,
                        "published_at": art.published_at.isoformat() if art.published_at else None,
                    }
                    for n, art in enumerate(s.articles, start=1)
                ],
                "angles": [
                    {"position": i, **v.model_dump()} for i, v in enumerate(a.angles)
                ],
            }
        )
    return {
        "date": day.isoformat(),
        "article_count": sum(len(item.story.articles) for item in items),
        "outlet_count": len(outlets),
        "stories": stories,
    }


def write_json(path: Path, records: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False))


def save_to_database(database_url: str, records: dict) -> None:
    """Replace the briefing for this date in one transaction, so reruns are safe."""
    import psycopg
    from psycopg.types.json import Jsonb

    # prepare_threshold=None keeps this working through Supabase's transaction pooler too.
    with psycopg.connect(database_url, prepare_threshold=None) as conn, conn.transaction():
        conn.execute("delete from briefings where date = %s", (records["date"],))
        conn.execute(
            "insert into briefings (date, article_count, outlet_count) values (%s, %s, %s)",
            (records["date"], records["article_count"], records["outlet_count"]),
        )
        for s in records["stories"]:
            (story_id,) = conn.execute(
                """insert into stories (briefing_date, rank, slug, title, topic, region, dek,
                       why_it_matters, agree, disagree, agreement_level, facts, image_url, image_alt)
                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id""",
                (
                    records["date"], s["rank"], s["slug"], s["title"], s["topic"], s["region"],
                    s["dek"], s["why_it_matters"], s["agree"], s["disagree"],
                    s["agreement_level"], Jsonb(s["facts"]), s["image_url"], s["image_alt"],
                ),
            ).fetchone()
            with conn.cursor() as cur:
                cur.executemany(
                    """insert into story_sources (story_id, ref, url, title, outlet, country,
                           leaning, published_at)
                       values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    [
                        (story_id, src["ref"], src["url"], src["title"], src["outlet"],
                         src["country"], src["leaning"], src["published_at"])
                        for src in s["sources"]
                    ],
                )
                cur.executemany(
                    """insert into angles (story_id, position, key, label, stance, body, refs)
                       values (%s, %s, %s, %s, %s, %s, %s)""",
                    [
                        (story_id, v["position"], v["key"], v["label"], v["stance"], v["body"],
                         v["refs"])
                        for v in s["angles"]
                    ],
                )
