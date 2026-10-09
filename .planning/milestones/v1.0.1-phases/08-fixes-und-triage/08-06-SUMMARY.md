---
phase: 08-fixes-und-triage
plan: 06
subsystem: ui
tags: [a11y, vue, playwright, axe, web-awesome, wa-drawer, wcag]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-04 und 08-05 (Texte und Etiketten); diese Plan teilt keine Datei mit ihnen"
provides:
  - "rahmenAttribute(ueberlaeuft, captionId) in components/datenTabelle.ts"
  - "DatenTabelle mit Pflicht-Props beschriftung/spalten/zeilen, ohne Slot-Modus, genau ein Name per Caption und aria-labelledby"
  - "Mobiles Menue: jeder Linkklick schliesst den Drawer, Fokus auf der h1 (fokussiereUeberschrift, beiDrawerLinkKlick)"
  - "Playwright: Tabellenrahmen und axe bei 360 px auf jeder Route, Drawer-Faelle, menueVersatz im Browser; CI-Spiegel in interaktion.spec.ts"
affects: [08-verify, phase-8-manual-checks]

actuals:
  tokens: 21000
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Reine Entscheidung (rahmenAttribute) im .ts neben der Komponente, im Browser bewiesen, weil vitest ohne Layout laeuft"
    - "Gemeinsame Playwright-Pruefungen in e2e/*.ts-Hilfsdateien, einmal im Projekt mobil und als Spiegel im Projekt ci"
    - "Fokus nach wa-drawer: setTimeout nach wa-after-hide, weil die Bibliothek den Fokus selbst per setTimeout zurueckgibt"

key-files:
  created:
    - app/e2e/tabellenrahmen.ts
    - app/e2e/menueDrawer.ts
  modified:
    - app/src/components/datenTabelle.ts
    - app/src/components/DatenTabelle.vue
    - app/src/components/__tests__/zustaende.test.ts
    - app/src/App.vue
    - app/src/components/ProduktAkkordeon.vue
    - app/e2e/mobil.spec.ts
    - app/e2e/interaktion.spec.ts
    - app/src/lib/__tests__/menueVersatz.test.ts

key-decisions:
  - "D-16/D-19: beschriftung, spalten und zeilen sind Pflicht-Props, der Slot-Modus von DatenTabelle ist entfernt (bewusste Abweichung von den Muenster-Props, im Code kommentiert und im Commit genannt)"
  - "D-20: Der Name der Tabelle kommt nur aus der Caption; der Rahmen verweist per aria-labelledby, kein aria-label"
  - "D-21 mit RESEARCH-Korrektur 1: Fokus nach jedem Drawer-Linkklick auf die h1, auch bei Links anderer Seiten"
  - "Region-Eindeutigkeit mit eigener Pruefung der Tabellenrahmen statt axe landmark-unique (RESEARCH-Korrektur 2)"

patterns-established:
  - "Overflow-Attribute nur gemeinsam und nur bei gerenderter, ueberlaufender Tabelle"
  - "Jedes im Projekt mobil bewiesene Verhalten, das gegatet bleiben soll, hat einen Spiegel in interaktion.spec.ts"

requirements-completed: [A11Y-01, A11Y-02, A11Y-03, TRI-04]

coverage:
  - id: D1
    description: "Ueberlaufender Tabellenrahmen traegt tabindex 0, role region und aria-labelledby auf eine Caption mit Text, kein aria-label; nicht ueberlaufende Rahmen tragen nichts (A11Y-01, A11Y-03, 05/WR-02, 01/IN-05)"
    requirement: "A11Y-01"
    verification:
      - kind: unit
        ref: "app/src/components/__tests__/zustaende.test.ts#rahmenAttribute"
        status: pass
      - kind: e2e
        ref: "app/e2e/mobil.spec.ts#Rahmen mit Rolle und genau einem Namen auf <Route> (11 Routen)"
        status: pass
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts#/investitionen: ueberlaufende Rahmen sind benannte Regionen mit Tabstopp"
        status: pass
    human_judgment: false
  - id: D2
    description: "Beschriftung ist Pflicht-Prop, Slot-Modus entfernt, Caption immer vorhanden mit id aus useId() (D-16, D-19, 05/IN-02)"
    requirement: "A11Y-03"
    verification:
      - kind: unit
        ref: "app/src/components/__tests__/zustaende.test.ts#DatenTabelle Name und Rahmen"
        status: pass
      - kind: other
        ref: "npm --prefix app run type-check (vue-tsc, alle 29 Aufrufe)"
        status: pass
    human_judgment: false
  - id: D3
    description: "axe mit WCAG-Tags meldet bei 360 px auf jeder Route mit geoeffneten wa-details keinen Verstoss; die Seite scrollt nicht waagerecht"
    requirement: "A11Y-03"
    verification:
      - kind: automated_ui
        ref: "app/e2e/mobil.spec.ts#axe meldet bei geoeffneten Bereichen auf <Route> keinen Verstoss (11 Routen)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Linkklick im mobilen Menue schliesst den Drawer immer (auch Link der aktuellen Seite), Fokus auf der h1; Escape gibt den Fokus an den Menueknopf (D-21, A11Y-02, 05/IN-05)"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/mobil.spec.ts#Mobiles Menue schliesst bei jedem Linkklick (3 Faelle)"
        status: pass
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts#Mobiles Menue schliesst bei jedem Linkklick (3 Faelle, Projekt ci)"
        status: pass
    human_judgment: false
  - id: D5
    description: "menueVersatz-Verdrahtung (Oeffnen, Resize, style.left) im Browser geprueft, Quelltext-Test entfernt (D-14, 06/IN-09)"
    requirement: "TRI-04"
    verification:
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts#die geoeffnete Liste bleibt nach dem Oeffnen und nach einem Resize im Fenster"
        status: pass
    human_judgment: false
  - id: D6
    description: "Doppelte Namensansage von Region und Caption bei einem Screenreader (Annahme A1)"
    verification: []
    human_judgment: true
    rationale: "Ob VoiceOver oder NVDA den Namen einmal oder doppelt ansagen, ist per Playwright nicht pruefbar; manuelle Pruefung am Phasenende"

duration: 75min
completed: 2026-10-07
status: complete
plan_head_before: d7e46f410d0503f7ae5b21d85919376c55857325
plan_head_after: 01c800ba21b9c96f6e3ec4254d801abfaace0d4b
---

# Phase 8 Plan 06: Tabellenrahmen, mobiles Menue, menueVersatz im Browser Summary

**Scrollbare DatenTabelle-Rahmen sind nur noch bei Ueberlauf fokussierbare Regionen mit genau einem Namen (Caption per aria-labelledby, useId), jeder Linkklick im 360-px-Drawer schliesst das Menue und setzt den Fokus auf die h1, und menueVersatz wird per Playwright statt per Quelltext geprueft.**

## Performance

- **Duration:** ca. 75 min
- **Started:** 2026-10-07T20:50:00Z
- **Completed:** 2026-10-07T21:10:00Z
- **Tasks:** 3 (plus ein Folgefix aus Task 1)
- **Files modified:** 10 (2 neu)

## Accomplishments

- `rahmenAttribute(ueberlaeuft, captionId)` liefert `{}` oder genau `tabindex 0`, `role region`, `aria-labelledby` zusammen; `DatenTabelle.vue` bindet es nur fuer eine gerenderte Tabelle (nicht bei Skeleton und Leerzustand).
- `DatenTabelle` ohne Slot-Modus: `beschriftung`, `spalten`, `zeilen` Pflicht (vue-tsc gruen ueber alle 29 Aufrufe), Caption immer vorhanden (`om-visually-hidden`, `id` aus `useId()`), kein `aria-label`, DEV-Warnung und `istDatenModus` entfernt.
- Playwright bei 360 px auf allen 11 Routen mit geoeffneten `wa-details`: Rahmenattribute, eindeutige Region-Namen, kein waagerechtes Scrollen, axe (WCAG 2.0/2.1 A/AA) ohne Verstoss; Spiegel fuer `/investitionen` im Projekt `ci`.
- Drawer: `beiDrawerLinkKlick` an beiden RouterLinks, `fokussiereUeberschrift()` aus dem Skip-Link herausgezogen und per `setTimeout` nach `wa-after-hide` aufgerufen. Gegenprobe: mit dem alten `App.vue` fallen die beiden Linkfaelle durch.
- `menueVersatz.test.ts` ohne `?raw`-Glob und ohne Quelltext-Block; das Verhalten (Oeffnen, Resize 720, 1200, 720) steht in `interaktion.spec.ts`. Gegenprobe: ohne `positioniere()` im Resize-Handler faellt der Test durch.
- Endstand in der Scratch-Kopie: vitest 2020 gruen (3 Quelltext-Tests weniger), type-check, lint, format:check gruen, Playwright `ci` 86 und `mobil` 39 gruen.

## Task Commits

1. **Task 1: Tabellenrahmen mit Rolle und genau einem Namen** - `fe416ab` (fix; Findings 05/WR-02, 01/IN-05, 05/IN-02; D-16, D-19, D-20)
   - Folgefix, den Task 1 braucht: `e75a05b` (fix, A11Y-03, Summary-Text der Produktgruppen)
2. **Task 2: Drawer schliesst bei jedem Link, Fokus auf h1** - `df0d2b0` (fix; 05/IN-05, D-21)
3. **Task 3: menueVersatz im Browser statt Quelltext** - `01c800b` (test; 06/IN-09, D-14)

**Plan metadata:** folgt als docs-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/components/datenTabelle.ts` - `rahmenAttribute`
- `app/src/components/DatenTabelle.vue` - Pflicht-Props, Caption mit id, `v-bind` der Rahmenattribute, Slot-Modus entfernt
- `app/src/components/__tests__/zustaende.test.ts` - `beschriftung` in allen Faellen, Caption/kein aria-label/keine Overflow-Attribute im SSR, `rahmenAttribute` beide Zustaende
- `app/src/App.vue` - `fokussiereUeberschrift`, `beiDrawerLinkKlick`, `setTimeout` nach `wa-after-hide`
- `app/src/components/ProduktAkkordeon.vue` - `overflow-wrap: anywhere` in `::part(summary)`
- `app/e2e/tabellenrahmen.ts` (neu) - gemeinsame Befundpruefung der Tabellenrahmen und Oeffnen aller Bereiche
- `app/e2e/menueDrawer.ts` (neu) - gemeinsame Drawer-Faelle
- `app/e2e/mobil.spec.ts`, `app/e2e/interaktion.spec.ts` - neue Describe-Bloecke, CI-Spiegel, menueVersatz-Test
- `app/src/lib/__tests__/menueVersatz.test.ts` - Quelltext-Block entfernt

## Decisions Made

- Region-Namen werden je Seite auf Eindeutigkeit geprueft (eigene Pruefung), axe `landmark-unique`/`region` bleiben kein Gate (RESEARCH-Korrektur 2).
- Der Fokus geht nach jedem Linkklick im Drawer auf die h1, auch bei Links anderer Seiten (RESEARCH-Korrektur 1, UI-SPEC Offene Annahmen 1); Escape, Schliessen-Knopf und Klick daneben enden weiter am Menueknopf.
- Spalten und Zeilen blieben Pflicht ohne Rueckfall auf optional: kein Aufruf liefert `undefined`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Seite scrollt auf /glossar bei 360 px waagerecht, sobald alle verschachtelten wa-details offen sind**
- **Found during:** Task 1 (axe-Test mit `reducedMotion` und Eindeutigkeitspruefung auf /glossar)
- **Issue:** In `ProduktAkkordeon.vue` schiebt ein langes Wort im Summary-Text den Pfeil der Produkt-Summary bis 383 px (Fenster 360 px). `overflow-wrap: break-word` senkt die Mindestbreite im Flex-Container nicht, und im Playwright-Image fehlt das deutsche Silbentrennwoerterbuch. Der bestehende Routentest in `mobil.spec.ts` sah das nur nicht, weil das Layout erst rund 300 ms nach dem Oeffnen steht.
- **Fix:** `overflow-wrap: anywhere` in `::part(summary)` (eine Zeile, mit Kommentar); in `tabellenrahmen.ts` wartet `oeffneAlleBereiche` 500 ms, damit die Messung nicht vor dem Layout liegt.
- **Files modified:** `app/src/components/ProduktAkkordeon.vue`, `app/e2e/tabellenrahmen.ts`
- **Verification:** mobil 39 und ci 86 Tests gruen, kein waagerechtes Scrollen auf /glossar
- **Committed in:** `e75a05b`

**2. [Rule 3 - Blocking] Zwei neue e2e-Hilfsdateien statt Duplikat in beiden Specs**
- **Found during:** Task 1 und Task 2
- **Issue:** Die Rahmenpruefung und die Drawer-Faelle laufen in `mobil.spec.ts` und als CI-Spiegel in `interaktion.spec.ts`; zweimal dieselbe Logik haette auseinanderlaufen koennen.
- **Fix:** `app/e2e/tabellenrahmen.ts` und `app/e2e/menueDrawer.ts` (Playwright greift nur `*.spec.ts` als Test auf, wie bei `routen.ts`).
- **Committed in:** `fe416ab`, `df0d2b0`

---

**Total deviations:** 2 (beide Rule 3)
**Impact on plan:** Beide notwendig fuer die Wahrheiten des Plans (kein waagerechtes Scrollen auf jeder Route, gleiche Pruefung in mobil und ci); kein Scope-Creep.

## Issues Encountered

- axe meldete im ersten Lauf `color-contrast` auf fast allen Routen: Web Awesome blendet `wa-details` ein, axe sah Text mit halber Deckkraft. Wie im Smoke-Test loest `emulateMedia({ reducedMotion: 'reduce' })` das; kein echter Kontrastfehler.
- Playwright liefert den Resize-Event erst nach `setViewportSize`; der menueVersatz-Test wartet deshalb per `expect.poll` auf die Lage und nicht auf die Fenstergroesse.

## Pending Manual Check

- Phasenende (RESEARCH A1, human-check aus Task 1): Mit VoiceOver oder NVDA bei 360 px auf `/ausgaben` in eine ueberlaufende Tabelle navigieren und notieren, ob der Name einmal oder doppelt angesagt wird. Bei stoerender Doppelansage ist die UI-SPEC-Alternative (nur Region oder nur Tabelle traegt den Namen) ein Folgeauftrag.

## Known Stubs

None.

## Threat Flags

None. `aria-labelledby`-Ids stammen aus `useId()` (T-08-10), der Drawer-Fokus ist in `mobil` und `ci` per Playwright belegt (T-08-11), kein Paket installiert (T-08-SC).

## Next Phase Readiness

- Plan-Verifikation: `daten/` und `app/src/data/` unveraendert (kein Pipeline-Lauf noetig, `git diff --stat d7e46f4 HEAD -- daten app/src/data` leer).
- Ausserhalb des Scopes nichts gefunden, das ein Eintrag in deferred-items braeuchte.

## Self-Check: PASSED

- Dateien vorhanden: `app/e2e/tabellenrahmen.ts`, `app/e2e/menueDrawer.ts`, `app/src/components/datenTabelle.ts` (rahmenAttribute), alle Commits `e75a05b`, `fe416ab`, `df0d2b0`, `01c800b` im Branch.
- Acceptance-Greps: `export function rahmenAttribute` 1 Treffer; `aria-label=` in DatenTabelle.vue 0; `useId()` 1; `<slot />` 0; `beschriftung` in zustaende.test.ts 5; `AxeBuilder` in mobil.spec.ts 2; `@click="beiDrawerLinkKlick"` 2; `function fokussiereUeberschrift` 1; `setTimeout(fokussiereUeberschrift)` 1; `?raw` in menueVersatz.test.ts 0; `setViewportSize` in interaktion.spec.ts 8.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
