import type { Story } from "./types";

/** "Finance · Interest rates", or just "Health" when the topic repeats the section. */
export function sectionLabel({ category, topic }: Pick<Story, "category" | "topic">): string {
  return topic && topic.toLowerCase() !== category.toLowerCase() ? `${category} · ${topic}` : category;
}

export function formatBriefingDate(isoDate: string): string {
  // Parse as UTC so the calendar date never shifts with the server's time zone.
  return new Date(`${isoDate}T00:00:00Z`).toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function plural(count: number, word: string, pluralWord = `${word}s`): string {
  return `${count} ${count === 1 ? word : pluralWord}`;
}
