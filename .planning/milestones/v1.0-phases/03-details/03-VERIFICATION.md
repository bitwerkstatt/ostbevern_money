---
phase: 03-details
verified: 2026-10-09T06:40:00Z
status: passed
score: 12/12 must-haves verified
covered_files: [".planning/milestones/v1.0-phases/03-details/03-01-PLAN.md", ".planning/milestones/v1.0-phases/03-details/03-01-SUMMARY.md", ".planning/milestones/v1.0-phases/03-details/03-02-PLAN.md", ".planning/milestones/v1.0-phases/03-details/03-02-SUMMARY.md", ".planning/milestones/v1.0-phases/03-details/03-03-PLAN.md", ".planning/milestones/v1.0-phases/03-details/03-03-SUMMARY.md", ".planning/milestones/v1.0-phases/03-details/03-04-PLAN.md", ".planning/milestones/v1.0-phases/03-details/03-04-SUMMARY.md", ".planning/milestones/v1.0-phases/03-details/03-05-PLAN.md", ".planning/milestones/v1.0-phases/03-details/03-05-SUMMARY.md", "daten/aufbereitet/erlaeuterungen.csv", "daten/aufbereitet/grundzahlen.csv", "daten/aufbereitet/investitionen.csv", "daten/aufbereitet/produkte.json", "daten/aufbereitet/ve_faelligkeiten.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/pruefberichte/quellenbelege.md", "daten/zwischen/investitionen_pb.csv", "daten/zwischen/querschnitte.csv", "pipeline/03_produktinfos.py", "pipeline/04_investitionen.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/freitext.py", "pipeline/ostbevern/investitionen.py", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/produkte.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/querschnitte.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/spalten.py", "pipeline/ostbevern/zahlen.py", "pipeline/tests/conftest.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_freitext.py", "pipeline/tests/test_investitionen.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_produkte.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_querschnitte.py", "pipeline/tests/test_schema.py", "pipeline/tests/test_spalten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v3:sha256:29b3a0a8aed0d93df6ba06f362d1ca83cd8e4de4da3d7edb0531d2081470a5df"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "11/11 must-haves verified"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
deferred: []
advisory: []
---

# Phase 3: Details Verification Report

**Phase Goal:** Alle 63 Produkte sind inhaltlich vollständig beschrieben (Produktinformationen, Bindungsgrad, Grundzahlen, Erläuterungen), und die Investitionsmaßnahmen stimmen mit den Finanzplänen überein.
**Verified:** 2026-10-09T06:40:00Z
**Status:** passed
**Re-verification:** Yes — gegen den Endstand nach Phase 8 und der D-20-Korrektur (Code geprüft auf HEAD `b07d34f`; Basislauf-Code `1d0df35`)

## Warum diese Re-Verifikation (Phase 9, AUD-02)

Der vorige Bericht (verifiziert 2026-10-02T12:30:00Z auf Commit `87f0580`, `status: passed`, `score: 11/11 must-haves verified`, Fingerprint v2) beschreibt den Stand vor den Phasen 4 bis 8. `verification.status` lieferte für dieses Verzeichnis `stale` (siehe `09-BASISLAUF.md`, Abschnitt „Verifikationsstatus vor der Re-Verifikation“). Diese Re-Verifikation wendet das Verfahren des gsd-verifier (Re-Verifikationsmodus, Schritte 3 bis 9) in Plan 09-06 an, weil Ausführende keine Unteragenten starten können (D-13). Jede Wahrheit des alten Berichts und jedes Erfolgskriterium aus `.planning/milestones/v1.0-ROADMAP.md` (Phase 3) wurde gegen den heutigen Code und die heutigen Daten neu geprüft, nicht aus dem alten Bericht übernommen.

Änderungen an Phase-3-Dateien seit `87f0580` (`git diff --stat 87f0580 HEAD -- <covered_files>`):

- **Daten, die Phase 3 erzeugt:** `produkte.json`, `grundzahlen.csv`, `erlaeuterungen.csv`, `investitionen.csv`, `ve_faelligkeiten.csv`, `investitionen_pb.csv`, `querschnitte.csv` sind **byte-identisch** zu `87f0580` (leere Diff-Ausgabe). `befunde.md` bekam nur zusätzliche Regel-5-Zeilen aus Phase 4 und 5, `konsistenz.md` zusätzlich die Regeln 5, 9 und 10; die Zeilen für Regel 1, 2, 3, 6 und 7 sind unverändert. Neu ist `daten/pruefberichte/quellenbelege.md` (Phase 7), das ich auf Personennamen geprüft habe (Wahrheit 9).
- **Pipeline-Code mit Wirkung auf Phase 3:**
  - Phase 7: `pdf.py` (`WortRahmen`, `RahmenZeile`, `zeilen_mit_rahmen`, `seitenmass`) und `produkte.py` (`personenfeld_rechtecke`) sind rein additiv; `extrahiere_produkte`, `lies_grundzahlen` und `lies_personennamen` sind unverändert.
  - Phase 4 bis 7: `schema.py` ist rein additiv (neue Pfade und Spaltenschemas); `schreibe_csv` mit dem Rundlauf-Check aus CR-01 ist unverändert.
  - Phase 7 und 8: `konfiguration.py` bekam die Allowlist `LEERE_LISTE_ERLAUBT` (Phase 7, WR-04) und die Ablehnung negativer `anzahlen.*` (Phase 8, Commit `4c105ff`, IN-04). `alle.py` rechnet `pdf_relativ` nur noch einmal (Phase 8, Commit `c18a032`, IN-02) und führt zusätzlich die Schritte 05, 07 und 08 aus.
  - `pruefung.py`: Regel 1, 2, 3, 6 (mit PB-Gegenprobe), 7 und 8 sind Zeile für Zeile identisch zu `87f0580` (Vergleich der Funktionskörper mit `diff`, leere Ausgabe). Neu sind nur die Regeln 4 (B.4, B.5, Längenprüfung B.1), 5, 9, 10, die Toleranz je Regel (`TOLERANZ_JE_REGEL = {9: 0, 10: 0}`, Regel 6 bis 8 behalten 1 €) und die maskierte Pipe in `lies_befunde`.
- Weitere Dateien der alten Liste (`spalten.py`, `querschnitte.py`, `investitionen.py`, `zahlen.py`, `freitext.py`, `03_produktinfos.py`, `04_investitionen.py`, `06_pruefen.py`) sind seit `87f0580` unverändert.

Phase-8-Commits, die Phase-3-Code berührten: `c18a032` (`alle.py`, `pdf_relativ` einmal berechnen) und `4c105ff` (`konfiguration.py`, negative Anzahlen ablehnen). Die Befehle: `git show --stat c18a032 4c105ff`; beide ändern kein Datenartefakt.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ROADMAP SC 1: `produkte.json` enthält alle 63 Produkte mit Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Klassifizierung, Zielgruppe, Zielen, PDF-Seiten und Bindungsgrad (normalisiert und original); Regel 8 grün | ✓ VERIFIED | Eigene Prüfung heute auf `daten/aufbereitet/produkte.json`: 63 Datensätze, 63 verschiedene Codes, in keinem der elf Pflichtfelder ein leerer Wert, alle Datensätze haben dieselben 16 Schlüssel. Bindungsgrad: 31 pflichtig, 15 teils, 17 freiwillig. Stichprobe `030101`: `bindungsgrad="teils"`, `bindungsgrad_original="teils pflichtig teils freiwillig"`, `pdf_seiten=[151,152,153,154]`. `konsistenz.md`: `Regel 8 – Vollständigkeit der Produkte \| grün \| 820 \| 0 \| 0 \| 0`; `09-BASISLAUF.md` Abschnitt 3: „Regel 8: grün (820 Werte)“. Test `pipeline/tests/test_pruefung.py::test_regel8_gruen_auf_eingecheckten_daten` (Zeile 1883) lief heute grün. |
| 2 | ROADMAP SC 2: `grundzahlen.csv` mit Einheit, Jahr, Stichtagshinweis inklusive Steuer-Istwerte 2022–2025 aus 160101 (Gewerbesteuer 2023 = 4.771.497 €); Erläuterungsposten je Produkt mit Betrag, Text, Zeilenbezug | ✓ VERIFIED | `grep` heute: `160101,1,,Gewerbesteuer (Im Teilplan Zeile 01),EUR,2023,4771497.0,0,,280` plus die Zeilen für 2022, 2024 und 2025 (2025 mit Hinweis „Ist-Wert 2025: Stand Ende 2025.“). `grundzahlen.csv`: 827 Werte, 48 Produkte, kein Wert null. `erlaeuterungen.csv`: 229 Posten für 50 Produkte, `test_erlaeuterungen_csv_zu_zeilen_format` (`test_produkte.py:693`) grün. `09-BASISLAUF.md`: „Schritt 03: 827 Einträge … grundzahlen.csv“, „229 Einträge … erlaeuterungen.csv“. |
| 3 | ROADMAP SC 3: `investitionen.csv` nur aus Produktseiten; Summe je Produkt = TFP Z. 23/30; Summe aller Maßnahmen 2026 = 7.224.830 € / 12.280.484 € (Regel 6); „(Kassenwirksamkeit)“ nur in `ve_faelligkeiten.csv` | ✓ VERIFIED | Heute mit polars aus `investitionen.csv` neu gerechnet (Wertart `ansatz`, Jahr 2026): Einzahlung 7.224.830, Auszahlung 12.280.484. Konten 692/792: 0 Zeilen in `investitionen.csv` und in `investitionen_pb.csv`; 0 Zeilen mit „Kassenwirksamkeit“ in `investitionen.csv`; `ve_faelligkeiten.csv` hat 8 Zeilen (Spalten produkt, massnahme_id, konto, jahr, betrag, pdf_seite). Produktseiten 87 bis 282. `konsistenz.md`: `Regel 6 … \| grün \| 1964 \| 0 \| 0 \| 8`. Tests grün: `test_regel6_gruen_auf_eingecheckten_daten` (`test_pruefung.py:1413`), `test_regel6_summe_trifft_sollwerte_b2` (:1424), `test_regel6_erkennt_manipulierten_investitionswert` (:1441), `test_regel6_erkennt_manipulierte_faelligkeit` (:1487), `test_regel6_pb_liste_erkennt_manipulierten_wert`. |
| 4 | ROADMAP SC 4: Querschnitte ab S. 291 stimmen mit den eigenen PG-Aggregaten überein (Regel 7); `konsistenz.md` meldet Regeln 1–4 und 6–8 grün | ✓ VERIFIED | `konsistenz.md` heute: `Gesamtstatus: grün`; Regel 1 (6593), 2 (7994), 3 (114), 4 (259), 6 (1964), 7 (1152), 8 (820) jeweils `grün` mit 0 Abweichungen und 0 Lücken (zusätzlich Regel 5, 9, 10 grün). `querschnitte.csv`: 1152 Zeilen auf den PDF-Seiten 291 bis 300. `09-BASISLAUF.md`: „Regel 7: grün (1152 Werte)“, „Veraltete Befunde: 0“. Tests grün: `test_regel7_gruen_auf_eingecheckten_daten` (:1173), `test_regel7_erkennt_manipulierten_querschnitt` (:1184), `test_regel7_toleriert_einen_euro` (:1212), 13 Tests in `test_querschnitte.py`. |
| 5 | WR-01 (Plan 03-01): `ordne_spalten` berechnet die Toleranz pro Ankerpaar, ein doppelter Anker setzt nicht die ganze Zuordnung außer Kraft | ✓ VERIFIED | `pipeline/ostbevern/spalten.py:20-48` (Toleranz je Wort aus den Nachbarankern, Zeile 44) ist seit `87f0580` unverändert (`git diff 87f0580 HEAD -- pipeline/ostbevern/spalten.py` leer). Aufrufer `produkte.py:433,469`, `querschnitte.py:242`, `investitionen.py:261`. `pytest tests/test_spalten.py` heute: 6 passed, darunter `test_ordne_spalten_doppelter_anker_bricht_nicht_die_ganze_zuordnung` (`test_spalten.py:55`). Die Daten der drei Aufrufer sind byte-identisch (siehe oben). |
| 6 | CR-01: `schreibe_csv` ergänzt `strict=True` um einen Rundlauf-Check gegen Float→Int-Verlust | ✓ VERIFIED | `pipeline/ostbevern/schema.py:134-160` (`cast(spalten, strict=True)` Zeile 149, `SchemaFehler` Zeile 155); der Kommentar Zeile 144-148 benennt den Fall. Die Funktion ist seit `87f0580` unverändert, die Phasen 4 bis 7 haben nur Schemas darum herum ergänzt (`git diff` zeigt ausschließlich additive Hunks). `pytest tests/test_schema.py` heute: 2 passed (`test_schreibe_csv_lehnt_fraktionalen_float_bei_int_narrowing_ab`, `test_schreibe_csv_schreibt_ganzzahligen_float_bei_int_narrowing`, `test_schema.py:21,29`). |
| 7 | WR-02, IN-01, IN-02: Test-Fixture mit echtem 3-Tupel, Etikett „Schritt 06“ nicht doppelt, CLI-Hilfe nennt alle Artefakte | ✓ VERIFIED | `pipeline/alle.py:128` meldet „Querschnitte: N Werte geschrieben.“, „Schritt 06“ steht nur in `alle.py:148-149` für die Prüfung. `03_produktinfos.py` und `04_investitionen.py` sind unverändert. Die Fixture `_produkte_ergebnisse()` in `pipeline/tests/test_alle.py:72-86` liefert das echte 3-Tupel (Produkte, Grundzahlen, Erläuterungen). Rein kosmetisch, kein Einfluss auf Daten. |
| 8 | Nyquist-Ergänzungen G1/G2: Finanzierungskonten-Gegenprobe gegen Teilfinanzplan Z. 33/35 auf P- und PB-Ebene; Schritt 03 ist byte-deterministisch | ✓ VERIFIED | Heute einzeln gelaufen, 6 passed in 25,8 s: `test_investitionen.py::test_finanzierungskonten_weichen_vom_teilfinanzplan_ab_bricht_ab` (:527), `…_pb_weichen_vom_teilfinanzplan_ab_bricht_ab` (:564), `test_pb_liste_summe_trifft_sollwerte_und_keine_finanzierungskonten` (:445), `test_produkte.py::test_produkte_json_erlaeuterungen_csv_grundzahlen_csv_byte_identisch` (:712), `test_keine_personennamen` (:198), `test_erlaeuterungen_csv_zu_zeilen_format` (:693). Zusätzlich belegt `09-BASISLAUF.md` Abschnitt 4 (`git diff --stat --exit-code -- daten app/src/data` leer) die Byte-Identität nach `alle.py`. |
| 9 | Plan 03-04 (D-09): Kein Personenname aus „Verantwortliche/r“ oder „Sachbearbeiter/innen“ erreicht eine Datei unter `daten/` | ✓ VERIFIED | `produkte.json` hat in jedem Datensatz genau die 16 Schlüssel von `PRODUKT_SCHLUESSEL`, keinen Personenschlüssel. `test_keine_personennamen` (`test_produkte.py:198`) liest die Namen aus dem PDF und durchsucht rekursiv `DATEN_WURZEL` (also auch das neue `quellenbelege.md`) mit und ohne Leerzeichen: grün. Ein Grep ohne Namen findet in `daten/` nur die Etiketten „Verantwortlich“ und „Sachbearbeit“ in der Datenschutz-Prüfliste von `daten/pruefberichte/quellenbelege.md` (Phase 7; Seite, Stichwort, Zeilenindex, „geschwärzt: ja/nein“, ausdrücklich ohne Textauszug) – das sind Spaltenüberschriften, keine Namen, und der Test bestätigt es. `personenfeld_rechtecke` (`produkte.py`, Phase 7) liefert nur Zahlen, nie Text. |
| 10 | Plan 03-05 (D-12, D-13): Grundzahlen mit Einheiten, Gruppen und Hinweis je Jahr; ein `–` erzeugt keine Zeile | ✓ VERIFIED | Heute aus `grundzahlen.csv`: 48 Produkte, die Fortsetzungsseiten 77, 85, 128 und 265 kommen vor, Einheiten normalisiert (`EUR`, `EUR/km`, `EUR/lfd. m.`, `EUR/m³`, `EUR/qm`, `Kehrmeter`, `Anz.`, `%`, `Std.` …; kein `C`-Rest). Die Positionen laufen in gedruckter Reihenfolge bis insgesamt 222 (`Summe max(position)`), davon haben zwei Zeilen (Produkte 020701 und 110101) nur `–` und damit keine CSV-Zeile: 220 verschiedene Zeilen mit Wert, 827 Werte. Das deckt die Planzahl „222 gedruckte Zeilen“ und die D-13-Regel ab. `grundzahlen.csv` ist byte-identisch zu `87f0580`. |
| 11 | Plan 03-01, 03-02, 03-03: Kontrollquellen und Fail-fast: Regel 7 liest nur `querschnitte.csv`, Regel 6 hat PB-Gegenprobe und Lücken, Finanzierungskonten bleiben draußen | ✓ VERIFIED | `pipeline/ostbevern/pruefung.py` enthält keinen Import von `pdf` und keine `PdfDokument`-Nutzung (`grep` leer); `lies_querschnitte_csv(daten_wurzel / QUERSCHNITTE_CSV)` Zeile 2629, `REGEL7_KENNZAHLEN` Zeile 147, `_pruefe_regel6_pb_gegenprobe` Zeile 2124, `_pruefe_regel6` Zeile 2237, `_pruefe_regel7` Zeile 2401, `_pruefe_regel8` Zeile 2492 – die Körper von Regel 6 (samt PB-Gegenprobe), 7 und 8 sind identisch zu `87f0580`. `06_pruefen.py:42,54` und `alle.py:124,141` rufen erst `extrahiere_querschnitte`, dann `pruefe_alles`. `investitionen_pb.csv` hat 959 Zeilen wie `investitionen.csv`, ohne Konten 692/792. Maßnahmen-IDs `BGA030101`, `BGA0301014`, `ÖKO001`, `STRAß004` stehen als gedruckt in `investitionen.csv`, kein Name endet auf einen Trennstrich. Produkt 010901 liest die Seiten 98 bis 101 als einen Datensatz. |
| 12 | Phasen-Gate: `alle.py --jahr 2026` läuft durch, reproduziert `daten/` byte-identisch, die volle Suite und die Prüfregeln sind grün | ✓ VERIFIED | Belegt durch `09-BASISLAUF.md` (Code `head: 1d0df35da1842daec515b40dd62f8d918e240105`): 681 pytest-Tests grün ohne Skip, `ruff check` und `ruff format --check` grün, `alle.py` Exit 0 mit „Schritt 01“ bis „Schritt 08“, Regeln 1 bis 10 grün, „Veraltete Befunde: 0“, `git diff --stat --exit-code -- daten app/src/data` leer. Dieser Plan hat `alle.py`, die volle Suite und Playwright nicht gestartet (D-23). Die Kette ist gegenüber Phase 3 erweitert (zusätzlich Schritt 05, 07, 08), ihre Phase-3-Glieder 01, 02, 03, 04, Querschnitte und 06 laufen weiter in dieser Reihenfolge (`alle.py` Zeilen 70 bis 150). |

**Score:** 12/12 Wahrheiten verifiziert, 0 present-but-behavior-unverified.

Alle Wahrheiten mit Laufzeitverhalten (Rot-Schalten bei 2 € Abweichung, Abbruch bei abweichenden Finanzierungskonten, Byte-Identität, Datenschutz) haben einen heute gelaufenen, benannten Test oder den Basislauf als Beleg; keine Wahrheit stützt sich nur auf Vorhandensein von Symbolen.

### Live-Evidenz

Die Läufe stammen aus `.planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md` (09-BASISLAUF.md), `head: 1d0df35da1842daec515b40dd62f8d918e240105`, erstellt 2026-10-09T06:24:00Z: `pytest_passed: 681`, `pytest_skipped: 0`, `alle_py: byte-identisch`, `vitest_tests: 2162`, `e2e_ci_passed: 89`. Dieser Plan hat keinen Code geändert und weder `alle.py` noch die volle pytest-Suite noch Playwright gestartet.

Nachweis, dass seit dem Basislauf kein Codepfad geändert wurde: `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline`, `-- app`, `-- daten` und `-- scripts .github` enden mit Exit 0.

Eigene, lesende Prüfungen dieses Plans (Linux, Worktree auf HEAD `b07d34f`):

| Befehl | Ergebnis |
|--------|----------|
| `uv run --directory pipeline pytest -p no:cacheprovider -q tests/test_schema.py tests/test_spalten.py` | 8 passed |
| `… pytest … tests/test_investitionen.py::test_finanzierungskonten_weichen_vom_teilfinanzplan_ab_bricht_ab` und die fünf weiteren Knoten aus Wahrheit 8 | 6 passed in 25,8 s |
| `… pytest … tests/test_pruefung.py -k "regel6 or regel7 or regel8 or regel_6 or regel_7 or regel_8"` | 24 passed, 65 deselected in 71,9 s |
| `… pytest … tests/test_querschnitte.py` | 13 passed |
| polars-Skripte auf `daten/aufbereitet` und `daten/zwischen` (Wahrheiten 1, 2, 3, 10, 11) | Werte wie in der Tabelle |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| EXTR-06 | 03-04 | Produktinformationen aller 63 Produkte in `produkte.json` | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheit 1 |
| EXTR-07 | 03-05 | Grundzahlen je Produkt, Steuer-Istwerte 160101 | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheiten 2 und 10 |
| EXTR-08 | 03-04 | Erläuterungsposten je Produkt | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheit 2 |
| EXTR-09 | 03-02, 03-03 | Investitionsmaßnahmen nur aus Produktseiten; Kassenwirksamkeit separat | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheit 3 |
| PRUEF-06 | 03-02, 03-03 | Investitionssummen je Produkt und gesamt | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheit 3 |
| PRUEF-07 | 03-01 | Querschnitte stimmen mit PG-Aggregaten überein | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheit 4 |
| PRUEF-08 | 03-05 | Vollständigkeit der 63 Produkte | ✓ SATISFIED (vorläufig, Task 2 ergänzt) | Wahrheit 1 |

### Anti-Patterns Found

Keine. Suche nach `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` über alle Phase-3-Implementierungsdateien (`pdf.py`, `produkte.py`, `pruefung.py`, `schema.py`, `konfiguration.py`, `spalten.py`, `querschnitte.py`, `investitionen.py`, `zahlen.py`, `freitext.py`, `alle.py`, `03_produktinfos.py`, `04_investitionen.py`, `06_pruefen.py`) ohne Treffer. `03-REVIEW-DISPOSITION.md`: `open: 0`, `total: 6`.

### Human Verification Required

Keine. Pipeline-Phase ohne Oberfläche; alle Prüfungen sind maschinell am heutigen Code und an den heutigen Daten gelaufen.

### Gaps Summary

Keine Lücken, keine Regressionen. Die Daten, die Phase 3 erzeugt, sind seit der letzten Verifikation byte-identisch; die Regeln 6 bis 8 und ihre Hilfsfunktionen sind im Quelltext unverändert; die Phasen 4 bis 8 haben `pdf.py`, `produkte.py`, `schema.py` und `konfiguration.py` nur additiv beziehungsweise mit strengeren Eingabeprüfungen ergänzt. Die Wahrheiten 1 bis 4 stammen aus der ROADMAP, die Wahrheiten 5 bis 12 aus den Plänen 03-01 bis 03-05 und den Review-Korrekturen.

---

_Verified: 2026-10-09T06:40:00Z_
_Verifier: Claude (gsd-verifier-Verfahren, ausgeführt in Plan 09-06)_
