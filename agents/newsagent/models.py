"""Data shapes shared by the agents.

`Article` is what the collector produces. The pydantic models below it are the
structured outputs Claude returns, and are also what gets stored.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, get_args

from pydantic import BaseModel, Field


# The site's sections, in the order the home page shows them.
Category = Literal["Politics", "Finance", "Technology", "Health", "Entertainment", "Sports"]
CATEGORIES: tuple[str, ...] = get_args(Category)


@dataclass
class Article:
    url: str
    title: str
    outlet: str
    country: str
    leaning: Optional[str]
    summary: str
    published_at: Optional[datetime]
    section: str = ""  # the feed's section, such as "Sports"; empty for general news


# --- Clustering output -------------------------------------------------------


class StoryCluster(BaseModel):
    title: str = Field(description="Neutral headline for the event, under 90 characters.")
    topic: str = Field(description="One word or two, such as Economy, Climate, Conflict.")
    category: Category = Field(description="The site section this story belongs in; pick the closest.")
    article_ids: list[int] = Field(description="Ids of every article covering this event.")
    why_it_matters: str = Field(description="One sentence on why this is a top story today.")


class ClusterResult(BaseModel):
    stories: list[StoryCluster]


# --- Analysis output ---------------------------------------------------------


class Fact(BaseModel):
    text: str = Field(description="One verifiable fact, stated neutrally.")
    refs: list[int] = Field(description="Source numbers that report this fact.")


class AngleView(BaseModel):
    key: str = Field(description="The angle key this view answers, exactly as given.")
    label: str = Field(description="Short display label, such as Left or Global South.")
    stance: str = Field(description="The angle's position in one sentence, under 80 characters.")
    body: str = Field(description="Two to four sentences explaining the view and its reasoning.")
    refs: list[int] = Field(description="Source numbers this view is drawn from.")


class StoryAnalysis(BaseModel):
    dek: str = Field(description="Two-sentence summary of what happened and why it is contested.")
    facts: list[Fact]
    agree: str = Field(description="What most coverage agrees on, one or two sentences.")
    disagree: str = Field(description="What coverage disagrees on, one or two sentences.")
    agreement_level: Literal["broad agreement", "mixed", "views split"]
    angles: list[AngleView]
