---
phase: "08"
slug: "fixes-und-triage"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
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
| 08-02 T2 | 08-02 | 1 | TXT-01 | T-08-04 | „genau“ only in case D | unit (constructed `Geldfluss`) | `npm --prefix "$S/app" run test -- src/lib/__tests__/geldfluss.test.ts` | ✅ extend | ✅ green |
| 08-02 T3 | 08-02 | 1 | TXT-02 | T-08-05 | Z. 27 > 0 throws in both consumers | unit | `npm --prefix "$S/app" run test -- src/lib/__tests__/berechnung.test.ts src/lib/__tests__/aufwandsarten.test.ts src/lib/__tests__/geldfluss.test.ts` | ✅ extend | ✅ green |
| 08-01 T1, T2 | 08-01 | 1 | TXT-03 | T-08-01..03 | typed years and title placeholders rejected | pytest + unit + identity script | `uv run --directory pipeline pytest tests/test_texte.py tests/test_app_daten.py -q`; `npm --prefix "$S/app" run test -- src/lib/__tests__/texte.test.ts` | ✅ extend | ✅ green |
| 08-02 T1 | 08-02 | 1 | TXT-04 (authority) | — | N/A | unit + SSR | `npm --prefix "$S/app" run test -- src/charts/__tests__/format.test.ts src/components/__tests__/eurobetrag.test.ts` | ✅ created (08-02) | ✅ green |
| 08-04 T1–T3, 08-05 T1 | 08-04, 08-05 | 2 | TXT-04 (copies) | T-08-08 | N/A | unit + e2e smoke | `npm --prefix "$S/app" run test -- src/lib/__tests__/drilldown.test.ts src/lib/__tests__/zeitreihen.test.ts src/lib/__tests__/quelltext.test.ts`; `scripts/e2e-wie-ci.sh "$S/app" e2e/smoke.spec.ts` | ✅ extend | ✅ green |
| 08-07 T1 | 08-07 | 3 | TXT-04 (guard) | T-08-12 | guard fail-first on pre-phase file | unit (guard via `?raw` glob) | `npm --prefix "$S/app" run test -- src/lib/__tests__/rdregel.test.ts` | ✅ created (08-07) | ✅ green |
| 08-03 T1, 08-05 T1–T2 | 08-03, 08-05 | 1, 2 | TXT-05 | T-08-07, T-08-09 | derived sums labelled, own pages | unit | `npm --prefix "$S/app" run test -- src/lib/__tests__/stellen.test.ts src/lib/__tests__/zuschuesse.test.ts` | ✅ extend | ✅ green |
| 08-03 T2 | 08-03 | 1 | TXT-06 | T-08-06 | missing Einwohnerzahl throws | unit | `npm --prefix "$S/app" run test -- src/lib/__tests__/einwohner.test.ts` | ✅ created (08-03) | ✅ green |
| 08-06 T1 | 08-06 | 3 | A11Y-01 | T-08-10 | tab stop only with role and name | unit + type-check | `npm --prefix "$S/app" run test -- src/components/__tests__/zustaende.test.ts`; `npm --prefix "$S/app" run type-check` | ✅ extend | ✅ green |
| 08-06 T1 | 08-06 | 3 | A11Y-01/03 | T-08-10 | one name per table, unique regions, axe at 360 px | e2e mobil + ci mirror | `scripts/e2e-wie-ci.sh "$S/app" --project=mobil`; `scripts/e2e-wie-ci.sh "$S/app" e2e/interaktion.spec.ts` | ✅ extend | ✅ green |
| 08-06 T2 | 08-06 | 3 | A11Y-02 | T-08-11 | focus on h1 after drawer link | e2e mobil + ci mirror | `scripts/e2e-wie-ci.sh "$S/app" --project=mobil`; `scripts/e2e-wie-ci.sh "$S/app"` | ✅ extend | ✅ green |
| WR-03 (98803c4) | 08-06 (review fix) | post | A11Y-01 | T-08-10 | empty/whitespace caption never yields an unnamed focusable region; dev warning | unit (SSR) + source guard (D-14) | `npm --prefix "$S/app" run test -- src/components/__tests__/zustaende.test.ts src/lib/__tests__/quelltext.test.ts` | ✅ extend (7b9f0a6) | ✅ green |
| WR-02 (13eb786) | 08-06 (review fix) | post | A11Y-02 | T-08-11 | Ctrl/Meta- and Shift-click on a drawer link leave drawer open and focus off the h1 | e2e mobil + ci mirror | `scripts/e2e-wie-ci.sh "$S/app" --project=mobil e2e/mobil.spec.ts`; `scripts/e2e-wie-ci.sh "$S/app" e2e/interaktion.spec.ts` | ✅ extend (7b9f0a6) | ✅ green |
| 08-09 T1 | 08-09 | 3 | TRI-04 (01/IN-03) | T-08-16 | warning icon file exists, orphan JSON deleted | unit (SSR) | `npm --prefix "$S/app" run test -- src/components/__tests__/chartcard.test.ts` | ✅ created (08-09) | ✅ green |
| 08-12 T1–T3 | 08-12 | 5 | TRI-01..03 | T-08-19 | every row cites commit or reason | scripted check | ledger checks in 08-12 (`^open: 0$`, no `disposition: open`, no open table row, awk Source-cell check) | n/a | ✅ green |
| 08-07..08-11, 08-12 T3 | 08-07..08-12 | 3–5 | TRI-04 | T-08-13..18 | data byte-identical | cross | `uv run --directory pipeline python alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data` plus `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` empty (only intended diffs: texte.json in 08-01, deletion of beispieldaten.json in 08-09) | n/a | ✅ green |

*`$S` is the scratch copy: `S=$(mktemp -d) && rsync -a --exclude node_modules --exclude dist --exclude test-results --exclude playwright-report app/ "$S/app/" && npm --prefix "$S/app" ci --no-audit --no-fund --silent`.*

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs are filled in by the planner/executor once PLAN.md files exist.*

---

## Wave 0 Requirements

- [x] `app/src/lib/__tests__/einwohner.test.ts` — TXT-06
- [x] guard test for the „rd.“ rule (new file or block in `quelltext.test.ts`) — TXT-04
- [x] `app/src/components/__tests__/chartcard.test.ts` (or block in an existing file) — 01/IN-03
- [x] new tests in `app/e2e/mobil.spec.ts` / `interaktion.spec.ts` — A11Y-01/02/03, 06/IN-09
- [x] No framework installs needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Screenreader does not announce a table name twice | A11Y-03 | Chromium a11y tree alone cannot prove screen-reader announcement behaviour (RESEARCH assumption A1) | VoiceOver/NVDA: navigate to a `DatenTabelle` on `/ausgaben` at 360 px, check the name is read once (human-check in 08-06 T1 and 08-12 T3) |
| Middle-click / Alt-click on a drawer link and the stale-flag reset in `oeffneDrawer` (WR-02) | A11Y-02 | Not automated: Ctrl/Meta and Shift cases cover the same early-return branch; middle-click popups are unreliable in headless Chromium | At 360 px open the menu, middle-click a link: drawer stays open, focus stays in the drawer |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-07 (validate-phase 08 at execute-phase verify:post; full CI chain green at e844e5b/HEAD: vitest 2153, pytest 678, Playwright ci 87, mobil 39, alle.py byte-identical); re-validated 2026-10-08 after review fixes WR-01..WR-03 at 7b9f0a6: vitest 2158, pytest test_texte 107, Playwright ci 89, mobil 41, type-check/lint/format/build green)

## Validation Audit 2026-10-07

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

## Validation Audit 2026-10-08

| Metric | Count |
|---|---|
| Gaps found | 2 |
| Resolved | 2 |
| Escalated | 0 |
