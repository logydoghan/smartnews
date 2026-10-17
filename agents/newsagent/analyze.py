"""Analysis agent: explain one story from several angles, grounded in the coverage collected."""

from __future__ import annotations

import logging

from .cluster import Story
from .config import Angle
from .llm import StructuredLLM
from .models import StoryAnalysis

log = logging.getLogger(__name__)

SYSTEM = """You help readers compare how different parts of the press see the same news story. \
You receive numbered sources about one event, each with its outlet, country and a rough \
editorial leaning, and a list of angles to cover.

Rules:
- Facts are things the sources report as having happened. State them neutrally and cite \
the source numbers that report each one.
- Each angle describes how that side sees the story, drawn from the sources you cite for \
it. Represent each view fairly and in its strongest form, without endorsing or mocking it.
- Cite only source numbers from the list. Never invent quotes, numbers or events.
- If no source speaks for an angle, leave that angle out rather than guessing.
- Write plainly for a general reader."""


def format_sources(story: Story) -> str:
    lines = []
    for n, a in enumerate(story.articles, start=1):
        leaning = a.leaning or "unknown"
        line = f"[{n}] {a.outlet} ({a.country}, leaning: {leaning}): {a.title}"
        if a.summary:
            line += f"\n    {a.summary}"
        lines.append(line)
    return "\n".join(lines)


def format_angles(angles: tuple[Angle, ...]) -> str:
    return "\n".join(f"- {a.key} (label \"{a.label}\"): {a.guidance}" for a in angles)


def clean_analysis(analysis: StoryAnalysis, story: Story, angles: tuple[Angle, ...]) -> StoryAnalysis:
    """Drop citations to sources that do not exist, angles that cite nothing, and repeated angles."""
    valid = set(range(1, len(story.articles) + 1))
    order = {a.key: i for i, a in enumerate(angles)}
    for fact in analysis.facts:
        fact.refs = sorted(set(fact.refs) & valid)
    kept, seen = [], set()
    for view in analysis.angles:
        view.refs = sorted(set(view.refs) & valid)
        # The database allows one view per angle, so the first valid one wins.
        if view.key in order and view.refs and view.key not in seen:
            seen.add(view.key)
            kept.append(view)
    analysis.angles = sorted(kept, key=lambda v: order[v.key])
    analysis.facts = [f for f in analysis.facts if f.refs]
    return analysis


def analyze_story(llm: StructuredLLM, story: Story, angles: tuple[Angle, ...]) -> StoryAnalysis:
    prompt = (
        f"Story: {story.title}\n\n"
        f"Sources:\n{format_sources(story)}\n\n"
        f"Angles to cover, in this order:\n{format_angles(angles)}"
    )
    analysis = llm.ask(SYSTEM, prompt, StoryAnalysis)
    return clean_analysis(analysis, story, angles)
