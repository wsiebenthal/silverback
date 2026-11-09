/**
 * Decide which tabs to close or leave when an approach trigger arrives.
 *
 * This module is pure: no chrome.* calls. background.js performs the plan.
 * Patterns are case-insensitive substrings of the tab URL or title.
 */

export function planTabAction(tabs, settings) {
  const switchPatterns = normalize(settings && settings.switchPatterns);
  const closePatterns = normalize(settings && settings.closePatterns);
  const safeUrl = (settings && settings.safeUrl) || "about:blank";
  const list = Array.isArray(tabs) ? tabs : [];

  const closeTabIds = list.filter((tab) => matches(tab, closePatterns)).map((tab) => tab.id);
  const closing = new Set(closeTabIds);
  const remaining = list.filter((tab) => !closing.has(tab.id));
  const active = list.find((tab) => tab.active) || null;
  const activeIsClosing = Boolean(active && closing.has(active.id));
  const activeNeedsSwitch = Boolean(active && !activeIsClosing && matches(active, switchPatterns));

  let activate = null;
  let createSafeTab = false;
  if (activeIsClosing || activeNeedsSwitch) {
    activate = pickSafe(remaining, active.windowId, switchPatterns, active.id);
    if (!activate) {
      createSafeTab = true;
    }
  } else if (remaining.length === 0 && closeTabIds.length > 0) {
    createSafeTab = true;
  }

  return {
    closeTabIds,
    activateTabId: activate ? activate.id : null,
    activateWindowId: activate ? activate.windowId ?? null : null,
    createSafeTab,
    safeUrl,
  };
}

function pickSafe(remaining, windowId, patterns, avoidId) {
  const safe = remaining.filter((tab) => tab.id !== avoidId && !matches(tab, patterns));
  return safe.find((tab) => tab.windowId === windowId) || safe[0] || null;
}

function matches(tab, patterns) {
  if (!patterns.length || !tab) {
    return false;
  }
  const haystack = `${tab.url || ""}\n${tab.title || ""}`.toLowerCase();
  return patterns.some((pattern) => haystack.includes(pattern));
}

function normalize(patterns) {
  if (!Array.isArray(patterns)) {
    return [];
  }
  return patterns.map((pattern) => String(pattern).trim().toLowerCase()).filter((pattern) => pattern.length > 0);
}
