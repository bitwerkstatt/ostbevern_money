---
phase: 06
review: 06-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "Fußnote \"zuzüglich der Verrechnung\" nennt das Vorzeichen nicht; wörtlich angewandt ergibt sie eine andere Zahl (Restmangel von CR-01)"
  - id: IN-01
    severity: info
    disposition: open
    title: "Hard-coded hex fallback colors in components"
  - id: IN-02
    severity: info
    disposition: open
    title: "Dead or test-only production exports"
  - id: IN-03
    severity: info
    disposition: open
    title: "Duplicated helpers across lib modules"
  - id: IN-04
    severity: info
    disposition: open
    title: "Cross-module coupling for small helpers"
  - id: IN-05
    severity: info
    disposition: open
    title: "`useMassnahmenFilter` is instantiated twice per page"
  - id: IN-06
    severity: info
    disposition: open
    title: "Minor markup and equality nits"
  - id: IN-07
    severity: info
    disposition: open
    title: "Derived sum shown without \"berechnet\" label; source line cites all pages on every tile"
  - id: IN-08
    severity: info
    disposition: open
    title: "Pipeline formulas raise untyped errors"
  - id: IN-09
    severity: info
    disposition: open
    title: "Neue Tests prüfen Quelltext statt Verhalten"
open: 10
total: 10
recorded: 2026-10-06T08:17:24.991Z
---

# Phase 06: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
