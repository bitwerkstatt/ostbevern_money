---
phase: 04-manuelle-daten-und-app-daten
plan: 04
subsystem: pipeline-and-app-data
tags: [polars, pytest, haushalt-json, kl-split, zuschussbedarf, finanzplan, produkte-json, investitionen-json, schuldenstand]

requires:
  - phase: 04-manuelle-daten-und-app-daten (04-02, 04-03)
    provides: "app_daten.schreibe_app_json/erzeuge_app_daten-Grundgerüst, manuell.schuldenstand_euro/pro_kopf_euro/investitionskredite_ende, pruefung.WEITERGABE_POSTEN/REGEL5_TOLERANZ_GEP_EURO, haushalt.json meta/eigenkapital, stellenplan.json"
provides:
  - "haushalt.json knoten/ergebnisplan/finanzplan: synthetischer KL-Knoten (Weitergabe an Kreis und Land) mit drei gerundeten Unterposten, PB16/PG1601/P160101 um TP Z. 15 reduziert, Zuschussbedarf je Knoten (D-01 bis D-04, D-22, D-23)"
  - "app_daten.baue_knoten/baue_ergebnisplan/baue_finanzplan, ERGEBNISPLAN_APP_ZEILEN, KL_CODE/KL_NAME/KL_POSTEN_NAMEN, GESAMT_CODE/GESAMT_NAME"
  - "app/src/data/produkte.json (63 Produkte + Grundzahlen, namensfrei) und app/src/data/investitionen.json (Maßnahmen inkl. PB, VE-Fälligkeiten, Finanzierung, Schuldenstand mit D-14-Fortschreibung, Bürgschaften)"
  - "app_daten.baue_produkte_json/baue_investitionen_json, APP_PRODUKT_SCHLUESSEL, PRODUKTE_APP_JSON, INVESTITIONEN_JSON"
  - "typen.ts: Knoten, KnotenWerte, FinanzplanWerte, Grundzahl, GrundzahlWert, Erlaeuterung, Produkt, Massnahme, VeFaelligkeit, Finanzierung, Schuldenstand, Buergschaft, Investitionen; daten.ts exportiert typisierte produkte/investitionen"
affects: ["05", "06"]

actuals:
  tokens: 268000
  tasks: 2
  commits: 2
  plan_head_before: 89e301e5e6469b3a3d67a8bb8db5a15dc89f3dd2
  plan_head_after: 26e9a1eab46bf0ced6f38968d7345944fcda1faa

tech-stack:
  added: []
  patterns:
    - "KL-Herauslösung lebt ausschließlich in app_daten.py als In-Memory-Overlay auf den Planwerte-Basiswerten (direkte Δ-Addition/-Subtraktion auf die betroffenen Zeilen), nie als Mutation von daten/aufbereitet/{hierarchie,ergebnisplan}.csv — die Formellinearität (D-23) macht die Overlay-Arithmetik exakt äquivalent zu einer Neuberechnung der Formelketten"
    - "ERGEBNISPLAN_APP_ZEILEN löst die GEP-27/28- vs. TP-30/31-Zeilennummerndifferenz über einen Reverse-Lookup (kanonisch -> Zeilennummer je Plantyp) auf, statt die Zeilennummern hart zu verdrahten"
    - "polars .unique() ist NICHT reihenfolgestabil (hash-basiert) — jede Stelle, an der eine deterministische JSON-Ausgabe von einer Zeilenmenge abhängt, muss .unique() nur als Mengentest verwenden und die Ausgabereihenfolge aus einer festen Struktur (hier: ZEILEN-Dict-Einfügereihenfolge) ableiten"
    - "produkte.json/investitionen.json folgen demselben Allowlist-Schema-Validierungs-Muster wie schema.schreibe_produkte_json (APP_PRODUKT_SCHLUESSEL exakt, AppDatenFehler bei Abweichung)"
    - "Investitionsmaßnahmen werden nach (produkt, massnahme_id, konto) gruppiert statt 1:1 aus investitionen.csv übernommen, weil eine Zeile dort ein (Jahr, Wertart)-Paar ist; PB kommt über die hierarchie.csv-Eltern-Kette (P -> PG -> PB), nie hartkodiert"
    - "Schuldenstand-Fortschreibung trennt investitionskredite und nrw_bank in getrennte Felder (statt der kombinierten manuell.schuldenstand_euro-Summe), weil die App beide Komponenten separat braucht (nrw_bank konstant ab dem letzten gedruckten Jahr, investitionskredite über manuell.investitionskredite_ende fortgeschrieben)"

key-files:
  created:
    - app/src/data/produkte.json
    - app/src/data/investitionen.json
  modified:
    - pipeline/ostbevern/app_daten.py
    - pipeline/tests/test_app_daten.py
    - app/src/data/haushalt.json
    - app/src/data/typen.ts
    - app/src/data/daten.ts

key-decisions:
  - "Die KL-Herauslösung überschreibt die Zeilenwerte direkt pro Knoten (Δ auf Aufwand-/Ergebnis-Zeilen), statt die zugrunde liegenden Planwerte zu mutieren und die Formeln neu auszuwerten — mathematisch äquivalent, da alle betroffenen Formeln linear in der verschobenen Zeile sind, aber einfacher zu testen und zu verifizieren"
  - "produkte.json/investitionen.json liegen als eigene Dateien statt als zusätzliche haushalt.json-Schlüssel, konsistent mit D-21s Dateischnitt"
  - "ve in FinanzplanWerte/Massnahme ist ein einzelner int (nicht je jahre-Array), weil Verpflichtungsermächtigungen nur für das Haushaltsjahr geführt werden — eine zweite, parallele Jahresachse hätte die meisten Einträge mit Nullen/Nulls aufgefüllt"

patterns-established:
  - "Overlay-Δ-Arithmetik für synthetische Knotenaufteilungen: Basiswerte unverändert aus Planwerte lesen, dann eine feste Menge von Zeilen um ein Δ verschieben (nie die Quelle mutieren)"

requirements-completed: [DATA-02, DATA-03]

coverage:
  - id: D1
    description: "haushalt.json trägt die vollständige Knotenliste (15 PB inkl. KL, synthetische PG/P, GESAMT, KL-Block mit drei gerundeten Kindern) und je Knoten die Ergebnisplan-Zeilen 01-26 + Minderaufwand + Ergebnis danach, mit der KL-Herauslösung exakt nach D-01 bis D-03"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_kl_knoten_gleich_tp_15"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_kl_knoten_reduziert_kette"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_kl_knoten_kinder_gerundet"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_ergebnisplan_ohne_interne_leistungen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_finanzplan_nur_gesamt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_hierarchie_csv_unveraendert"
        status: pass
      - kind: other
        ref: "command: uv run --directory pipeline python -c \"...assert k['KL']['eltern']=='GESAMT' ...\" (Task-1-Acceptance-Kriterien)"
        status: pass
    human_judgment: false
  - id: D2
    description: "berechnet.aufwand/ertraege/zuschussbedarf/ueberschuss je Knoten nach D-23-Formel; Σ der 15 Top-Knoten (PB16 reduziert, plus KL) == Σ der 15 unreduzierten PB für jede Zeile/Jahr; GESAMT-Aufwand/Erträge im Haushaltsjahr treffen die Satzung; Allgemeine Finanzwirtschaft hat ueberschuss true"
    requirement: "DATA-03"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_zuschussbedarf_formel"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_zuschussbedarf_summe_top_knoten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_zuschussbedarf_allgemeine_finanzwirtschaft_ueberschuss"
        status: pass
    human_judgment: false
  - id: D3
    description: "produkte.json (63 Produkte + Grundzahlen, APP_PRODUKT_SCHLUESSEL-Allowlist, keine Personenfelder) und investitionen.json (Maßnahmen mit PB, VE-Fälligkeiten, Finanzierung aus GFP, Schuldenstand mit D-14-Fortschreibung, Bürgschaften) erzeugt und typisiert; alle App-JSON-Dateien reproduzieren byte-identisch und bestehen den Personennamen-Scan"
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_produkte_json_ohne_personenfelder"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_investitionen_massnahmen_summen_und_pb"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_investitionen_schuldenstand_fortschreibung"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_keine_personennamen_in_app_daten"
        status: pass
      - kind: other
        ref: "command: uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data"
        status: pass
    human_judgment: false

duration: ca. 1h30min
completed: 2026-10-03
status: complete
---

# Phase 4 Plan 04: KL-Knoten, Zuschussbedarf und App-Daten (produkte/investitionen) Summary

**`haushalt.json` trägt jetzt den vollständigen Knotenbaum mit der synthetischen "Weitergabe an Kreis und Land" (eurogenau aus TP 160101 Z. 15 herausgelöst) und den nach D-23 berechneten Zuschussbedarf je Knoten; `produkte.json` und `investitionen.json` (inkl. Finanzierung, Schuldenstand-Fortschreibung und Bürgschaften) runden den App-Datenbestand ab.**

## Performance

- **Duration:** ca. 1h30min
- **Started:** ca. 2026-10-03T11:30:00Z
- **Completed:** 2026-10-03T12:53:03Z
- **Tasks:** 2 von 2
- **Files modified:** 5 geändert, 2 neu

## Accomplishments

- `app_daten.baue_knoten`: vollständige Knotenliste (GESAMT, alle hierarchie.csv-Zeilen in Dateireihenfolge, synthetischer KL-Knoten plus drei gerundete Unterposten-Kinder in `pruefung.WEITERGABE_POSTEN`-Reihenfolge), `daten/aufbereitet/hierarchie.csv` bleibt byte-identisch
- `app_daten.baue_ergebnisplan`: Ergebnisplan-Zeilen 01-26 + Minderaufwand + Ergebnis danach je Knoten (Reverse-Lookup über `ZEILEN` statt hartkodierter GEP-27/28- vs. TP-30/31-Zeilennummern), KL-Herauslösung als Δ-Overlay auf Produkt/PG/PB-Kette und KL/KL.&lt;posten&gt;, `berechnet.{aufwand,ertraege,zuschussbedarf,ueberschuss}` nach D-23 ohne Sonderregel für irgendeinen Knoten
- `app_daten.baue_finanzplan`: Gesamtfinanzplan nur auf GESAMT-Ebene, alle 41 Zeilen plus VE-Werte zum Haushaltsjahr
- `app_daten.baue_produkte_json`: 63 Produkte aus `daten/aufbereitet/produkte.json` (bereits namensfrei) plus Grundzahlen je `position`, Allowlist `APP_PRODUKT_SCHLUESSEL`
- `app_daten.baue_investitionen_json`: 137 Maßnahmen gruppiert nach (Produkt, Maßnahme, Konto) inkl. PB über die Hierarchie-Kette, VE-Fälligkeiten, Finanzierung (GFP Z. 23/30/33/35), Schuldenstand mit D-14-Fortschreibung (NRW.Bank-Anteil konstant ab dem letzten gedruckten Stand, Investitionskredite über `manuell.investitionskredite_ende`), Bürgschaften
- `typen.ts`/`daten.ts`: `Knoten`, `KnotenWerte`, `FinanzplanWerte`, `Grundzahl`, `Produkt`, `Massnahme`, `VeFaelligkeit`, `Schuldenstand`, `Investitionen` — typisierter Zugriff ohne `as`/`unknown`
- 14 neue Verhaltenstests, alle 419 Pipeline-Tests grün, `alle.py` reproduziert `daten/` und `app/src/data/` byte-identisch, App-Checks (type-check/lint/format:check/build) grün in einer Scratch-Kopie

## Task Commits

Jeder Task wurde atomar committet:

1. **Task 1: Knoten, KL split and Zuschussbedarf in haushalt.json** - `4a62b17` (feat)
2. **Task 2: produkte.json mit Grundzahlen und investitionen.json mit Finanzierung/Schuldenstand** - `26e9a1e` (feat)

## Files Created/Modified

- `pipeline/ostbevern/app_daten.py` - `baue_knoten`, `baue_ergebnisplan`, `baue_finanzplan`, `baue_produkte_json`, `_baue_massnahmen`, `baue_investitionen_json`, `GESAMT_CODE`/`GESAMT_NAME`/`KL_CODE`/`KL_NAME`/`KL_POSTEN_NAMEN`, `ERGEBNISPLAN_APP_ZEILEN`, `PRODUKTE_APP_JSON`, `APP_PRODUKT_SCHLUESSEL`, `INVESTITIONEN_JSON`
- `pipeline/tests/test_app_daten.py` - 14 neue Tests (KL-Identität, Reduktionskette, Rundung, Zuschussbedarf-Formel/-Erhaltung, Allgemeine-Finanzwirtschaft-Überschuss, keine TP 27/28, Finanzplan nur GESAMT, hierarchie.csv unverändert, Produkte ohne Personenfelder, Maßnahmen-Summen, Schuldenstand-Fortschreibung)
- `app/src/data/haushalt.json` - trägt jetzt `knoten`, `ergebnisplan`, `finanzplan` (nach `meta`, vor `vorbericht`)
- `app/src/data/produkte.json` (neu) - 63 Produkte + Grundzahlen
- `app/src/data/investitionen.json` (neu) - Maßnahmen, VE-Fälligkeiten, Finanzierung, Schuldenstand, Bürgschaften
- `app/src/data/typen.ts` - `Knoten`, `KnotenWerte`, `FinanzplanWerte`, `Grundzahl`, `GrundzahlWert`, `Erlaeuterung`, `Produkt`, `Massnahme`, `VeFaelligkeit`, `Finanzierung`, `Schuldenstand`, `Buergschaft`, `Investitionen`
- `app/src/data/daten.ts` - typisierte `produkte`/`investitionen`-Exporte

## Decisions Made

- KL-Herauslösung als direktes Δ-Overlay auf die betroffenen Zeilen statt Formel-Neuberechnung (mathematisch äquivalent, da alle Formeln linear in der verschobenen Zeile sind)
- `produkte.json`/`investitionen.json` als eigene Dateien, konsistent mit D-21s Dateischnitt
- `ve` als einzelner int (nicht je `jahre`), da Verpflichtungsermächtigungen nur für das Haushaltsjahr geführt werden

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `polars.Series.unique()` ist nicht reihenfolgestabil**
- **Found during:** Task 1 (`baue_finanzplan`, VE-Zeilenmenge)
- **Issue:** `finanzplan.filter(...)['zeile'].unique().to_list()` lieferte bei wiederholten Läufen unterschiedliche Reihenfolgen (verifiziert durch dreifachen Direktaufruf), was `test_app_json_deterministisch` sofort rot färbte und D-24 (deterministisches JSON) verletzt hätte
- **Fix:** `.unique()` nur noch als Mengentest (`set(...)`) verwendet; die Ausgabereihenfolge der `ve`-Werte kommt jetzt aus der festen Einfügereihenfolge von `ZEILEN["gesamtfinanzplan"]`
- **Files modified:** `pipeline/ostbevern/app_daten.py`
- **Verification:** `test_app_json_deterministisch` lief danach wiederholt grün; Kommentar im Code dokumentiert den Befund für künftige `.unique()`-Verwendungen
- **Committed in:** `4a62b17` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 Bug).
**Impact on plan:** Notwendig für D-24 (deterministische JSON-Ausgabe); kein Scope Creep, keine Abweichung von der Plan-Beschreibung.

## Issues Encountered

Keine blockierenden Probleme. Für atomare Task-Commits wurden Task-2-Codeänderungen temporär zurückgenommen (Imports, Konstanten/Funktionen, Wiring in `erzeuge_app_daten`, Testfälle, `typen.ts`/`daten.ts`-Ergänzungen), Task 1 isoliert committet und verifiziert, dann Task 2 erneut angewendet, regeneriert und verifiziert — beide Tasks sind dadurch einzeln revertierbar, exakt wie im Plan vorgesehen.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `baue_knoten`/`baue_ergebnisplan`/`baue_finanzplan` liefern die Knotenstruktur und Zuschussbedarf-Werte, auf denen Phase 5 (Treemap, Sankey, Ausgabenseite) und Phase 6 (Rat entscheidet) aufbauen (D-03: Reversibility costly).
- `produkte.json`/`investitionen.json` stehen für die Produktdetail- und Investitionen/Schulden-Seiten (Phase 5/6) bereit.
- DATA-02 und DATA-03 sind vollständig abgeschlossen. DATA-01 bleibt bis zum Abschluss von Plan 04-05 (gemeinsam deklariertes Requirement) offen — die shared-ID-Gate-Logik (`requirements.ready-ids`) hat das korrekt erkannt und nur DATA-02/DATA-03 markiert.
- Alle zehn Prüfregeln (1-10) bleiben grün; `alle.py` ist vollständig reproduzierbar (`git diff --exit-code -- daten app/src/data` leer, keine ungetrackten Dateien).

---
*Phase: 04-manuelle-daten-und-app-daten*
*Completed: 2026-10-03*

## Self-Check: PASSED

- All `key-files.created` paths verified present on disk: `[ -f app/src/data/produkte.json ]`, `[ -f app/src/data/investitionen.json ]`.
- Both task commits (`4a62b17`, `26e9a1e`) confirmed via `git log --oneline -3`.
- Re-ran Task 1 acceptance criteria (GESAMT aufwand/ertraege == Satzung, KL transferaufwendungen == TP Z. 15, PB 16 ueberschuss true, KL/KL.kreisumlage knoten fields, finanzplan == ["GESAMT"], no "interne_ertraege") via `uv run python -c ...`: all pass.
- Re-ran Task 2 acceptance criteria (63 Produkte ohne Personenfelder, Schuldenstand pro_kopf/investitionskredite/berechnet/nrw_bank) via `uv run python -c ...`: all pass.
- Re-ran the plan-level `<verification>` block: `uv run --directory pipeline pytest -q` (419 passed, twice), `uv run ruff check .` / `ruff format --check .` (clean), `alle.py --jahr 2026` followed by `git diff --exit-code -- daten app/src/data` and an untracked-file check (both clean), app `type-check`/`lint`/`format:check`/`build` in a fresh scratch copy (all green, twice — once per task state).
- `uv run --directory pipeline pytest tests/test_app_daten.py -q -k "kl_knoten or zuschussbedarf"` reports 6 passed (acceptance criterion: at least 6).
