---
phase: 06-kontext-seiten
plan: 06
subsystem: ui
tags: [vue3, vue-router, echarts, web-awesome, investitionen, filter, url-state]

requires:
  - phase: 06-kontext-seiten
    provides: Seitenrahmen /investitionen (06-02), horizontaleBalkenOption, DatenTabelle, ChartCard
provides:
  - lib/investitionen.ts mit Bündelung je (produkt, massnahme_id), Art-Filter, Aufgabenbereichsliste und URL-Filterzustand
  - MassnahmenListe.vue (Balken der größten 15 plus vollständige Tabelle mit Produktlinks)
  - MassnahmenFilter.vue (Aufgabenbereich und Art, aria-live-Ergebniszeile)
  - Abschnitt "Maßnahmen" auf /investitionen mit Leerzustand
affects: [06-07, 06-08, 06-09, 06-12]

actuals:
  tokens: 11100
  tasks: 2
  commits: 4

plan_head_before: 0094bff21346ad5ff9315e86e2fbb928e81d29eb
plan_head_after: 5e4116443e8ee4a26a6975d05151df2fe883d87b

tech-stack:
  added: []
  patterns:
    - "Erst auf Kontoebene nach Art und Aufgabenbereich filtern, dann bündeln, damit die gefilterte Summe nur die gewählten Konten enthält"
    - "URL-Filterzustand wie useAnsicht: Allowlist über Set, erstes Array-Element, replace mit fremden Schlüsseln und Hash; zusätzlich Guard auf die eigene Route"
    - "Router-Composable im Node-Test über createApp + createMemoryHistory + app.runWithContext prüfbar (kein DOM nötig)"

key-files:
  created:
    - app/src/lib/investitionen.ts
    - app/src/lib/__tests__/investitionen.test.ts
    - app/src/components/MassnahmenListe.vue
    - app/src/components/MassnahmenFilter.vue
  modified:
    - app/src/pages/InvestitionenPage.vue

key-decisions:
  - "Bündelungsschlüssel (produkt, massnahme_id) statt massnahme_id allein (Nutzerentscheidung 2, Abweichung von D-07): 11 Kennungen kommen unter mehreren Produkten vor, der Link auf /produkt/:code wäre sonst mehrdeutig"
  - "Gruppen mit Summe 0 werden nicht gelistet; baueGruppen liefert sie weiter, damit der Test die 89 Gruppen vor dem Weglassen prüfen kann"
  - "Spaltenkopf der Jahre lautet '{Jahr} {Wertart}' (Plan), abweichend von 'Wertart Jahr' der Produkttabellen"
  - "useMassnahmenFilter ersetzt die Query nur, solange die Route noch die eigene ist (Guard gegen den Routenwechsel vor dem Abbau der Komponente)"

patterns-established:
  - "buendeln(zeilen, ab) als reine Funktion über Rohzeilen: testbar mit synthetischen Massnahmen, ohne die Daten zu berühren"

requirements-completed: [INV-01]

duration: 40min
completed: 2026-10-06
status: complete

coverage:
  - id: D1
    description: "Maßnahmen je (produkt, massnahme_id) gebündelt, nur Auszahlungen, Summe der Planjahre, absteigend; Summen je Art und gesamt entsprechen den GFP-Zeilen; 89 Gruppen / 59 mit Summe ungleich 0 / 36.361.784 EUR im Jahrgang 2026"
    requirement: INV-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#baueVorhaben ohne Filter (INV-01, D-07, D-08)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#Jahrgang 2026 (RESEARCH Pattern 1, Pitfall 2)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Filter Aufgabenbereich und Art: Allowlist, Prototyp-Schlüssel, Arrays, Bereinigung per replace mit fremden Schlüsseln und Hash, kein Verlaufseintrag"
    requirement: INV-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#leseMassnahmenFilter (D-06, T-06-14)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#useMassnahmenFilter (D-06, Router-Zustand)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Balkendiagramm der 15 größten Maßnahmen in PB-Farben, vollständige Tabelle mit Produktlinks, Filterzeile, aria-live-Ergebniszeile und Leerzustand mit Filter zurücksetzen"
    requirement: INV-01
    verification:
      - kind: other
        ref: "npm run type-check && lint && format:check && test && build (Scratch-Kopie)"
        status: pass
    human_judgment: true
    rationale: "Tastaturbedienung, Fokusverhalten, Layout bei 1280 und 360 px, Balkenklick und umbrechende Optionstexte im wa-select sind ohne Browser nicht prüfbar; Human-Check ist für den Abschluss-Walkthrough der Phase vorgesehen"
---

# Phase 6 Plan 6: Investitionsmaßnahmen Summary

**Auszahlungs-Maßnahmen 2026-2029 je (Produkt, Maßnahme) gebündelt, als 15 größte Balken und vollständige Tabelle auf /investitionen, filterbar nach Aufgabenbereich und Art mit Filterzustand in der URL; Σ und Summe je Art treffen die Gesamtfinanzplan-Zeilen exakt**

## Performance

- **Duration:** ca. 40 min
- **Completed:** 2026-10-06T06:15:00Z
- **Tasks:** 2 (Tracer, TDD-Aufgabe)
- **Files modified:** 5 (4 neu, 1 geändert)

## Accomplishments

- `lib/investitionen.ts`: `buendeln(zeilen, ab)` (rein), `baueGruppen`, `baueVorhaben`, `filterArt`, `ARTEN`, `planjahre`, `GROESSTE_ANZAHL = 15`, `baueMassnahmenTabelle`, `klickIndex`. Planjahre kommen aus `haushalt.jahre.indexOf(haushaltsjahr)`, im Code steht keine Jahreszahl.
- Tests belegen: Σ aller Maßnahmen je Planjahr = GFP `auszahlungen_investitionen`; je Art = die in D-06 genannten GFP-Zeilen (Sonstige = Finanzanlagen + aktivierbare Zuwendungen + sonstige Investitionsauszahlungen); 2026: 89 Gruppen, 59 mit Summe ungleich 0, 36.361.784 EUR, KLIMA1 mehrfach; keine Einzahlung fließt ein.
- `MassnahmenListe.vue`: `BaseChart` mit `horizontaleBalkenOption` (PB-Farbe, Label `euroKurz`), Höhe `balkenHoehe` (höchstens 648 px), Hinweis "Gezeigt werden die k größten von n" nur bei n größer als k, Klick auf Balken öffnet das Produkt; `wa-details` "Tabelle anzeigen" mit `DatenTabelle`, erste Spalte als `RouterLink` auf `/produkt/:code`, fehlende Jahreswerte als "–".
- `MassnahmenFilter.vue`: `wa-select` "Aufgabenbereich" (erste Option "Alle Aufgabenbereiche", sonst die elf Bereiche mit Maßnahmen), Art ab 700 px als `wa-radio-group` mit Buttons, darunter als `wa-select`; Ergebniszeile "{n} Maßnahmen · zusammen {Betrag}" in `aria-live="polite"`.
- `InvestitionenPage.vue`: Finanzplan-Hinweis mit `GlossarBegriff`, Abschnitt "Maßnahmen {Jahr}–{Jahr}", Leerzustand mit "Filter zurücksetzen" (Karte und Tabelle entfallen dann).
- Filterzustand `?pb=`/`?art=`: ungültige Werte (auch `__proto__`, KL, `?art` ohne Wert) fallen auf "Alle" zurück und werden per `router.replace` entfernt; fremde Schlüssel und Hash bleiben; `?jahr=` hat auf der Seite keine Wirkung.

## Task Commits

1. **Task 1: Tracer, Maßnahmen bündeln, Balken und Tabelle** - `0db8e33` (feat)
2. **Task 2: Filter mit URL-Zustand** - RED `0647f41` (test), GREEN `4709e59` (feat)
3. **Task 2: Filterzeile, Ergebniszeile und Leerzustand (UI)** - `5e41164` (feat)

**Plan metadata:** folgt als `docs(06-06)`-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/lib/investitionen.ts` - Bündelung, Art-Zuordnung, Tabellenmodell, Filterzustand
- `app/src/lib/__tests__/investitionen.test.ts` - 65 Tests (Identitäten gegen GFP, Jahrgangszählungen, Query-Parsing, Router-Zustand)
- `app/src/components/MassnahmenListe.vue` - Balken und Tabelle
- `app/src/components/MassnahmenFilter.vue` - Filterzeile
- `app/src/pages/InvestitionenPage.vue` - Abschnitt Maßnahmen

## Decisions Made

Siehe `key-decisions`. Die dokumentierte Abweichung von D-07 (Schlüssel `(produkt, massnahme_id)`) ist Nutzerentscheidung 2 vom 2026-10-05. Die gefilterte Summe enthält nur die Konten der gewählten Art, weil erst gefiltert, dann gebündelt wird; so bleibt "Σ je Art = GFP-Zeile" gültig.

## TDD Gate Compliance

Task 2: RED `0647f41` (26 von 65 Tests scheitern an Behauptungen gegen ein wirkungsloses Gerüst in `lib/investitionen.ts`; die fünf Router-Tests scheitern an der Ausnahme des Gerüsts), GREEN `4709e59` (alle 65 grün). Die UI folgt separat in `5e41164`. Kein REFACTOR-Commit nötig. Task 1 ist ein Tracer: Tests und Implementierung wurden gemeinsam in `0db8e33` committet (die Tests zuerst geschrieben, aber nicht einzeln gegen fehlende Implementierung ausgeführt).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Spalte "PDF-Seite" in der Maßnahmentabelle**
- **Found during:** Task 1
- **Issue:** Der Plan nennt keine Quellenangabe je Maßnahme; Kernwert und Projektkonvention verlangen Rückführbarkeit jeder Zahl auf eine PDF-Seite.
- **Fix:** Letzte Spalte "PDF-Seite" (1-basiert, `pdf_seite` der Maßnahme; je (Produkt, Maßnahme) ist die Seite eindeutig, geprüft an den 89 Gruppen).
- **Files modified:** app/src/lib/investitionen.ts
- **Committed in:** 0db8e33

**2. [Rule 2 - Missing Critical] Routen-Guard in useMassnahmenFilter**
- **Found during:** Task 2
- **Issue:** Beim Verlassen der Seite wechselt die Route vor dem Abbau der Komponente; ein Bereinigungs-`replace` dürfte nicht die Query der nächsten Seite anfassen.
- **Fix:** `ersetze` führt nur aus, solange `route.name` der Name beim Aufbau ist.
- **Files modified:** app/src/lib/investitionen.ts
- **Committed in:** 4709e59

---

**Total deviations:** 2 auto-fixed (2 missing critical)
**Impact on plan:** additiv, kein Scope Creep. Zusätzlich dokumentiert: Bündelungsschlüssel `(produkt, massnahme_id)` statt `massnahme_id` (Nutzerentscheidung 2, siehe Plan-Kontext).

## Issues Encountered

- Der Scratch-Ordner `scratchpad/w` wurde offenbar von einer parallelen Ausführung mit `rsync --delete` überschrieben (Dateien verschwanden zwischen zwei Aufrufen); ich bin auf ein eigenes Verzeichnis `scratchpad/exec0606` umgezogen. Eine veraltete `tsbuildinfo` aus dem kopierten `node_modules/.tmp` verursachte dabei einen TS6053-Fehler und wurde in der Scratch-Kopie entfernt (nichts im Repo betroffen).
- Das Plan-Verfahren `npm ci` im Scratch war ohne Netz nicht nötig: die App-Kette lief in einer Scratch-Kopie mit vorhandenem Linux-`node_modules` (Lockfile identisch).
- Die Plan-Ablage des Commit-Ledgers unter `.git/worktrees/.../gsd-plan-head-before-06-06` war aus dem Worktree heraus nicht schreibbar; `plan_head_before` stammt daher direkt aus dem Spawn-Basiscommit `0094bff`.

## Known Stubs

Keine. Die Seite `/investitionen` ist weiterhin nur teilweise gefüllt (Kennzahlen, VE, Finanzierung, Schulden folgen in 06-07 bis 06-09); das ist im Plan so vorgesehen.

## Threat Flags

Keine neue Angriffsfläche über die Plan-Bedrohungen hinaus: T-06-14 (Allowlist, Prototyp-Schlüssel, Arrays) und T-06-16 (Identitäten gegen GFP, Zählung pinned) sind durch Tests belegt; T-06-15 (Tooltips) läuft über `horizontaleBalkenOption`/`tooltipZeilen`, kein Roh-HTML; keine neue Abhängigkeit (T-06-SC).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Offen für den Abschluss-Walkthrough (Human-Check Task 2): `/investitionen` bei 1280 und 360 px nur per Tastatur bedienen; `?pb=`/`?art=` ohne neue Verlaufseinträge; `/#/investitionen?art=xyz` wird bereinigt; Kombination ohne Treffer zeigt Leerzustand und "Filter zurücksetzen"; Balkenklick öffnet das Produkt; Tabelle scrollt bei 360 px im eigenen Container; lange Aufgabenbereichsnamen sind im aufgeklappten `wa-select` vollständig lesbar (im eingeklappten Feld kürzt Web Awesome unter Umständen).
- Parallele Pläne der Welle ändern ebenfalls `InvestitionenPage.vue`; beim Zusammenführen die Abschnitte nebeneinander lassen (mein Abschnitt steht in `<section aria-labelledby="om-investitionen-massnahmen">`).

## Self-Check: PASSED

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
