---
phase: 05-leitfragen-seiten
plan: 03
subsystem: texte-glossar
tags: [glossar, erklaertexte, platzhalter, d-02, texte-json, typen]

requires:
  - phase: 04-manuelle-daten-und-app-daten
    provides: "Textvertrag (Platzhalter, Ziffernregel, pruefe_text, loese_auf), erklaerungen.md, texte.json"
  - phase: 05-leitfragen-seiten
    provides: "05-02: zeilen_namen, Vorbericht-Tabellen; 05-01: formatiere-Fallback und node-Gegenprobe"
provides:
  - "daten/manuell/texte/glossar.md: 24 Begriffe (22 Pflichtbegriffe Spez. 6.14 plus produktgruppe, wertart) mit stabilen Schluesseln"
  - "texte.py: lies_glossar, lies_erklaerungen(kopfzeile, quelle_pflicht), pruefe_grundzahl_jahre (D-02)"
  - "texte.json.glossar [{schluessel, begriff, quelle_seiten, absaetze}] und typen.ts Glossarbegriff / Texte.glossar"
  - "sieben jahrneutrale Erklaertexte (steuern_selbst_festgelegt, zuwendungen_laufende_zwecke, ueberschuss_pb_16, ueberschuss_pb_11, ueberschuss_allgemein, ueberschuss_ruecklage, geldfluss_lesehilfe)"
  - "gewerbesteuer-Text: 2024 aus vorbericht.steuerarten statt Grundzahl (D-02)"
affects: [05-04, 05-07, 05-11, glossar-seite, geldfluss-seite, einnahmen-seite, produkt-seite]

actuals:
  tokens: 60000
  tasks: 3
  commits: 2
plan_head_before: 8403a43b4a14a6ce43ab467307a65386035a8b01
plan_head_after: fb6959a540e7644a5d340ef58178bd217b6738be
commits: 2

tech-stack:
  added: []
  patterns:
    - "Glossar im selben Textvertrag wie Erklaertexte; Quelle optional, Pflicht sobald ein Absatz einen Platzhalter hat"
    - "D-02-Regel: kein Euro-Grundzahl-Platzhalter ab dem ersten Jahr von haushalt.jahre; Einheit aus produkte.json, kein Produktcode im Code"
    - "Erster Glossarabsatz steht allein (Tooltip, D-16) und enthaelt nie einen Platzhalter"

key-files:
  created:
    - daten/manuell/texte/glossar.md
  modified:
    - pipeline/ostbevern/texte.py
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/tests/test_texte.py
    - pipeline/tests/test_app_daten.py
    - pipeline/tests/test_formatiere.py
    - daten/manuell/texte/erklaerungen.md
    - daten/manuell/README.md
    - app/src/data/texte.json
    - app/src/data/typen.ts

key-decisions:
  - "Glossar um produktgruppe und wertart auf 24 Begriffe erweitert (22 Pflichtbegriffe bleiben per Test erzwungen)"
  - "Quelle-Seiten einzeln geschrieben (S. 24, S. 25), nicht als Spanne (WR-04)"
  - "Seitenbelege geprueft und korrigiert: Haushaltssicherung S. 23, Abschreibungen S. 45, NKF S. 15, Produkt S. 17"
  - "Die sieben jahrneutralen Erklaertexte sind platzhalterfrei (Test), enthalten aber vereinzelt historische Jahreszahlen mit Vorbericht-Beleg"

requirements-completed: [GLOS-01, UI-05, EINN-05]

coverage:
  - id: D1
    description: "glossar.md mit mindestens 22 Pflichtbegriffen unter stabilen Schluesseln, nach Abnahme, in texte.json.glossar"
    requirement: GLOS-01
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_glossar_pflichtbegriffe"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_texte_json_enthaelt_glossar"
        status: pass
    human_judgment: false
  - id: D2
    description: "Glossartexte: Ziffernregel, Quelle bei Platzhalter, alle Schluessel aufloesbar, erster Absatz ohne Platzhalter"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_glossar_keine_nackten_ziffern, test_glossar_quelle_bei_platzhalter, test_glossar_alle_schluessel_existieren, test_glossar_erster_satz_ohne_platzhalter"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_formatiere.py#test_port_wie_format_ts (lief, nicht uebersprungen) und test_texte_json_rendert_korrekt rendern Glossarplatzhalter"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-02: Gewerbesteuer-Text nutzt dieselbe Quelle wie die Zeitreihe; Schritt 07 und Test lehnen Euro-Grundzahl ab dem ersten Planjahr ab"
    requirement: EINN-05
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_d02_keine_euro_grundzahl_ab_erstem_planjahr, test_grundzahl_jahre_*"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_euro_grundzahl_fuer_planjahr_bricht_schritt_07_ab"
        status: pass
    human_judgment: false
  - id: D4
    description: "Sieben jahrneutrale Erklaertexte (platzhalterfrei) inkl. geldfluss_lesehilfe zum Minderaufwand links (D-19)"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_jahrneutrale_erklaerungen_ohne_platzhalter, test_erklaerungen_umfang_d16"
        status: pass
    human_judgment: true
    rationale: "Fachliche Richtigkeit und Neutralitaet der Formulierungen: vom Nutzer im blocking-human-Checkpoint abgenommen (D-15); kein Test kann das pruefen"
  - id: D5
    description: "Reproduzierbarkeit: alle.py --jahr 2026 laesst daten/ und app/src/data/ unveraendert"
    verification:
      - kind: other
        ref: "alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data (sauber, keine untracked Dateien)"
        status: pass
    human_judgment: false

duration: ca. 2h
completed: 2026-10-04
status: complete
---

# Phase 5 Plan 03: Glossar und jahrneutrale Erklaertexte Summary

**Glossar mit 24 abgenommenen Begriffen und sieben jahrneutrale Erklaertexte laufen ueber den Phase-4-Textvertrag nach `texte.json.glossar`; D-02 (kein Euro-Grundzahl-Platzhalter ab dem ersten Planjahr) wird von Schritt 07 und einem Test erzwungen, der Gewerbesteuer-Text nutzt fuer 2024 die Vorbericht-Quelle.**

## Entscheidungen aus der Abnahme

Antwort des Nutzers im blocking-human-Checkpoint (Task 2, 2026-10-04, ueber die Checkpoint-Frage des Orchestrators, nach Ansicht der Vorschau A bis D); die Antwort enthaelt "freigegeben":

- **Texte** (Glossar mit 24 Begriffen, geaenderter Gewerbesteuer-Satz, sieben neue Erklaertexte): "Freigegeben", keine Korrekturen.
- **Bezugsgroessen** (Open Question 6, fuer Plan 05-11): "Vorschlag uebernehmen", d. h. 030101 und 030102 "Zuschussbedarf je Schueler/in"; 040301 "je Musikschueler/in"; 060101 "je betreutem Kind" (Summe aus "Betreute Kinder unter 3 Jahre" und "Betreute Kinder von 3 - 6 Jahre"); zusaetzlich fuer jedes Produkt "Zuschussbedarf je Einwohner (berechnet)".
- **Kontakt und PDF-URL** (Open Question 5, fuer Plan 05-07): "Spaeter (Platzhalter)". Die Platzhalter bleiben bis Phase 7, die sie ablehnen muss (D-17).

## Accomplishments

- Tracer: `lies_glossar`, parametrierbares `lies_erklaerungen(kopfzeile, quelle_pflicht)` (Default unveraendert) und `pruefe_grundzahl_jahre` mit synthetischen Tests; Vorschau mit Rohwerten gegen frische App-Daten.
- `glossar.md`: die 22 Pflichtbegriffe aus Spez. 6.14 plus `produktgruppe` und `wertart`; erster Absatz je Begriff als Tooltip-Text ohne Platzhalter; Zahlen nur als Platzhalter mit Quelle. Alle Seitenbelege gegen den PDF-Text geprueft.
- `erklaerungen.md`: `gewerbesteuer` nutzt fuer 2024 `vorbericht.steuerarten.gewerbesteuer.2024` (9,51 Mio. EUR, vorlaeufiges Ergebnis); sieben neue platzhalterfreie Texte, `geldfluss_lesehilfe` erklaert den globalen Minderaufwand links neben dem Defizit (D-19).
- Schritt 07 liest das Glossar, prueft jeden Absatz, erzwingt D-02 und loest Erklaertexte und Glossar in einem `loese_auf` auf; `texte.json` hat jetzt `haushaltsjahr, texte, glossar, werte`.
- `typen.ts`: `Glossarbegriff` und `Texte.glossar`. README: Glossarformat, D-02-Regel, WR-04-Hinweis.

## Task Commits

1. **Task 1: Tracer Text-Vertrag** - `9951542` (feat): texte.py, schema.py, test_texte.py; Entwuerfe bewusst nicht committet
2. **Task 2: Abnahme** - kein Commit (Checkpoint, "Freigegeben")
3. **Task 3: Abnahme einarbeiten, Glossar nach texte.json, Typen, Tests** - `fb6959a` (feat)

**Plan metadata:** wird mit diesem SUMMARY committet (docs).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, Plan-Hinweise] Seitenbelege korrigiert**
- **Found during:** Task 1 (Entwurf)
- **Issue:** Die Plan-Hinweise nannten Haushaltssicherung S. 24 und Abschreibungen S. 37 ff.; der PDF-Text zeigt S. 23 bzw. S. 45.
- **Fix:** Belege gegen den PDF-Text gesetzt (Haushaltssicherung S. 23, Abschreibungen S. 45, NKF S. 15, Produkt/Produktbereich S. 17).
- **Files modified:** daten/manuell/texte/glossar.md
- **Commit:** fb6959a

**2. [Rule 3 - Blocking/Konsistenz] Test-Aenderungen an test_texte.py vor Task 3 im Arbeitsbaum**
- **Found during:** Task 1 (Verify nach den Entwuerfen)
- **Issue:** Mit den Entwuerfen im Arbeitsbaum haette der Gleichheitstest `_D16_SCHLUESSEL` die zweite Verify-Zeile von Task 1 rot gemacht.
- **Fix:** Die Task-3-Aenderung (Obermengen-Test mit `_ERKLAERUNGEN_SCHLUESSEL`, Glossar-Tests) bereits im Arbeitsbaum eingearbeitet, aber erst mit Task 3 committet; der Task-1-Commit blieb auf die drei Dateien beschraenkt.
- **Commit:** fb6959a

**3. [Plan-Interpretation] TDD-Task 3 als ein Commit**
- **Issue:** Die Task-3-Tests auf echten Dateien liefen bereits gruen, weil die abgenommenen Daten im Arbeitsbaum lagen; fuer die Schritt-07-Tests (`test_texte_json_enthaelt_glossar`, die beiden Abbruchtests) wurde Code und Test zusammen committet, kein separater RED-Commit.
- **Mitigation:** Die Abbruchtests pruefen Mutationen auf tmp-Kopien von `daten/`; `pruefe_grundzahl_jahre` hatte RED/GREEN-Charakter durch Tests vor Code im Tracer.

---

**Total deviations:** 3 (1 Rule 1, 1 Rule 3, 1 Interpretation). **Impact:** keine Auswirkung auf Umfang oder Ergebnisse.

## TDD Gate Compliance

Task 3 war `tdd="true"`, aber ohne eigenen RED-Commit (siehe Abweichung 3). Der Tracer-Task schrieb die Parser-Tests vor der Implementierung (kein getrennter Test-Commit). `check tdd-red-evidence` wurde nicht ausgefuehrt.

## Verification

- `uv run --directory pipeline pytest -q -rs`: 515 passed, 0 skipped (node-Gegenprobe `test_port_wie_format_ts` lief, `app/node_modules` temporaer auf die Linux-Scratch-Kopie gelinkt und wieder entfernt, nichts committet).
- `ruff check` und `ruff format --check` sauber.
- Scratch-Kopie von `app/`: `type-check`, `lint`, `format:check`, `test` (14 passed), `build` grün.
- `alle.py --jahr 2026` danach: `git diff --exit-code -- daten app/src/data` sauber, keine untracked Dateien.
- Acceptance: 24 Abschnitte in glossar.md, 22 Pflichtschluessel und 7 neue Texte in `texte.json`, `interface Glossarbegriff` in typen.ts, `grundzahlen.160101.1.2024` kommt in erklaerungen.md nicht mehr vor.

## Issues Encountered

- Die Sandbox lehnt zusammengesetzte Shell-Befehle mit git ab; Befehle wurden einzeln ausgefuehrt. Die Ledger-Datei fuer `plan_head_before` wurde nicht angelegt; `8403a43` ist der bekannte Ausgangs-Commit (`git rev-list --count` ergibt 2).

## Known Stubs

None. (Kontakt-E-Mail und PDF-URL sind bewusst noch offen und gehoeren zu Plan 05-07/Phase 7; sie stehen nicht in den hier erzeugten Dateien.)

## Threat Flags

None. T-05-06 (HTML in Glossartexten) und T-05-07 (falsche Zahl) sind durch `pruefe_text`, `loese_auf`, D-02-Pruefung und die Abnahme mit Rohwert-Vorschau abgedeckt; T-05-08 durch den Checkpoint vor dem Commit der Texte.

## Next Phase Readiness

- Plan 05-04 ff. koennen `texte.glossar` und die sieben neuen Erklaertexte per Schluessel lesen; erster Glossarabsatz = Tooltip, `/glossar#<schluessel>` = Anker.
- Plan 05-11 uebernimmt die Bezugsgroessen-Liste aus "Entscheidungen aus der Abnahme"; Plan 05-07 den Platzhalter-Status fuer Kontakt und PDF-URL.

## Self-Check: PASSED

- Gefunden: daten/manuell/texte/glossar.md, Commits 9951542 und fb6959a.
