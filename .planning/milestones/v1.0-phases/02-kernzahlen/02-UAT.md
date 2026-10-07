---
status: complete
phase: 02-kernzahlen
source: [02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md, 02-05-SUMMARY.md]
started: 2026-10-01T17:00:56.471Z
updated: 2026-10-01T17:05:25Z
---

## Current Test

[testing complete]

User confirmed all 19 automated results on 2026-10-01T17:05:25Z.

## Tests

### 1. 02-01 D1 (EXTR-04)
expected: Tracer: Gesamtergebnisplan-Seite vollständig von PDF über Spaltenzuordnung und Zeilen-Wörterbuch nach ergebnisplan.csv extrahiert (198 Zeilen, gedrucktes Vorzeichen, Operator-Spalte, ist_summe, pdf_seite)
result: pass
source: automated
coverage_id: D1
verification: pipeline/tests/test_plaene.py#test_gesamtergebnisplan_zeilen_entsprechen_woerterbuch; pipeline/tests/test_plaene.py#test_gesamtergebnisplan_trifft_sollwerte_b1; uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026

### 2. 02-01 D2 (PRUEF-04)
expected: Regel 4 vergleicht ergebnisplan.csv gegen Anhang B.1 (126 Werte, grün); konsistenz.md wird byte-identisch von 06_pruefen.py und pytest erzeugt
result: pass
source: automated
coverage_id: D2
verification: pipeline/tests/test_pruefung.py#test_regel4_sollwerte_gesamtergebnisplan_gruen; pipeline/tests/test_pruefung.py#test_konsistenzbericht_wird_geschrieben; pipeline/tests/test_pruefung.py#test_konsistenzbericht_meldet_abweichung_ueber_einem_euro; pipeline/tests/test_pruefung.py#test_konsistenzbericht_toleriert_einen_euro

### 3. 02-01 D3 (EXTR-01)
expected: Vollständiger EXTR-01-Zahlenparser (dt. Tausenderformat, U+2212-Minus, kein Wert, C/EUR-Zeichen, angeklebte Beträge) mit reinen String-Tests
result: pass
source: automated
coverage_id: D3
verification: pipeline/tests/test_zahlen.py (21 Testfunktionen, teils parametrisiert)

### 4. 02-01 D4 (PRUEF-09)
expected: Sollwertdatei hält Anhang B.1 (komplett), B.2, B.3 je PB; lade_sollwerte validiert alle neuen Tabellen vollständig und meldet fehlende Schlüssel/Felder
result: pass
source: automated
coverage_id: D4
verification: pipeline/tests/test_konfiguration.py#test_lade_sollwerte_gibt_alle_tabellen_vollstaendig_zurueck; pipeline/tests/test_konfiguration.py#test_sollwertdatei_ohne_gesamtfinanzplan_meldet_schluessel; pipeline/tests/test_konfiguration.py#test_teilergebnisplaene_pb_eintrag_ohne_ordentliche_aufwendungen_meldet_feld; pipeline/tests/test_konfiguration.py#test_gesamtfinanzplan_ansatz_schluessel_ohne_zweistellige_zeile_wird_abgelehnt

### 5. 02-02 D1 (EXTR-02)
expected: seiten.csv klassifiziert alle 400 PDF-Seiten (Kapitelname außerhalb der Teilpläne, feines Typ-Vokabular innerhalb, Fortsetzungsseiten-Vererbung), 0 unbekannt für 2026
result: pass
source: automated
coverage_id: D1
verification: pipeline/tests/test_seiten.py (8 Testfunktionen, echte PDF-Seiten, D-07); uv run --directory pipeline python 01_seiten_klassifizieren.py --jahr 2026

### 6. 02-02 D2 (EXTR-03)
expected: hierarchie.csv mit 15 PB, 48 PG (40 synthetisch nach D-14) und 63 Produkten; alle Namen/Startseiten stimmen mit Anhang A überein (D-19, Roadmap SC 1)
result: pass
source: automated
coverage_id: D2
verification: pipeline/tests/test_hierarchie.py (5 Testfunktionen, eingecheckte CSVs, D-06); uv run --directory pipeline python 01_seiten_klassifizieren.py --jahr 2026

### 7. 02-02 D3 (EXTR-03)
expected: lade_sollwerte validiert Anhang A vollständig (2-/4-/6-stelliger Code, Name, pdf_seite >= 1); lade_jahrgang validiert kopfzeilen.produktgruppe/seitentypen und lehnt überlappende Seitenbereiche ab
result: pass
source: automated
coverage_id: D3
verification: pipeline/tests/test_konfiguration.py (6 neue Testfunktionen)

### 8. 02-03 D1 (EXTR-05)
expected: Gesamtfinanzplan inkl. VE-Spalte wird vollständig extrahiert (287 Zeilen, 41 Zeilen x 7 Spalten), die doppelte '2026'-Kopfzeile (Ansatz/VE) wird über x-Position statt Text aufgelöst
result: pass
source: automated
coverage_id: D1
verification: pipeline/tests/test_plaene.py#test_gesamtfinanzplan_zeilen_entsprechen_woerterbuch; pipeline/tests/test_plaene.py#test_gesamtfinanzplan_trifft_sollwerte_b2; pipeline/tests/test_plaene.py#test_gesamtfinanzplan_falscher_spaltenkopf_bricht_ab; uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026

### 9. 02-03 D2 (PRUEF-01)
expected: Regel 1 prüft über einen Formelketten-Resolver (Planwerte) jede gedruckte Summenzeile aller vier Plantypen; fehlende Zwischenzeilen (Pitfall 1) werden korrekt über die Kette hergeleitet statt als 0 fehlinterpretiert; grün mit 118 Werten (Gesamtergebnisplan 8x6, Gesamtfinanzplan 10x7)
result: pass
source: automated
coverage_id: D2
verification: pipeline/tests/test_pruefung.py#test_regel1_sollwerte_gesamtplaene_gruen; pipeline/tests/test_pruefung.py#test_regel1_formelkette_fuer_fehlende_zwischenzeilen; pipeline/tests/test_pruefung.py#test_regel1_toleriert_einen_euro_sonst_rot; pipeline/tests/test_pruefung.py#test_regel1_keine_formel_fuer_nachrichtlich_zeile_33; uv run --directory pipeline python 06_pruefen.py --jahr 2026

### 10. 02-03 D3 (PRUEF-04)
expected: Regel 4 deckt Anhang B.1 (Gesamtergebnisplan), B.2 (Gesamtfinanzplan Ansatz/VE) und Satzung §1-3 ab; 147 Werte insgesamt, grün
result: pass
source: automated
coverage_id: D3
verification: pipeline/tests/test_pruefung.py#test_regel4_sollwerte_gesamtergebnisplan_gruen; pipeline/tests/test_pruefung.py#test_regel4_sollwerte_gesamtfinanzplan_und_satzung_gruen; pipeline/tests/test_pruefung.py#test_regel4_satzung_ohne_formel_bricht_ab

### 11. 02-03 D4 (PRUEF-09)
expected: befunde.md mit maschinenlesbarer Schlüsseltabelle (D-02); D-04 (veraltete Befunde) und D-05 (Betragstoleranz) sind erzwungen und getestet; konsistenz.md zeigt Gesamtstatus, Übersicht, Abweichungen, Bekannte und Veraltete Befunde (D-03); pytest und 06_pruefen.py scheitern bei veralteten oder nicht passenden Befunden (PRUEF-09)
result: pass
source: automated
coverage_id: D4
verification: pipeline/tests/test_pruefung.py#test_befund_deckt_abweichung_innerhalb_toleranz_ab; pipeline/tests/test_pruefung.py#test_veralteter_befund_wenn_abweichung_nicht_mehr_passt; pipeline/tests/test_pruefung.py#test_veralteter_befund_ohne_passende_abweichung; pipeline/tests/test_pruefung.py#test_veralteter_befund_macht_bericht_nicht_gruen; pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_falsche_zellenzahl; pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_abweichung_nicht_int; pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_abweichung_zu_klein; pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_leere_begruendung; pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_fehlende_ueberschrift; pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_fehlende_datei; pipeline/tests/test_pruefung.py#test_konsistenzbericht_listet_bekannten_befund

### 12. 02-04 D1 (EXTR-04)
expected: ergebnisplan.csv and finanzplan.csv hold, besides GESAMT, the Teilergebnis- and Teilfinanzpläne of all 15 PB, all 8 printed PG, all 40 synthetic PG, and all 63 products, one line per printed value with zeile, zeile_kanonisch, ist_summe, operator and pdf_seite
result: pass
source: automated
coverage_id: D1
verification: pipeline/tests/test_plaene.py#test_alle_knoten_haben_teilplaene; pipeline/tests/test_hierarchie.py#test_jeder_knoten_hat_ergebnis_und_finanzplanzeilen; pipeline/tests/test_hierarchie.py#test_synthetische_pg_summieren_ihre_produkte; uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026

### 13. 02-04 D2 (EXTR-05)
expected: Teilfinanzplan continuation across pages (e.g. a product whose Teilfinanzplan continues on the next page) is extracted with correct pdf_seite per row, no duplicate row numbers, and includes the continuation's own rows (VE column included, EXTR-05)
result: pass
source: automated
coverage_id: D2
verification: pipeline/tests/test_plaene.py#test_teilfinanzplan_fortsetzung_auf_folgeseite; pipeline/tests/test_plaene.py#test_pb_teilfinanzplan_hat_sieben_spalten

### 14. 02-04 D3 (PRUEF-01)
expected: Regel 1 (zeilenformeln via the formula-chain resolver) is grün for every Gesamt- and Teilplan (PB, printed PG, synthetic PG, Produkt) — 6550 values checked
result: pass
source: automated
coverage_id: D3
verification: uv run --directory pipeline python 06_pruefen.py --jahr 2026 (Regel 1: grün); pipeline/tests/test_pruefung.py#test_regel1_sollwerte_gesamtplaene_gruen

### 15. 02-05 D1 (PRUEF-09)
expected: alle.py runs Schritt 01 -> 02 -> 06 in order (D-09), exits 1 on any step exception or a red/veraltet Konsistenzbericht (the report is still written first), and regenerates daten/ byte-identically on the committed state
result: pass
source: automated
coverage_id: D1
verification: pipeline/tests/test_alle.py#test_ohne_jahr_nutzt_standardjahr; pipeline/tests/test_alle.py#test_roter_bericht_beendet_mit_fehler; pipeline/tests/test_alle.py#test_schrittfehler_beendet_mit_fehler; uv run --directory pipeline python alle.py --jahr 2026 (exit 0, git status --porcelain daten/ empty)

### 16. 02-05 D2 (PRUEF-02)
expected: Regel 2 (two-level: Produkte->PG and PG->PB, printed and synthetic PG, both Teilplan types) is grün on the extracted data and proven to catch a 2 EUR manipulation at exactly the right hierarchy level
result: pass
source: automated
coverage_id: D2
verification: pipeline/tests/test_pruefung.py#test_regel2_gruen_auf_eingecheckten_daten; pipeline/tests/test_pruefung.py#test_regel2_erkennt_manipulierte_produktzeile; uv run --directory pipeline python 06_pruefen.py --jahr 2026 (Regel 2: grün, 7920 Werte)

### 17. 02-05 D3 (PRUEF-03)
expected: Regel 3 (15 PB -> Gesamtergebnisplan, Z. 01-17/19/20, no TP 27/28) is grün with 114 checked values and proven to ignore TP 27/28 and catch a 2 EUR PB-level manipulation
result: pass
source: automated
coverage_id: D3
verification: pipeline/tests/test_pruefung.py#test_regel3_gruen_auf_eingecheckten_daten; pipeline/tests/test_pruefung.py#test_regel3_ignoriert_tp_27_28; pipeline/tests/test_pruefung.py#test_regel3_erkennt_manipulierte_pb_zeile

### 18. 02-05 D4 (PRUEF-04)
expected: Regel 4 covers Anhang B.3 (194 Werte total: 126 B.1 + 9 B.2 + 12 Satzung + 45 B.3 + 2 PB-Summen), derives a missing PB Z.29 through the formula chain, and raises PruefungsFehler naming an unknown PB key instead of skipping it silently
result: pass
source: automated
coverage_id: D4
verification: pipeline/tests/test_pruefung.py#test_regel4_b3_gruen_auf_eingecheckten_daten; pipeline/tests/test_pruefung.py#test_regel4_b3_herleitet_fehlende_z29; pipeline/tests/test_pruefung.py#test_regel4_b3_unbekannte_pb_bricht_ab; uv run --directory pipeline python alle.py --jahr 2026 (Regel 4: grün, 194 Werte)

### 19. 02-05 D5 (PRUEF-09)
expected: konsistenz.md lists Regel 1-4 in order with Gesamtstatus grün, a '## Seiten mit typ=unbekannt' section (D-17, listed pages do not turn the report rot), and pytest regenerates it byte-identically
result: pass
source: automated
coverage_id: D5
verification: pipeline/tests/test_pruefung.py#test_konsistenzbericht_unbekannte_seiten_keine_auf_echten_daten; pipeline/tests/test_pruefung.py#test_konsistenzbericht_unbekannte_seiten_gelistet; pipeline/tests/test_pruefung.py#test_konsistenzbericht_wird_geschrieben; (cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest) -- CI replay

## Summary

total: 19
passed: 19
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
