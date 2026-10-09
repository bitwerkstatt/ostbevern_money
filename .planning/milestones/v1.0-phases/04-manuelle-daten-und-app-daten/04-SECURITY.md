---
phase: "4"
slug: "manuelle-daten-und-app-daten"
status: draft
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 4
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-09"
---

# Phase 4 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 4 turns the extracted PDF data into the dataset the app ships: hand-transcribed tables (`daten/manuell/`), the Stellenplan parser, the app JSON files in `app/src/data/` and the curated explanation texts with their placeholders. It has no network surface, no authentication and no runtime user input. The relevant threats are data integrity (wrong numbers published to citizens), false-green consistency checks, disclosure of personal names that stand next to public data in the PDF, and text that could carry markup into the app.

This register was written after phase 8 (plan 09-01, D-01): every row names the code location as it stands now and tests that ran green without a skip in the runs of that plan. Claims of the phase-4 plans were re-checked against the code, not copied.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PDF → hand transcription | A person copies printed numbers into `daten/manuell/`; typos enter citizen-facing data here | Public budget figures (Schulden, Rücklagen, VE, Eigenkapital, meta values) |
| PDF S. 9 → `meta.json` | The Satzung page carries names of natural persons next to the dates that are transcribed | Dates (public), names of persons (must not ship) |
| Sollwerte TOML → Prüfung | A Sollwert that no rule consumes would silently stop protecting a value | Public reference values |
| PDF S. 284–290 → Stellenplan parser | Untrusted layout (sparse rows, offset baselines, wrapped labels) is turned into structured data | Public Stellen figures |
| `stellenplan.csv` → app | Published Stellen figures for the Stellenplan page | Public Stellen figures, Amtsbezeichnungen, Gruppen |
| `daten/` → `app/src/data/` | Schritt 07 publishes the complete citizen-facing dataset that GitHub Pages serves to everyone | Everything below |
| `produkte.json` (phase 3) → app | Records that originally had person fields cross into published data | Public product text, no staff names |
| `erklaerungen.md` → Schritt 07 → `texte.json` → app | Hand-written text is parsed, its placeholders are resolved against data and rendered as text in the browser | Public budget texts, numbers via `formatiere()` |
| pytest → node subprocess | The test executes the repo's `format.ts` with the installed `app/node_modules/typescript` | Placeholder/format pairs as JSON on stdin |
| repo → CI | CI re-runs the pipeline and must detect any divergence from committed data | Byte-identical `daten/` and `app/src/data/` |
| Package registries → build | npm / PyPI installs | Supply chain (no dependency added in phase 4) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-04-01 | Tampering | `daten/manuell/*.csv` transcription | high | mitigate | Regel 5 stage (a) sums the posts against the printed Gesamt and stage (b) compares against the GEP line in `_pruefe_regel5` (`pipeline/ostbevern/pruefung.py:1412`); Regel 4 B.4 checks `steuerarten.csv` against the independent second transcription in `_pruefe_regel4_b4` (`pruefung.py:870`, Sollwerte `pipeline/jahrgaenge/2026_sollwerte.toml:288`). No phase-8 change to `pruefung.py` (`git diff --stat 93b0a61..HEAD` is empty for it). Tests `test_regel5_stufe_a_erkennt_tippfehler`, `test_regel4_b4_erkennt_tippfehler_in_steuerarten` (both build a manipulated tmp copy and expect rot; green in the 09-01 run, 0 skipped) | closed |
| T-04-02 | Repudiation | `daten/pruefberichte/befunde.md` | medium | mitigate | `_wende_befunde_an` (`pruefung.py:484`, called `pruefung.py:2746`) matches every deviation of every rule against `daten/pruefberichte/befunde.md`; an unused finding lands in `veraltete_befunde` and `ist_gruen` turns false (`pruefung.py:277`), the report lists it under Veraltete Befunde (`pruefung.py:2838`). Tests `test_veralteter_befund_wenn_abweichung_nicht_mehr_passt`, `test_veralteter_befund_ohne_passende_abweichung`, `test_veralteter_befund_macht_bericht_nicht_gruen` | closed |
| T-04-03 | Information Disclosure | `app/src/data/*.json` | high | mitigate | Builder emits only the allowlisted keys `APP_PRODUKT_SCHLUESSEL` (`pipeline/ostbevern/app_daten.py:417`), any other key set aborts with `AppDatenFehler` (`app_daten.py:486`); the PDF-derived name scan walks `APP_DATEN_WURZEL.rglob` over `*.json` (`pipeline/tests/test_app_daten.py:147`) and so covers every app JSON file. Phase 8 deleted `beispieldaten.json` (96a23de, no change to the scan). Tests `test_keine_personennamen_in_app_daten`, `test_produkte_json_ohne_personenfelder` (green, 0 skipped) | closed |
| T-04-04 | Tampering | `app/src/data/haushalt.json` determinism | medium | mitigate | `schreibe_app_json` writes via temp file plus `os.replace`, UTF-8 without BOM, LF, fixed key order, trailing newline (`pipeline/ostbevern/app_daten.py:707-720`); `schreibe_produkte_json` does the same (`pipeline/ostbevern/schema.py:366-393`). CI step Pipeline reproduzierbar (D-24) re-runs `alle.py` and fails on any diff or untracked file in `daten` and `app/src/data` (`.github/workflows/ci.yml:46-52`); phase 8 changed only three comment lines of `ci.yml` (`git diff 93b0a61 HEAD`). Tests `test_app_json_deterministisch`, `test_haushalt_json_eingecheckt_aktuell` | closed |
| T-04-05 | Information Disclosure | `daten/manuell/meta.json` | high | mitigate | Evidence is the strict allowlist, not the name scan: `lies_meta_json` (`pipeline/ostbevern/manuell.py:114`) rejects unknown top-level keys against `_META_TOP_SCHLUESSEL` (`manuell.py:28`, check `manuell.py:128-135`) and unknown `satzung` fields against `_META_SATZUNG_SCHLUESSEL` (`manuell.py:44`, only `beschluss` and `ausfertigung`, applied `manuell.py:140`); the signatures on PDF S. 9 are deliberately not transcribed (`daten/manuell/README.md:217-219`). A throwaway probe in 09-01 added `satzung.kaemmerin` to a copy of `meta.json` and `lies_meta_json` aborted with unbekannte Felder. Tests `test_meta_json_bricht_ab` (9 cases, among them unknown top-level key and unknown leaf field), `test_meta_json_gueltig`. The name scan `test_keine_personennamen` over all of `daten/` (`pipeline/tests/test_produkte.py:218`) only complements this, because its needles come from the product person fields, not from the Satzung page (RESEARCH Pitfall 5) | closed |
| T-04-06 | Tampering | eigenkapital/verbindlichkeiten/ve_uebersicht transcription | high | mitigate | Regel 5 cross-checks the transcribed tables: Eigenkapital sum against the printed Gesamt (`_pruefe_regel5_eigenkapital_summe`, `pruefung.py:1583`), Satzung § 4 against Eckwerte and GEP Z. 28 (`_pruefe_regel5_satzung_paragraf4`, `pruefung.py:1681`), VE-Gesamtbetrag against GFP-VE and `ve_faelligkeiten.csv` with a Luecke for unpaired entries (`_pruefe_regel5_ve_uebersicht`, `pruefung.py:1769`), orchestrated by `pruefe_regel5_schulden_ruecklagen_ve` (`pruefung.py:1873`, called `pruefung.py:2699`). No phase-8 change to `pruefung.py`. Tests `test_regel5_d11_gruen`, `test_regel5_ve_uebersicht_luecke_bei_fehlendem_paar`, `test_schema_verbindlichkeiten_kanonisch`, `test_schema_eigenkapital_kanonisch`, `test_schema_ve_uebersicht_kanonisch` | closed |
| T-04-07 | Tampering | `[eckwerte]` Sollwerte | medium | mitigate | `pruefe_eckwerte_konsumiert` (`pruefung.py:1318`) raises `PruefungsFehler` for any `[eckwerte.*]` name that neither Regel 5 nor Regel 9 consumes; `pruefe_alles` calls it before the rules run (`pruefung.py:2664`). Test `test_eckwerte_ohne_pruefung_bricht_ab` | closed |
| T-04-08 | Tampering | per-rule tolerance change in befunde matching | medium | mitigate | `TOLERANZ_EURO = 1` (`pruefung.py:85`), `TOLERANZ_JE_REGEL` with exact 0 only for rules 9 and 10 (`pruefung.py:92`), `toleranz_fuer` is the single lookup (`pruefung.py:95-97`); the 1-€ tolerance of rules 1 to 8 is unchanged since phase 4 and was not weakened in phase 8 (`pruefung.py` untouched). Test `test_toleranz_je_regel` | closed |
| T-04-09 | Tampering | `stellenplan.py` value-to-row assignment | high | mitigate | `_TOP_TOLERANZ = 8.0` (`pipeline/ostbevern/stellenplan.py:40`) bounds the nearest-top assignment (`stellenplan.py:338`), two equally near groups abort (`stellenplan.py:343`), the printed Insgesamt row is cross-checked against the sum of the rows (`stellenplan.py:357-376`); Regel 10 compares Stellenübersicht against Teil A/B exactly (`_pruefe_regel10`, `pruefung.py:2046`), Regel 9 checks `stellen_beamte` = 8 exactly (`REGEL9_ECKWERTE` `pruefung.py:1299`, `_pruefe_regel9` `pruefung.py:1997`, Sollwert `2026_sollwerte.toml:389`). Tests `test_stellenplan_manipulierte_insgesamt_bricht_ab`, `test_stellenplan_wert_ohne_gruppe_innerhalb_toleranz_bricht_ab`, `test_stellenplan_uebersicht_manipulierte_summe_zeile_bricht_ab`, `test_stellenplan_csv_eingecheckt_aktuell`, `test_regel10_gruen_wenn_summen_uebereinstimmen` | closed |
| T-04-10 | Tampering | hundredths conversion | medium | mitigate | `lies_stellen_hundertstel` (`stellenplan.py:51-72`) works on the printed string only (no float), `_STELLENWERT_MUSTER` allows at most two decimals (`stellenplan.py:47`) and anything else raises `StellenplanFehler` (`stellenplan.py:62`). Tests `test_lies_stellen_hundertstel` (including 6,9 and 8), `test_lies_stellen_hundertstel_ungueltig` | closed |
| T-04-11 | Information Disclosure | `stellenplan.csv` / `stellenplan.json` | low | accept | pending (09-01 Task 3) | open |
| T-04-12 | Information Disclosure | `app/src/data/produkte.json` | high | mitigate | pending (09-01 Task 3) | open |
| T-04-13 | Tampering | KL split arithmetic | high | mitigate | pending (09-01 Task 3) | open |
| T-04-14 | Tampering | Schuldenstand Fortschreibung | medium | mitigate | pending (09-01 Task 3) | open |
| T-04-15 | Tampering | placeholder resolution (`loese_auf`) | medium | mitigate | pending (09-01 Task 3) | open |
| T-04-16 | Tampering | numbers typed into texts | high | mitigate | Digit rule and year rule in `pruefe_text`: HTML characters `pipeline/ostbevern/texte.py:220`, hand-typed year 19xx/20xx `texte.py:245` (pattern `texte.py:45`), any remaining digit outside placeholder, § and S. `texte.py:254`; titles go through the same rules via `pruefe_titel` (`texte.py:264`). Real-file guards run `pruefe_text` over `erklaerungen.md` and the Glossar. Tests `test_pruefe_text_ungueltig`, `test_pruefe_text_lehnt_getippte_jahreszahl_ab`, `test_pruefe_text_1990er_trifft_die_allgemeine_ziffernregel`, `test_erklaerungen_keine_nackten_ziffern`, `test_glossar_keine_nackten_ziffern` (all green in the 09-01 run, 0 skipped). Phase 8 verschärft: Jahreszahlen keine Ausnahme mehr (27e0be7, 7d4be31, Test 57063a0), Division durch 0 (c1da62e) | closed |
| T-04-17 | Spoofing / XSS precursor | `texte.json` rendered later | medium | mitigate | pending (09-01 Task 3) | open |
| T-04-18 | Tampering (integrity of published numbers) | `formatiere()` / placeholder Formatkürzel for year values | high | mitigate | pending (09-01 Task 3) | open |
| T-04-19 | Tampering | Approved Erklärtext wording altered during the suffix change (bypassing D-17) | medium | mitigate | pending (09-01 Task 3) | open |
| T-04-20 | Elevation of privilege | pytest spawning node with code from `app/node_modules` | low | accept | pending (09-01 Task 3) | open |
| T-04-SC | Tampering | npm/pip installs | high | mitigate | pending (09-01 Task 3) | open |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on severity count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

wird in 09-01 Task 3 gefüllt

---

## Security Audit Trail

wird in 09-01 Task 3 gefüllt

---

## Sign-Off

wird in 09-01 Task 3 gefüllt
