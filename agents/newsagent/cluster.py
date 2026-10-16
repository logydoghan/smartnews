"""Morning news agent, step 2: group articles about the same event and pick the top stories."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .llm import StructuredLLM
from .models import Article, ClusterResult, StoryCluster

log = logging.getLogger(__name__)

SYSTEM = """You are the front-page editor of a world news briefing. You receive a numbered \
list of headlines published in the last day by outlets around the world. Group the articles \
that report the same event, then choose the most important world stories of the day.

Judge importance by consequences for many people and by how widely the event is covered \
across countries and outlets, not by sensationalism. Prefer events covered by several \
outlets. Leave out sports results, celebrity news, product reviews, opinion columns that \
report no event, and purely local stories. Every article id you list must come from the \
input, and an article belongs to at most one story. Order stories from most to least important."""


@dataclass
class Story:
    title: str
    topic: str
    region: str
    why_it_matters: str
    articles: list[Article]

    @property
    def outlets(self) -> set[str]:
        return {a.outlet for a in self.articles}


def format_headlines(articles: list[Article]) -> str:
    lines = []
    for i, a in enumerate(articles):
        line = f"[{i}] {a.title} ({a.outlet}, {a.country})"
        if a.summary:
            line += f" | {a.summary[:160]}"
        lines.append(line)
    return "\n".join(lines)


def build_stories(
    clusters: list[StoryCluster], articles: list[Article], min_outlets: int, max_stories: int
) -> list[Story]:
    """Turn Claude's clusters into stories, dropping invalid ids and thinly covered events."""
    used: set[int] = set()
    stories: list[Story] = []
    for cluster in clusters:
        ids = [i for i in dict.fromkeys(cluster.article_ids) if 0 <= i < len(articles) and i not in used]
        story = Story(
            title=cluster.title,
            topic=cluster.topic,
            region=cluster.region,
            why_it_matters=cluster.why_it_matters,
            articles=[articles[i] for i in ids],
        )
        if len(story.outlets) < min_outlets:
            log.info("Dropping %r: only %d outlet(s)", story.title, len(story.outlets))
            continue
        used.update(ids)
        stories.append(story)
        if len(stories) == max_stories:
            break
    return stories


def cluster_articles(
    llm: StructuredLLM, articles: list[Article], max_stories: int, min_outlets: int
) -> list[Story]:
    if not articles:
        return []
    prompt = (
        f"Choose up to {max_stories + 4} top stories from these {len(articles)} articles.\n\n"
        + format_headlines(articles)
    )
    result = llm.ask(SYSTEM, prompt, ClusterResult)
    stories = build_stories(result.stories, articles, min_outlets, max_stories)
    log.info("Picked %d stories", len(stories))
    return stories
