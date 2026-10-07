---
phase: 06
review: 06-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Footnote under the Rücklagen table does not reproduce the shown \"Rückgang im Jahr\""
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "\"1 Maßnahmen\" is reachable (and the same pattern exists for \"Produkte\")"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "`berechnet` flag applied to one Schulden tile but hard-coded `false` on its sibling"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`baueRuecklagen` presents a partial sum as \"Summe\" when one Rücklage is missing"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "Nachwuchs person counts treat a missing `personen` as 0"
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
total: 15
recorded: 2026-10-06T08:17:24.991Z
---

# Phase 06: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | fixed in 06-13 (gate 06-17); remainder re-reported as WR-01 |
| WR-02 | warning | fixed | fixed in 06-15 (gate 06-17) |
| WR-03 | warning | fixed | fixed in 06-16 (gate 06-17) |
| WR-04 | warning | fixed | fixed in 06-13 (gate 06-17) |
| WR-05 | warning | fixed | fixed in 06-16 (gate 06-17) |
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

Previous review (c193e3f): CR-01 and WR-04 fixed in 06-13, WR-01 (menu offset) fixed in 06-14, WR-02 in 06-15, WR-03 and WR-05 in 06-16; evidence: CI-identical gate in 06-17-SUMMARY.md and the re-review 06-REVIEW.md. The id WR-01 is reused by the current review for the CR-01 remainder (footnote sign wording), so the earlier WR-01 decision is recorded here rather than as a row.
