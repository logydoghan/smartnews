# SmartNews

One story, every angle. Each morning an agent gathers the top world news into one briefing, and a second agent explains each story from several viewpoints (left, center, right, regional and economic) so readers can compare how different parts of the press see the same event. Every fact and angle cites the articles it came from.

## How it fits together

```
agents/     Python. Runs once a day (GitHub Actions, 06:00 UTC).
  collect   RSS feeds from outlets in many countries, plus Reuters/AP via GDELT
  cluster   Claude groups articles about the same event and picks the top stories
  analyze   Claude writes the facts, agreement/disagreement and one view per angle
  store     Saves the briefing to Postgres (Supabase)
web/        Next.js site (Vercel). Reads the latest briefing from Supabase.
supabase/   Database schema.
```

Both halves share one Supabase Postgres database. The agents write with the database connection string; the site reads with the public anon key, which row-level security limits to read-only.

## Setup

1. **Database.** Create a Supabase project and run `supabase/migrations/0001_init.sql` in its SQL editor (or with `supabase db push`).
2. **Agents.** In the GitHub repository, add two Actions secrets:
   - `ANTHROPIC_API_KEY`: a Claude API key.
   - `DATABASE_URL`: the Supabase Postgres connection string.

   The **Morning briefing** workflow then runs every day at 06:00 UTC. Run it by hand from the Actions tab to publish the first briefing.
3. **Website.** Import the repository into Vercel with `web` as the root directory, and set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Without them the site shows built-in sample stories.

## Running locally

```bash
# Agents
cd agents
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
export ANTHROPIC_API_KEY=...
newsagent --no-db --json briefing.json   # dry run: writes JSON, skips the database

# Website
cd web
npm install
npm run dev                               # http://localhost:3000, sample stories unless .env.local is set
```

Settings for the agents are environment variables, listed in `agents/.env.example`: the Claude model (default `claude-sonnet-5-5`), how many stories to publish, how many distinct outlets a story needs, and the lookback window.

## Editing sources and angles

- **Sources** live in `agents/newsagent/sources.py`. Each feed has a rough editorial `leaning` used to balance coverage and to tell the analysis agent which outlets speak for which side. Review these labels; they are a starting point, not a verdict on any outlet.
- **Angles** live in `DEFAULT_ANGLES` in `agents/newsagent/config.py`. The analysis agent leaves an angle out when no source speaks for it, rather than guessing.

## Notes

- The agents read headlines and RSS summaries, not full article text, and link out to every source.
- Rerunning the agents on the same day replaces that day's briefing.
- Planned: an image agent that generates an image for each story.
