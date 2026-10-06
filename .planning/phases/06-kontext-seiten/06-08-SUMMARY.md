---
phase: 06-kontext-seiten
plan: 08
subsystem: ui
tags: [vue, echarts, vitest, ruecklagen, haushaltssicherung, entwicklung]

requires:
  - phase: 06-kontext-seiten
    provides: "meta.vorbericht_werte.hsk_schwelle_* (06-01), Pipeline-Text polster und Glossarbegriff haushaltssicherung (06-04), EntwicklungPage mit ENTW-01/02 (06-05), Chart-Fundament wertartStil/echartsTheme (06-02)"
provides:
  - "lib/ruecklagen.ts: baueRuecklagen, abbau, rueckgang, rueckgangPlanjahre, rueckgangAchsenMaximum, ruecklagenTabelle, hskSchwellen, ausgleichsruecklageAufgebrauchtJahr"
  - "RuecklagenBalken.vue: gestapelte Saeulen Ausgleichsruecklage/allgemeine Ruecklage, Bestand zu Jahresbeginn"
  - "RueckgangBalken.vue: Rueckgang in Prozent mit gestrichelter Schwellenlinie"
  - "Abschnitt 'Wie lange reicht das Polster?' auf /entwicklung (ENTW-03)"
affects: [06-12, verify-work, phase-06-verification]

actuals:
  tokens: 9500
  tasks: 2
  commits: 4

plan_head_before: 14ef1e238657bf4cf1989b34397f37fbc86ace94
plan_head_after: b8f97eea91d5c9ea5e100e57bed08829471ab734

tech-stack:
  added: []
  patterns:
    - "Lib-Funktionen mit optionalem Tabellenparameter (Default haushalt.eigenkapital/meta) fuer Randfalltests ohne Mocking"
    - "Unsichtbare Linienserie auf der Saeulenspitze als Summenbeschriftung ueber gestapelten Saeulen"
    - "markLine-Schwelle ohne Literal: Wert aus meta.vorbericht_werte, Achsenmaximum = max(Werte, Schwelle) x 1,2"

key-files:
  created:
    - app/src/lib/ruecklagen.ts
    - app/src/lib/__tests__/ruecklagen.test.ts
    - app/src/components/RuecklagenBalken.vue
    - app/src/components/RueckgangBalken.vue
  modified:
    - app/src/pages/EntwicklungPage.vue

key-decisions:
  - "Rueckgang gehoert zu dem Jahr der eigenen Spalte (abbau(t)/AR(t), Bezug Bestand zu Jahresbeginn), nie als Spaltendifferenz 'gegenueber Vorjahr' (Pitfall 1)"
  - "Tabellenspalte heisst 'Rueckgang im Jahr (berechnet)'; beide Bestandsspalten tragen den Zusatz 'Bestand zu Jahresbeginn'"
  - "Der Claim 'jeweils unter 5 %' aus der UI-SPEC erscheint nirgends; 2029 liegt mit 10,04 % ueber der Schwelle fuer zwei Jahre"
  - "Optionale Tabellenparameter statt Datenmocks: rueckgang/abbau/baueRuecklagen etc. nehmen die Tabelle als letzten Parameter"

patterns-established:
  - "Null bleibt null: fehlende Eigenkapitalwerte ergeben null (Anzeige '-'), nie 0; eine echte 0 bleibt 0 ('0 EUR') und zeichnet kein Segment"

requirements-completed: [ENTW-03]

coverage:
  - id: D1
    description: "Rucklagen 2024-2029 als gestapelte Saeulen (Ausgleichsruecklage unten, allgemeine Ruecklage oben) mit Summe und Unterschrift 'Bestand zu Jahresbeginn' aus eigenkapital.posten (S. 311)"
    requirement: ENTW-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts#baueRuecklagen (ENTW-03, S. 311)"
        status: pass
    human_judgment: true
    rationale: "Optik und Lesbarkeit der gestapelten Saeulen (hohle Planungssaeulen, Summenlabels, 360 px) sind nur im Browser beurteilbar; in diesem Lauf stand kein Browser zur Verfuegung."
  - id: D2
    description: "Rueckgang der allgemeinen Ruecklage je Planjahr reproduziert S. 23 auf zwei Nachkommastellen (1,77 / 4,23 / 4,73 / 10,04 %) und ist per Gefaelle AR(t)-AR(t+1) gegengeprueft"
    requirement: ENTW-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts#gedruckte Werte der S. 23 reproduziert 1,77 / 4,23 / 4,73 / 10,04 % auf zwei Nachkommastellen"
        status: pass
    human_judgment: false
  - id: D3
    description: "Rueckgang-Diagramm mit gestrichelter markLine bei hsk_schwelle_zwei_jahre, y max x 1,2, Schwellen in Text laut Vorbericht"
    requirement: ENTW-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts#hskSchwellen und rueckgangAchsenMaximum"
        status: pass
    human_judgment: true
    rationale: "Lage und Umbruch der Schwellenbeschriftung bei 360 px und 1280 px sind nur visuell pruefbar (Human-Check der Aufgabe 2 steht aus)."
  - id: D4
    description: "Immer sichtbare Tabelle mit 'Rueckgang im Jahr (berechnet)' und neutraler Callout mit dem Pipeline-Text polster und GlossarBegriff haushaltssicherung ohne jahr-Prop"
    requirement: ENTW-03
    verification:
      - kind: other
        ref: "grep schluessel=\"polster\" / schluessel=\"haushaltssicherung\" / 'Rueckgang im Jahr (berechnet)' in EntwicklungPage.vue"
        status: pass
    human_judgment: true
    rationale: "Textpruefung (keine rechtliche Bewertung, keine Aussage jenseits des letzten Planjahrs) ist ein Backstop-Urteil am Abnahme-Checkpoint."
  - id: D5
    description: "ausgleichsruecklageAufgebrauchtJahr() entspricht der Pipeline-Regel (texte.werte['abgeleitet.ausgleichsruecklage_aufgebraucht_jahr'])"
    requirement: ENTW-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts#ausgleichsruecklageAufgebrauchtJahr stimmt mit der Pipeline-Regel (texte.werte) ueberein"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 08: Rucklagen und "Wie lange reicht das Polster?" Summary

**/entwicklung zeigt die Ruecklagen als gestapelte Saeulen "Bestand zu Jahresbeginn" (S. 311), den jaehrlichen Rueckgang der allgemeinen Ruecklage in Prozent (S.-23-Werte auf zwei Nachkommastellen reproduziert) mit der HSK-Schwellenlinie aus den Daten, eine immer sichtbare Tabelle und den neutralen Polster-Text.**

## Performance

- **Duration:** ca. 30 min
- **Started:** 2026-10-06T08:30:00Z (ca.)
- **Completed:** 2026-10-06T08:45:00Z (ca.)
- **Tasks:** 2 (Tracer + TDD)
- **Files modified:** 5 (4 neu, 1 geaendert)

## Accomplishments

- `lib/ruecklagen.ts` rechnet den Abbau der allgemeinen Ruecklage nach der S.-23-Regel (`max(0, -JE - Ausgleich) - Verrechnung`) und teilt durch den Bestand zu Jahresbeginn; die vier Planjahre ergeben 1,77 / 4,23 / 4,73 / 10,04 %, ein Test prueft ausserdem die Identitaet `abbau(t) = AR(t) - AR(t+1)` und die S.-311-Summenidentitaet in allen sechs Spalten.
- `RuecklagenBalken.vue` (Tracer): Ausgleichsruecklage unten, allgemeine Ruecklage oben, Summe ueber jeder Saeule, Planung hohl ueber `saeulenStil`, Unterschrift "Bestand zu Jahresbeginn", Leerzustand, "0 EUR" zeichnet kein Segment.
- `RueckgangBalken.vue`: Saeulen der Planjahre mit `prozent()`-Beschriftung, gestrichelte `markLine` bei `hskSchwellen().zweiJahre` (Label bricht um, liegt auf der Kartenflaeche), y-Achse bis `max x 1,2`; entfaellt bei weniger als zwei Planjahren.
- `EntwicklungPage.vue`: Abschnitt mit Rueckgang-Karte (Etikett "berechnet"), Schwellenzeile "Laut Vorbericht (PDF-Seite ...)" aus den Daten, Tabelle immer sichtbar, neutraler Callout mit `ErklaerText polster` (ohne `jahr`-Prop) und `GlossarBegriff haushaltssicherung`; Leerzustand blendet Tabelle und Callout aus.

## Task Commits

1. **Task 1: Tracer Ruecklagen S. 311 -> lib -> gestapelte Saeulen -> /entwicklung** - `da3ba3c` (feat)
2. **Task 2: Rueckgang mit HSK-Schwelle, Tabelle, Polster-Text (TDD)**
   - RED: `5bf8663` (test) - 10 neue Tests schlagen fehl, weil `rueckgangPlanjahre`, `rueckgangAchsenMaximum`, `ruecklagenTabelle` fehlen (TypeError "is not a function"), die 21 bisherigen Tests bleiben gruen
   - GREEN: `2763c2e` (feat) - Lib-Funktionen, 31/31 Tests gruen
   - UI: `b8f97ee` (feat) - RueckgangBalken.vue und Seitenabschnitt

**Plan metadata:** wird mit diesem SUMMARY committet (docs).

## Files Created/Modified

- `app/src/lib/ruecklagen.ts` - Ruecklagen je Jahr, Abbau/Rueckgang nach S. 23, Schwellen, Jahr der aufgebrauchten Ausgleichsruecklage, Planjahre, Achsenmaximum, Tabellenzeilen
- `app/src/lib/__tests__/ruecklagen.test.ts` - 31 Tests: S.-311-Arithmetik, S.-23-Werte, Randfaelle (null, 0, fehlender Posten/Schluessel), Gleichheit mit der Pipeline-Regel
- `app/src/components/RuecklagenBalken.vue` - gestapelte Saeulen mit Summe, Legende, Tooltip, Unterschrift
- `app/src/components/RueckgangBalken.vue` - Rueckgang-Saeulen mit gestrichelter Schwellenlinie
- `app/src/pages/EntwicklungPage.vue` - Abschnitt "Wie lange reicht das Polster?"

## Decisions Made

- **Dokumentierte Abweichungen von der UI-SPEC (Nutzerentscheidung 3, 2026-10-05):** Achsenunterschrift "Bestand zu Jahresbeginn" wie auf S. 311 gedruckt; Rueckgangswerte wie auf S. 23 gedruckt (Test auf zwei Nachkommastellen, Anzeige mit einer Nachkommastelle ueber `prozent()`); der Claim "jeweils unter 5 %" fehlt (2029 liegt mit 10,04 % darueber, Test und Text ohne diese Aussage); Tabellenspalte "Rueckgang im Jahr (berechnet)" statt "gegenueber Vorjahr", damit der Rueckgang nicht um ein Jahr verschoben wird (Pitfall 1).
- Funktionen der Lib nehmen die Tabelle bzw. `meta` als optionalen letzten Parameter (Default: echte Daten). Das erlaubt Randfalltests ohne Daten-Mocks und aendert die Aufrufe der Seite nicht.
- `rueckgang()` liefert `null` (nicht 0, nicht NaN) bei fehlendem Eingangswert oder Bestand 0; abweichend vom Research-Skizzenwert 0 bei Bestand 0, damit kein falscher Wert angezeigt wird.
- Schwellenbeschriftung steht links ueber der Linie (`insideStartTop`) mit Kartenflaechen-Hintergrund, nicht rechts am Linienende: dort laege sie ueber der hoechsten Saeule (Planjahr mit dem groessten Rueckgang) und waere unlesbar.
- Auf schmalen Bildschirmen traegt nur die letzte Saeule des Ruecklagen-Diagramms die Summe (wie `ErgebnisBalken`); Tooltip und immer sichtbare Tabelle tragen alle Werte.

## Deviations from Plan

None - plan executed exactly as written. (Die oben genannten Abweichungen von der UI-SPEC sind in der Plan-Kontextnotiz bereits als Nutzerentscheidung 3 dokumentiert; Layoutdetails wie die Position der Schwellenbeschriftung liegen im Ermessen der Umsetzung.)

**Total deviations:** 0 auto-fixed.

## Issues Encountered

- Die erste RED-Fassung der Tests rief die neuen Funktionen auf Suite-Ebene (`describe`) auf, was die ganze Datei mit "0 tests" abbrechen liess (kein gueltiges RED). Die Aufrufe wurden in die `it`-Bloecke verschoben; danach schlugen genau die 10 Zieltests an der fehlenden Funktion fehl (gueltiges RED), bevor committet wurde.
- Kein Browser im Sandbox-Lauf: der `human-check` der Aufgabe 2 (Sichtpruefung bei 1280 px und 360 px) steht aus (siehe unten).

## Verification

- Scratch-Kopie mit Linux-`node_modules`: `type-check`, `lint`, `format:check`, `test` (31 Dateien, 1245 Tests) und `build` gruen.
- Akzeptanzkriterien Task 1 und 2: alle `grep`-Pruefungen bestanden (`export function rueckgang`, `hsk_schwelle_zwei_jahre`, `Bestand zu Jahresbeginn`, kein Jahreswert in Codezeilen von `ruecklagen.ts`, `markLine`/`SCHWELLE_FARBE`, `schluessel="polster"`/`"haushaltssicherung"`, `Rückgang im Jahr (berechnet)`); `unter 5` und `gegenüber Vorjahr` kommen in `app/src` nirgends vor.
- Tracer-Gate: Task-1-`<verify>` end-to-end gruen, daher "Tracer verified end-to-end - expanding".

## TDD Gate Compliance

RED (`5bf8663`, test) und GREEN (`2763c2e`, feat) liegen in dieser Reihenfolge vor; kein Refactor-Commit noetig.

## Known Stubs

None.

## Threat Flags

None. Keine neuen Netzwerkpfade, Auth-Pfade oder Dateizugriffe; T-06-21 (S.-23-Werte auf zwei Nachkommastellen, S.-311-Spaltenidentitaet, Python/TS-Regelgleichheit) und T-06-22 (nur der freigegebene Pipeline-Text, Schwellen dem Vorbericht zugeschrieben, keine Prognose ueber das letzte Planjahr) sind umgesetzt und getestet.

## User Setup Required

None - no external service configuration required.

## Open Item (human-check, Task 2)

Dev-Server, `/entwicklung` bei 1280 px und 360 px: Ruecklagen-Saeulen mit Summen und Unterschrift "Bestand zu Jahresbeginn"; Rueckgang-Saeulen 1,8 / 4,2 / 4,7 / 10 % mit gestrichelter Schwellenlinie, deren Beschriftung innerhalb des Diagramms bleibt; Tabelle und Polster-Text lesbar; keine Aussage ueber Jahre nach dem letzten Planjahr. Das Plan-Verify ist automatisiert gruen; die Sichtpruefung gehoert in den Phasen-Abnahmeschritt.

## Next Phase Readiness

- ENTW-03 abgeschlossen; zusammen mit 06-05 ist ROADMAP-Erfolgskriterium 1 fuer `/entwicklung` vollstaendig.
- Keine Blocker fuer die folgenden Plaene.

## Self-Check: PASSED

- FOUND: app/src/lib/ruecklagen.ts, app/src/lib/__tests__/ruecklagen.test.ts, app/src/components/RuecklagenBalken.vue, app/src/components/RueckgangBalken.vue
- FOUND commits: da3ba3c, 5bf8663, 2763c2e, b8f97ee

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
