import type { LanguageBreakdown } from "@/types/repository";

// A small, deterministic palette keyed by common language names, with a
// neutral fallback — avoids random color assignment across renders.
const LANGUAGE_COLORS: Record<string, string> = {
  Python: "#3B82C4",
  TypeScript: "#4A63E0",
  JavaScript: "#D9B23C",
  Go: "#4CB7A5",
  Rust: "#C24A34",
  Java: "#B8763E",
  "C++": "#A15FBF",
  C: "#7A8598",
  HTML: "#D9724A",
  CSS: "#5F8FC2",
  Shell: "#5FD97A",
  Ruby: "#C2445F",
};
const FALLBACK_COLOR = "#5B6373";

function colorFor(name: string): string {
  return LANGUAGE_COLORS[name] ?? FALLBACK_COLOR;
}

export function LanguageBar({ languages }: { languages: LanguageBreakdown[] }) {
  if (languages.length === 0) {
    return <p className="text-sm text-muted">No language data available.</p>;
  }

  const top = languages.slice(0, 6);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex h-2 w-full overflow-hidden rounded-full bg-surface-raised">
        {top.map((lang) => (
          <div
            key={lang.name}
            style={{ width: `${lang.percentage}%`, backgroundColor: colorFor(lang.name) }}
            title={`${lang.name}: ${lang.percentage}%`}
          />
        ))}
      </div>
      <ul className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs">
        {top.map((lang) => (
          <li key={lang.name} className="flex items-center gap-1.5 text-muted">
            <span
              className="h-2 w-2 shrink-0 rounded-full"
              style={{ backgroundColor: colorFor(lang.name) }}
              aria-hidden
            />
            <span className="font-mono text-foreground">{lang.name}</span>
            <span>{lang.percentage}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
