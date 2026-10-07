---
phase: 06-kontext-seiten
plan: 05
subsystem: ui
tags: [vue3, echarts, vue-echarts, vitest, zeitreihen, ergebnisplan]

requires:
  - phase: 06-kontext-seiten (Plan 02)
    provides: EntwicklungPage-Rahmen, charts/wertartStil.ts (linienSerie, jahresAchse, saeulenStil, LEGENDE_TEXT), Theme-Exporte (KL_FARBE, ZINSEN_FARBE, SCHWELLE_FARBE, HOHL_FLAECHE)
  - phase: 05-leitfragen-seiten
    provides: BaseChart, ChartCard, DatenTabelle, BerechnetEtikett, ErklaerText, GlossarBegriff, lib/zeitreihen.ts, lib/kreisumlage.ts, lib/aufwandsarten.ts
provides:
  - lib/entwicklung.ts mit Jahresreihen für Erträge, Aufwendungen, Ergebnis vor und nach globalem Minderaufwand sowie den fünf Posten-Reihen und der Veränderung in Prozent
  - EntwicklungsDiagramm.vue (zwei Linien mit Wertartstil und Direktbeschriftung), ErgebnisBalken.vue (Jahresergebnis nach Minderaufwand als Säulen), PostenZeitreihe.vue (Karte je Posten mit Veränderungszeile)
  - /entwicklung mit den Abschnitten „Erträge, Aufwendungen und Ergebnis“ und „Wichtige Posten im Verlauf“
affects: [06-06 (Rücklagen-Abschnitt derselben Seite), 06-12, verify-work Phase 6]

actuals:
  tokens: 12000
  tasks: 3
  commits: 5

plan_head_before: 0094bff21346ad5ff9315e86e2fbb928e81d29eb
plan_head_after: 2cba981de2ba45e3af225e67c15aee403e4db570

tech-stack:
  added: []
  patterns:
    - "Jahresreihen werden nur gelesen (GEP-Zeilen, Vorbericht-Posten), nie neu gerechnet; ein fehlender Schlüssel wirft mit seinem Namen"
    - "Jedes Jahresdiagramm der Seite teilt jahresAchse(haushalt.jahre, haushalt.wertarten) und die Wertartstile aus wertartStil.ts"
    - "Querprüfung gegen die Quellen von /einnahmen und /ausgaben im Test (baueZeitreihe, baueKreisumlage, baueAufwandsarten) statt gepinnter Zahlen"

key-files:
  created:
    - app/src/lib/entwicklung.ts
    - app/src/lib/__tests__/entwicklung.test.ts
    - app/src/components/EntwicklungsDiagramm.vue
    - app/src/components/ErgebnisBalken.vue
    - app/src/components/PostenZeitreihe.vue
  modified:
    - app/src/pages/EntwicklungPage.vue
    - app/src/lib/zeitreihen.ts

key-decisions:
  - "Der globale Minderaufwand steht in den Reihen als positive Kürzung (GEP-Zeile × −1, nie −0); damit gilt Ergebnis nach = Ergebnis vor + Minderaufwand wie im Plan formuliert, und die Tabelle zeigt keine doppelte Negation"
  - "Ergebnis vor Minderaufwand wird aus der GEP-Zeile jahresergebnis gelesen, nicht aus Erträge − Aufwendungen: Das erste Planjahr weicht dort um 1 € ab (PDF-Rundung); der Test erlaubt genau 1 € Toleranz"
  - "Die Jahresergebnis-Säulen lesen zeilen.ergebnis_nach_minderaufwand (Nutzerentscheidung 1), der Untertitel sagt „nach globalem Minderaufwand“, die Linien bleiben „vor“"
  - "Auf Bildschirmen bis 699 px trägt nur die letzte Ergebnissäule eine Beschriftung; Tooltip und Tabelle tragen die übrigen Werte (UI-SPEC: was nicht passt, wird nicht beschriftet)"
  - "ergebnisBeschriftung hat den optionalen Parameter genau, damit der Tooltip den Betrag auf den Euro genau nennt, die Säule aber gekürzt"

patterns-established:
  - "Posten-Karte: ChartCard (Titel, PDF-Seite) umschließt PostenZeitreihe (Veränderungszeile, Linie 240 px, Textlegende, Tabelle, optional Erklärtext)"
  - "veraenderungText: Plus, Minuszeichen U+2212 oder „–“; zeigt die Anzeige 0, steht keine Richtung davor"

requirements-completed: [ENTW-01, ENTW-02]

coverage:
  - id: D1
    description: "Erträge und Aufwendungen als Reihen und Zwei-Linien-Diagramm je Jahr aus haushalt.jahre, vor globalem Minderaufwand, mit Wertart je Jahr"
    requirement: "ENTW-01"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#baueErgebnisReihen (ENTW-01, D-11)"
        status: pass
      - kind: other
        ref: "npm run type-check && lint && format:check && test && build (Scratch-Kopie)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Jahresergebnis nach Minderaufwand als Säulen um die Nulllinie, identisch zum Startseitenwert; Defizit/Überschuss-Beschriftung; Tabelle mit Ergebnis vor und nach Minderaufwand"
    requirement: "ENTW-01"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#zeigt das Jahresergebnis des Haushaltsjahrs wie die Startseite"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#ergebnisBeschriftung (ENTW-01, Säulenbeschriftung)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#ergebnisTabelle (ENTW-01, Tabelle zur Säule)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Fünf Posten-Zeitreihen (Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personalaufwand, Zinsen) über haushalt.jahre mit denselben Quellen wie /einnahmen und /ausgaben und Veränderung in Prozent"
    requirement: "ENTW-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#bauePostenReihe (ENTW-02, D-12, D-13)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#veraenderung (ENTW-02, D-13)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/entwicklung.test.ts#veraenderungText (ENTW-02, D-13)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Lesbarkeit der zweizeiligen Jahresachse (Jahr plus Ist/Ansatz/Planung), Platz der Direktbeschriftungen und der Säulenbeschriftung, Rasteraufteilung bei 360 px, 700 px und 1280 px"
    verification: []
    human_judgment: true
    rationale: "Das Layout entsteht erst im Browser (Canvas-Textbreiten, Label-Platzierung); der Testlauf läuft in Node ohne DOM, und in der Sandbox steht kein Browser zur Verfügung. Human-Check ist für den Abschluss-Walkthrough der Phase vorgesehen (RESEARCH A3)."
---

# Phase 6 Plan 5: Entwicklung (Erträge, Aufwendungen, Ergebnis, Posten) Summary

**/entwicklung zeigt Erträge und Aufwendungen als zwei Linien, das Jahresergebnis nach globalem Minderaufwand (Satzungswert wie auf /start) als Säulen um die Nulllinie und fünf Posten-Zeitreihen mit Veränderung in Prozent; alle Reihen sind reine Lesezugriffe auf `haushalt.json` und im Test gegen die Quellen von /einnahmen und /ausgaben gesichert**

## Performance

- **Duration:** ca. 35 min
- **Completed:** 2026-10-06T06:16:00Z
- **Tasks:** 3 (Tracer, zwei TDD-Aufgaben)
- **Files modified:** 7 (5 neu, 2 geändert)

## Accomplishments

- `lib/entwicklung.ts`: `baueErgebnisReihen()` (Erträge, Aufwendungen, Ergebnis vor, Minderaufwand, Ergebnis nach; je Jahr aus `haushalt.jahre` mit Wertart und GEP-Seite), `ergebnisBeschriftung`, `ergebnisTabelle`, `ENTWICKLUNG_POSTEN`, `bauePostenReihe`, `veraenderung`, `veraenderungText`, `postenFussnote`. Keine Jahreszahl im Quelltext (Test prüft das), keine Grundzahl-Jahre (D-12).
- `EntwicklungsDiagramm.vue`: Erträge (`ERTRAG_FARBE`) und Aufwendungen (`AUFWANDSART_FARBE`) je Wertart als eigene Serie mit den gemeinsamen Linienstilen, zweizeilige Achse über `jahresAchse`, y ab 0, Direktbeschriftung am letzten Punkt (die Linie mit dem größeren Endwert trägt den Text oberhalb), Textlegende, Tabelle im Aufklapper.
- `ErgebnisBalken.vue`: Säulen von `ergebnis_nach_minderaufwand`, Farbe nach Vorzeichen, Planung hohl über `saeulenStil`, Nulllinie 1 px per `markLine`, Beschriftung „Defizit …“/„Überschuss …“, Achsenbeschriftung am unteren Rand statt an der Nulllinie, Tabelle mit Erträge, Aufwendungen, Ergebnis vor Minderaufwand, Minderaufwand (Kürzung) und Ergebnis nach Minderaufwand.
- `PostenZeitreihe.vue`: Veränderungszeile „Veränderung {erstes} → {letztes}: {±Prozent}“ mit `BerechnetEtikett` (bei „–“ ohne Etikett), Linie 240 px mit eigener y-Achse ab 0 und `connectNulls: false`, „rd.“ in Tooltip und Tabelle bei T€-Werten, Quellseite in der Fußnote, Erklärtext `kreisumlage` im Aufklapper „So funktioniert die Kreisumlage“.
- `EntwicklungPage.vue`: Abschnitt „Erträge, Aufwendungen und Ergebnis“ (zwei Karten plus neutraler Callout mit Pipeline-Text und `GlossarBegriff globaler_minderaufwand`) und Abschnitt „Wichtige Posten im Verlauf“ (Raster aus fünf Karten).

## Task Commits

1. **Task 1: Tracer, Erträge und Aufwendungen als Liniendiagramm** - `0ee8c62` (feat)
2. **Task 2: Jahresergebnis nach Minderaufwand, Callout, Tabelle** - RED `9f11156` (test), GREEN `42c7a7e` (feat)
3. **Task 3: Fünf Posten-Zeitreihen mit Veränderung** - RED `43f1cf8` (test), GREEN `2cba981` (feat)

**Plan metadata:** folgt als `docs(06-05)`-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/lib/entwicklung.ts` - Jahresreihen, Beschriftung, Tabelle, Posten, Veränderung
- `app/src/lib/__tests__/entwicklung.test.ts` - 49 Tests (Identitäten, Querprüfung gegen /einnahmen und /ausgaben, Sollwerte 2026, Quelltext ohne Jahreszahl)
- `app/src/components/EntwicklungsDiagramm.vue`, `ErgebnisBalken.vue`, `PostenZeitreihe.vue` - die drei Diagrammkomponenten
- `app/src/pages/EntwicklungPage.vue` - zwei neue Abschnitte
- `app/src/lib/zeitreihen.ts` - `zeitreihenSerien` akzeptiert jede Reihe mit `jahr`, `wert`, `wertart`

## Decisions Made

Siehe `key-decisions` im Frontmatter. Dokumentierte Abweichung von der UI-SPEC (Nutzerentscheidung 1, 2026-10-05): Die Jahresergebnis-Säulen lesen `zeilen.ergebnis_nach_minderaufwand` statt `zeilen.jahresergebnis`; der Untertitel nennt „nach globalem Minderaufwand“, die Linien bleiben „vor“. Damit zeigen die Säulen für das erste Planjahr +191.990 € und für das letzte −3.557.700 € (Test, nur bei Haushaltsjahr 2026) und stimmen mit der Startseite überein (Test über `baueKennzahlen`).

## TDD Gate Compliance

Task 2: RED `9f11156` (6 Tests scheitern an Assertions gegen das wirkungslose Gerüst), GREEN `42c7a7e`. Task 3: RED `43f1cf8` (20 Tests scheitern), GREEN `2cba981`. Task 1 ist ein Tracer (ein feat-Commit, Tests im selben Commit). Kein REFACTOR-Commit nötig. Wie in 06-02 enthält der RED-Commit ein Gerüst der neuen Exporte, damit nicht der Modulimport der Fehlergrund ist.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Ergebnis vor Minderaufwand weicht im ersten Planjahr um 1 € von Erträge − Aufwendungen ab**
- **Found during:** Task 1 (Datenprüfung)
- **Issue:** Der Plan formuliert `ergebnisVor = ertraege − aufwendungen = zeilen.jahresergebnis`. Für das erste Planjahr ergibt Erträge − Aufwendungen 191.991 €, die GEP-Zeile nennt 191.990 € (Rundung im PDF; die Spezifikation erlaubt 1 €).
- **Fix:** `ergebnisVor` wird aus der GEP-Zeile gelesen (nie neu gerechnet); der Test prüft die Identität mit genau 1 € Toleranz.
- **Files modified:** app/src/lib/entwicklung.ts, app/src/lib/__tests__/entwicklung.test.ts
- **Committed in:** 0ee8c62

**2. [Rule 2 - Missing Critical] Vorzeichen des globalen Minderaufwands und negatives Null**
- **Found during:** Task 2
- **Issue:** Die GEP-Zeile führt die Kürzung negativ (−564.600 €); eine Summe „vor + Zeile“ ergäbe das falsche Ergebnis, und `−0` (Jahr ohne Minderaufwand) würde als „-0 €“ formatiert.
- **Fix:** Die Reihe `minderaufwand` trägt die positive Kürzung, ein Wert 0 bleibt echte Null; Test `Object.is(wert, 0)` sichert das.
- **Committed in:** 9f11156, 42c7a7e

**3. [Rule 3 - Blocking] zeitreihenSerien nahm nur `Zeitpunkt[]`**
- **Found during:** Task 1
- **Issue:** Die Reihen aus `lib/entwicklung.ts` sind keine `Zeitpunkt` (kein `quelle`), das Serien-Splitting wäre sonst dupliziert worden.
- **Fix:** Parametertyp auf `Pick<Zeitpunkt, 'jahr' | 'wert' | 'wertart'>` verengt (aufwärtskompatibel, Datei nicht in `files_modified`).
- **Files modified:** app/src/lib/zeitreihen.ts
- **Committed in:** 0ee8c62

**4. [Rule 2 - Missing Critical] Tooltip mit Betrag auf den Euro genau**
- **Found during:** Task 2
- **Issue:** `ergebnisBeschriftung` liefert gekürzte Beträge („3,56 Mio. €“); der Tooltip soll den genauen Betrag nennen.
- **Fix:** optionaler Parameter `genau` (Standard `false`), eigener Test.
- **Committed in:** 42c7a7e

---

**Total deviations:** 4 auto-fixed (1 bug, 2 missing critical, 1 blocking)
**Impact on plan:** alle additiv, kein Scope Creep, keine neue Abhängigkeit.

## Issues Encountered

- Linux-Sandbox: Die App-Kette lief in einer Scratch-Kopie mit vorhandenem Linux-`node_modules` (kein `npm ci`, Lockfile identisch). Endstand: type-check, lint, format:check, 1120 Tests und `build` grün.
- Es steht kein Browser zur Verfügung; die Optik (Achsenüberlappung, Labelplatz) ist nicht gerendert geprüft, siehe nächster Abschnitt.

## Offene Punkte für den Human-Check (Abschluss-Walkthrough)

Alle betreffen das gerenderte Layout, nicht die Daten:

1. **Zweizeilige Achse bei 360 px (RESEARCH A3).** Bei sechs Jahren bleiben im Hauptdiagramm grob 37 px je Kategorie, die Wörter „Ansatz“ und „Planung“ sind bei 14 px etwa 45 bis 52 px breit. Überlappung ist wahrscheinlich, in den Posten-Karten (schmaler als das Hauptdiagramm) noch eher. Der im Plan genannte Ausweg „Plan“ löst nur „Planung“, nicht „Ansatz“; ernsthaftere Alternativen sind Abkürzungen, gedrehte Beschriftung oder weniger y-Achsen-Breite. Umsetzung bewusst nach Plan (volle Wörter, `interval: 0`), Entscheidung beim Walkthrough.
2. **Direktbeschriftung der Linien** nutzt `endLabel` mit `align: right`; Lage über/unter dem letzten Punkt ist nicht gerendert geprüft.
3. **Platz für die zweizeiligen Säulenbeschriftungen:** `boundaryGap: ['40%', '40%']` an der y-Achse soll Luft über und unter den Säulen schaffen; bei 240 px Höhe prüfen, ob „Defizit 3,56 Mio. €“ nicht in die Achsenbeschriftung ragt.
4. **Raster:** `repeat(auto-fit, minmax(300px, 1fr))` (Plan und UI-SPEC) ergibt bei 1152 px Seitenbreite drei Spalten statt zwei; bei Bedarf auf `minmax(340px, 1fr)` oder zwei feste Spalten ändern.
5. **Linker Rand:** Linien- und Säulendiagramm nutzen dieselben Gridwerte, die y-Achsenbeschriftungen sind verschieden breit; der Rand stimmt daher nur ungefähr überein.

## Known Stubs

Keine. Die Seite „Wie lange reicht das Polster?“ (Rücklagen) gehört laut UI-SPEC ebenfalls zu `/entwicklung`, liegt aber nicht in diesem Plan (06-06).

## Threat Flags

Keine neue Angriffsfläche. Tooltips laufen ausschließlich über `tooltipZeilen` (T-06-12, `quelltext.test.ts` grün, kein Roh-HTML); die Reihen sind durch Identitäts- und Querquellentests gesichert (T-06-13), der gedruckte Endwert (−3.557.700 €) ist gepinnt; keine neue Abhängigkeit (T-06-SC).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Der Rücklagen-Abschnitt kann `jahresAchse`, `Jahreswert` und das Abschnittsmuster in `EntwicklungPage.vue` übernehmen.
- Die Human-Checks oben gehören in den Abschluss-Walkthrough der Phase.

## Self-Check: PASSED
