---
phase: "7"
slug: "feinschliff-und-ver-ffentlichung"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
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
| 07-01-01 | 07-01 | 1 | DATA-04, UI-02 | T-07-01, T-07-02 | bbox nur bei Zeile+Betrag; Produktinformationsseiten nie ungeschwärzt | pytest + Determinismus + vitest + build | `uv run --directory pipeline pytest tests/test_quellen.py -x -q`; zweimal `08_quellenbelege.py` mit `sha256sum -c`; Scratch-Kette mit `quelle.test.ts` | ✅ (neu in Task) | ✅ green |
| 07-01-02 | 07-01 | 1 | UI-02, A11Y-02 | T-07-03, T-07-04 | kein Roh-HTML; `#page=` nur an fester URL | vitest | Scratch-Kette mit `quelle.test.ts`, `stiltokens.test.ts` | ✅ | ✅ green |
| 07-01-03 | 07-01 | 1 | UI-02 | T-07-05, T-07-SC | nur Requests an die Preview-Herkunft | Playwright (Docker) | `npx playwright test --project=ci e2e/quelle.spec.ts` | ✅ | ✅ green |
| 07-02-01 | 07-02 | 1 | DATA-04 (D-20) | T-07-07 | Fail-fast statt IndexError | pytest | `uv run --directory pipeline pytest tests/test_pruefung.py -x -q` | ✅ | ✅ green |
| 07-02-02 | 07-02 | 1 | DATA-04 (D-20) | T-07-06 | keine Datenänderung | pytest + Gate | `uv run --directory pipeline pytest -q`; `alle.py` + `git diff --stat --exit-code -- daten app/src/data` | ✅ | ✅ green |
| 07-03-01 | 07-03 | 2 | DATA-04 | T-07-10, T-07-11 | Mehrdeutigkeit → null + Bericht | pytest | `uv run --directory pipeline pytest tests/test_quellen.py -x -q` | ✅ (07-01) | ✅ green |
| 07-03-02 | 07-03 | 2 | DATA-04 | T-07-08 | Schwärzung geometrisch und per Pixel geprüft | pytest | `uv run --directory pipeline pytest tests/test_belegbilder.py tests/test_produkte.py tests/test_quellen.py tests/test_konfiguration.py -x -q` | ✅ | ✅ green |
| 07-03-03 | 07-03 | 2 | DATA-04 | T-07-12 | reproduzierbar inkl. `app/public/quellen` | pytest + Gate + vitest | `alle.py` + Diff/Untracked-Gate; Scratch-Kette mit `quelle-abdeckung.test.ts` | ✅ | ✅ green |
| 07-04-01 | 07-04 | 2 | A11Y-04 | T-07-13 | — | vitest | Scratch-Kette mit `stiltokens.test.ts`, `quelltext.test.ts` | ✅ | ✅ green |
| 07-04-02 | 07-04 | 2 | QUAL-02 | — | — | vitest + build | volle Scratch-Kette | ✅ | ✅ green |
| 07-05-01 | 07-05 | 3 | DEPL-02 | T-07-15 | Platzhalter erkannt | vitest | Scratch-Kette mit `config.test.ts` | ✅ | ✅ green |
| 07-05-02 | 07-05 | 3 | UI-06, DEPL-02 | T-07-14, T-07-16 | nie „offizielle“ Darstellung; noopener | vitest + build | volle Scratch-Kette | ✅ | ✅ green |
| 07-06-01 | 07-06 | 3 | UI-02 | T-07-17 | Schlüssel nur über `belegSchluessel` | vitest | Scratch-Kette mit `quelle-kacheln.test.ts` | ✅ | ✅ green |
| 07-06-02 | 07-06 | 3 | UI-02, DATA-04 | T-07-17 | — | vitest + Playwright | volle Scratch-Kette + `e2e/quelle.spec.ts` | ✅ | ✅ green |
| 07-07-01 | 07-07 | 3 | UI-02 | T-07-18 | — | vitest | Scratch-Kette mit `quelle-leitfragen.test.ts` | ✅ | ✅ green |
| 07-07-02 | 07-07 | 3 | UI-02 | T-07-18 | — | vitest + Playwright | volle Scratch-Kette + `e2e/quelle.spec.ts` | ✅ | ✅ green |
| 07-08-01 | 07-08 | 3 | UI-02 | T-07-19 | — | vitest | Scratch-Kette mit `quelle-kontext.test.ts` | ✅ | ✅ green |
| 07-08-02 | 07-08 | 3 | UI-02 | T-07-19 | — | vitest + Playwright | volle Scratch-Kette + `e2e/quelle.spec.ts` | ✅ | ✅ green |
| 07-09-01 | 07-09 | 4 | A11Y-02, UI-02 | — | — | Playwright | `npx playwright test --project=ci e2e/interaktion.spec.ts e2e/quelle.spec.ts` | ✅ | ✅ green |
| 07-09-02 | 07-09 | 4 | A11Y-01 | T-07-20 | geschlossene Ausnahmeliste | Playwright + vitest | volle Scratch-Kette + `npx playwright test --project=ci` | ✅ | ✅ green |
| 07-09-03 | 07-09 | 4 | A11Y-03 | — | — | Playwright | `npx playwright test --project=mobil` | ✅ | ✅ green |
| 07-10-01 | 07-10 | 5 | UI-06 | — | — | vitest + Playwright | Scratch mit `duanrede.test.ts` + `--project=texte` | ✅ | ✅ green |
| 07-10-02 | 07-10 | 5 | UI-06 | T-07-21, T-07-22 | Abnahme vor Commit | Checkpoint (blocking-human) | — | — | ✅ green (human-approved) |
| 07-10-03 | 07-10 | 5 | UI-06 | T-07-23 | Impressum ohne Platzhalter | pytest + Gate + vitest + Playwright | volle Ketten | ✅ | ✅ green |
| 07-11-01 | 07-11 | 6 | QUAL-02 | — | — | vitest (SSR) | Scratch mit `src/components/__tests__/zustaende.test.ts` | ✅ | ✅ green |
| 07-11-02 | 07-11 | 6 | QUAL-02, A11Y-02 | T-07-26, T-07-27 | keine Fremd-Requests, kein `.invalid` | Playwright + axe | `npx playwright test --project=ci` | ✅ | ✅ green |
| 07-11-03 | 07-11 | 6 | DEPL-01 | T-07-24, T-07-25 | Rechte nur im Deploy-Job, SHAs gepinnt | statisch (grep/awk) | `grep -c 'pages: write'`, Block-Prüfung per `awk`, SHA-Prüfung | ✅ | ✅ green |
| 07-12-01 | 07-12 | 7 | A11Y-04 | T-07-28 | Paketprüfung vor Installation | Checkpoint (blocking-human) | — | — | ✅ green (human-approved) |
| 07-12-02 | 07-12 | 7 | A11Y-04, A11Y-03 | T-07-28 | Lighthouse nur im Scratch | Lighthouse-Skript + CI-identisches Gate | `bash scripts/lighthouse-a11y.sh`; Pipeline- und App-Job lokal; `--project=ci --project=mobil` | ✅ | ✅ green |
| 07-12-03 | 07-12 | 7 | DEPL-02 | T-07-29 | Push nur durch den Nutzer | Checkpoint (human-action) | — (Sandbox erreicht github.io nicht) | — | ✅ green (human-approved) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `pipeline/tests/test_quellen.py` — DATA-04 (Suche, Maße, Abdeckung, Bericht)
- [x] `app/src/lib/__tests__/quelle.test.ts` — Schlüssel, Prozentumrechnung, Abdeckung
- [x] `app/src/lib/__tests__/duanrede.test.ts` — UI-06
- [x] `app/e2e/smoke.spec.ts`, `app/e2e/interaktion.spec.ts`, `app/e2e/mobil.spec.ts`, `app/e2e/inventar.spec.ts`, `app/playwright.config.ts`, `app/tsconfig.e2e.json`
- [x] `npm install -D @playwright/test@1.63.0 @axe-core/playwright@4.13.0` und Skript `"test:e2e": "playwright test"` in `app/package.json`
- [x] `.gitignore`: `playwright-report/`, `test-results/`, `blob-report/`
- [x] Lighthouse-Rezept als Skript

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Öffentliche URL lädt (Icons, Belegbild, Direktaufruf `/#/ausgaben`, `/#/ueber`, Fußzeile, PDF-Link mit `#page=`) | DEPL-02 | Repo hat noch keinen Remote; `*.github.io` aus dem Sandbox nicht erreichbar | Nach erstem Deploy URL im Browser öffnen und Liste abhaken |
| Texte deutsch und in Du-Anrede abgenommen | UI-06 | Heuristik hat Falschmeldungen; inhaltliche Abnahme | Text-Checkpoint mit Du-Test-Bericht |
| Belegseiten ohne Personennamen; Nutzungsrechte der Seitenbilder | DATA-04 / Datenschutz | Rechts-/Inhaltsfrage | Stellenplan-Seiten S. 284–290 sichten |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

## Validation Audit 2026-10-07

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
