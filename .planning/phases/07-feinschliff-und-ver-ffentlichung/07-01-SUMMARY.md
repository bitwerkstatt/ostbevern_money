---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 01
subsystem: quellenbelege
tags: [pdfplumber, pypdfium2, pillow, webp, vue, web-awesome, wa-drawer, playwright, a11y]

requires:
  - phase: 04-manuelle-daten-und-app-daten
    provides: "app_daten.schreibe_app_json, APP_DATEN_WURZEL, haushalt.json mit zeilen_namen und meta"
  - phase: 05-leitfragen-seiten
    provides: "KennzahlKachel, Start-Kacheln, DatenTabelle, bildschirm.ts, Menue-Drawer-Muster in App.vue"
provides:
  - "Schritt 08 (pipeline/08_quellenbelege.py, ostbevern/quellen.py, belegbilder.py): Zeilensuche mit Betrags-Gegenprobe, WebP-Seiten, quellen.json"
  - "app/src/data/quellen.json (haushaltsjahr, seiten, belege) fuer alle 74 GESAMT-Plan-Zeilen, Seiten 62 und 63 als WebP"
  - "lib/quelle.ts: vollstaendige Schluesselgrammatik, findeBeleg, bboxProzent, bildUrl, belegHinweis, originalSeitenUrl, quellAltText, Zustand der einen globalen Seitenleiste"
  - "QuelleKnopf, QuelleSeitenleiste, QuelleSeite; KennzahlKachel-Props quelle, herleitung, wertart; DatenTabelle-Spaltenart quelle"
  - "Playwright-Infrastruktur (ci, mobil, texte) und e2e/quelle.spec.ts"
affects: [07-03, 07-06, 07-07, 07-08, 07-09, 07-10, 07-11]

actuals:
  tokens: 30000
  tasks: 3
  commits: 5

tech-stack:
  added: ["pypdfium2 >=5.14.0", "Pillow >=12.3.0", "@playwright/test 1.63.0", "@axe-core/playwright 4.13.0"]
  patterns:
    - "Schluesselgrammatik identisch in Python (quellen.py Docstring) und TypeScript (belegSchluessel)"
    - "Eine globale wa-drawer-Instanz in App.vue, Zustand modulweit in lib/quelle.ts, Ausloeser aus event.currentTarget"
    - "Beleg nur wenn bbox ueber Zeilennummer und Haushaltsjahrbetrag eindeutig, sonst null mit Grund"
    - "Accessible Name per aria-label statt versteckter Textspanne"

key-files:
  created:
    - pipeline/ostbevern/quellen.py
    - pipeline/ostbevern/belegbilder.py
    - pipeline/08_quellenbelege.py
    - pipeline/tests/test_quellen.py
    - app/src/data/quellen.json
    - app/public/quellen/s062.webp
    - app/public/quellen/s063.webp
    - app/public/icons/solid/file-lines.svg
    - app/src/lib/quelle.ts
    - app/src/lib/__tests__/quelle.test.ts
    - app/src/components/QuelleKnopf.vue
    - app/src/components/QuelleSeitenleiste.vue
    - app/src/components/QuelleSeite.vue
    - app/playwright.config.ts
    - app/tsconfig.e2e.json
    - app/e2e/quelle.spec.ts
  modified:
    - pipeline/ostbevern/pdf.py
    - pipeline/pyproject.toml
    - pipeline/uv.lock
    - app/src/data/typen.ts
    - app/src/data/daten.ts
    - app/src/lib/kennzahlen.ts
    - app/src/pages/StartPage.vue
    - app/src/components/KennzahlKachel.vue
    - app/src/components/DatenTabelle.vue
    - app/src/components/datenTabelle.ts
    - app/src/styles/basis.css
    - app/src/App.vue
    - app/.prettierignore
    - app/.gitignore
    - app/package.json
    - app/package-lock.json
    - app/tsconfig.json

key-decisions:
  - "quellen.json-Schluessel fuer GESAMT-Zeilen: ep:GESAMT:{zeile_kanonisch} und fp:GESAMT:{zeile_kanonisch}, Knotencode aus der Ebene GESAMT (die CSV-Spalte code ist dort leer)"
  - "Haushaltsjahr-Spalte aus jahrgang.spalten per zerlege_spaltenkopf (Jahr gleich Haushaltsjahr, Wertart nicht ve), nie als Literal"
  - "Der Seitenleisten-Fokus beim Oeffnen bleibt der Web-Awesome-Standard (benannter Dialog, Schliessen-Knopf erster Tab-Stopp); die UI-SPEC-Aussage wird im Checkpoint 07-10 neu bewertet"
  - "Der zugaengliche Name des Quelle-Knopfs ist ein aria-label, weil Chromium vor einer absolut positionierten versteckten Spanne ein Leerzeichen einfuegt"
  - "Eine Kachel mit berechnetem Wert nennt die Herleitung aus haushalt.zeilen_namen und meta.einwohner.quelle; Tabellenzeilen koennen sie ueber das Zeilenfeld {spalte}Herleitung mitgeben"

patterns-established:
  - "Pflicht fuer Konsumenten (07-06 bis 07-08): Schluessel nur ueber belegSchluessel bauen, Knopf ueber QuelleKnopf, in Tabellen eine Spalte art quelle mit Titel Quelle"
  - "Die Seitenleiste laedt das Bild nur im geoeffneten Zustand (v-if auf der Anfrage) und rendert die Markierung erst nach dem Laden des Bildes"

requirements-completed: [DATA-04, UI-02, A11Y-02]

coverage:
  - id: D1
    description: "Schritt 08 schreibt quellen.json fuer alle GESAMT-Zeilen des Ergebnis- und Finanzplans mit eindeutigen Zeilenrechtecken (74 Belege, 0 ohne Markierung), deterministisch"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_quellen.py (25 Tests, u. a. test_quellen_json_eingecheckt_aktuell, test_jede_gesamtzeile_hat_einen_beleg)"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python 08_quellenbelege.py --jahr 2026 zweimal, sha256sum -c"
        status: pass
    human_judgment: false
  - id: D2
    description: "bbox von ep:GESAMT:ordentliche_ertraege liegt auf PDF-Seite 62 und umschliesst Zeilennummer und Haushaltsjahrbetrag der gedruckten Zeile 10"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_quellen.py#test_ordentliche_ertraege_bbox_enthaelt_zeilennummer_und_betrag"
        status: pass
      - kind: e2e
        ref: "app/e2e/quelle.spec.ts (Marker sichtbar und innerhalb des Bildes)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Belegbilder: WebP Qualitaet 60, 2 px je Punkt, Pixelmasse gleich 2 x Seitenmass, nur fehlende Seiten werden gerendert, Produktinformationen-Seiten nur mit Schwaerzung"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_quellen.py (Bildmasse, Seitenmass pdfplumber gleich pdfium fuer S. 62, 63, 291, 311, BelegbildFehler-Wache, Schwaerzung)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Sieben Start-Kacheln zeigen Quelle anzeigen, der Klick oeffnet die Seitenleiste mit Wertzeile, Hinweis, Original-Link und markierter Seite; Escape, Schliessen-Knopf und Klick daneben geben den Fokus an den Ausloeser zurueck"
    requirement: "UI-02"
    verification:
      - kind: e2e
        ref: "app/e2e/quelle.spec.ts (6 Tests im Docker-Image playwright:v1.63.0-noble)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/quelle.test.ts (35 Tests)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Hinweise (D-03), Ladeskelett, Ladefehler-Callout, Breiten, Markierungsdarstellung und Scrollen zur Zeile sehen so aus wie in der UI-SPEC"
    requirement: "UI-02"
    verification:
      - kind: e2e
        ref: "app/e2e/quelle.spec.ts (Ladefehler, berechneter Wert, Original-Link)"
        status: pass
    human_judgment: true
    rationale: "Optik (Abstaende, Typografie, Lesbarkeit der Markierung auf Hoch- und Querformat, 360 px) ist nur im Screenshot beurteilbar; zwei Screenshots wurden gesichtet, die Abnahme am Checkpoint 07-10 bleibt"
  - id: D6
    description: "DatenTabelle-Spaltenart quelle: Knopf PDF-Seite {n} je belegter Zeile, leere Zelle ohne Beleg, Spalte entfaellt ohne einen aufloesbaren Beleg"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle.test.ts (sichtbareSpalten und Server-Rendering von DatenTabelle)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Bei prefers-reduced-motion: reduce sind die Web-Awesome-Uebergangs-Tokens und die Drawer-Dauern 0"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/quelle.spec.ts (emulateMedia reducedMotion)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Playwright 1.63.0 und axe-core/playwright 4.13.0 exakt gepinnt, npm run test:e2e startet das Projekt ci"
    verification:
      - kind: other
        ref: "npm ci in sauberer Scratch-Kopie, docker run playwright test --project=ci e2e/quelle.spec.ts (6 passed)"
        status: pass
    human_judgment: false

duration: 60min
completed: 2026-10-06
status: complete
plan_head_before: e0a91c5c974c1469646175280212ef7f381d6931
plan_head_after: fdab3d51e78c8fdfa2436fae9d78c1c86ab2137e
---

# Phase 7 Plan 01: Quellenbelege-Tracer, Seitenleiste und Playwright Summary

**Schritt 08 findet die 74 Zeilen von Gesamtergebnis- und Gesamtfinanzplan im PDF (Zeilennummer plus Betrags-Gegenprobe), rendert S. 62/63 als WebP und schreibt quellen.json; eine globale wa-drawer-Seitenleiste zeigt die Seite mit markierter Zeile, die sieben Start-Kacheln und DatenTabelle-Zeilen bekommen den Knopf "Quelle anzeigen", Playwright beweist den Pfad im Browser.**

## Performance

- **Duration:** 60 min
- **Started:** 2026-10-06T10:42:00Z (geschaetzt)
- **Completed:** 2026-10-06T11:43:00Z
- **Tasks:** 3 (Task 2 als TDD mit RED- und GREEN-Commit)
- **Files modified:** 34 (inkl. 2 WebP und quellen.json)

## Accomplishments

- **Pipeline:** `PdfDokument.zeilen_mit_rahmen` und `seitenmass` (pdfplumber bleibt nur in pdf.py), `belegbilder.py` als einzige Stelle fuer pypdfium2 und Pillow, `quellen.py` mit `finde_planzeile`, `bbox_mit_rand` und `erzeuge_quellen`, typer-Einstieg `08_quellenbelege.py` mit `--jahr` und `--neu-rendern`. Alle 74 GESAMT-Zeilen haben ein Rechteck, zweiter Lauf ist byte-identisch.
- **Datenschutz-Wache:** Eine Seite vom Typ `produktinformationen` wird ohne Schwaerzungsrechtecke nie gerendert (`BelegbildFehler`, vor dem ersten Schreiben).
- **App:** `lib/quelle.ts` mit der vollstaendigen Schluesselgrammatik (Konsumentenplaene muessen nur noch aufrufen), `QuelleKnopf`, `QuelleSeitenleiste`, `QuelleSeite`, Herleitungstexte der vier berechneten Kennzahlen aus den Daten, `DatenTabelle` mit `art: 'quelle'`.
- **A11Y-02:** Reduzierte Bewegung nimmt Web-Awesome-Uebergaenge und Drawer-Dauern auf 0.
- **Tests:** 25 pytest (Suchlogik, Containment, Seitenmasse, Bildmasse, Wache), 35 vitest in quelle.test.ts (davon Server-Rendering von QuelleKnopf und DatenTabelle), 6 Playwright-Tests im Docker-Image.

## Task Commits

1. **Task 1: Tracer GESAMT-Planzeile bis Seitenleiste** - `a51a33e` (feat), plus `bf0c7b1` (fix: aria-label des Knopfs)
2. **Task 2: Seitenleiste vollstaendig und Spalte Quelle (TDD)** - RED `ba34d7d` (test), GREEN `c45ae56` (feat)
3. **Task 3: Playwright-Infrastruktur und Tracer-Browsertest** - `fdab3d5` (chore)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md)

## TDD Gate Compliance (Task 2)

- **RED:** `ba34d7d`, Ziel-Test "nennt bei vorhandenem Rechteck nur den Markierungshinweis" scheiterte mit `TypeError: belegHinweis is not a function`, zehn Tests insgesamt rot. `gsd_run check tdd-red-evidence` lieferte `RED_EVIDENCE_OK` (Format tap, `target_test_failed`). Semantische Bewertung: der Test lief und scheiterte an der geplanten, noch nicht exportierten Funktion, nicht an Syntax, Import oder Fixture.
- **GREEN:** `c45ae56`, alle 1623 vitest-Tests gruen.
- **REFACTOR:** nicht noetig.

## Files Created/Modified

Siehe Frontmatter `key-files`. Kerndateien: `pipeline/ostbevern/quellen.py` (Suche, Schluessel, JSON), `pipeline/ostbevern/belegbilder.py` (Rendern, Wache), `app/src/lib/quelle.ts` (Grammatik, Zustand, reine Funktionen), `app/src/components/QuelleSeitenleiste.vue` (globaler Drawer), `app/e2e/quelle.spec.ts` (Browserbeweis).

## Decisions Made

Siehe `key-decisions`. Zusaetzlich: Das Markierungselement liegt in einem inneren "Blatt" (Breite `max(100%, --om-seite-breite)`), nicht direkt im scrollenden Rahmen, weil die Prozentwerte sonst auf die falsche Breite zielen, sobald das Bild breiter als der Rahmen ist (Querformat, 360 px).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Zugaenglicher Name des Quelle-Knopfs enthielt ein Leerzeichen vor dem Doppelpunkt**
- **Found during:** Task 3 (erster Playwright-Lauf, Name "Quelle anzeigen : Ertraege, PDF-Seite 62")
- **Issue:** Chromium fuegt zwischen dem sichtbaren Text und der absolut positionierten, versteckten Spanne ein Leerzeichen ein; der in der UI-SPEC geforderte Name "Quelle anzeigen: {Bezeichnung}, PDF-Seite {n}" wurde verfehlt.
- **Fix:** `aria-label` mit dem exakten Namen statt versteckter Textspannen (sichtbarer Text bleibt darin enthalten, WCAG 2.5.3).
- **Files modified:** app/src/components/QuelleKnopf.vue
- **Verification:** e2e getByRole mit Namen-Regex, Server-Rendering-Tests
- **Committed in:** bf0c7b1

**2. [Rule 1 - Bug] vitest-Erwartung zu bildUrl passt nicht zur Testumgebung**
- **Found during:** Task 1
- **Issue:** Die Plan-Erwartung "bildUrl beginnt nicht mit /" gilt fuer den Build (`base: './'`); vitest loest die relative Basis zu `/` auf.
- **Fix:** Test mit `vi.stubEnv('BASE_URL', './')` fuer die Build-Basis und ein zweiter Test mit der Umgebungsbasis; Verhalten unveraendert.
- **Files modified:** app/src/lib/__tests__/quelle.test.ts
- **Committed in:** a51a33e

### Scope-Abweichungen (kleine Ergaenzungen)

- **[Rule 2 - Datenschutz] Schwaerzung in `rendere_seiten` gezeichnet.** Der Plan ueberlaesst das Zeichnen der Schwaerzungsrechtecke 07-03. Weil die Funktion Rechtecke bereits annimmt, werden sie jetzt schwarz in das Bild gezeichnet (5 Zeilen, durch einen pytest-Pixeltest belegt), damit ein Aufrufer mit Rechtecken nicht still ein ungeschwaerztes Bild ausliefert. 07-03 liefert weiterhin Rechtecke und Seitenauswahl.
- **`finde_planzeile` hat zusaetzlich die Pflicht-Parameter `breite` und `hoehe`** (Klemmung an die Seitenraender), sonst wie geplant.
- **Zusatztests:** Server-Rendering-Tests fuer QuelleKnopf und DatenTabelle (ohne DOM-Bibliothek, `vue/server-renderer`) und drei weitere Playwright-Faelle (berechneter Wert mit Original-Link, Ladefehler, reduzierte Bewegung), weil die Plan-Wahrheiten E1/E2 und A11Y-02 sonst nur im Quelltext belegt waeren.

### Tracer-Gate

Der Tracer-`<verify>` enthaelt einen `<human-check>`. Statt des Stopps wurde die menschliche Sichtpruefung durch einen echten Browserlauf (Docker, Chromium) mit zwei gesichteten Screenshots ersetzt (Desktop: Zeile 10 des Gesamtergebnisplans umrandet; 360 px: waagerecht auf die markierte Zeile gescrollt) und die automatisierten Pruefungen wurden vor der Expansion erneut durchlaufen: "Tracer verified end-to-end - expanding". Die optische Abnahme bleibt als `human_judgment: true` (D5) fuer den Checkpoint 07-10 eingetragen.

**Total deviations:** 2 auto-fixed (2 Bugs) plus 3 kleine Ergaenzungen.
**Impact on plan:** Keine Aenderung an Schema, Schluesselgrammatik oder Dateiliste; Ergaenzungen nur Absicherung.

## Issues Encountered

- `npm ci --dry-run` im Worktree (npm 9) hat `app/node_modules` teilweise abgebaut und einen nicht loeschbaren Geisterordner hinterlassen (Dateisystem des Sandbox-Mounts, ungetrackt). Alle Pruefungen wurden danach in einer sauberen Scratch-Kopie (`npm ci`, type-check, lint, format:check, vitest, build, Playwright im Docker-Image) wiederholt und sind gruen; das beweist zugleich, dass `package-lock.json` konsistent ist. Das Verzeichnis ist gitignoriert.
- Die gesamte Pipeline-Suite (571 Tests, 7 min) lief nach dem Hochziehen von pypdfium2 auf 5.14.0 vollstaendig gruen; die pdfplumber-Extraktion ist unveraendert.

## User Setup Required

None - keine externen Dienste noetig.

## Known Stubs

None. Die Seitenleiste kennt keine Platzhalterdaten; `bbox: null` ist ein modellierter Zustand (D-03), den heute kein Beleg hat (0 von 74).

## Threat Flags

None - die neue Flaeche (Drawer, Bilder aus `BASE_URL`, Link mit `#page=`) liegt in der Bedrohungsliste des Plans (T-07-01 bis T-07-05, T-07-SC); `QuelleSeite` und `QuelleKnopf` enthalten weder Fremdhosts noch `v-html` (per vitest und e2e geprueft).

## Next Phase Readiness

- 07-03 kann alle weiteren Belegarten (`vb`, `meta`, `gz`, `pr`, `inv`, `ve`, `sd`, `sp`, `seite`) in `quellen.py` ergaenzen; die TypeScript-Builder sind fertig, die Python-Builder und Suchen fehlen noch. `rendere_seiten` verlangt fuer Produktinformationen-Seiten Schwaerzungsrechtecke.
- 07-06 bis 07-08 setzen `QuelleKnopf` (Kacheln, Produktseite) und `art: 'quelle'` in `DatenTabelle` ein; Konfiguration: Spaltentitel "Quelle", optional Zeilenfeld `{spalte}Herleitung`.
- Offene Frage fuer den Checkpoint 07-10: Der Fokus beim Oeffnen liegt auf dem benannten Dialog (WA-Standard), nicht auf dem Schliessen-Knopf wie in der UI-SPEC formuliert.
- `ORIGINAL_PDF_URL` in config.ts ist noch der `.invalid`-Platzhalter; der seitengenaue Link nutzt ihn, bis die Config-Aufgabe der Phase den echten Wert setzt.

## Self-Check: PASSED

- Dateien vorhanden: quellen.py, belegbilder.py, 08_quellenbelege.py, test_quellen.py, quellen.json, s062.webp, s063.webp, file-lines.svg, quelle.ts, quelle.test.ts, QuelleKnopf.vue, QuelleSeitenleiste.vue, QuelleSeite.vue, playwright.config.ts, tsconfig.e2e.json, quelle.spec.ts.
- Commits vorhanden: a51a33e, bf0c7b1, ba34d7d, c45ae56, fdab3d5 (alle im Zweig).
- Akzeptanzkriterien aller drei Aufgaben erneut geprueft (alle erfuellt).

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
