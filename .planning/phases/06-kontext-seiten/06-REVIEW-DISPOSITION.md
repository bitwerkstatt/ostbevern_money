---
phase: 06
review: 06-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Footnote under the Rücklagen table does not reproduce the shown \"Rückgang im Jahr\""
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`MenueGruppe.positioniere` measures with the stale offset, so the list is clipped again on every second open and after resize"
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
---

# Phase 06 — Code-Review-Disposition

CR-01 und WR-01 bis WR-05 sind behoben: CR-01 und WR-04 in 06-13, WR-01 in 06-14, WR-02 in 06-15, WR-03 und WR-05 in 06-16; Nachweis im CI-identischen Gate von 06-17 (06-17-SUMMARY.md). Die acht Infos IN-01 bis IN-08 bleiben offen (Scope-Entscheidung des Gap-Laufs: nicht zielrelevant).
