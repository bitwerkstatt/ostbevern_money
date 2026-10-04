---
phase: 05-leitfragen-seiten
plan: 14
subsystem: app-ausgaben
tags: [ausgaben, aufwandsart, transferaufwendungen, kreisumlage, minderaufwand, echarts, vitest, tdd]
status: complete

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-06 KreisumlageCallout/ErklaerText/textFuerJahr/zeilenName/findeKlKnoten, 05-09 charts/balken.ts (horizontaleBalkenOption, balkenHoehe), 05-10 AusgabenPage (Drilldown, ansicht, ChartCard-Reihenfolge)"
provides:
  - "lib/aufwandsarten.ts: ABSCHREIBUNG_ZEILE, baueAufwandsarten, baueTransferaufwendungen, minderaufwandHinweis (+ Typen Aufwandsart, TransferPosten, MinderaufwandHinweis)"
  - "AufwandsartBalken.vue (AUFWANDSART_FARBE, nie PB-Farben)"
  - "Vollständige AusgabenPage: Aufwandsart-Karte, Transfer-Aufklapper, Kreisumlage-Callout, Minderaufwand-Hinweis"
affects: [05-leitfragen-seiten, phase-07-smoke-test]

requirements-completed: [AUSG-02, AUSG-04]

actuals:
  tokens: 9000
  tasks: 2
  commits: 5
plan_head_before: 87d0865f3cd6e48aab1c846e8abfc2141d4d504f
plan_head_after: 7d3658b68b17c76cc98e08ee1b653ce8d49c3d9e

tech-stack:
  added: []
  patterns:
    - "Builder lesen nur aus haushalt.json und liefern null/leer statt 0; Anzeige (rd., kein Geldfluss) erst in der Seite"
    - "Geprüfter Erklärtext nur über textFuerJahr (Haushaltsjahr), für andere Jahre ein Satz aus Betrag und Jahr der Daten (Pitfall 6)"
    - "Zeilenkennzeichen in DatenZeile als 0/1; zelle-/zeilenzusatz-Slot rendert Etiketten"

key-files:
  created:
    - app/src/lib/aufwandsarten.ts
    - app/src/lib/__tests__/aufwandsarten.test.ts
    - app/src/components/AufwandsartBalken.vue
  modified:
    - app/src/pages/AusgabenPage.vue

key-decisions:
  - "Die Aufwandsarten ergeben den Gesamtaufwand auf den Euro in jedem Jahr außer 2024, dort höchstens 1 € Druckrundung (Z. 17 gedruckt 30.551.079 €, Σ Z. 11-16 = 30.551.080 €); Test: exakt ab 2025, ±1 € für alle Jahre"
  - "Der Verweis '(siehe Fußnote)' im Namen der Kreisumlage-Zeile entfällt, solange die Daten keine Anmerkung tragen"
  - "KL-Callout erscheint bei pb=null und pb=KL (auch mit pg unterhalb von KL), nie in anderen Aufgabenbereichen"
  - "Der Minderaufwand-Satz außerhalb des Haushaltsjahrs nennt nur Jahr, Betrag und die jahrneutrale Definition als pauschalen Kürzungsbetrag, Quelle PDF-Seite des GESAMT-Knotens"

coverage:
  - id: D1
    description: "Aufwand nach Aufwandsart: sieben Zeilen (GEP 11-16, 20), absteigend, Namen aus zeilen_namen, Summe = berechnet.aufwand (exakt ab 2025, 2024 ±1 €), nur Abschreibungen 'kein Geldfluss'"
    requirement: AUSG-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/aufwandsarten.test.ts#baueAufwandsarten (AUSG-04), #Aufwandsarten Haushalt 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "Transferaufwendungen im Einzelnen: Vorbericht-Posten als rd. mit PDF-Seite, Summe innerhalb Anzahl x 1.000 € von GEP Z. 15, Kita-Einrichtungen nur im Haushaltsjahr"
    requirement: AUSG-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/aufwandsarten.test.ts#baueTransferaufwendungen (AUSG-04), #Transferaufwendungen Haushalt 2026"
        status: pass
    human_judgment: false
  - id: D3
    description: "Globaler-Minderaufwand-Hinweis nur in Jahren mit Wert != 0, geprüfter Text nur im Haushaltsjahr, zusammengesetzter Satz sonst, nie als Kachel"
    requirement: AUSG-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/aufwandsarten.test.ts#minderaufwandHinweis (AUSG-02, Pitfall 6), #Minderaufwand Haushalt 2026"
        status: pass
      - kind: other
        ref: "SSR-Rendering von /ausgaben für 2024/2025/2026 im Scratch-Copy (nicht eingecheckt): 2024 ohne Callout, 2025 mit Satz und PDF-Seite 62, 2026 mit Erklärtext Seite 51, 8"
        status: pass
    human_judgment: true
    rationale: "Optische Platzierung und Lesbarkeit der Callouts (360 px) brauchen einen Browser"
  - id: D4
    description: "Kreisumlage-Callout (volle Form) auf oberster Ebene und in KL, nicht in anderen Aufgabenbereichen; Layout der neuen Karte, Aufklapper und Etiketten"
    requirement: AUSG-02
    verification:
      - kind: other
        ref: "SSR-Rendering mit Memory-Router für ?pb=KL, ?pb=11, oberste Ebene: Callout vorhanden bzw. fehlend wie geplant (nicht eingecheckt)"
        status: pass
    human_judgment: true
    rationale: "Der Plan-Human-Check (npm run dev, /#/ausgaben 2026 und 2024) lief nicht: Linux-Sandbox ohne Browser"

duration: ca. 25 min
completed: 2026-10-04
---

# Phase 5 Plan 14: Ausgaben-Erklärungen und Aufwandsart-Sicht Summary

**`/ausgaben` ist komplett: Kreisumlage-Callout auf oberster Ebene und in KL, Hinweis „Globaler Minderaufwand“ nur in Jahren mit Wert und mit jahrespassendem Text, und die zweite Sicht „Aufwand nach Aufwandsart“ (sieben GEP-Zeilen in Aufwandsart-Grau, Abschreibungen als „kein Geldfluss“) mit aufklappbaren Transferaufwendungen inklusive Kita-Einrichtungen.**

## Performance

- **Tasks:** 2 (1 Tracer, 1 TDD)
- **Files:** 4 (3 neu, 1 geändert)
- **Commits:** 5 Code-Commits plus dieses SUMMARY
- **Tests:** vitest gesamt 952 passed (22 Dateien); `aufwandsarten.test.ts` 81 Tests

## Accomplishments

- **Tracer (Task 1):** `baueAufwandsarten` liest die GEP-Zeilen 11-16 und 20 (keine Summenzeilen, Nullzeilen entfallen), Namen über `zeilenName`, Anteil = Wert / `berechnet.aufwand`, Abschreibungen mit `keinGeldfluss`. `AufwandsartBalken` nutzt `horizontaleBalkenOption` mit `AUFWANDSART_FARBE`; die Karte „Aufwand nach Aufwandsart {jahr}“ steht am Seitenende (Quelle: GESAMT-Seite), mit Zeile `wa-tag` „kein Geldfluss“ + „Wertverlust von Gebäuden und Straßen, kein Geldfluss“ und Tabelle im Aufklapper (das Etikett steht auch in der Namenszelle). Tracer-Verify (Test, type-check, lint, format:check, build) war grün, bevor Task 2 begann.
- **Transferaufwendungen (Task 2):** `baueTransferaufwendungen` liefert die Vorbericht-Posten des Jahres absteigend, alle `gerundet` mit Quellseite; die sieben Kita-Einrichtungen hängen als `kinder` an den Kita-Zuschüssen und nur in Jahren, in denen der Vorbericht sie druckt (2026). Das geschlossene `wa-details` „Transferaufwendungen im Einzelnen“ zeigt „rd. …“ und PDF-Seite, Kita-Zeilen eingerückt.
- **Minderaufwand-Hinweis:** `minderaufwandHinweis` ist `null` bei GEP-Wert 0 (2024), sonst Betrag = −Wert; `textSchluessel` nur im Haushaltsjahr (über `textFuerJahr`), für 2025 und 2027-2029 ein Satz „Für {Jahr} setzt der Plan einen globalen Minderaufwand von {Betrag} an …“ mit PDF-Seite 62. Das Callout steht unter der Drilldown-Karte, nie als Kachel oder Treemap-Knoten.
- **Kreisumlage-Callout:** `KreisumlageCallout` (volle Form) erscheint bei `pb === null` und `pb === KL`; im SSR-Rendering fehlt er bei `pb=11`.

## Task Commits

1. **Task 1 (Tracer)** - `edeac66` (feat): Aufwandsart-Sicht inkl. Tests, Komponente, Seite
2. **Task 2 (TDD)**
   - RED `0fcbfd1` (test): Signatur-Stubs, 17 neue Tests scheitern an Assertions
   - GREEN `f691353` (feat): `baueTransferaufwendungen`, `minderaufwandHinweis`, 80 Tests grün
   - Fix `b197550` (fix): Fußnotenverweis ohne Anmerkung entfällt, Test ergänzt
   - Seite `7d3658b` (feat): Callouts und Transfer-Aufklapper in `AusgabenPage.vue`

## TDD Gate Compliance

Task 2: `test(05-14)` `0fcbfd1` vor `feat(05-14)` `f691353`. RED mit Signatur-Stubs (`[]`/`null`), die 17 Fehlschläge sind Assertions des geplanten Verhaltens (Mengen, Beträge, Textschlüssel, Wurf bei Jahresindex außerhalb), keine Modul- oder Syntaxfehler. `gsd_run check tdd-red-evidence` stand im Worktree nicht zur Verfügung; die Fehlschläge wurden an der vitest-Ausgabe geprüft. Task 1 ist ein Tracer (Test und Code in einem Commit, kein RED-Commit). Kein REFACTOR-Commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan-Annahme „Summe exakt in jedem Jahr“ trifft für 2024 nicht zu**
- **Found during:** Task 1 (Datenprüfung vor den Tests)
- **Issue:** `berechnet.aufwand` = GEP Z. 17 (gedruckt) + Z. 20. Die Summe der Zeilen 11-16 weicht 2024 um 1 € von Z. 17 ab (30.551.080 € statt 30.551.079 €), also 30.703.629 € statt 30.703.628 €. Das ist dieselbe PDF-Rundung, die die UI-SPEC beim Sankey-Ausgleich nennt.
- **Fix:** Der Test prüft die Summe in jedem Jahr mit höchstens 1 € Abweichung (Grenze aus CLAUDE.md „Genauigkeit“) und auf den Euro genau für alle Jahre außer 2024; 2026 exakt 30.455.569 €. Die Builder-Werte bleiben unverändert aus dem GEP.
- **Files modified:** app/src/lib/__tests__/aufwandsarten.test.ts
- **Committed in:** edeac66

**2. [Rule 1 - Bug] Dangling „(siehe Fußnote)“ in der Kreisumlage-Zeile**
- **Found during:** Task 2 (SSR-Rendering der Transfer-Tabelle)
- **Issue:** Der gedruckte Name „Kreisumlage (siehe Fußnote)“ verweist auf eine Fußnote, die die Daten (`anmerkung: null`) nicht tragen; die Tabelle zeigte einen Verweis ins Leere.
- **Fix:** Der Verweis wird nur entfernt, wenn der Posten keine Anmerkung hat; trägt ein Posten künftig eine Anmerkung, bleibt der Name unverändert und die Seite zeigt den Anmerkungstext als Tabellen-Fußnote.
- **Files modified:** app/src/lib/aufwandsarten.ts, app/src/lib/__tests__/aufwandsarten.test.ts
- **Committed in:** b197550

### Plan-Interpretation

- **Reihenfolge der Seite:** Drilldown-Karte, Kreisumlage-Callout, Minderaufwand-Callout, Überschuss-Callout (nur Modus Zuschussbedarf), Aufwandsart-Karte (UI-SPEC Page Layout Punkte 2-6). Der Transfer-Aufklapper steht in der Aufwandsart-Karte vor „Tabelle anzeigen“.
- **Sortierung der Transfer-Posten:** absteigend nach Wert statt in gedruckter Reihenfolge, damit der größte Posten (Kreisumlage) oben steht; die Kita-Einrichtungen sind ebenfalls absteigend.
- **KL-Callout bei pg:** auch bei `pb=KL&pg=KL.…` sichtbar (Ebene „innerhalb KL“).

**Total deviations:** 2 auto-fixed (2 Bugs) plus Interpretationshinweise. **Impact:** kein Scope-Creep; keine geteilten Dateien (`main.ts`, Router, `echartsTheme.ts`, `eslint.config.ts`) angefasst, keine neuen Web-Awesome-Imports nötig (`tag`, `details`, `callout` bereits in `main.ts`).

## Authentication Gates

None.

## Issues Encountered

- Der Plan-Human-Check (Dev-Server, `/#/ausgaben` für 2026 und 2024 bei 1280 und 360 px) lief nicht: Linux-Sandbox ohne Browser. Stattdessen SSR-Rendering der Seite mit Memory-Router und gemocktem `BaseChart` (nicht eingecheckt): 2026 Minderaufwand mit geprüftem Text (PDF-Seite 51, 8) und sieben Kita-Zeilen, 2025 Satz mit 564.600 € und PDF-Seite 62 ohne Kita-Zeilen, 2024 ohne Minderaufwand-Callout, KL-Callout bei oberster Ebene und `pb=KL`, nicht bei `pb=11`; keine `NaN`/`undefined`/`{{` im HTML.
- Weiter offen für die Abnahme am Phasenende: Balkenbreite der Aufwandsart-Karte bei 360 px, Fokus und Tastaturbedienung der beiden `wa-details`, optischer Eindruck der Callouts.
- Die Sandbox lehnte zusammengesetzte Shell-Befehle mit git bzw. Heredocs ab; Befehle wurden einzeln ausgeführt. Das Plan-Ledger `gsd-plan-head-before-05-14` im Git-Verzeichnis des Worktrees ließ sich nicht schreiben; die Basis ist der vom Orchestrator genannte Worktree-Base `87d0865`, `commits: 5` ist mit `git rev-list --count 87d0865..HEAD` vor diesem SUMMARY gemessen.

## Known Stubs

None. Kein hartkodierter Leerwert fließt in die Oberfläche; Leertexte sind Oberflächentexte.

## Threat Flags

None. T-05-37 (Summenprüfung je Jahr gegen `berechnet.aufwand`), T-05-38 (geprüfter Text nur im Haushaltsjahr, sonst Satz aus den Daten des Jahres, Tests), T-05-39 („rd.“ für jeden T€-Wert) und T-05-SC (keine neue Abhängigkeit, `npm ci` im Scratch-Copy aus dem Lockfile) sind umgesetzt.

## Verification

- Scratch-Copy (`npm ci` aus dem Lockfile): `npm run test` 952 passed, `type-check`, `lint`, `format:check`, `build` grün.
- Acceptance: `Aufwand nach Aufwandsart`, `Wertverlust von Gebäuden und Straßen, kein Geldfluss`, `AUFWANDSART_FARBE` (AufwandsartBalken.vue), `Transferaufwendungen im Einzelnen`, `Globaler Minderaufwand`, `KreisumlageCallout` in der Seite: alle `grep -q` mit Exit 0; vitest listet `aufwandsarten.test.ts` mit den Minderaufwand- und Transfer-Tests grün.

## Next Phase Readiness

- `/ausgaben` ist vollständig (AUSG-01 bis AUSG-04); Browser-Abnahme steht aus.

## Self-Check: PASSED

- Gefunden: aufwandsarten.ts, aufwandsarten.test.ts, AufwandsartBalken.vue, AusgabenPage.vue.
- Commits `edeac66`, `0fcbfd1`, `f691353`, `b197550`, `7d3658b` vorhanden.
