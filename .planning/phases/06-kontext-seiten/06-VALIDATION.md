---
phase: "6"
slug: "kontext-seiten"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| ENTW-01 | Reihen = `haushalt.jahre`; Jahresergebnis-Balken, Wertart je Jahr aus Daten | unit | vitest `entwicklung.test.ts` | ❌ W0 | ⬜ pending |
| ENTW-02 | Postenzeitreihen identisch zu `/einnahmen`/`/ausgaben`; Guard 0/`null` → „–“ | unit | vitest `entwicklung.test.ts` | ❌ W0 | ⬜ pending |
| ENTW-03 | Rückgang je Jahr = S. 23 (1,77/4,23/4,73/10,04 %); Schwellen aus `meta` mit `quelle` 23 | unit + pytest | vitest `ruecklagen.test.ts`; `pytest tests/test_manuell.py -k hsk` | ❌ W0 | ⬜ pending |
| INV-01 | Bündelung `(produkt, massnahme_id)`; Σ = GFP-Investitionsauszahlungen; Filter-Allowlist | unit | vitest `investitionen.test.ts` | ❌ W0 | ⬜ pending |
| INV-02 | Σ VE-Fälligkeiten = 11.600.000 = `ve.gesamt` | unit | vitest `investitionen.test.ts` | ❌ W0 | ⬜ pending |
| INV-03 | Finanzierungs-Zeitreihen = `jahre`; Σ Einzahlungen = GFP | unit | vitest `investitionen.test.ts` | ❌ W0 | ⬜ pending |
| INV-04 | `gesamt` = Investitionskredite + NRW.Bank; „berechnet“-Etikett aus Daten | unit + pytest | vitest `schulden.test.ts`; Regel-9-Test | ❌ W0 | ⬜ pending |
| RAT-01 | Bindungsgrad-Segmente 6.358.143 / 4.491.669 / 2.436.628 | unit | vitest `bindungsgrad.test.ts` | ❌ W0 | ⬜ pending |
| RAT-02 | Kacheln aus `lib/kreisumlage.ts` und Vorbericht-Werten | unit | vitest `kreisumlage.test.ts` | ✅ erweitern | ⬜ pending |
| RAT-03 | Σ Einzelzuschüsse = 120.000 = Transferposten 2026; Regel 5 grün/rot | pytest + unit | `pytest tests/test_manuell.py tests/test_pruefung.py tests/test_app_daten.py -k zuschuess -q`; vitest `zuschuesse.test.ts` | ❌ W0 | ⬜ pending |
| RAT-04 | Selbstauskunft-Hinweistext mit Seitenverweis | pytest | `pytest tests/test_texte.py -q` | ✅ erweitern | ⬜ pending |
| STEL-01 | Hundertstel-Summen 62,91 / 62,13 / 56,63 | unit | vitest `stellen.test.ts` | ❌ W0 | ⬜ pending |
| STEL-02 | Σ Teil = Σ PB = Σ Gruppe; KL nicht als Aufgabenbereich | unit | vitest `stellen.test.ts` | ❌ W0 | ⬜ pending |
| STEL-03 | Σ Personalaufwand je PB = 5.204.054; kein Aufwand je Stelle | unit | vitest `stellen.test.ts`, `quelltext.test.ts` | ❌ W0 | ⬜ pending |
| UI-04 | Hinweisbox auf drei Seiten; Glossar-/Textschlüssel `nicht_im_haushalt` | unit | vitest `quelltext.test.ts`, `glossar.test.ts` | ✅ erweitern | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/src/lib/__tests__/{entwicklung,ruecklagen,investitionen,schulden,bindungsgrad,stellen,zuschuesse}.test.ts`
- [ ] `app/src/lib/__tests__/{menue,glossar,quelltext,farben}.test.ts` anpassen
- [ ] `pipeline/tests/{test_manuell,test_pruefung,test_app_daten,test_texte}.py` erweitern
- [ ] Framework-Installation: keine (vitest/pytest vorhanden)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Achsenbeschriftung und Menüliste bei 360 px | ENTW-01, INV-01, STEL-02 | Playwright erst in Phase 7 | Dev-Server, Viewport 360 px, alle vier Seiten durchsehen |
| Menügruppe: Escape/Fokusrückgabe | UI-04 / D-19 | Tastaturinteraktion | Menü per Tastatur öffnen, Escape, Fokus prüfen |
| Fachliche Abnahme der neuen Texte | RAT-04, UI-04 | D-20-Checkpoint | Textvorschau lesen und freigeben |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
