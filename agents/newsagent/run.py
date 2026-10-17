"""Run the full morning pipeline: collect, cluster, analyze, save.

    python -m newsagent.run                 # save to DATABASE_URL
    python -m newsagent.run --json out.json # also (or only) write JSON
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .analyze import analyze_story
from .cluster import cluster_articles
from .collect import collect
from .config import Settings
from .llm import ClaudeLLM, LLMError, StructuredLLM
from .store import AnalyzedStory, save_to_database, to_records, write_json

log = logging.getLogger("newsagent")


def run(settings: Settings, llm: StructuredLLM) -> dict:
    day = datetime.now(timezone.utc).date()
    articles = collect(settings.lookback_hours, settings.max_articles_per_feed, settings.use_gdelt)
    stories = cluster_articles(llm, articles, settings.max_stories, settings.min_outlets_per_story)

    analyzed: list[AnalyzedStory] = []
    for story in stories:
        try:
            analyzed.append(AnalyzedStory(story, analyze_story(llm, story, settings.angles)))
        except LLMError as exc:
            # One failed story should not sink the whole morning briefing.
            log.error("Skipping %r: %s", story.title, exc)
    return to_records(day, analyzed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build today's SmartNews briefing.")
    parser.add_argument("--json", type=Path, help="Write the briefing to this JSON file.")
    parser.add_argument("--no-db", action="store_true", help="Do not write to the database.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
    if not args.no_db and not settings.database_url:
        parser.error("DATABASE_URL is not set (use --no-db with --json for a dry run)")

    try:
        records = run(settings, ClaudeLLM(settings.model))
    except LLMError as exc:
        log.error("Briefing failed: %s", exc)
        return 1
    if not records["stories"]:
        log.error("No stories were produced; leaving the previous briefing in place")
        return 1

    if args.json:
        write_json(args.json, records)
        log.info("Wrote %s", args.json)
    if not args.no_db:
        save_to_database(settings.database_url, records)
        log.info("Saved briefing for %s with %d stories", records["date"], len(records["stories"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
