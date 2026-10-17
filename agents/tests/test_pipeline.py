from datetime import date

from newsagent.analyze import analyze_story, clean_analysis
from newsagent.cluster import build_stories, cluster_articles
from newsagent.config import DEFAULT_ANGLES
from newsagent.models import AngleView, ClusterResult, Fact, StoryAnalysis, StoryCluster
from newsagent.store import AnalyzedStory, slugify, to_records

from .conftest import FakeLLM


def cluster(ids, title="Treaty signed"):
    return StoryCluster(title=title, topic="Climate", region="Global", article_ids=ids,
                        why_it_matters="It affects every coast.")


def analysis(**overrides):
    base = dict(
        dek="A treaty was signed. Enforcement is disputed.",
        facts=[Fact(text="41 countries signed.", refs=[1, 9]), Fact(text="Unsourced.", refs=[42])],
        agree="It is the biggest deal of its kind.",
        disagree="Whether it can be enforced.",
        agreement_level="mixed",
        angles=[
            AngleView(key="right", label="Right", stance="Costly.", body="Jobs at risk.", refs=[2]),
            AngleView(key="left", label="Left", stance="Too weak.", body="Producers escape.", refs=[1, 7]),
            AngleView(key="made_up", label="Other", stance="?", body="?", refs=[1]),
            AngleView(key="left", label="Left again", stance="Dup.", body="Dup.", refs=[1]),
            AngleView(key="economic", label="Economic", stance="?", body="?", refs=[]),
        ],
    )
    return StoryAnalysis(**{**base, **overrides})


def test_build_stories_filters_bad_ids_reuse_and_thin_coverage(articles):
    clusters = [
        cluster([0, 1, 1, 99]),          # valid, two outlets
        cluster([1, 2], "Reuses 1"),     # 1 already used, leaves one outlet
        cluster([0, 3], "One outlet"),   # both Left Daily (0 already used anyway)
        cluster([2, 3], "Second"),
    ]
    stories = build_stories(clusters, articles, min_outlets=2, max_stories=5)

    assert [s.title for s in stories] == ["Treaty signed", "Second"]
    assert [a.url for a in stories[0].articles] == [articles[0].url, articles[1].url]


def test_build_stories_caps_count(articles):
    stories = build_stories([cluster([0, 1]), cluster([2, 3], "B")], articles, 2, max_stories=1)
    assert len(stories) == 1


def test_cluster_articles_sends_numbered_headlines(articles):
    llm = FakeLLM(ClusterResult(stories=[cluster([0, 1])]))
    stories = cluster_articles(llm, articles, max_stories=3, min_outlets=2)

    _, prompt, schema = llm.calls[0]
    assert schema is ClusterResult
    assert "[0] Headline 0 (Left Daily, Testland) | Summary 0" in prompt
    assert len(stories) == 1


def test_cluster_articles_skips_llm_when_empty():
    llm = FakeLLM()
    assert cluster_articles(llm, [], 3, 2) == [] and llm.calls == []


def test_clean_analysis_drops_bad_refs_and_orders_angles(articles):
    story = build_stories([cluster([0, 1])], articles, 2, 1)[0]
    cleaned = clean_analysis(analysis(), story, DEFAULT_ANGLES)

    assert [f.refs for f in cleaned.facts] == [[1]]
    assert [(v.key, v.label, v.refs) for v in cleaned.angles] == [("left", "Left", [1]), ("right", "Right", [2])]


def test_analyze_story_prompt_lists_sources_and_angles(articles):
    story = build_stories([cluster([0, 1])], articles, 2, 1)[0]
    llm = FakeLLM(analysis())
    analyze_story(llm, story, DEFAULT_ANGLES)

    prompt = llm.calls[0][1]
    assert "[1] Left Daily (Testland, leaning: left): Headline 0" in prompt
    assert "[2] Right Times (Testland, leaning: right): Headline 1" in prompt
    assert '- regional (label "Regional")' in prompt


def test_to_records_shapes_briefing(articles):
    story = build_stories([cluster([0, 1, 2])], articles, 2, 1)[0]
    records = to_records(date(2026, 10, 16), [AnalyzedStory(story, clean_analysis(analysis(), story, DEFAULT_ANGLES))])

    assert records["date"] == "2026-10-16"
    assert records["article_count"] == 3 and records["outlet_count"] == 3
    s = records["stories"][0]
    assert s["slug"] == "2026-10-16-treaty-signed"
    assert [src["ref"] for src in s["sources"]] == [1, 2, 3]
    assert [v["position"] for v in s["angles"]] == [0, 1]


def test_to_records_makes_slugs_unique(articles):
    long = "European Union leaders agree new sanctions package against Russia over"
    stories = build_stories(
        [cluster([0, 1], long + " energy"), cluster([2, 3], long + " oil"), cluster([], "x")],
        articles, 1, 3,
    )
    items = [AnalyzedStory(s, analysis()) for s in stories]
    slugs = [s["slug"] for s in to_records(date(2026, 10, 17), items)["stories"]]
    assert slugs[0] == slugs[1].removesuffix("-2") and len(set(slugs)) == 2


def test_slugify():
    assert slugify("Café owners — rates rise 0.25%!") == "cafe-owners-rates-rise-0-25"
    assert slugify("???") == "story"
