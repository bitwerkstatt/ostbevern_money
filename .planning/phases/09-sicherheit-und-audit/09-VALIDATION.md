---
phase: "9"
slug: "sicherheit-und-audit"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-08"
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Pipeline, 681 Tests), vitest (App-Einheiten), Playwright + axe (89 Tests im Projekt `ci`) |
| **Config file** | `pipeline/pyproject.toml`, `app/vite.config.ts`, `app/playwright.config.ts` |
| **Quick run command** | gezielte pytest-Auswahl bzw. Dateiprüfung des betroffenen Artefakts (siehe 09-RESEARCH.md „Code Examples“, ~16 s) |
| **Full suite command** | Abschlusslauf: CI-Kette aus `.claude/CLAUDE.md` (Pipeline ~6 min, App ~15 s in Scratch-Kopie, e2e ~35 s über `scripts/e2e-wie-ci.sh`) |
| **Estimated runtime** | ~420 seconds (voll), ~16 seconds (gezielt) |

---

## Sampling Rate

- **After every task commit:** gezielte pytest-Auswahl oder Dateiprüfung des betroffenen Artefakts
- **After every plan wave:** `verification.status` über alle Phasen; bei Codeänderung zusätzlich volle Pipeline- und App-Kette
- **Before `/gsd-verify-work`:** Abschlusslauf vollständig grün
- **Max feedback latency:** 420 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| SEC-01 | tbd | 1 | SEC-01 | T-04-01 … T-04-20, T-04-SC | 21 Bedrohungen mit Code- und Testbeleg, Namens-Tests grün ohne Skip | pytest gezielt + Dateiprüfung | gezielter pytest-Lauf; `grep -E '^(status\|threats_open\|asvs_level):' .planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md` | ❌ W1 (Datei) | ⬜ pending |
| AUD-02 | tbd | 2 | AUD-02 | — | N/A | Tool | Schleife `verification.status` über Phasen 1–8, erwartet `passed`/nicht stale | ✅ | ⬜ pending |
| AUD-03 | tbd | 3 | AUD-03 | — | N/A | Textprüfung | `grep -n "02-REVIEW\|04-REVIEW-DISPOSITION\|secure-phase 04\|Kein Milestone-Audit" .planning/STATE.md` ohne Treffer | ✅ | ⬜ pending |
| AUD-01 | tbd | 4 | AUD-01 | — | N/A | Dateiprüfung + Tool | `test -f .planning/v1.0-MILESTONE-AUDIT.md`; Frontmatter `status`, `scores`; jede Lücke mit Disposition | ❌ W4 (Datei) | ⬜ pending |
| Querschnitt | tbd | 5 | alle | — | Byte-Identität, Regeln 1–10 | Lauf | Abschlusslauf (CI-Kette) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Falls Review-Befunde aus Phase 8 (WR-01/WR-02) behoben werden, entstehen neue vitest-Tests im jeweiligen Fix-Task.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Deploy- und Gerätecheck Phase 7 | AUD-02 | Nutzeraufgabe, vom Nutzer am 2026-10-08 bestätigt (D-14) | In `07-VERIFICATION.md` als „vom Nutzer bestätigt (2026-10-08)“ kennzeichnen, nicht als Verifier-Prüfung |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 420s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
