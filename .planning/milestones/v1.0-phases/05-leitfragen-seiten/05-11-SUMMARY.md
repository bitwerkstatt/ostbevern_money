---
phase: 05-leitfragen-seiten
plan: 11
subsystem: ui
tags: [vue, typescript, vitest, produktseite, teilergebnisplan, grundzahlen, bezugsgroessen]

requires:
  - phase: 05-leitfragen-seiten
    provides: "findeProdukt/findeKnoten/leseAnsicht (05-04), DatenTabelle, BerechnetEtikett, proKopf, zeilenName (05-05, 05-06), Bezugsgroessen-Freigabe (05-03)"
provides:
  - "lib/produkt.ts: Seitenmodell der Produktseite (Kopf, Teilergebnisplan, Erlaeuterungen, Grundzahlen, Investitionen, BEZUGSGROESSEN)"
  - "Vollstaendige Produktseite /produkt/:code mit allen AUSG-05-Abschnitten und Zurueck-Link"
  - "DatenTabelle: Spaltenart 'dezimal' und optionaler Slot 'zeilenzusatz' (additiv)"
affects: [05-13 Glossar-Produktakkordeon (Linkziel), Phase 6, Phase 7 Quellen-Panel]

actuals:
  tokens: 11500
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Seitenmodell als reine Funktionen in lib/ (Tabellen als {spalten, zeilen} fuer DatenTabelle), Seite nur Darstellung"
    - "URL-Werte nur ueber Map/leseAnsicht nachschlagen (Prototyp-Schluessel), gemerkte Query wird vor Gebrauch neu validiert"
    - "Zeilenmarkierung ueber Zeilenfeld etikett='berechnet' plus DatenTabelle-Slot zeilenzusatz statt den Zellinhalt zu ersetzen"

key-files:
  created:
    - app/src/lib/produkt.ts
    - app/src/lib/__tests__/produkt.test.ts
  modified:
    - app/src/pages/ProduktPage.vue
    - app/src/components/DatenTabelle.vue
    - app/src/components/datenTabelle.ts

key-decisions:
  - "BEZUGSGROESSEN exakt wie in 05-03 freigegeben (030101/030102 je Schueler/in, 040301 je Musikschueler/in, 060101 je betreutem Kind aus U3 + 3-6 summiert), per Test gepinnt"
  - "Dezimalspalten gelten fuer die ganze Grundzahlen-Tabelle, sobald eine Grundzahl des Produkts Nachkommastellen hat (Spalten sind je Jahr, Nachkommastellen je Zeile)"
  - "Zurueck-Link uebernimmt die gemerkte Ansicht nur, wenn sie zum Produkt passt; sonst PB/PG des Produkts"
  - "Hinweise der Grundzahlen werden dedupliziert; ein Hinweis, der in einem laengeren enthalten ist, entfaellt"

patterns-established:
  - "etikett-Zeilenfeld + zeilenzusatz-Slot fuer markierte berechnete Tabellenzeilen"

requirements-completed: [AUSG-05]

coverage:
  - id: D1
    description: "Produktseite zeigt Beschreibung, Leistungen, Bindungsgrad, Gremium, Fachbereich und Quellseite; Zurueck-Link fuehrt zur Ausgabenebene des Produkts"
    requirement: AUSG-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/produkt.test.ts#baueProduktKopf (D-09)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Teilergebnisplan 2024-2029 stimmt fuer alle 63 Produkte mit ergebnisplan[code].zeilen ueberein; Zuschussbedarf und Zuschussbedarf je Einwohner sind als berechnet markiert"
    requirement: AUSG-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/produkt.test.ts#baueTeilergebnisplan (AUSG-05, D-23)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Grundzahlen mit Dezimalstellen und Zuschussbedarf je Einheit nur fuer die freigegebene Liste und nur fuer Jahre mit beiden Werten"
    requirement: AUSG-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/produkt.test.ts#baueGrundzahlen (AUSG-05)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Erlaeuterungen mit aufgeloesten Zeilennamen und Investitionen je Produkt inklusive Leerzustand"
    requirement: AUSG-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/produkt.test.ts#baueErlaeuterungen (AUSG-05)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/produkt.test.ts#baueProduktInvestitionen (AUSG-05)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Optik und Verhalten im Browser: Abschnittsreihenfolge, horizontales Scrollen der Tabelle bei 360 px mit fester erster Spalte, Zurueck-Link mit gleichem Jahr"
    requirement: AUSG-05
    verification: []
    human_judgment: true
    rationale: "Layout, Scrollverhalten und Fokusreihenfolge sind im Node-Test nicht pruefbar; die Plan-Verifikation sieht einen Hostcheck vor"

duration: 25min
completed: 2026-10-04
status: complete
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: ec721bcebcb8829069643534d84a2b4815601d01
commits: 3
---

# Phase 5 Plan 11: Produktdetailseite Summary

**Vollstaendige Produktseite `/produkt/:code` mit getestetem Seitenmodell (Kopf, Teilergebnisplan, Erlaeuterungen, Grundzahlen mit freigegebenen Je-Einheit-Werten, Investitionen) fuer alle 63 Produkte**

## Performance

- **Duration:** ca. 25 min
- **Completed:** 2026-10-04T13:29:24Z
- **Tasks:** 2
- **Files modified:** 5 (2 neu, 3 geaendert)

## Accomplishments

- Tracer: `baueProduktKopf` (Namen von PB/PG, Quellseite, Bindungsgrad-Text, Zurueck-Ziel) end-to-end bis in die Seite; Prototyp- und Fremdcodes liefern `null` bzw. die Fehlerseite.
- Teilergebnisplan mit allen Zeilen mit Wert plus den Summen Ertraege, Aufwendungen, Jahresergebnis, benannt ueber `haushalt.zeilen_namen`, dazu die berechneten Zeilen Zuschussbedarf und Zuschussbedarf je Einwohner mit `BerechnetEtikett`. Spaltenkopf je Jahr als "{Wertart} {Jahr}".
- Erlaeuterungen mit Betrag, Text und aufgeloesten Zeilennamen ("zu: ..." nur bei Wechsel der Zeilen); Grundzahlen mit Einheit, Hinweis-Fussnote und Dezimalspalten; Investitionen als Tabelle oder Leertext.
- `DatenTabelle`: neue Spaltenart `dezimal` (max. 2 Nachkommastellen) und Slot `zeilenzusatz`, beides additiv.
- 268 Tests in `produkt.test.ts` (gesamt 410 in der Suite), darunter die Probe AUSG-05 ueber alle 63 Produkte und der Namensfreiheits-Test.

## Task Commits

1. **Task 1: Tracer Produktseite (Kopf, Beschreibung, Leistungen, Auf einen Blick, Quelle, Zurueck-Link)** - `f023e3e` (feat)
2. **Task 2 RED: fehlschlagende Tests fuer Teilergebnisplan, Bezugsgroessen, Grundzahlen, Investitionen, Erlaeuterungen** - `d270aff` (test; 182 Assertions schlugen gegen das Geruest fehl)
3. **Task 2 GREEN: Implementierung und Seite** - `ec721bc` (feat)

**Plan metadata:** wird mit diesem SUMMARY committet (docs).

## TDD Gate Compliance

RED-Commit `d270aff` (`test(05-11)`) vor GREEN-Commit `ec721bc` (`feat(05-11)`). Die RED-Tests liefen gegen ein Geruest mit leeren Rueckgaben und schlugen auf Assertions fehl (kein Lade- oder Importfehler). Ein erster RED-Lauf ohne Geruest scheiterte in der Collection-Phase (`BEZUGSGROESSEN` undefiniert, null Tests) und wurde deshalb als ungueltig verworfen. Kein REFACTOR-Commit noetig.

## Files Created/Modified

- `app/src/lib/produkt.ts` - Seitenmodell: Kopf, Teilergebnisplan, Erlaeuterungen, BEZUGSGROESSEN, Grundzahlen, Investitionen
- `app/src/lib/__tests__/produkt.test.ts` - Tests ueber alle 63 Produkte, Prototyp-Codes, Bezugsgroessen-Liste, Namensfreiheit
- `app/src/pages/ProduktPage.vue` - alle Abschnitte in UI-SPEC-Reihenfolge, Fehlerzustand unveraendert
- `app/src/components/DatenTabelle.vue` / `datenTabelle.ts` - Spaltenart `dezimal`, Slot `zeilenzusatz`

## Decisions Made

- Bezugsgroessen exakt wie in 05-03 freigegeben; Test pinnt die Produktliste und prueft, dass jede Bezeichnung im Produkt genau einmal vorkommt.
- Dezimalspalten pro Tabelle statt pro Zeile (siehe Abweichung 1).
- Zurueck-Link: gemerkte Query wird mit `leseAnsicht` neu validiert und nur uebernommen, wenn `pb` (und ggf. `pg`) zum Produkt passen; Modus bleibt erhalten.
- Bindungsgrad zeigt den Plan-Wortlaut nur, wenn er sich nach Normalisierung (ohne Kommas, Gross-/Kleinschreibung) vom ausgeschriebenen Text unterscheidet (3 Produkte mit "teils freiwillig teils pflichtig").

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Dezimalspalten pro Tabelle statt pro Spalte je Grundzahl**
- **Found during:** Task 2
- **Issue:** Der Plan verlangt "dezimal"-Spalten, wo `nachkommastellen > 0`. Die Spalten der Grundzahlen-Tabelle sind aber Jahre, Nachkommastellen haengen an den Zeilen; eine Spalte kann nicht je Zeile verschieden sein.
- **Fix:** Sobald eine Grundzahl des Produkts Nachkommastellen hat, sind alle Jahresspalten `dezimal` (0 bis 2 Nachkommastellen), sonst `zahl`. Ganze Werte erscheinen in Dezimalspalten ohne Nachkommastellen, Werte wie 12,5 behalten sie. Nachgestellte Nullen (z. B. 55,0) entfallen; der Zahlenwert bleibt korrekt.
- **Files modified:** app/src/lib/produkt.ts
- **Verification:** Test "waehlt dezimale Spalten genau dann, wenn eine Grundzahl Nachkommastellen hat".
- **Committed in:** ec721bc

**2. [Rule 3 - Blocking] Additiver Slot `zeilenzusatz` in DatenTabelle**
- **Found during:** Task 2
- **Issue:** Der Slot `zelle` ersetzt den kompletten Zellinhalt; ein Etikett "berechnet" neben dem Zeilennamen haette die ganze Zahlenformatierung in der Seite dupliziert.
- **Fix:** Optionaler Slot `zeilenzusatz` hinter dem Inhalt der ersten Zelle. Ohne Slot aendert sich nichts, bestehende Nutzer bleiben unberuehrt.
- **Files modified:** app/src/components/DatenTabelle.vue
- **Verification:** SSR-Rauchtest (nicht committet) fuer alle 63 Produkte, Typpruefung und Lint.
- **Committed in:** ec721bc

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Beide innerhalb der Plandateien, rueckwaertskompatibel, ohne Scope-Erweiterung. Keine Aenderung an Shared-Files (main.ts, router, echartsTheme.ts).

## Issues Encountered

- Die erste RED-Fassung war ungueltig (Collection-Fehler statt Assertion-Fehler); mit einem Geruest in `produkt.ts` neu aufgesetzt (siehe TDD Gate Compliance).
- Zusaetzlich zur Plan-Verifikation wurde die Seite fuer alle 63 Produkte in einem temporaeren SSR-Rauchtest (nicht committet) gerendert: kein Laufzeitfehler, `berechnet`-Etiketten nur an den erwarteten Zeilen.

## Verification Results

- `npm run test` 12 Dateien, 410 Tests gruen; `type-check`, `lint`, `format:check`, `build` gruen (Scratch-Kopie mit unveraendertem `package-lock.json`, kein `npm ci` noetig).
- Akzeptanzkriterien Task 1 und Task 2 per grep geprueft (PASS).
- Hostcheck (Plan, `human-check`) steht aus: /#/produkt/030101, /#/produkt/160101 und ein Produkt ohne Investitionen im Browser pruefen (Abschnittsreihenfolge, Scrollen bei 360 px, Zurueck-Link mit gleichem Jahr).

## Known Stubs

Keine. Die "Quelle"-Zeile ist bewusst reiner Text; das Quellen-Panel mit PDF-Ausschnitt folgt in Phase 7 (UI-02, DATA-04).

## Threat Flags

Keine neuen Angriffsflaechen. T-05-29 bis T-05-31 sind umgesetzt: Nachschlagen nur ueber Maps, gemerkte Query neu validiert, nicht freigegebene Je-Einheit-Zeilen per Test ausgeschlossen. Keine neue Abhaengigkeit, keine neuen Web-Awesome-Importe (`wa-tag`, `wa-button` sind in `main.ts` bereits importiert).

## Next Phase Readiness

- `/produkt/:code` ist als Linkziel fuer Ausgaben-Tabellen (05-10) und Glossar-Akkordeon (05-13) bereit; der Zurueck-Link erwartet die Query `modus`, `pb`, `pg`, `jahr` am Produktlink.
- Offen: Hostcheck im Browser am Phasenende.

## Self-Check: PASSED

- Gefunden: app/src/lib/produkt.ts, app/src/lib/__tests__/produkt.test.ts, app/src/pages/ProduktPage.vue, app/src/components/datenTabelle.ts
- Commits vorhanden: f023e3e, d270aff, ec721bc

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
