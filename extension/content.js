/**
 * GitHub Repository Intelligence — content script.
 *
 * Detects repo pages on github.com, calls the existing
 * /api/repositories/{owner}/{repo}/analytics endpoint, and injects a small
 * health score badge next to the repository name. Clicking the badge opens
 * the full dashboard.
 */

const DASHBOARD_BASE = "https://github-intelligence-nine.vercel.app";
const BADGE_ID = "ghi-health-badge";

// Reserved top-level GitHub paths that are never a repo owner.
const RESERVED_OWNERS = new Set([
  "marketplace", "notifications", "settings", "explore", "topics",
  "trending", "sponsors", "issues", "pulls", "dashboard", "new", "orgs",
  "apps", "about", "pricing", "features", "security", "contact", "join",
  "login", "session", "codespaces", "gists", "search", "watching", "stars",
]);

/** Parses owner/repo from the current URL, returns null if not a repo page. */
function getOwnerRepoFromUrl() {
  const segments = window.location.pathname.split("/").filter(Boolean);
  if (segments.length < 2) return null;
  const [owner, repo] = segments;
  if (RESERVED_OWNERS.has(owner.toLowerCase())) return null;
  return { owner, repo };
}

/** Finds the repo name heading GitHub renders on every repo page. */
function findRepoNameElement() {
  // GitHub has changed this markup multiple times across redesigns.
  // Try current selector first, then fall back to older ones for safety.
  return (
    document.querySelector("h1.heading-element") ||
    document.querySelector('strong[itemprop="name"]') ||
    document.querySelector('[data-testid="repository-title"]') ||
    null
  );
}

function removeExistingBadge() {
  const existing = document.getElementById(BADGE_ID);
  if (existing) existing.remove();
}

function labelToClass(label) {
  const normalized = (label || "").toLowerCase();
  if (normalized === "excellent") return "ghi-excellent";
  if (normalized === "good") return "ghi-good";
  if (normalized === "fair") return "ghi-fair";
  return "ghi-attention";
}

function renderBadge(anchorEl, { state, owner, repo, score, label }) {
  removeExistingBadge();

  const badge = document.createElement("a");
  badge.id = BADGE_ID;
  badge.className = "ghi-badge";
  badge.target = "_blank";
  badge.rel = "noopener noreferrer";
  badge.href = `${DASHBOARD_BASE}/analyze/${owner}/${repo}`;
  badge.title = "View full report on GitHub Repository Intelligence";

  if (state === "loading") {
    badge.classList.add("ghi-loading");
    badge.textContent = "Health: …";
  } else if (state === "error") {
    badge.classList.add("ghi-attention");
    badge.textContent = "Health: N/A";
  } else {
    badge.classList.add(labelToClass(label));
    badge.textContent = `Health: ${score} · ${label}`;
  }

  // Insert inline if the anchor is a heading (so badge sits next to the
  // text rather than dropping to its own line); otherwise insert after.
  if (anchorEl.tagName === "H1") {
    anchorEl.appendChild(badge);
  } else {
    anchorEl.insertAdjacentElement("afterend", badge);
  }
}

async function fetchHealth(owner, repo) {
  const response = await chrome.runtime.sendMessage({ type: "FETCH_HEALTH", owner, repo });
  if (!response || !response.ok) {
    throw new Error(response?.error || "Analytics request failed");
  }
  return { score: response.score, label: response.label };
}

let lastKey = null;

async function injectBadge() {
  const target = getOwnerRepoFromUrl();
  const nameEl = findRepoNameElement();
  if (!target || !nameEl) {
    removeExistingBadge();
    lastKey = null;
    return;
  }

  const key = `${target.owner}/${target.repo}`;
  if (key === lastKey && document.getElementById(BADGE_ID)) return;
  lastKey = key;

  renderBadge(nameEl, { state: "loading", ...target });

  try {
    const health = await fetchHealth(target.owner, target.repo);
    // Re-check we're still on the same repo (user may have navigated away).
    if (lastKey !== key) return;
    const currentNameEl = findRepoNameElement();
    if (currentNameEl) renderBadge(currentNameEl, { state: "ready", ...target, ...health });
  } catch {
    if (lastKey !== key) return;
    const currentNameEl = findRepoNameElement();
    if (currentNameEl) renderBadge(currentNameEl, { state: "error", ...target });
  }
}

// GitHub is a Turbo (formerly pjax) SPA — full page loads are rare after the
// first visit, so we re-run on Turbo navigation events plus a DOM fallback.
document.addEventListener("turbo:load", injectBadge);
document.addEventListener("pjax:end", injectBadge);

const observer = new MutationObserver(() => {
  if (!document.getElementById(BADGE_ID) && getOwnerRepoFromUrl() && findRepoNameElement()) {
    injectBadge();
  }
});
observer.observe(document.body, { childList: true, subtree: true });

injectBadge();
