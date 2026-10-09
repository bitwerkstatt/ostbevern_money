---
phase: "4"
slug: "manuelle-daten-und-app-daten"
status: draft
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 9
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
| T-04-01 | Tampering | `daten/manuell/*.csv` transcription | high | mitigate | pending (09-01 Task 2) | open |
| T-04-02 | Repudiation | `daten/pruefberichte/befunde.md` | medium | mitigate | pending (09-01 Task 2) | open |
| T-04-03 | Information Disclosure | `app/src/data/*.json` | high | mitigate | pending (09-01 Task 2) | open |
| T-04-04 | Tampering | `app/src/data/haushalt.json` determinism | medium | mitigate | pending (09-01 Task 2) | open |
| T-04-05 | Information Disclosure | `daten/manuell/meta.json` | high | mitigate | pending (09-01 Task 2) | open |
| T-04-06 | Tampering | eigenkapital/verbindlichkeiten/ve_uebersicht transcription | high | mitigate | pending (09-01 Task 2) | open |
| T-04-07 | Tampering | `[eckwerte]` Sollwerte | medium | mitigate | pending (09-01 Task 2) | open |
| T-04-08 | Tampering | per-rule tolerance change in befunde matching | medium | mitigate | pending (09-01 Task 2) | open |
| T-04-09 | Tampering | `stellenplan.py` value-to-row assignment | high | mitigate | pending (09-01 Task 2) | open |
| T-04-10 | Tampering | hundredths conversion | medium | mitigate | pending (09-01 Task 2) | open |
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
