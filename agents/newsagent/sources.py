"""News sources the morning agent reads.

`leaning` is a rough editorial label used to balance coverage and to tell the
analysis agent which outlets speak for which side. It is a starting point to
review, not a verdict on any outlet. Edit this list to add or drop sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Leaning = Literal["left", "center", "right"]


@dataclass(frozen=True)
class Feed:
    outlet: str
    url: str
    country: str
    leaning: Leaning


FEEDS: tuple[Feed, ...] = (
    Feed("BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml", "United Kingdom", "center"),
    Feed("The Guardian", "https://www.theguardian.com/world/rss", "United Kingdom", "left"),
    Feed("NPR", "https://feeds.npr.org/1004/rss.xml", "United States", "left"),
    Feed("Fox News", "https://moxie.foxnews.com/google-publisher/world.xml", "United States", "right"),
    Feed("New York Post", "https://nypost.com/news/feed/", "United States", "right"),
    Feed("Wall Street Journal", "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "United States", "right"),
    Feed("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "Qatar", "center"),
    Feed("Deutsche Welle", "https://rss.dw.com/rdf/rss-en-all", "Germany", "center"),
    Feed("France 24", "https://www.france24.com/en/rss", "France", "center"),
    Feed("The Hindu", "https://www.thehindu.com/news/international/feeder/default.rss", "India", "center"),
    Feed("South China Morning Post", "https://www.scmp.com/rss/91/feed", "Hong Kong", "center"),
    Feed("The Japan Times", "https://www.japantimes.co.jp/feed/", "Japan", "center"),
    Feed("AllAfrica", "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf", "Africa", "center"),
)

# GDELT indexes worldwide coverage, including wire services such as Reuters and AP
# that no longer publish open RSS feeds. Wire copy is labeled center.
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = "(domain:reuters.com OR domain:apnews.com) sourcelang:english"
GDELT_OUTLETS = {"reuters.com": "Reuters", "apnews.com": "AP News"}
