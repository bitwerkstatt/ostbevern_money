---
phase: 06-kontext-seiten
plan: 07
subsystem: ui
tags: [vue, echarts, vorbericht, rat-entscheidet, kennzahlkachel, vitest]

requires:
  - phase: 06-kontext-seiten
    provides: "06-01 vorbericht.zuschuesse_lfd_zwecke in haushalt.json (acht Posten, 120 T€, S. 47)"
  - phase: 06-kontext-seiten
    provides: "06-02 Rahmen RatEntscheidetPage (PageIntro, WertartEtikett)"
  - phase: 06-kontext-seiten
    provides: "06-03 HinweisNichtImHaushalt (variante kurz) und hinweis.test.ts"
provides:
  - "lib/zuschuesse.ts: Zuschuss, ZuschussGruppe, kitaZuschuesse(), weitereZuschuesse(), nichtBeeinflussbar(), zusammen(), ohneLeere()"
  - "ZuschussListe.vue: zwei Karten Kindertagesstätten und Weitere Zuschüsse (Balken in AUFWANDSART_FARBE, rd.-Label, Tabelle)"
  - "NichtBeeinflussbarBlock.vue: vier KennzahlKacheln (Kreisumlage, Gewerbesteuerumlage, Krankenhausinvestitionsumlage, Gesetzliche Sozialleistungen) mit Slot vergleich für 06-10"
  - "RatEntscheidetPage: Block, Einzelzuschüsse und Kurzhinweis BBO/TEO am Seitenende"
affects: [06-10, 06-12]

actuals:
  tokens: 7750
  tasks: 2
  commits: 4
plan_head_before: 0094bff21346ad5ff9315e86e2fbb928e81d29eb
plan_head_after: 8e74636ee2c7f37a89fa2d53b85dab3538f09624

tech-stack:
  added: []
  patterns:
    - "Datenmodul je Seitenabschnitt: Zuschuss mit wert null statt 0, Fehler bei fehlender Tabelle oder fehlendem Posten"
    - "Mehrere Balkendiagramme in einer ChartCard über BaseChart mit eigener beschreibung je Diagramm"
    - "Benannter Slot vergleich im Block für den Vergleichssatz der Folgeplanung"

key-files:
  created:
    - app/src/lib/zuschuesse.ts
    - app/src/lib/__tests__/zuschuesse.test.ts
    - app/src/components/ZuschussListe.vue
    - app/src/components/NichtBeeinflussbarBlock.vue
  modified:
    - app/src/pages/RatEntscheidetPage.vue
    - app/src/lib/__tests__/hinweis.test.ts

key-decisions:
  - "Die Zeile Zusammen der Kita-Karte steht als Beschreibung direkt unter dem Kartentitel, damit der Kartentitel exakt Kindertagesstätten lautet (Copywriting UI-SPEC)"
  - "Weitere Zuschüsse zeigt zwei Quellgruppen mit eigenem h3, eigener Seitenangabe und eigenem Diagramm statt einer vermischten Sortierung"
  - "Zusammen nimmt die gedruckte Gesamtzeile, sonst die Summe der vorhandenen Werte, ohne Wert gar nichts"
  - "Fehlender Transferposten oder fehlende Tabelle wirft einen Fehler mit Namen, statt still eine Karte zu verlieren"

patterns-established:
  - "nichtBeeinflussbar() liest die KL-Unterposten ausschließlich über baueKreisumlage, damit /ausgaben und /rat-entscheidet dieselben Zahlen zeigen"

requirements-completed: [RAT-02, RAT-03, UI-04]

coverage:
  - id: D1
    description: "Einzelzuschüsse (Kita-Einrichtungen, Kinder- und Jugendwerk, OGS, acht Posten lfd. Zwecke) stammen aus den Vorbericht-Daten; Σ Kita = 559.000 €, Σ lfd. Zwecke = 120.000 € = Transferposten"
    requirement: RAT-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/zuschuesse.test.ts#kitaZuschuesse, weitereZuschuesse, Einzelzuschüsse Haushalt 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "Block Was der Rat nicht beeinflussen kann zeigt Kreisumlage 10.147.000 €, Gewerbesteuerumlage 654.000 €, Krankenhausinvestitionsumlage 200.000 € und Sozialleistungen 491.000 € mit denselben KL-Werten wie /ausgaben; Posten mit 0 oder ohne Wert entfallen"
    requirement: RAT-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/zuschuesse.test.ts#nichtBeeinflussbar, ohneLeere, Nicht beeinflussbare Posten Haushalt 2026"
        status: pass
    human_judgment: false
  - id: D3
    description: "Kurzhinweis BBO/TEO schließt /rat-entscheidet als letztes Element ab; Block steht vor den Einzelzuschüssen"
    requirement: UI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/hinweis.test.ts#HinweisNichtImHaushalt auf /rat-entscheidet"
        status: pass
    human_judgment: false
  - id: D4
    description: "Optik und Layout der beiden Karten und der Kachelzeile bei 1280 px und 360 px (kein horizontales Scrollen, Silbentrennung Krankenhausinvestitionsumlage, Balkenbeschriftung rd.)"
    verification: []
    human_judgment: true
    rationale: "Kein Browser in der Linux-Sandbox; Layout und Silbentrennung sind nur im gerenderten Zustand beurteilbar (Task 2 human-check)"

duration: 12min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 07: Einzelzuschüsse, nicht beeinflussbare Posten und Kurzhinweis Summary

**/rat-entscheidet zeigt jetzt die Einzelzuschüsse aus dem Vorbericht (Kitas, Kinder- und Jugendwerk, OGS, Vereine, VHS, Sport, Musikschule) in zwei Balkenkarten, vier Kacheln für Kreisumlage, Gewerbesteuerumlage, Krankenhausinvestitionsumlage und Sozialleistungen sowie den Kurzhinweis BBO/TEO, alles datengetrieben mit PDF-Seite.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-10-06T06:00:00Z (geschätzt)
- **Completed:** 2026-10-06T06:12:00Z
- **Tasks:** 2 (Tracer plus TDD-Task, je RED- und GREEN-Commit)
- **Files modified:** 6 (4 neu, 2 geändert)

## Accomplishments

- `lib/zuschuesse.ts` liest Kita-Einrichtungen, Transfer-Zuschüsse und die acht Posten der laufenden Zwecke für das Haushaltsjahr aus `haushalt.vorbericht`; fehlende Tabellen oder Posten werfen mit Namen, ein fehlender Wert bleibt `null` und erscheint als „–“ ohne Balken.
- `ZuschussListe` bildet zwei Karten: Kindertagesstätten (sieben Einrichtungen, „Zusammen rd. 559.000 €“) und Weitere Zuschüsse (Transferaufwendungen, S. 46, und Zuschüsse für laufende Zwecke, S. 47, je eigenes Diagramm mit Quellenzeile). Balken in `AUFWANDSART_FARBE`, Label „rd. {Betrag}“, Höhe Zeilen × 40 px + 48 px, Tabelle in „Tabelle anzeigen“.
- `NichtBeeinflussbarBlock` zeigt die KL-Unterposten über `baueKreisumlage` (identisch zu /ausgaben) plus „Gesetzliche Sozialleistungen“ als `KennzahlKachel` mit „{Wertart} {Jahr} · PDF-Seite {n}“; Posten mit 0 oder ohne Wert entfallen; ein Slot `vergleich` ist für den Vergleichssatz aus 06-10 vorbereitet.
- `RatEntscheidetPage` rahmt die Abschnitte: Block, Einzelzuschüsse, `HinweisNichtImHaushalt variante="kurz"` als letztes Element.

## Task Commits

1. **Task 1: Tracer Einzelzuschüsse** — `6f803a0` (test, RED: 9 Assertions schlagen fehl) und `24f9d64` (feat, GREEN)
2. **Task 2: Block nicht beeinflussbar und Kurzhinweis** — `0c37318` (test, RED: 10 Assertions schlagen fehl) und `8e74636` (feat, GREEN)

**Plan metadata:** folgt als docs-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/lib/zuschuesse.ts` — Datenlogik für Einzelzuschüsse und nicht beeinflussbare Posten
- `app/src/lib/__tests__/zuschuesse.test.ts` — Σ-Tests gegen Transferposten und Gesamtzeile, KL-Gleichheit mit `lib/kreisumlage.ts`, Sollwerte 2026 über `describe.runIf`
- `app/src/components/ZuschussListe.vue` — zwei Karten mit Balken, Quellenzeilen und Tabellen
- `app/src/components/NichtBeeinflussbarBlock.vue` — Kachelraster `repeat(auto-fit, minmax(160px, 1fr))`
- `app/src/pages/RatEntscheidetPage.vue` — Einbau der drei Abschnitte
- `app/src/lib/__tests__/hinweis.test.ts` — Reihenfolge- und Variantenprüfung für /rat-entscheidet

## Decisions Made

- Die Zeile „Zusammen“ der Kita-Karte steht als Beschreibung unter dem Titel, nicht im Titel selbst: Der Kartentitel bleibt exakt „Kindertagesstätten“ wie im Copywriting-Vertrag, die Zeile steht direkt darunter.
- Zwei Quellgruppen in „Weitere Zuschüsse“ bleiben getrennt (je h3, Quellenzeile mit Seitenzahl, Diagramm, Tabelle), damit jede Gruppe mit ihrer Seite benannt ist und Transfer- und Einzelposten nicht in einer Sortierung verschwimmen.
- Die Datenstruktur enthält keine `ist_gesamt`-Zeilen unter `posten` (die Gesamtzeile liegt in `gesamt_vorbericht`), daher ist die geforderte Ausnahme dieser Zeilen strukturell erfüllt.

## Deviations from Plan

None - plan executed exactly as written. Die Plan-Verifikation nutzt `npm ci` im Scratch-Verzeichnis; stattdessen kam die vorhandene Linux-`node_modules`-Kopie zum Einsatz (Vorgabe aus den Umgebungshinweisen, identische package-lock.json). Die Befehle (`test`, `type-check`, `lint`, `format:check`, `build`) liefen unverändert.

## Issues Encountered

- Prettier formatierte nach dem Schreiben drei Dateien im Scratch-Verzeichnis um; die Änderungen wurden ins Worktree zurückkopiert und vor jedem Commit per `format:check` bestätigt.
- Der Task-2-Befehl `human-check` (Dev-Server bei 1280 px und 360 px) konnte nicht laufen, weil die Sandbox keinen Browser hat. Er bleibt für die Verifikation am Phasenende offen (siehe coverage D4).

## Verification

- Scratch-Kopie von `app/`: `npm run type-check`, `lint`, `format:check` grün; `npm run test` 28 Dateien, 1093 Tests grün; `npm run build` erfolgreich (nur die bekannte Warnung zur Chunkgröße).
- Akzeptanzkriterien beider Tasks: alle PASS (`export function kitaZuschuesse`, `AUFWANDSART_FARBE`, `export function nichtBeeinflussbar`, `variante="kurz"`, Überschrift im Block, kein Jahreswert im Code von `zuschuesse.ts`).

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None. T-06-17: Tooltips laufen über `horizontaleBalkenOption` mit `tooltipZeilen`, kein `v-html`. T-06-18: Σ-Tests gegen Transferposten und Kita-Gesamtzeile, KL-Werte gegen `lib/kreisumlage.ts`. T-06-SC: keine neue Abhängigkeit.

## Next Phase Readiness

- 06-10 kann den Vergleichssatz in den Slot `vergleich` des `NichtBeeinflussbarBlock` setzen und liefert den Bindungsgrad-Balken oberhalb des Blocks.
- 06-12 prüft den Glossaranker `nicht_im_haushalt`, auf den der Kurzhinweis verlinkt.

## Self-Check: PASSED

Alle vier neuen Dateien vorhanden; die Commits 6f803a0, 24f9d64, 0c37318 und 8e74636 stehen im Log (`git log --grep="06-07"`).

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
