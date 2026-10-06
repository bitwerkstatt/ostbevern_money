---
phase: "7"
slug: "feinschliff-und-ver-ffentlichung"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-06"
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest 5.0.3 (App, `environment: 'node'`, `src/**/__tests__/*.test.ts`), pytest (Pipeline), neu: Playwright 1.63.0 + `@axe-core/playwright` 4.13.0 (`app/e2e/*.spec.ts`, im Docker-Image `mcr.microsoft.com/playwright:v1.63.0-noble`), Lighthouse 13.5.0 (Skript, nicht in `package.json`) |
| **Config file** | `app/vitest.config.ts`, `app/tsconfig.vitest.json`; `pipeline/pyproject.toml`; neu `app/playwright.config.ts`, `app/tsconfig.e2e.json` |
| **Quick run command** | Pipeline: `uv run --directory pipeline pytest tests/test_quellen.py -x -q`; App: Scratch-Kopie (`S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app \| tar -xf - -C "$S" && npm --prefix "$S/app" ci --no-audit --no-fund`), dann `npm --prefix "$S/app" run test -- <datei>` |
| **Full suite command** | `uv run --directory pipeline pytest -q` **plus** `uv run --directory pipeline python alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data && test -z "$(git status --porcelain --untracked-files=all -- daten app/src/data)"` (WebP-Bytes unter `app/public/quellen/` ausgenommen, siehe RESEARCH) **plus** App-Kette in Scratch-Kopie (`ci`, `type-check`, `lint`, `format:check`, `test`, `build`) **plus** Playwright im Docker-Image (`npx playwright test`) |
| **Estimated runtime** | App-Tests < 5 s; gezielte pytest-Dateien < 60 s; Seitenrendern ≈ 21 s; volle Pipeline-Suite ≈ 330 s; Playwright-Suite ≈ 60 s |

---

## Sampling Rate

- **After every task commit:** gezielte pytest- bzw. vitest-Datei (Scratch-Kopie) plus `type-check`/`lint`/`format:check`
- **After every plan wave:** volle Pipeline-Suite + Reproduzierbarkeitsgate + komplette App-Kette + Playwright im Docker-Image
- **Before `/gsd-verify-work`:** Full suite must be green, Lighthouse-Tabelle aller Routen ≥ 95, Du-Test grün und Texte abgenommen, öffentliche URL geprüft (menschlicher Checkpoint)
- **Max feedback latency:** 60 seconds (pro Task; volle Suite nur am Wellenende)

---

## Per-Task Verification Map

*Wird vom Planer/Executor je Task befüllt. Anforderungs-zu-Test-Zuordnung siehe 07-RESEARCH.md § Validation Architecture.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-xx-xx | — | — | DATA-04 | — | N/A | pytest | `uv run --directory pipeline pytest tests/test_quellen.py -x -q` | ❌ W0 | ⬜ pending |
| 07-xx-xx | — | — | UI-02 | — | N/A | vitest + Playwright | `npm --prefix "$S/app" run test -- src/lib/__tests__/quelle.test.ts` / `e2e/interaktion.spec.ts` | ❌ W0 | ⬜ pending |
| 07-xx-xx | — | — | UI-06 | — | N/A | vitest | `npm --prefix "$S/app" run test -- src/lib/__tests__/duanrede.test.ts` | ❌ W0 | ⬜ pending |
| 07-xx-xx | — | — | A11Y-01..03 | — | N/A | Playwright | `e2e/inventar.spec.ts`, `e2e/interaktion.spec.ts`, `e2e/mobil.spec.ts` | ❌ W0 | ⬜ pending |
| 07-xx-xx | — | — | A11Y-04 | — | N/A | Lighthouse-Skript | Lighthouse-Rezept (RESEARCH § Code Examples) | ❌ W0 | ⬜ pending |
| 07-xx-xx | — | — | QUAL-02 | — | Keine Fremd-Requests | Playwright | `e2e/smoke.spec.ts` | ❌ W0 | ⬜ pending |
| 07-xx-xx | — | — | DEPL-01 | — | Minimale Workflow-Berechtigungen, gepinnte SHAs | statisch (grep) | `grep` auf `permissions`, `if:` in `.github/workflows/` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pipeline/tests/test_quellen.py` — DATA-04 (Suche, Maße, Abdeckung, Bericht)
- [ ] `app/src/lib/__tests__/quelle.test.ts` — Schlüssel, Prozentumrechnung, Abdeckung
- [ ] `app/src/lib/__tests__/duanrede.test.ts` — UI-06
- [ ] `app/e2e/smoke.spec.ts`, `app/e2e/interaktion.spec.ts`, `app/e2e/mobil.spec.ts`, `app/e2e/inventar.spec.ts`, `app/playwright.config.ts`, `app/tsconfig.e2e.json`
- [ ] `npm install -D @playwright/test@1.63.0 @axe-core/playwright@4.13.0` und Skript `"test:e2e": "playwright test"` in `app/package.json`
- [ ] `.gitignore`: `playwright-report/`, `test-results/`, `blob-report/`
- [ ] Lighthouse-Rezept als Skript

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Öffentliche URL lädt (Icons, Belegbild, Direktaufruf `/#/ausgaben`, `/#/ueber`, Fußzeile, PDF-Link mit `#page=`) | DEPL-02 | Repo hat noch keinen Remote; `*.github.io` aus dem Sandbox nicht erreichbar | Nach erstem Deploy URL im Browser öffnen und Liste abhaken |
| Texte deutsch und in Du-Anrede abgenommen | UI-06 | Heuristik hat Falschmeldungen; inhaltliche Abnahme | Text-Checkpoint mit Du-Test-Bericht |
| Belegseiten ohne Personennamen; Nutzungsrechte der Seitenbilder | DATA-04 / Datenschutz | Rechts-/Inhaltsfrage | Stellenplan-Seiten S. 284–290 sichten |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
