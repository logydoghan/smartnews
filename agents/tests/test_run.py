import copy

from newsagent import run as run_module


def test_briefing_is_saved_before_images_are_drawn(monkeypatch):
    records = {"date": "2026-10-17", "stories": [{"title": "T", "image_url": None, "image_alt": None}]}
    saved = []

    def fake_add_images(records, llm, generator, store):
        assert len(saved) == 1, "the briefing must already be saved"
        records["stories"][0]["image_url"] = "https://cdn.example/t.webp"
        return 1

    monkeypatch.setenv("DATABASE_URL", "postgres://example")
    monkeypatch.setenv("RECRAFT_API_KEY", "rk")
    monkeypatch.setenv("SUPABASE_URL", "https://abc.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_x")
    monkeypatch.setattr(run_module, "ClaudeLLM", lambda model: object())
    monkeypatch.setattr(run_module, "run", lambda settings, llm: records)
    monkeypatch.setattr(run_module, "add_images", fake_add_images)
    monkeypatch.setattr(run_module, "save_to_database", lambda url, r: saved.append(copy.deepcopy(r)))

    assert run_module.main([]) == 0
    assert [s["stories"][0]["image_url"] for s in saved] == [None, "https://cdn.example/t.webp"]
