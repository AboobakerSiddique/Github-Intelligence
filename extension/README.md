# GitHub Repository Intelligence — Browser Extension

Injects a repository health score badge directly onto GitHub repo pages,
powered by the same backend as the main dashboard. Click the badge to open
the full analysis.

## Install (unpacked, for development/testing)

1. Open `chrome://extensions` in Chrome (or `edge://extensions` in Edge)
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select this `extension/` folder
5. Visit any public repo, e.g. `https://github.com/vercel/next.js` — a
   badge should appear next to the repo name within a second or two

## Install (for other users, via GitHub release)

1. Go to the [Releases page](https://github.com/AboobakerSiddique/github-intelligence/releases)
   and download the latest `github-intelligence-extension.zip`
2. Extract the `.zip` file to a folder
3. Open `chrome://extensions` in Chrome
4. Enable **Developer mode** (top right toggle)
5. Click **Load unpacked** and select the extracted folder
6. Visit any public GitHub repo — the badge should appear automatically

This installs the extension in "developer mode," which Chrome shows a
small warning banner for — that's expected for extensions not distributed
through the Chrome Web Store, and does not affect functionality.

**Privacy:** see [`PRIVACY.md`](./PRIVACY.md) for what data this extension
sends and why.

## How it works

- `manifest.json` — Manifest V3 config, content script runs on all
  `github.com/*` pages
- `content.js` — detects `owner/repo` from the URL and DOM, calls
  `GET /api/repositories/{owner}/{repo}/analytics` on the backend, and
  injects a badge next to the repo name heading. Re-runs on GitHub's
  Turbo/pjax navigation so it works when browsing between repos without a
  full page reload.
- `content.css` — badge styling, color-coded by health label (Excellent /
  Good / Fair / Needs attention)

v1 scope is intentionally minimal: badge + score, linking back to the full
dashboard. No settings, no popup, no auth.

## Publishing

To ship this to the Chrome Web Store: zip the contents of this folder
(not the folder itself), replace the placeholder icons in `icons/` with
final artwork, and submit via the
[Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole).
