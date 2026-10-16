import type { Briefing, Source, Story } from "./types";

// Shown when no database is configured, so the site can be developed and previewed
// before the agents have run. Stories and outlets here are made up.

function sources(slug: string, specs: [string, string, Source["leaning"]][]): Source[] {
  return specs.map(([outlet, country, leaning], i) => ({
    ref: i + 1,
    url: `https://example.com/${slug}/${i + 1}`,
    title: `${outlet} coverage of the story`,
    outlet,
    country,
    leaning,
    published_at: "2026-10-16T05:00:00Z",
  }));
}

const plastic: Story = {
  briefing_date: "2026-10-16",
  rank: 1,
  slug: "sample-plastic-treaty",
  title: "Coastal nations sign a treaty to cut ocean plastic by half",
  topic: "Climate",
  region: "Global",
  dek: "Forty-one countries agreed on binding limits for single-use plastic exports. Supporters call it a turning point; critics say enforcement is left to each country.",
  why_it_matters: "Plastic waste reaches every coastline, and this is the largest deal of its kind.",
  agree: "The deal is the largest of its kind, and the 2028 export ban is its strongest part.",
  disagree: "Whether enforcement is strong enough, and who pays the cost of switching.",
  agreement_level: "mixed",
  facts: [
    { text: "Forty-one countries signed the treaty after a week of talks.", refs: [1, 4] },
    { text: "It sets a target of halving plastic waste reaching the sea by 2035.", refs: [2] },
    { text: "Exports of unsorted plastic waste are banned from 2028.", refs: [1] },
    { text: "Each country enforces the rules itself; there is no shared penalty system.", refs: [3] },
  ],
  sources: sources("plastic", [
    ["Sample Left Daily", "United Kingdom", "left"],
    ["Sample Wire", "United States", "center"],
    ["Sample Herald", "Germany", "center"],
    ["Sample Right Times", "United States", "right"],
    ["Sample Coast Post", "Kenya", "center"],
    ["Sample Business Review", "Singapore", "center"],
  ]),
  angles: [
    { position: 0, key: "left", label: "Left", stance: "Overdue, and too easy on producers.", body: "Progressive outlets welcome the deal but argue it targets waste instead of the companies that make plastic, and that leaving enforcement to each country invites delays.", refs: [1] },
    { position: 1, key: "center", label: "Center", stance: "A real step, with an open question on enforcement.", body: "Centrist coverage focuses on what the treaty does and does not require, and notes that similar deals worked when trade rules backed them up.", refs: [2, 3] },
    { position: 2, key: "right", label: "Right", stance: "Good goal, risky for jobs and sovereignty.", body: "Conservative outlets support cleaner oceans but warn of costs for manufacturers and question signing binding international targets.", refs: [4] },
    { position: 3, key: "regional", label: "Global South", stance: "Rich countries are exporting the cleanup.", body: "Outlets on African and Southeast Asian coasts say the 2028 ban is too late, and that poorer coastlines carry most of the cost today.", refs: [5] },
    { position: 4, key: "economic", label: "Economic", stance: "Winners in recycling, losers in packaging.", body: "Business coverage expects investment in recycling and alternative materials, and higher costs for packaging-heavy industries.", refs: [6] },
  ],
};

function brief(rank: number, slug: string, title: string, topic: string, region: string, dek: string, level: Story["agreement_level"]): Story {
  return {
    briefing_date: "2026-10-16",
    rank,
    slug,
    title,
    topic,
    region,
    dek,
    why_it_matters: dek,
    agree: "The basic facts of the event are not disputed.",
    disagree: "What it means and who benefits.",
    agreement_level: level,
    facts: [{ text: dek.split(". ")[0] + ".", refs: [1, 2] }],
    sources: sources(slug, [
      ["Sample Left Daily", "United Kingdom", "left"],
      ["Sample Wire", "United States", "center"],
      ["Sample Right Times", "United States", "right"],
    ]),
    angles: [
      { position: 0, key: "left", label: "Left", stance: "Sample left-leaning view.", body: "How left-leaning coverage frames the story appears here.", refs: [1] },
      { position: 1, key: "center", label: "Center", stance: "Sample centrist view.", body: "How centrist coverage frames the story appears here.", refs: [2] },
      { position: 2, key: "right", label: "Right", stance: "Sample right-leaning view.", body: "How right-leaning coverage frames the story appears here.", refs: [3] },
    ],
  };
}

export const SAMPLE_BRIEFING: Briefing = {
  date: "2026-10-16",
  article_count: 140,
  outlet_count: 24,
  sample: true,
  stories: [
    plastic,
    brief(2, "sample-rates", "Central bank raises rates a quarter point", "Economy", "Americas", "Markets expected the move. The debate is over what it means for mortgages and jobs.", "views split"),
    brief(3, "sample-ai-ads", "New rules require labels on AI-made political ads", "Technology", "Europe", "Regulators say voters deserve to know. Platforms warn the rules are hard to enforce.", "broad agreement"),
    brief(4, "sample-vaccine-plant", "Regional vaccine plant opens after two-year delay", "Health", "Africa", "The plant will supply three neighbouring countries. Cost and ownership are disputed.", "mixed"),
    brief(5, "sample-ceasefire", "Ceasefire talks resume with a new mediator", "Conflict", "Middle East", "Both sides sent delegations. Neighbouring governments describe the stakes very differently.", "views split"),
    brief(6, "sample-solar", "Grid operator plans record solar build-out", "Energy", "Asia-Pacific", "Supporters cite cheaper power. Rural communities worry about land use.", "mixed"),
  ],
};
