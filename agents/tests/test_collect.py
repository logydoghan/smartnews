from datetime import datetime, timezone
from pathlib import Path

from newsagent.collect import clean_text, dedupe, normalize_url, parse_feed, parse_gdelt
from newsagent.sources import Feed

FEED = Feed("Example", "https://example.com/rss", "Testland", "center")
FIXTURE = Path(__file__).parent / "fixtures" / "world.xml"


def test_parse_feed_keeps_recent_and_undated_entries():
    since = datetime(2026, 10, 15, tzinfo=timezone.utc)
    articles = parse_feed(FEED, FIXTURE.read_bytes(), since, limit=10)

    assert [a.title for a in articles] == ["Coastal nations sign ocean plastic treaty", "Undated bulletin"]
    first = articles[0]
    assert first.url == "https://example.com/world/plastic-treaty"
    assert first.summary == "Forty-one countries agreed on binding limits."
    assert first.outlet == "Example" and first.leaning == "center"
    assert first.published_at == datetime(2026, 10, 16, 4, tzinfo=timezone.utc)
    assert articles[1].url == "https://example.com/world/undated"


def test_parse_feed_respects_limit():
    since = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert len(parse_feed(FEED, FIXTURE.read_bytes(), since, limit=1)) == 1


def test_parse_gdelt_labels_wire_services():
    payload = {
        "articles": [
            {"url": "https://www.reuters.com/world/a", "title": "Wire story", "domain": "reuters.com",
             "sourcecountry": "United States", "seendate": "20261016T053000Z"},
            {"url": "https://blog.example/b", "title": "Other", "domain": "blog.example"},
            {"url": "", "title": "Missing url"},
        ]
    }
    articles = parse_gdelt(payload)

    assert [(a.outlet, a.leaning) for a in articles] == [("Reuters", "center"), ("blog.example", None)]
    assert articles[0].published_at == datetime(2026, 10, 16, 5, 30, tzinfo=timezone.utc)


def test_dedupe_by_url_and_title(articles):
    copy = articles[0]
    same_title = type(copy)(**{**copy.__dict__, "url": "https://other.example/x"})
    assert dedupe([copy, copy, same_title, articles[1]]) == [copy, articles[1]]


def test_clean_text_truncates_on_word_boundary():
    assert clean_text("one two three four", limit=10) == "one two…"
    assert normalize_url("HTTPS://Example.COM/a/?q=1#x") == "https://example.com/a"
