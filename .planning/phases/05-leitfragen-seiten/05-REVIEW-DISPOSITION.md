---
phase: 05
review: 05-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`Quelle:` page lists without a repeated `S.` are still silently truncated (incomplete fix of the old WR-04)"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`DatenTabelle` overflow detection observes only the elements present at mount"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "`alsRgb` turns an unparseable colour into black without a signal"
  - id: IN-02
    severity: info
    disposition: open
    title: "Scroll region without `beschriftung` is never keyboard-focusable; the new overflow logic has no test"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "Regel 5 still skips the Kreisumlage check silently when `meta` is `None`"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "The \"rd.\" / \"berechnet\" cell template is copy-pasted three times; the space after \"rd.\" can wrap"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "`mitDeckkraft` silently ignores every non-hex colour, so the decal opacity from the design never applies"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`lies_erklaerungen` / `lies_glossar` silently drop page ranges in `Quelle:` lines"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "Konzessionsabgaben check is silently skipped when `meta` is absent; Regel 5 then reports a clean pass"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "Fixed-year shape in `texte.py` formulas: KeyError instead of `TexteFehler`, and every formula runs even when unused"
  - id: WR-07
    severity: warning
    disposition: fixed
    title: "`DatenTabelle` makes every captioned table a tab stop and duplicates its name for screen readers"
  - id: IN-05
    severity: info
    disposition: open
    title: "Mobile drawer stays open after clicking the link of the current page"
  - id: IN-06
    severity: info
    disposition: open
    title: "Lesehilfe states \"Erträge und Aufwendungen gleichen sich … genau aus\" even when only the Minderaufwand closes the gap"
  - id: IN-07
    severity: info
    disposition: open
    title: "`minderaufwandHinweis` can print a negative \"Minderaufwand\""
  - id: IN-08
    severity: info
    disposition: open
    title: "`EbenenTabelle` silently drops the per-capita column when `einwohner` is not a number"
  - id: IN-09
    severity: info
    disposition: open
    title: "Placeholder contact data and PDF URL are live links, guarded only by a comment"
  - id: IN-10
    severity: info
    disposition: open
    title: "Digit rule in `pruefe_text` lets hand-typed numbers between 1900 and 2099 through"
  - id: IN-11
    severity: info
    disposition: open
    title: "Documentation and tooling drift"
open: 9
total: 18
recorded: 2026-10-05T05:19:26.707Z
---

# Phase 05: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | fixed | 05-REVIEW-FIX.md |
| IN-01 | info | fixed | 05-REVIEW-FIX.md |
| IN-02 | info | open | - |
| IN-03 | info | fixed | 05-REVIEW-FIX.md |
| IN-04 | info | fixed | 05-REVIEW-FIX.md |
| WR-03 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-05 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-06 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-07 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| IN-05 | info | open | - (not in the current review) |
| IN-06 | info | open | - (not in the current review) |
| IN-07 | info | open | - (not in the current review) |
| IN-08 | info | open | - (not in the current review) |
| IN-09 | info | open | - (not in the current review) |
| IN-10 | info | open | - (not in the current review) |
| IN-11 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
