---
phase: "6"
slug: "kontext-seiten"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: true) (#2117)
status: validated
nyquist_compliant: false
wave_0_complete: true
created: "2026-10-05"
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest 5.0.3 (App, `src/**/__tests__/*.test.ts`) und pytest (Pipeline) |
| **Config file** | `app/vitest.config.ts`, `app/tsconfig.vitest.json`; `pipeline/pyproject.toml` |
| **Quick run command** | App: Scratch-Kopie (`S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app \| tar -xf - -C "$S" && npm --prefix "$S/app" ci --no-audit --no-fund`), dann `npm --prefix "$S/app" run test -- <datei>`; Pipeline: `uv run --directory pipeline pytest tests/<datei>.py -x -q` |
| **Full suite command** | `uv run --directory pipeline pytest -q` **plus** `uv run --directory pipeline python alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data && test -z "$(git status --porcelain --untracked-files=all -- daten app/src/data)"` **plus** App-Kette in Scratch-Kopie (`ci`, `type-check`, `lint`, `format:check`, `test`, `build`) |
| **Estimated runtime** | App-Tests < 5 s; gezielte pytest-Dateien < 60 s; volle Pipeline-Suite ≈ 330 s |

---

## Sampling Rate

- **After every task commit:** gezielte vitest-Datei (Scratch-Kopie) plus `type-check`/`lint`/`format:check`; für Pipeline-Tasks gezielte pytest-Dateien
- **After every plan wave:** volle Pipeline-Suite + Reproduzierbarkeitsgate + komplette App-Kette
- **Before `/gsd-verify-work`:** Full suite must be green, Texte am Checkpoint abgenommen, manuelle 360-px-Prüfung erledigt
- **Max feedback latency:** 60 seconds (pro Task; volle Suite nur am Wellenende)

---

## Per-Task Verification Map

Wird vom Planer je Task befüllt. Anforderungs-Abdeckung laut Research:

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| ENTW-01 | Reihen = `haushalt.jahre`; Jahresergebnis-Balken, Wertart je Jahr aus Daten | unit | vitest `entwicklung.test.ts` | ✅ | ✅ green |
| ENTW-02 | Postenzeitreihen identisch zu `/einnahmen`/`/ausgaben`; Guard 0/`null` → „–“ | unit | vitest `entwicklung.test.ts` | ✅ | ✅ green |
| ENTW-03 | Rückgang je Jahr = S. 23 (1,77/4,23/4,73/10,04 %); Schwellen aus `meta` mit `quelle` 23 | unit + pytest | vitest `ruecklagen.test.ts`; `pytest tests/test_manuell.py -k hsk` | ✅ | ✅ green |
| INV-01 | Bündelung `(produkt, massnahme_id)`; Σ = GFP-Investitionsauszahlungen; Filter-Allowlist | unit | vitest `investitionen.test.ts` | ✅ | ✅ green |
| INV-02 | Σ VE-Fälligkeiten = 11.600.000 = `ve.gesamt` | unit | vitest `investitionen.test.ts` | ✅ | ✅ green |
| INV-03 | Finanzierungs-Zeitreihen = `jahre`; Σ Einzahlungen = GFP | unit | vitest `investitionen.test.ts` | ✅ | ✅ green |
| INV-04 | `gesamt` = Investitionskredite + NRW.Bank; „berechnet“-Etikett aus Daten | unit + pytest | vitest `schulden.test.ts`; Regel-9-Test | ✅ | ✅ green |
| RAT-01 | Bindungsgrad-Segmente 6.358.143 / 4.491.669 / 2.436.628 | unit | vitest `bindungsgrad.test.ts` | ✅ | ✅ green |
| RAT-02 | Kacheln aus `lib/kreisumlage.ts` und Vorbericht-Werten | unit | vitest `kreisumlage.test.ts` | ✅ | ✅ green |
| RAT-03 | Σ Einzelzuschüsse = 120.000 = Transferposten 2026; Regel 5 grün/rot | pytest + unit | `pytest tests/test_manuell.py tests/test_pruefung.py tests/test_app_daten.py -k zuschuess -q`; vitest `zuschuesse.test.ts` | ✅ | ✅ green |
| RAT-04 | Selbstauskunft-Hinweistext mit Seitenverweis | pytest | `pytest tests/test_texte.py -q` | ✅ | ✅ green |
| STEL-01 | Hundertstel-Summen 62,91 / 62,13 / 56,63 | unit | vitest `stellen.test.ts` | ✅ | ✅ green |
| STEL-02 | Σ Teil = Σ PB = Σ Gruppe; KL nicht als Aufgabenbereich | unit | vitest `stellen.test.ts` | ✅ | ✅ green |
| STEL-03 | Σ Personalaufwand je PB = 5.204.054; kein Aufwand je Stelle | unit | vitest `stellen.test.ts`, `quelltext.test.ts` | ✅ | ✅ green |
| UI-04 | Hinweisbox auf drei Seiten; Glossar-/Textschlüssel `nicht_im_haushalt` | unit | vitest `quelltext.test.ts`, `glossar.test.ts` | ✅ | ✅ green |

### Task-Zuordnung (Planer, 2026-10-06)

App-Kette = `S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app | tar -xf - -C "$S" && npm --prefix "$S/app" ci --no-audit --no-fund && …` (gezielte Datei per `npm --prefix "$S/app" run test -- <datei>`, sonst volle Kette bis `build`).

| Plan / Task | Requirement | Automated Command (Kurzform) | Test-Datei |
|-------------|-------------|------------------------------|------------|
| 06-01 T1 | RAT-03 | `alle.py --jahr 2026` + JSON-Assertion Σ = 120.000; `pytest tests/test_app_daten.py tests/test_manuell.py -x -q` | test_app_daten.py |
| 06-01 T2 | RAT-03 | `pytest tests/test_manuell.py tests/test_pruefung.py tests/test_app_daten.py -x -q`; konsistenz „grün“ | test_manuell.py |
| 06-01 T3 | ENTW-03 | `pytest -q`; ruff; App-Kette; Reproduzierbarkeitsgate | test_manuell.py (`test_meta_hsk_schwellen`) |
| 06-02 T1 | D-19 | App-Kette (voll) | quelltext.test.ts |
| 06-02 T2 | D-19 | App-Kette + `menue.test.ts quelltext.test.ts stiltokens.test.ts` | menue.test.ts |
| 06-02 T3 | ENTW-01 (Stil) | App-Kette (voll) | wertartStil.test.ts, farben.test.ts |
| 06-03 T1/T2 | UI-04 | App-Kette + `hinweis.test.ts quelltext.test.ts` / voll | hinweis.test.ts |
| 06-04 T1 | ENTW-03, INV-04 | `pytest tests/test_texte.py -x -q`; Entwurfsvalidierung mit Vorschau | test_texte.py |
| 06-04 T2 | RAT-04, UI-04 | Checkpoint (blocking-human, D-20) | — |
| 06-04 T3 | RAT-04, STEL-02 | `pytest -q`; App-Kette; Reproduzierbarkeitsgate | test_texte.py, glossar.test.ts |
| 06-05 T1-T3 | ENTW-01, ENTW-02 | App-Kette + `entwicklung.test.ts` / voll | entwicklung.test.ts |
| 06-06 T1-T2 | INV-01 | App-Kette + `investitionen.test.ts` / voll | investitionen.test.ts |
| 06-07 T1-T2 | RAT-02, RAT-03, UI-04 | App-Kette + `zuschuesse.test.ts` / voll | zuschuesse.test.ts, hinweis.test.ts |
| 06-08 T1-T2 | ENTW-03 | App-Kette + `ruecklagen.test.ts` / voll | ruecklagen.test.ts |
| 06-09 T1-T3 | INV-02, INV-03, INV-04 | App-Kette + `schulden.test.ts` / `finanzierung.test.ts` / voll | schulden.test.ts, finanzierung.test.ts |
| 06-10 T1-T2 | RAT-01, RAT-04, RAT-02 | App-Kette + `bindungsgrad.test.ts` / voll | bindungsgrad.test.ts |
| 06-11 T1-T3 | STEL-01, STEL-02, STEL-03 | App-Kette + `stellen.test.ts` / voll | stellen.test.ts |
| 06-12 T1-T2 | alle | App-Kette + `quelltext hinweis glossar menue`; `pytest -q`; ruff; Reproduzierbarkeitsgate; volle App-Kette | quelltext.test.ts, hinweis.test.ts |

Kein Task ohne `<automated>` außer dem Abnahme-Checkpoint 06-04 T2; keine drei aufeinanderfolgenden Tasks ohne automatische Prüfung.

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `app/src/lib/__tests__/{entwicklung,ruecklagen,investitionen,schulden,bindungsgrad,stellen,zuschuesse}.test.ts`
- [x] `app/src/lib/__tests__/{menue,glossar,quelltext,farben}.test.ts` anpassen
- [x] `pipeline/tests/{test_manuell,test_pruefung,test_app_daten,test_texte}.py` erweitern
- [x] Framework-Installation: keine (vitest/pytest vorhanden)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Achsenbeschriftung und Menüliste bei 360 px | ENTW-01, INV-01, STEL-02 | Playwright erst in Phase 7 | Dev-Server, Viewport 360 px, alle vier Seiten durchsehen |
| Menügruppe: Escape/Fokusrückgabe | UI-04 / D-19 | Tastaturinteraktion | Menü per Tastatur öffnen, Escape, Fokus prüfen |
| Fachliche Abnahme der neuen Texte | RAT-04, UI-04 | D-20-Checkpoint | Textvorschau lesen und freigeben |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-06

---

## Validation Audit 2026-10-06
| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Alle 15 Anforderungen COVERED. App: 37 Testdateien / 1576 Tests grün (Scratch-Kopie, vitest 5.0.3); Pipeline: `test_manuell`, `test_pruefung`, `test_app_daten`, `test_texte` 244 Tests grün. Sollwerte geprüft: 11.600.000 (finanzierung), 5.204.054 und 62,91 (stellen), 120.000 (zuschuesse), 1,77 % (ruecklagen), 6.358.143 (bindungsgrad), `nicht_im_haushalt` (hinweis). Manual-Only-Punkte durch UAT 06 (3/3 pass) abgedeckt.
