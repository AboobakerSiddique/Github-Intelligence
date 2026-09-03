/**
 * Background service worker.
 *
 * Content scripts execute fetch() using the origin of the page they're
 * injected into (https://github.com), so they're still subject to that
 * origin's CORS restrictions. The extension's background context, however,
 * is exempt from CORS for any host declared in `host_permissions` in the
 * manifest — so we proxy the analytics request through here instead.
 */

const API_BASE = "https://github-intelligence.onrender.com";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "FETCH_HEALTH") return false;

  const { owner, repo } = message;

  fetch(`${API_BASE}/api/repositories/${owner}/${repo}/analytics`, {
    headers: { Accept: "application/json" },
  })
    .then((response) => {
      if (!response.ok) throw new Error(`Analytics request failed: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      sendResponse({ ok: true, score: data.health.overall, label: data.health.label });
    })
    .catch((error) => {
      sendResponse({ ok: false, error: String(error) });
    });

  return true; // keep the message channel open for the async sendResponse
});
