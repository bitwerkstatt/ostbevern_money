---
phase: 04-manuelle-daten-und-app-daten
plan: 01

subsystem: pipeline-and-app-data
tags: [polars, typer, pytest, toml, vue-tsc, prettier, steuerarten, zuwendungen, transferaufwendungen, kita, regel5, regel4, app-json]

requires:
  - phase: 03-details
    provides: daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan,produkte.json}, Regeln 1-4 und 6-8
provides:
  - Vier manuelle Vorberichtstabellen (Steuerarten, Zuwendungen, Transferaufwendungen, Kita-Zuschüsse) in T€, long format, mit PDF-Seite
  - Regel 5 (zweistufig: Posten-Summe vs. gedruckte Gesamtzeile, Gesamtzeile vs. GEP-Zeile) plus Kita/Transfer-Kreuzvergleich und Weitergabe an Kreis und Land (D-01)
  - Regel 4 B.4/B.5: unabhängige zweite Abschrift aus discussion/SPEZIFIKATION.md, geprüft gegen die manuellen CSVs
  - Schritt 07 (ostbevern/app_daten.py, 07_app_daten.py): app/src/data/haushalt.json deterministisch aus daten/ erzeugt, inkl. berechnetem "Sonstige"-Posten für Zuwendungen
  - app/src/data/typen.ts, daten.ts: zentrale TS-Typen, typisierter JSON-Import ohne Cast
  - CI-Schritt "Pipeline reproduzierbar (D-24)" im Job pipeline
affects: [04-02, 04-03, 04-04, 04-05, 05, 06]

actuals:
  tokens: 31171
  tasks: 3
  commits: 4
  plan_head_before: fb1ef7a567ef4abbe8d460e37592233aed4c5d56
  plan_head_after: d77a47f2321a0ef1feaac6cafe0fbefa049ccb3a

tech-stack:
  added: []
  patterns:
    - "Manuelle Vorbericht-CSVs über schema.VORBERICHT_SPALTEN/schreibe_vorbericht_csv/lies_vorbericht_csv, nie von einem Pipeline-Schritt überschrieben (D-09)"
    - "Regel 5 trägt den fachlichen Kontext im Pruefpunkt-Feld `plan` (vorbericht_{tabelle}, weitergabe_kreis_land), ebene/code bleiben GESAMT/leer für Nicht-PB/PG/P-Vergleiche"
    - "Unabhängige zweite Sollwert-Abschrift (Anhang B.4/B.5) als optionale TOML-Tabellen in {jahr}_sollwerte.toml, übersprungen statt Pflicht, wenn ein anderer Jahrgang sie nicht hat"
    - "App-JSON-Schritt (app_daten.py) liest ausschließlich daten/, nie das PDF; atomarer Schreiber (tempfile + os.replace) wie schema.schreibe_produkte_json"

key-files:
  created:
    - daten/manuell/steuerarten.csv
    - daten/manuell/zuwendungen.csv
    - daten/manuell/transferaufwendungen.csv
    - daten/manuell/kita_zuschuesse.csv
    - daten/manuell/README.md
    - pipeline/ostbevern/app_daten.py
    - pipeline/07_app_daten.py
    - pipeline/tests/test_manuell.py
    - pipeline/tests/test_app_daten.py
    - app/src/data/typen.ts
    - app/src/data/daten.ts
    - app/.prettierignore
  modified:
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/ostbevern/konfiguration.py
    - pipeline/alle.py
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/tests/test_pruefung.py
    - pipeline/tests/test_alle.py
    - pipeline/tests/test_konfiguration.py
    - daten/pruefberichte/befunde.md
    - daten/pruefberichte/konsistenz.md
    - app/src/data/haushalt.json
    - .github/workflows/ci.yml

key-decisions:
  - "Sonstige-Posten (Zuwendungen) als GEP minus Summe der Posten berechnet (nicht GEP minus gedruckter Gesamtzeile), damit Posten-Summe + Sonstige in jeder markierten Jahr exakt die GEP-Zeile trifft — wichtiger für die Bürgerkorrektheit der App-Darstellung als die engere Spez.-3.8-Differenz allein"
  - "baue_vorbericht_tabelle verlangt keine Gesamtzeile mehr für jedes Jahr aus `jahre` (nur noch für mindestens eines) — kita_zuschuesse druckt laut MANU-04 nur das Haushaltsjahr, fehlende Jahre werden null statt AppDatenFehler"
  - "Kreisumlage-Fußnote (10.1473) wird als korrigierter Wert 10147 mit erklärender Anmerkung gespeichert, nie als gedruckter Rohtext — Regel 5 vergleicht den korrigierten Wert gegen GEP/TP"

patterns-established:
  - "Regel-5-Erweiterungen (Kita-Kreuzvergleich, Weitergabe) leben als eigene _pruefe_regel5_*-Hilfsfunktionen neben der Haupt-Zweistufenprüfung, damit spätere Plans (weitere_vorberichtstabellen.csv) dasselbe Muster fortsetzen können"

requirements-completed: [MANU-01, MANU-02, MANU-03, MANU-04, MANU-07, PRUEF-05, DATA-01, PRUEF-10]

coverage:
  - id: D1
    description: "Steuerarten-Vorberichtstabelle (S. 27) abgeschrieben, Regel 5 zweistufig grün (Tracer-Task)"
    requirement: "MANU-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_schema_vorbericht_tabelle_kanonisch"
        status: pass
    human_judgment: false
  - id: D2
    description: "Schritt 07 (app_daten.py) erzeugt app/src/data/haushalt.json deterministisch, nur aus daten/, nie aus dem PDF"
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_app_json_deterministisch"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_haushalt_json_eingecheckt_aktuell"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_app_daten_liest_kein_pdf"
        status: pass
    human_judgment: false
  - id: D3
    description: "CI-Job pipeline bekommt einen Reproduzierbarkeits-Schritt, der bei jedem Diff/jeder ungetrackten Datei unter daten/ oder app/src/data/ fehlschlägt"
    requirement: "PRUEF-10"
    verification:
      - kind: other
        ref: "command: uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data"
        status: pass
    human_judgment: true
    rationale: "Für dieses Repository existiert noch kein GitHub-Remote (STATE.md); der CI-Schritt ist nur lokal mit identischer Befehlszeile nachgestellt, nie auf GitHub Actions selbst gelaufen."
  - id: D4
    description: "Zuwendungen, Transferaufwendungen und Kita-Zuschüsse abgeschrieben; Regel 5 um Kita/Transfer-Kreuzvergleich und Weitergabe an Kreis und Land (D-01) erweitert; sechs gedruckte Rundungsdifferenzen in befunde.md belegt"
    requirement: "MANU-02"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_weitergabe_kreis_land_gleich_tp_15"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_kita_gleich_transferposten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_haushalt_json_zuwendungen_sonstige"
        status: pass
    human_judgment: false
  - id: D5
    description: "Anhang B.4/B.5 als unabhängige zweite Sollwert-Abschrift, Regel 4 vergleicht sie gegen die manuellen CSVs"
    requirement: "PRUEF-05"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_b4_b5_gruen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_b4_erkennt_tippfehler_in_steuerarten"
        status: pass
    human_judgment: false
  - id: D6
    description: "daten/manuell/README.md begründet jede manuelle Datei mit PDF-Seite (MANU-07)"
    requirement: "MANU-07"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_readme_nennt_jede_manuelle_datei"
        status: pass
    human_judgment: false

duration: 5h50min
completed: 2026-10-02
status: complete
---

# Phase 4 Plan 01: Manuelle Vorberichtstabellen und App-JSON Summary

**Vier manuell abgeschriebene Vorberichtstabellen (Steuerarten, Zuwendungen, Transferaufwendungen, Kita-Zuschüsse) laufen durch eine auf zwei Stufen geprüfte Regel 5 (inkl. Kita-Kreuzvergleich und Weitergabe an Kreis und Land) und eine unabhängig gegengeprüfte Regel 4 (Anhang B.4/B.5) in ein deterministisch erzeugtes `app/src/data/haushalt.json`, abgesichert durch einen neuen CI-Reproduzierbarkeits-Schritt.**

## Performance

- **Duration:** 5h50min (erste bis letzte Commit-Zeit; ein erheblicher Teil davon ist Wartezeit auf Hintergrund-pytest-Läufe von 2-4 Minuten, die während der Ausführung rund zehnmal liefen)
- **Started:** 2026-10-02T15:09:00Z (ungefähr, erste Dateizugriffe im Worktree)
- **Completed:** 2026-10-02T20:59:19Z (letzter Commit)
- **Tasks:** 3 von 3
- **Files modified:** 25 (12 neu, 13 geändert)

## Accomplishments

- Steuerarten (Tracer), Zuwendungen, Transferaufwendungen und Kita-Zuschüsse als manuelle Vorbericht-CSVs transkribiert, Regel 5 zweistufig grün mit 6 dokumentierten, PDF-belegten Rundungsdifferenzen
- Weitergabe an Kreis und Land (D-01) als eigener Regel-5-Kreuzvergleich: TP 160101 Z. 15 == Kreisumlage + Gewerbesteuerumlage + Krankenhausinvestitionsumlage, alle sechs Jahre innerhalb ±3.000 €
- Schritt 07 (`app_daten.py`, `07_app_daten.py`) erzeugt `app/src/data/haushalt.json` deterministisch, inkl. berechnetem "Sonstige"-Posten für die Zuwendungen-GEP-Differenz (Spez. 3.8)
- Anhang B.4/B.5 als unabhängige zweite Sollwert-Abschrift in `2026_sollwerte.toml`, Regel 4 wächst von 194 auf 259 geprüfte Werte, weiterhin grün
- CI-Job `pipeline` bekommt einen Reproduzierbarkeits-Schritt (D-24); App-Typen (`typen.ts`, `daten.ts`) machen strukturelle Drift zu einem `type-check`-Fehler

## Task Commits

Jeder Task wurde atomar committet (Task 1 als Tracer in einem Commit, Task 2 im TDD-Zyklus RED→GREEN, Task 3 als ein Commit):

1. **Task 1: Tracer — Steuerarten end-to-end** - `bce07ab` (feat)
2. **Task 2a: Zuwendungen/Transfer/Kita Regel-5-Erweiterungen (RED)** - `d2d64f0` (test)
2. **Task 2b: Zuwendungen/Transfer/Kita Regel-5-Erweiterungen (GREEN)** - `c22f255` (feat)
3. **Task 3: Anhang B.4/B.5, Regel 4** - `d77a47f` (feat)

_Hinweis: Task 2 trägt `tdd="true"` und folgte dem RED-GREEN-Zyklus (test-Commit vor dem feat-Commit); Task 1 (Tracer) und Task 3 (auto) folgten dem Standard-Commit-pro-Task-Muster._

## Files Created/Modified

- `daten/manuell/steuerarten.csv` - S. 27, 9 Posten × 6 Jahre, T€ wie gedruckt
- `daten/manuell/zuwendungen.csv` - S. 28, 4 Posten × 6 Jahre
- `daten/manuell/transferaufwendungen.csv` - S. 45-46, 11 Posten × 6 Jahre, inkl. korrigierter Kreisumlage-Fußnote
- `daten/manuell/kita_zuschuesse.csv` - S. 46, 8 Posten, nur Haushaltsjahr 2026
- `daten/manuell/README.md` - Begründung jeder Datei mit PDF-Seite (MANU-07)
- `pipeline/ostbevern/schema.py` - VORBERICHT_SPALTEN, schreibe/lies_vorbericht_csv, vier neue Pfadkonstanten
- `pipeline/ostbevern/pruefung.py` - Regel 5 (zweistufig + Kita-Kreuzvergleich + Weitergabe), Regel 4 B.4/B.5
- `pipeline/ostbevern/konfiguration.py` - Validierung der optionalen anhang_b4/b5-Sollwerttabellen
- `pipeline/ostbevern/app_daten.py` (neu) - Schritt-07-Logik: baue_vorbericht_tabelle, erzeuge_app_daten, schreibe_app_json
- `pipeline/07_app_daten.py` (neu) - dünner typer-Einstieg für Schritt 07
- `pipeline/alle.py` - Schritt 07 nach grünem Konsistenzbericht
- `pipeline/jahrgaenge/2026.toml` - [layout.weitergabe_kreis_land]
- `pipeline/jahrgaenge/2026_sollwerte.toml` - [anhang_b4_steuerarten], [anhang_b5_transferaufwendungen]
- `app/src/data/typen.ts`, `daten.ts` (neu) - zentrale TS-Typen, typisierter JSON-Import
- `app/.prettierignore` (neu) - generierte JSON-Dateien von Prettier ausgenommen
- `.github/workflows/ci.yml` - Reproduzierbarkeits-Schritt (D-24)
- `daten/pruefberichte/befunde.md` - Regel-5-Kopfabsatz, 6 neue Befunde
- `daten/pruefberichte/konsistenz.md` - generiert (Regel 4: 259, Regel 5: 44, beide grün)
- `app/src/data/haushalt.json` - generiert, 4 Vorbericht-Tabellen
- `pipeline/tests/test_manuell.py`, `test_app_daten.py` (neu); `test_pruefung.py`, `test_alle.py`, `test_konfiguration.py` erweitert

## Decisions Made

- **Sonstige-Posten als GEP minus Posten-Summe** (nicht GEP minus gedruckter Gesamtzeile): garantiert, dass Posten-Summe + Sonstige in jedem markierten Jahr exakt die GEP-Zeile trifft, statt den Rundungsrest zwischen Stufe (a) und (b) unbemerkt zu lassen — wichtiger für die im CLAUDE.md geforderte Zahlenkorrektheit der App als die enger gefasste Spez.-3.8-Differenz allein.
- **Kita-Tabelle ohne Pflicht-Gesamtzeile je Jahr**: `baue_vorbericht_tabelle` verlangt jetzt nur noch mindestens eine Gesamtzeile insgesamt, nicht mehr je Jahr aus `jahre` — notwendig, weil `kita_zuschuesse.csv` laut MANU-04 nur das Haushaltsjahr druckt.
- **Kreisumlage-Fußnote korrigiert, nicht roh gespeichert**: `betrag_teur = 10147` (nicht der gedruckte Text "10.1473"), mit erklärender `anmerkung`; Regel 5 und Regel 4 B.5 vergleichen den korrigierten Wert.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Sonstige-Berechnung von gedruckter Gesamtzeile auf Posten-Summe umgestellt**
- **Found during:** Task 2 (app_daten.py Sonstige-Logik)
- **Issue:** Der Plan beschreibt nur, wann "Sonstige" nicht-null ist (Stufe-b-Abweichung > Toleranz), nicht die genaue Formel. Eine naive Umsetzung (GEP minus gedruckter Gesamtzeile) hätte dazu geführt, dass Posten-Summe + Sonstige in Jahren mit einer zusätzlichen Stufe-(a)-Rundungsdifferenz (z. B. 2026: Posten-Summe 3.108 vs. Gesamtzeile 3.109) NICHT exakt die GEP-Zeile trifft — ein für die Bürgerkorrektheit der App (CLAUDE.md-Vorgabe) relevanter Fehler.
- **Fix:** Sonstige = GEP-Zeile minus Σ Posten (nicht minus Gesamtzeile), sodass die Summe aller angezeigten Posten in der App immer exakt die Planzeile ergibt.
- **Files modified:** pipeline/ostbevern/app_daten.py
- **Verification:** `pipeline/tests/test_app_daten.py#test_haushalt_json_zuwendungen_sonstige` prüft die Summeninvariante explizit.
- **Committed in:** c22f255 (Task 2 GREEN-Commit)

**2. [Rule 1 - Bug] baue_vorbericht_tabelle verlangte fälschlich eine Gesamtzeile für jedes Jahr**
- **Found during:** Task 2 (Kita-Tabelle erzeugen)
- **Issue:** Die ursprüngliche Task-1-Implementierung (nur für Steuerarten geschrieben) brach mit `AppDatenFehler` ab, sobald ein Jahr aus `jahre` keine Gesamtzeile hatte — korrekt für Steuerarten (alle sechs Jahre gedruckt), aber falsch für `kita_zuschuesse` (MANU-04: nur das Haushaltsjahr).
- **Fix:** Fehlende Jahre werden jetzt `null` statt eines Abbruchs; ein Abbruch erfolgt nur noch, wenn eine Tabelle überhaupt keine Gesamtzeile hat.
- **Files modified:** pipeline/ostbevern/app_daten.py, app/src/data/typen.ts (gesamt_vorbericht.werte auf `(number | null)[]` erweitert)
- **Verification:** `pipeline/tests/test_app_daten.py#test_haushalt_json_steuerarten_aus_manueller_tabelle` (Steuerarten weiterhin vollständig) und die Vorbericht-Reihenfolge-/Sonstige-Tests (Kita läuft ohne Abbruch).
- **Committed in:** c22f255 (Task 2 GREEN-Commit)

---

**Total deviations:** 2 auto-fixed (1 missing critical für Zahlenkorrektheit, 1 Bug-Fix für die Kita-Tabelle)
**Impact on plan:** Beide Fixes waren notwendig, damit Task 2 überhaupt grün werden konnte; kein Scope Creep, beide bleiben innerhalb der von Task 2 selbst beschriebenen Dateien.

## Issues Encountered

Keine blockierenden Probleme. Hintergrund-pytest-Läufe (volle Suite: 300-333 Tests) dauerten wiederholt 130-230 Sekunden; das Sandbox-Benachrichtigungssystem für Hintergrundprozesse lieferte Ergebnisse zuverlässig, aber mit spürbarer Latenz, was die Wall-Clock-Dauer dieser Ausführung deutlich über die reine CPU-Zeit hinaus verlängert hat.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Die Architektur für manuelle Vorbericht-Tabellen (Schema, Regel 5, Schritt 07, CI-Diff-Gate) ist etabliert und von Plan 04-02 bis 04-05 wiederverwendbar (weitere_vorberichtstabellen.csv, Schulden/Rücklagen/VE, Stellenplan, Erklärtexte).
- `app/src/data/haushalt.json` und `typen.ts` sind der Vertrag, den Phase 5/6 für die Einnahmenseite der App konsumieren werden.
- Bekannter, bereits in STATE.md dokumentierter Blocker bleibt offen: die CI läuft nur lokal nachgestellt, bis ein GitHub-Remote existiert (betrifft auch den in diesem Plan neuen D-24-Schritt).

---
*Phase: 04-manuelle-daten-und-app-daten*
*Completed: 2026-10-02*
