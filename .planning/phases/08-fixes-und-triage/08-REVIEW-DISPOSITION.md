---
phase: 08
review: 08-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "The new WR-03 render tests cannot fail, because SSR never produces an overflowing frame"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Blank `beschriftung` silently trades the unnamed region for a keyboard-inaccessible scroll area"
  - id: IN-01
    severity: info
    disposition: open
    title: "Source-text regex tests are fragile against formatting"
  - id: IN-02
    severity: info
    disposition: open
    title: "`pruefeLinkMitZusatztaste` asserts the h1 focus before the code under test could have moved it"
  - id: IN-03
    severity: info
    disposition: open
    title: "`_pruefe_jahrbezug` checks a paragraph as a set, not pair by pair; `Titel` is not covered"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "`DatenTabelle` accepts an empty `beschriftung`, producing an unnamed scroll region with no guard left"
  - id: IN-04
    severity: info
    disposition: open
    title: "Unusual rest-tuple signature for `einwohnerZahl`"
  - id: IN-05
    severity: info
    disposition: open
    title: "`quellenZeile` renders a dangling separator for an empty page list"
  - id: IN-06
    severity: info
    disposition: open
    title: "Fixed 500 ms sleep in the table-frame e2e helper"
  - id: IN-07
    severity: info
    disposition: open
    title: "`rdregel` guard covers only \"rd.\", not the \"rund\" prefix; comment stripping can hide copies"
open: 9
total: 10
recorded: 2026-10-08T18:19:18.615Z
---

# Phase 08: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| WR-03 | warning | fixed | 08-REVIEW-FIX.md (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-05 | info | open | - (not in the current review) |
| IN-06 | info | open | - (not in the current review) |
| IN-07 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
