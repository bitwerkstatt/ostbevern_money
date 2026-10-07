---
phase: 04
review: 04-REVIEW.md
titles: json
findings:
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`_SEITENZAHL_MUSTER` silently drops page numbers from range-style `Quelle:` lines"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "CR-01 regression guard (jahr-namespace vs. `jahr` kürzel) exists only in the test suite, not in the pipeline's own validation"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "`formatiere()` has no default/exhaustiveness guard — an unexpected kürzel value silently returns `undefined` instead of failing loudly"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "Haushaltsjahr is duplicated across two independent locations in `texte.json`"
  - id: CR-01
    severity: critical
    disposition: fixed
  - id: WR-01
    severity: warning
    disposition: fixed
  - id: WR-02
    severity: warning
    disposition: fixed
  - id: WR-03
    severity: warning
    disposition: fixed
  - id: IN-01
    severity: info
    disposition: fixed
open: 0
total: 9
recorded: 2026-10-04T08:41:31.891Z
---

# Phase 04: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-04 | warning | fixed | Quelle-Zeilen mit Seitenspannen brechen ab: commit 9d18267 (fix 05, `_QUELLE_ERLAUBT_MUSTER` prüft die ganze Zeile), vorher e3a2122; Tests `test_lies_erklaerungen_lehnt_seitenspannen_in_der_quelle_ab` in 07-02 erneut bestätigt |
| WR-05 | warning | fixed | commit d53ffc7 (07-02): `pruefe_text` verlangt für `jahr.`-Platzhalter das Formatkürzel jahr, Test `test_pruefe_text_jahr_platzhalter_braucht_formatkuerzel_jahr` |
| WR-06 | warning | fixed | commit 65cd6d8 (05-01): `formatiere` wirft bei unbekanntem Kürzel (exhaustiver `never`-Guard), in 07-02 gegen `app/src/charts/format.ts` verifiziert |
| IN-02 | info | fixed | commit d53ffc7 (07-02): `pruefe_texte_haushaltsjahr` vergleicht `haushaltsjahr` mit `werte["jahr.haushaltsjahr"]`, beide Felder bleiben in der Datei, Test `test_texte_haushaltsjahr_muss_zu_jahr_wert_passen` |
| CR-01 | critical | fixed | 04-REVIEW.md, behoben in 04-06 (not in the current review) |
| WR-01 | warning | fixed | `ve_uebersicht.csv` per-year summary rows are never cross-checked (frühere Review, commit 1485175): commit d53ffc7 (07-02), `validiere_ve_uebersicht` bricht vor allen Regeln ab, Tests `test_ve_uebersicht_*` |
| WR-02 | warning | fixed | Fragile negative-index fallback in Schuldenstand-Fortschreibung (frühere Review, commit 1485175): commit d53ffc7 (07-02), `schreibe_schuldenstand_fort` wirft `AppDatenFehler`, Test `test_schuldenstand_fortschreibung_ohne_gedruckten_stand_vor_dem_jahr_bricht_ab` |
| WR-03 | warning | fixed | `ABGELEITET`-Formeln in `texte.py` nehmen Nachbarjahre ungeprüft an (frühere Review, commit 1485175): Eingabefehler in 7587fd5 (fix 05, nur in `textwerte`) und in d53ffc7 (07-02) für jede Formel direkt, Test `test_abgeleitete_formel_ohne_eingabewert_nennt_formel_und_schluessel` |
| IN-01 | info | fixed | `formatiere()` has no runtime fallback for an unknown kuerzel (frühere Review, commit 1485175): commit 65cd6d8 (05-01), Strich-Fallback und Fehler bei unbekanntem Kürzel |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

## Nachtrag Phase 7 (D-20)

Triage in Plan 07-02, aus den Review-Dateien und der Git-Historie neu hergeleitet. Die Review-IDs wurden beim erneuten Review wiederverwendet: WR-04, WR-05, WR-06 und IN-02 gehören zur aktuellen `04-REVIEW.md`, die Zeilen WR-01, WR-02, WR-03 und IN-01 zu der früheren Review (Commit 1485175, `04-REVIEW.md`), deren Titel oben in den Source-Zellen stehen. Die Fixes sind reine Guards und Tests: `alle.py --jahr 2026` erzeugt `daten/` und `app/src/data/` ohne Unterschied (D-20), der Konsistenzbericht bleibt byte-identisch.
