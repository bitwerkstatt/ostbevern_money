---
phase: "08"
slug: "fixes-und-triage"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-07"
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest 5.0.3 (node env, SSR render); Playwright 1.63.0 + axe 4.13.0; pytest 9.1.1; ruff 0.16.9 |
| **Config file** | `app/vitest.config.ts`, `app/playwright.config.ts`, `pipeline/pyproject.toml` |
| **Quick run command** | App (in scratch copy of `app/`): `npx vitest run src/lib/__tests__/<file>.test.ts`; Pipeline: `uv run --directory pipeline pytest tests/<file>.py -q` |
| **Full suite command** | App chain in scratch copy (`npm ci && npm run type-check && npm run lint && npm run format:check && npm run test && npm run build`), `scripts/e2e-wie-ci.sh <scratch>/app` plus `--project=mobil`; `uv run --directory pipeline pytest`; `uv run --directory pipeline python alle.py --jahr 2026` |
| **Estimated runtime** | quick: ~2–5 s; full: ~8 min (pytest ~6 min, e2e ~1 min, alle.py ~30 s) |

---

## Sampling Rate

- **After every task commit:** Run the affected vitest/pytest file(s), plus `npm run type-check` for any `.vue`/`.ts` edit
- **After every plan wave:** Full vitest, type-check, lint, format:check, build; Playwright `ci` project; for pipeline waves the `test_texte.py test_app_daten.py test_konfiguration.py test_formatiere.py` files and `ruff`
- **Before `/gsd-verify-work`:** Full CI chain (scratch copies, incl. `mobil` project and the `alle.py --jahr 2026` reproducibility diff) must be green
- **Max feedback latency:** ~30 seconds per task

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | TXT-01 | — | N/A | unit | `npx vitest run src/lib/__tests__/geldfluss.test.ts` | ✅ extend | ⬜ pending |
| TBD | TBD | 1 | TXT-02 | — | N/A | unit | `npx vitest run src/lib/__tests__/aufwandsarten.test.ts src/lib/__tests__/geldfluss.test.ts` | ✅ extend | ⬜ pending |
| TBD | TBD | 1 | TXT-03 | — | N/A | pytest + unit | `uv run --directory pipeline pytest tests/test_texte.py tests/test_app_daten.py -q`; `npx vitest run src/lib/__tests__/texte.test.ts` | ✅ extend | ⬜ pending |
| TBD | TBD | 1 | TXT-04 | — | N/A | unit (guard) | `npx vitest run src/lib/__tests__/quelltext.test.ts src/charts/__tests__/format.test.ts` | ❌ W0 guard | ⬜ pending |
| TBD | TBD | 1 | TXT-05 | — | N/A | unit | `npx vitest run src/lib/__tests__/stellen.test.ts src/lib/__tests__/zuschuesse.test.ts` | ✅ extend | ⬜ pending |
| TBD | TBD | 1 | TXT-06 | — | N/A | unit | `npx vitest run src/lib/__tests__/einwohner.test.ts` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | A11Y-01 | — | N/A | unit + type-check | `npx vitest run src/components/__tests__/zustaende.test.ts`; `npm run type-check` | ✅ extend | ⬜ pending |
| TBD | TBD | 2 | A11Y-01/03 | — | N/A | e2e mobil | `scripts/e2e-wie-ci.sh <scratch>/app --project=mobil e2e/mobil.spec.ts` | ✅ extend | ⬜ pending |
| TBD | TBD | 2 | A11Y-02 | — | N/A | e2e mobil + ci | `scripts/e2e-wie-ci.sh <scratch>/app e2e/interaktion.spec.ts` | ✅ extend | ⬜ pending |
| TBD | TBD | 3 | TRI-01..03 | — | N/A | scripted check | `grep -c "| open |" <ledger>` = 0 and `grep -n "^open:" <ledger>` shows `open: 0` | n/a | ⬜ pending |
| TBD | TBD | 3 | TRI-04 | — | N/A | cross | `alle.py --jahr 2026` + `git status --porcelain -- daten app/src/data app/public/quellen` shows only intended changes | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs are filled in by the planner/executor once PLAN.md files exist.*

---

## Wave 0 Requirements

- [ ] `app/src/lib/__tests__/einwohner.test.ts` — TXT-06
- [ ] guard test for the „rd.“ rule (new file or block in `quelltext.test.ts`) — TXT-04
- [ ] `app/src/components/__tests__/chartcard.test.ts` (or block in an existing file) — 01/IN-03
- [ ] new tests in `app/e2e/mobil.spec.ts` / `interaktion.spec.ts` — A11Y-01/02/03, 06/IN-09
- [ ] No framework installs needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Screenreader does not announce a table name twice | A11Y-03 | Chromium a11y tree alone cannot prove screen-reader announcement behaviour (RESEARCH assumption A1) | VoiceOver/NVDA: navigate to a `DatenTabelle` on `/ausgaben` at 360 px, check the name is read once |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
