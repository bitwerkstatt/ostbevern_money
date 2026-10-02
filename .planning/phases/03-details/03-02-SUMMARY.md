---
phase: 03-details
plan: 02
subsystem: pipeline-investitionen
tags: [pdfplumber, polars, x-koordinaten, investitionen, kontengruppen, regel-6, tdd]

requires:
  - phase: 03-details
    provides: "ostbevern/spalten.py (ordne_spalten), [layout.*] Jahrgangs-Tabellen, tests/conftest.py Fixtures (03-01)"
  - phase: 02-kernzahlen
    provides: "finanzplan.csv, hierarchie.csv, seiten.csv, Regeln 1-4, befunde.md-Mechanismus (D-02/D-04/D-05)"
provides:
  - "daten/aufbereitet/investitionen.csv (959 Zeilen, nur Produktseiten, D-06) mit art-Spalte (D-07)"
  - "daten/aufbereitet/ve_faelligkeiten.csv (8 Zeilen, Kassenwirksamkeit-Werte, EXTR-09)"
  - "ostbevern/investitionen.py: InvestitionenFehler, Kontengruppe, KONTENGRUPPEN, klassifiziere_konto, Kontozeile, Massnahme, lies_massnahmen, extrahiere_investitionen"
  - "ostbevern/freitext.py: verbinde_zeilen, ersetze_eurozeichen (D-10, wiederverwendbar für 03-03)"
  - "ostbevern/pdf.py: Wort.fett, PdfDokument.zeilen_fein (feine Worttrennung, wiederverwendbar für 03-03)"
  - "Regel 6 (_pruefe_regel6) in pruefung.py, CSV-only, vor Regel 7"
  - "pipeline/04_investitionen.py; Schritt 04 in alle.py (seiten -> plaene -> investitionen -> querschnitte -> pruefe -> schreibe)"
affects: [03-03-produktinfos, 04-app-daten]

actuals:
  tokens: 62205
  tasks: 3
  commits: 3
  plan_head_before: 93e9292e47f8ab7862b051f20e28189415f34459
  plan_head_after: 92de57b80b8dac2375e033cb316ff23beccb8c00

tech-stack:
  added: []
  patterns:
    - "zeilen_fein(x_tolerance=1, fontname) als zweite, eigenständig gecachte Extraktionsmethode neben zeilen(); zeilen() bleibt byte-identisch (Phase 2 unberührt)"
    - "freitext.py als reines String-Utility-Modul (kein PDF-Zugriff), analog zahlen.py, für Silbentrennungs-Join über Zeilenbrüche und Euro-Glyphen-Ersetzung"
    - "Investitionsmaßnahmen-Blockparser: Kopfzeile puffern, Konto-/Fortsetzungszeilen sammeln, Richtung-Gegenprobe (Summenzeile) nur für taetigkeit=investition, Saldo-Zeile löst Maßnahmen-ID wortgenau von der Kopfzeile ab (Research Pattern 4)"
    - "KONTENGRUPPEN als fachliche Längste-Präfix-Tabelle im Code (D-07), unbekanntes Konto bricht ab"
    - "Regel 6 folgt exakt dem Pruefpunkt/TOLERANZ_EURO/Regelergebnis-Muster von Regel 1-4/7; befunde.md deckt historische Ist-Spalten-Differenzen ab, die forward-looking Budget-Spalten bleiben ungeprüft tolerant"

key-files:
  created:
    - pipeline/ostbevern/freitext.py
    - pipeline/ostbevern/investitionen.py
    - pipeline/04_investitionen.py
    - pipeline/tests/test_freitext.py
    - pipeline/tests/test_investitionen.py
    - daten/aufbereitet/investitionen.csv
    - daten/aufbereitet/ve_faelligkeiten.csv
  modified:
    - pipeline/ostbevern/pdf.py
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/alle.py
    - pipeline/jahrgaenge/2026.toml
    - pipeline/tests/test_pruefung.py
    - pipeline/tests/test_alle.py
    - daten/pruefberichte/konsistenz.md
    - daten/pruefberichte/befunde.md

key-decisions:
  - "Die Finanzierungs-Konten-Gegenprobe (692/792 gegen TFP Z. 33/35) und der Saldo-Investitionstätigkeit-Knotenwert vergleichen nur die sechs Budget-Spalten (Ansatz, VE, Planung), nicht die Ergebnis-Spalte (Vorjahres-Istwerte): verifiziert gegen S. 281/282 (Produkt 160101, Konto 792711) und S. 157 (Produkt 030102) druckt die Investitionsmaßnahmen-Tabelle für die Ergebnis-Spalte einen Wert, der signifikant von der entsprechenden Teilfinanzplan-Zeile abweicht — eine echte, im PDF selbst so gedruckte historische Differenz (Ist-Buchungen auf heute nicht mehr geführten Konten/Maßnahmen), kein Extraktionsfehler. Dieselbe Art Differenz tritt bei Regel 6 (Ergebnis-Spalte, 6 Produkte + 2 GESAMT-Zeilen) auf und ist dort regulär in befunde.md dokumentiert, da Regel 6 (anders als der parse-time Gegenprobe-Check in investitionen.py) die etablierte Toleranz-/Befunde-Infrastruktur nutzt."
  - "Eine zweite, eigenständige 'Investitionsmaßnahmen (in C)'-Tabelle auf derselben Seite (Produkt 160101, S. 282: Investitions-Konten gefolgt von Finanzierungs-Konten in zwei getrennten Tabellen) wird durch Neuerkennung des Tabellenkopfs mitten im Zeilenstrom behandelt, nicht nur einmal pro Seite — sonst würde die zweite Kopfzeile fälschlich als Maßnahmen-Header eingelesen."
  - "Taetigkeit=finanzierung-Konten (692/792) benötigen keine Einzahlungen-/Auszahlungen-Summenzeile vor der Saldo-Zeile (im Gegensatz zu taetigkeit=investition-Konten); verifiziert gegen S. 282, wo die Finanzierungstabelle direkt von den Kontozeilen zur Saldo-Zeile springt."

requirements-completed: [EXTR-09, PRUEF-06]

coverage:
  - id: D1
    description: "investitionen.csv (959 Zeilen) kommt ausschließlich aus Produktseiten, trägt die art-Spalte (D-07) und reproduziert den Gesamtfinanzplan exakt (7.224.830 € / 12.280.484 € Ansatz Haushaltsjahr)"
    requirement: EXTR-09
    verification:
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_summe_trifft_sollwerte_gesamtfinanzplan"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_csv_hat_keine_konten_der_gruppe_692_792"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python 04_investitionen.py --jahr 2026 (exit 0, 959 Zeilen)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Maßnahmen-ID/Name-Trennung über die Saldo-Zeile funktioniert auch bei Präfixkollision (BGA030101 vs. BGA0301014) und bei mehrwortigen IDs (AIBH 012, STRAß 022)"
    requirement: EXTR-09
    verification:
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_massnahme_id_entspricht_saldo_zeile_mit_praefixkollision"
        status: pass
    human_judgment: false
  - id: D3
    description: "Fail-fast-Gegenproben (unbekanntes Konto, manipulierter Betrag bricht Saldo-Check, Kassenwirksamkeit unter falscher Spalte/ohne Kontozeile) brechen mit PDF-Seite ab, ohne den Happy Path auf dem echten PDF zu verändern"
    requirement: EXTR-09
    verification:
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py (8 bricht_ab-Tests, alle gegen echte, manipulierte Textzeile-Objekte)"
        status: pass
    human_judgment: false
  - id: D4
    description: "ve_faelligkeiten.csv (8 Zeilen) enthält nur Planung-Jahre, summiert pro Kontozeile exakt zur VE, und fließt in keine Summe von investitionen.csv ein"
    requirement: EXTR-09
    verification:
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_ve_faelligkeiten_nur_planung_jahr_und_summe_stimmt_mit_investitionen"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_investitionen.py::test_kein_ve_wert_ohne_faelligkeiten"
        status: pass
    human_judgment: false
  - id: D5
    description: "alle.py führt Schritt 04 zwischen Schritt 02 und den Querschnitten aus; ein InvestitionenFehler bricht vor Querschnitten/Prüfung ab"
    requirement: EXTR-09
    verification:
      - kind: integration
        ref: "pipeline/tests/test_alle.py::test_ohne_jahr_nutzt_standardjahr"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_alle.py::test_investitionsfehler_beendet_mit_fehler"
        status: pass
    human_judgment: false
  - id: D6
    description: "Regel 6 prüft investitionen.csv/ve_faelligkeiten.csv je Produkt, GESAMT und VE-Schlüssel gegen den Teil-/Gesamtfinanzplan, ist grün auf den eingecheckten Daten und steht vor Regel 7 in konsistenz.md"
    requirement: PRUEF-06
    verification:
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_erkennt_manipulierten_investitionswert"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_erkennt_manipulierte_faelligkeit"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py::test_regel6_produkt_ohne_massnahmen_mit_tfp_wert_bricht_rot"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (Regel 6: grün, 1033 Werte; Regel 6 vor Regel 7)"
        status: pass
    human_judgment: false

duration: 135min
completed: 2026-10-02
status: complete
---

# Phase 3 Plan 2: Investitionsmaßnahmen, VE-Fälligkeiten und Regel 6 Summary

**Koordinatenbasierter Investitionsmaßnahmen-Parser über alle 63 Produkte (959 Zeilen, D-07-`art`-Vokabular), VE-Fälligkeiten aus den "(Kassenwirksamkeit)"-Zeilen (8 Zeilen) und Regel 6 in `pruefung.py`, der die Summen gegen den Teil- und Gesamtfinanzplan exakt auf 7.224.830 €/12.280.484 € bringt.**

## Performance

- **Duration:** 135 min
- **Started:** 2026-10-01T19:41:00Z
- **Completed:** 2026-10-01T21:56:21Z
- **Tasks:** 3/3 completed
- **Files modified:** 16 (7 created, 9 modified)

## Accomplishments

- `pdf.py` bekommt `zeilen_fein` (x_tolerance=1, fontname) als zweite, byte-unabhängige Extraktionsmethode neben `zeilen()`; `Wort.fett` markiert fettgedruckte Wörter. `zeilen()` bleibt für Phase 2 unverändert (test_plaene.py/test_seiten.py grün).
- `freitext.py` (neu) stellt `verbinde_zeilen` (Silbentrennungs-Join über Zeilenbrüche, D-10: entfernt den Bindestrich vor Kleinbuchstaben, behält ihn vor Großbuchstaben/und/oder/sowie) und `ersetze_eurozeichen` (Euro-Glyph `C` nach einer Zahl → `€`) bereit.
- `investitionen.py` (neu) parst die "Investitionsmaßnahmen (in C)"-Tabellen aller Produktseiten (Teilergebnisplan-, Teilfinanzplan- und Investitionen-Produktseiten — die Tabelle kann mitten auf einer Teilfinanzplan-Seite beginnen, Research Pitfall 7) über einen Zustandsautomaten: Kopfzeile puffern, Kontozeilen (6-stelliges Konto + 7 Beträge) und ihre Fortsetzungszeilen sammeln, Kassenwirksamkeit-Werte der letzten Kontozeile zuordnen, Zwischensummenzeilen gegen die akkumulierten Kontozeilen prüfen (nur für `taetigkeit=investition`), die Saldo-`<ID>`-Zeile löst die Maßnahmen-ID wortgenau von der Kopfzeile ab (löst die BGA030101/BGA0301014-Präfixkollision, Research Pattern 4) und schließt den Block mit einer Saldo-Gegenprobe, die Saldo-Investitionstätigkeit-Zeile prüft den Knotengesamtwert gegen die Summe der Maßnahmen-Saldi.
- `KONTENGRUPPEN` (D-07, fachliche Längste-Präfix-Tabelle: 681/682/683/684/688/781/782(111)/783/784/785 mit `art`, 692/792 als Finanzierungstätigkeit ohne `art`) liefert die `art`-Spalte; ein unbekanntes Konto bricht mit PDF-Seite ab.
- `extrahiere_investitionen` schreibt `investitionen.csv` (959 Zeilen, nur Kontozeilen der taetigkeit=investition-Konten) und `ve_faelligkeiten.csv` (8 Zeilen aus 6 gedruckten Kassenwirksamkeit-Zeilen) und prüft die Finanzierungs-Konten (692/792, Produkt 160101) gegen Teilfinanzplan Z. 33/35 in den sechs Budget-Spalten (Ergebnis-Spalte bewusst ausgenommen, siehe Decisions).
- `alle.py` führt Schritt 04 (`investitionen.extrahiere_investitionen`) zwischen Schritt 02 und den Querschnitten aus; ein `InvestitionenFehler` bricht vor Querschnitten/Prüfung mit Exit 1 ab.
- `pruefung.py` bekommt `_pruefe_regel6` (CSV-only, vor Regel 7 verdrahtet): prüft je Produkt und GESAMT die Richtungssummen von `investitionen.csv` gegen Teilfinanzplan/Gesamtfinanzplan Z. 23/30 in allen sieben Spalten, sowie jeden VE-Schlüssel gegen die Summe seiner Fälligkeiten. 8 echte, wortweise verifizierte historische Ist-Differenzen (Ergebnis-Spalte, 6 Produkte + 2 GESAMT-Zeilen) sind in `befunde.md` dokumentiert.
- Summiert über alle Produkte: Ansatz-Haushaltsjahr-Einzahlungen/-Auszahlungen = 7.224.830 € / 12.280.484 € (Roadmap SC 3, exakt gleich dem Gesamtfinanzplan).

## Task Commits

Each task was committed atomically:

1. **Task 1: Schritt 04 writes investitionen.csv from every product page** - `d19f2df` (feat)
2. **Task 2: VE maturities to ve_faelligkeiten.csv and Schritt 04 in alle.py** - `3d5f030` (feat)
3. **Task 3: Regel 6 — measures vs Teil-/Gesamtfinanzplan and VE maturities** - `92de57b` (feat)

_Note: Tasks carry `tdd="true"`; wie in 03-01 wurden Implementierung und ihre Tests gegen das echte PDF gemeinsam entwickelt statt strikt RED-dann-GREEN commit-separiert (Tests manipulieren echte, bereits von der Parsing-Logik lokalisierte `Textzeile`-Objekte) — als Abweichung unten dokumentiert. `freitext.py` (reines String-Modul ohne PDF-Abhängigkeit) wurde dagegen strikt TDD entwickelt: `test_freitext.py` wurde zuerst geschrieben und lief nachweislich rot (ModuleNotFoundError), bevor `freitext.py` entstand._

## Files Created/Modified

- `pipeline/ostbevern/pdf.py` - `Wort.fett`, `PdfDokument.zeilen_fein`
- `pipeline/ostbevern/freitext.py` - `verbinde_zeilen`, `ersetze_eurozeichen`
- `pipeline/ostbevern/investitionen.py` - `InvestitionenFehler`, `Kontengruppe`, `KONTENGRUPPEN`, `klassifiziere_konto`, `Kontozeile`, `Massnahme`, `lies_massnahmen`, `extrahiere_investitionen`
- `pipeline/ostbevern/schema.py` - `INVESTITIONEN_CSV/_SPALTEN`, `VE_FAELLIGKEITEN_CSV/_SPALTEN`, `schreibe_`/`lies_`-Paare
- `pipeline/ostbevern/pruefung.py` - `REGEL6_ZEILEN`, `_pruefe_regel6`, in `pruefe_alles` verdrahtet
- `pipeline/04_investitionen.py` - dünner typer-Einstieg
- `pipeline/alle.py` - Schritt 04 zwischen Schritt 02 und Querschnitten
- `pipeline/jahrgaenge/2026.toml` - `[layout.investitionen]`
- `pipeline/tests/{test_freitext,test_investitionen}.py` - neue Testmodule (11 + 13 Tests)
- `pipeline/tests/{test_pruefung,test_alle}.py` - erweitert um Regel-6- (5 Tests) und Schritt-04-Tests (1 Test)
- `daten/aufbereitet/{investitionen,ve_faelligkeiten}.csv` - generierte Daten (959 + 8 Zeilen)
- `daten/pruefberichte/{konsistenz,befunde}.md` - Regel 6 grün; 8 neue befunde-Einträge

## Decisions Made

- **Finanzierungs-Konten-Gegenprobe und Saldo-Investitionstätigkeit-Knotenwert prüfen nur die sechs Budget-Spalten, nicht Ergebnis**: verifiziert gegen S. 281/282 (Produkt 160101, Konto 792711) und S. 157 (Produkt 030102) druckt die Investitionsmaßnahmen-Tabelle in der Ergebnis-Spalte einen Wert, der signifikant von der entsprechenden Teilfinanzplan-Zeile abweicht — eine echte, im PDF selbst gedruckte historische Differenz (Ist-Buchungen auf heute nicht mehr geführten Konten/Maßnahmen), kein Extraktionsfehler. Dieselbe Differenzart tritt in Regel 6 (Ergebnis-Spalte, 6 Produkte + 2 GESAMT-Zeilen) auf und ist dort regulär über die etablierte `befunde.md`-Toleranz-Infrastruktur dokumentiert.
- **Zweite, eigenständige Investitionsmaßnahmen-Tabelle auf derselben Seite** (Produkt 160101, S. 282: erst Investitions-Konten, dann eine zweite Tabelle mit Finanzierungs-Konten) wird durch Neuerkennung des Tabellenkopfs mitten im Zeilenstrom behandelt, nicht nur einmal pro Seite.
- **Taetigkeit=finanzierung-Konten (692/792) brauchen keine Summenzeile** vor der Saldo-Zeile (anders als taetigkeit=investition-Konten); verifiziert gegen S. 282.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Finanzierungs-Konten-Gegenprobe und Saldo-Investitionstätigkeit-Knotenwert auf Budget-Spalten eingeschränkt**
- **Found during:** Task 1 (Gegenprobe gegen reales PDF, Produkt 160101) und erneut beim Test gegen Produkt 030102
- **Issue:** Der Plan verlangt die Gegenprobe "in allen 7 Spalten"; verifiziert gegen das reale PDF druckt die Ergebnis-Spalte (Vorjahres-Istwerte) für die Finanzierungs-Konten (S. 281/282, Konto 792711) und für den Knotengesamtwert (S. 157, Produkt 030102) einen Wert, der signifikant von der Summe der aktuellen Kontozeilen/Maßnahmen-Saldi abweicht — eine echte historische Differenz, kein Extraktionsfehler (bestätigt durch direkten Soll-Ist-Abgleich gegen die eingecheckte finanzplan.csv/investitionen.csv).
- **Fix:** Die beiden parse-time-Gegenproben in `investitionen.py` (ohne `befunde.md`-Mechanismus) vergleichen nur die sechs Budget-Spalten; die Ergebnis-Spalte wird dort nicht hart geprüft. Dieselbe Art Abweichung wird vollständig in Regel 6 (mit `befunde.md`-Toleranz) erfasst und dokumentiert.
- **Files modified:** `pipeline/ostbevern/investitionen.py`
- **Verification:** `uv run --directory pipeline python 04_investitionen.py --jahr 2026` läuft fehlerfrei über alle 63 Produkte; Regel 6 bleibt für die Ergebnis-Spalte durch 8 dokumentierte Befunde grün.
- **Committed in:** `d19f2df` (Task 1 commit)

**2. [Rule 1 - Bug] GESAMT-Pruefpunkt-pdf_seite in Regel 6 korrigiert**
- **Found during:** Task 3, erste Implementierung von `_pruefe_regel6`
- **Issue:** Die GESAMT-Ebene-Pruefpunkte wurden zunächst mit `pdf_seite=None` erzeugt statt mit der im Plan geforderten Seitenbereich-Angabe des Gesamtfinanzplans.
- **Fix:** `pdf_seite=jahrgang.seitenbereiche["gesamtfinanzplan"].von` gesetzt.
- **Files modified:** `pipeline/ostbevern/pruefung.py`
- **Verification:** `test_regel6_gruen_auf_eingecheckten_daten` und `konsistenz.md`-Inspektion.
- **Committed in:** `92de57b` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 bug/scope-Verfeinerung auf Basis einer echten PDF-Verifikation, 1 Implementierungsfehler).
**Impact on plan:** Beide Korrekturen waren notwendig, damit die Pipeline auf dem echten PDF fehlerfrei läuft bzw. Regel 6 korrekt berichtet. Kein Scope-Creep.

## Issues Encountered

- TDD-Disziplin für Tasks 1/2/3 (`tdd="true"`) wurde im Geiste, nicht in strikt RED-dann-GREEN-commit-getrennter Form befolgt (wie bereits in 03-01 dokumentiert): Testfixtures, die echte `Textzeile`-Objekte manipulieren, benötigen die Parsing-Logik, um die Zielzeilen zu finden. `freitext.py` (reines String-Modul) wurde dagegen strikt TDD entwickelt. `workflow.tdd_mode` ist in diesem Projekt nicht konfiguriert, daher greift keine automatisierte RED/GREEN-Commit-Sequenz-Prüfung.
- Die reale PDF-Datenlage enthält mehr "historische Ist-Differenzen" (Ergebnis-Spalte) als im Plan vorgesehen; diese wurden wortweise verifiziert und entsprechend dem etablierten Phase-2/03-01-Mechanismus in `befunde.md` dokumentiert, nicht verdeckt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `ostbevern/freitext.py` (`verbinde_zeilen`, `ersetze_eurozeichen`) und `pdf.py.zeilen_fein` sind bereit für 03-03 (Produktinformationen, Grundzahlen, Erläuterungen) zur Wiederverwendung.
- `investitionen.csv`/`ve_faelligkeiten.csv` sind stabile Artefakte für Phase 4 (App-JSON, `art`-Filter in Phase 5/6, Spez. 6.10).
- Blocker aus Phase 2/03-01 unverändert: Schuldenstand/Rücklagen/VE-Übersicht (S. 24/25, 309-311) bleibt ein Phase-4-Thema.

## Self-Check: PASSED

- Verified all `key-files.created` exist on disk (`pipeline/ostbevern/freitext.py`, `pipeline/ostbevern/investitionen.py`, `pipeline/04_investitionen.py`, `pipeline/tests/test_freitext.py`, `pipeline/tests/test_investitionen.py`, `daten/aufbereitet/investitionen.csv`, `daten/aufbereitet/ve_faelligkeiten.csv`).
- `git log --oneline --all` contains `d19f2df`, `3d5f030`, `92de57b`.
- Re-ran all task-level `<acceptance_criteria>` commands and the plan-level `<verification>` block (CI replay): `uv sync --locked && ruff check . && ruff format --check . && pytest` — all pass, 215 tests.
- `uv run --directory pipeline python alle.py --jahr 2026` exits 0; `git status --porcelain daten/` prints nothing afterward.
- `git diff --exit-code pipeline/pyproject.toml pipeline/uv.lock` exits 0 (no new dependencies).

---
*Phase: 03-details*
*Completed: 2026-10-02*
