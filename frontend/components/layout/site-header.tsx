import Link from "next/link";
import { Terminal } from "lucide-react";

export function SiteHeader() {
  return (
    <header className="border-b border-border">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2 text-sm font-medium">
          <Terminal className="h-4 w-4 text-accent" strokeWidth={2} />
          <span className="font-mono">github-intelligence</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm text-muted">
          <Link href="/" className="transition-colors hover:text-foreground">
            Analyze
          </Link>
          <Link href="/compare" className="transition-colors hover:text-foreground">
            Compare
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}
