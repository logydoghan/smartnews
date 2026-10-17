export type Leaning = "left" | "center" | "right";
export type AgreementLevel = "broad agreement" | "mixed" | "views split";

export interface Source {
  ref: number;
  url: string;
  title: string;
  outlet: string;
  country: string;
  leaning: Leaning | null;
  published_at: string | null;
}

export interface Fact {
  text: string;
  refs: number[];
}

export interface Angle {
  position: number;
  key: string;
  label: string;
  stance: string;
  body: string;
  refs: number[];
}

export interface Story {
  briefing_date: string;
  rank: number;
  slug: string;
  title: string;
  topic: string;
  region: string;
  dek: string;
  why_it_matters: string;
  agree: string;
  disagree: string;
  agreement_level: AgreementLevel;
  facts: Fact[];
  /** AI illustration made by the image agent; null when it has none. */
  image_url: string | null;
  image_alt: string | null;
  sources: Source[];
  angles: Angle[];
}

export interface Briefing {
  date: string;
  article_count: number;
  outlet_count: number;
  stories: Story[];
  /** True when the site is showing built-in sample stories instead of database content. */
  sample?: boolean;
}

export const REGIONS = ["Americas", "Europe", "Asia-Pacific", "Middle East", "Africa", "Global"] as const;
