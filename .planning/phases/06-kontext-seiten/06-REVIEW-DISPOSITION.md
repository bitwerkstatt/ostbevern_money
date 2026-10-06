---
phase: 06
review: 06-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "Footnote under the Rücklagen table does not reproduce the shown \"Rückgang im Jahr\""
  - id: WR-01
    severity: warning
    disposition: open
    title: "`MenueGruppe.positioniere` measures with the stale offset, so the list is clipped again on every second open and after resize"
  - id: WR-02
    severity: warning
    disposition: open
    title: "\"1 Maßnahmen\" is reachable (and the same pattern exists for \"Produkte\")"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`berechnet` flag applied to one Schulden tile but hard-coded `false` on its sibling"
  - id: WR-04
    severity: warning
    disposition: open
    title: "`baueRuecklagen` presents a partial sum as \"Summe\" when one Rücklage is missing"
  - id: WR-05
    severity: warning
    disposition: open
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

Alle 14 Befunde aus 06-REVIEW.md (1 critical, 5 warning, 8 info) sind offen und noch nicht triagiert.
