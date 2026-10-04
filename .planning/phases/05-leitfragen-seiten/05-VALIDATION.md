---
phase: "5"
slug: "leitfragen-seiten"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-04"
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (pipeline, existing) + vitest 5.0.3 (app, installed by 05-01 after the legitimacy checkpoint) |
| **Config file** | `pipeline/pyproject.toml`; `app/vitest.config.ts` + `app/tsconfig.vitest.json` (Wave 1, plan 05-01) |
| **Quick run command** | `uv run --directory pipeline pytest tests/<datei>.py -x -q` bzw. `S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app \| tar -xf - -C "$S" && npm --prefix "$S/app" ci --no-audit --no-fund && npm --prefix "$S/app" run test -- <testdatei>` |
| **Full suite command** | `uv run --directory pipeline pytest -q` + reproducibility gate (`alle.py --jahr 2026` → `git diff --exit-code -- daten app/src/data`, no untracked) + app chain in a scratch copy (`npm ci`, `type-check`, `lint`, `format:check`, `test`, `build`) |
| **Estimated runtime** | pipeline ~60 s; app chain ~90 s (dominated by `npm ci` in the scratch copy) |

---

## Sampling Rate

- **After every task commit:** Run the task's `<automated>` command (targeted pytest file or targeted vitest file plus type-check/lint/format in the scratch copy)
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green (plan 05-15 Task 2 is the phase gate)
- **Max feedback latency:** ~90 seconds (scratch-copy `npm ci`; the sandbox cannot run npm in the mounted `app/` because of macOS binaries)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 1 | — | T-05-SC | vitest installed only after human approval | checkpoint | blocking-human | n/a | ⬜ pending |
| 5-01-02 | 01 | 1 | UI-05 | T-05-SC | exact pin, scratch install | unit | app chain incl. `npm run test` (format.test.ts) | ❌ W0 → created | ⬜ pending |
| 5-01-03 | 01 | 1 | UI-05 | T-05-01 | missing value → '–', unknown code throws | unit + pytest | `pytest tests/test_formatiere.py tests/test_texte.py`; app chain | ✅ extend | ⬜ pending |
| 5-02-01 | 02 | 1 | EINN-04 | T-05-03/04 | 2.1.7 checked by Regel 5, Befunde exact | pytest | `pytest tests/test_manuell.py tests/test_app_daten.py tests/test_pruefung.py`; `alle.py` + konsistenz green | ✅ extend | ⬜ pending |
| 5-02-02 | 02 | 1 | EINN-06, EINN-04 | T-05-03/05 | Pauschalen vs GFP Z. 18, Konzessionsabgaben split | pytest | same + `-k "gfp or konzession"` | ✅ extend | ⬜ pending |
| 5-02-03 | 02 | 1 | (AUSG-05 support) | T-05-03 | zeilen_namen from zeilen.py only | pytest + type-check | full pytest, reproducibility gate, app chain | ✅ extend | ⬜ pending |
| 5-03-01 | 03 | 2 | GLOS-01, EINN-05 | T-05-06/07 | digit rule, D-02 Euro-Grundzahl check | pytest | `pytest tests/test_texte.py`; draft validation command | ✅ extend | ⬜ pending |
| 5-03-02 | 03 | 2 | GLOS-01 | T-05-08 | texts approved before commit | checkpoint | blocking-human | n/a | ⬜ pending |
| 5-03-03 | 03 | 2 | GLOS-01, UI-05 | T-05-06/07 | Schritt 07 aborts on unknown key / D-02 violation | pytest | full pytest, reproducibility gate, app chain | ✅ extend | ⬜ pending |
| 5-04-01 | 04 | 2 | UI-01 | T-05-09 | jahr only from haushalt.jahre | unit | vitest jahr.test.ts + app chain | ❌ W0 → created | ⬜ pending |
| 5-04-02 | 04 | 2 | UI-01, AUSG-05 | T-05-09/10 | Map allowlists, prototype keys rejected | unit | vitest ansicht.test.ts | ❌ W0 → created | ⬜ pending |
| 5-04-03 | 04 | 2 | UI-01 | T-05-11 | named routes only, focus/title | build + human-check | app chain | n/a | ⬜ pending |
| 5-05-01 | 05 | 2 | AUSG-01/02, FLUSS-01 | T-05-12/13 | escaped tooltips, contrast ≥ 4.5 | unit | vitest farben/tooltip | ❌ W0 → created | ⬜ pending |
| 5-05-02 | 05 | 2 | FLUSS-04 | — | reduced motion, '–' in tables | unit | vitest bewegung + app chain | ❌ W0 → created | ⬜ pending |
| 5-05-03 | 05 | 2 | — | — | UI-SPEC amended (D-19/D-20) | grep | marker grep on 05-UI-SPEC.md | ✅ | ⬜ pending |
| 5-06-01 | 06 | 2 | UI-05 | T-05-14/15/16 | text only, year binding | unit | vitest texte.test.ts | ❌ W0 → created | ⬜ pending |
| 5-06-02 | 06 | 2 | EINN-01, START-01 | — | per-capita rounding, Σ Ertragsarten | unit | vitest berechnung/zeilen/ertragsarten | ❌ W0 → created | ⬜ pending |
| 5-06-03 | 06 | 2 | START-02, AUSG-02 | T-05-14 | KL Unterposten 'rd.' | unit | vitest kreisumlage + app chain | ❌ W0 → created | ⬜ pending |
| 5-07-01 | 07 | 3 | UI-03 | T-05-17/18/20 | placeholders detectable, rel noopener | unit + pytest | vitest config/format; pytest test_formatiere | ❌ W0 → created | ⬜ pending |
| 5-07-02 | 07 | 3 | UI-03 | T-05-19 | skip link never navigates | unit + human-check | vitest menue + app chain | ❌ W0 → created | ⬜ pending |
| 5-08-01 | 08 | 3 | START-01 | T-05-21 | values only from data | unit | vitest kennzahlen | ❌ W0 → created | ⬜ pending |
| 5-08-02 | 08 | 3 | START-02 | T-05-22 | KL excluded (D-20) | unit + human-check | vitest kennzahlen + app chain | ✅ extend | ⬜ pending |
| 5-09-01 | 09 | 3 | EINN-01 | T-05-25 | escaped tooltips | unit | vitest balken | ❌ W0 → created | ⬜ pending |
| 5-09-02 | 09 | 3 | EINN-02/03/04/06 | T-05-23 | Finanzplan separate | unit | vitest einnahmen | ❌ W0 → created | ⬜ pending |
| 5-09-03 | 09 | 3 | EINN-05 | T-05-24 | D-01 source per year | unit + human-check | vitest zeitreihen + app chain | ❌ W0 → created | ⬜ pending |
| 5-10-01 | 10 | 3 | AUSG-01/02 | T-05-26/27/28 | read-only berechnet values | unit | vitest drilldown | ❌ W0 → created | ⬜ pending |
| 5-10-02 | 10 | 3 | AUSG-03 | T-05-27 | surplus texts exist | unit + human-check | vitest drilldown + app chain | ✅ extend | ⬜ pending |
| 5-11-01 | 11 | 3 | AUSG-05 | T-05-29/30 | Map lookup, text only | unit | vitest produkt | ❌ W0 → created | ⬜ pending |
| 5-11-02 | 11 | 3 | AUSG-05 | T-05-31 | only approved Bezugsgrößen | unit + human-check | vitest produkt + app chain | ✅ extend | ⬜ pending |
| 5-12-01 | 12 | 3 | FLUSS-01/02/03 | T-05-32/33 | balance ±2 € all years | unit | vitest geldfluss | ❌ W0 → created | ⬜ pending |
| 5-12-02 | 12 | 3 | FLUSS-04, FLUSS-02 | T-05-34 | year-matching reading aid | unit + human-check | vitest geldfluss + app chain | ✅ extend | ⬜ pending |
| 5-13-01 | 13 | 3 | GLOS-01 | T-05-35/36 | text only, hash = id lookup | unit | vitest glossar | ❌ W0 → created | ⬜ pending |
| 5-13-02 | 13 | 3 | GLOS-02/03 | T-05-36 | key union + usage scan | unit + human-check | vitest glossar + app chain | ✅ extend | ⬜ pending |
| 5-14-01 | 14 | 4 | AUSG-04 | T-05-37 | exact Aufwand sum | unit | vitest aufwandsarten | ❌ W0 → created | ⬜ pending |
| 5-14-02 | 14 | 4 | AUSG-02, AUSG-04 | T-05-38/39 | year-matching Minderaufwand text | unit + human-check | vitest aufwandsarten + app chain | ✅ extend | ⬜ pending |
| 5-15-01 | 15 | 5 | GLOS-03 | T-05-42 | every page links the glossary | unit | vitest quelltext/glossar | ❌ W0 → created | ⬜ pending |
| 5-15-02 | 15 | 5 | UI-05 | T-05-40/41 | no hand-typed numbers, no raw HTML | unit + gate + human-check | full suite command | ✅ extend | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] vitest 5.0.3 install after the blocking-human legitimacy checkpoint (05-01 Task 1/2)
- [ ] `app/vitest.config.ts`, `app/tsconfig.vitest.json`, script `test`, CI step "Tests (vitest)", CLAUDE.md command (05-01)
- [ ] `app/src/charts/__tests__/format.test.ts` as the first suite (05-01); every later `__tests__/*.test.ts` is created test-first by its plan
- [ ] ESLint `ignoreParents` for Web Awesome slot hosts (05-04), self-hosted external-link icon (05-07)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual layout at 360/1280 px, focus visibility, drawer, skip link, tooltips on focus | UI-01, UI-03, GLOS-03, START-01 | No browser in the sandbox; Playwright/Lighthouse are Phase 7 | `<human-check>` blocks of 05-04 T3, 05-06 T3, 05-07 T2, 05-08 T2, 05-09 T3, 05-10 T2, 05-11 T2, 05-12 T2, 05-13 T2, 05-14 T2, 05-15 T2 (consolidated at phase end) |
| Fachliche correctness of glossary and new Erklärtexte, Bezugsgrößen list | GLOS-01, AUSG-05 | Content judgement (D-15) | 05-03 Task 2 blocking-human checkpoint |
| Package legitimacy of vitest 5.0.3 | — | Supply-chain judgement | 05-01 Task 1 blocking-human checkpoint |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** {pending / approved YYYY-MM-DD}
