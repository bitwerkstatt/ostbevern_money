---
phase: "9"
slug: "sicherheit-und-audit"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-09"
---

# Phase 9 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 9 is almost entirely documentation: the phase-4 security register, seven re-verifications, the Basislauf, the STATE.md cleanup and the milestone audit. Two plans changed app code: 09-02 (`tabellenRahmen` in `DatenTabelle`) and 09-14 (display logic for G-09-01 to G-09-03). There is no network surface, no authentication and no runtime user input. The relevant threats are repudiation (reports that claim more than the evidence shows), tampering with shipped data or archived history, and the supply chain of the package installs used for test runs.

The register below is the union of the `<threat_model>` blocks of plans 09-01 to 09-15 (`register_authored_at_plan_time: true`). Every SUMMARY reports "Threat Flags: None". The classification was done at ASVS L1 depth (grep and command checks on 2026-10-09, after the merge of all 15 plans, HEAD `1f50eaa`). The short-circuit rule of `/gsd-secure-phase` applies (threats_open 0, plan-time register, ASVS 1), so no auditor agent ran.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Code and data → reports | Verification reports, the Basislauf and the audit claim facts about the code; a claim without evidence misleads later phases and the user | Test counts, statuses, digests, file:line references |
| Pipeline run → shipped data | `alle.py` regenerates `daten/`, `app/src/data/` and `app/public/quellen`; an unintended change would publish wrong numbers | Public budget figures |
| Package registries → test environments | `uv` and `npm ci` install packages for test runs in worktrees and scratch copies | Third-party code |
| Keyboard user → table scroll frame | An overflowing table frame must stay reachable and named | UI focus and accessible name |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-09-01 | Repudiation | 04-SECURITY.md register | medium | mitigate | Every row of `04-SECURITY.md` cites file:line and a test from the `-rs` runs of 09-01; `status: verified`, `threats_open: 0` | closed |
| T-09-02 | Information Disclosure | app/src/data/*.json, daten/manuell/meta.json | high | mitigate | Name tests green without skip (09-01 runs; Abschlusslauf 681 passed, 0 skipped); meta.json allowlist plus `test_meta_json_bricht_ab` | closed |
| T-09-03 | Tampering | conditional D-04 fix | high | mitigate | No threat was open, so no fix was made (09-01 SUMMARY); `git diff 86c56dc HEAD -- daten app/src/data app/public/quellen` is empty | closed |
| T-09-04 | Denial of Service | DatenTabelle scroll frame | medium | mitigate | `tabellenRahmen` in `app/src/components/datenTabelle.ts`, wired in `DatenTabelle.vue`, tests in `zustaende.test.ts`; Playwright mobil green (09-02, Abschlusslauf) | closed |
| T-09-05 | Repudiation | 08-REVIEW-DISPOSITION.md | low | mitigate | Ledger at `open: 0`, each row cites a commit or a reason (09-02) | closed |
| T-09-06 | Tampering | 08-VERIFICATION.md digest | medium | mitigate | Digest from `verification.fingerprint`; `verification.status` prints `passed` (re-checked after 09-15 Nachlauf) | closed |
| T-09-07 | Repudiation | 09-BASISLAUF.md | medium | mitigate | Numbers copied from command output, `head` pinned to `1d0df35`; code paths unchanged until 09-14 | closed |
| T-09-08 | Tampering | daten/, app/src/data/, app/public/quellen | medium | mitigate | `alle.py` byte-identical in Basislauf, 09-14 and Abschlusslauf; no tracked or untracked change in the three directories over the phase | closed |
| T-09-09 | Repudiation | 01-VERIFICATION.md truths | medium | mitigate | Truths cite file:line or Basislauf lines; `re_verification` keeps previous status and score | closed |
| T-09-10 | Tampering | covered_digest, shared data directories | medium | mitigate | Digest from `verification.fingerprint`; `verification.status` `passed`; no full runs in the plan | closed |
| T-09-11 | Repudiation | 02-VERIFICATION.md truths | medium | mitigate | As T-09-09 for phase 2 | closed |
| T-09-12 | Tampering | covered_digest, shared data directories | medium | mitigate | As T-09-10 for phase 2; status `passed` | closed |
| T-09-13 | Repudiation | 03-VERIFICATION.md truths | medium | mitigate | As T-09-09 for phase 3 | closed |
| T-09-14 | Tampering | covered_digest, shared data directories | medium | mitigate | As T-09-10 for phase 3; status `passed` | closed |
| T-09-15 | Repudiation | 04-VERIFICATION.md truths | medium | mitigate | As T-09-09 for phase 4 | closed |
| T-09-16 | Tampering | covered_digest, shared data directories | medium | mitigate | As T-09-10 for phase 4; status `passed` | closed |
| T-09-17 | Repudiation | 05-VERIFICATION.md truths and human items | medium | mitigate | Every human item keeps its entry with a `beleg` separating UAT and user confirmation from verifier checks (D-21); status `human_needed`, not overstated | closed |
| T-09-18 | Tampering | covered_digest, shared data directories | medium | mitigate | As T-09-10 for phase 5; refreshed in the 09-15 Nachlauf; not `stale` | closed |
| T-09-19 | Repudiation | 06-VERIFICATION.md truths | medium | mitigate | As T-09-09 for phase 6 | closed |
| T-09-20 | Tampering | covered_digest, shared data directories | medium | mitigate | As T-09-10 for phase 6; refreshed in the 09-15 Nachlauf; status `passed` | closed |
| T-09-21 | Repudiation | 07-VERIFICATION.md user-confirmed items | medium | mitigate | Deploy and device check marked "vom Nutzer bestätigt (2026-10-08)", not counted as verifier checks (D-14) | closed |
| T-09-22 | Tampering | covered_digest, shared data directories | medium | mitigate | As T-09-10 for phase 7; status `passed` | closed |
| T-09-23 | Repudiation | STATE.md Blockers/Concerns | medium | mitigate | Three bullets removed after automated evidence checks (ledgers `open: 0`, `04-SECURITY` `threats_open: 0`, no `stale` phase); the still-true `node_modules` note kept (09-11) | closed |
| T-09-24 | Tampering | archived planning documents | low | mitigate | `git diff 86c56dc HEAD` over v1.0-ROADMAP.md and RETROSPECTIVE.md is empty | closed |
| T-09-25 | Repudiation | requirement rows of the audit | medium | mitigate | 102 rows from three named sources, scripted completeness check (09-12) | closed |
| T-09-26 | Tampering | archived phase directories | low | mitigate | Only the intended files changed under `.planning/milestones/` (seven VERIFICATION reports and `04-SECURITY.md`) | closed |
| T-09-27 | Repudiation | integration and flow verdicts | medium | mitigate | Each verdict cites file:line, a Basislauf Playwright title or a run line; steps without automated evidence are named (F2–F4 `partial`) | closed |
| T-09-28 | Tampering | D-10 triage | high | mitigate | Written D-10 rule applied per row with the check recorded; Disposition column: 3 `fixed`, 18 `deferred`, 2 `v2-backlog`, none `fix`; audit `status: tech_debt` | closed |
| T-09-29 | Tampering | fixes to pipeline or app code | high | mitigate | Red test first for G-09-01..03; `alle.py` byte-identical after the fixes; tolerance and Prüfregeln untouched (09-14, Abschlusslauf) | closed |
| T-09-30 | Repudiation | Lückenliste rows set to fixed | medium | mitigate | Each `fixed` row cites test and fix commits known to git (3f944a7/f8aef3f, 74fed1c/ce5880e, b3b2658/448e43d) | closed |
| T-09-31 | Repudiation | requirement ticks, audit status, Nachlauf entries | medium | mitigate | SEC-01, AUD-01..03 ticked only after the status loop and the green Abschlusslauf on `109cfac`; Nachlauf entries name commits | closed |
| T-09-32 | Tampering | archived history | medium | mitigate | MILESTONES.md diff over the phase has no deleted line; v1.0-ROADMAP.md and RETROSPECTIVE.md unchanged (D-17) | closed |
| T-09-SC | Tampering | npm/pip installs | high | mitigate | `git diff 86c56dc HEAD` over `app/package.json`, `app/package-lock.json`, `pipeline/pyproject.toml`, `pipeline/uv.lock` is empty; installs used `npm ci` / `uv` against the committed lockfiles | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

No accepted risks.

The `npm audit` chain in development dependencies (G-09-18 in the milestone audit, 4 high, `braces` → `micromatch` → `fast-glob` → `@vue/eslint-config-typescript`; production: 0) is tracked as deferred tech debt in `.planning/v1.0-MILESTONE-AUDIT.md`, not as a phase-9 threat.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-09 | 33 | 33 | 0 | /gsd-secure-phase (orchestrator, L1 short-circuit, no auditor) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-09
