---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 12
subsystem: testing
tags: [lighthouse, a11y, github-pages, ci, deploy]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: "07-09 Mobil-Spec (360 px), 07-11 CI mit Smoke-Schritt und Deploy-Job"
provides:
  - "scripts/lighthouse-a11y.sh: einmaliger Lighthouse-Barrierefreiheitslauf je Route (nicht CI, nicht package.json)"
  - "Lighthouse-Tabelle: alle 11 Routen 100"
  - "CI-identisches Abschluss-Gate lokal grün, 360-px-UAT-Liste"
  - "Öffentliche App unter https://bitwerkstatt.github.io/ostbevern_money/ (erster grüner CI-Lauf inkl. deploy)"
affects: [milestone-abschluss]

plan_head_before: e927ed703b31c39edcd7e4fe85b837aa3954b7d8
plan_head_after: 7ca75917af1dddc3edf2dd73282dece9062b116f

actuals:
  tokens: 3000
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Einmal-Werkzeug im Scratch-Verzeichnis: lighthouse@13.5.0 mit --ignore-scripts, nie in app/package.json oder CI"

key-files:
  created:
    - scripts/lighthouse-a11y.sh
  modified:
    - README.md
    - .github/workflows/ci.yml

key-decisions:
  - "lighthouse wird nur nach bestätigter Paketprüfung (blocking-human) und nur als Einmal-Lauf im Scratch-Verzeichnis genutzt (D-13, D-14)"
  - "Der echte Repository-Name ist ostbevern_money (Unterstrich); README und ci.yml-Kommentar wurden angepasst, Paket- und Theme-Namen ostbevern-money(-app) bleiben unverändert"

requirements-completed: [A11Y-04, A11Y-03, DEPL-02]

coverage:
  - id: D1
    description: "Lighthouse-Barrierefreiheit >= 95 auf allen 11 Routen (gemessen 100)"
    requirement: "A11Y-04"
    verification:
      - kind: other
        ref: "bash scripts/lighthouse-a11y.sh (Lighthouse 13.5.0, Playwright Chromium, 2026-10-07)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Alle Seiten ab 360 px nutzbar (kein horizontaler Scroll, keine Ziele unter 44 px)"
    requirement: "A11Y-03"
    verification:
      - kind: e2e
        ref: "playwright --project=mobil (14 Tests, Docker mcr.microsoft.com/playwright:v1.63.0-noble)"
        status: pass
    human_judgment: false
  - id: D3
    description: "CI-identisches Abschluss-Gate (Pipeline und App) lokal grün"
    verification:
      - kind: integration
        ref: "ruff, pytest 631, alle.py --jahr 2026, npm ci, type-check, lint, format:check, vitest 1967, build, playwright ci+mobil 90"
        status: pass
    human_judgment: false
  - id: D4
    description: "Axe-DevTools-Prüfung der geöffneten Quelle-Leiste auf /#/ und Sichtprüfung zweier Routen bei 360 px"
    verification: []
    human_judgment: true
    rationale: "Browser-Erweiterung und Sichtprüfung; die Nutzerin bzw. der Nutzer hat dazu nicht gesondert berichtet (nicht separat bestätigt); automatisiert deckt axe im Smoke-Test die offene Leiste ab"
  - id: D5
    description: "App öffentlich erreichbar, erster CI-Lauf grün in allen Jobs, Pages-Quelle GitHub Actions"
    requirement: "DEPL-02"
    verification:
      - kind: integration
        ref: "https://github.com/bitwerkstatt/ostbevern_money/actions/runs/37576891540 (pipeline, app, deploy: success)"
        status: pass
    human_judgment: true
    rationale: "Das Sandbox-Netz erreicht github.io nicht; die Browserprüfungen (Schritt 5) stützen sich auf die Antwort der Nutzerin bzw. des Nutzers 'veröffentlicht'"

duration: "n/a (Fortsetzung über mehrere Agenten und Nutzer-Checkpoints)"
completed: 2026-10-07
status: complete
---

# Phase 7 Plan 12: Lighthouse, Abschluss-Gate und Veröffentlichung Summary

**Lighthouse-Barrierefreiheit 100 auf allen 11 Routen (einmaliger Lauf mit lighthouse@13.5.0 im Scratch-Verzeichnis), CI-identisches Gate grün und die App unter https://bitwerkstatt.github.io/ostbevern_money/ veröffentlicht.**

## Performance

- **Duration:** n/a (Fortsetzung über mehrere Agenten und Nutzer-Checkpoints)
- **Completed:** 2026-10-07
- **Tasks:** 3 (Task 1 und 3 Checkpoints, Task 2 auto)
- **Files modified:** 3 (`scripts/lighthouse-a11y.sh` neu, `README.md`, `.github/workflows/ci.yml`)

## Accomplishments

- Einmal-Skript `scripts/lighthouse-a11y.sh`: Scratch-Kopie, Production-Build, `vite preview` im Playwright-Image, Lighthouse (`--only-categories=accessibility`) je Route.
- Alle 11 Routen erreichen 100 Punkte, kein fehlschlagendes binäres Audit, kein Fix nötig.
- CI-identisches Abschluss-Gate und Playwright `ci` + `mobil` grün; 360-px-UAT-Liste vollständig.
- Öffentliche Veröffentlichung: erster realer CI-Lauf grün (pipeline, app, deploy), Pages-Quelle „GitHub Actions“.

## Paketprüfung lighthouse

Task 1 (`checkpoint:human-verify`, `gate="blocking-human"`): lighthouse@13.5.0 (Google/GoogleChrome, github.com/GoogleChrome/lighthouse, kein postinstall; im Audit SUS nur wegen nicht erreichbarer Download-Zahlen und der jungen Version). Antwort der Nutzerin bzw. des Nutzers, wörtlich:

> approved

Vor dieser Freigabe wurde nichts installiert. Installation danach nur als `lighthouse@13.5.0` mit `--ignore-scripts` im Scratch-Verzeichnis.

## Lighthouse je Route (A11Y-04)

Lighthouse 13.5.0, Chromium aus dem Playwright-Image `mcr.microsoft.com/playwright:v1.63.0-noble`, Kategorie accessibility, Production-Build über `vite preview`.

| Route | Wert | Datum |
|-------|------|-------|
| `/#/` | 100 | 2026-10-07 |
| `/#/einnahmen` | 100 | 2026-10-07 |
| `/#/ausgaben` | 100 | 2026-10-07 |
| `/#/produkt/010601` | 100 | 2026-10-07 |
| `/#/geldfluss` | 100 | 2026-10-07 |
| `/#/entwicklung` | 100 | 2026-10-07 |
| `/#/investitionen` | 100 | 2026-10-07 |
| `/#/rat-entscheidet` | 100 | 2026-10-07 |
| `/#/stellenplan` | 100 | 2026-10-07 |
| `/#/glossar` | 100 | 2026-10-07 |
| `/#/ueber` | 100 | 2026-10-07 |

Kein fehlschlagendes binäres Audit auf irgendeiner Route. Die Überschriftenreihenfolge auf `/glossar` war bereits durch 07-04 behoben, daher war kein Fix nötig. Hinweis (RESEARCH A6): Werte aus dem Playwright-Chromium können leicht von einem lokalen Chrome abweichen.

## CI-identisches Abschluss-Gate

Alle Läufe lokal in einer Scratch-Kopie bzw. im Docker-Image, nie `npm ci` im Haupt-Checkout.

| Prüfung | Ergebnis |
|---------|----------|
| `ruff check`, `ruff format --check` (Pipeline, 51 Dateien) | sauber |
| `pytest` | 631 passed |
| `alle.py --jahr 2026` | Exit 0 („2496 Belege, 33 ohne Markierung, 231 Seiten, 0 Bilder neu gerendert“) |
| `git diff` / `git status` für `daten`, `app/src/data`, `app/public/quellen` | sauber |
| App (Scratch-Kopie): `npm ci`, `type-check`, `lint`, `format:check` | grün |
| `vitest` | 1967 passed |
| `build` | grün |
| Playwright im Docker (`--project=ci --project=mobil`) | 90 passed (76 ci, 14 mobil) |
| Akzeptanz: Skript ausführbar, enthält `lighthouse@13.5.0` und `only-categories=accessibility` | erfüllt |
| lighthouse nicht in `app/package.json`, `package-lock.json`, `ci.yml` | erfüllt |

## UAT-Liste 360 px (A11Y-03)

Viewport 360 × 640, kein horizontaler Scroll, kein Ziel unter 44 px (Mobil-Lauf aus 07-09, hier erneut gelaufen).

| Route / Zustand | Geprüfte Ziele | Ergebnis |
|-----------------|----------------|----------|
| `/` | 9 | bestanden |
| `/einnahmen` | 44 | bestanden |
| `/ausgaben` | 51 | bestanden |
| `/geldfluss` | 2 | bestanden |
| `/entwicklung` | 2 | bestanden |
| `/investitionen` | 64 | bestanden |
| `/rat-entscheidet` | 23 | bestanden |
| `/stellenplan` | 24 | bestanden |
| `/glossar` | 2 | bestanden |
| `/ueber` | 2 | bestanden |
| `/produkt/010601` | 38 | bestanden |
| `/` mit geöffneter Quelle-Leiste | 9 | bestanden |
| `/` mit geöffnetem Menü-Drawer | 18 | bestanden |
| `/stellenplan` mit Quelle-Leiste (Querformat) | 11 | bestanden |

Offene manuelle Prüfungen laut `<human-check>` (07-09 D9): axe DevTools auf der geöffneten Quelle-Leiste an `/#/` und zwei Routen bei 360 px per Auge. Dazu hat die Nutzerin bzw. der Nutzer nicht gesondert berichtet; Status: **human_judgment, nicht separat bestätigt**. Die automatische axe-Prüfung im Smoke-Test (07-11) deckt die offene Leiste ab.

## Veröffentlichung

Task 3 (`checkpoint:human-action`, `gate="blocking"`): Die Nutzerin bzw. der Nutzer hat das Repository angelegt, die Pages-Quelle gesetzt und `main` gepusht. Antwort, wörtlich:

> veröffentlicht

Vom Orchestrator per `gh` verifiziert:

- Repository: https://github.com/bitwerkstatt/ostbevern_money (mit **Unterstrich**; Plan und README nannten fälschlich `ostbevern-money`, siehe Abweichung 1). Remote `origin` = `git@github.com:bitwerkstatt/ostbevern_money.git`, `main` gepusht und synchron.
- Workflow-Lauf „CI“ auf Head `b46259f`: https://github.com/bitwerkstatt/ostbevern_money/actions/runs/37576891540. Jobs `pipeline` success, `app` success, `deploy` success. Das ist zugleich der erste reale CI-Lauf (offener STATE-Blocker aus Phase 1).
- GitHub Pages: `build_type` „workflow“ (Source „GitHub Actions“).
- **Öffentliche URL: https://bitwerkstatt.github.io/ostbevern_money/**

Einschränkung: Die Sandbox erreicht github.io nicht (Firewall). Die Browserprüfungen aus Schritt 5 (kein 404 im Netzwerk-Panel, direkter Reload von `/#/ausgaben` und `/#/ueber`, Quelle-Leiste mit Bild, Fußzeile mit mail@thomas-manthey.de, PDF-Link) stützen sich auf die Antwort „veröffentlicht“, nicht auf eine eigene Messung. Die App nutzt `base: './'` und den Hash-Router, daher hängt keine Laufzeitlogik am Pages-Unterpfad.

## Task Commits

1. **Task 1: Paketprüfung lighthouse@13.5.0** - kein Commit (Checkpoint, Antwort „approved“)
2. **Task 2: Lighthouse je Route, Abschluss-Gate, UAT-Liste** - `b46259f` (feat)
3. **Task 3: Veröffentlichung** - kein Commit des Executors (Aktion der Nutzerin bzw. des Nutzers, D-10); Korrektur des Repository-Namens: `7ca7591` (docs)

**Plan metadata:** folgt als `docs(07-12): complete Lighthouse und Veröffentlichung plan`

## Files Created/Modified

- `scripts/lighthouse-a11y.sh` - Einmal-Lauf von Lighthouse (Accessibility) je Route im Playwright-Image
- `README.md` - Abschnitt „Veröffentlichung auf GitHub Pages“ auf den echten Namen `ostbevern_money`
- `.github/workflows/ci.yml` - Kommentar zum Repository-Namen angepasst (nur Kommentar, keine Wirkung)

## Decisions Made

- lighthouse nur als Einmal-Werkzeug im Scratch-Verzeichnis, nie als Abhängigkeit oder CI-Schritt (D-13, D-14).
- Paket- und Theme-Namen `ostbevern-money-app` (`app/package.json`, `package-lock.json`) und `CHART_THEME = 'ostbevern-money'` (`echartsTheme.ts`) sind interne Bezeichner und bleiben unverändert.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Falscher Repository-Name in README und ci.yml-Kommentar**
- **Found during:** Task 3 (Veröffentlichung, Prüfung durch den Orchestrator)
- **Issue:** Plan und README (aus 07-11) gingen von `ostbevern-money` aus; das echte Repository heißt `ostbevern_money`. README nannte dadurch falschen Namen, falschen Remote und falsche Pages-URL.
- **Fix:** Alle Vorkommen in README.md (Repository-Name, `git remote add`-Befehl, Pages-URL) und der Namenshinweis im ci.yml-Kommentar auf `ostbevern_money` geändert.
- **Files modified:** `README.md`, `.github/workflows/ci.yml` (nur Kommentar)
- **Verification:** `grep -rn "ostbevern-money"` über README, `.github`, `app` (ohne `node_modules`) findet nur noch Paket-/Theme-Namen. Weder Laufzeitpfad noch Test hängt am Pages-Unterpfad (App nutzt `base './'` und Hash-Router).
- **Committed in:** `7ca7591`

---

**Total deviations:** 1 auto-fixed (1 bug, reine Dokumentation)
**Impact on plan:** Nur Texte; kein Einfluss auf Build, Tests oder Daten.

## Issues Encountered

- Der Lighthouse-Lauf musste im Docker-Image des Playwright-Chromiums laufen (Sandbox ohne eigenen Chrome); durch das Skript abgedeckt, keine Wiederholung nötig.
- github.io ist aus der Sandbox nicht erreichbar, daher die öffentliche Prüfung nur über die Nutzerantwort und die `gh`-Befunde (siehe „Veröffentlichung“).

## User Setup Required

Erledigt durch die Nutzerin bzw. den Nutzer (Repository, Pages-Quelle, Push). Keine weitere Konfiguration offen.

## Next Phase Readiness

- Letzter Plan der Phase 7; die Phase ist bereit für Verifikation und den Milestone-Abschluss.
- Offen (nicht blockierend): axe-DevTools-Handprüfung der offenen Quelle-Leiste und Sichtprüfung zweier Routen bei 360 px.

## Known Stubs

Keine.

## Self-Check: PASSED

- `scripts/lighthouse-a11y.sh` vorhanden, ausführbar; Commit `b46259f` und `7ca7591` im Verlauf von HEAD (`git merge-base --is-ancestor`).

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-07*
