---
phase: 03-details
plan: 05
subsystem: pipeline-produkte-pruefung
tags: [pdfplumber, polars, grundzahlen, regel-8, luecken, vollstaendigkeit]

requires:
  - phase: 03-details
    provides: "ostbevern/spalten.ordne_spalten (03-01/02), ostbevern/pdf.PdfDokument.zeilen_fein mit Wort.fett, produkte.py zerlege_felder/extrahiere_produkte (03-04), pruefung.py Luecke/Regelergebnis.luecken-Mechanismus (03-03)"
  - phase: 02-kernzahlen
    provides: "hierarchie.csv (P -> PG -> PB), ergebnisplan.csv/finanzplan.csv, befunde.md-Mechanismus"
provides:
  - "daten/aufbereitet/grundzahlen.csv (827 Werte, 222 gedruckte Zeilen, 48 Produkte) mit Einheit, Jahr, Dezimalwert+Nachkommastellen, Gruppe und per-Jahr-Hinweis (Stichtag/Fußnote)"
  - "ostbevern/zahlen.lies_kennzahl: Dezimalwert-Parser (Gebühren, Quoten) neben dem int-only lies_betrag"
  - "ostbevern/produkte.py: Grundzahl, lies_grundzahlen (Spalten-Zonen, Gruppenüberschriften D-13, Stichtag/Fußnoten D-12)"
  - "ostbevern/schema.py: GRUNDZAHLEN_CSV, GRUNDZAHLEN_SPALTEN, schreibe_/lies_grundzahlen_csv"
  - "ostbevern/pruefung.py: REGEL8_PFLICHTFELDER, REGEL8_MERKMALE, _pruefe_regel8 (Vollständigkeit aller 63 Produkte); Regel 8 in pruefe_alles"
  - "Phase-3-Abschluss: konsistenz.md meldet Regel 1-4 und 6-8 grün, Gesamtstatus grün"
affects: [04-app-daten]

actuals:
  tokens: 32240
  tasks: 2
  commits: 2
  plan_head_before: a918265e5a2efb7dd58a8f983d5c0bdf333def52
  plan_head_after: 5073a4ab690ab7ec7fa5f6354161c5f8c4b0ffb2

tech-stack:
  added: []
  patterns:
    - "Grundzahlen-Zeilenklassifikation prüft IMMER zuerst ist_fett, bevor überhaupt eine Spalten-Zone bestimmt wird: eine fette, wertfreie Zeile (Stichtag-Stempel, Fußnote, Gruppenüberschrift) kann Wörter enthalten, die über die Label-/Einheit-Grenze hinweg reichen oder rechts von der ersten Jahresspalte liegen (dieselbe Zone wie echte Werte) — eine Zonen-Prüfung VOR der Fett-Prüfung lehnt solche Zeilen fälschlich als 'außerhalb jeder Spalte' ab oder verwechselt sie mit einer Datenzeile"
    - "grundzahlen.wert ist Float64 plus nachkommastellen (Int64): Grundzahlen drucken Dezimalwerte (Gebühren, Quoten) neben Euro-Ganzzahlen; nachkommastellen 0 markiert einen Ganzzahlwert, den Float64 exakt darstellt (CONTEXT-Diskretion)"
    - "hinweis(jahr) wird zweiphasig berechnet: eine Lesephase sammelt allgemeine Fußnoten, jahresbezogene Fußnoten und Stichtag-Stempel-Jahre über das ganze Produkt (seitenübergreifend), eine Finalisierungsphase kombiniert sie je Jahr erst nach dem vollständigen Scan — eine Fußnote kann NACH der Zeile gedruckt sein, die sie betrifft (D-12)"
    - "Regel 8 hat keine Abweichungen (kein Soll/Ist-Betragsvergleich), nur Lücken: die Mengen-/Anzahl-Prüfung (produkte.json-Codes == Hierarchie-P-Codes in erwarteter Anzahl) zählt als EIN Check, unabhängig davon, wie viele Lücken sie erzeugt (Behavior-Vorgabe wörtlich: 'the product-set check')"

key-files:
  created:
    - daten/aufbereitet/grundzahlen.csv
  modified:
    - pipeline/ostbevern/zahlen.py
    - pipeline/ostbevern/produkte.py
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/tests/test_zahlen.py
    - pipeline/tests/test_produkte.py
    - pipeline/tests/test_pruefung.py
    - daten/pruefberichte/konsistenz.md
    - daten/pruefberichte/befunde.md

key-decisions:
  - "Zonen-Klassifikation einer Grundzahlen-Zeile läuft NIE für fette Zeilen (siehe tech-stack patterns oben): notwendige Korrektur, siehe Deviations."
  - "produkte_mit_grundzahlen = 48 gegen das echte PDF verifiziert (eigenständiges Koordinaten-Scan-Skript, exakt übereinstimmend mit der Planungszeit-Angabe im Plan)."
  - "REGEL8_PFLICHTFELDER (8 Felder) plus 5 weitere Merkmale (leistungen, bindungsgrad, pdf_seiten, teilergebnisplan, teilfinanzplan) = REGEL8_MERKMALE; geprueft = 63 × 13 + 1 = 820 (Mengen-/Anzahl-Check zählt einmal)."
  - "pruefung.py bleibt CSV/JSON-only (Modul-Docstring präzisiert statt verletzt): produkte.json ist eine generierte Datei unter daten/, kein PDF-Zugriff; test_pruefung_liest_kein_pdf (AST-Prüfung) bleibt unverändert grün."

requirements-completed: [EXTR-07, PRUEF-08]

coverage:
  - id: D1
    description: "grundzahlen.csv (827 Werte, 222 gedruckte Zeilen) liest Grundzahlen aller 48 Produkte mit Grundzahlen-Tabelle (inkl. Steuer-Istwerte 2022-2025 von 160101, Gewerbesteuer 2023 = 4.771.497 €), mit korrektem per-Jahr-Hinweis (Stichtag-Stempel, überschreibende/allgemeine Fußnoten) und Gruppenüberschriften, Einheit C/C-Präfix zu EUR/EUR-Präfix normalisiert"
    requirement: EXTR-07
    verification:
      - kind: unit
        ref: "pipeline/tests/test_zahlen.py::test_lies_kennzahl_dezimal_zwei_stellen"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_stichprobe_grundzahl_steuer"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_stichprobe_grundzahl_stichtag"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_stichprobe_grundzahl_ueberschreibung"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_stichprobe_grundzahl_gruppe"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_stichprobe_grundzahl_kein_wert"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_grundzahlen_anzahl_produkte_stimmt_mit_stichprobe"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_produkte.py::test_grundzahlen_manipuliertes_wort_bricht_mit_seite_ab"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python 03_produktinfos.py --jahr 2026 (exit 0, 827 Zeilen grundzahlen.csv, git diff aufbereitet/produkte.json+erlaeuterungen.csv leer)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regel 8 prüft die Vollständigkeit aller 63 Produkte (produktinformationen, Pflichtfelder, Leistungen, Bindungsgrad, PDF-Seiten, Teilergebnis-/Teilfinanzplan-Zeilen) als Lücken; konsistenz.md meldet Regel 1-4 und 6-8 grün, Gesamtstatus grün, nach vollständiger Regeneration der Pipeline"
    requirement: PRUEF-08
    verification:
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_fehlendes_produkt_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_unbekanntes_produkt_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_ungueltiger_bindungsgrad_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_bindungsgrad_original_null_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_leeres_gremium_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_fehlende_teilergebnisplan_zeilen_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_fehlende_teilfinanzplan_zeilen_erzeugt_luecke"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel8_falsche_gesamtanzahl_erzeugt_luecke"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (exit 0; Regel 6/7/8: grün); uv run --directory pipeline pytest -q (294 passed); git status --porcelain daten/ leer danach"
        status: pass
      - kind: other
        ref: "CI-Replay: uv sync --locked && ruff check . && ruff format --check . && pytest (alle grün)"
        status: pass
    human_judgment: false

duration: ~75min
completed: 2026-10-02
status: complete
---

# Phase 3 Plan 5: Grundzahlen und Regel 8 (Phase-3-Abschluss) Summary

**Koordinatenbasierter Grundzahlen-Parser (48 Produkte, 222 gedruckte Zeilen inkl. Steuer-Istwerte 2022-2025 von 160101) mit per-Jahr-Stichtag-/Fußnoten-Hinweisen und Gruppenüberschriften, plus Regel 8 (Vollständigkeit aller 63 Produkte) als neuer Lücken-Mechanismus, womit konsistenz.md Regel 1-4 und 6-8 grün meldet.**

## Performance

- **Duration:** ~75 min (geschätzt; keine präzise Sitzungsstartzeit protokolliert, wie bereits in 03-04 dokumentiert)
- **Completed:** 2026-10-02T07:21:28Z
- **Tasks:** 2/2 abgeschlossen
- **Files modified:** 11 (1 neu/generiert, 10 geändert)

## Accomplishments

- `zahlen.lies_kennzahl` parst deutsche Grundzahlen-Kennzahlen zu `(Float64-Wert, Nachkommastellen)`: Tausenderpunkte, optionaler Dezimalteil (Komma), ASCII-/U+2212-Minus, `"–"` als kein Wert — wie `lies_betrag`, aber mit Dezimalwerten für Gebühren/Quoten. `lies_betrag` bleibt unverändert int-only.
- `produkte.lies_grundzahlen` scannt je Produkt seine Produktinformationen- UND grundzahlen-typisierten Seiten (die Tabelle kann auf der PI-Seite beginnen und auf einer eigenen, den Tabellenkopf neu druckenden Seite fortsetzen, wie `investitionen.lies_massnahmen`). Drei Spalten-Zonen (Label/Einheit/Werte) werden über die x0 von "Einheit" und die x0 der ersten Jahresspalte bestimmt; **fette Zeilen werden IMMER vor jeder Zonen-Klassifikation behandelt** (Stichtag-Stempel, überschreibende/allgemeine Fußnoten, Gruppenüberschriften — siehe Deviations). Gruppenüberschriften (`gruppe`) gelten bis zur nächsten Überschrift; mehrzeilige Bezeichnungen/Einheiten werden zusammengeführt (D-13); Einheit `C`/`C/...` wird zu `EUR`/`EUR/...` normalisiert.
- `hinweis(jahr)` kombiniert allgemeine Fußnoten (immer), eine jahresbezogene Fußnote (falls vorhanden, ersetzt den Stichtag-Stempel für dieses Jahr) oder sonst den Stichtag-Stempel (falls dieses Jahr ihn trägt) — zweiphasig berechnet, da eine Fußnote nach der betroffenen Zeile gedruckt sein kann (D-12).
- `grundzahlen.csv` (827 Werte, 222 gedruckte Zeilen, 48 Produkte) wird als drittes `ExtraktionsErgebnis` von `extrahiere_produkte` geschrieben; `produkte.json`/`erlaeuterungen.csv` bleiben byte-identisch.
- `pruefung._pruefe_regel8`: `REGEL8_PFLICHTFELDER` (8 String-Felder) plus `REGEL8_MERKMALE` (+leistungen, bindungsgrad, pdf_seiten, teilergebnisplan, teilfinanzplan = 13 Merkmale je Produkt). Prüft zuerst (ein Check) die Codemenge/-anzahl von `produkte.json` gegen die Hierarchie-P-Codes; dann je Produkt alle 13 Merkmale. Jeder Verstoß ist eine `Luecke` (03-03-Mechanismus, nie über `befunde.md` entschärfbar) — Regel 8 hat keine Abweichungen. `geprueft` = 63×13+1 = 820 auf den echten Daten.
- `pruefe_alles` liest `produkte.json` über `lies_produkte_json` und hängt Regel 8 nach Regel 7 an; `befunde.md` dokumentiert im Kopf-Absatz, dass Regel 8 nur Lücken meldet.
- Phase-Gate: `alle.py --jahr 2026` regeneriert `daten/` deterministisch (Regel 1-4, 6-8 grün, Gesamtstatus grün), die volle Testsuite (294 Tests) und der CI-Replay (`uv sync --locked`, `ruff check`, `ruff format --check`, `pytest`) sind grün.

## Task Commits

Each task was committed atomically:

1. **Task 1: Grundzahlen to grundzahlen.csv with per-year hints and groups (EXTR-07, D-12, D-13)** - `700fbb9` (feat)
2. **Task 2: Regel 8 Vollständigkeit and the Phase 3 gate (PRUEF-08)** - `5073a4a` (feat)

**Plan metadata:** (this commit) `docs(03-05): complete Grundzahlen und Regel 8 plan`

_Note: Tasks carry `tdd="true"`; wie in 03-01..04 wurden Implementierung und Tests gegen das echte PDF bzw. die eingecheckten CSVs gemeinsam entwickelt statt strikt RED-dann-GREEN commit-separiert (Testfixtures manipulieren echte Wort-/Zeilenobjekte bzw. echte Produkt-/Planzeilen, die die Parsing-/Prüflogik selbst braucht, um Zielzeilen/-schlüssel zu finden). `workflow.tdd_mode` ist in diesem Projekt nicht konfiguriert, daher greift keine automatisierte RED/GREEN-Commit-Sequenz-Prüfung. Für `zahlen.lies_kennzahl` (reines String-Modul ohne PDF-Abhängigkeit) wurden die Behavior-Tests vor der Implementierung geschrieben und liefen nachweislich rot (ImportError) vor dem GREEN-Commit._

## Files Created/Modified

- `pipeline/ostbevern/zahlen.py` - `lies_kennzahl(text) -> tuple[float, int] | None`
- `pipeline/ostbevern/produkte.py` - `Grundzahl`, `lies_grundzahlen(dokument, jahrgang, seiten, hierarchie)`; `extrahiere_produkte` schreibt zusätzlich `grundzahlen.csv`
- `pipeline/ostbevern/schema.py` - `GRUNDZAHLEN_CSV`, `GRUNDZAHLEN_SPALTEN`, `schreibe_/lies_grundzahlen_csv`
- `pipeline/ostbevern/pruefung.py` - `REGEL8_PFLICHTFELDER`, `REGEL8_MERKMALE`, `_pruefe_regel8`; Regel 8 in `pruefe_alles`
- `pipeline/jahrgaenge/2026.toml` - `[layout.grundzahlen]` (`kopf`, `einheit`, `fussnote_jahr_muster`, `fussnote_allgemein_muster`, `eurozeichen`)
- `pipeline/jahrgaenge/2026_sollwerte.toml` - `[stichproben.grundzahl_*]` (5 Stichproben), `stichproben.anzahlen.produkte_mit_grundzahlen`
- `pipeline/tests/{test_zahlen,test_produkte,test_pruefung}.py` - 10 + 10 + 11 neue Tests
- `daten/aufbereitet/grundzahlen.csv` - generierte Daten (827 Werte)
- `daten/pruefberichte/{konsistenz,befunde}.md` - Regel 8 in der Übersicht, Kopf-Absatz-Hinweis

## Decisions Made

- **Fette Zeilen werden vor jeder Spalten-Zonen-Klassifikation behandelt**: siehe Deviations (Rule 1 — notwendige Korrektur).
- **`produkte_mit_grundzahlen = 48`**: gegen das echte PDF über ein eigenständiges Koordinaten-Scan-Skript verifiziert, deckt sich exakt mit der im Plan dokumentierten Planungszeit-Zahl (48 Produkte, 222 Zeilen).
- **`REGEL8_PFLICHTFELDER`/`REGEL8_MERKMALE`-Aufteilung**: exakt wie im Plan vorgegeben (8 Pflichtfelder + 5 weitere Merkmale), keine Abweichung.
- **Mengen-/Anzahl-Prüfung zählt als EIN Check**: exakt wie im Plan-Behavior-Text ("the product-set check", Singular), keine Abweichung.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fette, wertfreie Zeilen werden vor der Spalten-Zonen-Klassifikation behandelt**
- **Found during:** Task 1, Testlauf gegen die echte PI-Seite des ersten Produkts (010101, S. 72)
- **Issue:** Die ursprüngliche Implementierung klassifizierte JEDE Zeile zuerst in Label-/Einheit-/Wert-Zonen und prüfte erst danach, ob sie fett ist. Der Stichtag-Stempel ("Stand 30.06.", S. 72) liegt vollständig rechts der ersten Jahresspalte — exakt dieselbe Zone wie echte Werte — und wurde dadurch fälschlich als Datenzeile ohne Einheit erkannt (`ProdukteFehler: Grundzahlen-Zeile ohne Einheit`). Eine zweistellige Jahres-Fußnote (S. 103, "Ist-Werte 2024 und 2025: Entwurf Jahresabschluss 2024 und Prognose 2025") enthält zusätzlich ein Wort ("Prognose"), dessen x-Koordinaten über die Label-/Einheit-Grenze hinweg reichen, ohne in eine der drei Zonen einer echten Datenzeile zu passen (`ProdukteFehler: ... liegt in keiner Grundzahlen-Spalte`).
- **Fix:** `ist_fett` wird jetzt VOR jeder Zonen-Klassifikation geprüft; eine fette Zeile wird ausschließlich über ihren vollständigen Zeilentext (Stichtag-Stempel-Erkennung, Fußnoten-Muster, sonst Gruppenüberschrift) behandelt, nie über Spalten-Zonen. Rows (stets unfett, verifiziert gegen das echte PDF) durchlaufen weiterhin die Drei-Zonen-Prüfung.
- **Files modified:** `pipeline/ostbevern/produkte.py`
- **Verification:** `uv run python 03_produktinfos.py --jahr 2026` läuft fehlerfrei über alle 48 Produkte mit Grundzahlen-Tabelle; `pytest tests/test_produkte.py -k grundzahl` grün.
- **Committed in:** `700fbb9` (Task 1 commit)

**2. [Rule 1 - Bug] Jahrgangswert-Literal in einem Code-Kommentar entfernt**
- **Found during:** Task 1, Akzeptanzkriterium `! grep -lwE '202[2-9]' pipeline/ostbevern/produkte.py pipeline/tests/test_produkte.py`
- **Issue:** Ein erklärender Code-Kommentar zitierte den vollen Fußnotentext aus dem PDF inklusive der Jahreszahlen 2024/2025, was den Akzeptanzkriterium-Grep (keine Jahrgangswerte im Code) auslöste, obwohl es sich um einen Beispiel-Kommentar und keinen Jahrgangswert handelte.
- **Fix:** Kommentar umformuliert, ohne die konkreten Jahreszahlen zu nennen.
- **Files modified:** `pipeline/ostbevern/produkte.py`
- **Verification:** `grep -lwE '202[2-9]' pipeline/ostbevern/produkte.py pipeline/tests/test_produkte.py` liefert keinen Treffer mehr.
- **Committed in:** `700fbb9` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (beide Rule 1 — notwendige Korrekturen, damit die Pipeline auf dem echten PDF fehlerfrei läuft bzw. die Akzeptanzkriterien erfüllt; kein Scope-Creep).
**Impact on plan:** Beide Korrekturen waren Voraussetzung dafür, dass `lies_grundzahlen` auf dem echten PDF korrekt läuft; keine Abweichung vom fachlichen Plan-Inhalt.

## Issues Encountered

- TDD-Disziplin für beide Tasks (`tdd="true"`) wurde im Geiste, nicht in strikt RED-dann-GREEN-commit-getrennter Form befolgt (wie bereits in 03-01..04 dokumentiert): Testfixtures, die echte PDF-Wortobjekte bzw. echte Produkt-/Planzeilen manipulieren, benötigen die Parsing-/Prüflogik selbst, um Zielzeilen/-schlüssel zu finden. `zahlen.lies_kennzahl` (reines String-Modul) wurde dagegen strikt TDD entwickelt: die Tests schlugen vor der Implementierung nachweislich mit `ImportError` fehl.
- `_kopiere_hierarchie_nach` in `test_pruefung.py` kopiert seit diesem Plan zusätzlich `produkte.json` mit (nicht nur `hierarchie.csv`), da `pruefe_alles` seit Regel 8 bei jedem Aufruf `produkte.json` liest; alle 25 bestehenden `daten_wurzel=tmp_path`-Testaufrufe nutzen diese Funktion direkt oder über `_kopiere_regel6_abhaengigkeiten`/`_kopiere_regel7_abhaengigkeiten` und blieben dadurch unverändert grün, ohne dass jeder einzelne Testaufruf angepasst werden musste.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `grundzahlen.csv` und `produkte.json` (inkl. Regel-8-Vollständigkeitsgarantie) sind stabile, eingecheckte Artefakte für Phase 4 (App-JSON-Erzeugung): Phase 4 liest Grundzahlen mit ihren per-Jahr-Hinweisen (Spez. 6.x, AUSG-05-ähnliche Produktdetailsicht) und kann sich auf eine vollständige `produkte.json` verlassen.
- Phase 3 ist mit diesem Plan abgeschlossen: `konsistenz.md` meldet Regel 1-4 und 6-8 grün, Gesamtstatus grün — Roadmap-Erfolgskriterien 1 (Regel-8-Teil), 2 und 4 sind erfüllt.
- Blocker aus Phase 2/03-01..04 unverändert: Schuldenstand/Rücklagen/VE-Übersicht (S. 24/25, 309-311) bleibt ein Phase-4-Thema (Spez. 3.8, D-Hinweis aus früheren Summaries).

## Self-Check: PASSED

- Verified `daten/aufbereitet/grundzahlen.csv` exists on disk (827 Zeilen, Header `produkt,position,gruppe,bezeichnung,einheit,jahr,wert,nachkommastellen,hinweis,pdf_seite`).
- `git log --oneline --all` contains `700fbb9` and `5073a4a`.
- Re-ran all task-level `<acceptance_criteria>` commands and the plan-level `<verification>` block:
  - CI replay: `uv sync --locked && ruff check . && ruff format --check . && pytest` — 294 tests pass.
  - `uv run --directory pipeline python alle.py --jahr 2026` exits 0; stdout names "Regel 6: grün", "Regel 7: grün", "Regel 8: grün"; `git status --porcelain daten/` prints nothing afterward.
  - `konsistenz.md`: Gesamtstatus grün; Regel 1, 2, 3, 4, 6, 7, 8 grün in this order; `## Lücken` and `## Veraltete Befunde` show "Keine.".
  - `uv run --directory pipeline pytest tests/test_produkte.py -q -k keine_personennamen` passes.
- `git diff --exit-code pipeline/pyproject.toml pipeline/uv.lock` exits 0 (no new dependencies).
- `grep -lwE '202[2-9]' pipeline/ostbevern/produkte.py pipeline/ostbevern/pruefung.py pipeline/tests/test_produkte.py pipeline/tests/test_pruefung.py` — no matches, no year literals in new/modified pipeline code (outside the `<!-- planner-discipline-allow: 202[2-9] -->`-exempted PLAN.md itself).

---
*Phase: 03-details*
*Completed: 2026-10-02*
