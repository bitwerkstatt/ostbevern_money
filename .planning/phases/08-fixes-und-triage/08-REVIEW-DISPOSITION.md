---
phase: 08
review: 08-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Year label and value key are now decoupled; a new Jahrgang silently produces wrong statements"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "Drawer link click sets the \"closes by navigation\" flag even when no navigation happens"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "`DatenTabelle` accepts an empty `beschriftung`, producing an unnamed scroll region with no guard left"
  - id: IN-01
    severity: info
    disposition: open
    title: "`kurzMitHinweis(..., false)` drops the rounding disclosure of `euroKurz`"
  - id: IN-02
    severity: info
    disposition: open
    title: "`flaechenFarbe()` docstring contradicts how the decals use it"
  - id: IN-03
    severity: info
    disposition: open
    title: "Redundant condition in `lies_glossar`"
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
open: 7
total: 10
recorded: 2026-10-08T05:13:48.256Z
---

# Phase 08: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 08-REVIEW-FIX.md |
| WR-02 | warning | fixed | 08-REVIEW-FIX.md |
| WR-03 | warning | fixed | 08-REVIEW-FIX.md |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
