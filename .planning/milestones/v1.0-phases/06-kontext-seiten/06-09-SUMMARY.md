---
phase: 06-kontext-seiten
plan: 09
subsystem: ui
tags: [vue3, echarts, investitionen, schulden, verpflichtungsermaechtigungen, finanzierung, tdd]

requires:
  - phase: 06-kontext-seiten
    provides: "06-04: Text schulden_anstieg und Glossar verpflichtungsermaechtigung; 06-06: InvestitionenPage mit Maßnahmen und lib/investitionen.ts; 06-02: SCHULDEN_FARBEN, BERECHNET_DECAL, jahresAchse"
provides:
  - "lib/schulden.ts: Schuldenreihen unverändert aus den Daten, Kennzahlen des Vorjahrs, Achse und Decal nur aus berechnet[i], Option, Tabelle, Satz zu fehlenden Liquiditätskrediten"
  - "lib/finanzierung.ts: VE je Fälligkeitsjahr (Σ = GFP-VE), Finanzierungsreihen = GFP-Zeilen, Einzahlungsaufteilung Z. 18-22, Optionen und Tabellen"
  - "SchuldenstandDiagramm.vue, VeFaelligkeiten.vue, FinanzierungsDiagramm.vue"
  - "InvestitionenPage: drei Kennzahlkacheln und die Abschnitte Verpflichtungsermächtigungen, Wie die Investitionen bezahlt werden, Schulden"
  - "charts/beschriftung.ts: gemeinsamer zweizeiliger Betragstext"
affects: [06-12]

actuals:
  tokens: 20800
  tasks: 3
  commits: 7

plan_head_before: 14ef1e238657bf4cf1989b34397f37fbc86ace94
plan_head_after: a2bb53ff0645e6fe17c87539ab9763f391447bfd

tech-stack:
  added: []
  patterns:
    - "Reine Builder in lib/ liefern ECharts-Option und DatenTabelle-Modell, die Vue-Komponente verdrahtet nur; Decal, Achsenzeile und Beschriftung sind per Test an das Datenfeld gebunden"
    - "Beschriftung nur des größten Werts je Jahr über die Formatterfunktion der Serie, damit die Datenpunkte unverändert die Finanzplan-Werte bleiben"
    - "Pure Gruppierfunktion mit Daten als Parameter (baueVeFaelligkeiten) für Zero-One-Many-Tests ohne Eingriff in die Jahrgangsdaten"

key-files:
  created:
    - app/src/lib/schulden.ts
    - app/src/lib/__tests__/schulden.test.ts
    - app/src/lib/finanzierung.ts
    - app/src/lib/__tests__/finanzierung.test.ts
    - app/src/components/SchuldenstandDiagramm.vue
    - app/src/components/VeFaelligkeiten.vue
    - app/src/components/FinanzierungsDiagramm.vue
    - app/src/charts/beschriftung.ts
    - app/src/charts/__tests__/beschriftung.test.ts
  modified:
    - app/src/pages/InvestitionenPage.vue

key-decisions:
  - "Liquiditätskredite stehen nicht im Stapel und nicht im Schuldenstand (gesamt = Investitionskredite + NRW.Bank), nur in der Tabelle und im datengetriebenen Satz; null erscheint als Strich, nie als 0 (Nutzerentscheidung 4, überschreibt UI-SPEC E9)"
  - "Die Kachel 'Schulden je Einwohner' trägt 'berechnet' nur, wenn berechnet[Vorjahr] wahr ist; im Jahrgang 2026 ist es falsch, der Wert steht gedruckt auf der Einwohner-Seite (Nutzerentscheidung 4)"
  - "Berechnete Jahre folgen allein schuldenstand.berechnet (heute 2027-2029, nicht 2026 wie D-09 schrieb); keine Jahresliste im Code (UI-SPEC Offene Annahme 1)"
  - "Gruppierte Finanzierungssäulen beschriften immer zweizeilig ('16,8' / 'Mio. €'), bis 699 px nur den größten Wert je Jahr, damit sich benachbarte Beschriftungen nicht überlappen"

patterns-established:
  - "etikett-Schlüssel in der Tabellenzeile plus Slot zeilenzusatz für BerechnetEtikett (wie ProduktPage)"

requirements-completed: [INV-02, INV-03, INV-04]

duration: ca. 60min
completed: 2026-10-06
status: complete

coverage:
  - id: D1
    description: "Schuldenstand 2024-2029 als gestapelte Säulen (Investitionskredite + NRW.Bank, Summe über der Säule), BERECHNET_DECAL und dritte Achsenzeile genau bei berechnet === true, keine Liquiditätskredite im Stapel, Strich statt 0, Satz zu den Jahren ohne Liquiditätskredite, Tabelle und So wurde gerechnet; Kacheln 7,71 Mio. € und 656 € ohne berechnet"
    requirement: INV-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/schulden.test.ts#schuldenstandOption (D-09, INV-04)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/schulden.test.ts#schuldenKennzahlen (D-09, D-10, Nutzerentscheidung 4)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/schulden.test.ts#Jahrgang 2026 (ROADMAP SC 2)"
        status: pass
    human_judgment: true
    rationale: "Streifenmuster, Lesbarkeit der dreizeiligen Achse und der Summenbeschriftungen bei 360 px sowie die Legende sind ohne Browser nicht prüfbar; Human-Check ist für den Abschluss-Walkthrough der Phase vorgesehen"
  - id: D2
    description: "Verpflichtungsermächtigungen: Säulen je Fälligkeitsjahr (2027 9,4 Mio. €, 2028 2,2 Mio. €), Kachel 11,6 Mio. €, Tabelle mit Maßnahmen und Links, Σ = GFP-VE, jede VE-Zeile findet ihre Maßnahme"
    requirement: INV-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/finanzierung.test.ts#veFaelligkeiten und veGesamt (INV-02, D-10, T-06-23)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/finanzierung.test.ts#baueVeFaelligkeiten (INV-02, D-10)"
        status: pass
    human_judgment: true
    rationale: "Tabellenzelle mit Produktlinks, Tastaturbedienung und Layout sind ohne Browser nicht prüfbar"
  - id: D3
    description: "Finanzierung: zwei gruppierte Säulendiagramme (Investitionen und Einzahlungen, Kreditaufnahme und Tilgung) aus den Finanzplan-Reihen mit Zweizeilen-Achse, Textlegende, nur größter Wert je Jahr beschriftet bis 699 px, Aufklapper Woraus die Einzahlungen bestehen (Z. 18-22, Σ = Z. 23 bis auf 1 € im ersten Jahr)"
    requirement: INV-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/finanzierung.test.ts#finanzierungsOption (INV-03, D-08, UI-SPEC E8)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/finanzierung.test.ts#einzahlungsAufteilung (INV-03, D-08)"
        status: pass
      - kind: other
        ref: "npm run type-check && lint && format:check && test && build (Scratch-Kopie)"
        status: pass
    human_judgment: true
    rationale: "Lesbarkeit der Beschriftungen bei 1280 und 360 px und das Zusammenspiel von Legende und Farben sind ohne Browser nicht prüfbar (human-check des Plans)"
---

# Phase 6 Plan 9: Schulden, Verpflichtungsermächtigungen und Finanzierung Summary

**/investitionen zeigt jetzt Schuldenstand 7,71 Mio. € und 656 € je Einwohner (gedruckt, ohne 'berechnet'), 11,6 Mio. € Verpflichtungsermächtigungen nach Fälligkeit sowie Finanzierung und Schuldenentwicklung als Diagramme, deren Summen und 'berechnet'-Markierung per Test an die Daten gebunden sind**

## Performance

- **Duration:** ca. 60 min
- **Completed:** 2026-10-06
- **Tasks:** 3 (Tracer, zwei TDD-Aufgaben)
- **Files modified:** 10 (9 neu, 1 geändert)

## Accomplishments

- **Schulden (INV-04):** `lib/schulden.ts` liefert die Reihen unverändert aus `investitionen.json`. `SchuldenstandDiagramm.vue` stapelt Investitionskredite und NRW.Bank mit 2-px-Weißtrenner, die Summe aus `schuldenstand.gesamt` steht über der Säule (bis 699 px zweizeilig). `BERECHNET_DECAL` und die dritte Achsenzeile stehen genau an den Jahren mit `berechnet[i] === true` (heute 2027-2029). Darunter: farbige Legende mit Streifenerklärung (nur wenn ein Jahr berechnet ist), der Satz "Für 2027, 2028 und 2029 nennt der Haushaltsplan keine Liquiditätskredite." (Jahre aus den Daten), Tabelle mit "–" für `null` und das Etikett "berechnet" in der ersten Zelle berechneter Jahre, "So wurde gerechnet" mit der Formel aus den Daten und PDF-Seite 310.
- **Kacheln:** "Schuldenstand Ende {Vorjahr}" (7,71 Mio. €), "Schulden je Einwohner" (656 €, Seiten 310 und 25, kein Etikett, solange `berechnet[Vorjahr]` falsch ist) und "Verpflichtungsermächtigungen" (11,6 Mio. €, Seiten der VE-Zeilen).
- **VE (INV-02):** `baueVeFaelligkeiten` bündelt je Fälligkeitsjahr und `(produkt, massnahme_id)`; eine VE-Zeile ohne Maßnahme wirft mit Produkt und Kennung. `veGesamt` = Σ Zeilen = `finanzplan.GESAMT.ve.auszahlungen_investitionen` (Test). `VeFaelligkeiten.vue`: Säulen in `INVEST_FARBE`, Achse nur Jahre, Caption "Fälligkeit laut Haushaltsplan", Tabelle mit Maßnahmen als Links auf `/produkt/:code`; auf der Seite mit `ErklaerText verpflichtungsermaechtigungen` und `GlossarBegriff verpflichtungsermaechtigung`.
- **Finanzierung (INV-03):** `finanzierungsReihen` = GFP-Zeilen 23, 30, 33, 35 (Test gegen `haushalt.finanzplan` und gegen `investitionen.finanzierung`). `finanzierungsOption` liefert genau zwei Säulenserien (dunkel `INVEST_FARBE`, hell `KATEGORIE_FARBEN[2]`) mit unveränderten Datenpunkten, Zweizeilen-Achse, bis 699 px Beschriftung nur am größten Wert je Jahr (Gleichstand: erste Serie). `einzahlungsAufteilung` liefert Z. 18-22 mit den gedruckten Namen; Σ = Z. 23 exakt ab dem zweiten Jahr der Daten, im ersten Jahr 1 € Abweichung (Fußnote nennt das datengetrieben).
- **Seite:** Reihenfolge Kennzahlen, Maßnahmen, Verpflichtungsermächtigungen, Wie die Investitionen bezahlt werden, Schulden (UI-SPEC Page Layouts); `ErklaerText schulden_anstieg` steht unter der Schuldenkarte.

## Task Commits

1. **Task 1: Tracer, Schuldenstand und Kennzahlen** - `061b18a` (feat; Tests und Implementierung gemeinsam, Tracer)
2. **Task 2: Verpflichtungsermächtigungen** - RED `a3963ae` (test), GREEN `70730fd` (feat), UI `ea82601` (feat)
3. **Task 3: Finanzierung** - RED `f955b0d` (test), GREEN `331c576` (feat), UI `a2bb53f` (feat)

**Plan metadata:** folgt als `docs(06-09)`-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/lib/schulden.ts` - Schuldenreihen, Kennzahlen, Option, Tabelle, Satz
- `app/src/lib/finanzierung.ts` - VE-Fälligkeiten, Finanzierungsreihen, Einzahlungsaufteilung, Optionen, Tabellen
- `app/src/lib/__tests__/schulden.test.ts`, `finanzierung.test.ts` - Identitäten, Datenbindung, Zero-One-Many mit synthetischen Daten, Jahrgangswerte unter `describe.runIf`
- `app/src/components/SchuldenstandDiagramm.vue`, `VeFaelligkeiten.vue`, `FinanzierungsDiagramm.vue` - Diagrammkomponenten
- `app/src/charts/beschriftung.ts` (+ Test) - `zweizeilig()`
- `app/src/pages/InvestitionenPage.vue` - Kacheln und drei neue Abschnitte

## Decisions Made

Siehe `key-decisions`. Die beiden dokumentierten Abweichungen aus dem Plan-Kontext (Nutzerentscheidung 4, 2026-10-05): Liquiditätskredite werden nicht gestapelt und zählen nicht zu `gesamt`; die 656-€-Kachel trägt kein "berechnet", weil der Wert auf S. 25 gedruckt ist.

## TDD Gate Compliance

Task 2: RED `a3963ae` (12 von 16 Tests scheitern an Behauptungen gegen ein wirkungsloses Gerüst), GREEN `70730fd` (16 grün), UI separat in `ea82601`. Task 3: RED `f955b0d` (22 Tests scheitern, einige über die Hilfsfunktion der Tests, weil das Gerüst keine Serie liefert), GREEN `331c576` (alle grün), UI separat in `a2bb53f`. Kein REFACTOR-Commit nötig. Task 1 ist ein Tracer: Tests und Implementierung in einem Commit (`061b18a`). Das formelle RED-Evidence-Protokoll (`check tdd-red-evidence`) entfällt, da der Plan `type: execute` ist und `workflow.tdd_mode` nicht gilt.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] "berechnet" in der Tabelle über die erste Zelle statt im Spaltenkopf**
- **Found during:** Task 1
- **Issue:** Der Plan nennt das Etikett am Spaltenkopf "je Einwohner". `DatenSpalte.titel` ist ein String; ein Kopf mit Komponente würde `DatenTabelle` ändern (geteilte Basiskomponente, Konvention: Namen und Props bleiben).
- **Fix:** Spaltenkopf "Je Einwohner"; das Etikett steht über den vorhandenen Slot `zeilenzusatz` in der Jahreszelle berechneter Jahre (kennzeichnet damit alle Werte dieser Zeile), und die Fußnote sagt datengetrieben, dass nur der Wert des Vorjahrs gedruckt ist.
- **Files modified:** app/src/lib/schulden.ts, app/src/components/SchuldenstandDiagramm.vue
- **Committed in:** 061b18a

**2. [Rule 2 - Missing Critical] Quelle der VE-Karte als Text mit allen Seiten**
- **Found during:** Task 2
- **Issue:** Der Plan nennt "pdf = page of the VE rows"; die VE-Zeilen liegen auf mehreren Seiten, `ChartCard.pdf` nimmt nur eine.
- **Fix:** `quelle="Haushaltsplan, PDF-Seiten …"` aus den Daten (`vePdfSeiten()`), Kachel zeigt dieselben Seiten.
- **Files modified:** app/src/pages/InvestitionenPage.vue, app/src/lib/finanzierung.ts
- **Committed in:** 70730fd, ea82601

**3. [Rule 2 - Missing Critical] Fußnote zur 1-€-Abweichung in der Einzahlungsaufteilung**
- **Found during:** Task 3
- **Issue:** Σ der Zeilen 18-22 weicht im ersten Jahr der Daten um 1 € von der gedruckten Z. 23 ab (innerhalb der Plangrenze, aber sichtbar in der Tabelle).
- **Fix:** `einzahlungsAbweichungen()` (getestet) speist eine datengetriebene Fußnote; ohne Abweichung entfällt sie.
- **Files modified:** app/src/lib/finanzierung.ts, app/src/components/FinanzierungsDiagramm.vue
- **Committed in:** 331c576, a2bb53f

**4. [Rule 2 - Missing Critical] Zweizeilige Beschriftung der gruppierten Säulen auch bei breiter Darstellung**
- **Found during:** Task 3
- **Issue:** Zwölf Säulen mit "16,8 Mio. €" einzeilig überlappen auch bei 1280 px; ECharts würde Beschriftungen zufällig ausblenden.
- **Fix:** `charts/beschriftung.ts` (`zweizeilig`, mit Test) für Finanzierung und Schuldenstand (bis 699 px); neue Datei außerhalb der Plan-Dateiliste, additiv.
- **Files modified:** app/src/charts/beschriftung.ts, app/src/charts/__tests__/beschriftung.test.ts, app/src/lib/schulden.ts, app/src/lib/finanzierung.ts
- **Committed in:** 331c576

---

**Total deviations:** 4 auto-fixed (4 missing critical, alle additiv)
**Impact on plan:** kein Scope Creep. Zusätzliche, nicht im Plan genannte Exporte: `schuldenstandOption`, `schuldenTabelle`, `jahreListe`, `liquiditaetsSatz`, `hatBerechneteJahre`, `veOption`, `veTabelle`, `vePdfSeiten`, `baueVeFaelligkeiten`, `einzahlungsAbweichungen`, `finanzierungsTabelle`, `einzahlungsTabelle`, `finanzierungsLegende`; sie halten die Logik testbar außerhalb der Vue-Dateien.

## Issues Encountered

- App-Kette nicht per `npm ci` gegen das Netz, sondern in einer Scratch-Kopie mit vorhandenem Linux-`node_modules` (Lockfile identisch): type-check, lint, format:check, vitest (33 Dateien, 1283 Tests) und build grün. Der Tracer-Gate lief damit auf dem Stand von `061b18a` durch (ohne Human-Check), danach auf jedem Task-Ende.
- Der Human-Check von Task 3 (Dev-Server bei 1280 und 360 px) war ohne Browser nicht ausführbar. Ersatz: ein Wegwerf-Test in der Scratch-Kopie hat die drei Optionen per ECharts-SSR als SVG gerendert und die Texte geprüft (Achse "berechnet" nur bei 2027-2029, Summenbeschriftungen, bei 320 px nur der größte Wert je Jahr in den Finanzierungsdiagrammen, VE-Säulen 9,4 und 2,2 Mio. €). Nicht im Repo.
- Das Commit-Ledger unter `.git/worktrees/…/gsd-plan-head-before-06-09` war schreibbar; `plan_head_before` ist der Spawn-Basiscommit `14ef1e2`.

## Known Stubs

Keine.

## Threat Flags

Keine neue Angriffsfläche über die Plan-Bedrohungen hinaus. T-06-23 (Identitätstests: gesamt, Σ VE = GFP-VE, Σ Z. 18-22 = Z. 23, Reihen = GFP-Zeilen), T-06-24 (Decal und Achsenzeile nur aus `berechnet`, gegen das Array getestet) und T-06-25 (Tooltips ausschließlich über `tooltipZeilen`, kein Roh-HTML; `quelltext.test.ts` grün) sind durch Tests belegt; keine neue Abhängigkeit (T-06-SC).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Offen für den Abschluss-Walkthrough: `/investitionen` bei 1280 und 360 px prüfen (drei Kacheln 7,71 Mio. €, 656 € ohne "berechnet", 11,6 Mio. €; VE-Säulen 2027 und 2028; beide Finanzierungsdiagramme mit Legende, bei 360 px nur der größte Wert je Jahr; Schuldenstand mit Streifen und "berechnet" genau bei 2027-2029, kein Liquiditätskredit-Segment, Satz zu den Jahren ohne Liquiditätskredite; "So wurde gerechnet" bricht um; Tabellen scrollen nur im eigenen Container; Produktlinks in der VE-Tabelle per Tastatur).
- Parallele Pläne der Welle ändern ebenfalls `InvestitionenPage.vue`; beim Zusammenführen die Abschnitte nebeneinander lassen (Kennzahlenliste `om-investitionen__kacheln` nach dem Hinweis, Abschnitte mit `aria-labelledby` `om-investitionen-ve`, `-finanzierung`, `-schulden` nach `-massnahmen`).

## Self-Check: PASSED

- Dateien vorhanden: schulden.ts, schulden.test.ts, finanzierung.ts, finanzierung.test.ts, SchuldenstandDiagramm.vue, VeFaelligkeiten.vue, FinanzierungsDiagramm.vue, beschriftung.ts, beschriftung.test.ts, InvestitionenPage.vue.
- Commits vorhanden: 061b18a, a3963ae, 70730fd, ea82601, f955b0d, 331c576, a2bb53f.
- Acceptance Criteria aller drei Tasks (grep-Prüfungen, keine Jahreszahl in `schulden.ts` und `finanzierung.ts` außerhalb von Kommentaren) bestanden; Plan-Verifikation (Kette in Scratch-Kopie) grün.

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
