---
phase: 05-leitfragen-seiten
plan: 09
subsystem: app-einnahmen
tags: [einnahmen, echarts, balken, zeitreihe, vorbericht, finanzplan, wa-details, tdd]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-02: vorbericht.sonstige_ertraege/investitionszuwendungen, meta.vorbericht_werte.konzessionsabgabe_*, zeilen_namen; 05-03: Erklaertexte; 05-04: useJahr, JahrUmschalter; 05-05: BaseChart, DatenTabelle, ERTRAG_FARBE/INVEST_FARBE, tooltipZeilen; 05-06: baueErtragsarten, ErklaerText, BerechnetEtikett"
provides:
  - "charts/balken.ts: horizontaleBalkenOption, balkenHoehe, balkenBeschriftung, balkenTooltip (Direktbeschriftung, maskierter Tooltip, 40-px-Zeilen)"
  - "lib/einnahmen.ts: baueSteuern, baueZuwendungen, baueSonstigeErtraege, baueInvestiveEinnahmen, baueInvestiveTabelle, hatInvestiveWerte, quellenText und die fachlichen Konstanten"
  - "lib/zeitreihen.ts: ZEITREIHEN_POSTEN (einzige Posten-Grundzahl-Zuordnung), baueZeitreihe, zeitreihenSerien, quellenFussnote, betragText"
  - "ErtragsBalken.vue, SteuerZeitreihe.vue und die vollstaendige EinnahmenPage (EINN-01 bis EINN-06)"
affects: [05-leitfragen-seiten, einnahmen-seite, phase-07-smoke-test]

actuals:
  tokens: 22000
  tasks: 3
  commits: 8

tech-stack:
  added: []
  patterns:
    - "Builder in lib/ lesen nur und liefern null fuer fehlende Werte; Anzeige (rd., berechnet, kein Geldfluss) erst in der Seite"
    - "DatenTabelle-Zeilen tragen Kennzeichen als 0/1, weil DatenZeile nur Text, Zahl und null kennt; der zelle-Slot liest sie"
    - "wa-details wird per getElementById/open geoeffnet, nicht ueber gebundenen Zustand (Tooltip-Events bubblen sonst in den Zustand)"

key-files:
  created:
    - app/src/charts/balken.ts
    - app/src/charts/__tests__/balken.test.ts
    - app/src/components/ErtragsBalken.vue
    - app/src/components/SteuerZeitreihe.vue
    - app/src/lib/einnahmen.ts
    - app/src/lib/__tests__/einnahmen.test.ts
    - app/src/lib/zeitreihen.ts
    - app/src/lib/__tests__/zeitreihen.test.ts
  modified:
    - app/src/pages/EinnahmenPage.vue

key-decisions:
  - "SONDERPOSTEN_POSTEN umfasst zusaetzlich aufloesung_sonstiger_sonderposten (Vorbericht 2.1.7): derselbe Ertrag ohne Geldzufluss, sonst stuende dort eine Aufloesung ohne Etikett"
  - "Hebesaetze erscheinen immer mit dem Haushaltsjahr beschriftet, auch bei anderem gewaehltem Jahr (Annahme EINN-02 aus dem Plan bestaetigt)"
  - "Zeitreihe haengt nicht am Jahr-Umschalter; die Steuerart ist Seitenzustand (v-model), der Seitentitel und die PDF-Seite der ChartCard folgen ihr"
  - "Ein berechneter Rest ohne Wert (Zuwendungen/Sonstige in Jahren ohne Differenz) wird als Zeile weggelassen statt als '–' gezeigt"
  - "Bis 699 px: Namensbereich der Balken 140 px statt 160 px und zweizeilige Beschriftung, damit auf 360 px noch Balken bleiben (Abweichung von UI-SPEC E3 long-text, siehe Deviations)"

requirements-completed: [EINN-01, EINN-02, EINN-03, EINN-04, EINN-05, EINN-06]

coverage:
  - id: D1
    description: "/einnahmen zeigt die Ertragsarten des gewaehlten Jahres als Balken mit Betrag, Anteil und Wertart sowie als Tabelle; Leerzustand benennt das Jahr"
    requirement: EINN-01
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/balken.test.ts (17 Tests: Reihenfolge, 160-px-Umbruch, null -> '–', maskierter Tooltip, Hoehe 328px/48px)"
        status: pass
      - kind: other
        ref: "SSR-Rendering der Seite fuer 2024/2026/2029 im Scratch-Copy (nicht eingecheckt): Tabellen und Balkenoptionen ohne undefined/NaN"
        status: pass
    human_judgment: true
    rationale: "Optische Qualitaet der Balken und der Beschriftung (vor allem 360 px) ist ohne Browser nicht pruefbar"
  - id: D2
    description: "Aufschluesselung Steuern/Zuwendungen/Sonstige mit Hebesaetzen, Markierung selbst festgelegter Steuern, kein-Geldfluss-Etikett, Konzessionsabgaben nach Sparte"
    requirement: EINN-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/einnahmen.test.ts (136 Tests ueber alle Jahre: Summen gegen Gesamtergebnisplan, Konstanten in den Tabellen, Sonderposten, Konzessionsabgaben, kein undefined)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Zeitreihe je Steuerart und Schluesselzuweisung: Grundzahlen vor dem ersten Planjahr, Vorbericht ab dem ersten Planjahr, Ist/Ansatz/Planung als drei Serien mit geteiltem Uebergangspunkt"
    requirement: EINN-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/zeitreihen.test.ts (Zuordnung eindeutig, D-01: kein Grundzahl-Wert fuer Planjahre, Gewerbesteuer 2023 = 4.771.497 und 2024 = 9.511.000)"
        status: pass
    human_judgment: true
    rationale: "Unterscheidbarkeit der drei Linienstile ohne Farbe und Lesbarkeit der Jahresbeschriftung bei 360 px sind Sichtpruefung (UI-SPEC E5 populated: backstop)"
  - id: D4
    description: "Investive Einnahmen getrennt durch wa-divider, Callout und eigene ChartCard in INVEST_FARBE; Pauschalen plus 'Sonstige (berechnet)' = GFP Z. 18 in jedem Jahr"
    requirement: EINN-06
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/einnahmen.test.ts#investive Einnahmen (je Jahr: Summe = GFP Z. 18, Reihenfolge, Jahre ohne Aufschluesselung, 2026: Sonstige 1.751.000 = Summe der uebrigen Posten von S. 52)"
        status: pass
    human_judgment: true
    rationale: "Renderfehler-Text des Diagramms (UI-SPEC E6 error) ist ein Backstop fuer den Smoke-Test in Phase 7"

duration: ca. 35 min (Startzeit nicht exakt erfasst)
completed: 2026-10-04
status: complete
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: 12d43a15b89f42dbcf8233af82934db1c980b49b
commits: 8
---

# Phase 5 Plan 09: Woher kommt das Geld? Summary

**Die Seite `/einnahmen` zeigt Ertragsarten als Balken (Betrag, Anteil, Wertart), die Aufschluesselung von Steuern, Zuwendungen und Sonstigen Ertraegen mit Hebesaetzen und "kein Geldfluss"-Etikett, eine Zeitreihe je Steuerart mit Quellenwechsel Grundzahlen/Vorbericht und die investiven Einnahmen aus dem Finanzplan klar getrennt von den Ertraegen.**

## Performance

- **Duration:** ca. 35 min (Startzeit nicht exakt erfasst)
- **Completed:** 2026-10-04
- **Tasks:** 3 (1 Tracer, 2 TDD)
- **Files:** 9 (8 neu, 1 geaendert)
- **Tests:** vitest gesamt 381 passed (14 Dateien); davon neu 17 (balken), 136 (einnahmen), 90 (zeitreihen)

## Accomplishments

- **Tracer (Task 1):** `horizontaleBalkenOption` (Kategorienachse invertiert, Wertachse ab 0, Direktbeschriftung am Balkenende, Tooltip ueber `tooltipZeilen`), `balkenHoehe(n) = n * 40 + 48 px`, `ErtragsBalken.vue` mit getipptem Klick-Event, `/einnahmen` mit ChartCard "Ertragsarten {jahr}" und Tabelle im Aufklapper. Tracer-Verify (vitest, type-check, lint, format:check, build) vor der Expansion erneut gruen.
- **Ebene 2 (Task 2):** `lib/einnahmen.ts` mit den fachlichen Regeln als benannten Konstanten (`SELBST_FESTGELEGTE_STEUERN`, `SONDERPOSTEN_POSTEN`, `GEZEIGTE_PAUSCHALEN`). Drei `wa-details` (Steuern offen), nur fuer Ertragsarten mit Werten. Zuwendungen mit berechnetem Rest "Sonstige" (2026: 5.200 €), Sonderposten mit "kein Geldfluss", 2.1.7 mit den Konzessionsabgaben und, nur im Haushaltsjahr, Strom/Gas/Wasser (315 + 40 + 115 T€ = 470 T€). Klick auf einen Balken oeffnet die passende Aufschluesselung.
- **Investive Einnahmen (Task 2):** `baueInvestiveEinnahmen` liest nur `finanzplan` und `vorbericht.investitionszuwendungen`; "Sonstige (berechnet)" = GFP Z. 18 minus gezeigte Pauschalen (2026: 1.751.000 € = Feuerschutzpauschale plus Foerderungen). In Jahren ohne gedruckte Aufschluesselung sind alle Pauschalen `null` und die Sonstige traegt die ganze Zeile 18. Eigene ChartCard in `INVEST_FARBE` hinter `wa-divider` und Callout.
- **Zeitreihe (Task 3):** `ZEITREIHEN_POSTEN` als einzige Zuordnungstabelle (Praefix mit oeffnender Klammer, sonst traefe "Gewerbesteuer" auch "Gewerbesteuerumlage"). Jahre vor dem ersten Planjahr aus den Grundzahlen (Ist), alle Planjahre aus dem Vorbericht (2024 Gewerbesteuer 9.511.000 € statt 8.418.043 €). `zeitreihenSerien` liefert Ist/Ansatz/Planung mit geteiltem Uebergangspunkt; `SteuerZeitreihe.vue` zeichnet sie durchgezogen/gestrichelt/gepunktet mit gefuelltem Kreis, hohlem Kreis, hohler Raute, `connectNulls: false`, y ab 0, alle Jahre als Achsenbeschriftung, Textlegende, Tabelle mit Wertart und Quelle und Erklaertext fuer Gewerbesteuer/Schluesselzuweisung.

## Task Commits

1. **Task 1: Tracer Ertragsarten-Balken** - `872c98a` (feat)
2. **Task 2: Aufschluesselung und investive Einnahmen (TDD)**
   - RED `6a00126` (test) - 79 von 123 Tests scheitern an Assertions (Stub mit leeren Rueckgaben)
   - GREEN `491460e` (feat) - lib/einnahmen.ts, alle 133 Tests des RED-Stands gruen
   - Seite `6028a66` (feat) - Aufklapper, Tabellen, investive Karte, `quellenText`
3. **Task 3: Zeitreihe (TDD)**
   - RED `ab01c9d` (test) - 23 Tests scheitern an Assertions
   - GREEN `7682cdc` (feat) - lib/zeitreihen.ts
   - Komponente und Seite `12d43a1` (feat)
4. **Nacharbeit schmale Balken** - `d5f8f5c` (fix)

**Plan metadata:** wird mit diesem SUMMARY committet (docs).

## TDD Gate Compliance

- Task 2: `test(05-09)` `6a00126` vor `feat(05-09)` `491460e`. RED: Signatur-Stub, daher scheiterten die Tests an Assertions des geplanten Verhaltens (Mengen, Summen, Etiketten), nicht an fehlenden Modulen. `gsd_run check tdd-red-evidence` wurde nicht erzeugt (Werkzeug im Worktree nicht verwendet); die Fehlschlaege wurden an der vitest-Ausgabe geprueft.
- Task 3: `test(05-09)` `ab01c9d` vor `feat(05-09)` `7682cdc`, gleiches Vorgehen. Die beiden `betragText`-Tests kamen mit der Implementierung hinzu (Hilfsfunktion, die erst beim Bau der Komponente noetig wurde); ein erster Lauf scheiterte am geschuetzten Leerzeichen vor "€" und wurde auf `euro()` als Erwartung umgestellt.
- Task 2: `quellenText` und seine drei Tests liegen im Seiten-Commit `6028a66`, nicht im RED-Commit (Hilfsfunktion, erst beim Seitenbau noetig).
- Kein REFACTOR-Commit noetig.

## Deviations from Plan

### Auto-fixed / Plan-Abweichungen

**1. [Rule 1/UI - Lesbarkeit] Schmale Balken bis 699 px**
- **Found during:** Task 3 (SVG-Rendering der Option im Scratch-Copy mit 280 px Kartenbreite)
- **Issue:** Mit Namensbereich 160 px und einzeiliger Beschriftung ("18,4 Mio. € · 67,1 %") bleibt auf 360 px (Karteninhalt ca. 280 px) kein Platz fuer Balken.
- **Fix:** Bis 699 px (`useSchmalerBildschirm`) Namensbereich 140 px und Beschriftung in zwei Zeilen ("18,4 Mio. €" / "67,1 %"); rechter Rand wird aus der laengsten Zeile berechnet. Ab 700 px unveraendert 160 px (UI-SPEC E3 long-text).
- **Files modified:** app/src/charts/balken.ts, balken.test.ts, ErtragsBalken.vue
- **Commit:** d5f8f5c (und 872c98a)
- **Offen:** Die Balken bleiben auf 360 px kurz (ca. 30-40 px). Das ist ohne Browser nicht abschliessend beurteilbar; siehe Human-Check.

**2. [Rule 2 - Konsistenz] Sonderposten-Etikett auch in 2.1.7**
- **Found during:** Task 2
- **Issue:** `aufloesung_sonstiger_sonderposten` (Vorbericht 2.1.7) ist wie `aufloesung_sonderposten` ein Ertrag ohne Geldzufluss; ohne Etikett stuende er unmarkiert neben echten Einnahmen.
- **Fix:** `SONDERPOSTEN_POSTEN` nennt beide Schluessel; der Erklaertext `sonderposten` steht auch im Aufklapper der Sonstigen Ertraege.
- **Files modified:** app/src/lib/einnahmen.ts, app/src/pages/EinnahmenPage.vue
- **Commit:** 491460e, 6028a66

**3. [Plan-Interpretation] Leerzustand der Zeitreihe**
- **Issue:** UI-SPEC E5 nennt "Für {jahr} gibt es keine Einzelwerte"; die Zeitreihe hat kein einzelnes Jahr.
- **Fix:** Titel "Für diese Auswahl gibt es keine Einzelwerte" mit eigenem Text zur Steuerart.
- **Commit:** 12d43a1

**4. [Plan-Interpretation] Zusaetzliche Exporte und ein Berechnungsdetail**
- Zusaetzlich zu den im Plan genannten Exporten: `AUFSCHLUESSELUNG_FUER_ERTRAGSART`, `baueInvestiveTabelle`, `hatInvestiveWerte`, `quellenText` (einnahmen); `ZEITREIHEN_PRODUKT`, `STANDARD_ZEITREIHE`, `findeGrundzahl`, `zeitreihenOptionen`, `zeitreihenSeite`, `quellenFussnote`, `betragText` (zeitreihen); `balkenBeschriftung`, `balkenTooltip` (balken). Alle in den genannten Dateien, keine neue Datei ausserhalb von `files_modified`.
- Ein berechneter Rest ohne Wert wird als Zeile weggelassen (siehe key-decisions).
- Die Zeitreihen-Optionen entstehen in `SteuerZeitreihe.vue` (nicht in `charts/`), weil die Akzeptanzpruefungen `connectNulls: false` und den Legendentext in der Komponente verlangen.

**5. [Hinweis] `containLabel` ersetzt**
- ECharts 6 markiert `grid.containLabel` als veraltet; die Optionen nutzen die dokumentierte Entsprechung `outerBoundsMode: 'same'`, `outerBoundsContain: 'axisLabel'`.

**Total deviations:** 5 (1 Lesbarkeit, 1 Konsistenz, 3 Interpretation/Hinweis). **Impact:** kein Scope-Creep ausserhalb der Plan-Dateien; Shared-Files (`main.ts`, `router/index.ts`, `echartsTheme.ts`) wurden nicht angefasst, es kamen keine neuen Web-Awesome-Imports hinzu (details, tag, divider, callout, icon, select, option sind bereits in `main.ts`).

## Authentication Gates

None.

## Issues Encountered

- Die Sandbox lehnte zusammengesetzte Shell-Befehle mit git bzw. Heredocs ab; Befehle wurden einzeln ausgefuehrt, Dateien ueber Write/Edit erstellt.
- Kein Browser vorhanden: Layout und Linienstile wurden ueber ECharts-SVG-Rendering im Node-Scratch-Copy (nicht eingecheckt) auf Fehler und Warnungen geprueft; es gab keine. Die Pixelqualitaet bleibt Sichtpruefung.
- Die Hebesatz-Begriffsverknuepfung `GlossarBegriff` aus UI-SPEC (Steuern-Aufklapper) fehlt, weil die Komponente in Plan 05-13 entsteht und im Worktree nicht vorhanden ist; der Plan verlangt sie nicht.

## Known Stubs

None. (Kein hartkodierter Leerwert fliesst in die Oberflaeche; `hoehe="320px"` und Leertexte sind Oberflaechentexte.)

## Threat Flags

None. T-05-23 (Plan-Mischung) durch getrennten Builder, ChartCard, Divider und Callout mitigiert; T-05-24 (Quellenmix) durch den D-01-Test und die einzige Zuordnungstabelle; T-05-25 (Tooltip-XSS) durch `tooltipZeilen` in beiden Tooltip-Formattern und einen Test mit `<b>`-Zeilennamen.

## Verification

- Scratch-Copy (`npm ci` aus dem Lockfile): `npm run test` 381 passed, `type-check`, `lint`, `format:check`, `build` gruen.
- Acceptance: alle `grep`-Kriterien der drei Tasks erfuellt (`baueErtragsarten`/`Tabelle anzeigen`, `horizontaleBalkenOption`, 0 Treffer fuer "x,y Mio" in der Seite, "Woraus sich die Erträge zusammensetzen", "Investive Einnahmen", "kein Geldfluss", Callout-Text, `INVEST_FARBE`, `connectNulls: false`, Legendentext, `baueZeitreihe`, 0 Jahreszahlen in `SteuerZeitreihe.vue`).
- Plan-Human-Check (Dev-Server bei 1280 und 360 px, Jahrwechsel 2024/2026/2029, Linienstile, Tooltip, Jahresbeschriftung) wurde **nicht** ausgefuehrt (Linux-Sandbox ohne Browser); er bleibt fuer die Abnahme am Phasenende. Besonders zu pruefen: Balkenbreite und Beschriftung der Ertragsarten und der investiven Einnahmen auf 360 px.

## Next Phase Readiness

- `ErtragsBalken`/`horizontaleBalkenOption` sind fuer weitere horizontale Balken (z. B. Zuschussbalken) wiederverwendbar.
- Phase 7 Smoke-Test: Fehlertext bei Renderfehler fuer die drei Diagramme der Seite (UI-SPEC E5/E6 backstop).

## Self-Check: PASSED

- Gefunden: balken.ts, balken.test.ts, ErtragsBalken.vue, SteuerZeitreihe.vue, einnahmen.ts, einnahmen.test.ts, zeitreihen.ts, zeitreihen.test.ts, EinnahmenPage.vue.
- Commits 872c98a, 6a00126, 491460e, 6028a66, ab01c9d, 7682cdc, d5f8f5c, 12d43a1 vorhanden.
