---
phase: "1"
slug: "setup"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-01"
---

# Phase 1 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PyPI / npm registry -> developer machine and CI | Package code (install scripts, create-vue scaffolder) executes locally and in CI | Third-party code |
| Jahrgangsdatei / Sollwertdatei -> pipeline loader | Config decides which file is read and which numbers count as correct | Team-authored TOML (integrity-relevant) |
| Working tree -> git history | Untracked files could be committed by accident | Local files (caches, OS metadata) |
| Static site -> visitor browser | The page decides which hosts the visitor's browser contacts | Visitor IP / request metadata |
| GitHub raw content -> app/public/icons | Static SVG assets downloaded once and committed | Static assets |
| App content -> citizen | Displayed figures are read as statements about the Gemeinde's budget | Public budget figures (demo data in Phase 1) |
| Data/props -> DOM | Strings from JSON and props are rendered into the page | Bundled JSON strings |
| Third-party GitHub Actions -> CI runner | Action code runs with the workflow token and checked-out source | Source code, GITHUB_TOKEN |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-01 | Tampering | `npm create vue@3.24.0` | high | mitigate | Pinned `create-vue@3.24.0` on the approved list; 01-03-SUMMARY.md:140 records exactly that invocation | closed |
| T-01-SC | Tampering | npm/pip installs (01-02, 01-03, 01-04, CI) | high | mitigate | Human approval of all 26 packages (01-01-SUMMARY.md, re-confirmed in 01-UAT.md test 2); `pipeline/uv.lock` (397 hashes) and `app/package-lock.json` tracked; ci.yml:32 `uv sync --locked`, ci.yml:55 `npm ci` | closed |
| T-01-02 | Tampering / Information disclosure | `lade_jahrgang` (`pdf_pfad`) | medium | mitigate | `pipeline/ostbevern/konfiguration.py:135` rejects absolute paths, `:140` `is_relative_to(PROJEKT_WURZEL)`; tests `test_absoluter_pdf_pfad_wird_abgelehnt`, `test_relativer_pdf_pfad_ausserhalb_projekt_wird_abgelehnt` | closed |
| T-01-03 | Tampering (data integrity) | `lade_jahrgang`, `lade_sollwerte` | high | mitigate | int-not-bool (`konfiguration.py:127`), recursive int-not-float/bool (`:201-204`); 12 negative/completeness tests in `test_konfiguration.py`, all green | closed |
| T-01-04 | Denial of service | `alle.py --jahr` | low | accept | int-typed typer option; unknown year exits 1 with German error (verified 2026-10-01) | closed |
| T-01-05 | Information disclosure | git staging | low | mitigate | Root `.gitignore` covers .DS_Store, caches, .venv, node_modules, dist; explicit-path staging convention in CLAUDE.md | closed |
| T-01-06 | Information disclosure | Runtime asset loading | medium | mitigate | `app/src/lib/webawesome.ts:7` `setIconPath(BASE_URL + icons)`; only external host in app/src + index.html is the github.com credit link (App.vue:22); UAT test 3 confirmed no third-party requests | closed |
| T-01-07 | Tampering | create-vue extras, downloaded SVGs | low | mitigate | No oxlint / vite-plugin-vue-devtools in `app/package.json`; icons committed under `app/public/icons/solid` | closed |
| T-01-08 | Spoofing (misleading content) | StartPage demo chart and table | medium | mitigate | Notice text lives only in `ChartCard.vue:30`; StartPage passes `:beispieldaten` (line 71) from `beispieldaten.json` (`"beispieldaten": true`); UAT test 5 confirmed notice visible | closed |
| T-01-09 | Tampering (script injection) | Components rendering strings | low | mitigate | 0 occurrences of `v-html` / `innerHTML` in app/src | closed |
| T-01-10 | Tampering | `uses:` steps in ci.yml | medium | mitigate | All 4 `uses:` pinned to 40-char SHAs with version comment | closed |
| T-01-11 | Elevation of privilege | `GITHUB_TOKEN` in CI | medium | mitigate | ci.yml:15-16 `permissions: contents: read`; no `secrets.` references; no deploy job | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01-01 | T-01-04 | Local developer CLI with no network surface; invalid input fails fast with a named error and exit code 1 | Plan 01-02 threat model (planner), confirmed at audit | 2026-10-01 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-01 | 12 | 12 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 grep-depth; plan-time register, short-circuit) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-01
