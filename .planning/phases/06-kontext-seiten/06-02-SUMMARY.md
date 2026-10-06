---
phase: 06-kontext-seiten
plan: 02
subsystem: ui
tags: [vue-router, vue3, web-awesome, echarts, a11y, disclosure-menu]

requires:
  - phase: 05-leitfragen-seiten
    provides: PageIntro, WertartEtikett, MENUE, SteuerZeitreihe, echartsTheme, useJahr, quelltext/stiltokens-Tests
provides:
  - Routen entwicklung, investitionen, rat-entscheidet, stellenplan mit Seitenrahmen (PageIntro, Lead aus Daten)
  - MENUE als Vereinigung MenueLink | MenueGruppe, menueLinks()
  - MenueGruppe.vue (Disclosure „Mehr wissen“ im Kopfmenü, feste Gruppe im Drawer)
  - echartsTheme: MarkLineComponent, BINDUNG_FARBEN, SCHULDEN_FARBEN, BERECHNET_DECAL, SCHWELLE_FARBE, HOHL_FLAECHE
  - charts/wertartStil.ts: LINIENSTILE, LEGENDE_TEXT, flaechenFarbe, linienSerie, jahresAchse, saeulenStil
affects: [06-03, 06-04, 06-05, 06-06, 06-07, 06-08, 06-09, 06-10, 06-11, 06-12]

actuals:
  tokens: 10600
  tasks: 3
  commits: 5

plan_head_before: 724fa45bf051bed5c07a034bac3e8560379aaa70
plan_head_after: c488ac27dd2e6cba6ed651f5b43a867ecac8861a

tech-stack:
  added: []
  patterns:
    - "Disclosure-Menügruppe: Schalter mit aria-expanded/aria-controls plus Linkliste, kein role=menu"
    - "Eine Stiltabelle für Ist/Ansatz/Planung in charts/wertartStil.ts, Farbe als Parameter"
    - "Router-Quelltext per import.meta.glob ?raw gegen Menünamen prüfen"

key-files:
  created:
    - app/src/components/MenueGruppe.vue
    - app/src/charts/wertartStil.ts
    - app/src/charts/__tests__/wertartStil.test.ts
    - app/src/pages/EntwicklungPage.vue
    - app/src/pages/InvestitionenPage.vue
    - app/src/pages/RatEntscheidetPage.vue
    - app/src/pages/StellenplanPage.vue
  modified:
    - app/src/router/index.ts
    - app/src/lib/menue.ts
    - app/src/lib/__tests__/menue.test.ts
    - app/src/App.vue
    - app/src/charts/echartsTheme.ts
    - app/src/charts/__tests__/farben.test.ts
    - app/src/components/SteuerZeitreihe.vue

key-decisions:
  - "MenueGruppe bekommt das Linkziel als Prop (ziel), damit mitJahr-Links weiter über useJahr().jahrLink in App.vue laufen und useJahr nicht doppelt instanziiert wird"
  - "Die geöffnete Liste wird per JS an den Fensterrand geklemmt (Versatz aus getBoundingClientRect und max-width), weil die Gruppe mitten in der umbrechenden Leiste steht"
  - "focusout mit relatedTarget null schließt nicht (Safari/Firefox öffnen sonst beim Klick auf den Schalter sofort wieder); Klick außerhalb fängt pointerdown ab"
  - "SCHULDEN_FARBEN enthält zusätzlich liquiditaetskredite (gray-60), damit die Seitenpläne den dritten Stapel nicht aus BINDUNG_FARBEN borgen müssen"
  - "BERECHNET_DECAL: rect, Rotation 90 Grad, Periode 4 px, 45 % Weiß; unterscheidet sich in Symbol, Rotation und Muster von KL_DECAL und PUNKT_DECAL"

patterns-established:
  - "Menü-Union mit typ-Diskriminante; App.vue filtert leere Gruppen vor dem Rendern"
  - "wertartStil.jahresAchse/saeulenStil als Eintrittspunkt für alle Jahresdiagramme der Phase 6"

requirements-completed: [ENTW-01, INV-01, RAT-01, STEL-01]

duration: 15min
completed: 2026-10-06
status: complete

coverage:
  - id: D1
    description: "Vier Routen /entwicklung, /investitionen, /rat-entscheidet, /stellenplan mit PageIntro, Titel aus meta.titel, Jahreszahlen nur aus den Daten"
    requirement: "ENTW-01, INV-01, RAT-01, STEL-01 (nur Seitenrahmen, Inhalte folgen in 06-05 bis 06-11)"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menue.test.ts#verweist nur auf Routen, die im Router stehen"
        status: pass
      - kind: other
        ref: "npm run type-check && lint && format:check && test && build (Scratch-Kopie)"
        status: pass
    human_judgment: false
  - id: D2
    description: "MENUE als Vereinigung mit Gruppe „Mehr wissen“ als einzige Quelle für Kopfmenü und Drawer"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menue.test.ts"
        status: pass
    human_judgment: false
  - id: D3
    description: "Disclosure im Kopfmenü (Enter/Leertaste, Escape mit Fokusrückgabe, Klick außen, Routenwechsel, Fokusverlust, aktiver Zustand) und feste Gruppe im Drawer"
    verification: []
    human_judgment: true
    rationale: "Tastatur- und Fokusverhalten sowie Randpositionierung der Liste sind im Node-Testlauf (kein DOM) nicht prüfbar; Human-Check ist für den Abschluss-Walkthrough vorgesehen"
  - id: D4
    description: "Diagrammgrundlagen: MarkLine, Phase-6-Farben mit Kontrast >= 3:1, BERECHNET_DECAL, gemeinsames Wertart-Stilmodul; SteuerZeitreihe unverändert in der Ausgabe"
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/farben.test.ts#Farben der Phase 6"
        status: pass
      - kind: unit
        ref: "app/src/charts/__tests__/wertartStil.test.ts"
        status: pass
    human_judgment: false
---

# Phase 6 Plan 2: Kontext-Seiten Rahmen Summary

**Vier geroutete Seitenrahmen, Disclosure-Menügruppe „Mehr wissen“ (Kopfmenü und Drawer) aus einer MENUE-Union sowie das gemeinsame Chart-Fundament (MarkLine, Bindungs-/Schuldenfarben, Berechnet-Schraffur, Ist/Ansatz/Planung-Stilmodul)**

## Performance

- **Duration:** ca. 15 min
- **Completed:** 2026-10-06T05:45:16Z
- **Tasks:** 3 (Tracer, zwei TDD-Aufgaben)
- **Files modified:** 14 (7 neu, 7 geändert)

## Accomplishments

- Routen `entwicklung`, `investitionen`, `rat-entscheidet`, `stellenplan` vor dem Catch-all; jede Seite zeigt `PageIntro` mit dem UI-SPEC-Titel und Lead, Jahr und Wertart nur aus `haushalt.jahre`/`haushaltsjahr`.
- `MENUE` ist `MenueLink | MenueGruppe`; `menueLinks()` flacht ab; Test sichert Reihenfolge, `mitJahr`, Einmaligkeit und dass jeder Name im Router steht.
- `MenueGruppe.vue`: Schalter mit `aria-expanded`/`aria-controls`, Linkliste ohne `role="menu"`, Pfeil inline als SVG (keine Icon-Datei), Schließen per Escape (Fokus zurück), Klick außen, Routenwechsel und Fokusverlust; aktive Unterseite markiert den Schalter mit `aria-current="true"`, brand-40, Fettdruck und Unterstreichung. Drawer zeigt die Gruppe als Überschrift mit vier eingerückten Links.
- `echartsTheme.ts` registriert `MarkLineComponent` und exportiert `BINDUNG_FARBEN`, `SCHULDEN_FARBEN`, `BERECHNET_DECAL`, `SCHWELLE_FARBE`, `HOHL_FLAECHE`; `farben.test.ts` belegt Kontrast >= 3:1.
- `charts/wertartStil.ts` hält die eine Stiltabelle; `SteuerZeitreihe.vue` nutzt sie ohne Verhaltensänderung.

## Task Commits

1. **Task 1: Tracer, vier Routen mit Seitenrahmen** - `d869616` (feat)
2. **Task 2: Menügruppe „Mehr wissen“** - RED `1cc2bec` (test), GREEN `e3605c5` (feat)
3. **Task 3: Diagramm-Grundlagen** - RED `4c0364a` (test), GREEN `c488ac2` (feat)

**Plan metadata:** folgt als `docs(06-02)`-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/router/index.ts` - vier neue Routen mit `meta.titel`
- `app/src/pages/{Entwicklung,Investitionen,RatEntscheidet,Stellenplan}Page.vue` - Seitenrahmen mit PageIntro (und WertartEtikett)
- `app/src/lib/menue.ts` - Union, `MENUE`, `menueLinks()`
- `app/src/components/MenueGruppe.vue` - Disclosure-Gruppe
- `app/src/App.vue` - rendert Leiste und Drawer aus der Union
- `app/src/charts/echartsTheme.ts` - MarkLine und neue Farben/Muster
- `app/src/charts/wertartStil.ts` - gemeinsame Wertart-Stile, Jahresachse, Säulenstil
- `app/src/components/SteuerZeitreihe.vue` - auf `wertartStil` umgestellt

## Decisions Made

Siehe `key-decisions` im Frontmatter. Kernpunkte: Linkziel als Prop an `MenueGruppe`, JS-Klemmung der geöffneten Liste am Fensterrand, `focusout` mit `relatedTarget === null` schließt nicht, `SCHULDEN_FARBEN` um `liquiditaetskredite` ergänzt.

## TDD Gate Compliance

Task 2: RED `1cc2bec` (7 von 7 Tests scheitern an `menueLinks` und der fehlenden Gruppe), GREEN `e3605c5`. Task 3: RED `4c0364a` (16 Tests scheitern an Behauptungen; `wertartStil.ts` als wirkungsloses Gerüst mitcommittet, damit der Modulimport nicht der Fehlergrund ist), GREEN `c488ac2`. Kein REFACTOR-Commit nötig.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] RED-Gerüst für wertartStil.ts**
- **Found during:** Task 3 (RED)
- **Issue:** Ohne das Modul scheitert `wertartStil.test.ts` am Import (keine Tests entdeckt), das wäre kein gültiges RED.
- **Fix:** Im RED-Commit ein Gerüst mit den Signaturen, das nur wirft; die Tests scheitern damit an Behauptungen.
- **Files modified:** app/src/charts/wertartStil.ts
- **Committed in:** 4c0364a

**2. [Rule 2 - Missing Critical] Fensterrand-Klemmung der Menüliste**
- **Found during:** Task 2
- **Issue:** Die Gruppe steht mitten in der umbrechenden Leiste; eine nur per `left: 0` positionierte Liste kann bei 700 px rechts über den Viewport ragen (UI-SPEC E12 overflow verlangt, dass sie nie breiter/außerhalb liegt).
- **Fix:** `positioniere()` verschiebt die Liste nach dem Öffnen und bei Resize so, dass sie innerhalb von `100vw - 2 x md` liegt.
- **Files modified:** app/src/components/MenueGruppe.vue
- **Committed in:** e3605c5

**3. [Rule 2 - Missing Critical] liquiditaetskredite in SCHULDEN_FARBEN**
- **Found during:** Task 3
- **Issue:** UI-SPEC nennt für den Schuldenstand drei Farben (gray-30/50/60), der Plan listet zwei.
- **Fix:** dritter Schlüssel `liquiditaetskredite` ergänzt (additiv, Kontrast 3,02:1 getestet).
- **Committed in:** c488ac2

---

**Total deviations:** 3 auto-fixed (1 blocking, 2 missing critical)
**Impact on plan:** Alle drei sind additiv und bleiben im Plan-Umfang; kein Scope Creep.

## Issues Encountered

- Der Plan verlangt `grep -c 'role="menu"' ... = 0`; ein Kommentar in `MenueGruppe.vue` nannte den Ausdruck und wurde umformuliert.
- Linux-Sandbox: die App-Kette lief in einer Scratch-Kopie mit vorhandenem Linux-`node_modules` (kein `npm ci`, kein Netz); Lockfile identisch zum committeten.

## Known Stubs

Die vier Seiten sind bewusst nur Rahmen (PageIntro, ggf. WertartEtikett) ohne Inhalt; die Inhaltsabschnitte liefern 06-05 (Entwicklung), 06-08/06-09 (Rücklagen, Investitionen), 06-10 (Rat entscheidet), 06-11 (Stellenplan). Das ist im Plan so vorgesehen (Flagged assumptions), keine Verdrahtungslücke.

## Threat Flags

Keine neue Angriffsfläche: statische Routen ohne Parameter (T-06-04), Escape/Außenklick/Routenwechsel/Fokusverlust schließen die Liste, kein Fokusfänger (T-06-05), Pfeil inline ohne Icon-Datei (T-06-06), keine neue Abhängigkeit (T-06-SC).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Seitenpläne der Wellen 2 und 3 können `wertartStil` und die neuen Theme-Exporte importieren, ohne gemeinsame Dateien erneut anzufassen.
- Offen für den Abschluss-Walkthrough (Human-Check Task 2): Menügruppe bei 1280 px (Enter/Leertaste, Tab, Escape, Klick außen, aktive Unterseite) und bei 360 px (Drawer, Liste bleibt im Viewport); Zweizeilen-Achse bei 360 px (RESEARCH A3) tragen die Seitenpläne.

## Self-Check: PASSED

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
