---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 14
subsystem: ui-ci
tags: [css-grid, playwright, fonts, github-actions, a11y, gap-closure]
gap_closure: true
gap_ids: [G-07-2]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: "07-13: Kachelraster, kacheln.spec.ts, Entscheidungen G-01 bis G-06"
provides:
  - "scripts/e2e-wie-ci.sh: Playwright im Image mit dem Schriftpaket des Runners (gepinnt, SHA-256 geprüft)"
  - "basis.css: li-Reset und --om-kachel-mindestbreite = 13,25rem, unter DejaVu Sans Bold kalibriert"
  - "kacheln.spec.ts: Spaltensprünge, li-Check, Check schmalste Spur, Schriftprotokoll, Selbsttest"
  - "ci.yml: app-Job auf ubuntu-24.04"
affects: [07-UAT, 07-VERIFICATION, deploy]

actuals:
  tokens: 31000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Messumgebung = CI-Schrift: Browser-Messungen laufen nur über scripts/e2e-wie-ci.sh"
    - "Mindestspur als eine Custom Property, vom Test im Browser aufgelöst"

key-files:
  created:
    - scripts/e2e-wie-ci.sh
  modified:
    - app/e2e/kacheln.spec.ts
    - app/src/styles/basis.css
    - .github/workflows/ci.yml
    - README.md
    - .planning/phases/07-feinschliff-und-ver-ffentlichung/07-UI-SPEC.md

key-decisions:
  - "li des Kachelrasters ohne Außenabstand (Web-Awesome-Einzug von 18 px zurückgesetzt)"
  - "--om-kachel-mindestbreite = 13,25rem: kleinster Kandidat mit mindestens 16 px Spurreserve unter DejaVu Sans Bold"
  - "Kalibrierumgebung = CI-Schrift über scripts/e2e-wie-ci.sh; app-Job auf ubuntu-24.04 festgelegt"
  - "Spaltensprünge 488, 732, 968, 1204, 1440 px als eigene Sweep-Breiten mit Selbsttest"

patterns-established:
  - "Die 16-px-Reserve bleibt eine Auswahlregel, keine Assertion"

requirements-completed: [A11Y-03, QUAL-02, DEPL-01, DEPL-02]

coverage:
  - id: D1
    description: "Rote Ausgangsmessung in der CI-Schrift reproduziert den GitHub-Befund byte-identisch"
    requirement: QUAL-02
    verification:
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh <app> --project=ci e2e/kacheln.spec.ts (vor dem Fix: 1 failed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Kacheln auf allen vier Routen passen bei allen Sweep-Breiten und in die schmalste Spur (DejaVu Sans)"
    requirement: A11Y-03
    verification:
      - kind: e2e
        ref: "app/e2e/kacheln.spec.ts, Projekt ci, über scripts/e2e-wie-ci.sh"
        status: pass
    human_judgment: false
  - id: D3
    description: "app-Job auf ubuntu-24.04, nur eine Zeile plus Kommentar geändert"
    requirement: DEPL-01
    verification:
      - kind: other
        ref: "git diff 840c372 -- .github/workflows/ci.yml"
        status: pass
    human_judgment: false
  - id: D4
    description: "GitHub Actions grün inklusive deploy und öffentliche URL zeigt die Kachelkorrektur (UAT-Test 2)"
    requirement: DEPL-02
    verification: []
    human_judgment: true
    rationale: "Push und Prüfung der öffentlichen URL sind Sache des Nutzers (D-10)"
  - id: D5
    description: "Kacheln auf dem eigenen Gerät bei 360, 400, 600, 768 und 1280 px (UAT-Test 1)"
    requirement: A11Y-03
    verification: []
    human_judgment: true
    rationale: "Gerätschriften weichen von der CI-Schrift ab; Sichtprüfung durch den Nutzer"

plan_head_before: a15ac6ada0e4abd2f15b0f7c861596cbb516da71
plan_head_after: 93b8ec596d164a07b3f55206f58d889a8367fe57
duration: 11min
completed: 2026-10-07
status: complete
---

# Phase 7 Plan 14: Kachelraster gegen die CI-Schrift kalibriert (G-07-2) Summary

**Das GitHub-Ergebnis „Kreisumlage ragt 6,0 px“ ist lokal byte-identisch reproduziert und behoben: li-Einzug zurückgesetzt, Mindestspur unter DejaVu Sans Bold auf 13,25rem kalibriert, Messumgebung über `scripts/e2e-wie-ci.sh` mit der CI-Schrift gleichgezogen, app-Job auf `ubuntu-24.04` festgelegt.**

## Performance

- **Duration:** 11 min
- **Tasks:** 3 (Task 1 Tracer, Task 2 und 3 auto)
- **Files modified:** 6 (davon 1 neu)

## Accomplishments

- Wurzelursache behoben: Schrift (DejaVu Sans Bold 164,0 px statt WenQuanYi 141,1 px für „rd. 10,1 Mio. €“) und li-Einzug (18 px) zusammen.
- Lokale Messung und CI messen dieselbe Schrift; der Test protokolliert sie je Route.
- Der Sweep trifft jeden Spaltensprung der Mindestspur, abgesichert durch Selbsttest und eine viewportunabhängige Prüfung der schmalsten Spur.
- `.om-zahl` ist byte-identisch (nowrap), die Betragsschrift bleibt `--wa-font-size-l`, Label „Quelle“ unverändert.

## Rote Ausgangsmessung in CI-Schrift (vor dem Fix)

Unveränderter Code (Stand 840c372), `scripts/e2e-wie-ci.sh <scratch>/app --project=ci e2e/kacheln.spec.ts`, Schriftzeile `Schrift für sans-serif: DejaVuSans.ttf: "DejaVu Sans" "Book"`:

```
Error: /rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px)
  1 failed
    [ci] › e2e/kacheln.spec.ts:324:5 › … › Kacheln und Seitenbreite: /rat-entscheidet
  4 passed (5.9s)
```

Das ist der GitHub-Befund (Lauf 37589932223) byte-identisch. Tabellenzeilen `/rat-entscheidet` (Spalten: Route, Breite, Kacheln, Spalten, breitester Betrag, Betragsbreite, Inhalt, Reserve, scrollWidth):

| Route | Breite | Spalten | Betrag | Betragsbreite | Inhalt | Reserve |
|-------|--------|---------|--------|---------------|--------|---------|
| /rat-entscheidet | 360 | 1 | rd. 10,1 Mio. € | 164.0 | 262.0 | 98.0 |
| /rat-entscheidet | 400 | 1 | rd. 10,1 Mio. € | 164.0 | 302.0 | 138.0 |
| /rat-entscheidet | 480 | 2 | rd. 10,1 Mio. € | 164.0 | 158.0 | -6.0 |
| /rat-entscheidet | 560 | 2 | rd. 10,1 Mio. € | 164.0 | 198.0 | 34.0 |
| /rat-entscheidet | 600 | 2 | rd. 10,1 Mio. € | 164.0 | 218.0 | 54.0 |
| /rat-entscheidet | 700 | 2 | rd. 10,1 Mio. € | 164.0 | 264.0 | 100.0 |
| /rat-entscheidet | 768 | 3 | rd. 10,1 Mio. € | 164.0 | 174.0 | 10.0 |
| /rat-entscheidet | 1024 | 4 | rd. 10,1 Mio. € | 164.0 | 176.0 | 12.0 |
| /rat-entscheidet | 1280 | 4 | rd. 10,1 Mio. € | 164.0 | 220.0 | 56.0 |
| /rat-entscheidet | 1440 | 4 | rd. 10,1 Mio. € | 164.0 | 220.0 | 56.0 |

### Rote Ausgangsmessung 2: erweiterte Spec gegen den unveränderten CSS-Stand

4 failed, 1 passed (alle vier Kachelrouten rot). 408 Befunde „li hat Außenabstand …“ (jede Kachel jeder Route bei jeder Breite), außerdem auf `/rat-entscheidet`:

```
/rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px)
/rat-entscheidet @ 720 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px)
/rat-entscheidet @ 952 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px)
```

Die zuvor ungetesteten Sprünge 720 und 952 px sind damit als zweite und dritte Fehlerstelle belegt. Alle vier Schriftzeilen: DejaVu Sans (DejaVuSans-Bold).

## Kalibrierung der Mindestspur X unter DejaVu Sans Bold

Ein Scratch-Lauf je Kandidat (`kacheln.spec.ts` mit li-Reset, über `scripts/e2e-wie-ci.sh`). Die Spurreserve ist viewportunabhängig; ihr Minimum liegt für alle Kandidaten bei „rd. 10,1 Mio. €“ (164,0 px) auf `/rat-entscheidet` (bei jeder Breite gleich).

| X | Ergebnis | kleinste Spurreserve | Stelle |
|---|----------|----------------------|--------|
| 13rem (208 px) | grün, 5 passed | 12,0 px | /rat-entscheidet, „rd. 10,1 Mio. €“ |
| **13,25rem (212 px)** | **grün, 5 passed** | **16,0 px** | /rat-entscheidet, „rd. 10,1 Mio. €“ |
| 13,5rem (216 px) | grün, 5 passed | 20,0 px | /rat-entscheidet, „rd. 10,1 Mio. €“ |
| 13,75rem (220 px) | grün, 5 passed | 24,0 px | /rat-entscheidet, „rd. 10,1 Mio. €“ |
| 14rem (224 px) | grün, 5 passed | 28,0 px | /rat-entscheidet, „rd. 10,1 Mio. €“ |

**Gewählt: 13,25rem**, der kleinste Kandidat mit mindestens 16,0 px Spurreserve. 13rem ist grün, verfehlt aber die Auswahlregel (12,0 px).

Vergleich mit 07-13: „rd. 10,1 Mio. €“ war dort mit der CJK-Ersatzschrift WenQuanYi Zen Hei 141,1 px breit; unter DejaVu Sans Bold (CI) sind es 164,0 px, rund 16 % mehr.

**Spaltensprünge (SPALTENSPRUENGE)** für 212 px Mindestspur, Lücke 16 px unter 700 px, 24 px ab 700 px, 48 px Seitenpolster: 488, 732, 968, 1204, 1440 px. Auf `/` ist an jeder dieser Breiten die engste Spur 212,0 px und der Inhalt 180,0 px (= 212 − 32), der Selbsttest ist grün.

## Lesbarkeit je Kachelroute (G-06)

Je Route beim ersten Spaltensprung (488 px, zwei Spalten), Schrift DejaVu Sans Bold:

| Route | Spalten | breitester Betrag | Breite | Inhalt der Kachel | Reserve | passt |
|-------|---------|-------------------|--------|-------------------|---------|-------|
| / | 2 | -2,35 Mio. € | 133,6 px | 180,0 px | 46,4 px | ja |
| /investitionen | 2 | 7,71 Mio. € | 125,3 px | 180,0 px | 54,7 px | ja |
| /rat-entscheidet | 2 | rd. 10,1 Mio. € | 164,0 px | 180,0 px | 16,0 px | ja |
| /stellenplan | 2 | 62,91 VZÄ | 115,7 px | 180,0 px | 64,3 px | ja |

Schriftzeilen der Läufe: `Schrift der Beträge auf /`, `/investitionen`, `/rat-entscheidet`, `/stellenplan`: jeweils `DejaVu Sans (DejaVuSans-Bold)`.

## Gate-Ergebnisse (CI-identisch, frische Scratch-Kopie)

- `npm ci`, `type-check`, `lint`, `format:check`: sauber. (`prettier --check e2e/kacheln.spec.ts` meldet eine vor diesem Plan bestehende Umbruchstelle in Zeile 227; `format:check` prüft laut Skript nur `src/`, nicht angefasst.)
- vitest: 45 Dateien, 1968 Tests bestanden.
- `npm run build`: grün.
- Playwright über `scripts/e2e-wie-ci.sh --project=ci --project=mobil --project=texte`: 96 passed, `textliste.md` nicht leer (1464 Zeilen), vier DejaVu-Schriftzeilen.
- Job `pipeline` (uv sync, ruff, der rund sechsminütige pytest, alle.py) **übersprungen**. Grund: `git diff 840c372` über `pipeline/`, `daten/`, `app/src/data/` und `app/public/` ist leer, es ändert sich nichts, was der Job abdeckt.
- Scope-Wächter: unter `app/src` unterscheidet sich nur `app/src/styles/basis.css` von 840c372; `package.json`, `package-lock.json`, `playwright.config.ts`, `SPEZIFIKATION.md`, `REQUIREMENTS.md`, `07-REVIEW-DISPOSITION.md` und `07-UAT.md` sind unverändert.
- `ci.yml`-Diff: eine geänderte Zeile (`runs-on: ubuntu-latest` zu `runs-on: ubuntu-24.04` im Job `app`) plus vier Kommentarzeilen. Playwright-Installationsschritt, Jobs `pipeline` und `deploy`, Rechte und SHA-Pins unverändert.
- Der Executor hat nichts gepusht, kein Repository angelegt und keinen Workflow gestartet (D-10). CR-02, WR-01 bis WR-05, IN-01 bis IN-08, `REQUIREMENTS.md` und `07-UAT.md` wurden nicht angefasst.

## Offen (Mensch)

1. **Push und öffentliche URL (UAT-Test 2).** Du pushst `main`. Im Reiter Actions muss der Lauf grün sein inklusive `deploy`; im Log des Jobs `app` zeigt der Schritt „Smoke-Test (Playwright + axe)“ vier Zeilen „Schrift der Beträge auf …: DejaVu Sans“, und `kacheln.spec.ts` besteht. Danach auf https://bitwerkstatt.github.io/ostbevern_money/ prüfen: Kacheln bündig mit den Überschriften, Beträge und „Quelle“ in der grauen Kachel, kein 404 (Icons, Belegbild unter `/ostbevern_money/quellen/`), Neuladen von `/#/ausgaben` und `/#/ueber` geht, Quelle-Drawer zeigt sein Bild, Fußzeile zeigt die Kontaktadresse, der PDF-Link öffnet die Gemeindedatei.
2. **Gerät (UAT-Test 1).** Auf dem eigenen Gerät bei 360, 400, 600, 768 und 1280 px: jeder Betrag und jeder Knopf „Quelle“ in der Kachel, kein seitliches Scrollen (die Spur ist breiter geworden).

Beides markiert der Executor nicht als verifiziert.

## Task Commits

1. **Task 1: Tracer, CI-Schrift lokal, li-Einzug zurückgesetzt, Sprünge 720/952** - `67db9e8` (fix)
2. **Task 2: Mindestspur kalibriert, schmalste Spur und Spaltensprünge** - `435ee8b` (fix)
3. **Task 3: app-Job auf ubuntu-24.04, Vertrag und README** - `93b8ec5` (fix)

## Decisions Made

- 13,25rem als `--om-kachel-mindestbreite`, siehe Kalibrierungstabelle.
- Die Spaltensprünge stehen als feste Liste im Test (mit Formel im Kommentar) statt aus CSS abgeleitet, damit der Selbsttest tatsächlich gegen das CSS prüft.

## Deviations from Plan

None - plan executed exactly as written. (Kleine Umsetzungsdetails: Das Schriftprotokoll steht in jedem Routen-Test vor dem Sweep; der Describe-Titel blieb unverändert.)

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. (Neue Angriffsfläche: Download des Schriftpakets in `scripts/e2e-wie-ci.sh`, im Plan als T-07-32 erfasst und durch Version und SHA-256 abgesichert.)

## Next Phase Readiness

GitHub Actions kann grün werden und deployen. Nach dem Push durch den Nutzer bleiben UAT-Test 2 und die Gerätprüfung offen; `/gsd-verify-work` gleicht G-07-2 ab.

## Self-Check: PASSED

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-07*
