import type { RepositoryComparisonEntry } from "@/types/compare";

function Row({
  label,
  left,
  right,
}: {
  label: string;
  left: string | number;
  right: string | number;
}) {
  return (
    <div className="grid grid-cols-3 items-center gap-4 border-b border-border py-2.5 last:border-b-0">
      <span className="font-mono text-sm text-foreground">{left}</span>
      <span className="text-center text-xs text-muted">{label}</span>
      <span className="text-right font-mono text-sm text-foreground">{right}</span>
    </div>
  );
}

export function CompareView({ entries }: { entries: RepositoryComparisonEntry[] }) {
  const [a, b] = entries;
  if (!a || !b) return null;

  const topLanguageA = a.overview.languages[0]?.name ?? "—";
  const topLanguageB = b.overview.languages[0]?.name ?? "—";

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-3 items-baseline gap-4">
        <a
          href={a.overview.html_url}
          target="_blank"
          rel="noreferrer"
          className="font-mono text-lg text-foreground transition-colors hover:text-accent"
        >
          {a.overview.full_name}
        </a>
        <span className="text-center text-xs text-muted">VS</span>
        <a
          href={b.overview.html_url}
          target="_blank"
          rel="noreferrer"
          className="text-right font-mono text-lg text-foreground transition-colors hover:text-accent"
        >
          {b.overview.full_name}
        </a>
      </div>

      <div className="rounded-md border border-border px-5">
        <Row label="Health score" left={`${a.health_score}/100`} right={`${b.health_score}/100`} />
        <Row label="Stars" left={a.overview.stars} right={b.overview.stars} />
        <Row label="Forks" left={a.overview.forks} right={b.overview.forks} />
        <Row label="Open issues" left={a.open_issues} right={b.open_issues} />
        <Row label="Contributors" left={a.contributors_count} right={b.contributors_count} />
        <Row label="Primary language" left={topLanguageA} right={topLanguageB} />
        <Row
          label="License"
          left={a.overview.license_name ?? "None"}
          right={b.overview.license_name ?? "None"}
        />
      </div>
    </div>
  );
}
