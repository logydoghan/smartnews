"""Morning news agent, step 1: gather recent articles from RSS feeds and GDELT."""

from __future__ import annotations

import calendar
import html
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit

import feedparser
import httpx

from .models import Article
from .sources import FEEDS, GDELT_OUTLETS, GDELT_QUERY, GDELT_URL, Feed

log = logging.getLogger(__name__)

USER_AGENT = "SmartNewsBot/0.1 (+https://github.com/logydoghan/smartnews)"
_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def clean_text(raw: str, limit: int = 400) -> str:
    text = _SPACE_RE.sub(" ", html.unescape(_TAG_RE.sub(" ", raw or ""))).strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def normalize_url(url: str) -> str:
    """Drop query strings and fragments so the same article from two feeds dedupes."""
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def _entry_time(entry) -> datetime | None:
    stamp = entry.get("published_parsed") or entry.get("updated_parsed")
    if not stamp:
        return None
    try:
        return datetime.fromtimestamp(calendar.timegm(stamp), tz=timezone.utc)
    except (ValueError, OverflowError, OSError):
        # Bogus dates such as 0000-00-00 parse to year -1.
        return None


def parse_feed(feed: Feed, content: bytes, since: datetime, limit: int) -> list[Article]:
    parsed = feedparser.parse(content)
    articles: list[Article] = []
    for entry in parsed.entries[:limit]:
        url, title = entry.get("link"), clean_text(entry.get("title", ""), 200)
        if not url or not title:
            continue
        published = _entry_time(entry)
        # Keep undated entries: some feeds omit dates, and the feed order is already recent-first.
        if published and published < since:
            continue
        try:
            url = normalize_url(url)
        except ValueError:
            continue
        articles.append(
            Article(
                url=url,
                title=title,
                outlet=feed.outlet,
                country=feed.country,
                leaning=feed.leaning,
                summary=clean_text(entry.get("summary", "")),
                published_at=published,
            )
        )
    return articles


def parse_gdelt(payload: dict) -> list[Article]:
    articles: list[Article] = []
    for item in payload.get("articles", []):
        url, title = item.get("url"), clean_text(item.get("title", ""), 200)
        domain = (item.get("domain") or "").removeprefix("www.")
        if not url or not title:
            continue
        seen = item.get("seendate")  # e.g. 20261016T053000Z
        published = (
            datetime.strptime(seen, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc) if seen else None
        )
        articles.append(
            Article(
                url=normalize_url(url),
                title=title,
                outlet=GDELT_OUTLETS.get(domain, domain),
                country=item.get("sourcecountry") or "",
                leaning="center" if domain in GDELT_OUTLETS else None,
                summary="",
                published_at=published,
            )
        )
    return articles


def _fetch_feed(client: httpx.Client, feed: Feed, since: datetime, limit: int) -> list[Article]:
    try:
        response = client.get(feed.url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("Skipping %s: %s", feed.outlet, exc)
        return []
    try:
        return parse_feed(feed, response.content, since, limit)
    except Exception:
        log.exception("Skipping %s: could not parse its feed", feed.outlet)
        return []


def _fetch_gdelt(client: httpx.Client, hours: int) -> list[Article]:
    params = {
        "query": GDELT_QUERY,
        "mode": "artlist",
        "format": "json",
        "maxrecords": "150",
        "timespan": f"{hours}h",
        "sort": "hybridrel",
    }
    try:
        response = client.get(GDELT_URL, params=params)
        response.raise_for_status()
        return parse_gdelt(response.json())
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("Skipping GDELT: %s", exc)
        return []


def dedupe(articles: list[Article]) -> list[Article]:
    seen_urls: set[str] = set()
    seen_titles: set[tuple[str, str]] = set()
    unique: list[Article] = []
    for article in articles:
        title_key = (article.outlet, article.title.lower())
        if article.url in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(article.url)
        seen_titles.add(title_key)
        unique.append(article)
    return unique


def collect(
    lookback_hours: int = 24,
    per_feed_limit: int = 40,
    use_gdelt: bool = True,
    feeds: tuple[Feed, ...] = FEEDS,
) -> list[Article]:
    since = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    with httpx.Client(
        timeout=20, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client, ThreadPoolExecutor(max_workers=8) as pool:
        batches = list(pool.map(lambda f: _fetch_feed(client, f, since, per_feed_limit), feeds))
        if use_gdelt:
            batches.append(_fetch_gdelt(client, lookback_hours))
    articles = dedupe([a for batch in batches for a in batch])
    log.info("Collected %d articles from %d sources", len(articles), len(feeds))
    return articles
