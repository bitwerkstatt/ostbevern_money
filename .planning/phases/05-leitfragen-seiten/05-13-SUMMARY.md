---
phase: 05-leitfragen-seiten
plan: 13
subsystem: ui
tags: [vue, glossar, web-awesome, wa-tooltip, wa-details, vitest]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-03 texte.glossar, 05-04 Routen und Hash-Fokus, 05-06 rendereAbsatz"
provides:
  - "lib/glossar.ts: GLOSSAR_SCHLUESSEL, GlossarSchluessel, glossarBegriffe, findeBegriff, ersterSatz, produktGruppen, glossarVerwendungen"
  - "GlossarListe, GlossarBegriff (wiederverwendbar, Plan 05-15), ProduktAkkordeon"
  - "Vollständige /glossar-Seite mit Sprunglinks, 24 Begriffen und 63 Produkten"
affects: [05-15, phase-06]

actuals:
  tokens: 5436
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Schlüssel-Union aus const-Tupel, durch Mengengleichheitstest gegen die Pipeline-Daten abgesichert"
    - "Verwendungsprüfung per import.meta.glob mit ?raw über alle .vue-Dateien"
    - "Router-Fokus auf Section wird per @focus an die h3 weitergereicht"

key-files:
  created:
    - app/src/lib/glossar.ts
    - app/src/lib/__tests__/glossar.test.ts
    - app/src/components/GlossarListe.vue
    - app/src/components/GlossarBegriff.vue
    - app/src/components/ProduktAkkordeon.vue
  modified:
    - app/src/pages/GlossarPage.vue

key-decisions:
  - "Der Router (05-04) fokussiert das Element mit der Fragment-ID, also die Section. GlossarListe reicht diesen Fokus per @focus an die h3 (tabindex -1) weiter, damit die Überschrift fokussiert ist und den 2-px-Rahmen trägt."
  - "Sprunglinks und GlossarBegriff setzen aria-current-value=false: Der Router ignoriert das Fragment beim exact-active-Vergleich, sonst wäre auf /glossar jeder Link 'aktuelle Seite'."
  - "produktGruppen leitet Gruppen aus produkt.pb ab und ordnet sie nach der Reihenfolge der Produktbereiche in haushalt.knoten; unbekannte Bereiche stehen am Ende, damit kein Produkt fehlt."

patterns-established:
  - "GlossarBegriff-Verwendung: <GlossarBegriff schluessel=\"hebesatz\">Text</GlossarBegriff>, Prüfung durch Typ und glossar.test.ts"

requirements-completed: [GLOS-01, GLOS-02, GLOS-03]

coverage:
  - id: D1
    description: "/glossar listet alle 24 Begriffe alphabetisch (Intl.Collator de) mit Anker, h3, Definition und Seitenverweis"
    requirement: GLOS-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/glossar.test.ts#glossarBegriffe"
        status: pass
    human_judgment: false
  - id: D2
    description: "Sprunglink-Navigation und /glossar#schluessel scrollt und fokussiert die Überschrift; unbekannter Hash bleibt oben"
    requirement: GLOS-01
    verification: []
    human_judgment: true
    rationale: "Scroll-, Fokus- und Layoutverhalten im Browser; keine DOM-Tests im Projekt (vitest environment node)"
  - id: D3
    description: "Produktakkordeon: 63 Produkte genau einmal in datengetriebenen Gruppen, alle geschlossen"
    requirement: GLOS-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/glossar.test.ts#produktGruppen"
        status: pass
    human_judgment: true
    rationale: "Geschlossen-Zustand, 44-px-Trefferflächen und Umbruch sind visuell zu prüfen"
  - id: D4
    description: "GlossarBegriff mit typisiertem Schlüssel, gepunkteter Unterstreichung und Tooltip mit erstem Definitionssatz; Verwendungsprüfung"
    requirement: GLOS-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/glossar.test.ts#Verwendungsprüfung aller .vue-Dateien"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/glossar.test.ts#GLOSSAR_SCHLUESSEL"
        status: pass
    human_judgment: true
    rationale: "Tooltip bei Hover/Fokus und Schließen per Escape ist Browserverhalten"

duration: 12min
completed: 2026-10-04
status: complete
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: 888684605678564e835349313bbc1d7c078dc879
commits: 3
---

# Phase 5 Plan 13: Glossar und Produktakkordeon Summary

**Vollständige /glossar-Seite: 24 Begriffe in deutscher Sortierung mit Sprunglinks und Ankern, die wiederverwendbare Komponente GlossarBegriff mit typgeprüftem Schlüssel und Tooltip, und ein Akkordeon der 63 Produkte in 15 datengetriebenen Aufgabenbereichen.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-10-04T13:14:00Z
- **Completed:** 2026-10-04T13:26:40Z
- **Tasks:** 2 (Task 2 als TDD mit RED- und GREEN-Commit)
- **Files modified:** 6 (5 neu, 1 geändert)

## Accomplishments
- `lib/glossar.ts`: Schlüssel-Tupel mit Union-Typ (Mengengleichheit zu `texte.glossar` in beide Richtungen getestet), Sortierung per `Intl.Collator('de')`, `findeBegriff` über Map, `ersterSatz` mit Abkürzungsschutz.
- `GlossarListe` + `GlossarPage`: Section je Begriff (id = Schlüssel), h3 mit tabindex -1, Definition als Text (kein v-html), Seitenverweis, `scroll-margin-top`, Sprung-Navigation `aria-label="Begriffe"` mit 44-px-Zielen.
- `GlossarBegriff`: RouterLink auf `{ name: 'glossar', hash }`, gepunktete Unterstreichung mit 4 px Abstand, `wa-tooltip` mit dem ersten Definitionssatz.
- `ProduktAkkordeon`: 15 äußere und 63 innere `wa-details` (im SSR-Smoke-Test gezählt: 78 `wa-details`, 25 `section`), Link „Produkt öffnen“, Produkte ohne Beschreibung zeigen nur den Link.
- Verwendungsprüfung: Test scannt alle `.vue`-Dateien unter `src` per `import.meta.glob(?raw)` und prüft jeden `GlossarBegriff`-Schlüssel gegen das Tupel; ein untergeschobener Schlüssel wird erkannt.

## Task Commits

1. **Task 1: Tracer Glossar end-to-end** - `a93c8b3` (feat)
2. **Task 2 RED: failing tests Produktgruppen und Verwendungsprüfung** - `30b51b9` (test; 6 Tests scheitern an Behauptungen, leere Funktionsrümpfe)
3. **Task 2 GREEN: GlossarBegriff, Produktakkordeon, Verwendungsprüfung** - `8886846` (feat)

Kein REFACTOR-Commit nötig.

## Files Created/Modified
- `app/src/lib/glossar.ts` - Schlüssel, Sortierung, erster Satz, Produktgruppen, Verwendungsregex
- `app/src/lib/__tests__/glossar.test.ts` - 25 Tests inkl. Verwendungsscan
- `app/src/components/GlossarListe.vue` - alphabetische Liste mit Ankern
- `app/src/components/GlossarBegriff.vue` - Inline-Link mit Tooltip
- `app/src/components/ProduktAkkordeon.vue` - Produkte nach Aufgabenbereich
- `app/src/pages/GlossarPage.vue` - Seite: PageIntro, Sprungleiste, Liste, Divider, „Alle Produkte“

## Decisions Made
Siehe `key-decisions` im Frontmatter. Keine Web-Awesome-Imports ergänzt: `details`, `tooltip` und `divider` sind in `main.ts` bereits importiert; `main.ts`, Router und `echartsTheme.ts` blieben unangetastet.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fokus landete auf der Section statt auf der Überschrift**
- **Found during:** Task 1
- **Issue:** Der Router fokussiert das Element mit der Fragment-ID (die Section); die Truth verlangt Fokus auf die Überschrift.
- **Fix:** `@focus` an der Section reicht den Fokus an die h3 weiter (`preventScroll`, nur wenn die Section selbst das Ziel ist).
- **Files modified:** app/src/components/GlossarListe.vue
- **Committed in:** a93c8b3

**2. [Rule 1 - Bug] Alle Sprunglinks trugen aria-current="page"**
- **Found during:** Task 2 (SSR-Smoke-Test der Seite)
- **Issue:** Der Router vergleicht das Fragment nicht; auf `/glossar` war jeder Link „exact-active“ und wurde als aktuelle Seite angesagt.
- **Fix:** `aria-current-value="false"` an den Sprunglinks und in `GlossarBegriff`.
- **Files modified:** app/src/pages/GlossarPage.vue, app/src/components/GlossarBegriff.vue
- **Committed in:** 8886846

**3. [Rule 1 - Bug] Falsche Erwartung im eigenen Kollationstest**
- **Found during:** Task 1
- **Issue:** `compare('Äpfel','Arbeit') > 0` war falsch (p < r auf Primärebene).
- **Fix:** Test nutzt `'Äpfel' < 'Zebra'` (Codepunkt: false) gegenüber `compare(...) < 0` und `Ärger` vs. `Arbeit`.
- **Committed in:** a93c8b3

---

**Total deviations:** 3 auto-fixed (3 Rule 1). **Impact:** Alle drei korrigieren Korrektheit bzw. Barrierefreiheit, kein Scope-Zuwachs.

## Issues Encountered
- Der RED-Stand nutzt leere Funktionsrümpfe in `glossar.ts` (im RED-Commit), damit die Tests an Behauptungen statt am Import scheitern. Kein `gsd_run check tdd-red-evidence` (Plan ist nicht `type: tdd`).
- Das Menschenprüf-Item aus dem Plan (Sprunglinks, `#gibtesnicht`, Akkordeon im Browser) ist hier nicht ausführbar (keine Host-Browserumgebung) und bleibt für die Phasenabnahme offen.

## Known Stubs
None.

## Threat Flags
None. Fragment wird nur vom Router als `getElementById` genutzt (T-05-35); Definitionen und Tooltips ausschließlich per Textinterpolation, kein `v-html` (T-05-36); keine neue Abhängigkeit (T-05-SC).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 05-15 kann `GlossarBegriff` auf den anderen Seiten einsetzen; `glossar.test.ts` prüft die Schlüssel automatisch mit.
- Offen für die Phasenabnahme: Browsercheck von Sprunglinks, unbekanntem Hash und Akkordeon.

## Self-Check: PASSED
- Alle 6 Dateien vorhanden, Commits a93c8b3, 30b51b9, 8886846 vorhanden.
- Scratch-Kette (vitest 163 Tests, type-check, lint, format:check, build) grün; alle Akzeptanzkriterien beider Tasks erfüllt.

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
