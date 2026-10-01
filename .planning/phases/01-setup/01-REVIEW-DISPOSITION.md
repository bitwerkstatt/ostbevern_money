---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "No `base` path configured for GitHub Pages project hosting"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`prefers-reduced-motion` is a stated a11y requirement but is implemented nowhere"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Unsafe `as number` casts in `DatenTabelle.vue` with no runtime check against `spalte.art`"
  - id: WR-04
    severity: warning
    disposition: open
    title: "ECharts theme tokens are read once at module load and never update"
  - id: WR-05
    severity: warning
    disposition: open
    title: "`DatenTabelle`'s `spalten` prop is optional but required whenever `zeilen` is passed"
  - id: IN-01
    severity: info
    disposition: open
    title: "Unused icon asset `bars.svg`"
  - id: IN-02
    severity: info
    disposition: open
    title: "Duplicate `pdf_relativ` computation in `alle.py`"
  - id: IN-03
    severity: info
    disposition: open
    title: "`circle-info` icon used inside a `warning`-variant callout"
  - id: IN-04
    severity: info
    disposition: open
    title: "No overlap/positivity validation for Jahrgang config values"
  - id: IN-05
    severity: info
    disposition: open
    title: "Redundant double-labeling of data tables for screen readers"
open: 10
total: 10
recorded: 2026-10-01T09:51:16.231Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
