---
phase: 02
review: 02-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`befunde.md` header describes the Regel-1 deviation formula with the wrong sign"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Anhang B.3 sollwerte for PB 09/15 Zeile 29 are derived via the same formula the pipeline itself uses, weakening that specific check's independence"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`_pruefe_regel4_b1` can raise an unhandled `IndexError` instead of a clear `PruefungsFehler` if `spalten` and `jahre` ever go out of sync"
  - id: IN-01
    severity: info
    disposition: open
    title: "`REGEL3_ZEILEN` comment only explains a subset of the excluded lines"
  - id: IN-02
    severity: info
    disposition: open
    title: "`lies_befunde`'s hand-rolled Markdown table parser has no defence against a `|` inside `begruendung`"
open: 5
total: 5
recorded: 2026-10-01T15:26:00.127Z
---

# Phase 02: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
