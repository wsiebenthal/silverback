/**
 * MV3 service worker.
 *
 * Today this worker handles messages from the extension itself (the popup
 * test button, or chrome.runtime.sendMessage from an extension page).
 * The desktop app does not send those messages yet. Native messaging is
 * planned; see ROADMAP.md.
 */

import { planTabAction } from "./tab_policy.js";

const DEFAULTS = {
  switchPatterns: [],
  closePatterns: [],
  safeUrl: "about:blank",
};

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message || message.type !== "privacy_trigger") {
    return;
  }
  if (message.state && message.state !== "approach") {
    sendResponse({ ok: true, ignored: true, state: message.state });
    return;
  }
  applyApproach()
    .then((plan) => sendResponse({ ok: true, plan }))
    .catch((error) => sendResponse({ ok: false, error: String(error) }));
  return true;
});

async function applyApproach() {
  const settings = await chrome.storage.local.get(DEFAULTS);
  const tabs = await chrome.tabs.query({});
  const plan = planTabAction(tabs, settings);
  if (plan.closeTabIds.length > 0) {
    await chrome.tabs.remove(plan.closeTabIds);
  }
  if (plan.activateTabId != null) {
    await chrome.tabs.update(plan.activateTabId, { active: true });
    await focusWindow(plan.activateWindowId);
  } else if (plan.createSafeTab) {
    await chrome.tabs.create({ url: plan.safeUrl || "about:blank" });
  }
  return plan;
}

async function focusWindow(windowId) {
  if (windowId == null || !chrome.windows) {
    return;
  }
  try {
    await chrome.windows.update(windowId, { focused: true });
  } catch (_error) {
    // The tab is already active. Focusing its window is best-effort.
  }
}
