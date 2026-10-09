---
phase: "08"
slug: "fixes-und-triage"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-07"
---

# Phase 08 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Curated texts → pipeline → texte.json | Hand-written explanation texts are rendered into shipped JSON | Public budget texts (integrity, no secrets) |
| Jahrgang config → pipeline | TOML configuration drives extraction counts and paths | Public configuration |
| URL query → Maßnahmen filter | Visitor-controlled `?pb=` parameter | Untrusted query string (allowlisted) |
| Package registries → build | npm / PyPI installs | Supply chain (no new packages in this phase) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-08-01 | Tampering | `pruefe_titel` / ErklaerText titles | medium | mitigate | `def pruefe_titel` in `pipeline/ostbevern/texte.py`; pytest (08-01) | closed |
| T-08-02 | Tampering | `pruefe_text` year rule | medium | mitigate | Year detector in `texte.py`, boundary tests 1900/2099 (08-01) | closed |
| T-08-03 | Tampering | `festes_jahr` resolver | low | mitigate | `jahr.fest_JJJJ` only, other keys fail in `loese_auf` (08-01) | closed |
| T-08-04 | Tampering (statement integrity) | `lesehilfeSatz` | medium | mitigate | Four cases, „genau“ only in case D; `geldfluss.test.ts` (08-02) | closed |
| T-08-05 | Tampering (statement integrity) | `minderaufwandBetrag` | medium | mitigate | Positive Z. 27 throws, used by both consumers; `berechnung.test.ts` (08-02) | closed |
| T-08-06 | Tampering (integrity) | `einwohnerZahl` / EbenenTabelle | medium | mitigate | `export function einwohnerZahl` throws on missing value; `einwohner.test.ts` (08-03) | closed |
| T-08-07 | Repudiation (provenance) | Stellenplan source lines | low | mitigate | `berechnet` + `herleitung` per tile in `StellenplanPage.vue`; quellen.json unchanged (08-03) | closed |
| T-08-08 | Tampering | Tooltip/label strings | low | accept | Constant prefix + `Intl` output only; `htmlSicher` in `charts/tooltip.ts` unchanged (08-04) | closed |
| T-08-09 | Repudiation (provenance) | „Zusammen“ row, filter sum | low | mitigate | `zusammen().berechnet` drives label in `zuschuesse.ts`; filter sum labelled (08-05) | closed |
| T-08-10 | Tampering | `aria-labelledby` ids | low | mitigate | `useId()` in `DatenTabelle.vue`; Playwright asserts caption reference (08-06) | closed |
| T-08-11 | Denial of Service (AT users) | Drawer focus | low | mitigate | `setTimeout` focus to h1 in `App.vue`; Playwright mobil + ci (08-06) | closed |
| T-08-12 | Tampering (guard bypass) | `rdregel.test.ts` | low | mitigate | Comment stripping, probes, minimum file count, fail-first run (08-07) | closed |
| T-08-13 | Tampering | `lade_jahrgang` anzahlen | low | mitigate | `wert < 0` rejected in `konfiguration.py`; pytest per key (08-08) | closed |
| T-08-14 | Denial of Service | Rücklagen formula division | low | mitigate | `anfang == 0` raises `TexteFehler` in `texte.py` (08-08) | closed |
| T-08-15 | Information Disclosure | CLAUDE.md / ci.yml comments | low | accept | Only public repo name and commands written (08-08) | closed |
| T-08-16 | Tampering (shipped data) | Deletion of `beispieldaten.json` | low | mitigate | No importer under `app/src`; file absent; alle.py does not recreate it (08-09) | closed |
| T-08-17 | Tampering (number integrity) | Shared index helper | low | mitigate | `export function haushaltsjahrIndex` throws instead of `indexOf` −1; alle.py byte-identical (08-10) | closed |
| T-08-18 | Tampering | `?pb=` URL query | low | mitigate | `leseMassnahmenFilter` allowlist unchanged, single instance; Playwright removes invalid `pb` (08-11) | closed |
| T-08-19 | Repudiation | Review ledgers | low | mitigate | Every hash in ledgers 01/05/06 resolves via `git cat-file -e` (0 unresolvable) (08-12) | closed |
| T-08-SC | Tampering (supply chain) | npm/pip installs | high | mitigate | No package added: 0 changes to `package.json`, `package-lock.json`, `pyproject.toml`, `uv.lock` since 93b0a61 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-08-01 | T-08-08 | New tooltip strings contain only a constant prefix and `Intl` output, no markup; existing escaping stays in place | plan 08-04 threat model | 2026-10-07 |
| AR-08-02 | T-08-15 | Documentation comments name only the public repository and commands; no secrets or personal data | plan 08-08 threat model | 2026-10-07 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-07 | 20 | 20 | 0 | secure-phase 08 (orchestrator, L1 grep depth, register authored at plan time) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed

## Security Audit 2026-10-08

| Metric | Count |
|---|---|
| Threats found | 20 |
| Closed | 20 |
| Open | 0 |
