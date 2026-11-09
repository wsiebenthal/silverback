# Browser extras: private windows, domain hide, and field blur

Labels: `enhancement`, `privacy`

## Description

On a trigger, close private or incognito windows, hide tabs by domain, and blur form fields the user named. Page contents and field values stay on the machine and are not read out or sent.

Roadmap: [Phase 14 — Browser extras](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-browser-extras)

## Acceptance criteria

- Private and incognito windows close on trigger.
- Tabs hide when their domain is on the user's list. Matching uses the domain only.
- A content script blurs selectors the user configured and does not read or transmit field values.
- Tests use fixture pages and domain strings. They do not open a real account.
