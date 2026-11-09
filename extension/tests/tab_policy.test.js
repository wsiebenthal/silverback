import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { planTabAction } from "../src/tab_policy.js";

const root = path.resolve(import.meta.dirname, "..");

function tab(id, extras = {}) {
  return {
    id,
    windowId: 1,
    url: `https://example.test/${id}`,
    title: `Tab ${id}`,
    active: false,
    ...extras,
  };
}

test("empty patterns leave tabs alone", () => {
  const plan = planTabAction([tab(1, { active: true }), tab(2)], {});
  assert.deepEqual(plan.closeTabIds, []);
  assert.equal(plan.activateTabId, null);
  assert.equal(plan.createSafeTab, false);
  assert.equal(plan.safeUrl, "about:blank");
});

test("switches from a sensitive active tab to a safe tab in the same window", () => {
  const tabs = [
    tab(1, { active: true, url: "https://calendar.example/day", windowId: 1 }),
    tab(2, { url: "https://other.example/", windowId: 2 }),
    tab(3, { url: "https://notes.example/", windowId: 1 }),
  ];
  const plan = planTabAction(tabs, { switchPatterns: ["Calendar.Example"] });
  assert.deepEqual(plan.closeTabIds, []);
  assert.equal(plan.activateTabId, 3);
  assert.equal(plan.activateWindowId, 1);
  assert.equal(plan.createSafeTab, false);
});

test("uses another window when the same window has no safe tab", () => {
  const tabs = [
    tab(1, { active: true, url: "https://bank.example/", windowId: 1 }),
    tab(2, { url: "https://bank.example/pay", windowId: 1 }),
    tab(3, { url: "https://news.example/", windowId: 4 }),
  ];
  const plan = planTabAction(tabs, { switchPatterns: ["bank.example"] });
  assert.equal(plan.activateTabId, 3);
  assert.equal(plan.activateWindowId, 4);
});

test("asks for a safe tab when every tab matches", () => {
  const tabs = [
    tab(1, { active: true, title: "Inbox" }),
    tab(2, { title: "Inbox draft" }),
  ];
  const plan = planTabAction(tabs, { switchPatterns: ["inbox"], safeUrl: "about:blank" });
  assert.equal(plan.activateTabId, null);
  assert.equal(plan.createSafeTab, true);
  assert.equal(plan.safeUrl, "about:blank");
});

test("closes matching background tabs without stealing focus", () => {
  const tabs = [
    tab(1, { active: true, url: "https://news.example/" }),
    tab(2, { url: "https://draft.example/secret" }),
  ];
  const plan = planTabAction(tabs, { closePatterns: ["draft.example"] });
  assert.deepEqual(plan.closeTabIds, [2]);
  assert.equal(plan.activateTabId, null);
  assert.equal(plan.createSafeTab, false);
});

test("closes the active tab and activates a survivor", () => {
  const tabs = [
    tab(1, { active: true, url: "https://draft.example/" }),
    tab(2, { url: "https://news.example/" }),
  ];
  const plan = planTabAction(tabs, { closePatterns: ["draft.example"] });
  assert.deepEqual(plan.closeTabIds, [1]);
  assert.equal(plan.activateTabId, 2);
  assert.equal(plan.createSafeTab, false);
});

test("closes every tab and opens a safe page", () => {
  const tabs = [tab(1, { active: true, url: "https://draft.example/a" }), tab(2, { url: "https://draft.example/b" })];
  const plan = planTabAction(tabs, { closePatterns: ["draft.example"], safeUrl: "https://safe.example/" });
  assert.deepEqual(plan.closeTabIds, [1, 2]);
  assert.equal(plan.activateTabId, null);
  assert.equal(plan.createSafeTab, true);
  assert.equal(plan.safeUrl, "https://safe.example/");
});

test("matches titles and ignores blank patterns", () => {
  const tabs = [tab(1, { active: true, title: "Quarterly Review" }), tab(2)];
  const plan = planTabAction(tabs, { switchPatterns: ["  ", "review"] });
  assert.equal(plan.activateTabId, 2);
});

test("a sensitive background tab does not change focus", () => {
  const tabs = [
    tab(1, { active: true, url: "https://news.example/" }),
    tab(2, { url: "https://bank.example/" }),
  ];
  const plan = planTabAction(tabs, { switchPatterns: ["bank.example"] });
  assert.equal(plan.activateTabId, null);
  assert.deepEqual(plan.closeTabIds, []);
});

test("manifest points at files that exist", () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, "manifest.json"), "utf8"));
  assert.equal(manifest.manifest_version, 3);
  assert.equal(manifest.background.type, "module");
  const files = [
    manifest.background.service_worker,
    manifest.action.default_popup,
    manifest.options_ui.page,
    manifest.icons["16"],
    manifest.icons["48"],
    manifest.icons["128"],
  ];
  for (const file of files) {
    assert.equal(fs.existsSync(path.join(root, file)), true, file);
  }
});
