---
phase: 05-leitfragen-seiten
plan: 07
subsystem: app-rahmen
tags: [kopfmenue, drawer, skip-link, fusszeile, konfiguration, platzhalter, a11y, ui-03]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-03: Entscheidung Kontakt/PDF-URL spaeter (Platzhalter); 05-04: useJahr/jahrLink, Router mit sechs Routen, Web-Awesome-Komponenten in main.ts"
provides:
  - "app/src/config.ts: KONTAKT_EMAIL, ORIGINAL_PDF_URL (Platzhalter auf .invalid), istPlatzhalter(wert)"
  - "format.ts: datum(iso) (UTC, de-DE, ungueltig -> Gedankenstrich)"
  - "lib/menue.ts: MENUE und MenueEintrag (datengetriebene Menueliste, Phase 6 erweitert um Gruppe Mehr wissen)"
  - "App.vue: Kopfzeile mit Wortmarke, Menue, mobilem Drawer, deutschem Skip-Link; Fusszeile mit Datenstand, Original-PDF, Hinweis, Kontakt, Muenster-Dank"
  - "app/public/icons/solid/arrow-up-right-from-square.svg (selbst gehostet, FA Free 7.3.1 mit Lizenzkommentar)"
affects: [05-08, 05-09, 05-10, 05-11, 05-12, 05-13, phase-06, phase-07]

actuals:
  tokens: 21000
  tasks: 2
  commits: 4
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: 1c140773bb9196b54edfb010877eef04d63d1618
commits: 4

tech-stack:
  added: []
  patterns:
    - "Kontakt und PDF-URL nur in config.ts; Platzhalter auf der reservierten Domain .invalid, per istPlatzhalter erkennbar (Phase-7-Gate)"
    - "Quelltext-Test (node:fs liest App.vue) sichert Prohibitions: keine fest eingetragene Adresse/URL, rel noopener noreferrer an jedem externen Link"
    - "Skip-Link: Capture-Klick auf wa-page, Erkennung ueber composedPath() und part=skip-to-content"

key-files:
  created:
    - app/src/config.ts
    - app/src/lib/menue.ts
    - app/src/lib/__tests__/config.test.ts
    - app/src/lib/__tests__/menue.test.ts
    - app/public/icons/solid/arrow-up-right-from-square.svg
  modified:
    - app/src/App.vue
    - app/src/charts/format.ts
    - app/src/charts/__tests__/format.test.ts

key-decisions:
  - "Skip-Link-Variante: composedPath()-Abfang (Primaervariante des Plans); die Rueckfall-Variante mit eigenem Link wurde nicht gebraucht, aber auch nicht im Browser belegt (kein Browser im Sandkasten)"
  - "Menue-Schalter als natives button statt wa-button, damit aria-label, aria-expanded und aria-controls wirklich am fokussierbaren Element liegen"
  - "Nach einem Seitenwechsel bekommt die neue Seite den Fokus (Router), nach Escape/Schliessen-Knopf der Menue-Schalter"

requirements-completed: [UI-03]

coverage:
  - id: D1
    description: "Fusszeile: Datenstand (Haushaltsjahr, Beschlussdatum aus meta.json), Original-PDF-Link, Hinweis inoffiziell, Kontakt-mailto, Muenster-Dank; kein Build-Datum"
    requirement: UI-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#App.vue (Fusszeile, D-17, D-18)"
        status: pass
      - kind: unit
        ref: "app/src/charts/__tests__/format.test.ts#datum (UI-03, D-18)"
        status: pass
    human_judgment: false
  - id: D2
    description: "config.ts mit Platzhaltern auf .invalid und istPlatzhalter fuer das Phase-7-Gate"
    requirement: UI-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#istPlatzhalter (UI-03, D-17)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Externe Links: target _blank, rel noopener noreferrer, selbst gehostetes Icon, verstecktem Text (oeffnet in neuem Tab)"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#oeffnet jeden externen Link mit noopener noreferrer"
        status: pass
    human_judgment: false
  - id: D4
    description: "Kopfmenue aus MENUE in der Reihenfolge Start, Woher?, Wofuer?, Geldfluss, Glossar; Jahr bleibt bei drei Eintraegen erhalten"
    requirement: UI-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menue.test.ts#MENUE (D-13)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Aktiver Menuepunkt mit aria-current, Farbe, Gewicht 600 und Unterstreichung; Drawer bis 699 px mit Fokus-Rueckgabe; Skip-Link springt zur h1 ohne Routenwechsel"
    verification:
      - kind: other
        ref: "App-Kette in Scratch-Kopie: type-check, lint, format:check, build gruen (Verhalten im Browser nicht geprueft)"
        status: pass
    human_judgment: true
    rationale: "Fokusverhalten, Drawer-Animation und Skip-Link im Hash-Router lassen sich ohne Browser nicht automatisch belegen; human-check aus Task 2 (Tab, 360 px, Escape, Footer-Umbruch) steht am Phasenende aus"

duration: ca. 25 min
completed: 2026-10-04
status: complete
---

# Phase 5 Plan 07: Kopfmenue, Drawer, Skip-Link und Fusszeile Summary

**Kopfzeile mit datengetriebenem Fuenf-Punkte-Menue (`MENUE`), mobilem `wa-drawer` bis 699 px und deutschem, hash-router-festem Skip-Link; Fusszeile mit Datenstand aus `meta.json`, Original-PDF, Inoffizielles-Projekt-Hinweis und Kontakt aus `config.ts`, dessen `.invalid`-Platzhalter per `istPlatzhalter` fuer das Phase-7-Gate erkennbar sind.**

## Accomplishments

- Tracer: `config.ts` (`KONTAKT_EMAIL`, `ORIGINAL_PDF_URL`, `istPlatzhalter`), `datum()` in `format.ts` (ohne Import, `FormatKuerzel` unveraendert), Fusszeile in `App.vue`, Icon `arrow-up-right-from-square.svg`. Pipeline-Gegenprobe `test_formatiere.py` + `test_texte.py` mit verlinktem `node_modules`: 77 passed (node-Port-Test lief).
- `lib/menue.ts` mit `MENUE`/`MenueEintrag` (TDD: RED-Commit `0dd52d4`, GREEN-Commit `ca054e7`).
- Header: Wortmarke, `<nav aria-label="Hauptnavigation">` aus `MENUE`; Links fuer Woher?, Wofuer?, Geldfluss gehen ueber `jahrLink`. Aktiver Eintrag: `[aria-current='page']` mit `--wa-color-brand-40`, Gewicht 600, Unterstreichung. Eintraege umbrechen (`overflow-wrap`), Trefferflaeche mindestens 44 px.
- Bis 699 px (`useSchmalerBildschirm`): 44-px-Schalter mit `aria-label="Menue oeffnen"`, `aria-expanded`, `aria-controls`; `wa-drawer placement="end" label="Menü" light-dismiss` mit derselben Liste vertikal.
- Skip-Link: `<span slot="skip-to-content">Zum Inhalt springen</span>`; Capture-Listener auf `wa-page` erkennt den eingebauten Link im Shadow-DOM ueber `composedPath()` und `part="skip-to-content"`, ruft `preventDefault` und fokussiert die `h1` (Rueckfall `main`).
- Inhaltsbereich ist jetzt `<main class="om-content">` (Landmark).

## Task Commits

1. **Task 1 (Tracer): Fusszeile end-to-end** - `7edb297` (feat)
2. **Task 2 RED: MENUE-Test** - `0dd52d4` (test; Test schlug mit fehlendem Modul fehl)
3. **Task 2 GREEN: menue.ts** - `ca054e7` (feat)
4. **Task 2: Kopfmenue, Drawer, Skip-Link in App.vue** - `1c14077` (feat)

## Hand-off an Phase 7 (D-17)

Kontakt und PDF-URL sind laut 05-03 "Spaeter (Platzhalter)": `KONTAKT_EMAIL = kontakt-noch-nicht-festgelegt@example.invalid`, `ORIGINAL_PDF_URL = https://haushaltsplan-noch-nicht-festgelegt.invalid/`. **Phase 7 muss das Deployment abbrechen, solange `istPlatzhalter(KONTAKT_EMAIL)` oder `istPlatzhalter(ORIGINAL_PDF_URL)` wahr ist** (Smoke-Test auf die gebaute Fusszeile bzw. `config.ts`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Kritische Funktionalitaet / A11y] Menue-Schalter als natives `button` statt `wa-button`**
- **Found during:** Task 2
- **Issue:** `aria-label`, `aria-expanded` und `aria-controls` auf dem `wa-button`-Host erreichen den fokussierbaren inneren `<button>` im Shadow-DOM nicht; Screenreader bekaemen keinen Namen und keinen Zustand.
- **Fix:** Natives `<button type="button" class="om-menue-schalter">` mit `wa-icon name="bars"` (44 x 44 px, WA-Tokens), Attribute direkt am Button. Die Acceptance-Greps (`Menü öffnen`, `wa-drawer`) bleiben erfuellt.
- **Files modified:** app/src/App.vue
- **Commit:** 1c14077

**2. [Plan-Interpretation] Fokus nach Seitenwechsel**
- **Found during:** Task 2
- **Issue:** Plan und UI-SPEC verlangen, dass der Fokus nach dem Schliessen zum Schalter zurueckkehrt. Der Router fokussiert nach einem Seitenwechsel aber die `h1` (D-13); `wa-after-hide` kommt nach der Animation und wuerde den Fokus danach zum Schalter stehlen.
- **Fix:** Rueckgabe an den Schalter nur bei Escape, Klick daneben und Schliessen-Knopf; schliesst ein Seitenwechsel (`route.path`) den Drawer, behaelt die neue Seite den Fokus. Ein Klick auf den Link der aktuellen Seite (kein Pfadwechsel) fuehrt zum Schalter zurueck.
- **Files modified:** app/src/App.vue
- **Commit:** 1c14077

**Total deviations:** 2 (1 Rule 2, 1 Interpretation). **Impact:** keine Aenderung des Umfangs; beide Punkte sind Zugaenglichkeits-Verbesserungen, die im human-check geprueft werden sollten.

## Verification

- Scratch-Kopie von `app/` (`npm ci`): `test` 13 Dateien / 162 Tests gruen, `type-check`, `lint`, `format:check`, `build` gruen.
- Pipeline: `uv run --directory pipeline pytest tests/test_formatiere.py tests/test_texte.py` 77 passed (node-Gegenprobe lief, `app/node_modules` temporaer verlinkt und wieder entfernt).
- Acceptance Task 1 und 2: alle Greps wie im Plan (0 Treffer fuer typisierte Adressen in `App.vue`, 0 Imports in `format.ts`).
- Nicht geprueft: Browser-Verhalten (kein Browser im Sandkasten). Der human-check aus Task 2 steht aus: Tab/Enter auf den Skip-Link ohne Routenwechsel, Drawer bei 360 px (Escape, Navigation, Fokus), aktiver Eintrag unterstrichen, Fusszeile ohne horizontales Scrollen.

## Issues Encountered

- Die Sandbox lehnt zusammengesetzte Shell-Befehle mit git ab; Befehle wurden einzeln ausgefuehrt, Ledger-Datei fuer `plan_head_before` manuell mit der bekannten Basis angelegt.
- Der Skip-Link ueber `composedPath()` ist nicht im Browser belegt. Falls er dort versagt, gilt der Rueckfall aus dem Plan (eingebauten Link per `wa-page::part(skip-to-content)` ausblenden und eigenen ersten Link rendern).

## Known Stubs

- `app/src/config.ts`: `KONTAKT_EMAIL` und `ORIGINAL_PDF_URL` sind bewusst Platzhalter auf `.invalid` (Entscheidung 05-03, D-17); Phase 7 loest sie ueber das `istPlatzhalter`-Gate auf. Nicht in `.planning/WINDOWS.md` eingetragen, weil das Gate die Absicherung ist.

## Threat Flags

None. T-05-17 (rel noopener noreferrer, per Test), T-05-18 (`.invalid`, `istPlatzhalter`, Hand-off oben), T-05-19 (Klick abgefangen, navigiert nie), T-05-20 (Icon selbst gehostet, keine Drittanbieter-Requests) sind umgesetzt; keine neue Angriffsflaeche.

## Shared files

Keine geteilten Dateien (`main.ts`, `router/index.ts`, `echartsTheme.ts`) angefasst; `wa-icon`, `wa-drawer` waren bereits in `main.ts` importiert.

## Next Phase Readiness

- Alle Seiten haben Menue, Footer und Skip-Link; Phase 6 erweitert `MENUE` um die Gruppe "Mehr wissen".
- Phase 7: Platzhalter-Gate (siehe Hand-off).

## Self-Check: PASSED

- Gefunden: app/src/config.ts, app/src/lib/menue.ts, app/src/lib/__tests__/config.test.ts, app/src/lib/__tests__/menue.test.ts, app/public/icons/solid/arrow-up-right-from-square.svg.
- Commits 7edb297, 0dd52d4, ca054e7, 1c14077 vorhanden.
