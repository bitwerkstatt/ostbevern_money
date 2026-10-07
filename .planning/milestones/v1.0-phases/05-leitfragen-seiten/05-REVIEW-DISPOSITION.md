---
phase: 05
review: 05-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`rd.` rule is only half migrated; the new non-breaking space and `EuroBetrag` coexist with five older copies"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`DatenTabelle` makes the scroll container focusable without a role or name when `beschriftung` is missing"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "`alsRgb` rejects a valid colour that happens to normalise to the marker"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`DatenTabelle` only re-observes on `laedt` / `istLeer` / `istDatenModus` changes, not on slot-mode content swaps"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "Edge-tooltip test has a vacuous negative assertion"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "The token guard cannot see dynamic token names and only reads Web Awesome's global stylesheets"
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
    disposition: fixed
    title: "Mobile drawer stays open after clicking the link of the current page"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "Lesehilfe states \"Erträge und Aufwendungen gleichen sich … genau aus\" even when only the Minderaufwand closes the gap"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "`minderaufwandHinweis` can print a negative \"Minderaufwand\""
  - id: IN-08
    severity: info
    disposition: fixed
    title: "`EbenenTabelle` silently drops the per-capita column when `einwohner` is not a number"
  - id: IN-09
    severity: info
    disposition: fixed
    title: "Placeholder contact data and PDF URL are live links, guarded only by a comment"
  - id: IN-10
    severity: info
    disposition: fixed
    title: "Digit rule in `pruefe_text` lets hand-typed numbers between 1900 and 2099 through"
  - id: IN-11
    severity: info
    disposition: fixed
    title: "Documentation and tooling drift"
open: 0
total: 18
recorded: 2026-10-05T18:00:34.075Z
---

# Phase 05: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | fixed in 08-02 (dde7341), 08-04 (39efb8f, fdd22d7, d848102), 08-07 (9994371); rd.-Regel nur noch in format.ts, Wächter gegen neue Kopien |
| WR-02 | warning | fixed | fixed in 08-06 (fe416ab), Tabellenrahmen mit Rolle und genau einem Namen (D-19) |
| IN-01 | info | fixed | fixed in 08-09 (b9d3a68), Flächenfarbe nur aus echartsTheme, zwei Marker |
| IN-02 | info | fixed | fixed in 08-06 (fe416ab), Slot-Modus entfernt (D-16), der Befund ist gegenstandslos |
| IN-03 | info | fixed | fixed in 08-02 (dde7341), der Kanten-Tooltip-Test prüft den Betrag |
| IN-04 | info | fixed | fixed in 08-07 (567fde7), Grenzen des Token-Wächters getestet |
| WR-03 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-05 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-06 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| WR-07 | warning | fixed | 05-REVIEW-FIX.md (not in the current review) |
| IN-05 | info | fixed | fixed in 08-06 (df0d2b0), Drawer schließt bei jedem Link, Fokus auf h1 (D-21) (not in the current review) |
| IN-06 | info | fixed | fixed in 08-02 (d5f9cdf, 5e959de), die Lesehilfe sagt genau nur bei echtem Ausgleich (D-06) (not in the current review) |
| IN-07 | info | fixed | fixed in 53b96ac (Phase 7) und 08-02 (9f9c367, de7fe83), gemeinsame Minderaufwand-Regel, positiver Z. 27 wirft (D-08) (not in the current review) |
| IN-08 | info | fixed | fixed in 08-03 (2a8e5a5, 52c1ee7), einwohnerZahl wirft laut (D-09) (not in the current review) |
| IN-09 | info | fixed | fixed in Phase 7 (1ab6b4b, b29be89, f4fad93), echte Kontaktdaten und PDF-URL, Test über alle vier Konfigurationswerte, Smoke-Test mit axe je Route (D-17) (not in the current review) |
| IN-10 | info | fixed | fixed in 08-01 (7d4be31, 27e0be7, c27904b), getippte Jahreszahlen werden abgelehnt, Platzhalter statt fester Jahre (D-01) (not in the current review) |
| IN-11 | info | fixed | fixed in 08-08 (28462a7, c1da62e), CI-Block und ci.yml-Kopf aktuell, Glossar-Invariante absaetze[0] geprüft; @types/node war schon erledigt (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

Previous review (ce51941): the first review round of phase 5 reported other findings under the ids IN-01 to IN-04 (and WR-01, WR-02). They were still open when the current review reused the ids, so they were replaced by id reuse and have no row of their own. They are not part of the 28 findings of phase 8 and no plan of phase 8 fixed them; they are reported to the user in 08-12-SUMMARY.md for a decision. State of each in the code at the end of phase 8: (1) latent „-0 €“ and „-0 %“ from `proKopf` (`lib/berechnung.ts`) and `Intl` — still present, no data case today; (2) hard-coded superlative „Der größte Einzelposten ist die Weitergabe an Kreis und Land“ in `KreisumlageCallout.vue` — still present, true for every year today; (3) „PDF-Seite“ in the singular for several pages in `ErklaerText.vue` (`quelle_seiten.join`) — still present; (4) redirect watcher registered in every call of `useJahr` (`lib/jahr.ts`) — still present, converges. The two warnings of that round (Sankey amounts without „rd.“ or „berechnet“, Start page claim about the largest Aufgabenbereich) no longer exist in the code: `GeldflussKnoten` carries `gerundet` and `berechnet`, and the Start page sentence reads „Ohne die Weitergabe an Kreis und Land …“.
