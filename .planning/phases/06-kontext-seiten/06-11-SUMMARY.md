---
phase: 06-kontext-seiten
plan: 11
subsystem: ui
tags: [stellenplan, vzae, echarts, vue3, hundertstel, web-awesome]
requires:
  - phase: 06-kontext-seiten
    provides: "06-02: StellenplanPage-Rahmen, echartsTheme (KATEGORIE_FARBEN, HOHL_FLAECHE, farbeFuerPb), balkenHoehe"
  - phase: 06-kontext-seiten
    provides: "06-04: Glossarbegriffe vzae und entgeltgruppen"
provides:
  - "lib/stellen.ts: Stellensummen in Hundertstel (gesamt, je Teil, je Aufgabenbereich, je Gruppe), Nachwuchs, Differenztext"
  - "StellenNachTeil, StellenNachBereich, StellenNachGruppe"
  - "vollständige Seite /stellenplan (STEL-01, STEL-02, STEL-03)"
affects: [06-12]

actuals:
  tokens: 14900
  tasks: 3
  commits: 5

plan_head_before: 14ef1e238657bf4cf1989b34397f37fbc86ace94
plan_head_after: bbd1fa36ff538668c5c98dd0a6c8a9ac38e0066c

tech-stack:
  added: []
  patterns:
    - "Summen als ganze Hundertstel (Math.round(x * 100)), Division durch 100 erst in alsVzae() zur Anzeige"
    - "Lib-Funktionen nehmen die Datenquelle als optionalen Parameter (Standard: App-Daten), damit Tests Kopien mutieren können"
    - "Fehlender Wert ist null, nie 0; die Anzeige zeigt dann '–'"

key-files:
  created:
    - app/src/lib/stellen.ts
    - app/src/lib/__tests__/stellen.test.ts
    - app/src/components/StellenNachTeil.vue
    - app/src/components/StellenNachBereich.vue
    - app/src/components/StellenNachGruppe.vue
  modified:
    - app/src/pages/StellenplanPage.vue

key-decisions:
  - "Gruppen absteigend nach gedruckter position sortiert (ergibt 1 → 14, A 8 → B 3, S 11 → S 12); weicht vom UI-SPEC-Wortlaut 'aufsteigend nach position' ab (Nutzerentscheidung 4, RESEARCH Pitfall 7)"
  - "Differenz in Kachel 3 ist besetzt minus Stellen Haushaltsjahr (−6,28 gegenüber Stellen {Haushaltsjahr}); der Plantext nennt +6,28, aber das Vorzeichen folgt wie in Kachel 1 dem Kachelwert"
  - "Stellen und Personalaufwand je Aufgabenbereich liegen in einer ChartCard (h2) mit zwei h3-Diagrammen, damit die Überschriftenhierarchie stimmt; eigener Option-Builder statt horizontaleBalkenOption, weil dessen Achse fest euroKurz formatiert und das rechte Diagramm ohne Namensspalte nötig ist"
  - "Pauschal-/Sonderzeilen stehen am Ende der Gruppenachse (UI-SPEC); in den 2026-Daten gibt es keine"

patterns-established:
  - "Zwei fluchtende Balkendiagramme: gleiche balkenHoehe, gleiche Zeilenreihenfolge, gleiche Gitterränder; das zweite blendet die Namensspalte ab 700 px aus"
  - "Schmal (bis 699 px): Säulenwerte senkrecht (rotate 90) mit mehr Kopfraum statt überlappender Direktwerte"

requirements-completed: [STEL-01, STEL-02, STEL-03]

duration: 40min
completed: 2026-10-06
status: complete

coverage:
  - id: D1
    description: "Drei Stellenkacheln (Haushaltsjahr, Vorjahr, besetzt am Stichtag) mit berechneten Differenzen und PDF-Seiten; Summen in Hundertstel (6291 / 6213 / 5663, Stichtag 2025-06-30)"
    requirement: "STEL-01"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stellen.test.ts#stellenSummen"
        status: pass
    human_judgment: false
  - id: D2
    description: "Gruppierte Säulen je Teil (Haushaltsjahr, Vorjahr, besetzt hohl) mit Textlegende, Nachwuchskräfte-Callout (5 und 6 Personen, S. 290) und VZÄ-Hinweis"
    requirement: "STEL-01"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stellen.test.ts#stellenNachTeil, #nachwuchs"
        status: pass
    human_judgment: true
    rationale: "Darstellung (Säulenreihenfolge, Legende, Lesbarkeit bei 360 px) ist im Node-Testlauf ohne DOM nicht prüfbar"
  - id: D3
    description: "Stellen und Personalaufwand je Aufgabenbereich in zwei fluchtenden Balkendiagrammen; Σ Stellen = 6291, Σ Personalaufwand = 5.204.054 €; kein Aufwand je Stelle"
    requirement: "STEL-02, STEL-03"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stellen.test.ts#stellenNachBereich"
        status: pass
    human_judgment: true
    rationale: "Zeilenfluchtung der beiden Diagramme bei 1280 px und Stapelung bei 360 px sind nur im Browser prüfbar"
  - id: D4
    description: "Stellen je Besoldungs-, Entgelt- und S-Gruppe, sortiert A 8 → B 3, 1 → 14, S 11 → S 12; Summe je Gruppe = Teilsumme = Σ je Aufgabenbereich"
    requirement: "STEL-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stellen.test.ts#stellenNachGruppe"
        status: pass
    human_judgment: true
    rationale: "Glossarlinks und Diagrammdarstellung sind im Browser zu prüfen (Human-Check Task 3)"
---

# Phase 6 Plan 11: Stellenplan Summary

**Seite /stellenplan mit Stellensummen in Hundertstel (62,91 / 62,13 / 56,63 VZÄ), Säulen je Teil, fluchtenden Stellen- und Personalaufwand-Balken je Aufgabenbereich und Säulen je Besoldungs-, Entgelt- und S-Gruppe, ohne jeden Aufwand je Stelle**

## Performance

- **Duration:** ca. 40 min
- **Tasks:** 3 (Tracer, zwei TDD-Aufgaben)
- **Files:** 6 (5 neu, 1 geändert)

## Accomplishments

- `lib/stellen.ts`: `stellenSummen`, `stellenNachTeil`, `nachwuchs`, `stellenNachBereich`, `stellenNachGruppe`, `differenzText`, `alsVzae`, `TEILE`. Alle Summen laufen in ganzen Hundertstel; nur die Merkmale `stellen` und `besetzt` ohne `produktbereich` zählen, `davon_ausgesondert` und Nachwuchs nie. Jahre stammen aus den Daten (kein Jahreswert im Quelltext). Die Datenquelle ist ein optionaler Parameter, damit Tests mutierte Kopien prüfen.
- Pinned 2026: Haushaltsjahr 6291, Vorjahr 6213, besetzt 5663, Stichtag 2025-06-30, Nachwuchs 5 und 6 Personen (S. 290), Σ Aufgabenbereich 6291, Σ Personalaufwand 5.204.054 € (= GESAMT), Gruppenfolgen wie in D-17.
- `StellenNachTeil.vue`: gruppierte Säulen 320 px in fester Reihenfolge, besetzt hohl (`HOHL_FLAECHE`, 2 px Rand), Direktwerte über `vzae()`, Textlegende, Tabelle mit Insgesamt-Zeile.
- `StellenNachBereich.vue`: zwei Balkendiagramme mit gleicher Höhe (`balkenHoehe`), Reihenfolge und Gitterrand, PB-Farben, getrennte Achsen; ab 700 px nebeneinander, das rechte ohne Namensspalte; fehlende Seite zeigt „–“.
- `StellenNachGruppe.vue` (Prop `teil`): Säulen 240 px, rendert bei leerer Liste nichts; die Seite blendet auch die h3 solcher Teile aus.
- `StellenplanPage.vue`: drei Kennzahlkacheln, Karte „Stellen nach Teil des Stellenplans“, Callout mit Nachwuchs und VZÄ-Hinweis (`GlossarBegriff vzae`), Karte „Stellen und Personalaufwand nach Aufgabenbereich“ mit dem Satz zum bewusst nicht berechneten Aufwand je Stelle, Karte „Stellen nach Gruppe“ (`GlossarBegriff entgeltgruppen`).

## Task Commits

1. **Task 1: Tracer, Kacheln und Stellen nach Teil** - `9bceb49` (feat)
2. **Task 2: Stellen und Personalaufwand je Aufgabenbereich** - RED `88431ff` (test), GREEN `c3ae3ae` (feat)
3. **Task 3: Stellen nach Gruppe** - RED `58c3393` (test), GREEN `bbd1fa3` (feat)

**Plan metadata:** folgt als `docs(06-11)`-Commit mit dieser Datei.

## Tracer Gate

Der Tracer (Task 1) wurde mit dem automatisierten `<verify>` (Tests, type-check, lint, format:check) geprüft und bestanden; es gibt kein `<human-check>` im Tracer, daher kein Checkpoint (`HUMAN_VERIFY_MODE` end-of-phase). Die Expansion (Tasks 2 und 3) lief danach.

## TDD Gate Compliance

Task 2: RED `88431ff` (6 Tests scheitern an Behauptungen; `stellenNachBereich` als wirkungsloses Gerüst, das `[]` liefert), GREEN `c3ae3ae` (34 von 34 grün). Task 3: RED `58c3393` (7 Tests scheitern), GREEN `bbd1fa3` (45 von 45 grün). Kein REFACTOR-Commit nötig.

## Deviations from Plan

### Dokumentierte Abweichungen (vom Plan vorgesehen)

**1. Gruppensortierung absteigend nach position** (Nutzerentscheidung 4, RESEARCH Pitfall 7): ergibt 1 → 14, A 8 → B 3, S 11 → S 12 wie D-17 beabsichtigt; der UI-SPEC-Wortlaut „aufsteigend nach position“ wird nicht wörtlich befolgt.

### Auto-fixed Issues

**2. [Rule 1 - Bug-Vermeidung] Vorzeichen der Differenz in Kachel 3**
- **Found during:** Task 1
- **Issue:** Der Plan nennt „+6,28 gegenüber …“ für die Kachel „Besetzt am …“. Besetzt (56,63) liegt aber unter den Stellen des Haushaltsjahrs (62,91); „+6,28“ an dieser Kachel wäre eine falsche Aussage.
- **Fix:** `differenzText(wert, vergleich)` bildet immer Kachelwert minus Vergleich: Kachel 1 „+0,78 gegenüber Stellen {Vorjahr}“, Kachel 3 „−6,28 gegenüber Stellen {Haushaltsjahr}“. Beide tragen `BerechnetEtikett` und die PDF-Seiten.
- **Files modified:** app/src/lib/stellen.ts, app/src/pages/StellenplanPage.vue
- **Commit:** 9bceb49

**3. [Rule 3 - Blocking] Eigener Balken-Builder statt `horizontaleBalkenOption`**
- **Found during:** Task 2
- **Issue:** `horizontaleBalkenOption` formatiert die Wertachse fest mit `euroKurz` und zeigt immer die Namensspalte; das Stellen-Diagramm braucht VZÄ-Achse, das rechte Diagramm ab 700 px keine Namen. `charts/balken.ts` ist nicht in `files_modified` und wird von parallelen Plänen mitgenutzt.
- **Fix:** lokaler Builder in `StellenNachBereich.vue` mit denselben Konstanten (Zeilenhöhe über `balkenHoehe`, Gitterränder, Beschriftung rechts am Balken).
- **Commit:** c3ae3ae

**4. [Rule 2 - Missing Critical] Schmale Bildschirme bei Säulenbeschriftung**
- **Found during:** Task 1 und 3
- **Issue:** Drei Direktwerte je Teil (und bis zu elf Gruppen) überlappen bei 360 px.
- **Fix:** bis 699 px läuft die Beschriftung senkrecht, die Wertachse bekommt mehr Kopfraum.
- **Commit:** 9bceb49, bbd1fa3

**5. [Rule 2 - Missing Critical] Sonderzeilen am Achsenende**
- **Found during:** Task 3
- **Issue:** UI-SPEC verlangt, dass „pauschal“-Zeilen am Ende der Achse stehen; die reine Positionssortierung hätte sie nach vorn gestellt.
- **Fix:** `istSonderzeile` sortiert Gruppen mit Präfix „pauschal“ ans Ende, mit Test an einer Kopie der Daten.
- **Commit:** bbd1fa3

**Total deviations:** 1 dokumentiert, 4 auto-fixed (1 Bug-Vermeidung, 1 blocking, 2 missing critical). **Impact:** alle innerhalb des Plan-Umfangs; kein Scope Creep.

## Issues Encountered

- Linux-Sandbox: die App-Kette (type-check, lint, format:check, test, build) lief in einer Scratch-Kopie mit dem vorhandenen Linux-`node_modules` (kein Netz für `npm ci`, Lockfile identisch). Ergebnis: type-check, lint, format:check grün, 1260 Tests grün, Build grün.
- Der Human-Check aus Task 3 (Dev-Server bei 1280 px und 360 px) konnte nicht laufen, weil die Sandbox keinen Browser hat. Offen für den Abschluss-Walkthrough: Kacheln 62,91 / 62,13 / 56,63 VZÄ, Teil-Säulen mit Legende, Fluchtung der Bereichsdiagramme bei 1280 px und Stapelung bei 360 px, drei Gruppendiagramme in der Reihenfolge 1 → 14, A 8 → B 3, S 11 → S 12, Glossarlinks VZÄ und Gruppen.

## Known Stubs

None.

## Threat Flags

Keine neue Angriffsfläche. T-06-28 (falsche Zahl): Hundertstel-Arithmetik, Dreifach-Summenidentität (Teil = Bereich = Gruppe = 6291), Σ Personalaufwand = GESAMT, Wertpinnung 2026 in `stellen.test.ts`. T-06-29 (Offenlegung): `amtsbezeichnung` wird nirgends gelesen oder gerendert, kein Aufwand je Stelle (ein Test prüft Exporte und Quelltext von `lib/stellen.ts`). T-06-SC: keine neue Abhängigkeit.

## Self-Check: PASSED

- Dateien vorhanden: `app/src/lib/stellen.ts`, `app/src/lib/__tests__/stellen.test.ts`, `app/src/components/StellenNachTeil.vue`, `StellenNachBereich.vue`, `StellenNachGruppe.vue`, `app/src/pages/StellenplanPage.vue`.
- Commits vorhanden: 9bceb49, 88431ff, c3ae3ae, 58c3393, bbd1fa3.
- Akzeptanzkriterien aller drei Tasks erneut geprüft (grep-Kriterien und Testlauf grün).

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
