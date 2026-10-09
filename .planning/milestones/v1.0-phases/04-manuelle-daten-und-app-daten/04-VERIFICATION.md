---
phase: 04-manuelle-daten-und-app-daten
verified: 2026-10-09T06:31:00Z
status: passed
score: 10/10 must-haves verified
covered_files:
  - ".github/workflows/ci.yml"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-01-PLAN.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-01-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-02-PLAN.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-02-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-03-PLAN.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-03-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-04-PLAN.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-04-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-05-PLAN.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-05-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-06-PLAN.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-06-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-REVIEW.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md"
  - "app/.prettierignore"
  - "app/src/charts/format.ts"
  - "app/src/data/daten.ts"
  - "app/src/data/haushalt.json"
  - "app/src/data/investitionen.json"
  - "app/src/data/produkte.json"
  - "app/src/data/stellenplan.json"
  - "app/src/data/texte.json"
  - "app/src/data/typen.ts"
  - "daten/aufbereitet/stellenplan.csv"
  - "daten/manuell/README.md"
  - "daten/manuell/meta.json"
  - "daten/manuell/texte/erklaerungen.md"
  - "daten/manuell/texte/glossar.md"
  - "daten/pruefberichte/befunde.md"
  - "daten/pruefberichte/konsistenz.md"
  - "pipeline/05_stellenplan.py"
  - "pipeline/07_app_daten.py"
  - "pipeline/alle.py"
  - "pipeline/jahrgaenge/2026_sollwerte.toml"
  - "pipeline/ostbevern/app_daten.py"
  - "pipeline/ostbevern/konfiguration.py"
  - "pipeline/ostbevern/manuell.py"
  - "pipeline/ostbevern/pruefung.py"
  - "pipeline/ostbevern/schema.py"
  - "pipeline/ostbevern/stellenplan.py"
  - "pipeline/ostbevern/texte.py"
  - "pipeline/tests/test_app_daten.py"
  - "pipeline/tests/test_formatiere.py"
  - "pipeline/tests/test_manuell.py"
  - "pipeline/tests/test_produkte.py"
  - "pipeline/tests/test_pruefung.py"
  - "pipeline/tests/test_stellenplan.py"
  - "pipeline/tests/test_texte.py"
covered_digest: "v3:sha256:c70d7da0a35f1566808f86064207cef6952cfaa4a1f30a72a19547c84cb51b8f"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "10/10 must-haves verified"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
deferred: []
advisory:
  - finding: "Das Key-Link-Muster von Plan 04-05 (`texte\\.(lies_erklaerungen|loese_auf)\\(`) trifft den heutigen Code nicht mehr, weil `app_daten.py` die Funktionen seit Phase 5 direkt importiert (`from ostbevern.texte import lies_erklaerungen, loese_auf`) und ohne Modulpräfix aufruft (`app_daten.py:1112`, `:1124`). Die Verdrahtung besteht, nur der Regex des Plans ist veraltet."
    category: other
    reason: "Musterdrift im archivierten Plan, kein Codefehler; `verify.key-links` meldet für 04-05 deshalb `all_verified: false`. Ein Eingriff in den archivierten Plan unterbleibt, die Prüfung hier erfolgt über den Import und die beiden Aufrufstellen."
    evidence_status: "deterministisch belegt (grep und verify.key-links), kein Befund gegen das Phasenziel"
  - finding: "Der Roadmap-Satz „Die Fußnote an 10.147 ist in `befunde.md` dokumentiert“ trifft nur im Wortsinn der Prosa zu: `befunde.md` beschreibt die Prüfung `brutto_fussnote` (Regel 5, D-10) im Regeltext, hat aber keine Zeile in der Schlüsseltabelle, weil die Fußnote keine Abweichung erzeugt. Die Fußnote selbst ist in `daten/manuell/README.md` (Abschnitt „Kreisumlage, Fußnote“) und in `meta.json` (`rueckstellungsaufloesung`) belegt und wird in Regel 5 exakt geprüft."
    category: other
    reason: "Dokumentationsort weicht vom Roadmap-Wortlaut ab; der Inhalt ist vorhanden und geprüft. Wortlaut des Roadmaps wird nicht nachträglich geändert."
    evidence_status: "deterministisch belegt (grep in befunde.md, README.md, meta.json)"
behavior_unverified_items: []
---

# Phase 4: Manuelle Daten und App-Daten Verification Report

**Phase Goal:** Die Pipeline ist geschlossen. Die Vorberichtswerte sind manuell gepflegt und gegen den Plan geprüft, der Stellenplan ist extrahiert, und die App-JSON-Dateien entstehen reproduzierbar ohne Personennamen.
**Verified:** 2026-10-09T06:31:00Z
**Status:** passed
**Re-verification:** Yes — neue Verifikation auf dem Endstand nach Phase 8 und dem D-20-Fix aus Phase 9 (Plan 09-07), ersetzt den Bericht vom 2026-10-04T08:51:42Z

## Warum diese Re-Verifikation (Phase 9, AUD-02)

Der Bericht vom 2026-10-04T08:51:42Z (`status: passed`, `score: 10/10 must-haves verified`, Fingerprint v2) bezog sich auf Dateien unter `.planning/phases/04-…`. Seitdem hat sich der Code der Phase 4 geändert, und `verification.status` meldete für dieses Verzeichnis `stale` (siehe `09-BASISLAUF.md`, Abschnitt „Verifikationsstatus vor der Re-Verifikation“). Dieser Bericht prüft jede Wahrheit des alten Berichts und jedes Roadmap-Erfolgskriterium der Phase 4 neu gegen den heutigen Code, mit dem Verfahren des gsd-verifier im Re-Verifikationsmodus (Step 0, dann Steps 3 bis 9).

Geänderte Dateien der Phase 4 seit 2026-10-04T08:51:42Z (`git log --since=2026-10-04T08:51:42Z -- <covered_files>`), nach Phasen:

- **Phase 5** (Leitfragen-Seiten): `format.ts` Strich-Fallback und exhaustiver `never`-Guard (65cd6d8, WR-06/IN-01 des alten Berichts), `texte.py` Quelle-Zeile wird als Ganzes geprüft (e3a2122, 9d18267: WR-04), fehlende Formel-Eingaben als `TexteFehler` (7587fd5: WR-03), Glossar und jahrneutrale Erklärtexte (9951542, fb6959a), Regel 5 mit Finanzplan-Zweig, Investitionszuwendungen und Konzessionsabgaben (38b631f, 09e0ce0, 8a64bef, 32dc5d1), `zeilen_namen` in `haushalt.json` (abf4f6c).
- **Phase 6** (Kontext-Seiten): Einzelzuschüsse lfd. Zwecke bis `haushalt.json` und Regel 5 (405fcf4, fc73bc6), HSK-Schwellen in `meta.json` (5d68b62), Polster- und Schuldenformeln und abgenommene Erklärtexte (50d5372, 319ef84).
- **Phase 7** (Feinschliff): Wächter in `app_daten.py`/`pruefung.py` (d53ffc7, ee7f4ae: WR-01, WR-02, IN-02 des alten Berichts), Schritt 08 in `alle.py` (897f10d, 6fddfc1, a51a33e), CI-Anpassungen an `ci.yml` (92fc4cc, 93b8ec5, 2cb379e, a3f05af, ef612e9, 93a4720, 8523030).
- **Phase 8** (Fixes und Triage), die Änderungen, die der Plan eigens nennt: `27e0be7` (`pruefe_text` lehnt getippte Jahreszahlen ab, Titel werden geprüft), `7d4be31` (Jahreszahlen in Erklärtexten als Platzhalter, `texte.json`, `erklaerungen.md`), `e8e25d5` (`_pruefe_jahrbezug`, `texte.py:585`), `c1da62e` (`TexteFehler` statt Division durch 0), `4c105ff` (`konfiguration.py`: Anzahlen nicht negativ), `c27904b` (`test_formatiere.py` kennt `jahr.fest_JJJJ`). Außerdem `96a23de`, das `app/src/data/beispieldaten.json` entfernt hat (keine der vier Pflichtdateien der Phase 4).

Das Ergebnis dieser Neuprüfung: keine der zehn Wahrheiten ist zurückgefallen, es gibt keine Lücke. Die Änderungen sind durchweg Verschärfungen (zusätzliche Wächter und Tests), die die Daten nicht verändern: `alle.py` erzeugt `daten/`, `app/src/data/` und `app/public/quellen` im Basislauf byte-identisch.

### Live-Evidenz

Die vollen Läufe stammen aus `09-BASISLAUF.md` (Kopf `head: 1d0df35da1842daec515b40dd62f8d918e240105`, erstellt 2026-10-09T06:24:00Z), nicht aus diesem Plan. Dieser Plan hat weder `alle.py` noch die volle pytest-Suite noch Playwright gestartet.

- Unveränderter Code seit dem Basislauf: `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline app daten scripts .github` endet mit Exit 0 (geprüft in diesem Plan, vor dem Schreiben).
- Pipeline (Basislauf Abschnitt „Pipeline“): `ruff check` und `ruff format --check` grün (51 Dateien), volle pytest-Suite `681 passed in 350.31s` ohne Skip (inklusive `test_port_wie_format_ts`), `alle.py --jahr 2026` Exit 0 in 29 s mit den Schritten 01, 02, 03, 04, Querschnitte, 05, 06, 07, 08 in dieser Reihenfolge, Prüfregeln 1 bis 10 grün (u. a. `Regel 4: grün (259 Werte)`, `Regel 5: grün (150 Werte)`, `Regel 9: grün (12 Werte)`, `Regel 10: grün (19 Werte)`, `Veraltete Befunde: 0`), anschließend `git diff --stat --exit-code -- daten app/src/data` und `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` leer.
- App (Basislauf Abschnitt „App (Scratch-Kopie)“): `type-check`, `lint`, `format:check` Exit 0, `npm run test` `Tests 2162 passed (2162)` in 49 Dateien, `npm run build` Exit 0.
- Playwright (Basislauf Abschnitt „Playwright“): Projekt `ci` `89 passed`, `mobil` `41 passed`, `texte` `1 passed`. Für Phase 4 relevant ist der Titel `e2e/smoke.spec.ts:138:5 › Smoke / › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten` (zitiert aus der Titelliste von `ci`): die gerenderten Erklärtexte tragen keinen offenen Platzhalter.

Eigene lesende Prüfungen dieses Plans, alle auf demselben Code (HEAD `b07d34f`):

- `uv run --directory pipeline pytest -p no:cacheprovider -q -rs tests/test_texte.py tests/test_formatiere.py`: `130 passed`, nach Einrichten von `app/node_modules` in der eigenen Worktree-Kopie ohne Skip (vorher `129 passed, 1 skipped`, der Skip war `test_port_wie_format_ts` wegen fehlendem `app/node_modules/typescript`, wie im Basislauf beschrieben).
- `pytest … tests/test_app_daten.py tests/test_manuell.py tests/test_stellenplan.py -k "personennamen or produkte_json or deterministisch or eingecheckt or meta_json or stellenplan or kl_knoten or zuschussbedarf or schuldenstand or lies_stellen"`: `56 passed, 62 deselected`.
- `pytest … tests/test_pruefung.py tests/test_produkte.py -k "regel5 or regel4_b4 or toleranz_je_regel or eckwerte_ohne or veralteter or regel10 or regel9 or keine_personennamen"`: `21 passed, 109 deselected`.
- `vitest run src/charts/__tests__/format.test.ts src/lib/__tests__/texte.test.ts` in einer Scratch-Kopie von `app/` (`mktemp`-Verzeichnis im Scratchpad, eigenes `npm ci`): `Test Files 2 passed (2)`, `Tests 51 passed (51)`.
- `verify.artifacts` für alle sechs Pläne: `all_passed: true` (9, 7, 5, 4, 4 und 5 Artefakte, also 34 von 34); `verify.key-links`: alle Links verifiziert bis auf das veraltete Muster von 04-05 (siehe Advisory im Kopf).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Alle Tabellen in `daten/manuell/` haben eine `quelle`-Spalte mit PDF-Seite, ein README begründet die Werte; Prüfregel 5 ist grün (Steuerarten gegen GEP Z. 01 B.4, Transfers 13.764 T€ B.5, Kita 559 T€); Zuwendungsdifferenz und Fußnote an 10.147 sind dokumentiert | ✓ VERIFIED | Alle zehn CSV-Dateien tragen `quelle` im Kopf (`head -1 daten/manuell/*.csv`: `eigenkapital`, `investitionszuwendungen`, `kita_zuschuesse`, `steuerarten`, `transferaufwendungen`, `ve_uebersicht`, `verbindlichkeiten`, `weitere_vorberichtstabellen`, `zuschuesse_lfd_zwecke`, `zuwendungen`); `daten/manuell/README.md` vorhanden (Spaltenbeschreibung `anmerkung`, `jahr`, Abschnitt „Kreisumlage, Fußnote (S. 46)“). Basislauf: `Regel 5: grün (150 Werte)` (vorher 133, die Mehrung stammt aus den Phasen 5 und 6), `Regel 4: grün (259 Werte)`; `konsistenz.md` Zeile Regel 5: 0 Abweichungen, 0 Lücken, 29 bekannte Befunde. Sollwerte in `pipeline/jahrgaenge/2026_sollwerte.toml:283-318`: Steuerarten-Gesamt 2026 = 18.443 T€, Transfers `gesamt = 13764`, `zuschuesse_kindertageseinrichtungen = 559`. Zuwendungsdifferenz: `befunde.md:162`, `gep_02` 2026, -4.200 €, Seite 28. Fußnote 10.147: README und `meta.json` (siehe Advisory im Kopf) |
| 2 | SC2: `meta.json` enthält Einwohner 11.741 (Stichtag, Quelle), Hebesätze 242/554/418 %, Fläche, Satzungsdatum, Kreisumlage brutto/netto, Kreisumlage-Hebesätze; `erklaerungen.md` enthält geprüfte Erklärtexte mit Seitenverweis (Schlüsselzuweisung, Gewerbesteuer, Kreisumlage) | ✓ VERIFIED | `daten/manuell/meta.json`: `einwohner.wert` 11741, `stichtag` 2024-06-30, `herkunft` IT.NRW, `quelle` 25; `hebesaetze` 242/554/418, Quelle 9; `flaeche` 8960 ha (S. 10); `satzung.beschluss` 2026-03-03, `ausfertigung` 2026-03-04; `kreisumlage.netto` 10.147.000 €, `rueckstellungsaufloesung` 1.325.478 €, `brutto` 11.472.478 € (berechnet, Formel `netto + rueckstellungsaufloesung`); Kreisumlage-Hebesätze als Promille: `hebesatz_kreisumlage` 363 (= 36,3 %), `hebesatz_jugendamtsumlage` 210 (= 21 %), beide mit Vorjahr (330 und 203). `erklaerungen.md`: 21 Abschnitte (die zehn ursprünglichen von `schluesselzuweisung` bis `nicht_im_haushalt` an den Zeilen 3 bis 57 plus elf aus den Phasen 5 und 6), `grep -c '^Quelle: S\.'` = 21, also je Abschnitt eine Quelle-Zeile; `schluesselzuweisung` (S. 28), `gewerbesteuer` (S. 27), `kreisumlage` (S. 46, S. 47). Du-Anrede: die zwei Treffer von „Sie“ (Zeilen 131 und 143) sind dritte Person („Diese Produkte … Sie brauchen“, „Sie zeigt“ für die App), `app/src/lib/__tests__/duanrede.test.ts` liegt im grünen Vitest-Lauf des Basislaufs |
| 3 | SC2b: Schuldenstand, Rücklagen, VE-Übersicht (S. 24/25, 309–311) liegen mit Quelle vor | ✓ VERIFIED | `daten/manuell/verbindlichkeiten.csv`, `eigenkapital.csv`, `ve_uebersicht.csv` vorhanden, jeweils mit `quelle`. Gegenprüfung in Regel 5 (`pruefe_regel5_schulden_ruecklagen_ve`, `pruefung.py:1873`, aufgerufen `pruefung.py:2699`); `04-SECURITY.md` T-04-06 (closed) führt `_pruefe_regel5_eigenkapital_summe`, `_pruefe_regel5_satzung_paragraf4`, `_pruefe_regel5_ve_uebersicht` mit den zugehörigen Tests; Basislauf Regel 5 grün |
| 4 | SC3: `stellenplan.csv` enthält Teil A (Beamte), Teil B (Tarif) und die Stellenübersicht nach PB mit Stellen 2026, 2025, besetzt 30.06.2025 und Vermerken; Beamtenstellen 2026 = 8 | ✓ VERIFIED | `daten/aufbereitet/stellenplan.csv`: 162 Zeilen plus Kopf, `teil` = beamte (37), nachwuchs (4), sozial_erziehungsdienst (8), tarif (113), `merkmal` stellen, beschaeftigt, vorgesehen, davon_ausgesondert, besetzt, Spalten `stichtag` und `vermerk` vorhanden; eigene Summe der sechs Beamtenzeilen 2026 ohne Produktbereich (merkmal `stellen`, S. 284) = 800 Hundertstel = 8 Stellen; Sollwert `[eckwerte.stellen_beamte] wert = 8` (`2026_sollwerte.toml:389`); Basislauf `Regel 9: grün (12 Werte)`, `Regel 10: grün (19 Werte)`, `Schritt 05: 162 Zeilen geschrieben` |
| 5 | SC4: `app/src/data/` enthält `haushalt.json`, `produkte.json`, `investitionen.json`, `stellenplan.json`; ein Test bestätigt, dass keine Personennamen enthalten sind; „Weitergabe an Kreis und Land“ ist eigene Kategorie, der Rest von PB 16 heißt „Allgemeine Finanzwirtschaft“; Zuschussbedarf je Knoten und Jahr als berechneter Wert gekennzeichnet | ✓ VERIFIED | Alle vier Dateien vorhanden und als JSON lesbar (`produkte.json` Array mit 63 Einträgen, `stellenplan.json` Schlüssel `haushaltsjahr`, `einheit_stellen`, `zeilen`); daneben `texte.json` und `quellen.json` aus den Phasen 4 und 7 (`beispieldaten.json` ist seit 96a23de entfernt und war nie eine der vier Pflichtdateien). Personennamen: `test_keine_personennamen_in_app_daten` und `test_produkte_json_ohne_personenfelder` liefen in der eigenen Auswahl grün (56 passed), `04-SECURITY.md` T-04-03, T-04-05, T-04-12. KL: `haushalt.json` `knoten` enthält genau einen Knoten „Weitergabe an Kreis und Land“ (`KL_NAME`, `app_daten.py:91`) und drei Knoten „Allgemeine Finanzwirtschaft“ (PB, PG, Produkt); Zuschussbedarf steht unter `berechnet` (`app_daten.py:332-336`), Tests `test_kl_knoten_gleich_tp_15`, `test_zuschussbedarf_summe_top_knoten` (in der Auswahl grün) |
| 6 | SC5: `alle.py` führt alle Schritte in Reihenfolge aus; die CI schlägt bei einem Diff auf eingecheckten Daten fehl | ✓ VERIFIED | `pipeline/alle.py`: `klassifiziere_seiten` (Z. 83), `extrahiere_plaene` (96), `extrahiere_produkte` (104), `extrahiere_investitionen` (115), `extrahiere_querschnitte` (124), `extrahiere_stellenplan` (131), `pruefe_alles` (141, rot beendet den Lauf, Z. 151-153), `erzeuge_app_daten` (156, nur nach grünem Bericht), `erzeuge_quellen` (171). Ausgabe im Basislauf zeigt dieselbe Reihenfolge, Exit 0, anschließend leerer `git diff` und leerer `git status`. `.github/workflows/ci.yml:46-60`: Schritt „Pipeline reproduzierbar (D-24)“ ruft `alle.py` auf, `git diff --stat --exit-code -- daten app/src/data` (Z. 50), Prüfung auf nicht verfolgte Dateien (Z. 51-54) und auf Änderungen unter `app/public/quellen` (Z. 59-62); Tests `test_alle.py` (Fehlerfälle je Schritt, `test_roter_bericht_ruft_app_daten_nicht_auf`) |
| 7 | Anforderungsabdeckung: alle 14 deklarierten IDs sind von einem Plan beansprucht und belegt | ✓ VERIFIED | Siehe Tabelle „Requirements Coverage“. Die REQUIREMENTS-Buchführung (alter Bericht, Abschnitt „Bookkeeping note“) ist erledigt: `.planning/milestones/v1.0-REQUIREMENTS.md` zeigt `grep -c '^- \[x\]'` = 85 und `grep -c '^- \[ \]'` = 0, alle 14 Zeilen der Phase 4 stehen in der Tracking-Tabelle auf `Complete` (Zeilen 204 bis 225) |
| 8 | Volle Pipeline-Testsuite grün, Lint und Format sauber, App-Prüfungen grün, Pipeline reproduzierbar | ✓ VERIFIED | Aus `09-BASISLAUF.md`: `681 passed in 350.31s (0:05:50)` ohne Skip (alter Bericht: 472), `ruff check` und `ruff format --check` (51 Dateien) grün, `alle.py` Exit 0 mit byte-identischer Ausgabe, App `type-check`, `lint`, `format:check`, `test` (2162), `build` Exit 0, Playwright `ci` 89, `mobil` 41, `texte` 1 grün. Seit dem Basislauf kein Codepfad geändert (`git diff --quiet 1d0df35 HEAD -- pipeline app daten scripts .github` Exit 0) |
| 9 | MANU-08/D-15: Jede Zahl in den Erklärtexten ist ein Platzhalter; kein nackter Ziffernlauf außer Seitenverweisen | ✓ VERIFIED | Heute strenger als im alten Bericht: `pruefe_text` (`texte.py:208`) lehnt HTML-Zeichen (Z. 220), getippte Jahreszahlen 19xx/20xx (Z. 245) und jede übrige Ziffer außerhalb von Platzhalter, § und S. (Z. 254) ab; Titel laufen über `pruefe_titel` (`texte.py:264`); `_pruefe_jahrbezug` (`texte.py:585`) bricht ab, wenn ein Wertschlüssel mit Jahressuffix nicht zum beschrifteten Jahr passt. Eigene Läufe: `tests/test_texte.py` und `tests/test_formatiere.py` `130 passed`; `04-SECURITY.md` T-04-16 und T-04-17 (closed). Keine `v-html` unter `app/src` in Vue-Dateien (`grep -rn "v-html" app/src --include=*.vue` ohne Treffer), Wächter `quelltext.test.ts` im Vitest-Lauf des Basislaufs |
| 10 | MANU-08/D-15: Jede Zahl in den Erklärtexten wird beim Rendern über `formatiere()` korrekt angezeigt (CR-01: kein „2.026“) | ✓ VERIFIED | `app/src/charts/format.ts`: `JAHR_FORMAT` mit `useGrouping: false` (Z. 21), `jahr()` (Z. 92), `'jahr'` in `FormatKuerzel` (Z. 141), `case 'jahr'` (Z. 169) und `default` mit `never`-Guard, der bei unbekanntem Kürzel wirft (Z. 177-180); `texte.py:31` `FORMATKUERZEL` mit `jahr` an gleicher Stelle; Namensraumregel `texte.py:233` (jeder `jahr.`-Platzhalter braucht das Kürzel `jahr`). Daten: in `erklaerungen.md` 14 Platzhalter `{{jahr.haushaltsjahr|jahr}}` und kein `{{jahr.…|zahl}}`; in `texte.json` (Texte und Glossar) 29 Platzhalter `jahr.haushaltsjahr|jahr`, 0 `jahr.*` mit `zahl`; `werte` enthält die Jahresschlüssel `jahr.haushaltsjahr`, `jahr.vorjahr`, `jahr.vorvorjahr`, `jahr.haushaltsjahr_plus_1`, `jahr.haushaltsjahr_plus_2`, `jahr.letztes_jahr` und `jahr.fest_2020` bis `jahr.fest_2025`. Verhalten: `test_port_wie_format_ts` rendert die echte `format.ts` über node und lief ohne Skip (eigener Lauf, `130 passed`, und Basislauf `681 passed, 0 skipped`); Vitest `format.test.ts` und `texte.test.ts` `51 passed` in der Scratch-Kopie |

**Score:** 10/10 Wahrheiten verifiziert (0 vorhanden, aber Verhalten ungeprüft)

### Deferred Items

Keine. Es gibt keine Lücke, die in einer späteren Phase des Meilensteins nachgeholt würde.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | Key-Link-Muster von Plan 04-05 veraltet (Import ohne Modulpräfix seit Phase 5), Verdrahtung intakt | other | Musterdrift im archivierten Plan, kein Codefehler; belegt durch `app_daten.py:63-67`, `:1112`, `:1124` |
| 2 | Fußnote an 10.147 steht in README und `meta.json`, in `befunde.md` nur als Regeltext der Prüfung `brutto_fussnote`, nicht als Tabellenzeile | other | Keine Abweichung zu dokumentieren; Prüfung läuft exakt und grün |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/src/charts/format.ts` | `formatiere()`/`FormatKuerzel` mit ungruppiertem `jahr` und Guard | ✓ VERIFIED | `JAHR_FORMAT` Z. 21, `jahr()` Z. 92, Union Z. 141, Dispatch Z. 158-180 |
| `pipeline/ostbevern/texte.py` | `FORMATKUERZEL` mit `jahr`, gleiche Reihenfolge wie die TS-Union | ✓ VERIFIED | `texte.py:31`; `test_formatkuerzel_wie_format_ts` grün |
| `daten/manuell/texte/erklaerungen.md` | Erklärtexte mit Quelle und Platzhaltern, Jahre als `jahr`-Kürzel | ✓ VERIFIED | 21 Abschnitte, 21 Quelle-Zeilen, 0 `|zahl` für `jahr.*` |
| `app/src/data/texte.json` | aus `erklaerungen.md` und `glossar.md` erzeugt, Rohwerte | ✓ VERIFIED | Basislauf: `alle.py` byte-identisch |
| `daten/manuell/README.md` | Begründung der Werte, Kürzel-Vokabular | ✓ VERIFIED | Abschnitt Spalten, Kreisumlage-Fußnote, Weitergabe |
| `pipeline/tests/test_formatiere.py` | Python-Port, Rendertests, CR-01-Mutationstest, Node-Gegenprobe | ✓ VERIFIED | in den 130 passed; Node-Test lief |
| `daten/aufbereitet/stellenplan.csv`, `app/src/data/stellenplan.json` | Stellenplan Teil A/B und Übersicht | ✓ VERIFIED | 162 Zeilen, Beamte 2026 = 8 |
| `app/src/data/haushalt.json`, `produkte.json`, `investitionen.json` | App-Daten ohne Personennamen | ✓ VERIFIED | vorhanden, Namenswächter grün |
| `.github/workflows/ci.yml` | Reproduzierbarkeitsprüfung (D-24) | ✓ VERIFIED | Z. 46-62 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `app/src/charts/format.ts` (`formatiere`) | `pipeline/ostbevern/texte.py` (`FORMATKUERZEL`) | `test_formatkuerzel_wie_format_ts` | ✓ WIRED | beide Listen: euro, mio, zahl, jahr, prozent, promille, vzae |
| `daten/manuell/texte/erklaerungen.md` | `app/src/data/texte.json` | Schritt 07: `lies_erklaerungen` (`app_daten.py:1112`), `loese_auf` (`:1124`) | ✓ WIRED | direkter Import `app_daten.py:63-67`; das Plan-Muster mit Modulpräfix ist veraltet (Advisory 1) |
| `app/src/data/texte.json` | echte `format.ts::formatiere()` | `test_port_wie_format_ts` | ✓ WIRED | lief ohne Skip |
| `pipeline/alle.py` | `app_daten.erzeuge_app_daten`, `stellenplan.extrahiere_stellenplan` | Aufrufe `alle.py:156`, `:131` | ✓ WIRED | Reihenfolge laut Basislauf |
| `.github/workflows/ci.yml` | `alle.py` | Schritt „Pipeline reproduzierbar (D-24)“ | ✓ WIRED | Z. 46-62 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `texte.json` `werte["jahr.haushaltsjahr"]` | 2026 | `textwerte()` aus `haushalt.json["haushaltsjahr"]` (`texte.py:471`) | Ja, `pruefe_texte_haushaltsjahr` vergleicht beide Felder | ✓ FLOWING |
| `formatiere(2026, 'jahr')` | „2026“ | `JAHR_FORMAT.format` | Ja, Vitest `format.test.ts` | ✓ FLOWING |
| `haushalt.json` `knoten`/`berechnet` | Zuschussbedarf je Knoten und Jahr | `baue_ergebnisplan` aus den geprüften Plänen (`app_daten.py:232`) | Ja, byte-identische Regeneration | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Texte und Formatierung | `uv run --directory pipeline pytest -p no:cacheprovider -q -rs tests/test_texte.py tests/test_formatiere.py` | `130 passed` | ✓ PASS |
| App-Daten, Meta, Stellenplan | `pytest … -k "personennamen or produkte_json or deterministisch or eingecheckt or meta_json or stellenplan or kl_knoten or zuschussbedarf or schuldenstand or lies_stellen"` | `56 passed, 62 deselected` | ✓ PASS |
| Regel 4, 5, 9, 10 und Befunde | `pytest … -k "regel5 or regel4_b4 or toleranz_je_regel or eckwerte_ohne or veralteter or regel10 or regel9 or keine_personennamen"` | `21 passed, 109 deselected` | ✓ PASS |
| Formatierung im Browser-Code | `vitest run src/charts/__tests__/format.test.ts src/lib/__tests__/texte.test.ts` (Scratch-Kopie) | `51 passed` | ✓ PASS |
| Codepfade seit Basislauf unverändert | `git diff --quiet 1d0df35 HEAD -- pipeline app daten scripts .github` | Exit 0 | ✓ PASS |

### Probe Execution

Step 7c: übersprungen, die Phase deklariert keine Probe-Skripte (`scripts/*/tests/probe-*.sh` kommen in den Plänen 04-01 bis 04-06 nicht vor).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| MANU-01 | 04-01 | `steuerarten.csv` | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-02 | 04-01 | `zuwendungen.csv` | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-03 | 04-01 | `transferaufwendungen.csv` | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-04 | 04-01 | `kita_zuschuesse.csv` | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-05 | 04-02 | `weitere_vorberichtstabellen.csv` | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-06 | 04-02 | `meta.json` | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-07 | 04-01, 04-02 | `quelle`-Spalte und README | ✓ SATISFIED | vorläufig, Task 2 |
| MANU-08 | 04-05, 04-06 | Erklärtexte mit Seitenverweis, korrekt gerendert | ✓ SATISFIED | vorläufig, Task 2 |
| PRUEF-05 | 04-01, 04-02 | Regel 5 grün | ✓ SATISFIED | vorläufig, Task 2 |
| EXTR-10 | 04-03 | Stellenplan extrahiert | ✓ SATISFIED | vorläufig, Task 2 |
| DATA-01 | 04-01, 04-03, 04-04, 04-05, 04-06 | App-JSON-Dateien | ✓ SATISFIED | vorläufig, Task 2 |
| DATA-02 | 04-04 | Weitergabe an Kreis und Land | ✓ SATISFIED | vorläufig, Task 2 |
| DATA-03 | 04-04 | Zuschussbedarf berechnet | ✓ SATISFIED | vorläufig, Task 2 |
| PRUEF-10 | 04-01, 04-03, 04-05, 04-06 | `alle.py` und CI-Diff | ✓ SATISFIED | vorläufig, Task 2 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (alle Dateien der Phase 4) | – | Debt-Marker `TBD`, `FIXME`, `XXX`, `TODO`, `HACK` | – | Keine Treffer in `app_daten.py`, `manuell.py`, `stellenplan.py`, `texte.py`, `schema.py`, `konfiguration.py`, `pruefung.py`, `alle.py`, `05_stellenplan.py`, `07_app_daten.py`, `format.ts`, `daten.ts`, `typen.ts`, `README.md`, `erklaerungen.md`, `test_formatiere.py` |

Die acht offenen Warnungen und Hinweise des alten Berichts (WR-01 bis WR-06, IN-01, IN-02) sind inzwischen alle behoben: `04-REVIEW-DISPOSITION.md` zeigt `open: 0`, `total: 9`, alle Zeilen `fixed` mit Commit (65cd6d8, 9d18267, e3a2122, d53ffc7, 7587fd5) und Test. Jeweils wieder belegt in `04-SECURITY.md` (T-04-14, T-04-15, T-04-16, T-04-18).

### Human Verification Required

Keine. Die Phase besteht aus einer headless Pipeline und statischen Daten; jede Wahrheit ist durch Code, Testlauf oder Basislauf belegt, kein Verhalten ist nur durch Präsenz geprüft.

### Gaps Summary

Keine Lücken. Die Phase-4-Wahrheiten gelten auch auf dem Endstand: Die Wächter und Tests, die Phase 5 bis 8 ergänzt haben, schärfen die Wahrheiten 1, 9 und 10, ohne Daten zu verändern (Basislauf: `alle.py` byte-identisch). Zwei Hinweise (Advisory im Kopf) betreffen nur die Dokumentation, nicht den Code.

---

_Verified: 2026-10-09T06:31:00Z_
_Verifier: Claude (gsd-verifier-Verfahren, ausgeführt in Plan 09-07)_
