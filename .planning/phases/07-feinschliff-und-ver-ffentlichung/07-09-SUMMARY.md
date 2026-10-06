---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 09
subsystem: barrierefreiheit-browsertests
tags: [playwright, a11y, wcag, menuegruppe, inventar, 360px, reduced-motion, vitest]

requires:
  - phase: 07-01
    provides: "Playwright-Infrastruktur (ci, mobil, texte), QuelleKnopf, globale Quell-Seitenleiste"
  - phase: 07-05
    provides: "Quelle-Knoepfe an Kacheln der Leitfragen-Seiten"
  - phase: 07-06
    provides: "Quelle an Kacheln und Produktseite"
  - phase: 07-08
    provides: "Quelle-Spalten /rat-entscheidet, /investitionen, /stellenplan"
provides:
  - "e2e/routen.ts: routen() und beispielProdukt(), vollstaendig aus menueLinks(), FUSSZEILEN_ROUTEN und den App-Daten abgeleitet"
  - "e2e/interaktion.spec.ts: Beweis der Menuegruppe (D-19), Fokus und Titel bei jedem Routenwechsel, reduzierte Bewegung fuer Leiste, Menue-Drawer und wa-details"
  - "e2e/inventar.spec.ts: Inventar je ChartCard (Diagramme gegen Tabellen, role-img-Beschreibung), geschlossene Ausnahmeliste mit einem Eintrag"
  - "e2e/mobil.spec.ts: 360-px-Pruefung aller 11 Routen plus Quell-Leiste, Menue-Drawer und Querformatseite"
  - "erweiterte e2e/quelle.spec.ts: deterministischer Erst-Test, Tabellenzeile per Enter, Querformat, Beleg nur mit Seite, Pro-Kopf-Kachel, Fokus beim Oeffnen"
  - "src/lib/__tests__/quelle-ui-abdeckung.test.ts: D-01 global (KennzahlKachel ohne :quelle, Quelle-Spalten ohne Art quelle)"
affects: [07-10, 07-11, 07-12]

actuals:
  tokens: 36000
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Inventar zaehlt je ChartCard Diagramme (.om-base-chart) gegen Tabellen; eine gemeinsame Tabelle zaehlt nur ueber data-om-deckt-diagramme am umgebenden Element und nur mit genug Spalten"
    - "Flackerfreie Drawer-Messung: erst auf das Ende aller endlichen Animationen warten, dann Bild- und Markierungsrechteck in einem page.evaluate lesen und per expect.poll pruefen"
    - "Mobil-Spec sammelt alle Verstoesse einer Route (Selektor, Groesse, Route) und gibt je Zustand eine Tabellenzeile aus"

key-files:
  created:
    - app/e2e/routen.ts
    - app/e2e/interaktion.spec.ts
    - app/e2e/inventar.spec.ts
    - app/e2e/mobil.spec.ts
    - app/src/lib/__tests__/quelle-ui-abdeckung.test.ts
  modified:
    - app/e2e/quelle.spec.ts
    - app/src/components/AufwandsartBalken.vue
    - app/src/components/ErtragsBalken.vue
    - app/src/components/PostenZeitreihe.vue
    - app/src/components/SankeyDiagramm.vue
    - app/src/components/SteuerZeitreihe.vue
    - app/src/components/StellenNachBereich.vue
    - app/src/components/DatenTabelle.vue
    - app/src/styles/basis.css

key-decisions:
  - "Der Seitenleisten-Fokus beim Oeffnen bleibt der Web-Awesome-Standard: gemessen liegt er im benannten Dialog (Shadow-DOM der wa-drawer), der erste Tab-Stopp ist der Schliessen-Knopf; quelle.spec.ts haelt diese Reihenfolge fest, der UI-SPEC-Satz bleibt fuer 07-10 zur Neubewertung"
  - "Eine Karte mit zwei Diagrammen darf eine gemeinsame Tabelle haben, wenn sie das erklaert (data-om-deckt-diagramme=n) und die Tabelle Zeilenkopf plus eine Wertspalte je Diagramm hat; die Ausnahmeliste bleibt bei einem Eintrag (om-entwicklung-polster)"
  - "Footer-Textlinks im Fliesstext (Anzeigeart inline, Absatz mit weiterem Text) sind von der 44-px-Zielmenge ausgenommen (WCAG 2.5.8 Inline-Ausnahme), der Fussnotenlink auf /ueber (eigener Absatz) bleibt geprueft"

patterns-established:
  - "Neue Diagramme brauchen beschreibung (ohne Zahl, Du-Anrede) am BaseChart oder an der ChartCard und eine Tabelle in derselben Karte; sonst scheitert e2e/inventar.spec.ts"
  - "Scroll-Container mit versteckten Texten brauchen position: relative (sonst Seitenueberlauf durch absolut positionierte om-visually-hidden-Spans)"

requirements-completed: [A11Y-01, A11Y-02, A11Y-03, UI-02]

coverage:
  - id: D1
    description: "routen.ts leitet die Routenliste aus menueLinks(), FUSSZEILEN_ROUTEN und dem ersten Produkt mit Grundzahl, Erlaeuterung und Massnahme ab (heute /produkt/010601); keine Route ist getippt"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts, inventar.spec.ts, mobil.spec.ts (alle laufen ueber routen())"
        status: pass
    human_judgment: false
  - id: D2
    description: "Menuegruppe Mehr wissen (D-19): Enter und Leertaste, aria-expanded und aria-controls, Escape mit Fokus auf dem Schalter, Tab ohne Falle und Schliessen beim Verlassen, Klick ausserhalb, Routenwechsel, aria-current, keine Menue-Rollen, Drawer bis 699 px ohne Schalter"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts (8 Tests im Docker-Image playwright:v1.63.0-noble)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Nach dem Klick auf jede Menuroute und den Fusszeilenlink zu /ueber steht der Fokus auf der h1 und document.title endet auf - Ostbevern Money"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts (10 Routen)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Bei emulierter reduzierter Bewegung oeffnen Quell-Leiste, Menue-Drawer (360 px) und ein wa-details mit --show-duration 0 und ohne laufende Animation"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts (3 Tests)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Quell-Leiste: Tabellenzeile auf /ausgaben per Enter, Stellenplan-Zeile mit Querformatseite und Markierung im Bild, Beleg nur mit Seite ohne Markierung, Pro-Kopf-Kachel mit Berechneter Wert; Seitenzahlen aus Knopfnamen und quellen.json, nie getippt"
    requirement: "UI-02"
    verification:
      - kind: e2e
        ref: "app/e2e/quelle.spec.ts (10 Tests; Erst-Test 30 von 30 gruen bei vier Workern)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Inventar: jede ChartCard hat mindestens so viele Tabellen wie Diagramme und jedes role-img-Diagramm eine Beschreibung; Luecken in den Komponenten geschlossen, Ausnahmeliste mit einem Eintrag"
    requirement: "A11Y-01"
    verification:
      - kind: e2e
        ref: "app/e2e/inventar.spec.ts (11 Routen)"
        status: pass
    human_judgment: false
  - id: D7
    description: "D-01 global: keine KennzahlKachel ohne :quelle, keine Spalte Quelle/PDF-Seite mit anderer Art als quelle, in ganz src/"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle-ui-abdeckung.test.ts (7 Tests, mit Positiv- und Negativproben)"
        status: pass
    human_judgment: false
  - id: D8
    description: "360 x 640: kein waagerechtes Seitenscrollen und Ziele von mindestens 44 px auf allen 11 Routen, mit offener Quell-Leiste, offenem Menue-Drawer und Querformatseite im eigenen Rahmen"
    requirement: "A11Y-03"
    verification:
      - kind: e2e
        ref: "app/e2e/mobil.spec.ts (14 Tests, Projekt mobil)"
        status: pass
    human_judgment: false
  - id: D9
    description: "Optik bei 360 px: Quelle-Spalten der Tabellen, Markierung auf Querformatseiten (Stellenplan), Lesbarkeit der geoeffneten Leiste, Menue-Drawer"
    requirement: "A11Y-03"
    verification:
      - kind: e2e
        ref: "app/e2e/mobil.spec.ts (Geometrie bestanden, keine Optikpruefung)"
        status: pass
    human_judgment: true
    rationale: "Die Tests messen Ueberlauf und Zielgroessen, nicht ob Abstaende, Umbrueche und die Sichtbarkeit der Markierung gut aussehen; die Abnahme am Geraet bleibt (human-check des Plans, UAT 07-12)"

duration: 75min
completed: 2026-10-06
status: complete
plan_head_before: 325a1254bfc402a7260d2122a5fe38aa42886e45
plan_head_after: 9312f219437a11338cfb3a54fb83e4c3d85aa778
---

# Phase 7 Plan 09: Browserbeweis der Barrierefreiheit Summary

**Playwright beweist im Chromium die Menügruppe (D-19), den Fokus auf der Überschrift bei jedem Routenwechsel, reduzierte Bewegung bei Web-Awesome-Komponenten, ein Inventar der Tabellenalternativen je Diagramm (mit fünf geschlossenen Beschreibungslücken und einer gemeinsamen Stellenplan-Tabelle) und die Nutzbarkeit aller 11 Routen bei 360 px (mit einem gefundenen und behobenen Seitenüberlauf auf /investitionen).**

## Performance

- **Duration:** 75 min
- **Tasks:** 3 (plus ein Fix-Commit aus der 360-px-Messung)
- **Files modified:** 14 (5 neu)

## Accomplishments

- **Routenliste:** `routen()` besteht aus `menueLinks()`, `FUSSZEILEN_ROUTEN` und `/produkt/{code}`; `beispielProdukt()` wählt das erste Produkt nach Code mit Grundzahl, Erläuterung und Maßnahme (heute 010601).
- **D-19:** Je Zeile der UI-SPEC-Tabelle ein Test, alle grün beim ersten vollständigen Lauf; der 360-px-Fall prüft Überschrift ohne Schalter und vier sichtbare Links. Gruppenname und Untereinträge stammen aus `MENUE`.
- **Routenfokus:** Für alle 10 Nicht-Produkt-Routen (Menü, Gruppenlinks nach dem Öffnen, `/ueber` über den Fußzeilenlink) steht der Fokus nach dem Klick auf der `h1`, der Titel endet auf „– Ostbevern Money“.
- **Reduzierte Bewegung:** Quell-Leiste, Menü-Drawer und ein `wa-details` haben `--show-duration` 0 und keine laufende Animation; die Tokens aus Plan 07-01 genügen, kein weiterer CSS-Eingriff nötig.
- **Quell-Leiste:** Die vier Fälle des Plans plus der Fokus beim Öffnen. Der flackernde Erst-Test ist deterministisch (siehe unten).
- **Inventar (D-16):** Fünf Routen scheiterten zuerst; jede Lücke ist in der Komponente geschlossen (siehe Tabelle).
- **D-01 global:** `quelle-ui-abdeckung.test.ts` scannt alle `.vue`- und `.ts`-Dateien in `src/` (ohne Tests) und hat eigene Positiv- und Negativproben für beide Muster.
- **360 px:** Alle 11 Routen, die Quell-Leiste und der Menü-Drawer bestehen nach zwei Fixes.

### Inventar: gefundene Lücken und Fixes

| Route | Karte | Befund | Fix |
|-------|-------|--------|-----|
| /einnahmen | Ertragsarten, Investive Einnahmen | Diagramm ohne Beschreibung | `ErtragsBalken.vue`: `beschreibung` am BaseChart |
| /einnahmen | Entwicklung (Steuerarten) | Diagramm ohne Beschreibung | `SteuerZeitreihe.vue` |
| /ausgaben | Aufwand nach Aufwandsart | Diagramm ohne Beschreibung | `AufwandsartBalken.vue` |
| /geldfluss | Vom Ertrag zur Ausgabe | Diagramm ohne Beschreibung | `SankeyDiagramm.vue` (nennt, dass Werte und Links in den Tabellen darunter stehen) |
| /entwicklung | fünf Posten-Karten (Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personalaufwand, Zinsen) | Diagramm ohne Beschreibung | `PostenZeitreihe.vue` |
| /entwicklung | Rücklagen, Rückgang der allgemeinen Rücklage | 0 Tabellen in der Karte | durch die einzige Ausnahme `om-entwicklung-polster` gedeckt (gemeinsame, immer sichtbare Tabelle im Abschnitt) |
| /stellenplan | Stellen und Personalaufwand nach Aufgabenbereich | 2 Diagramme, 1 Tabelle | `StellenNachBereich.vue`: die vorhandene Tabelle trägt beide Messgrößen und ist als `data-om-deckt-diagramme="2"` erklärt |

Alle Beschreibungstexte sind ohne Zahl und in Du-Anrede formuliert („Dieselben Werte stehen in der Tabelle darunter.“). Nicht in der Dateiliste des Plans, aber vom Inventar genannt und deshalb angefasst: `StellenNachBereich.vue`.

### 360-px-Ergebnistabelle (für die UAT-Liste 07-12)

Gemessen im Projekt `mobil` (Chromium 360 × 640, Docker-Image `playwright:v1.63.0-noble`), alle `wa-details` geöffnet. „Ziele“ ist die Zahl der geprüften sichtbaren Ziele (Auswahl des Plans, Inline-Textlinks ausgenommen).

| Route / Zustand | scrollWidth | Ziele geprüft | Ergebnis |
|-----------------|-------------|---------------|----------|
| / | 360 | 9 | bestanden |
| /einnahmen | 360 | 44 | bestanden |
| /ausgaben | 360 | 51 | bestanden |
| /geldfluss | 360 | 2 | bestanden |
| /entwicklung | 360 | 2 | bestanden |
| /investitionen | 360 | 64 | bestanden (vor dem Fix 565) |
| /rat-entscheidet | 360 | 23 | bestanden |
| /stellenplan | 360 | 24 | bestanden |
| /glossar | 360 | 2 | bestanden |
| /ueber | 360 | 2 | bestanden |
| /produkt/010601 | 360 | 38 | bestanden |
| / mit Quell-Leiste | 360 | 9 | bestanden (Schließen-Knopf vor dem Fix 43 × 43 px) |
| / mit Menü-Drawer | 360 | 18 | bestanden (Schließen-Knopf vor dem Fix 43 × 43 px) |
| /stellenplan mit Quell-Leiste (Querformat) | 360 | 11 | bestanden; Seite scrollt nur im eigenen Rahmen (`.om-quelle-seite` breiter als sichtbar) |

## Task Commits

1. **Task 1: Routenliste, Menügruppe, Routenfokus, reduzierte Bewegung, Leistenfälle** - `2c4ad80` (test)
2. **Task 2: Inventar, Beschreibungen, D-01 global** - `09a6ba5` (feat)
3. **Task 3 (Fix aus der Messung): Tabellenrahmen und Schließen-Knopf** - `bb6a258` (fix)
4. **Task 3: 360-px-Spec** - `9312f21` (test)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md)

## Verification

Im Worktree nach frischem `npm ci` (Linux-`node_modules`), statt der mktemp-Kopie des Plans (Wurzeldateisystem knapp, wie in 07-06/07-08):

- `type-check`, `lint`, `format:check` grün; `npm run test`: 43 Dateien, 1922 Tests grün (darunter 7 neue).
- `build-only` grün.
- Playwright im Docker-Image, Projekt `ci`: 43 von 43 grün, dreimal hintereinander wiederholt (keine Flakes).
- Playwright, Projekt `mobil`: 14 von 14 grün.
- Erst-Test der Quell-Leiste: 30 von 30 grün bei `--repeat-each=30 --workers=4`; auf dem Ausgangsstand reproduzierte sich der Fehler im allerersten Lauf dieser Sitzung.
- Akzeptanzkriterien aller drei Aufgaben per `grep` geprüft (erfüllt).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Seitenüberlauf auf /investitionen bei 360 px**
- **Found during:** Task 3 (erster mobil-Lauf: scrollWidth 565 > 360)
- **Issue:** Die absolut positionierten `.om-visually-hidden`-Spans in den Zellen der Maßnahmentabelle hatten den Tabellenrahmen (`overflow-x: auto`, aber `position: static`) nicht als Bezugsrahmen und ragten bis 565 px hinaus. Die Tabelle selbst war korrekt eingerahmt, ein erster Diagnoselauf fand deshalb keinen ungeclippten Verursacher; erst die Auswertung nach `position` zeigte die Spans.
- **Fix:** `.om-tabelle-rahmen { position: relative }`.
- **Files modified:** `app/src/components/DatenTabelle.vue`
- **Verification:** mobil-Spec /investitionen scrollWidth 360, Gesamtsuite grün
- **Commit:** `bb6a258`

**2. [Rule 1 - Bug] Schließen-Knopf der Drawer 43 × 43 px**
- **Found during:** Task 3 (Quell-Leiste und Menü-Drawer offen)
- **Fix:** `wa-drawer::part(close-button__base)` mit `min-width`/`min-height` 44 px.
- **Files modified:** `app/src/styles/basis.css`
- **Commit:** `bb6a258`

**3. [Rule 1 - Bug] Flackernder Erst-Test von quelle.spec.ts (Übergabe der Orchestrierung)**
- **Found during:** Task 1 (im ersten Lauf reproduziert)
- **Issue:** Markierungs- und Bildrechteck wurden in zwei Aufrufen zu verschiedenen Zeitpunkten der Einfahranimation gemessen.
- **Fix:** `warteAufRuhe` (Bild geladen, alle endlichen Animationen beendet), ein einziger `page.evaluate` für beide Rechtecke, Prüfung per `expect.poll`.
- **Files modified:** `app/e2e/quelle.spec.ts`
- **Commit:** `2c4ad80`

### Weitere Hinweise

- **[Rule 3] Inventar, Sonderfall zwei Diagramme, eine Tabelle:** Der Plan verlangt gleichzeitig „Tabellen ≥ Diagramme je Karte“ und lässt „eine Tabelle mit allen Werten beider Diagramme“ zu (UI-SPEC). Das Inventar erkennt die gemeinsame Tabelle nur, wenn das umgebende Element `data-om-deckt-diagramme="n"` trägt und die Tabelle Kopfzellen für Zeilenbezeichnung plus n Wertspalten hat. Das ist keine Erweiterung der Ausnahmeliste (sie hat weiter einen Eintrag), sondern eine geprüfte, im Quelltext der Komponente stehende Erklärung. Alternative wäre gewesen, die Stellenplan-Tabelle in zwei zu teilen und das Layout zu ändern.
- **Ausnahmeabschnitt:** Die Ausnahme `om-entwicklung-polster` greift nur, solange der Abschnitt eine Tabelle außerhalb eines `wa-details` enthält. Der Abschnitt hat kein `id`, sondern `aria-labelledby`; das Inventar liest deshalb dieses Attribut.
- **Verify-Befehle:** wie in den Vorgängerplänen direkt im Worktree statt in einer `mktemp`-Kopie (Platz); Container mit eindeutigem Namen und `--rm`.
- **Fokus beim Öffnen (Übergabe der Orchestrierung):** Browser-Messung: Der Fokus liegt im Shadow-DOM der `wa-drawer` (benannter Dialog), der erste Tab-Stopp ist der Schließen-Knopf; er verlässt die Leiste nicht. `quelle.spec.ts` hält das fest. Die Entscheidung, ob der Schließen-Knopf wie in der UI-SPEC direkt fokussiert werden soll, bleibt bei 07-10.
- **Footer-Links:** Im 360-px-Test fallen die Textlinks der Fußzeile im Fließtext unter die Inline-Ausnahme (Kommentar im Test). Unter 44 px blieben damit der PDF-, Kontakt- und Münster-Link; geprüft und bestanden sind der Link zu `/ueber` und alle Schaltflächen.

**Total deviations:** 3 auto-fixed (3 Bugs), 1 Sonderfall im Inventar. **Impact:** Zwei CSS-Dateien und sechs Komponenten außerhalb der reinen Testdateien geändert; keine Änderung an Daten, Schlüsseln oder Verhalten.

## Deferred Issues

- Optische Abnahme der neuen Quelle-Spalten bei 360 px und der Markierung auf den Querformat-Seiten (Stellenplan) bleibt `human_judgment` (D9): Geometrie ist bewiesen, Optik nicht. Einzutragen in die UAT-Liste 07-12 mit dem `human-check` des Plans (Stellenplan öffnen, Quelle-Knopf einer Tabellenzeile, Leiste vollbreit, Seite scrollt nur im Rahmen).
- Die Fußzeilen-Textlinks im Fließtext liegen unter 44 px Höhe (WCAG 2.5.8-Inline-Ausnahme angewandt, nicht behoben).

## Known Stubs

None.

## Threat Flags

None - nur Tests und Barrierefreiheitsfixes; keine neue Netz-, Auth- oder Dateizugriffsfläche. T-07-20 mitigiert: Ausnahmeliste mit einem begründeten Eintrag, Lücken in den Komponenten geschlossen, Tests laufen im Projekt `ci`.

## Next Phase Readiness

- 07-10 kann den Fokus beim Öffnen anhand der Messung entscheiden (Test hält den Ist-Zustand fest).
- 07-11 (Smoke-Test mit axe) kann `routen()` wiederverwenden; die Beschreibungen der Diagramme sind jetzt vollständig.
- 07-12: Ergebnistabelle oben für die UAT-Liste übernehmen.

## Self-Check: PASSED

- Dateien vorhanden: routen.ts, interaktion.spec.ts, inventar.spec.ts, mobil.spec.ts, quelle.spec.ts, quelle-ui-abdeckung.test.ts.
- Commits vorhanden: 2c4ad80, 09a6ba5, bb6a258, 9312f21 (alle im Zweig).
- Akzeptanzkriterien aller drei Aufgaben erneut geprüft (erfüllt); Plan-Verifikation (ci und mobil im Docker-Image) grün.

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
