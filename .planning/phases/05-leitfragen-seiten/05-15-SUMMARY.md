---
phase: 05-leitfragen-seiten
plan: 15
subsystem: ui
tags: [vue, glossar, vitest, quelltext-scan, phase-gate]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-13 GlossarBegriff mit typisiertem Schlüssel und Verwendungsscan, 05-07 bis 05-14 die fünf Inhaltsseiten"
provides:
  - "GlossarBegriff im Fließtext von Start, Einnahmen, Ausgaben, Geldfluss und Produkt (alle 13 Pflichtschlüssel plus produktbereich)"
  - "quelltext.test.ts: Seitenabdeckung der Glossarverlinkung, Template-Scan auf getippte Zahlen und Roh-HTML-Direktive mit Fail-first-Proben"
  - "Grüner Phasen-Gate: pytest, ruff, alle.py reproduzierbar, App-Kette (type-check, lint, format:check, test, build)"
affects: [phase-06, phase-07]

actuals:
  tokens: 3000
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Quelltext-Scan über import.meta.glob(?raw): templateTeil und getippteZahlen, Direktivenname aus zwei Teilen gebaut"
    - "Glossarverweis als zahlenfreier Hinweissatz neben dem erklärten Inhalt (Klasse om-*-hinweis)"

key-files:
  created:
    - app/src/lib/__tests__/quelltext.test.ts
  modified:
    - app/src/pages/StartPage.vue
    - app/src/pages/EinnahmenPage.vue
    - app/src/pages/AusgabenPage.vue
    - app/src/pages/GeldflussPage.vue
    - app/src/pages/ProduktPage.vue

key-decisions:
  - "Der Zuschussbedarf-Hinweis der Ausgaben-Ansicht wandert vom hint-Attribut in den hint-Slot der wa-radio-group (mit with-hint), weil ein Attribut keine Komponente tragen kann."
  - "Glossarverweise stehen als kurze, zahlenfreie Sätze (Was X ist, erklärt das Glossar) neben dem erklärten Inhalt statt in datengetriebenen Texten, damit Daten und Erklärtexte unverändert bleiben."
  - "Der Scan prüft nur das Template; CSS-Werte und Skript bleiben außen vor. Es war keine Anpassung an Bestandsdateien nötig."

patterns-established:
  - "GlossarBegriff in Hinweissätzen: <GlossarBegriff schluessel=\"x\">Text</GlossarBegriff> mit Union-Typ und Verwendungsscan als Absicherung"

requirements-completed: [GLOS-03, UI-05]

coverage:
  - id: D1
    description: "Alle fünf Inhaltsseiten verlinken Glossarbegriffe im Fließtext; zusammen sind die 13 Pflichtschlüssel abgedeckt"
    requirement: GLOS-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#Glossarverlinkung auf den Inhaltsseiten"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/glossar.test.ts#Verwendungsprüfung aller .vue-Dateien"
        status: pass
    human_judgment: false
  - id: D2
    description: "Tooltip bei Hover und Tastaturfokus sowie Sprung zum Glossarbegriff von jeder Inhaltsseite"
    requirement: GLOS-03
    verification: []
    human_judgment: true
    rationale: "Browserverhalten (Tooltip, Fokus, Hash-Sprung); keine DOM-Tests im Projekt (vitest environment node)"
  - id: D3
    description: "Keine getippten Beträge, Prozente, gruppierten Zahlen oder Roh-HTML-Direktiven in den Templates; Zahlen kommen nur aus Daten über format.ts"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#Keine getippten Zahlen in den Templates"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#getippteZahlen (UI-05, Fail-first)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Phasen-Gate: pytest, ruff, alle.py ohne Diff, App-Kette inklusive build"
    verification:
      - kind: other
        ref: "uv run --directory pipeline pytest -q (515 passed inkl. test_port_wie_format_ts mit temporärem node_modules-Symlink)"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (git diff und git status leer)"
        status: pass
      - kind: other
        ref: "npm run type-check, lint, format:check, test (1005 Tests), build im Scratch-Copy"
        status: pass
    human_judgment: false
  - id: D5
    description: "End-of-phase-Rundgang aller Phase-5-Seiten bei 1280 px und 360 px im Browser"
    verification: []
    human_judgment: true
    rationale: "Im Sandbox ist kein Browser verfügbar; Layout, Fokus, Diagramme und Tooltips brauchen menschliche Sicht (siehe Abschnitt Offene Menschenprüfung)"

duration: 11min
completed: 2026-10-04
status: complete
plan_head_before: c236ef41f32e969510120b67417275240c18fbf7
plan_head_after: 72121d94df1dd0dcd50e0a1e87d2ff5d3f60bcaa
commits: 3
---

# Phase 5 Plan 15: Glossarverlinkung und Quelltext-Gate Summary

**GlossarBegriff-Links im Fließtext aller fünf Inhaltsseiten (alle 13 Pflichtbegriffe plus Produktbereich), ein Template-Scan, der getippte Zahlen und Roh-HTML-Direktiven in jeder .vue-Datei ausschließt, und ein grüner Phasen-Gate über Pipeline, Reproduzierbarkeit und App-Kette.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-04T14:03:58Z
- **Completed:** 2026-10-04T14:15:00Z
- **Tasks:** 2 (Task 1 Tracer, Task 2 TDD mit RED- und GREEN-Commit)
- **Files modified:** 6 (1 neu, 5 geändert)

## Accomplishments

- Start: Hinweissatz unter „Die wichtigsten Zahlen“ mit Ergebnisplan, Erträge und Aufwendungen, Finanzplan.
- Einnahmen: Hebesatz im Steuern-Hinweis; Schlüsselzuweisungen und Sonderposten im Zuwendungen-Aufklapper.
- Ausgaben: Zuschussbedarf im Hinweis der Ansichtsumschaltung, Produktbereich über der Brotkrume, Kreisumlage unter dem Kreisumlage-Callout, globaler Minderaufwand in seinem Callout, Transferaufwendungen und Abschreibungen an der Aufwandsart-Karte.
- Geldfluss: Ergebnisplan und globaler Minderaufwand in der Lesehilfe.
- Produkt: Produkt unter der Überschrift (PageIntro-Slot), Bindungsgrad in „Auf einen Blick“.
- `quelltext.test.ts`: Seitenabdeckung (je Seite mindestens eine Verwendung, Vereinigung enthält die 13 Pflichtschlüssel), `templateTeil`, `getippteZahlen`, Fail-first-Proben (u. a. „4,5 Mio. €“, „2.594“, „12 %“, „3€“), Per-Datei-Scan über alle Vue-Dateien.
- Phasen-Gate grün (siehe Verification).

## Task Commits

1. **Task 1: Tracer, Glossarverlinkung und Abdeckungstest** - `86ce67e` (feat; Test zuerst: 6 Tests scheiterten an Behauptungen, danach grün)
2. **Task 2 RED: Template-Scan mit Stub-Helfern** - `a26307a` (test; 9 Tests scheitern an Behauptungen, die Stubs liefern leer)
3. **Task 2 GREEN: templateTeil und getippteZahlen** - `72121d9` (feat; 53 Tests grün, kein Befund in den echten Templates)

Kein REFACTOR-Commit nötig. Tracer-Gate: die automatische Verifikation (Scan, Glossartests, type-check, lint, format:check, build) lief nach dem Commit grün, die Erweiterung wurde danach gestartet.

## Files Created/Modified

- `app/src/lib/__tests__/quelltext.test.ts` - Seitenabdeckung, Template-Scan, Fail-first-Proben
- `app/src/pages/StartPage.vue` - Hinweissatz mit drei Glossarbegriffen, Klasse `om-start__hinweis`
- `app/src/pages/EinnahmenPage.vue` - Hebesatz, Schlüsselzuweisung, Sonderposten
- `app/src/pages/AusgabenPage.vue` - sechs Begriffe, `hint`-Slot, Klasse `om-ausgaben-hinweis`
- `app/src/pages/GeldflussPage.vue` - Ergebnisplan, globaler Minderaufwand in der Lesehilfe
- `app/src/pages/ProduktPage.vue` - Produkt (Intro-Slot), Bindungsgrad

## Decisions Made

Siehe `key-decisions` im Frontmatter.

## Deviations from Plan

None - plan executed exactly as written.

Anmerkung: Der Plan nennt „Transferaufwendungen und Abschreibungen at the Aufwandsart card“ ohne Position; sie stehen als Hinweissatz unter dem Diagramm der Karte. „Produktbereich in the breadcrumb hint“ steht als Satz über der Brotkrume (Brotkrumen.vue gehört nicht zu den Plan-Dateien).

## Verification

- `uv run --directory pipeline pytest -q`: 514 passed, 1 skipped (Sandbox ohne app/node_modules); der übersprungene Test `test_port_wie_format_ts` lief separat mit temporärem Symlink auf das Scratch-`node_modules` grün (also 515 passed), Symlink wieder entfernt.
- `ruff check .` und `ruff format --check .`: sauber.
- `alle.py --jahr 2026`: Exit 0, kein „Fehler:“, `git diff` und `git status` leer (daten und app/src/data byte-identisch); `Gesamtstatus: grün` in `daten/pruefberichte/konsistenz.md`.
- App-Kette im Scratch-Copy (`npm ci` aus dem Lockfile): type-check, lint, format:check, test (23 Dateien, 1005 Tests), build grün.

## Issues Encountered

None.

## Übergabe an Phase 7

- **Platzhalter-Konfiguration (D-17):** `app/src/config.ts` führt Kontakt-E-Mail und Original-PDF-URL noch als Platzhalter; `istPlatzhalter` (getestet in `config.test.ts`) erkennt sie an der Endung `.invalid`. Vor dem Livegang müssen echte Werte eingetragen werden, sonst zeigen Footer und Quellenverweise Platzhalter.
- **Backstop-Wahrheiten der UI-SPEC für den Smoke-Test:**
  - Lade- und Fehlerzustände: laut UI-SPEC verworfen (statische JSON-Importe); im Smoke-Test nur bestätigen, dass kein Seitenwechsel einen leeren Zustand zeigt.
  - Farbkonsistenz: dieselbe Wertart/Kategorie trägt auf Einnahmen, Ausgaben und Geldfluss dieselbe Farbe (Quelle ausschließlich `echartsTheme.ts`).
  - Summenkonsistenz Sankey und Balken: die Summen von Sankey (Desktop) und Balkenansicht (Mobil) für dasselbe Jahr stimmen überein, auch mit globalem Minderaufwand links.
  - E13 partial: Glossar-Langtexte und lange Begriffe brechen nur an Leerzeichen (gepunktete Unterstreichung bleibt lesbar), Tooltips bleiben bei 360 px im Viewport.
  - Tastaturbedienung: jede Diagramminteraktion ist über Tabellen oder Schaltflächen erreichbar, der Fokus ist überall sichtbar.

## Offene Menschenprüfung (pending, human_judgment)

Im Sandbox ist kein Browser verfügbar. Auf dem Host: einmal `npm --prefix app ci` (macOS), dann `npm --prefix app run dev`, geprüft bei 1280 px und 360 px; Befunde je Seite berichten.

- **Start (`#/`):** sieben Kennzahlen 2026 (27,5 Mio. € · 30,5 Mio. € · -2,35 Mio. € Defizit · 12,3 Mio. € · 5,2 Mio. € · 2.594 € · 1.571 €), zwei Einstiegskacheln, Kreisumlage-Hinweis; neuer Hinweissatz mit Ergebnisplan, Erträge und Aufwendungen, Finanzplan liest sich flüssig und umbricht bei 360 px.
- **Einnahmen:** Jahr-Umschalter, Aufklapper (Steuern offen), Hebesatz-Link im Hebesatz-Satz, Satz mit Schlüsselzuweisungen und Sonderposten im Zuwendungen-Aufklapper, Zeitreihe, investiver Block.
- **Ausgaben:** Drill-down zu einem Produkt und zurück; Hinweis der Ansicht (Zuschussbedarf-Link im `hint`-Slot, korrekt unter der Radiogruppe, Tastatur und Screenreader); Satz zu Produktbereichen über der Brotkrume; Zuschussbedarf mit Überschüssen; Aufwandsart-Karte mit Satz zu Transferaufwendungen und Abschreibungen; Kreisumlage-Callout mit Glossarsatz; Minderaufwand-Callout mit verlinkter Überschrift.
- **Geldfluss:** Sankey (Minderaufwand links) und mobile Balken; Lesehilfe mit neuem Satz zu Ergebnisplan und globalem Minderaufwand.
- **Produkt:** Satz „Ein Produkt ist eine Leistung der Gemeinde“ im Kopf, Bindungsgrad-Link in „Auf einen Blick“.
- **Glossar:** Begriffe, Sprunglinks, Produktakkordeon; GlossarBegriff-Links von jeder Inhaltsseite landen auf dem richtigen Begriff mit sichtbarem Fokus.
- **Querschnitt:** GlossarBegriff-Tooltips bei Hover und Tastaturfokus (Escape schließt), Header-Menü und Drawer, Skip-Link, Footer; nur Tastatur: jede Diagramminteraktion über Tabellen oder Schaltflächen erreichbar, Fokus immer sichtbar.

## Known Stubs

None. Die Platzhalter-Konfiguration (`config.ts`) stammt aus Plan 05-12 und ist unter „Übergabe an Phase 7“ vermerkt.

## Threat Flags

None. Keine neue Abhängigkeit, kein Netzwerkzugriff, keine neue Vertrauensgrenze; T-05-40 und T-05-41 sind durch den Template-Scan, T-05-42 durch Union-Typ und Verwendungsscan mitigiert.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 5 ist inhaltlich vollständig; die Phasenabnahme braucht den Browser-Rundgang (siehe oben) und die Verifier-UAT-Punkte.
- Phase 7 übernimmt Platzhalter-Werte und Smoke-Test-Backstops (siehe Übergabe).

## Self-Check: PASSED

- `quelltext.test.ts` und alle fünf Seitendateien vorhanden; Commits 86ce67e, a26307a, 72121d9 vorhanden.
- Akzeptanzkriterien beider Tasks erfüllt (GlossarBegriff je Seite, vitest-Ausgabe mit quelltext.test.ts und glossar.test.ts, ruff sauber, Gesamtstatus grün, Abschnitt „Übergabe an Phase 7“ vorhanden).

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
