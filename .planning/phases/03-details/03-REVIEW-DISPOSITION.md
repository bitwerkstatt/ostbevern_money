---
phase: 03
review: 03-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`ordne_spalten` tolerance is computed globally, not per-anchor-pair — a single duplicate anchor breaks column assignment for the whole table"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`test_alle.py` mocks `extrahiere_produkte` with a 2-tuple, but the real function returns a 3-tuple"
  - id: IN-01
    severity: info
    disposition: open
    title: "`alle.py` reuses the \"Schritt 06\" label for two unrelated operations, inconsistent with `06_pruefen.py`'s own labeling of the same step"
  - id: IN-02
    severity: info
    disposition: open
    title: "CLI help text for `03_produktinfos.py` / `04_investitionen.py` doesn't mention all artifacts the command actually writes"
  - id: IN-03
    severity: info
    disposition: open
    title: "`schreibe_csv` relies on a blind `.cast(spalten)` that can silently coerce/truncate mismatched types instead of failing loud"
open: 3
total: 5
recorded: 2026-10-02T08:26:58.078Z
---

# Phase 03: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 03-REVIEW-FIX.md |
| WR-02 | warning | fixed | 03-REVIEW-FIX.md |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
