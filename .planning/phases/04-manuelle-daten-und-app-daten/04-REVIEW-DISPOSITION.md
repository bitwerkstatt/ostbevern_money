---
phase: 04
review: 04-REVIEW.md
titles: json
findings:
  - id: WR-04
    severity: warning
    disposition: open
    title: "`_SEITENZAHL_MUSTER` silently drops page numbers from range-style `Quelle:` lines"
  - id: WR-05
    severity: warning
    disposition: open
    title: "CR-01 regression guard (jahr-namespace vs. `jahr` kürzel) exists only in the test suite, not in the pipeline's own validation"
  - id: WR-06
    severity: warning
    disposition: open
    title: "`formatiere()` has no default/exhaustiveness guard — an unexpected kürzel value silently returns `undefined` instead of failing loudly"
  - id: IN-02
    severity: info
    disposition: open
    title: "Haushaltsjahr is duplicated across two independent locations in `texte.json`"
  - id: CR-01
    severity: critical
    disposition: fixed
  - id: WR-01
    severity: warning
    disposition: open
  - id: WR-02
    severity: warning
    disposition: open
  - id: WR-03
    severity: warning
    disposition: open
  - id: IN-01
    severity: info
    disposition: open
open: 8
total: 9
recorded: 2026-10-04T08:41:31.891Z
---

# Phase 04: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| IN-02 | info | open | - |
| CR-01 | critical | fixed | 04-REVIEW.md, behoben in 04-06 (not in the current review) |
| WR-01 | warning | open | 04-REVIEW.md (not in the current review) |
| WR-02 | warning | open | 04-REVIEW.md (not in the current review) |
| WR-03 | warning | open | 04-REVIEW.md (not in the current review) |
| IN-01 | info | open | 04-REVIEW.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
