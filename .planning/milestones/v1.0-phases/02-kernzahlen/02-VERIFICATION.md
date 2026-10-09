---
phase: 02-kernzahlen
verified: 2026-10-09T06:33:00Z
status: passed
score: 5/5 must-haves verified (roadmap Success Criteria); 10/10 requirement IDs satisfied
covered_files: [".github/workflows/ci.yml", ".planning/milestones/v1.0-phases/02-kernzahlen/02-01-PLAN.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-01-SUMMARY.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-02-PLAN.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-02-SUMMARY.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-03-PLAN.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-03-SUMMARY.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-04-PLAN.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-04-SUMMARY.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-05-PLAN.md", ".planning/milestones/v1.0-phases/02-kernzahlen/02-05-SUMMARY.md", "daten/aufbereitet/ergebnisplan.csv", "daten/aufbereitet/finanzplan.csv", "daten/aufbereitet/hierarchie.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/seiten.csv", "pipeline/01_seiten_klassifizieren.py", "pipeline/02_plaene_extrahieren.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/plaene.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/seiten.py", "pipeline/ostbevern/zahlen.py", "pipeline/ostbevern/zeilen.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_hierarchie.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_plaene.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_schema.py", "pipeline/tests/test_seiten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v3:sha256:2c6913041514ce847c1c2bddfc496bae09c7d375131fe03653540d7d23950aad"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "5/5 must-haves verified (roadmap Success Criteria); 10/10 requirement IDs satisfied"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
deferred: []
advisory: []
behavior_unverified_items: []
---

# Phase 2: Kernzahlen Verification Report

**Phase Goal:** Alle Ergebnis- und Finanzpläne (Gesamt, PB, Produkt) liegen korrekt im Langformat vor. Die Pipeline weist das durch automatische Prüfungen und Anhang-B-Sollwerte nach.
**Verified:** 2026-10-09T06:33:00Z
**Status:** passed
**Re-verification:** Yes — vollständiger Goal-Backward-Lauf gegen den Endstand nach Phase 8 (Plan 09-05, D-13). Vorheriger Bericht: `status: passed`, verifiziert 2026-10-02T12:10:21Z, `score: 5/5 must-haves verified (roadmap Success Criteria); 10/10 requirement IDs satisfied`.

## Warum diese Re-Verifikation (Phase 9, AUD-02)

Der vorherige Bericht stand auf `stale` (`gsd-tools query verification.status` meldete `stale`, vor dieser Erneuerung geprüft). Seit seinem Stand (2026-10-02, HEAD `189c481`) haben die Phasen 3 bis 8 Dateien verändert, die dieser Bericht abdeckt. Statt dem alten Bericht oder einem SUMMARY zu trauen, wird jede Wahrheit gegen den heutigen Code und den gepinnten Basislauf (`09-BASISLAUF.md`) neu geprüft.

### Änderungen an Phase-2-Dateien seit dem letzten Bericht

`git log --since=2026-10-02T12:10:21Z --format='%h %ad %s' -- <Datei>` je Implementierungsdatei, danach `git diff 189c481 HEAD` auf die Löschungen:

| Datei | Änderung seit 2026-10-02 | Bewertung |
|-------|--------------------------|-----------|
| `pipeline/ostbevern/zahlen.py`, `zeilen.py`, `seiten.py`, `plaene.py` | keine Commits | unverändert; Wahrheiten 1 bis 3 stützen sich auf unveränderten Parser- und Klassifikationscode |
| `pipeline/ostbevern/schema.py` | nur Ergänzungen (Phase 4 bis 7: Schemata der manuellen Daten, `QUELLENBELEGE_MD`); `git diff a531fb6 HEAD --stat`: 173 Einfügungen, 0 Löschungen | `schreibe_csv` samt Float-zu-Int-Rundlaufprüfung (CR-01 aus Phase 3) unverändert, `test_schema.py` grün |
| `pipeline/ostbevern/pdf.py` | Commit `a51a33e` (Phase 7, `feat(07-01)`): `WortRahmen`, `RahmenZeile`, `zeilen_mit_rahmen` | rein additiv, `zeilen()` und `zeilen_fein()` unberührt |
| `pipeline/ostbevern/konfiguration.py` | Phase 4 bis 7 (`cabf5c1`, `d77a47f`, `6fddfc1`, `93a4720`) und **Phase 8: `4c105ff` `fix(08-08): 01/IN-04 Anzahlen nicht negativ`** | Phase 8 verschärft `lade_jahrgang` um die Ablehnung negativer `anzahlen.*` (5 Zeilen, `konfiguration.py:178-182`), Test dazu in `35b3d51`; die Werte in `2026.toml` (400 / 15 / 63) sind positiv, kein Einfluss auf die Daten |
| `pipeline/alle.py` | Phase 4 bis 7 (Schritte 05, 07, 08 angehängt) und **Phase 8: `c18a032` `refactor(08-08): 01/IN-02 pdf_relativ einmal berechnen`** | Phase 8 zieht eine Berechnung vor die Existenzprüfung, Verhalten gleich; Schritte 01, 02 und 06 laufen unverändert in derselben Reihenfolge |
| `pipeline/ostbevern/pruefung.py` | Phase 4 bis 7 (Regeln 5 bis 10, Toleranz je Regel `toleranz_fuer`, B.4/B.5 in Regel 4, Längenwächter `WR-03`, Pipe-Wächter `IN-02`); **Phase 8 hat die Datei nicht berührt** (`git log` ab 2026-10-07 über `pipeline daten` listet sie nicht) | Regeln 1 bis 3 unverändert in der Logik; Regel 4 um B.4/B.5 erweitert (siehe Wahrheit 4) |
| `pipeline/jahrgaenge/2026.toml`, `2026_sollwerte.toml` | Phase 4 bis 7 (Tabellen B.4, B.5, Eckwerte, Stichproben); Phase 8 keine | Die in Phase 2 geführten Tabellen `[satzung]`, `[gesamtergebnisplan]`, `[gesamtfinanzplan]`, `[teilergebnisplaene_pb]`, `[anhang_a]` sind unverändert |
| `pipeline/tests/test_konfiguration.py` | Phase 8: `35b3d51` | zusätzlicher Test, grün |
| `daten/aufbereitet/{ergebnisplan,finanzplan,hierarchie}.csv`, `daten/zwischen/seiten.csv`, `daten/pruefberichte/{befunde,konsistenz}.md` | `git diff 189c481 HEAD --stat` über `ergebnisplan.csv`, `finanzplan.csv`, `hierarchie.csv`, `seiten.csv`: leer, diese vier Dateien sind byte-identisch zum Stand des alten Berichts. `befunde.md` (+117 Zeilen, Regeln 5 bis 10 und Toleranztext) und `konsistenz.md` (Regeln 5 bis 10, Regel 4 von 194 auf 259 Werte durch B.4/B.5) wuchsen | die Befundzeilen zu Regel 1 bis 3 (`befunde.md:124-133`) sind unverändert (`git diff` zeigt keine geänderte Tabellenzeile mit Regel 1, 2 oder 3) |

Phase-8-Commits, die Phase-2-Code ändern: `4c105ff` (`konfiguration.py`), `35b3d51` (`test_konfiguration.py`), `c18a032` (`alle.py`). Keiner verändert Extraktion, Klassifikation oder Prüfregeln 1 bis 4.

### Live-Evidenz

Die vollständigen Läufe stammen aus `.planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md` (Kopf: `head: 1d0df35da1842daec515b40dd62f8d918e240105`, erstellt 2026-10-09T06:24:00Z). Dieser Plan hat weder `alle.py` noch die volle pytest-Suite noch Playwright ausgeführt (D-23).

- Gepinnter Stand: `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline app daten scripts .github` endete mit Exit 0 (geprüft auf HEAD `b07d34f`). Die Evidenz des Basislaufs gilt damit für den Code, den dieser Bericht beschreibt.
- Basislauf, Pipeline: `681 passed in 350.31s`, 0 Skips; `uv run --directory pipeline python alle.py --jahr 2026` Exit 0, `daten/`, `app/src/data/` und `app/public/quellen` byte-identisch. Ausgabezeilen: `Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte.`, `Schritt 02: 14899 Planzeilen geschrieben.`, `Regel 1: grün (6593 Werte)`, `Regel 2: grün (7994 Werte)`, `Regel 3: grün (114 Werte)`, `Regel 4: grün (259 Werte)`, `Veraltete Befunde: 0`.
- Eigene, benannte Läufe in diesem Plan (`uv run --directory pipeline pytest -p no:cacheprovider -q …`):
  - `tests/test_hierarchie.py tests/test_zahlen.py`: `60 passed`
  - `tests/test_seiten.py tests/test_schema.py tests/test_konfiguration.py tests/test_plaene.py`: `99 passed`
  - `tests/test_pruefung.py -k "regel1_sollwerte_gesamtplaene_gruen or regel1_formelkette or regel1_toleriert_einen_euro or regel2_gruen or regel2_erkennt or regel3_gruen or regel3_ignoriert or regel3_erkennt or regel4_sollwerte or regel4_b3_gruen or regel4_b4_b5_gruen or regel4_b4_erkennt or regel4_satzung or regel4_b1_laengen or konsistenzbericht_meldet_abweichung_ueber_einem_euro or konsistenzbericht_toleriert_einen_euro or befund_deckt"`: `20 passed, 69 deselected`
  - Danach war `git status --short` leer (die Läufe haben nichts verändert).
- Eigene Zählung auf den eingecheckten Daten (Python-Skript, nur lesend): `seiten.csv` 400 Zeilen, 0 mit `typ=unbekannt`; `hierarchie.csv` 15 PB, 49 PG (41 `synthetisch=true`, 8 gedruckt), 63 P; `ergebnisplan.csv` 10 188 Zeilen (GESAMT 198, PB 1236, PG 3762, P 4992), `finanzplan.csv` 4 711 Zeilen (GESAMT 287, PB 672, PG 1589, P 2163); alle Zeilen tragen `pdf_seite` und `zeile_kanonisch`; Wertarten `ergebnis`, `ansatz`, `planung` im Ergebnisplan sowie zusätzlich `ve` (673 Zeilen) im Finanzplan.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `seiten.csv` ordnet jeder PDF-Seite Typ, PB, PG und Produkt zu, Fortsetzungsseiten erben den Kontext, ein Test bestätigt die Startseiten aller 63 Produkte gegen Anhang A; `hierarchie.csv` hat 15 PB, alle PG (synthetische markiert) und 63 Produkte mit Namen | ✓ VERIFIED | Code: `seiten.py:201-270` (`klassifiziere_dokument`: eine `Seite` je PDF-Seite 1 bis `anzahlen.pdf_seiten`; Vererbung von Typ und Kontext nur bei gleichem Kopf-Kontext `seiten.py:250-258`, sonst `unbekannt` `:260`). Daten heute: 400 Zeilen, 0 `unbekannt`, 15 PB / 49 PG (41 synthetisch) / 63 P; Basislauf `Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte.`. Tests (grün, eigener Lauf): `test_hierarchie.py:149 test_produktseiten_in_seiten_csv_stimmen_mit_anhang_a` (alle 86 Anhang-A-Einträge, davon 63 Produkte, gegen `seiten.csv`), `:68 test_anhang_a_eintraege_stimmen_mit_hierarchie_ueberein` (Startseite und Name), `:47 test_hierarchie_hat_korrekte_ebenenzahlen`, `:79 test_synthetische_pg_markierung_und_namen`; `test_seiten.py:116 test_fortsetzungsseite_erbt_typ` (gegen das echte PDF). |
| 2 | Die Unit-Tests des Zahlenparsers sind grün: deutsches Format, Minus, „–“ als „kein Wert“, angeklebte Beträge, `C` als Eurozeichen | ✓ VERIFIED | Code unverändert seit Phase 2 (`git log` über `zahlen.py` ab 2026-10-02: leer): `zahlen.py:17` Tausenderformat, `:23` U+2212, `:24` „–“, `:22` `C`/`€`, `:39-52` `lies_betrag`, `:102-115` `trenne_angeklebten_betrag`. Tests (grün, eigener Lauf, 60 passed mit `test_hierarchie.py`): `test_zahlen.py:20 …deutsches_tausenderformat`, `:28 …ascii_minus`, `:32 …unicode_minus`, `:36 …kein_wert_gibt_none`, `:48 …eurozeichen_c_mit_leerzeichen`, `:52 …eurozeichen_c_angeklebt`, `:85 test_trenne_angeklebten_betrag_findet_glued_amount`, `:68 …ungueltige_formen_loesen_zahlenfehler_aus`. |
| 3 | `ergebnisplan.csv` und `finanzplan.csv` (inkl. VE) enthalten Gesamt-, PB- und Produktpläne mit `zeile`, `zeile_kanonisch`, `ist_summe`, `pdf_seite`; Regel 1 grün, Regel 2 grün (Produkte → PG → PB), Regel 3 grün (15 PB → Gesamtergebnisplan ohne TP 27/28) | ✓ VERIFIED | Kopfzeile der CSV `ebene,code,synthetisch,zeile,zeile_kanonisch,zeile_name,operator,ist_summe,jahr,wertart,betrag,pdf_seite`; Ebenen GESAMT/PB/PG/P in beiden Dateien, `ve` 673 Zeilen im Finanzplan (eigene Zählung). Basislauf: `Regel 1: grün (6593 Werte)`, `Regel 2: grün (7994 Werte)`, `Regel 3: grün (114 Werte)`, Zahlen identisch zum Bericht vom 2026-10-02. Code: `pruefung.py:502-539` (Regel 1, Formeln aus `zeilen.py:304 FORMELN`), `:553-638` (Regel 2 zweistufig PG und PB), `:641-679` (Regel 3, `REGEL3_ZEILEN` `:111` = Z. 01–17, 19, 20; TP 27/28 ausgenommen, Begründung `:100-110`). Tests (grün, eigener Lauf): `test_pruefung.py:518 test_regel1_sollwerte_gesamtplaene_gruen`, `:555 …regel2_gruen_auf_eingecheckten_daten`, `:563 …regel2_erkennt_manipulierte_produktzeile`, `:616 …regel3_gruen_auf_eingecheckten_daten` (`geprueft == 114`), `:625 …regel3_ignoriert_tp_27_28`, `:651 …regel3_erkennt_manipulierte_pb_zeile`. Die zehn dokumentierten Rundungsbefunde zu Regel 1 bis 3 (3 + 6 + 1, entspricht der Spalte „Bekannte Befunde“ in `konsistenz.md`: PB 08 Z. 17, PB 01/02 Z. 29/31/10, PB 01 Finanzplan Z. 09, Gesamt Z. 11, je 2024) stehen mit Begründung in `befunde.md:124-133`; `konsistenz.md` meldet „Veraltete Befunde: Keine.“ |
| 4 | Die Anhang-B-Sollwerte werden auf den Euro getroffen: B.1 (z. B. Z. 28 2026 = −2.353.506 €), B.2 (Z. 23 = 7.224.830 €, Z. 30 = 12.280.484 €, Z. 33 = 5.200.000 €, Z. 41 = 4.199.420 €), B.3 (Σ Erträge 27.042.063 €, Σ Aufwendungen 30.255.569 €), Satzung § 1 (27.502.063 € / 30.455.569 €) | ✓ VERIFIED | Sollwerte in `2026_sollwerte.toml:11-24` (Satzung), `:31-53` (B.1, Z. 28 Spalte 2026 = −2353506), `:58-68` (B.2), `:88-111` (B.3 und Summen), unverändert gegenüber Phase 2. Eigene Gegenprobe in den Daten: `ergebnisplan.csv` `GESAMT,,false,28,…,2026,ansatz,-2353506,62`; `finanzplan.csv` Z. 23 `7224830`, Z. 30 `12280484`, Z. 33 `5200000`, Z. 41 `4199420` (je Ansatz 2026, Seite 63). Basislauf `Regel 4: grün (259 Werte)`: Die Zahl wuchs von 194 auf 259, weil Phase 4 die unabhängig abgeschriebenen Tabellen B.4 (Steuerarten, 9 Posten × 6 Jahre = 54) und B.5 (Transferaufwendungen, 11 Posten) in Regel 4 aufgenommen hat (`pruefung.py:870-967`, `:1000-1017`); die Phase-2-Anteile bleiben 126 (B.1) + 9 (B.2) + 12 (Satzung) + 47 (B.3) = 194 (eigene Zählung aus der TOML, 194 + 54 + 11 = 259). Tests (grün, eigener Lauf): `test_pruefung.py:334 test_regel4_sollwerte_gesamtergebnisplan_gruen`, `:345 …gesamtfinanzplan_und_satzung_gruen`, `:392 …regel4_b3_gruen_auf_eingecheckten_daten`, `:457 …regel4_b4_b5_gruen`, `:466 …regel4_b4_erkennt_tippfehler_in_steuerarten`. |
| 5 | `uv run pytest` erzeugt `daten/pruefberichte/konsistenz.md`; eine Abweichung über 1 €, die nicht in `befunde.md` steht, lässt den Lauf scheitern | ✓ VERIFIED | `pruefung.py:85 TOLERANZ_EURO = 1`, `:92-97` `toleranz_fuer` (nur Regel 9 und 10 exakt 0, alle anderen Regeln unverändert 1 €), `:256-261` `Regelergebnis.status` rot bei Abweichung über der Toleranz, `:273-277` `Bericht.ist_gruen` (auch rot bei veralteten Befunden), `:446-481` `gleiche_befunde_ab` (nur dokumentierte Befunde decken ab). `06_pruefen.py:74-75` beendet mit Exit 1, wenn der Bericht nicht grün ist; `alle.py` stoppt dann vor Schritt 07. pytest schreibt den Bericht: `test_pruefung.py:1060 test_konsistenzbericht_wird_geschrieben` (im Basislauf Teil der 681 grünen Tests), und die Tests auf den echten Daten behaupten „grün“ (`:334`, `:518`, `:555`, `:616`), ein undokumentierter Wert wäre dort ein roter Test. Gegenprobe: `:1121 test_konsistenzbericht_meldet_abweichung_ueber_einem_euro` (Abweichung 2 € ⇒ Regel 4 rot), `:695 test_regel1_toleriert_einen_euro_sonst_rot`, `:1829 test_konsistenzbericht_toleriert_einen_euro`, `:744 test_befund_deckt_abweichung_innerhalb_toleranz_ab` (alle grün im eigenen Lauf). `ci.yml:45` führt `uv run pytest` aus, `:46-62` die Reproduzierbarkeit (`alle.py` + `git diff --exit-code`). Die eingecheckte `konsistenz.md` meldet „Gesamtstatus: grün“. |

**Score:** 5/5 Roadmap-Erfolgskriterien verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pipeline/ostbevern/zahlen.py` | Zahlenparser (EXTR-01) | ✓ VERIFIED | vorhanden, 115 Zeilen, importiert von `plaene.py` und `tests/test_zahlen.py` |
| `pipeline/ostbevern/seiten.py`, `pipeline/01_seiten_klassifizieren.py` | Seitenklassifikation und Hierarchie | ✓ VERIFIED | Schritt 01 läuft im Basislauf (`Schritt 01: …`) |
| `pipeline/ostbevern/plaene.py`, `zeilen.py`, `pipeline/02_plaene_extrahieren.py` | Plan-Extraktion | ✓ VERIFIED | `Schritt 02: 14899 Planzeilen geschrieben.` |
| `pipeline/ostbevern/pruefung.py`, `pipeline/06_pruefen.py` | Regeln 1 bis 4 und Bericht | ✓ VERIFIED | Schritt 06 grün im Basislauf |
| `daten/aufbereitet/ergebnisplan.csv`, `finanzplan.csv`, `hierarchie.csv`, `daten/zwischen/seiten.csv`, `daten/pruefberichte/konsistenz.md` | Ergebnisdateien | ✓ VERIFIED | byte-identisch nach `alle.py` (Basislauf, Abschnitt 4) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `seiten.py` | `jahrgaenge/2026.toml` | `jahrgang.kopfzeilen.seitentypen`, `jahrgang.seitenbereiche` | ✓ WIRED | `seiten.py:241` liest die Muster aus der Konfiguration |
| `pruefung.py` | `2026_sollwerte.toml` | `lade_sollwerte`, `sollwerte["gesamtergebnisplan"]` usw. | ✓ WIRED | `pruefung.py:685`, `:733`, `:766`, `:810` |
| `06_pruefen.py` / `pytest` | `pruefe_alles` | gemeinsame Funktion | ✓ WIRED | `06_pruefen.py:54`, `test_pruefung.py:1060` |
| `alle.py` | Schritte 01, 02, 06 | feste Reihenfolge, Abbruch bei rotem Bericht | ✓ WIRED | Basislauf-Ausgabe in Reihenfolge |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `ergebnisplan.csv` / `finanzplan.csv` | `betrag` | `plaene.lies_plantabelle` über `pdf.py` aus `raw_data/haushalt-2026.pdf` | ja, 10 188 und 4 711 Zeilen, `alle.py` regeneriert sie byte-identisch | ✓ FLOWING |
| `konsistenz.md` | Regelzahlen | `pruefe_alles` aus den CSVs und der Sollwertdatei (liest kein PDF, `test_pruefung.py:1814 test_pruefung_liest_kein_pdf`) | ja | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Zahlenparser und Hierarchie-Sollwerte | `pytest tests/test_hierarchie.py tests/test_zahlen.py` | 60 passed | ✓ PASS |
| Klassifikation, Schema, Konfiguration, Planparser | `pytest tests/test_seiten.py tests/test_schema.py tests/test_konfiguration.py tests/test_plaene.py` | 99 passed | ✓ PASS |
| Regeln 1 bis 4 inkl. 1-€-Gate | `pytest tests/test_pruefung.py -k "…"` (siehe Live-Evidenz) | 20 passed | ✓ PASS |
| Vollständige Kette | siehe `09-BASISLAUF.md` | 681 passed, `alle.py` byte-identisch | ✓ PASS (zitiert) |

### Probe Execution

Step 7c: SKIPPED (keine Probe-Skripte in Phase 2 deklariert).

### Requirements Coverage

Vorläufig; Task 2 von Plan 09-05 ergänzt Pläne, Beschreibungen und die Regressionsprüfung.

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| EXTR-01 | 02-01 | Zahlenparser | ✓ SATISFIED | Wahrheit 2 |
| EXTR-02 | 02-02 | `seiten.csv` | ✓ SATISFIED | Wahrheit 1 |
| EXTR-03 | 02-02 | `hierarchie.csv` | ✓ SATISFIED | Wahrheit 1 |
| EXTR-04 | 02-01, 02-04 | Ergebnispläne | ✓ SATISFIED | Wahrheit 3 |
| EXTR-05 | 02-03, 02-04 | Finanzpläne inkl. VE | ✓ SATISFIED | Wahrheit 3 |
| PRUEF-01 | 02-03, 02-04 | Regel 1 | ✓ SATISFIED | Wahrheit 3 |
| PRUEF-02 | 02-05 | Regel 2 | ✓ SATISFIED | Wahrheit 3 |
| PRUEF-03 | 02-05 | Regel 3 | ✓ SATISFIED | Wahrheit 3 |
| PRUEF-04 | 02-01, 02-03, 02-05 | Regel 4 | ✓ SATISFIED | Wahrheit 4 |
| PRUEF-09 | 02-01, 02-03, 02-05 | Bericht und 1-€-Gate | ✓ SATISFIED | Wahrheit 5 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (alle abgedeckten Pipeline-, Test- und Berichtsdateien) | – | Suche nach `TBD`, `FIXME`, `XXX`, `TODO`, `HACK`, `PLACEHOLDER` (grep, heute) | – | keine Treffer |

### Human Verification Required

Keine. Die Pipeline ist deterministisch und headless; jede Wahrheit hat einen Testlauf oder einen byte-genauen Datenvergleich als Beleg.

### Gaps Summary

Keine Lücken. Alle fünf Roadmap-Erfolgskriterien halten auf dem Endstand nach Phase 8. Die Änderungen an Phase-2-Dateien seit 2026-10-02 sind additiv oder verschärfen nur Prüfungen (siehe Tabelle oben); die Plan-CSVs sind byte-identisch, die Zahlen für Regel 1 bis 3 (6593 / 7994 / 114) gleich geblieben, und die Mehrung bei Regel 4 (194 auf 259) stammt aus den in Phase 4 ergänzten Tabellen B.4 und B.5.

---

_Verified: 2026-10-09T06:33:00Z_
_Verifier: Claude (gsd-verifier-Verfahren, ausgeführt in Plan 09-05)_
