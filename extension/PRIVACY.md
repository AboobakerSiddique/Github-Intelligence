# Privacy Policy — GitHub Repository Intelligence Extension

_Last updated: September 2026_

## What this extension does

GitHub Repository Intelligence adds a health score badge to public GitHub
repository pages. When you visit a repository page on github.com, the
extension reads the repository's **owner and name from the page URL** and
sends them to our backend API (`github-intelligence.onrender.com`) to
fetch a health score.

## What data we collect

- **Repository owner/name** (e.g. `vercel/next.js`) — sent to our backend
  solely to look up public repository data via the GitHub API.

We do **not** collect, store, or transmit:
- Your name, email, IP address, or any personally identifiable information
- Your GitHub login, session, cookies, or authentication data
- Browsing history beyond the current repository page being viewed
- Any data from private repositories (the extension only works on pages
  you're already viewing; it does not access private repo content)

## Data storage

The extension does not use local storage, cookies, or any persistent
tracking. Each badge lookup is a single, stateless request — nothing is
retained on our servers beyond standard, temporary server logs used for
debugging and abuse prevention (routinely purged).

## Third parties

Repository/owner names are passed to the [GitHub REST API](https://docs.github.com/en/rest)
by our backend in order to compute the health score. No data is shared
with any other third party, and nothing is sold or used for advertising.

## Permissions

The extension requests:
- **Host permission** for `github-intelligence.onrender.com` — to fetch
  health score data via its own background service worker (required to
  avoid cross-origin restrictions; see [technical note](#technical-note)).
- **Content script access** on `github.com/*` — to detect the repository
  page and display the badge.

No other permissions (bookmarks, history, tabs, downloads, etc.) are
requested.

## Technical note

Analytics requests are made from the extension's background service
worker rather than the content script, purely for technical reasons
(cross-origin request handling) — this does not change what data is sent
or collected.

## Changes to this policy

If this policy changes, the updated version will be posted here and in
the extension's repository.

## Contact

Questions about this policy or the extension can be raised via
[GitHub Issues](https://github.com/AboobakerSiddique/github-intelligence/issues).
