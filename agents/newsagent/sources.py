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
    # Feeds for one section (such as "Sports") hint the story's category; "" is general news.
    section: str = ""


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
    # Section feeds. Each one was checked on 2026-10-17 and had items from the last two days.
    # Finance
    Feed("NPR", "https://feeds.npr.org/1006/rss.xml", "United States", "left", "Finance"),
    Feed("Dawn", "https://www.dawn.com/feeds/business", "Pakistan", "left", "Finance"),
    Feed("The Irish Times", "https://www.irishtimes.com/arc/outboundfeeds/feed-business/?outputType=xml", "Ireland", "center", "Finance"),
    Feed("Euronews", "https://www.euronews.com/rss?level=vertical&name=business", "France", "center", "Finance"),
    Feed("Business Standard", "https://www.business-standard.com/rss/economy-102.rss", "India", "center", "Finance"),
    Feed("ABC News (Australia)", "https://www.abc.net.au/news/feed/51892/rss.xml", "Australia", "center", "Finance"),
    Feed("City AM", "https://www.cityam.com/feed/", "United Kingdom", "right", "Finance"),
    Feed("Washington Examiner", "https://www.washingtonexaminer.com/section/business/feed/", "United States", "right", "Finance"),
    # Technology
    Feed("NPR", "https://feeds.npr.org/1019/rss.xml", "United States", "left", "Technology"),
    Feed("Rest of World", "https://restofworld.org/feed/latest", "United States", "left", "Technology"),
    Feed("Sky News", "https://feeds.skynews.com/feeds/rss/technology.xml", "United Kingdom", "center", "Technology"),
    Feed("Euronews", "https://www.euronews.com/rss?level=vertical&name=next", "France", "center", "Technology"),
    Feed("The Irish Times", "https://www.irishtimes.com/arc/outboundfeeds/feed-technology/?outputType=xml", "Ireland", "center", "Technology"),
    Feed("Japan Today", "https://japantoday.com/category/tech/feed", "Japan", "center", "Technology"),
    Feed("Fox News", "https://moxie.foxnews.com/google-publisher/tech.xml", "United States", "right", "Technology"),
    Feed("Washington Examiner", "https://www.washingtonexaminer.com/tag/technology/feed/", "United States", "right", "Technology"),
    # Health
    Feed("NPR", "https://feeds.npr.org/1128/rss.xml", "United States", "left", "Health"),
    Feed("ABC News (Australia)", "https://www.abc.net.au/news/feed/9167762/rss.xml", "Australia", "center", "Health"),
    Feed("STAT", "https://www.statnews.com/feed/", "United States", "center", "Health"),
    Feed("Euronews", "https://www.euronews.com/rss?level=vertical&name=health", "France", "center", "Health"),
    Feed("ThePrint", "https://theprint.in/category/health/feed/", "India", "center", "Health"),
    Feed("Premium Times", "https://www.premiumtimesng.com/health/feed", "Nigeria", "center", "Health"),
    Feed("Fox News", "https://moxie.foxnews.com/google-publisher/health.xml", "United States", "right", "Health"),
    Feed("Washington Examiner", "https://www.washingtonexaminer.com/tag/health/feed/", "United States", "right", "Health"),
    # Entertainment
    Feed("NPR", "https://feeds.npr.org/1008/rss.xml", "United States", "left", "Entertainment"),
    Feed("ABC News (Australia)", "https://www.abc.net.au/news/feed/103728568/rss.xml", "Australia", "center", "Entertainment"),
    Feed("Sky News", "https://feeds.skynews.com/feeds/rss/entertainment.xml", "United Kingdom", "center", "Entertainment"),
    Feed("Global News", "https://globalnews.ca/entertainment/feed/", "Canada", "center", "Entertainment"),
    Feed("NDTV", "https://feeds.feedburner.com/ndtvmovies-latest", "India", "center", "Entertainment"),
    Feed("Philippine Daily Inquirer", "https://entertainment.inquirer.net/feed", "Philippines", "center", "Entertainment"),
    Feed("Fox News", "https://moxie.foxnews.com/google-publisher/entertainment.xml", "United States", "right", "Entertainment"),
    Feed("The Jerusalem Post", "https://www.jpost.com/rss/rssfeedsculture.aspx", "Israel", "right", "Entertainment"),
    # Sports
    Feed("NPR", "https://feeds.npr.org/1055/rss.xml", "United States", "left", "Sports"),
    Feed("Dawn", "https://www.dawn.com/feeds/sport", "Pakistan", "left", "Sports"),
    Feed("Sky Sports", "https://www.skysports.com/rss/12040", "United Kingdom", "center", "Sports"),
    Feed("ESPNcricinfo", "https://www.cricinfo.com/rss/content/story/feeds/0.xml", "India", "center", "Sports"),
    Feed("The Irish Times", "https://www.irishtimes.com/arc/outboundfeeds/feed-sport/?outputType=xml", "Ireland", "center", "Sports"),
    Feed("ABC News (Australia)", "https://www.abc.net.au/news/feed/2942460/rss.xml", "Australia", "center", "Sports"),
    Feed("Fox News", "https://feeds.foxnews.com/foxnews/sports", "United States", "right", "Sports"),
    Feed("The Jerusalem Post", "https://www.jpost.com/rss/rssfeedssports.aspx", "Israel", "right", "Sports"),
)

# GDELT indexes worldwide coverage, including wire services such as Reuters and AP
# that no longer publish open RSS feeds. Wire copy is labeled center.
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = "(domain:reuters.com OR domain:apnews.com) sourcelang:english"
GDELT_OUTLETS = {"reuters.com": "Reuters", "apnews.com": "AP News"}
