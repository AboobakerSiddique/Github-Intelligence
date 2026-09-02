export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-5xl flex-col items-start justify-between gap-2 px-6 py-6 text-xs text-muted sm:flex-row sm:items-center">
        <span>Built on public GitHub data. Not affiliated with GitHub.</span>
        <span className="font-mono">v0.1.0</span>
      </div>
    </footer>
  );
}
