---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 07
subsystem: quellenbelege-leitfragen
tags: [vue, vitest, quelle, datentabelle, einnahmen, ausgaben, playwright]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: "07-01: belegSchluessel, findeBeleg, DatenTabelle-Spaltenart quelle; 07-03: quellen.json mit allen Belegarten"
provides:
  - "Feld beleg (und herleitung) in lib/einnahmen.ts (PostenZeile, InvestiveZeile), lib/zeitreihen.ts (Zeitpunkt) und lib/aufwandsarten.ts (TransferPosten)"
  - "lib/ebenenBeleg.ts: ebenenBeleg(eintrag, jahrIndex, modus) fuer die Drilldown-Tabelle"
  - "Spalte Quelle (art quelle) in den Tabellen auf /einnahmen (Steuern, Zuwendungen, sonstige Ertraege, investive Einnahmen, Steuer-Zeitreihe) und /ausgaben (Drilldown, Transferaufwendungen)"
  - "lib/__tests__/quelle-leitfragen.test.ts: Abdeckung der Woher/Wofuer-Tabellen"
affects: [07-09, 07-10, 07-11]

actuals:
  tokens: 36000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Zeilenmodelle der lib/-Builder tragen den Belegschluessel (beleg) und optional die Herleitung; die Seite reicht beides als Zeilenfelder quelle und quelleHerleitung an DatenTabelle"
    - "Belegschluessel nur ueber belegSchluessel; ein Test loest jeden Schluessel ueber findeBeleg auf und vergleicht die Seite mit dem Seitenfeld der Zeile"

key-files:
  created:
    - app/src/lib/ebenenBeleg.ts
    - app/src/lib/__tests__/quelle-leitfragen.test.ts
  modified:
    - app/src/lib/einnahmen.ts
    - app/src/lib/zeitreihen.ts
    - app/src/lib/aufwandsarten.ts
    - app/src/pages/EinnahmenPage.vue
    - app/src/pages/AusgabenPage.vue
    - app/src/components/SteuerZeitreihe.vue
    - app/src/components/EbenenTabelle.vue
    - app/src/lib/__tests__/einnahmen.test.ts
    - app/src/lib/__tests__/zeitreihen.test.ts
    - app/src/lib/__tests__/aufwandsarten.test.ts

key-decisions:
  - "KL-Zeile im Drilldown zeigt auf seite:{pdf_seite des Knotens} (S. 281, Z. 15 des Teilergebnisplans), nicht auf vb:transferaufwendungen:gesamt; die Gesamtzeile umfasst alle Transferaufwendungen und waere falsche Evidenz (T-07-18)"
  - "Steuer-Zeitreihe: Vorbericht-Punkte tragen vb:{tabelle}:{posten} mit der Tabelle des Postens (steuerarten oder zuwendungen), weil die Schluesselzuweisung in zuwendungen steht"
  - "Konzessionsabgaben nach Sparte (Strom, Gas, Wasser) tragen meta:vorbericht_werte.{sparte}, weil ihre Seite aus meta.json stammt und kein vb-Posten existiert"
  - "Aufwand eines Knotens ist Z. 17 plus Z. 20: wo berechnet.aufwand von der gedruckten Z. 17 abweicht (16, 1601, 160101), nennt der Beleg im Modus Aufwand die Herleitung 'Ordentliche Aufwendungen plus Zinsen und aehnliche Aufwendungen'"

requirements-completed: [UI-02]

coverage:
  - id: D1
    description: "Alle Tabellenzeilen mit Seite auf /einnahmen (Steuern, Zuwendungen, sonstige Ertraege, investive Tabelle, Steuer-Zeitreihe) tragen einen Belegschluessel, der aufloest und auf die Seite der Zeile zeigt; berechnete Posten nennen eine Herleitung"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle-leitfragen.test.ts#Einnahmen, einnahmen.test.ts#Belegschluessel der Tabellenzeilen, zeitreihen.test.ts#Belegschluessel der Zeitreihe"
        status: pass
      - kind: e2e
        ref: "Wegwerf-Playwright-Lauf im Docker-Image (nicht eingecheckt): 42 Quelle-Knoepfe in den Tabellen von /einnahmen, Knopf Gewerbesteuer oeffnet die Seitenleiste"
        status: pass
    human_judgment: false
  - id: D2
    description: "Drilldown-Tabelle und Transferaufwendungen auf /ausgaben haben die Spalte Quelle mit ep-, vb- bzw. Seitenbeleg; im Modus Zuschussbedarf steht die Herleitung 'Aufwendungen minus Ertraege'"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle-leitfragen.test.ts#Ausgaben (alle Ebenen, alle Jahre, beide Modi), aufwandsarten.test.ts#jede Zeile traegt vb:transferaufwendungen"
        status: pass
      - kind: e2e
        ref: "Wegwerf-Playwright-Lauf: 33 Knoepfe auf /ausgaben, KL-Zeile oeffnet Seite 281 mit Hinweis Berechneter Wert im Modus Zuschussbedarf"
        status: pass
    human_judgment: false
  - id: D3
    description: "Eine Textspalte fuer die PDF-Seite ist in EinnahmenPage, SteuerZeitreihe, AusgabenPage und EbenenTabelle nicht mehr moeglich (Quelltextpruefung), es gibt keine zweite Seitenspalte"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle-leitfragen.test.ts#Seitenquelltexte definieren keine Seitenspalte als Text"
        status: pass
    human_judgment: false
  - id: D4
    description: "Optik der Quelle-Spalte (Abstaende, Umbruch bei 360 px, Lesbarkeit der Knoepfe in den breiten Tabellen)"
    requirement: "UI-02"
    verification:
      - kind: other
        ref: "Screenshot von /ausgaben gesichtet; 360-px-Pruefung gehoert zu Plan 07-09"
        status: pass
    human_judgment: true
    rationale: "Optik ist nur im Screenshot beurteilbar; die Abnahme folgt am Checkpoint 07-10"

duration: 40min
completed: 2026-10-06
status: complete
plan_head_before: a799ce0b63e5b0c7c9c4495564c479089661e7ae
plan_head_after: de559548fa584010f241079845122dd4574bcd9c
---

# Phase 7 Plan 07: Quelle-Spalten auf /einnahmen und /ausgaben Summary

**Jede Tabellenzeile mit PDF-Seite auf den beiden Leitfragen-Seiten (Aufschluesselungen, investive Einnahmen, Steuer-Zeitreihe, Drilldown, Transferaufwendungen) oeffnet jetzt ueber die Spalte "Quelle" die Belegseite; die Schluessel entstehen nur ueber belegSchluessel, berechnete Werte nennen ihre Herleitung, und ein Abdeckungstest loest jeden Schluessel ueber findeBeleg auf.**

## Performance

- **Duration:** 40 min
- **Tasks:** 2 (beide TDD mit RED- und GREEN-Commit)
- **Files modified:** 12 (2 neu)

## Accomplishments

- **/einnahmen:** `PostenZeile`, `InvestiveZeile` und `Zeitpunkt` tragen `beleg` (vb, fp, meta, gz) und `herleitung`. Die drei Aufschluesselungen bekommen eine neue Spalte Quelle (sie hatten nur eine Fussnote), die investive Tabelle und die Steuer-Zeitreihe ersetzen ihre Textspalten "PDF-Seite {n}" bzw. "Quelle" durch `art: 'quelle'`.
- **/ausgaben:** `ebenenBeleg` (neu) liefert je Drilldown-Zeile den Beleg: `ep:{code}:ordentliche_aufwendungen` fuer alle Knoten ausserhalb von KL, `vb:transferaufwendungen:{posten}` fuer die KL-Unterposten, `seite:281` fuer KL. `EbenenTabelle` haengt die Spalte Quelle an; die Transferaufwendungen-Tabelle nutzt `TransferPosten.beleg` (vb:transferaufwendungen, vb:kita_zuschuesse).
- **Abdeckungstest** `quelle-leitfragen.test.ts`: alle Jahre, alle Ebenen, beide Modi; Seitenvergleich zwischen Beleg und Zeile; Quelltextpruefung auf Textspalten; Selbsttests, dass ein erfundener Schluessel und eine Textspalte erkannt werden.
- **Pruefung im Browser:** Ein nicht eingecheckter Playwright-Lauf im Docker-Image bestaetigte 42 Knoepfe in den Tabellen von /einnahmen und 33 auf /ausgaben, das Oeffnen der Seitenleiste und den Hinweis "Berechneter Wert ... Aufwendungen minus Ertraege" im Modus Zuschussbedarf.

## Task Commits

1. **Task 1: /einnahmen** - RED `9ad104a` (test), GREEN `a16826d` (feat)
2. **Task 2: /ausgaben** - RED `fd39543` (test, mit Geruest `ebenenBeleg.ts`), GREEN `de55954` (feat)

## TDD Gate Compliance

- **RED Aufgabe 1** (`9ad104a`): 57 Tests rot (`beleg`/`herleitung` undefined, Seiten ohne `art: 'quelle'`). Semantische Bewertung: jeder Test lief und scheiterte an der Erwartung des neuen Felds, nicht an Syntax oder Import. `gsd_run check tdd-red-evidence` wurde nicht ausgefuehrt (`workflow.tdd_mode` aus, vitest-Standardbericht).
- **RED Aufgabe 2** (`fd39543`): 24 Tests rot; ein Geruest `ebenenBeleg` (liefert `null`) stellt sicher, dass die Tests an Assertions scheitern und nicht am Import.
- **GREEN:** `a16826d` und `de55954`, danach 1846 vitest-Tests gruen. Kein REFACTOR noetig.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] KL-Zeile haette mit vbGesamt('transferaufwendungen') falsche Evidenz gezeigt**
- **Found during:** Task 2 (Daten geprueft)
- **Issue:** Der Plan sieht fuer die KL-Zeile `vbGesamt('transferaufwendungen')` vor, "wenn es aufloest". Diese Zeile (Vorbericht S. 46) summiert alle Transferaufwendungen der Gemeinde, der KL-Wert (11.001.181 EUR) ist dagegen Z. 15 des Teilergebnisplans auf S. 281. Die Seitenleiste haette einen abweichenden Betrag gezeigt (T-07-18).
- **Fix:** KL zeigt auf `seite:{pdf_seite des Knotens}` (S. 281, ohne Markierung; die Seitenleiste nennt das offen).
- **Files modified:** app/src/lib/ebenenBeleg.ts
- **Committed in:** de55954

**2. [Rule 2 - Missing Critical] Herleitung fuer Knoten mit Zinsaufwendungen**
- **Found during:** Task 2
- **Issue:** `berechnet.aufwand` ist Z. 17 plus Z. 20; bei den Knoten 16, 1601, 160101 weicht er von der gedruckten Z. 17 ab. Ein reiner ep-Beleg haette dort einen gedruckten Wert behauptet.
- **Fix:** Im Modus Aufwand nennt der Beleg dort die Herleitung "Ordentliche Aufwendungen plus Zinsen und aehnliche Aufwendungen" (datengetrieben per Vergleich, kein Knotencode im Quelltext).
- **Files modified:** app/src/lib/ebenenBeleg.ts
- **Committed in:** de55954

### Kleine Abweichungen

- **Neue Datei `app/src/lib/ebenenBeleg.ts`** statt Logik in `EbenenTabelle.vue`, damit sie als reine Funktion testbar ist (nicht in der Dateiliste des Plans).
- **Steuer-Zeitreihe:** vb-Schluessel mit der Tabelle des Postens (nicht fest `steuerarten`), weil die Schluesselzuweisung in `zuwendungen` steht.
- **Konzessionsabgaben nach Sparte** tragen `meta:vorbericht_werte.{sparte}` (Plan nennt nur vb/fp).
- **Fussnoten** ("Quelle: PDF-Seite 27") unter den Aufschluesselungen bleiben stehen (ChartCard- und Tabellenfusszeile bleiben Text, UI-SPEC).
- **Ertragsarten-Tabelle (Ebene 1)** hat weiterhin keine Quelle-Spalte (nicht Teil der Dateiliste; ihre Quelle steht in der ChartCard-Zeile). Kandidat fuer eine Folgeaufgabe: `ep:GESAMT:{zeile}` ist vorhanden.
- **Die `<automated>`-Befehle** liefen direkt im Worktree (`npm ci`, type-check, lint, format:check, vitest, build-only, Playwright im Docker-Image) statt in einer Scratch-Kopie; alle gruen.

**Total deviations:** 2 auto-fixed (1 Bug, 1 Rule 2) plus kleine Ergaenzungen.
**Impact on plan:** Keine Aenderung an Schema oder Schluesselgrammatik.

## Issues Encountered

None.

## User Setup Required

None - keine externen Dienste noetig.

## Known Stubs

None. `bbox: null` (KL, einzelne vb-Posten) ist ein modellierter Zustand (D-03).

## Threat Flags

None - keine neue Flaeche; T-07-18 ist durch `belegSchluessel`, den Abdeckungstest und die Herleitungen abgedeckt.

## Next Phase Readiness

- Ready for 07-09 (Mobilpruefung der neuen Spalten bei 360 px) und 07-10 (optische Abnahme).
- Offen fuer 07-10: Die Spalte Quelle macht die Tabellen breiter; DatenTabelle scrollt waagerecht (bekanntes Verhalten).

## Self-Check: PASSED

- Dateien vorhanden: ebenenBeleg.ts, quelle-leitfragen.test.ts und alle geaenderten Dateien.
- Commits vorhanden: 9ad104a, a16826d, fd39543, de55954 (alle im Zweig).
- Akzeptanzkriterien beider Aufgaben erfuellt; Gesamtkette (type-check, lint, format:check, 1846 vitest, build-only, quelle.spec.ts 6 passed) gruen.

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
