---
phase: 04-manuelle-daten-und-app-daten
plan: 05
subsystem: pipeline-and-app-data
tags: [placeholder-contract, texte-json, pytest, format-ts, pruef-10, d-17-review]

requires:
  - phase: 04-manuelle-daten-und-app-daten (04-01, 04-04)
    provides: "app_daten.erzeuge_app_daten/schreibe_app_json-Grundgerüst, haushalt.json/investitionen.json/produkte.json mit KL-Knoten, Zuschussbedarf, Schuldenstand-Fortschreibung, meta.json/manuell.lies_meta_json, format.ts euro/euroKurz/zahl/vzae/prozent"
provides:
  - "ostbevern.texte: Platzhalter-Parser/-Prüfung/-Auflösung für Erklärtexte (lies_erklaerungen, pruefe_text, textwerte, loese_auf, vorschau, FORMATKUERZEL, ABGELEITET-Formelregistry) — D-15 Vertrag zwischen Pipeline, Textdatei und App"
  - "app/src/charts/format.ts: FormatKuerzel-Union und formatiere()-Dispatcher — die App-seitige Hälfte des D-15-Vertrags"
  - "daten/manuell/texte/erklaerungen.md: zehn fachlich geprüfte und freigegebene Erklärtexte (D-16/D-17) mit Datenplatzhaltern"
  - "app/src/data/texte.json + typen.ts Erklaertext/Texte + daten.ts texte-Export: letztes Teil des App-Datenbestands (D-21, DATA-01 abgeschlossen)"
  - "PRUEF-10 abgeschlossen: alle.py 01→02→03→04→Querschnitte→05→06→07 reproduzierbar, CI-Diff-Schritt grün"
affects: ["05", "06"]

actuals:
  tokens: 16899
  tasks: 3
  commits: 2
  plan_head_before: c6b184d01687cc61947161d2f001be0322e17aad
  plan_head_after: f9e085d6e44e274ccd938a51f57d3a5057e7722b

tech-stack:
  added: []
  patterns:
    - "Platzhalter-Syntax {{schluessel|formatkuerzel}}: die Pipeline löst den Schlüssel gegen einen kuratierten Werte-Namensraum auf und schreibt den Rohwert; formatiert wird ausschließlich in format.ts::formatiere (D-15) — zwei parallele Enum-Listen (FORMATKUERZEL in texte.py, FormatKuerzel in format.ts) werden durch einen Regex-Test (test_formatkuerzel_wie_format_ts) synchron gehalten"
    - "Ziffernregel per pruefe_text: valide Platzhalter werden zuerst textuell entfernt, danach werden Jahreszahlen/§-Verweise/Seitenverweise abgezogen; jede verbleibende Ziffer ist ein Fehler — macht das Format selbstprüfend ohne externes Lint-Tool"
    - "ABGELEITET-Formelregistry: benannte Python-Funktionen (relative Namen wie *_haushaltsjahr, nie ein Jahrgangswert) lesen jahr.haushaltsjahr/jahr.vorjahr aus dem bereits gebauten Werte-Dict, um den konkreten Jahresschlüssel zur Laufzeit zu bilden — hält D-15 (keine Jahrgangswerte im Code) auch für abgeleitete Werte ein"
    - "texte.json schreibt nur die tatsächlich verwendeten Platzhalter-Werte (loese_auf-Ergebnis), nie den vollständigen textwerte-Namensraum (hunderte ungenutzte Schlüssel) — kleineres, stabileres Artefakt"
    - "D-17-Workflow: Task 1 committet nur den Code (texte.py/test_texte.py/format.ts), der Textentwurf und meta.json-Ergänzungen bleiben im Working Tree bis zum Checkpoint; erst nach fachlicher Freigabe (Task 2) committet Task 3 die Texte und alle regenerierten App-Daten"

key-files:
  created:
    - pipeline/ostbevern/texte.py
    - pipeline/tests/test_texte.py
    - daten/manuell/texte/erklaerungen.md
    - app/src/data/texte.json
  modified:
    - app/src/charts/format.ts
    - app/src/data/haushalt.json
    - app/src/data/typen.ts
    - app/src/data/daten.ts
    - daten/manuell/meta.json
    - daten/manuell/README.md
    - pipeline/ostbevern/app_daten.py
    - pipeline/ostbevern/schema.py
    - pipeline/07_app_daten.py
    - pipeline/alle.py
    - pipeline/tests/test_app_daten.py

key-decisions:
  - "NRW.Bank-Fortschreibungsbasis bestätigt bei 746 T€ (letzter gedruckter Stand, Ende 2026, S. 310), nicht 831 T€ (Ende 2025) — Nutzerentscheidung im Task-2-Checkpoint, keine Codeänderung nötig (04-04 hatte dies bereits korrekt implementiert)"
  - "Zwei Werte ohne eigene Datenquelle (Satzung-§-4-Eckwert 'Verringerung allgemeine Rücklage' 221.293 €, BBO-Wirtschaftsplan-Verlustausgleich 584.000 €) wandern in meta.json vorbericht_werte statt in eine neue CSV, weil sie Einzelwerte ohne Tabellenstruktur sind"
  - "Gewerbesteuer-Text nennt zwei verschiedene Quellen explizit benannt (Grundzahlen-Ist-Werte 2022-2024 vs. Vorbericht-Ansatz 2026) statt sie zu vermischen (Research Pitfall 6) — vom Nutzer im Checkpoint ausdrücklich bestätigt"
  - "texte.textwerte liest die bereits im Speicher gebauten App-Dictionaries (haushalt/investitionen/produkte-Dicts aus erzeuge_app_daten), nicht erneut von Platte — vermeidet einen zweiten Datei-Durchlauf und hält Schritt 07 PDF-frei (D-06)"

patterns-established:
  - "Checkpoint-Workflow für fachlich zu prüfende Texte: Entwurf + Validierung in Task 1 (committet nur Code), Nutzer-Freigabe in Task 2 (blocking-human), Anwendung + Commit in Task 3 — reproduzierbar für künftige Erklärtext-Erweiterungen (Phase 5/6 Glossar)"

requirements-completed: [MANU-08, PRUEF-10, DATA-01]

coverage:
  - id: D1
    description: "Zehn geprüfte Erklärtexte (schluesselzuweisung, gewerbesteuer, kreisumlage, grundsteuer_hebesaetze, sonderposten, globaler_minderaufwand, defizit_ruecklagen, schulden, verpflichtungsermaechtigungen, nicht_im_haushalt) mit Platzhaltern statt handgeschriebener Zahlen, jeweils mit PDF-Seitenverweis; fachlich vom Nutzer freigegeben (D-17-Checkpoint: 'freigegeben, NRW.Bank 746, Sprachvorschläge übernehmen')"
    requirement: "MANU-08"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_erklaerungen_umfang_d16"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_erklaerungen_keine_nackten_ziffern"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_erklaerungen_alle_schluessel_existieren"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_erklaerungen_jeder_text_hat_quelle"
        status: pass
      - kind: other
        ref: "Nutzer-Checkpoint (Task 2, D-17): Freigabe der Texte, NRW.Bank-Basis und drei Formulierungskorrekturen, protokolliert in diesem Plan-Verlauf"
        status: pass
    human_judgment: false
  - id: D2
    description: "alle.py (01→02→03→04→Querschnitte→05→06→07) reproduzierbar; CI-Diff-Schritt grün: nach erneutem Lauf kein Diff und keine ungetrackten Dateien unter daten/ und app/src/data/"
    requirement: "PRUEF-10"
    verification:
      - kind: other
        ref: "command: uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data && test -z \"$(git status --porcelain --untracked-files=all -- daten app/src/data)\""
        status: pass
      - kind: unit
        ref: "pipeline: uv run pytest -q (456 passed)"
        status: pass
      - kind: other
        ref: "command: cd pipeline && uv run ruff check . && uv run ruff format --check ."
        status: pass
      - kind: other
        ref: "command: npm ci && npm run type-check && npm run lint && npm run format:check && npm run build (Scratch-Kopie, zweimal ausgeführt)"
        status: pass
    human_judgment: false
  - id: D3
    description: "texte.json schließt den App-Datenbestand von D-21 ab (haushalt/produkte/investitionen/stellenplan/texte.json); typisierter Zugriff ohne as/unknown über typen.ts/daten.ts; werte enthält ausschließlich die tatsächlich verwendeten Datenschlüssel"
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_texte_json_nur_verwendete_werte"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_texte_json_eingecheckt_aktuell"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_unbekannter_platzhalter_bricht_schritt_07_ab"
        status: pass
      - kind: other
        ref: "command: npm run type-check (vue-tsc --build, daten.ts weist texteJson ohne Typumwandlung Texte zu)"
        status: pass
    human_judgment: false

duration: ca. 50 min (inkl. Wartezeit auf Nutzer-Freigabe im Checkpoint)
completed: 2026-10-03
status: complete
---

# Phase 4 Plan 05: Erklärtexte, texte.json und Reproduzierbarkeits-Gate Summary

**Zehn vom Nutzer fachlich freigegebene Erklärtexte mit Datenplatzhaltern (`{{schluessel|format}}`) laufen jetzt durch Schritt 07 zu `app/src/data/texte.json`; der Platzhalter-Vertrag zwischen Pipeline (`ostbevern.texte`) und App (`format.ts::formatiere`) ist getestet, und die volle Pipeline (01–07) ist reproduzierbar — Phase 4 ist damit inhaltlich abgeschlossen.**

## Performance

- **Duration:** ca. 50 min (Task 1 Entwurf + Validierung, Task 2 Nutzer-Checkpoint, Task 3 Anwendung + Reproduzierbarkeits-Gate)
- **Started:** 2026-10-03T21:00:00Z (ca.)
- **Completed:** 2026-10-03T21:48:28+02:00
- **Tasks:** 3 von 3 (inkl. ein blocking-human Checkpoint)
- **Files modified:** 15 (4 neu, 11 geändert)

## Accomplishments

- `ostbevern/texte.py` (neu): `TexteFehler`, `FORMATKUERZEL`, `PLATZHALTER_MUSTER`, `Erklaertext`, `lies_erklaerungen`, `pruefe_text`, `textwerte`, `ABGELEITET`, `loese_auf`, `vorschau` — vollständiger Platzhalter-Vertrag (D-15), 34 Tests
- `app/src/charts/format.ts`: `FormatKuerzel`-Union und `formatiere()`-Dispatcher, die App-seitige Hälfte des Vertrags; ein Regex-Test hält beide Seiten synchron
- Zehn Erklärtexte in `daten/manuell/texte/erklaerungen.md` (schluesselzuweisung, gewerbesteuer, kreisumlage, grundsteuer_hebesaetze, sonderposten, globaler_minderaufwand, defizit_ruecklagen, schulden, verpflichtungsermaechtigungen, nicht_im_haushalt) — entworfen, gegen das PDF geprüft, vom Nutzer fachlich freigegeben (D-17) inkl. drei Formulierungskorrekturen
- Zwei neue `meta.json`-`vorbericht_werte`-Einträge für Werte ohne eigene Datenquelle (Satzung-§-4-Eckwert, BBO-Wirtschaftsplan)
- `app_daten.erzeuge_app_daten` baut jetzt auch `texte.json`: parst, prüft und löst die Texte gegen die bereits im Speicher gebauten App-Dictionaries auf (kein zweiter Datei-Durchlauf), schreibt nur die tatsächlich verwendeten Werte
- `typen.ts`/`daten.ts`: `Erklaertext`, `Texte`, typisierter `texte`-Export
- `TexteFehler` bricht `07_app_daten.py` und `alle.py` fail-fast ab wie `AppDatenFehler`
- Volles Reproduzierbarkeits-Gate grün: 456 Pipeline-Tests, ruff clean, `alle.py` erzeugt `daten/` und `app/src/data/` byte-identisch zum committeten Stand, App `type-check`/`lint`/`format:check`/`build` grün in einer Scratch-Kopie (PRUEF-10)

## Task Commits

Jeder Task wurde atomar committet:

1. **Task 1: texte.py Platzhalter-Vertrag, formatiere in format.ts, draft erklaerungen.md (uncommitted)** - `f3e9ad2` (feat)
2. **Task 2: Fachliche Abnahme der Erklärtexte und der Schulden-Fortschreibung (D-17)** — Checkpoint, keine eigene Code-Änderung; Nutzer-Freigabe: "freigegeben, NRW.Bank 746, Sprachvorschläge übernehmen"
3. **Task 3: Apply review, commit texts, texte.json via Schritt 07, final reproducibility gate (PRUEF-10)** - `f9e085d` (feat)

**Plan metadata:** folgt in diesem Commit (docs: complete plan)

## Files Created/Modified

- `pipeline/ostbevern/texte.py` (neu) - Platzhalter-Parser/-Prüfung/-Auflösung (D-15)
- `pipeline/tests/test_texte.py` (neu) - 34 Tests inkl. `test_formatkuerzel_wie_format_ts`, vier Echte-Datei-Tests gegen `erklaerungen.md`
- `daten/manuell/texte/erklaerungen.md` (neu) - zehn freigegebene Erklärtexte
- `app/src/data/texte.json` (neu) - Rohtexte + nur verwendete Rohwerte
- `app/src/charts/format.ts` - `FormatKuerzel`, `formatiere()`
- `app/src/data/haushalt.json` - trägt jetzt die zwei neuen `vorbericht_werte`
- `app/src/data/typen.ts` / `daten.ts` - `Erklaertext`, `Texte`, `texte`-Export
- `daten/manuell/meta.json` - zwei neue `vorbericht_werte`-Einträge
- `daten/manuell/README.md` - Dokumentation des Platzhalter-Formats, bestätigte NRW.Bank-Basis
- `pipeline/ostbevern/app_daten.py` - `TEXTE_JSON`, texte.json-Writer in `erzeuge_app_daten`
- `pipeline/ostbevern/schema.py` - `ERKLAERUNGEN_MD`-Pfadkonstante
- `pipeline/07_app_daten.py` / `pipeline/alle.py` - `TexteFehler` in der Fehlerbehandlung
- `pipeline/tests/test_app_daten.py` - zwei neue Tests (`test_texte_json_nur_verwendete_werte`, `test_unbekannter_platzhalter_bricht_schritt_07_ab`), `test_texte_json_eingecheckt_aktuell`, Pfadlisten-Assertions erweitert

## Decisions Made

- NRW.Bank-Fortschreibungsbasis bestätigt bei 746 T€ (letzter gedruckter Stand) statt 831 T€ — keine Codeänderung nötig, 04-04 war bereits korrekt
- Zwei Satzungs-/Wirtschaftsplan-Werte ohne eigene Tabelle landen in `meta.json` `vorbericht_werte` statt in einer neuen CSV
- Gewerbesteuer-Text benennt zwei Quellen (Grundzahlen-Ist vs. Vorbericht-Ansatz) statt sie zu vermischen
- `textwerte` liest die im Speicher gebauten App-Dictionaries statt erneut von Platte zu lesen

## Deviations from Plan

None — plan executed exactly as written. `pipeline/07_app_daten.py` und `pipeline/alle.py` wurden geändert (Fehlerbehandlung für `TexteFehler`), wie im Plan-Text von Task 3 explizit vorgegeben ("catch it in 07_app_daten.py and alle.py like AppDatenFehler"), auch wenn beide Dateien nicht in der `<files>`-Liste des Tasks standen — dies ist die direkte Umsetzung der Plan-Anweisung, keine Abweichung.

## Issues Encountered

None. Die drei Nutzer-Korrekturen aus dem Checkpoint (kreisumlage, sonderposten, grundsteuer_hebesaetze) wurden angewendet und gegen die Ziffernregel/Schlüsselauflösung erneut validiert, bevor Task 3 begann.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 4 ist mit diesem Plan inhaltlich abgeschlossen: alle fünf App-JSON-Dateien (`haushalt`, `produkte`, `investitionen`, `stellenplan`, `texte`) sind vorhanden, typisiert und reproduzierbar.
- Phase 5/6 können `app/src/data/texte.json` direkt importieren und die Platzhalter zur Laufzeit mit `format.ts::formatiere` auflösen (D-15); das Glossar (Phase 5) folgt demselben Checkpoint-Workflow für künftige Begriffe.
- PRUEF-10 ist vollständig erfüllt; die CI (`.github/workflows/ci.yml`) muss nur noch auf einem echten GitHub-Remote laufen (bestehender Blocker aus Phase 1, unverändert).

---
*Phase: 04-manuelle-daten-und-app-daten*
*Completed: 2026-10-03*

## Self-Check: PASSED

- `key-files.created` auf Platte verifiziert: `[ -f pipeline/ostbevern/texte.py ]`, `[ -f pipeline/tests/test_texte.py ]`, `[ -f daten/manuell/texte/erklaerungen.md ]`, `[ -f app/src/data/texte.json ]` — alle vorhanden.
- Beide Task-Commits (`f3e9ad2`, `f9e085d`) via `git log --oneline -3` bestätigt.
- Re-Run aller Task-1- und Task-3-Acceptance-Criteria (Commit-Dateisatz, Draft-nicht-committet-Status vor Task 2, `grep -c '^## '` >= 10, `formatiere`-Export, `test_formatkuerzel_wie_format_ts`, texte.json-Inhalt, `test_texte.py -q`, `Gesamtstatus: grün`, ruff clean, finaler `alle.py`+Diff-Check): alle bestanden.
- Plan-Level-Verifikation erneut ausgeführt: `uv run --directory pipeline pytest -q` (456 passed), `uv run ruff check .`/`ruff format --check .` (clean), `alle.py --jahr 2026` gefolgt von `git diff --exit-code -- daten app/src/data` und leerem `git status --porcelain --untracked-files=all` (beide leer), App `type-check`/`lint`/`format:check`/`build` in einer frischen Scratch-Kopie (alle grün, zweimal ausgeführt — einmal vor, einmal nach dem finalen Commit).
