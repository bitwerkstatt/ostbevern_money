---
phase: 06-kontext-seiten
plan: 10
subsystem: ui
tags: [vue, echarts, bindungsgrad, rat-entscheidet, wa-details, vitest]

requires:
  - phase: 06-kontext-seiten
    provides: "06-04: Texte bindungsgrad_selbstauskunft und ueberschuss_produkte, Glossarbegriff bindungsgrad"
  - phase: 06-kontext-seiten
    provides: "06-07: NichtBeeinflussbarBlock, lib/zuschuesse.ts nichtBeeinflussbar()"
provides:
  - "lib/bindungsgrad.ts: BINDUNGSGRADE, FINANZIERUNGSPRODUKT, baueBindungsgrad(), klAnteil()"
  - "BindungsgradBalken, ProduktBalkenListe, UeberschussListe und der KL-Vergleichssatz im NichtBeeinflussbarBlock"
  - "/rat-entscheidet vollständig in der UI-SPEC-Reihenfolge (RAT-01, RAT-02 mit Vergleich, RAT-04)"
affects: [06-11, phase-06-verification]

actuals:
  tokens: 8500
  tasks: 2
  commits: 3

plan_head_before: 14ef1e238657bf4cf1989b34397f37fbc86ace94
plan_head_after: 8c037c35e458ea14729bde881f819147677e5501

tech-stack:
  added: []
  patterns:
    - "Diagramm in geschlossenem wa-details erst beim ersten eigenen wa-show mounten (target === currentTarget) und danach gemountet lassen"
    - "Ein benannter Ausschluss (FINANZIERUNGSPRODUKT = ZEITREIHEN_PRODUKT) statt Codeliste in Komponenten"

key-files:
  created:
    - app/src/lib/bindungsgrad.ts
    - app/src/lib/__tests__/bindungsgrad.test.ts
    - app/src/components/BindungsgradBalken.vue
    - app/src/components/ProduktBalkenListe.vue
    - app/src/components/UeberschussListe.vue
  modified:
    - app/src/components/NichtBeeinflussbarBlock.vue
    - app/src/pages/RatEntscheidetPage.vue

key-decisions:
  - "Überschuss-Liste und Balken schließen beide das Finanzierungsprodukt aus (D-01 überstimmt UI-SPEC E5 populated, das jedes negative Produkt listete)"
  - "BindungsSegment trägt zusätzlich zu name (bindungsgradText, Produktseiten-Wortlaut) ein Feld bezeichnung (Pflichtig, Teils pflichtig, Freiwillig) für Beschriftung, Legende und Aufklapper"
  - "Klick auf einen Produktbalken wird über dataIndex aufgelöst (klickIndex aus lib/investitionen), weil horizontaleBalkenOption keine Codes in den Datenpunkten führt"
  - "Der Vergleichssatz steht im NichtBeeinflussbarBlock selbst (Prop balkenSumme); der Slot vergleich bleibt für weitere Hinweise erhalten"

requirements-completed: [RAT-01, RAT-04, RAT-02]

coverage:
  - id: D1
    description: "Gestapelter Bindungsgrad-Balken aus berechnet.zuschussbedarf mit Summen 6.358.143 / 4.491.669 / 2.436.628 € (Σ 13.286.440 €), ohne Finanzierungsprodukt, Satz dazu, Selbstauskunft-Callout"
    requirement: RAT-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/bindungsgrad.test.ts#Bindungsgrad Haushalt 2026"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/bindungsgrad.test.ts#baueBindungsgrad"
        status: pass
    human_judgment: false
  - id: D2
    description: "Überschuss-Liste enthält genau 011202, 011204, 110101 und verlinkt auf /produkt/:code"
    requirement: RAT-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/bindungsgrad.test.ts#führt im Überschuss genau 011202, 011204 und 110101"
        status: pass
    human_judgment: false
  - id: D3
    description: "KL-Vergleichssatz mit klAnteil (null bei Summe 0)"
    requirement: RAT-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/bindungsgrad.test.ts#klAnteil (RAT-02, D-02)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Visuelles Verhalten: Legende ab 700 px unter den Segmenten und bis 699 px als Tabelle, Aufklapper mit Diagramm in voller Breite, Balkenklick und Tastaturpfad zu /produkt/:code"
    requirement: RAT-01
    verification: []
    human_judgment: true
    rationale: "Im Sandbox gibt es keinen Browser; Layout, wa-show-Mounten und Fokusreihenfolge sind nur im laufenden Dev-Server prüfbar (Human-Check der Aufgabe 2)."

duration: 38min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 10: Bindungsgrad auf /rat-entscheidet Summary

**Bindungsgrad-Balken aus `berechnet.zuschussbedarf` mit einem benannten Ausschluss des Finanzierungsprodukts, drei Produkt-Aufklappern (Diagramm erst beim ersten `wa-show`), Überschuss-Liste und KL-Vergleichssatz auf /rat-entscheidet**

## Performance

- **Duration:** 38 min
- **Started:** 2026-10-06T08:30:00Z
- **Completed:** 2026-10-06T09:08:00Z
- **Tasks:** 2 (Tracer plus TDD-Aufgabe)
- **Files modified:** 7 (5 neu, 2 geändert)

## Accomplishments

- `lib/bindungsgrad.ts` liest jeden Wert aus `ergebnisplan[code].berechnet.zuschussbedarf` am Haushaltsjahr-Index, ohne Neurechnen. `FINANZIERUNGSPRODUKT` ist ein Alias von `ZEITREIHEN_PRODUKT`, es gibt kein zweites Codeliteral. Auf den 2026er Daten ergeben sich die Segmente 6.358.143 € (29 Produkte), 4.491.669 € (15), 2.436.628 € (15), Σ 13.286.440 €, und genau 011202, 011204, 110101 im Überschuss.
- `BindungsgradBalken` zeichnet einen gestapelten Balken (56 px im 160-px-Diagramm, `BINDUNG_FARBEN`, 2-px-Trenner in der Flächenfarbe). Ab 700 px stehen Name, Betrag und Anteil unter dem Segment (Raster proportional zum Betrag), bis 699 px steht die Legendentabelle immer sichtbar da, ab 700 px im Aufklapper „Tabelle anzeigen“. Ohne Segment erscheint der Leerzustand.
- Die Seite zeigt unter dem Balken einen ziffernfreien Satz mit dem Namen des Finanzierungsprodukts aus den Daten, der klarstellt, dass die Balkensumme nicht der Zuschussbedarf des ganzen Haushalts ist, danach das neutrale Callout mit dem abgenommenen Text `bindungsgrad_selbstauskunft` und einem `GlossarBegriff bindungsgrad`.
- `ProduktBalkenListe`: pro Bindungsgrad ein geschlossenes `wa-details` („{Bezeichnung} · {Betrag} · {n} Produkte“), Produktbalken in PB-Farben absteigend, Klick auf `/produkt/:code`, Tabelle mit `RouterLink` als Tastaturpfad. Das Diagramm wird erst beim ersten eigenen `wa-show` gemountet.
- `UeberschussListe` (rendert nichts ohne Überschuss-Produkte) und der Satz „Die Weitergabe an Kreis und Land beträgt {Betrag}. Das entspricht {Anteil} der Summe im Balken oben.“ mit `BerechnetEtikett` im `NichtBeeinflussbarBlock` (2026: 11 Mio. €, 82,8 %).

## Task Commits

1. **Task 1: Tracer, Bindungsgrad-Balken und Selbstauskunft** - `6c80c10` (feat)
2. **Task 2 RED: failing Test für klAnteil** - `5505bdd` (test)
3. **Task 2 GREEN: Produkte je Bindungsgrad, Überschuss-Liste, KL-Vergleichssatz** - `8c037c3` (feat)

**Plan metadata:** folgt als `docs(06-10)`-Commit mit dieser Datei.

Tracer-Gate (Modus `end-of-phase`, `<verify>` nur automatisiert): Die Verify-Kette lief nach dem Commit grün durch, Log „Tracer verified end-to-end — expanding“.

## Files Created/Modified

- `app/src/lib/bindungsgrad.ts` - Segmente, Produktlisten, Überschuss, `klAnteil`
- `app/src/lib/__tests__/bindungsgrad.test.ts` - 19 Tests: Konstante, Summen, Ausschluss, Sortierung, Sollwerte 2026, `klAnteil`
- `app/src/components/BindungsgradBalken.vue` - gestapelter Balken mit Beschriftung und Legende
- `app/src/components/ProduktBalkenListe.vue` - Aufklapper mit Produktbalken und Tabelle
- `app/src/components/UeberschussListe.vue` - Tabelle der Überschuss-Produkte
- `app/src/components/NichtBeeinflussbarBlock.vue` - Vergleichssatz mit Prop `balkenSumme`
- `app/src/pages/RatEntscheidetPage.vue` - Karte, Satz, Callout, Aufklapper, Überschuss, Block

## Decisions Made

Siehe `key-decisions`. Kurz: Ausschluss des Finanzierungsprodukts auch in der Überschuss-Liste (D-01), Feld `bezeichnung` für die kurzen Anzeigenamen, Klick-Auflösung über `dataIndex`, Satz im Block statt im Slot.

## Deviations from Plan

### Documented plan deviation (vom Plan vorgesehen)

**1. [D-01 überstimmt UI-SPEC E5 populated] Überschuss-Liste ohne das Finanzierungsprodukt**
- **Issue:** Die UI-SPEC listet jedes Produkt mit negativem Zuschussbedarf, D-01 nennt für 2026 nur 011202, 011204, 110101.
- **Fix:** `baueBindungsgrad()` schließt das Finanzierungsprodukt (160101, −20.225.500 €) aus Balken und Überschuss aus. Ein Test fixiert die Menge `{011202, 011204, 110101}`.
- **Files modified:** app/src/lib/bindungsgrad.ts, app/src/lib/__tests__/bindungsgrad.test.ts
- **Committed in:** 6c80c10

### Auto-fixed Issues

**2. [Rule 3 - Blocking] Gemeinsame Hilfsfunktion statt Doppelung für den Balkenklick**
- **Found during:** Task 2
- **Issue:** `horizontaleBalkenOption` führt keine Codes in den Datenpunkten, `codeAusParams` aus `lib/drilldown` greift deshalb nicht.
- **Fix:** `klickIndex(params, anzahl)` aus `lib/investitionen` (wie in `MassnahmenListe`) löst den Klick über `dataIndex` auf.
- **Files modified:** app/src/components/ProduktBalkenListe.vue
- **Committed in:** 8c037c3

**3. [Rule 2 - Missing Critical] Segmentfeld `bezeichnung`**
- **Found during:** Task 1
- **Issue:** `bindungsgradText` liefert „teils pflichtig, teils freiwillig“, die UI-SPEC verlangt „Pflichtig“, „Teils pflichtig“, „Freiwillig“ für Beschriftung, Legende, Summary und Tooltip.
- **Fix:** `name` bleibt `bindungsgradText` (wie im Plan), neues Feld `bezeichnung` trägt die Kurzform; ein Test sichert beide.
- **Committed in:** 6c80c10

### Ablaufabweichungen (ohne Wirkung auf das Ergebnis)

- **Verify im Scratch-Copy:** Die Verify-Kette lief in einem dauerhaften Scratch-Copy von `app/` mit der vorhandenen Linux-`node_modules` (Lockfile identisch, laut Umgebungshinweis) statt mit `npm ci` in einem `mktemp`-Verzeichnis. Gelaufen: type-check, lint, format:check, die ganze vitest-Suite (31 Dateien, 1234 Tests) und `npm run build`, alle grün.
- **Plan-Ledger:** Die Dateien `gsd-plan-head-before-06-10` und `gsd-spawn-toplevel` ließen sich im Worktree-Sandbox nicht schreiben (Schreibzugriff auf das gemeinsame `.git`-Verzeichnis gesperrt). `plan_head_before` ist deshalb der vom Orchestrator genannte Basis-SHA `14ef1e2`; `commits: 3` ist mit `git rev-list --count 14ef1e2..HEAD` gemessen (vor dem SUMMARY-Commit).
- **RED-Commit:** `5505bdd` enthält `klAnteil` als Platzhalter mit bewusst falschem Ergebnis, damit das Rot auf Zusicherungen beruht und kein Ladefehler ist (alle drei `klAnteil`-Tests scheiterten an Zusicherungen). Die Prettier-Formatierung der Testdatei kam erst mit dem GREEN-Commit.
- **Tracer ohne eigenen RED-Commit:** Aufgabe 1 ist ein Tracer ohne `tdd="true"`; Test-zuerst wurde lokal belegt (sieben Fehlschläge gegen einen Platzhalter), committet wurde einmal.

**Total deviations:** 1 geplante Abweichung (D-01), 2 automatische Korrekturen (Rule 2, Rule 3), 4 reine Ablaufabweichungen.
**Impact on plan:** Keine Ausweitung des Umfangs.

## TDD Gate Compliance

Aufgabe 2 (`tdd="true"`): RED `5505bdd` (`test(06-10)`), GREEN `8c037c3` (`feat(06-10)`), kein REFACTOR. Der Plan selbst hat `type: execute`, daher kein plan-weites Gate.

## Issues Encountered

None.

## Known Stubs

None.

## Offene Prüfung

Der Human-Check der Aufgabe 2 (Dev-Server, 1280 px und 360 px) wurde nicht ausgeführt, weil die Sandbox keinen Browser hat. Ersatzweise wurde die Seite einmalig per Server-Rendering geprüft (Balkenbeschriftung, Aufklapper-Summaries „Pflichtig · 6,36 Mio. € · 29 Produkte“ und weitere, Überschuss-Tabelle mit drei Produkten, Satz „… 11 Mio. €. Das entspricht 82,8 % …“, Callout-Text). Der Mount-Zeitpunkt beim ersten `wa-show` und das Layout der aufgeklappten Diagramme bleiben für `/gsd-verify-work` offen (RESEARCH A2).

## Threat Flags

None. Tooltips laufen ausschließlich über `tooltipZeilen`/`horizontaleBalkenOption`, keine Roh-HTML-Direktive (T-06-27); Werte stammen aus `berechnet.zuschussbedarf`, Summen und Ausschluss sind getestet, die Karte erklärt, dass die Balkensumme nicht der Gesamt-Zuschussbedarf ist (T-06-26); keine neue Abhängigkeit (T-06-SC).

## Next Phase Readiness

/rat-entscheidet ist mit 06-07 vollständig (ROADMAP SC 3). Die UI-Prüfung im Browser steht für die Phasenverifikation aus.

## Self-Check: PASSED

- Dateien vorhanden: lib/bindungsgrad.ts, lib/__tests__/bindungsgrad.test.ts, BindungsgradBalken.vue, ProduktBalkenListe.vue, UeberschussListe.vue.
- Commits `6c80c10`, `5505bdd`, `8c037c3` liegen auf dem Branch.
- Alle `<acceptance_criteria>` beider Aufgaben erneut geprüft und bestanden.

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
