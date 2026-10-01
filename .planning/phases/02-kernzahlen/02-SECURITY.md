---
phase: "2"
slug: "kernzahlen"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-01"
---

# Phase 2 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 2 is an offline data pipeline (PDF → CSV/Markdown, checked into git). There is no network surface, no authentication and no user input at runtime. The relevant threats are data integrity (wrong numbers published to citizens), false-green consistency checks, and disclosure of employee names.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Published PDF (`raw_data/haushalt-2026.pdf`) → `seiten.py` / `plaene.py` | Layout-dependent text; misreading publishes wrong numbers | Public budget figures; employee names on Produktinformationen pages (personal data, must not ship) |
| Jahrgangsdatei / Sollwertdatei (team-authored TOML) → `konfiguration.py` / `pruefung.py` | Regex patterns compiled at runtime; target values decide what counts as correct | Config, reviewed in git |
| `befunde.md` (human-edited Markdown) → `pruefung.py` | Can declare deviations as known and thereby turn red checks green | Documented deviations |
| `seiten.csv` / `hierarchie.csv` → `plaene.py`, Regel 2 | Node context and grouping decide which node a value belongs to | Derived structure |
| Generated CSV/MD → git → Phase 4 App-JSON | Checked-in data consumed by the public app | Public budget figures |
| `alle.py` / `06_pruefen.py` exit code, `konsistenz.md` → developer / CI / readers | Public claim that the numbers add up | Check result |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation (evidence) | Status |
|-----------|----------|-----------|----------|-------------|------------------------|--------|
| T-02-01 | Tampering (data integrity) | `plaene.lies_plantabelle` | high | mitigate | `PlaeneFehler` on missing/foreign column header and unknown row text (`ostbevern/plaene.py:38,165-177`); label check via `normalisiere_bezeichnung`; negative tests `test_gesamtergebnisplan_unbekannte_zeile_bricht_ab`, `…_falscher_text_bricht_ab`, `test_gesamtfinanzplan_falscher_spaltenkopf_bricht_ab` | closed |
| T-02-02 | Repudiation (false green) | `pruefung.pruefe_alles` | high | mitigate | Each rule reports `geprueft` count; missing values raise `PruefungsFehler` (`pruefung.py:80`); every rule incl. Regel 4 (`pruefung.py:594,623`) applies `TOLERANZ_EURO`; red report → exit 1 (`06_pruefen.py:45`, `alle.py:53`, `test_roter_bericht_beendet_mit_fehler`); +2 EUR detection proven for Regel 1/2/3 (`test_regel1_toleriert_einen_euro_sonst_rot`, `test_regel2_erkennt_manipulierte_produktzeile`, `test_regel3_erkennt_manipulierte_pb_zeile`). Residual: no dedicated +2 EUR manipulation test for Regel 4 itself (see audit note) | closed |
| T-02-03 | Tampering | `2026_sollwerte.toml` transcription | medium | mitigate | `lade_sollwerte` validates tables, keys and int types (`KonfigurationsFehler`, tests in `test_konfiguration.py` e.g. `test_sollwert_als_float_wird_abgelehnt`, `test_sollwertdatei_ohne_gesamtfinanzplan_meldet_schluessel`); Regel 4 compares 194 values every run | closed |
| T-02-04 | Information disclosure | `seiten.baue_hierarchie` names | medium | mitigate | Names must equal Anhang A (`test_anhang_a_eintraege_stimmen_mit_hierarchie_ueberein`); `grep -ciE "Verantwortlich\|Sachbearbeit"` on `hierarchie.csv` and `seiten.csv` = 0 | closed |
| T-02-05 | Tampering (data integrity) | `seiten.klassifiziere_dokument` | high | mitigate | `SeitenFehler` guards (`seiten.py:172-323`); start pages equal Anhang A (`test_anhang_a_eintraege_…`, `test_produktseiten_in_seiten_csv_stimmen_mit_anhang_a`); 0 unbekannt pages for 2026 | closed |
| T-02-06 | DoS / Tampering | Kopfzeilen regexes from TOML | low | mitigate | Patterns compiled in `lade_jahrgang` (`konfiguration.py:267`) with `KonfigurationsFehler`; file reviewed in git | closed |
| T-02-07 | Repudiation (masked errors) | `pruefung.gleiche_befunde_ab` | high | mitigate | Key + amount match within 1 EUR (D-05), unused entries `veraltet` make report non-green (`pruefung.py:171,323-354`); tests `test_befund_deckt_abweichung_innerhalb_toleranz_ab`, `test_veralteter_befund_*` (3) | closed |
| T-02-08 | Tampering | `pruefung.lies_befunde` | medium | mitigate | Strict parser (`pruefung.py:230-316`): heading, header, cell count, int, \|abweichung\| > 1, non-empty Begründung; tests `test_kaputte_schluesseltabelle_*` (6) | closed |
| T-02-09 | Tampering (data integrity) | Finanzplan column mapping | high | mitigate | Columns by x order vs. `spalten['finanzplan']`; `test_gesamtfinanzplan_trifft_sollwerte_b2` (Ansatz and VE vs. Anhang B.2), `test_pb_teilfinanzplan_hat_sieben_spalten` | closed |
| T-02-10 | Tampering (data integrity) | `plaene.lies_abschnitte` / `lies_teilplaene` | high | mitigate | Duplicate-row and completeness checks raise `PlaeneFehler` (`plaene.py:389,436`); Regel 1 on every node (6593 values green); `test_teilfinanzplan_fortsetzung_auf_folgeseite` | closed |
| T-02-11 | Tampering (invented values) | synthetic PG rows | medium | mitigate | Rows copied only from the single child product, flagged `synthetisch` (`plaene.py:481`); `test_synthetische_pg_ist_kopie_ihres_einzigen_produkts`, `test_synthetische_pg_markierung_und_namen`; declared PG validated (D-08) | closed |
| T-02-12 | Information disclosure | Erläuterung text on product pages | low | accept | Erläuterungen only terminate a section (`plaene.py:146`); CSV schema has no text column beyond `zeile_name` — see Accepted Risks | closed |
| T-02-13 | Tampering (data integrity) | Regel 2 / Regel 3 aggregation | high | mitigate | Two-level Regel 2 (7994 values) and Regel 3 (114 values) green; manipulation tests for both, `test_regel3_ignoriert_tp_27_28` | closed |
| T-02-14 | Repudiation (false success) | `alle.py`, `06_pruefen.py` | high | mitigate | `typer.Exit(code=1)` on step exception and red report (`alle.py:48-79`, `06_pruefen.py:33,45`); `test_roter_bericht_beendet_mit_fehler`, `test_schrittfehler_beendet_mit_fehler` | closed |
| T-02-15 | Tampering | Non-deterministic regeneration | medium | mitigate | Sorted output, atomic report write via temp file + `os.replace` (`pruefung.py:917-928`); `alle.py --jahr 2026` leaves `git status --porcelain daten/` empty (re-verified 2026-10-01) | closed |
| T-02-SC | Tampering | Python dependencies | low | mitigate | `git diff f6797a4c^ HEAD -- pipeline/pyproject.toml pipeline/uv.lock` empty for the whole phase | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-02-01 | T-02-12 | Erläuterung free text is never written to Phase 2 outputs; Phase 3 extracts it under its own threat review (Datenschutz: names must not ship) | Plan 02-04 threat model (disposition `accept`) | 2026-10-01 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-01 | 16 | 16 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 grep-depth; auditor skipped per short-circuit rule) |

**Audit note (non-blocking):** T-02-02's plan text promised "a +2 EUR manipulation turns Regel 4 rot". Regel 4 uses the same `TOLERANZ_EURO` comparison as Regel 1–3, whose +2 EUR detection is tested, and red reports are proven to exit 1 — but no test manipulates a Regel-4 (Sollwert) value directly. Candidate for a follow-up test (`test_regel4_erkennt_manipulierten_wert`).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-01
