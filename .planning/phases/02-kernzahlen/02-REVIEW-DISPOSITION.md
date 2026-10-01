---
phase: 02
review: 02-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`_synthetische_pg_datensaetze` keeps a `plantyp` parameter that is now dead code"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`befunde.md`'s Regel-1 sign description is still inverted relative to the code"
  - id: IN-01
    severity: info
    disposition: open
    title: "Duplicate derivation of the D-14 PG-resolution rule in tests vs. production code"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`_pruefe_regel4_b1` can raise an unhandled `IndexError` instead of a clear `PruefungsFehler` if `spalten` and `jahre` ever go out of sync"
  - id: IN-02
    severity: info
    disposition: open
    title: "`lies_befunde`'s hand-rolled Markdown table parser has no defence against a `|` inside `begruendung`"
open: 3
total: 5
recorded: 2026-10-01T16:53:08.685Z
---

# Phase 02: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 02-REVIEW-FIX.md |
| WR-02 | warning | fixed | 02-REVIEW-FIX.md |
| IN-01 | info | open | - |
| WR-03 | warning | open | - (not in the current review) |
| IN-02 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
