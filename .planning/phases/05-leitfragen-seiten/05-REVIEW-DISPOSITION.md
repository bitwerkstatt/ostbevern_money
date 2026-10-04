---
phase: 05
review: 05-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Geldfluss shows Vorbericht-derived amounts as exact euros, without \"rd.\" or \"berechnet\""
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "Start page says \"Den größten Anteil bekommt Innere Verwaltung\", but Weitergabe an Kreis und Land is more than twice as large"
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
  - id: IN-01
    severity: info
    disposition: open
    title: "Latent \"-0 €\" and \"-0 %\" output from `proKopf` and `Intl`"
  - id: IN-02
    severity: info
    disposition: open
    title: "Hard-coded superlative in the Kreisumlage callout"
  - id: IN-03
    severity: info
    disposition: open
    title: "\"Quelle: PDF-Seite 51, 8\" – singular for several pages, unsorted order"
  - id: IN-04
    severity: info
    disposition: open
    title: "Page-wide `useJahr` registers a redirect watcher in every component that calls it"
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
open: 11
total: 18
recorded: 2026-10-04T21:17:52.220Z
---

# Phase 05: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 05-REVIEW-FIX.md |
| WR-02 | warning | fixed | 05-REVIEW-FIX.md |
| WR-03 | warning | fixed | 05-REVIEW-FIX.md |
| WR-04 | warning | fixed | 05-REVIEW-FIX.md |
| WR-05 | warning | fixed | 05-REVIEW-FIX.md |
| WR-06 | warning | fixed | 05-REVIEW-FIX.md |
| WR-07 | warning | fixed | 05-REVIEW-FIX.md |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |
| IN-10 | info | open | - |
| IN-11 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
