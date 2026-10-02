---
phase: "3"
slug: "details"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-02"
---

# Phase 3 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 3 extends the offline data pipeline (PDF → CSV/JSON/Markdown, checked into git) with Haushaltsquerschnitte, Investitionsmaßnahmen, VE-Fälligkeiten, Produktinformationen, Erläuterungen and Grundzahlen. It has no network surface, no authentication and no runtime user input. The relevant threats are data integrity (wrong numbers published to citizens), false-green consistency checks, and disclosure of staff names printed on the Produktinformationen pages.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PDF pages 291-300 → `querschnitte.py` | Semi-trusted layout that can deviate (titles, wraps, page breaks) | Public budget figures |
| PDF investment tables → `investitionen.py` | Semi-trusted layout with glued text, wraps, two tables on one page | Public budget figures |
| PB-list pages → `investitionen.py` | Second printed copy of the measures with its own layout quirks | Public budget figures (control data) |
| PDF Produktinformationen → `produkte.py` | Personal data (staff names) next to public product data | Personal data (must not ship), public text |
| PDF Grundzahlen tables → `produkte.py` | Semi-trusted layout with footnotes, stamps, groups and decimals | Public key figures |
| `querschnitte.csv` / `investitionen_pb.csv` → `pruefung.py` (Regel 6/7) | Control data that decides whether the extracted plans are believed | Derived figures |
| `investitionen.csv`, `grundzahlen.csv`, `produkte.json` → Phase 4/5 app | Citizens see amounts, categories and partial-year values | Public budget figures |
| `erlaeuterungen.csv` → spreadsheet users | CSV may be opened in office software | Public budget text |
| `daten/` → public GitHub repository | Every checked-in byte is published | Everything above |
| test/CI output → CI logs | Logs of a public repository are public | Error messages, assertion output |
| `konsistenz.md` / `alle.py` exit code → developer, CI, readers | Public claim that the numbers add up and are complete | Check result |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation (evidence) | Status |
|-----------|----------|-----------|----------|-------------|------------------------|--------|
| T-03-01 | Tampering (data integrity) | Regel 7 mapping, `befunde.md` | high | mitigate | `REGEL7_KENNZAHLEN` (`pruefung.py:96-115`, `ergebnis_teilhaushalt` → Z. 26); unknown Kennzahl aborts (`pruefung.py:1151-1153`); stale befunde block green (`pruefung.py:228`); `befunde.md` restricts entries to printed deviations with page refs. Tests `test_regel7_erkennt_manipulierten_querschnitt` (+2 rot), `test_regel7_toleriert_einen_euro` (+1 grün), `test_regel7_veralteter_befund_macht_bericht_rot` | closed |
| T-03-02 | Tampering | `querschnitte.py` column/block reading | high | mitigate | Anchors from each block header (`querschnitte.py:165-177`), `ordne_spalten` + exact amount count (`:240-251`), PG-in-PB check (`:234-238`), completeness vs. hierarchie (`:284-314`); every abort names the PDF page. Tests `test_querschnitte_bricht_ab_*` (5), `test_querschnitte_vollstaendigkeit_*` (3), `test_spalten.py` (6). Abort behaviour preserved after review fix WR-01 (see audit note) | closed |
| T-03-03 | Repudiation (false success) | `pruefung.py` / `alle.py` exit code | medium | mitigate | `test_pruefung_liest_kein_pdf` (AST check); `alle.py:107-111,125-127` and `06_pruefen.py:43-45,74-75` exit 1 on `QuerschnitteFehler` and red report; `test_querschnittfehler_beendet_mit_fehler`, `test_roter_bericht_beendet_mit_fehler` | closed |
| T-03-04 | Tampering (data integrity) | Kassenwirksamkeit values | high | mitigate | Placed via `ordne_spalten`, abort outside Planung columns (`investitionen.py:443-478`), written only to `ve_faelligkeiten.csv` (`:841-851`); Regel 6(d) sum = VE (`pruefung.py:1078-1118`). Tests `test_kassenwirksamkeit_unter_falscher_spalte_bricht_ab`, `…_ohne_vorherige_kontozeile_bricht_ab`, `test_ve_faelligkeiten_nur_planung_jahr_und_summe_stimmt_mit_investitionen`, `test_regel6_erkennt_manipulierte_faelligkeit` | closed |
| T-03-05 | Tampering | Kontengruppen mapping, Finanzierungskonten | high | mitigate | Unknown Kontengruppe aborts (`investitionen.py:104-114`); 692/792 Gegenprobe vs. TFP Z. 33/35 before any write (`_pruefe_finanzierungskonten`, `:708-752`, called `:853-863,898-908`). Tests `test_unbekannte_kontengruppe_bricht_ab`, `test_unbekanntes_konto_in_tabelle_bricht_ab`, `test_csv_hat_keine_konten_der_gruppe_692_792`, `test_pb_liste_summe_trifft_sollwerte_und_keine_finanzierungskonten` | closed |
| T-03-06 | Tampering | ID/name split, block attribution | medium | mitigate | ID from Saldo line, header must start with it (`investitionen.py:598-616`, `_teile_bis_ziel` `:208-231`); Saldo/Summenzeile/Saldo-Investitionstätigkeit checks (`:339-362,537-564,644-663`); Regel 6 per product and total (`pruefung.py:1013-1069`). Tests `test_massnahme_id_entspricht_saldo_zeile_mit_praefixkollision`, `test_manipulierter_betrag_bricht_saldo_check`, `test_regel6_erkennt_manipulierten_investitionswert` | closed |
| T-03-07 | Tampering (data integrity) | Product-page extraction missing/duplicating a measure | high | mitigate | PB-Gegenprobe per (pb, massnahme_id, konto, jahr, wertart) plus Lücken (`pruefung.py:852-962`); Lücken turn the rule rot (`:205-212`) and are never excused by befunde (`:415-430`). Tests `test_regel6_pb_liste_erkennt_manipulierten_wert`, `test_luecke_wenn_massnahme_nur_auf_produktseiten`, `…_nur_in_pb_liste`, `test_wende_befunde_an_erhaelt_luecken_unveraendert` | closed |
| T-03-08 | Information disclosure / scope | PB-list data leaking into app sources | low | mitigate | `investitionen_pb.csv` under `daten/zwischen/` (`schema.py:37`), separate row list (`investitionen.py:865-896`); `test_pb_liste_laesst_investitionen_csv_byte_identisch` | closed |
| T-03-09 | Information disclosure | `produkte.py` / `produkte.json` / `daten/` (staff names) | high | mitigate | `PERSONENFELDER` (`produkte.py:73`) popped right after `zerlege_felder` (`:923-925`); exact-key check on write and read (`schema.py:312-321,343-346`); `test_keine_personennamen` scans all of `daten/`. Independent audit scan: no leak (see audit note) | closed |
| T-03-10 | Information disclosure | Error messages, test output, CI logs, SUMMARY, commits | medium | mitigate | No `ProdukteFehler`/`SchemaFehler` message can carry a person-field value; privacy test asserts on (path, count) pairs only; pytest without `--showlocals`. History scan over all commits, blobs and messages: no staff names (see audit note) | closed |
| T-03-11 | Tampering (CSV formula injection) | `erlaeuterungen.csv` text cells | low | accept | Verbatim public budget text; escaping would alter wording — see Accepted Risks | closed |
| T-03-12 | Tampering (data integrity) | Erläuterung attribution to plan lines | medium | mitigate | `pruefe_plausibilitaet` (`produkte.py:748-794`) runs before any write (`:957`). Tests `test_pruefe_plausibilitaet_erkennt_fehlende_zeile`, `…_erkennt_zu_grossen_posten`, `…_gruen_auf_echten_daten`, `test_stichprobe_erlaeuterung_posten` (S. 152), `test_stichprobe_erlaeuterung_ohne_zu_nr` (S. 184) | closed |
| T-03-13 | Tampering (data integrity) | Grundzahlen values, units, hints | medium | mitigate | Word outside the three column zones aborts (`produkte.py:324-349`); stamp/value placement via `ordne_spalten` (`:427-438,466-478`); strict decimal parsing, "–" → None, never a row (`zahlen.py:55-81`, `produkte.py:477`). Tests `test_grundzahlen_wert_ausserhalb_der_spalten_bricht_ab`, `test_grundzahlen_manipuliertes_wort_bricht_mit_seite_ab`, `test_stichprobe_grundzahl_*` (5), `test_lies_kennzahl_*` | closed |
| T-03-14 | Repudiation (false completeness) | Regel 8 | medium | mitigate | Every Regel-8 gap becomes a Lücke (`pruefung.py:1220-1336`), Lücken turn the report rot and cannot be excused by befunde; 10 `test_regel8_*` tests | closed |
| T-03-15 | Information disclosure | `daten/` incl. `grundzahlen.csv` | high | mitigate | Grundzahlen parsing skips everything before the bold Grundzahlen header, reset per page (`produkte.py:384,396-413`); `test_keine_personennamen` runs after regenerating all outputs; regenerated `daten/` byte-identical to the checked-in tree | closed |
| T-03-SC | Tampering | Python dependencies | low | mitigate | No phase-3 commit touches `pipeline/pyproject.toml` or `pipeline/uv.lock`; diff over the phase is empty | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-03-01 | T-03-11 | Erläuterung and Grundzahlen text is verbatim public budget text consumed by the pipeline and app; escaping would alter the wording. Checked at audit time: 0 of 229 `erlaeuterungen.csv` text cells and 0 of 827 `grundzahlen.csv` rows start with `=`, `+`, `-`, `@`, TAB or CR | Plan 03-04 threat model (disposition `accept`), 03-RESEARCH.md | 2026-10-02 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-02 | 16 | 16 | 0 | /gsd-secure-phase (gsd-security-auditor, ASVS L1, deeper checks on WR-01 and T-03-10) |

**Audit note — WR-01 (`ordne_spalten` per-anchor tolerance, commit `e842ff3`):** Old and new code were run side by side on edge cases. Both abort on midpoint words, words on or near duplicated anchors, two words claiming one anchor, more words than anchors, and words beyond the outer anchors. The only behavioural change is that a word clearly nearest one anchor under uneven spacing is now accepted instead of aborting, and it always lands on the same nearest column. On the 2026 PDF (273 Grundzahlen, 785 Investitionen, 128 Querschnitte calls) no real word falls into the newly accepted range, and output is unchanged.

**Audit note — T-03-09/T-03-10 leak scan (no names recorded here):** 967 working-tree files, 418 git blobs across all 175 commits and all commit messages were scanned for 104 whole person-field values, 192 name word pairs and 94 single words taken from the PDF. Whole values: 0 hits. Words that occur in the PDF only inside person fields: 0 hits in project files or history. One word-pair hit in `produkte.json`/`erlaeuterungen.csv` is a public service unit of the Kreis Warendorf (PDF pages 35, 100, 341), not a person.

**Non-blocking hardening candidates (follow-up tests):**
1. T-03-09: `test_keine_personennamen` matches whole field values; 38 of 126 values list several people without separators, so a partial leak of one person would pass. Add per-person word pairs as needles.
2. T-03-05: the TFP Z. 33/35 mismatch abort (`investitionen.py:741-752`) has no direct test; `test_pb16_finanzierungskonto_manipuliert_bricht_ab` aborts earlier at the Saldo check. The check covers the 6 budget columns, not 7 as planned (deviation documented in 03-02-SUMMARY).
3. T-03-14: the `leistungen` and `pdf_seiten` branches of Regel 8 (`pruefung.py:1291-1308`) have no manipulation test.
4. T-03-03: `test_pruefung_liest_kein_pdf` would not catch `from ostbevern import pdf` or imports of `produkte`, `investitionen`, `seiten`, `plaene`.
5. WR-01: the new regression test covers only the accepting case; add a negative test (a word on a duplicated anchor must still abort).
6. T-03-04: no direct test that Kassenwirksamkeit values are absent from `investitionen.csv` (kept out structurally and caught by Regel 6).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-02
