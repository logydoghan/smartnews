# SmartNews

One story, every angle. Each morning an agent gathers the top world news into one briefing, a second agent explains each story from several viewpoints (left, center, right, regional and economic) so readers can compare how different parts of the press see the same event, and a third draws an illustration for each story. Every fact and angle cites the articles it came from.

## How it fits together

```
agents/     Python. Runs once a day (GitHub Actions, 06:00 UTC).
  collect   RSS feeds from outlets in many countries, plus Reuters/AP via GDELT
  cluster   Claude groups articles about the same event and picks the top stories
  analyze   Claude writes the facts, agreement/disagreement and one view per angle
  images    Claude describes a scene, Recraft draws it, Claude checks it; saved to Supabase Storage
  store     Saves the briefing to Postgres (Supabase)
web/        Next.js site (Vercel). Reads the latest briefing from Supabase.
supabase/   Database schema.
```

Both halves share one Supabase Postgres database. The agents write with the database connection string; the site reads with the public anon key, which row-level security limits to read-only.

## Setup

1. **Database.** Create a Supabase project and run the files in `supabase/migrations/` in order (`0001_init.sql`, then `0002_story_images.sql`) in its SQL editor, or use `supabase db push`.
2. **Agents.** In the GitHub repository, add these Actions secrets:
   - `ANTHROPIC_API_KEY`: a Claude API key.
   - `DATABASE_URL`: the Supabase connection string from the dashboard's **Connect** dialog. Use the **Session pooler** URI (`...pooler.supabase.com:5432/postgres`), not the Direct connection: GitHub Actions has no IPv6, and the direct host is IPv6-only.
   - `RECRAFT_API_KEY`: a [Recraft](https://www.recraft.ai) API key, for the image agent. Recraft bills prepaid credit, about $0.035 per image.
   - `SUPABASE_URL` and `SUPABASE_SECRET_KEY`: the project URL and a secret key (`sb_secret_...`) from **Project Settings → API Keys**, so the image agent can upload to Storage.

   Without the last three, the briefing still publishes, just without images.

   The **Morning briefing** workflow then runs every day at 06:00 UTC. Run it by hand from the Actions tab to publish the first briefing.
3. **Website.** Import the repository into Vercel with `web` as the root directory, and set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (the anon key, called the publishable key, `sb_publishable_...`, in newer projects). Without them the site shows built-in sample stories.

## Running locally

```bash
# Agents (from the repository root)
cd agents
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
export ANTHROPIC_API_KEY=...
newsagent --no-db --json briefing.json   # dry run: writes JSON, skips the database

# Website (from the repository root)
cd web
npm install
npm run dev                               # http://localhost:3000, sample stories unless .env.local is set
```

Settings for the agents are environment variables, listed in `agents/.env.example`: the Claude model (default `claude-sonnet-5-5`), how many stories to publish, how many distinct outlets a story needs, the lookback window, and the image settings (`NEWSAGENT_IMAGES=0` turns images off).

## Editing sources and angles

- **Sources** live in `agents/newsagent/sources.py`. Each feed has a rough editorial `leaning` used to balance coverage and to tell the analysis agent which outlets speak for which side. Review these labels; they are a starting point, not a verdict on any outlet.
- **Angles** live in `DEFAULT_ANGLES` in `agents/newsagent/config.py`. The analysis agent leaves an angle out when no source speaks for it, rather than guessing.

## Notes

- The agents read headlines and RSS summaries, not full article text, write in their own words, and link out to every source.
- Rerunning the agents on the same day replaces that day's briefing.
- Story images are illustrations, never photo-like, and never show recognizable real people. The site labels each one as made by AI. Before an image is saved, Claude looks at it and rejects text, logos, photo-like images and realistic faces; a rejected image is redrawn once, then the story goes without one.
- Images are stored exactly as Recraft returns them, so their provenance metadata stays intact. The house style lives in `HOUSE_STYLE` in `agents/newsagent/images.py`; a Recraft style made from reference images can be added with `RECRAFT_STYLE_ID`.
