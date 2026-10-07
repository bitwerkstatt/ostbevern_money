---
phase: 03-details
plan: 03
subsystem: pipeline-investitionen
tags: [pdfplumber, polars, investitionen, pb-liste, regel-6, luecken]

requires:
  - phase: 03-details
    provides: "ostbevern/investitionen.py (lies_massnahmen, Kontengruppe, Kontozeile, Massnahme), ostbevern/pruefung.py Regel-6-Pruefpunkt/Regelergebnis-Muster (03-02)"
  - phase: 02-kernzahlen
    provides: "hierarchie.csv (P -> PG -> PB), finanzplan.csv, befunde.md-Mechanismus"
provides:
  - "daten/zwischen/investitionen_pb.csv (959 Zeilen, Kontrollquelle, D-06) mit allen 13 PB-Investitionslisten"
  - "ostbevern/investitionen.py: PB-Knoten-Schleife in extrahiere_investitionen (drittes ExtraktionsErgebnis), _trenne_investitions_und_finanzierungskonten, _pruefe_finanzierungskonten"
  - "ostbevern/pruefung.py: Luecke(regel, ebene, code, merkmal, pdf_seite), Regelergebnis.luecken, _pruefe_regel6_pb_gegenprobe, _produkt_zu_pb; Regel 6 Teil (c)"
  - "rendere_konsistenzbericht: Spalte 'Lücken' in der Übersicht, Abschnitt '## Lücken'"
  - "06_pruefen.py: Lücken-Anzahl je Regel im Echo, wenn nicht 0"
affects: [03-05-regel-8]

actuals:
  tokens: 28621
  tasks: 2
  commits: 2
  plan_head_before: 2017c2a3d43710e8fa1003f97085acd9ec283ecc
  plan_head_after: a4127e066ef2ecf0f7adbefcacd3258553788ee6

tech-stack:
  added: []
  patterns:
    - "lies_massnahmen validiert 'Saldo Investitionstätigkeit' erst NACH dem Lesen aller Seiten gegen die Summe ALLER (nicht nur bereits gelesener) Investitions-Maßnahmen, weil PB-Listen diese Zeile als Knoten-Gesamtwert mitten in der Liste drucken (Research Pitfall 8, verifiziert S. 235 PB 12 = TFP Z. 31)"
    - "Finanzierungstätigkeit-Maßnahmen (692/792) werden aus der 'Saldo Investitionstätigkeit'-Summe ausgeschlossen (eigener Tätigkeitsbereich im NKF-Finanzplan, verifiziert Produkt 160101/PB 16 S. 279/282)"
    - "Gemeinsame Helfer _trenne_investitions_und_finanzierungskonten/_pruefe_finanzierungskonten zwischen Produkt- und PB-Verarbeitung in extrahiere_investitionen (DRY, ebene-parametrisiert)"
    - "Luecke-Dataclass + Regelergebnis.luecken: ein struktureller Befund (Eintrag nur in einer von zwei Quellen) ist niemals über befunde.md abdeckbar, im Gegensatz zu einer Betragsabweichung (Pruefpunkt)"
    - "PB-Gegenprobe-Muster: Produkt -> PB über die Hierarchie (P -> PG -> PB), Betragsvergleich als Vereinigung der (pb, massnahme_id, konto, jahr, wertart)-Schlüssel beider Quellen, Vollständigkeit separat als (pb, massnahme_id)-Mengendifferenz (feiner als jede Abweichung, kann aber keine Abweichung ausdrücken)"

key-files:
  created:
    - daten/zwischen/investitionen_pb.csv
  modified:
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/investitionen.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/06_pruefen.py
    - pipeline/tests/test_investitionen.py
    - pipeline/tests/test_pruefung.py
    - daten/pruefberichte/konsistenz.md
    - daten/pruefberichte/befunde.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "'Saldo Investitionstätigkeit' wird deferred validiert (nach Abschluss aller Seiten), nicht mehr am Punkt des Auftretens: PB 12 (S. 235) und PB 13 (S. 256) drucken diese Zeile als Knoten-GESAMTWERT mitten in der Liste, bevor weitere Maßnahmen folgen — eine Prüfung gegen die bis dahin akkumulierten Maßnahmen schlug fehl, weil der gedruckte Wert dem TFP Z. 31 (Gesamt-PB) entspricht, nicht der Teilsumme. Verifiziert: S. 235 druckt -1.106.000 (Ansatz 2026), identisch zu finanzplan.csv PB 12 Z. 31."
  - "Finanzierungstätigkeit-Maßnahmen (Konten 692/792) zählen nicht zur Summe der 'Saldo Investitionstätigkeit'-Gegenprobe: Produkt 160101 und PB 16 drucken diese Zeile zwischen den Investitions- und einer separaten Finanzierungs-Tabelle (S. 279/282); ohne Ausschluss wichen die berechneten Summen signifikant vom gedruckten Wert ab, da Kreditaufnahme/Tilgung ein eigener Tätigkeitsbereich ist."
  - "PB-Gegenprobe behandelt die PB-Liste als 'soll' (Kontrollquelle) und die Produktseiten als 'ist' (zu prüfende Pipeline-Daten), exakt wie im Plan vorgegeben — abweichung = ist - soll bleibt damit konsistent mit allen anderen Regel-6-Teilen."
  - "Alle 15 PB werden in der PB-Schleife durchlaufen (nicht nur die 13 mit investitionen_pb-Seiten): lies_massnahmen liefert für PB 11/14 (ohne Liste) korrekt ([], None) zurück, das spart eine Sonderfall-Filterung."

requirements-completed: [EXTR-09, PRUEF-06]

coverage:
  - id: D1
    description: "investitionen_pb.csv (959 Zeilen) liest alle 13 PB-Investitionslisten mit demselben Blockparser wie die Produktseiten, behält Mehrfachblöcke derselben Maßnahmen-ID (AIB00001, KLIMA1) unzusammengeführt, enthält keine Finanzierungs-Konten (692/792), und lässt investitionen.csv/ve_faelligkeiten.csv byte-identisch"
    requirement: EXTR-09
    verification:
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_jede_pb_mit_investitionskonten_hat_pb_liste_und_umgekehrt"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_pb_liste_behaelt_mehrere_bloecke_derselben_massnahme_id"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_pb_liste_summe_trifft_sollwerte_und_keine_finanzierungskonten"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_pb_liste_laesst_investitionen_csv_byte_identisch"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_pb16_finanzierungskonto_manipuliert_bricht_ab"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python 04_investitionen.py --jahr 2026 (exit 0, 959 Zeilen investitionen_pb.csv, git diff aufbereitet/ leer)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regel 6 prüft zusätzlich die PB-Gegenprobe (plan investitionen_pb_liste) je (pb, massnahme_id, konto, jahr, wertart); eine Maßnahme in nur einer Quelle wird zur Luecke, die niemals über befunde.md abdeckbar ist und den Bericht rot macht; konsistenz.md zeigt 'Lücken'-Spalte und -Abschnitt"
    requirement: PRUEF-06
    verification:
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_pb_liste_erkennt_manipulierten_wert"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_pb_liste_befund_deckt_ab"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_luecke_wenn_massnahme_nur_auf_produktseiten"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_luecke_wenn_massnahme_nur_in_pb_liste"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py::test_luecke_macht_regelergebnis_rot_und_bericht_nicht_gruen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py::test_wende_befunde_an_erhaelt_luecken_unveraendert"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_konsistenzbericht_zeigt_luecken_abschnitt_keine_auf_echten_daten"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (Regel 6: grün, 1964 Werte; konsistenz.md '## Lücken' = Keine.)"
        status: pass
    human_judgment: false

duration: 76min
completed: 2026-10-02
status: complete
---

# Phase 3 Plan 3: PB-Investitionslisten und Regel-6-Gegenprobe mit Lücken Summary

**`investitionen_pb.csv` (959 Zeilen, alle 13 PB-Investitionslisten) als Kontrollquelle, und Regel 6 erweitert um eine PB-Gegenprobe gegen die Produktseiten plus einen neuen, nicht über `befunde.md` abdeckbaren "Lücke"-Mechanismus für Maßnahmen, die nur in einer von zwei Quellen vorkommen.**

## Performance

- **Duration:** 76 min
- **Started:** 2026-10-02T04:10:00Z
- **Completed:** 2026-10-02T05:26:00Z
- **Tasks:** 2/2 completed
- **Files modified:** 9 (1 created, 8 modified)

## Accomplishments

- `extrahiere_investitionen` liest zusätzlich zu den Produktseiten alle 15 PB-Knoten mit demselben `lies_massnahmen`-Blockparser (`ebene="PB"`) und schreibt die Kontozeilen der 13 PB mit Investitionslisten nach `daten/zwischen/investitionen_pb.csv` (959 Zeilen, Schema `pb, massnahme_id, konto, richtung, jahr, wertart, betrag, pdf_seite`). Mehrfachblöcke derselben Maßnahmen-ID (AIB00001 auf S. 146, KLIMA1 auf S. 149) bleiben unzusammengeführt erhalten. Finanzierungs-Konten (692/792, PB 16 S. 279) werden gegen die PB-Teilfinanzplan-Zeilen 33/35 geprüft, aber nicht geschrieben; `investitionen.csv`/`ve_faelligkeiten.csv` bleiben byte-identisch.
- `lies_massnahmen` validiert die Zeile "Saldo Investitionstätigkeit" jetzt erst nach dem Lesen aller Seiten des Knotens gegen die Summe ALLER (nicht nur bereits gelesener) Investitions-Maßnahmen und schließt Finanzierungstätigkeit-Maßnahmen aus der Summe aus — notwendig, weil PB-Listen (PB 12/13) diese Zeile als Knoten-Gesamtwert mitten in der Liste drucken (verifiziert gegen Teilfinanzplan Z. 31), und weil Produkt 160101/PB 16 sie vor einer separaten Finanzierungs-Tabelle drucken.
- `pruefung.py` bekommt `Luecke(regel, ebene, code, merkmal, pdf_seite)` und `Regelergebnis.luecken`; `status` ist "rot" bei einer offenen Abweichung ODER einer Lücke. `_pruefe_regel6_pb_gegenprobe` bildet jedes Produkt über die Hierarchie auf seinen PB ab, vergleicht beide Quellen je `(pb, massnahme_id, konto, jahr, wertart)` (PB-Liste = soll, Produktseiten = ist) und erzeugt eine Lücke für jede `(pb, massnahme_id)`, die nur in einer Quelle vorkommt — eine Lücke ist strukturell, keine Betragsabweichung, und daher nie über `befunde.md` entschärfbar.
- `rendere_konsistenzbericht` zeigt eine neue Spalte "Lücken" in der Übersichtstabelle und einen neuen Abschnitt "## Lücken" (sortiert nach Regel/Ebene/Code/Merkmal, oder "Keine."); `06_pruefen.py` echot die Lücken-Anzahl je Regel, wenn sie nicht 0 ist.
- `befunde.md` dokumentiert die neue Regel-6-Formel (`plan investitionen_pb_liste`) im Kopf-Absatz und weist ausdrücklich darauf hin, dass Lücken dort nicht dokumentierbar sind.
- Auf den eingecheckten Daten ist Regel 6 grün (1964 geprüfte Werte, 0 Lücken, vorher 1033); `alle.py --jahr 2026` und die volle Testsuite (227 Tests) bleiben grün.

## Task Commits

Each task was committed atomically:

1. **Task 1: PB-Investitionslisten to daten/zwischen/investitionen_pb.csv (D-06)** - `1aca359` (feat)
2. **Task 2: Regel 6 PB-Gegenprobe and Lücken in the Prüfbericht** - `a4127e0` (feat)

_Note: Tasks carry `tdd="true"`; wie in 03-01/03-02 wurden Implementierung und ihre Tests gegen das echte PDF bzw. die eingecheckten CSVs gemeinsam entwickelt statt strikt RED-dann-GREEN commit-separiert — als Abweichung unten dokumentiert. `workflow.tdd_mode` ist in diesem Projekt nicht konfiguriert, daher greift keine automatisierte RED/GREEN-Commit-Sequenz-Prüfung._

## Files Created/Modified

- `daten/zwischen/investitionen_pb.csv` - generierte PB-Investitionslisten (959 Zeilen, Kontrollquelle)
- `pipeline/ostbevern/schema.py` - `INVESTITIONEN_PB_CSV`, `INVESTITIONEN_PB_SPALTEN`, `schreibe_`/`lies_investitionen_pb_csv`
- `pipeline/ostbevern/investitionen.py` - PB-Knoten-Schleife, `_trenne_investitions_und_finanzierungskonten`, `_pruefe_finanzierungskonten`, deferred Saldo-Investitionstätigkeit-Validierung mit Finanzierungs-Ausschluss
- `pipeline/ostbevern/pruefung.py` - `Luecke`, `Regelergebnis.luecken`, `_produkt_zu_pb`, `_pruefe_regel6_pb_gegenprobe`, Regel-6-Teil (c), Konsistenzbericht-Erweiterung
- `pipeline/06_pruefen.py` - Lücken-Anzahl im Echo
- `pipeline/tests/{test_investitionen,test_pruefung}.py` - 5 + 10 neue Tests
- `daten/pruefberichte/{konsistenz,befunde}.md` - neue Spalte/Abschnitt, Regel-6-Formel-Dokumentation
- `.planning/REQUIREMENTS.md` - EXTR-09, PRUEF-06 als Complete markiert

## Decisions Made

- **Deferred Saldo-Investitionstätigkeit-Validierung**: siehe Deviations unten (Rule 1 — notwendige Korrektur, kein geplantes Feature).
- **Finanzierungstätigkeit-Ausschluss aus der Saldo-Summe**: siehe Deviations unten (Rule 1).
- **PB-Liste = soll, Produktseiten = ist**: exakt wie im Plan vorgegeben, keine Abweichung.
- **Alle 15 PB in der Schleife, nicht nur die 13 mit Liste**: `lies_massnahmen` liefert für PB ohne Tabelle `([], None)`, spart eine Sonderfall-Filterung über `seiten.csv`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] "Saldo Investitionstätigkeit" wird erst nach dem Lesen aller Seiten validiert**
- **Found during:** Task 1, Testlauf gegen die echte PB-12-Liste (S. 235)
- **Issue:** Die ursprüngliche (aus 03-02 übernommene) Logik validierte die Zeile "Saldo Investitionstätigkeit" sofort beim Auftreten gegen die SUMME DER BISHER GELESENEN Maßnahmen. Auf Produktseiten steht diese Zeile immer am Ende, auf PB-Listen (PB 12 S. 235, PB 13 S. 256) aber MITTEN in der Liste, und druckt dort bereits den GESAMT-Saldo des ganzen Knotens (verifiziert: S. 235 "-1.106.000" entspricht exakt `finanzplan.csv` PB 12 Z. 31 Ansatz 2026, nicht der Teilsumme der bis dahin gelesenen drei Maßnahmen).
- **Fix:** Der gedruckte Wert wird jetzt gepuffert (`saldo_gesamt_gedruckt`) und erst nach Abschluss der gesamten Seitenschleife gegen die Summe ALLER (auch später gelesener) Investitions-Maßnahmen geprüft.
- **Files modified:** `pipeline/ostbevern/investitionen.py`
- **Verification:** `pytest tests/test_investitionen.py` (alle 13 PB-Listen plus alle 63 Produkte parsen fehlerfrei); `04_investitionen.py --jahr 2026` exit 0.
- **Committed in:** `1aca359` (Task 1 commit)

**2. [Rule 1 - Bug] Finanzierungstätigkeit-Maßnahmen aus der Saldo-Investitionstätigkeit-Summe ausgeschlossen**
- **Found during:** Task 1, Testlauf gegen Produkt 160101/PB 16 (S. 279/282) nach Fix 1
- **Issue:** Nach Fix 1 schlug die Validierung für Produkt 160101 und PB 16 fehl, weil beide eine zweite, eigenständige Finanzierungs-Tabelle (Konten 692/792) nach der Zeile "Saldo Investitionstätigkeit" drucken; deren Maßnahmen-Saldo floss fälschlich in die Summe ein (Kreditaufnahme/Tilgung ist ein eigener Tätigkeitsbereich im NKF, nicht Teil der Investitionstätigkeit).
- **Fix:** Maßnahmen, deren Kontozeilen ausschließlich `taetigkeit="finanzierung"` sind, werden von der Summenbildung für "Saldo Investitionstätigkeit" ausgenommen.
- **Files modified:** `pipeline/ostbevern/investitionen.py`
- **Verification:** `pytest tests/test_investitionen.py::test_pb16_finanzierungskonto_manipuliert_bricht_ab` und die volle Testsuite grün; `04_investitionen.py --jahr 2026` exit 0 über alle 63 Produkte und 13 PB-Listen.
- **Committed in:** `1aca359` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (beide Rule 1 — notwendige Korrekturen, damit die Pipeline auf dem echten PDF fehlerfrei läuft; kein Scope-Creep).
**Impact on plan:** Beide Korrekturen waren Voraussetzung dafür, dass `lies_massnahmen` generisch für Produkt- UND PB-Knoten funktioniert, wie vom Plan verlangt ("apply the same node checks as for products").

## Issues Encountered

- TDD-Disziplin für Tasks 1/2 (`tdd="true"`) wurde im Geiste, nicht in strikt RED-dann-GREEN-commit-getrennter Form befolgt (wie bereits in 03-01/03-02 dokumentiert): Tests gegen das echte PDF bzw. die eingecheckten CSVs wurden gemeinsam mit der Implementierung entwickelt, da die Testfixtures die Parsing-Logik selbst benötigen, um Zielzeilen/-schlüssel zu finden. `workflow.tdd_mode` ist in diesem Projekt nicht konfiguriert, daher greift keine automatisierte RED/GREEN-Commit-Sequenz-Prüfung.
- Plan 03-02 hatte EXTR-09/PRUEF-06 in `REQUIREMENTS.md` absichtlich unmarkiert gelassen, da beide Requirement-IDs zwischen 03-02 und diesem Plan geteilt sind; dieser Plan markiert sie jetzt als Complete (`gsd-tools query requirements.mark-complete`), da beide Plan-Anteile abgeschlossen sind.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Der `Luecke`-Mechanismus (`Regelergebnis.luecken`, Konsistenzbericht-Abschnitt) ist bereit für Regel 8 (Plan 03-05, Vollständigkeitsprüfung), die ihn laut Plan-Hinweis wiederverwenden soll.
- `investitionen_pb.csv` ist eine stabile, eingecheckte Kontrollquelle für künftige Phasen (nicht App-Datenquelle, Spez. 3.8).
- Blocker aus Phase 2/03-01/03-02 unverändert: Schuldenstand/Rücklagen/VE-Übersicht (S. 24/25, 309-311) bleibt ein Phase-4-Thema.

## Self-Check: PASSED

- Verified `daten/zwischen/investitionen_pb.csv` exists on disk with the expected header and sample rows (AIB00001 681011/785111, S. 146).
- `git log --oneline --all` contains `1aca359` and `a4127e0`.
- Re-ran all task-level `<acceptance_criteria>` commands and the plan-level `<verification>` block (CI replay): `uv sync --locked && ruff check . && ruff format --check . && pytest` — all pass, 227 tests.
- `uv run --directory pipeline python alle.py --jahr 2026` exits 0; Regel 6 grün (1964 Werte); `konsistenz.md` shows `## Lücken` → `Keine.`; `git status --porcelain daten/` prints nothing afterward (besides the regenerated, now-committed `befunde.md`/`konsistenz.md`/`investitionen_pb.csv`).
- `git diff --exit-code pipeline/pyproject.toml pipeline/uv.lock` exits 0 (no new dependencies).
- `pytest tests/test_pruefung.py -q -k "luecke or pb_liste"` — 7 passed (≥4 required).

---
*Phase: 03-details*
*Completed: 2026-10-02*
