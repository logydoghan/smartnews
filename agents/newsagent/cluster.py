"""Morning news agent, step 2: group articles about the same event and pick the top stories."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

from .llm import StructuredLLM
from .models import Article, ClusterResult, StoryCluster

log = logging.getLogger(__name__)

SYSTEM = """You are the front-page editor of a world news site with six sections: Politics, \
Finance, Technology, Health, Entertainment and Sports. You receive a numbered list of headlines \
published in the last day by outlets around the world; some are tagged with the section of the \
feed they came from. Group the articles that report the same event, then choose the most \
important stories for each section.

Put each story in the one section it fits best; a feed's section is a hint, not a rule. Politics \
covers government, elections, diplomacy, conflict and other world affairs, including major \
events that fit no other section. Finance covers business, markets and the economy.

Judge importance by consequences for many people and by how widely the event is covered across \
countries and outlets, not by sensationalism. Prefer events covered by several outlets. In \
Sports, choose news of wide international interest, such as finals, records and major \
tournaments, over routine fixtures. In Entertainment, choose industry news, major releases and \
awards, not gossip about people's private lives. Leave out product reviews, opinion columns that \
report no event, and purely local stories. Every article id you list must come from the input, \
and an article belongs to at most one story. List stories from most to least important overall.

Write each story's title and why_it_matters in your own words rather than reusing an outlet's headline."""


@dataclass
class Story:
    title: str
    topic: str
    category: str
    why_it_matters: str
    articles: list[Article]

    @property
    def outlets(self) -> set[str]:
        return {a.outlet for a in self.articles}


def format_headlines(articles: list[Article]) -> str:
    lines = []
    for i, a in enumerate(articles):
        section = f", {a.section} feed" if a.section else ""
        line = f"[{i}] {a.title} ({a.outlet}, {a.country}{section})"
        if a.summary:
            line += f" | {a.summary[:160]}"
        lines.append(line)
    return "\n".join(lines)


def build_stories(
    clusters: list[StoryCluster],
    articles: list[Article],
    min_outlets: int,
    max_stories: int,
    per_category: int,
) -> list[Story]:
    """Turn Claude's clusters into stories, dropping invalid ids and thinly covered events.

    Each category keeps at most `per_category` stories, so one busy section cannot crowd out
    the others.
    """
    used: set[int] = set()
    per_section: Counter[str] = Counter()
    stories: list[Story] = []
    for cluster in clusters:
        if per_section[cluster.category] >= per_category:
            continue
        ids = [i for i in dict.fromkeys(cluster.article_ids) if 0 <= i < len(articles) and i not in used]
        story = Story(
            title=cluster.title,
            topic=cluster.topic,
            category=cluster.category,
            why_it_matters=cluster.why_it_matters,
            articles=[articles[i] for i in ids],
        )
        if len(story.outlets) < min_outlets:
            log.info("Dropping %r: only %d outlet(s)", story.title, len(story.outlets))
            continue
        used.update(ids)
        per_section[story.category] += 1
        stories.append(story)
        if len(stories) == max_stories:
            break
    return stories


def cluster_articles(
    llm: StructuredLLM,
    articles: list[Article],
    max_stories: int,
    min_outlets: int,
    per_category: int,
) -> list[Story]:
    if not articles:
        return []
    # Ask for spares: stories with too few outlets are dropped afterwards.
    prompt = (
        f"Choose up to {per_category + 2} stories for each section from these "
        f"{len(articles)} articles.\n\n" + format_headlines(articles)
    )
    result = llm.ask(SYSTEM, prompt, ClusterResult)
    stories = build_stories(result.stories, articles, min_outlets, max_stories, per_category)
    log.info("Picked %d stories", len(stories))
    return stories
