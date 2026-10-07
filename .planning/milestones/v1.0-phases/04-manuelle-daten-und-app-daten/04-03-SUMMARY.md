---
phase: 04-manuelle-daten-und-app-daten
plan: 03
subsystem: pipeline-and-app-data
tags: [pdfplumber, polars, typer, pytest, koordinatenparser, stellenplan, regel9, regel10, stellenplan-json, vue-tsc]

requires:
  - phase: 04-manuelle-daten-und-app-daten (04-02)
    provides: pruefung.TOLERANZ_JE_REGEL/toleranz_fuer, REGEL9_ECKWERTE-Muster, app_daten.schreibe_app_json, alle.py-Schrittkette bis Querschnitte
provides:
  - ostbevern/stellenplan.py (neu) — Koordinatenparser für S. 284-290: StellenplanFehler, Stellenwert, lies_stellen_hundertstel(text), lies_stellenplan(dokument, jahrgang, *, hierarchie=None), extrahiere_stellenplan(jahrgang, *, daten_wurzel)
  - 05_stellenplan.py (neu) — Schritt 05, dünner typer-Einstieg
  - daten/aufbereitet/stellenplan.csv (162 Zeilen) — Teil A Beamte, Teil B Tarif/Sozial-Erziehungsdienst, Nachwuchskräfte, drei Stellenübersichten nach Produktbereichen, alle gegen die gedruckten Summen-/Insgesamt-Zeilen geprüft
  - Regel 10 "Stellenplan: Stellenübersicht → Teil A/B" (exakt, 0 Hundertstel Toleranz) und der Eckwert stellen_beamte in Regel 9 (Anhang B.6, Beamte 2026 = 8)
  - alle.py Schritt 05 zwischen Querschnitte und Schritt 06 verdrahtet
  - app/src/data/stellenplan.json + typen.ts (StellenplanZeile, Stellenplan) + daten.ts (typisierter stellenplan-Export)
affects: [05, 06]

actuals:
  tokens: 42189
  tasks: 3
  commits: 3
  plan_head_before: e02c6c7b29799467e88218ff6fd9de6a7796368d
  plan_head_after: b3614276266888fab6b3281f4f056d6b671b0dbc

tech-stack:
  added: []
  patterns:
    - "Sparse-Matrix-Spaltenzuordnung (Research Pattern 1): die Stellenübersichten (S. 287-289) verlangen `ordne_spalten` OHNE die aus investitionen.py/querschnitte.py bekannte Vollständigkeitsprüfung — eine fehlende (PB, Gruppe)-Kombination ist 'kein Eintrag', nicht 0"
    - "Zwei-Pass-Zuordnung für wertlose Label-Zeilen: Gruppen-Label und Werte können auf unterschiedlichen `top`-Zeilen stehen (S. 285 EG 9c/9b/9a); ein zweiter Durchlauf ordnet unzugeordnete Wertzeilen der nächstgelegenen Gruppe per |Δtop| <= 8.0pt (eindeutiges Minimum) zu"
    - "Hundertstel-exaktes String-Parsing (D-18): lies_stellen_hundertstel arbeitet nie mit round(float*100), sondern zerlegt die gedruckte Zeichenkette (Ganzzahl-/Dezimalteil, auf 2 Stellen aufgefüllt)"
    - "Vermerk-Zone per x0-Schwelle (x0 > Anker der letzten Wertspalte), Vermerk-Fortsetzungszeilen hängen an die zuletzt gesehene Datenzeile in Lesereihenfolge (nicht per Δtop)"
    - "_REGEL9_SOLL_FAKTOR (pruefung.py): ein Eckwert, dessen Ist-Wert in einer feineren Einheit geführt wird als der gedruckte Sollwert (hier Stellen vs. Hundertstel), bekommt einen expliziten Skalierungsfaktor statt einer Ad-hoc-Division"

key-files:
  created:
    - pipeline/ostbevern/stellenplan.py
    - pipeline/05_stellenplan.py
    - pipeline/tests/test_stellenplan.py
    - daten/aufbereitet/stellenplan.csv
    - app/src/data/stellenplan.json
  modified:
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/alle.py
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/tests/test_pruefung.py
    - pipeline/tests/test_alle.py
    - pipeline/tests/test_app_daten.py
    - daten/pruefberichte/befunde.md
    - app/src/data/typen.ts
    - app/src/data/daten.ts

key-decisions:
  - "Task 1 ließ lies_stellenplan die drei Stellenübersicht-Titel zwar bereits in der TOML konfigurieren, aber ohne Parsing-Zweig überspringen (kein harter Titel-Vollständigkeits-Check); erst Task 2 schaltete die strikte 'jede konfigurierte Seite muss einen bekannten Titel haben'-Prüfung scharf, nachdem alle sieben Titel einen Parsing-Pfad hatten — sonst hätte Task 1 beim Iterieren über S. 287-289 sofort abgebrochen"
  - "Teil-A/B-Tests mussten nach Task 2 auf `pl.col('produktbereich').is_null()` geschärft werden: Gruppen wie 'A 14' oder '9c' kommen jetzt sowohl in der Teil-A/B-Tabelle als auch in der Stellenübersicht vor, und ein ungefilterter Gruppen-Filter traf beide Quellen"
  - "Regel 10 zählt eine Gruppe, die nur in einer der beiden Quellen vorkommt, in der fehlenden Quelle als 0 (kein struktureller Lücken-Typ wie bei Regel 6/8) — auf den eingecheckten Daten tritt das nicht auf, da jede gedruckte Teil-A/B-Stelle auch in der Übersicht verteilt ist"
  - "stellenplan.json teilt stellen_hundertstel durch 100 zu einem JSON-Float (VZÄ); Personen bleiben unverändert — keine Formatierung in der Pipeline (D-15), die App rundet/formatiert selbst"

patterns-established:
  - "PDF-Seitenzahl-Bereinigung mit Zeilen-Verwurf: _entferne_seitenzahl() in stellenplan.py verwirft eine durch die Bereinigung leer gewordene Textzeile vollständig, statt sie als leere Zeile weiterzureichen (sonst erreicht eine Phantom-Zeile die Gruppen-/Wert-Erkennung und bricht mit 'unerwartete leere Zeile' ab)"

requirements-completed: [EXTR-10, DATA-01, PRUEF-10]

coverage:
  - id: D1
    description: "Teil A Beamte (S. 284), Teil B Tarif (S. 285) und Sozial-/Erziehungsdienst (S. 286) sowie Nachwuchskräfte (S. 290) exakt in Hundertsteln/Personen extrahiert, inkl. Vermerke und Stichtage; gedruckte insgesamt-Zeilen je Spalte gegengeprüft, nie gespeichert"
    requirement: "EXTR-10"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_beamte_b3_davon_ausgesondert"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_beamte_a14_stellen_vermerk_besetzt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_tarif_9c_nicht_an_10_angehaengt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_tarif_9a_vermerk_sperrvermerk"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_nachwuchs_summen_und_keine_stellen"
        status: pass
      - kind: other
        ref: "command: grep acceptance criteria against daten/aufbereitet/stellenplan.csv (A 14, 9c rows, besetzt stichtag)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Drei Stellenübersichten nach Produktbereichen (S. 287-289) mit dünn besetzter PB x Gruppe-Matrix, inkl. PB-Summe-Zellen und abschließender Summe-Zeile je Spalte gegen die Gruppenwerte geprüft"
    requirement: "EXTR-10"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_uebersicht_pb11_pb16_ohne_summe_zelle"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_uebersicht_tarif_pb09_zwei_namenszeilen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_uebersicht_summen_je_teil"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_stellenplan.py#test_stellenplan_uebersicht_manipulierte_summe_zeile_bricht_ab"
        status: pass
    human_judgment: false
  - id: D3
    description: "Regel 10 beweist die Stellenübersicht exakt gegen Teil A/B (19 geprüfte Gruppen, 0 Abweichungen); Eckwert stellen_beamte in Regel 9 (Anhang B.6, Beamte 2026 = 8) verdrahtet"
    requirement: "PRUEF-10"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel10_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel10_erkennt_abweichende_summe"
        status: pass
      - kind: other
        ref: "command: uv run --directory pipeline python alle.py --jahr 2026 (Regel 9/10 grün in konsistenz.md)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Schritt 05 läuft innerhalb von alle.py in der D-24-Reihenfolge (01→02→03→04→Querschnitte→05→06→07); ein StellenplanFehler bricht vor Schritt 06 ab"
    requirement: "PRUEF-10"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_stellenplanfehler_beendet_mit_fehler"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_ohne_jahr_nutzt_standardjahr"
        status: pass
    human_judgment: false
  - id: D5
    description: "stellenplan.json veröffentlicht und typisiert (StellenplanZeile, Stellenplan), VZÄ = stellen_hundertstel / 100, deterministisch, byte-identisch bei Regeneration"
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_stellenplan_json_vzae"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_stellenplan_json_eingecheckt_aktuell"
        status: pass
      - kind: other
        ref: "command: npm run type-check (Scratch-Kopie, app/src/data/daten.ts importiert stellenplan.json typisiert)"
        status: pass
    human_judgment: false

duration: ca. 2h
completed: 2026-10-03
status: complete
---

# Phase 4 Plan 03: Stellenplan (S. 284-290) und Schritt 05 Summary

**Neuer Koordinatenparser `ostbevern/stellenplan.py` extrahiert den kompletten Stellenplan (Teil A Beamte, Teil B Tarif/Sozial- und Erziehungsdienst, Nachwuchskräfte, drei Stellenübersichten nach Produktbereichen) in 162 CSV-Zeilen, bewiesen durch eine neue exakte Regel 10 gegen Teil A/B und als `stellenplan.json` veröffentlicht; Schritt 05 läuft jetzt in `alle.py`.**

## Performance

- **Duration:** ca. 2h
- **Tasks:** 3 von 3
- **Files modified:** 12 geändert, 5 neu

## Accomplishments

- `ostbevern/stellenplan.py` (neu): `StellenplanFehler`, `Stellenwert`, `lies_stellen_hundertstel` (hundertstel-exaktes String-Parsing, nie `round(float*100)`, D-18), `lies_stellenplan`, `extrahiere_stellenplan` — deckt alle sieben gedruckten Stellenplan-Titel S. 284-290 ab
- Teil A Beamte (S. 284), Teil B Tarif (S. 285) und Sozial-/Erziehungsdienst (S. 286): Gruppen-Erkennung (Buchstabe+Zahl, "S "+Zahl/"pauschal", EG-Token), Amtsbezeichnung/Vermerk-Trennung über Spaltenanker, Zwei-Pass-Zuordnung für Werte auf abweichender `top`-Zeile (EG 9c/9b/9a), gedruckte insgesamt-Zeilen je Spalte gegengeprüft
- Nachwuchskräfte (S. 290): eigener `teil`, Personen statt Stellen, zwei Freitextspalten (Bezeichnung über Fortsetzungszeilen, Vergütung) über Spaltenanker-Mittelpunkte abgegrenzt
- Drei Stellenübersichten nach Produktbereichen (S. 287-289): dünn besetzte PB×Gruppe-Matrix (`ordne_spalten` ohne Vollständigkeitsprüfung, Research Pattern 1), PB-Blöcke über mehrere Namenszeilen gesammelt (PB 09 Tarif), je-PB-Summe-Zelle und abschließende Summe-Zeile je Spalte und Gesamtsumme gegen die Gruppenwerte geprüft
- Neue exakte Regel 10 "Stellenplan: Stellenübersicht → Teil A/B" (0 Hundertstel Toleranz): 19 (teil, gruppe)-Paare geprüft, 0 Abweichungen auf den eingecheckten Daten
- Eckwert `stellen_beamte` (Anhang B.6, Beamte 2026 = 8) in Regel 9 verdrahtet, neue `_REGEL9_SOLL_FAKTOR`-Skalierung für Eckwerte mit feinerer Ist-Einheit
- `alle.py`: Schritt 05 zwischen Querschnitte und Schritt 06, vollständige Fehlerbehandlung wie die übrigen Schritte
- `app_daten.py`: `stellenplan.json` (haushaltsjahr, einheit_stellen "vzae", 162 Zeilen in CSV-Reihenfolge, `stellen` = `stellen_hundertstel` / 100); `typen.ts`/`daten.ts` um `StellenplanZeile`/`Stellenplan` und den typisierten `stellenplan`-Export erweitert

## Task Commits

Jeder Task wurde atomar committet:

1. **Task 1: Teil A/B und Nachwuchskräfte parser (S. 284-286, 290) -> stellenplan.csv via Schritt 05** - `910033c` (feat)
2. **Task 2: Stellenübersicht nach Produktbereichen (S. 287-289) mit Summe-Kreuzprüfungen** - `453f583` (feat)
3. **Task 3: Regel 10 Kreuzprüfung, Beamte Eckwert, Schritt 05 in alle.py, stellenplan.json** - `b361427` (feat)

## Files Created/Modified

- `pipeline/ostbevern/stellenplan.py` - Koordinatenparser S. 284-290 (neu)
- `pipeline/05_stellenplan.py` - Schritt-05-typer-Einstieg (neu)
- `pipeline/tests/test_stellenplan.py` - 27 Tests gegen das reale PDF (neu)
- `daten/aufbereitet/stellenplan.csv` - 162 Zeilen (neu)
- `app/src/data/stellenplan.json` - VZÄ-Stellenplan für die App (neu)
- `pipeline/ostbevern/schema.py` - `STELLENPLAN_CSV`, `STELLENPLAN_SPALTEN`, `schreibe_/lies_stellenplan_csv`
- `pipeline/ostbevern/pruefung.py` - `TOLERANZ_JE_REGEL[10]=0`, `_pruefe_regel10`, `_REGEL9_SOLL_FAKTOR`, `stellen_beamte` in `REGEL9_ECKWERTE`
- `pipeline/ostbevern/app_daten.py` - `STELLENPLAN_JSON`, `baue_stellenplan_json`
- `pipeline/alle.py` - Schritt 05 verdrahtet
- `pipeline/jahrgaenge/2026.toml` - `[layout.stellenplan]` (Titel, Spaltenlisten, kein_wert, datum_muster)
- `pipeline/jahrgaenge/2026_sollwerte.toml` - `[eckwerte.stellen_beamte]`
- `pipeline/tests/test_pruefung.py` - 4 neue Regel-10-Tests, `_kopiere_hierarchie_nach` kopiert jetzt stellenplan.csv mit
- `pipeline/tests/test_alle.py` - Schritt-05-Platzierung, `test_stellenplanfehler_beendet_mit_fehler`
- `pipeline/tests/test_app_daten.py` - `test_stellenplan_json_vzae`, `test_stellenplan_json_eingecheckt_aktuell`
- `daten/pruefberichte/befunde.md` - Regel-10- und Eckwert-`stellen_beamte`-Absatz
- `app/src/data/typen.ts` - `StellenplanZeile`, `Stellenplan`
- `app/src/data/daten.ts` - typisierter `stellenplan`-Export

## Decisions Made

- Task 1 ließ die drei Stellenübersicht-Titel in der TOML bereits konfiguriert, aber ohne Parsing-Zweig überspringen (kein harter Titel-Vollständigkeits-Check); Task 2 schaltete die strikte Prüfung erst scharf, nachdem alle sieben Titel einen Parsing-Pfad hatten
- Teil-A/B-Tests wurden nach Task 2 auf `produktbereich.is_null()` geschärft, da Gruppen (z. B. "A 14", "9c") jetzt in beiden Tabellen vorkommen
- Regel 10 zählt eine Gruppe, die nur in einer Quelle vorkommt, in der fehlenden Quelle als 0 (keine strukturelle Lücke wie bei Regel 6/8); auf den eingecheckten Daten tritt dieser Fall nicht auf
- `stellenplan.json` teilt `stellen_hundertstel` durch 100 zu einem JSON-Float (VZÄ); keine Formatierung in der Pipeline (D-15)

## Deviations from Plan

None - plan executed exactly as written. Die Implementierung folgte den im Plan vorverifizierten PDF-Koordinaten (Planning-time facts) exakt; alle Soll/Ist-Kreuzprüfungen (insgesamt-Zeilen, PB-Summen, Regel 9/10) waren beim ersten vollständigen Lauf grün, ohne dass eine Korrektur an den verifizierten Fakten nötig war.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `stellenplan.py` (Stellenwert-Hundertstel-Konvention, `lies_stellenplan`/`extrahiere_stellenplan`) und `stellenplan.json` (VZÄ) stehen für Phase 6 (Stellenplan-Seite der App) bereit.
- Alle zehn Prüfregeln (1-10) sind grün; `alle.py` ist vollständig reproduzierbar (`git diff --exit-code -- daten app/src/data` leer, keine ungetrackten Dateien, verifiziert nach dem Commit).
- Phase 4 ist mit diesem Plan inhaltlich abgeschlossen (Erfolgskriterium 3: Stellenplan vollständig, Beamtenstellen 2026 = 8); verbleibend laut ROADMAP sind etwaige weitere Pläne der Phase (Erklärtexte, falls noch nicht abgedeckt) separat zu prüfen.

---
*Phase: 04-manuelle-daten-und-app-daten*
*Completed: 2026-10-03*

## Self-Check: PASSED

- `[ -f pipeline/ostbevern/stellenplan.py ]`, `[ -f pipeline/05_stellenplan.py ]`, `[ -f pipeline/tests/test_stellenplan.py ]`, `[ -f daten/aufbereitet/stellenplan.csv ]`, `[ -f app/src/data/stellenplan.json ]` all confirmed present on disk.
- All three task commits (`910033c`, `453f583`, `b361427`) confirmed via `git log --oneline --all`.
- Re-ran every `<acceptance_criteria>` check from all three tasks: all pass (header check, A 14/9c/S 12 row greps, besetzt stichtag grep, Python sum checks for Task 1/2, `grep -c 'raise StellenplanFehler'` >= 6, konsistenz.md Regel 9/10 grün, `[eckwerte.stellen_beamte]` present, Regel 10 pdf_seite checks, post-commit `git diff --exit-code -- daten app/src/data` + empty untracked check, `ruff check`/`ruff format --check`).
- Re-ran the plan-level `<verification>` block: `uv run --directory pipeline pytest -q` (404 passed), `alle.py --jahr 2026` (Regel 1-10 all grün) followed by `git diff --exit-code -- daten app/src/data` and an untracked-file check (both clean, post-commit), app `type-check`/`lint`/`format:check` in a fresh scratch copy (all green).
