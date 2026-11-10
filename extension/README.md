# Browser extension

A Manifest V3 extension for Chrome and Firefox. It keeps a list of tab patterns. When it receives an approach message it can close matching tabs and switch away from a sensitive active tab.

The desktop app does not send that message yet. Native messaging is planned and tracked in [ROADMAP.md](../ROADMAP.md). Until then, use the toolbar popup button **Send test trigger** to exercise the worker.

## Load it

There is no build step.

Chrome: open `chrome://extensions`, turn on Developer mode, choose **Load unpacked**, and select this `extension/` directory.

Firefox 128 or newer: open `about:debugging#/runtime/this-firefox`, choose **Load Temporary Add-on**, and select `manifest.json`. The id `silverback@wsiebenthal.github.io` is a local development id. Replace it before any store listing. Firefox temporary add-ons disappear when the browser closes.

## Patterns

Open **Tab patterns** from the popup.

- **Switch** patterns change focus when the active tab's URL or title contains the text.
- **Close** patterns remove matching tabs, including ones in the background.
- When the active tab has to go and nothing safe is left, the extension opens the safe URL (`about:blank` unless you change it).

Matching is a case-insensitive substring. The decision lives in `src/tab_policy.js` and is covered by `tests/tab_policy.test.js`. `src/background.js` is the part that calls `chrome.tabs`.

```bash
node --test extension/tests/*.test.js
```

Run that from the repository root.
