---
phase: 06-kontext-seiten
plan: 12
subsystem: app-tests
tags: [vitest, quelltext-test, hinweis-test, phasen-gate, glossar, ui-04, ui-05]

requires:
  - phase: 06-kontext-seiten
    provides: "06-01 bis 06-11: die vier Kontext-Seiten, HinweisNichtImHaushalt, Glossarbegriffe, Pipeline-Texte"
provides:
  - "quelltext.test.ts: INHALTSSEITEN umfasst neun Seiten (fünf aus Phase 5, vier aus Phase 6), PFLICHT_SCHLUESSEL um haushaltssicherung, verpflichtungsermaechtigung, vzae, entgeltgruppen erweitert"
  - "hinweis.test.ts: Glossaranker nicht_im_haushalt (GLOSSAR_SCHLUESSEL, texte.glossar mit PDF-Seite) und die drei Platzierungen ausgaben/einnahmen/kurz"
  - "CI-identischer Phasen-Gate grün (pytest, ruff, alle.py reproduzierbar, Gesamtstatus grün, App-Kette)"
affects: [phase-07, verify-work]

actuals:
  tokens: 975
  tasks: 2
  commits: 1
plan_head_before: a3132c48b86bfc057eb9c08ad5967a47b68bcb8d
plan_head_after: f64e07ff4affaa3d19f7e0251bbcb9b9016e722d

tech-stack:
  added: []
  patterns:
    - "Eine Liste INHALTSSEITEN und eine Liste PFLICHT_SCHLUESSEL für alle Phasen; neue Seiten und Pflichtbegriffe werden angehängt, nicht ersetzt"

key-files:
  created: []
  modified:
    - app/src/lib/__tests__/quelltext.test.ts
    - app/src/lib/__tests__/hinweis.test.ts

key-decisions:
  - "Die Platzierungs- und Variantenprüfungen aus 06-03 und 06-07 wurden nicht dupliziert, sondern nur um den Glossaranker (GLOSSAR_SCHLUESSEL, texte.glossar) und einen Sammeltest über die drei Seiten ergänzt"

requirements-completed: [UI-04, ENTW-01, ENTW-02, ENTW-03, INV-01, INV-02, INV-03, INV-04, RAT-01, RAT-02, RAT-03, RAT-04, STEL-01, STEL-02, STEL-03]

duration: 40min
completed: 2026-10-06
status: complete

coverage:
  - id: D1
    description: "Die vier Phase-6-Seiten zählen als Inhaltsseiten: je mindestens ein GlossarBegriff, und zusammen verlinken die Inhaltsseiten haushaltssicherung, verpflichtungsermaechtigung, vzae, entgeltgruppen zusätzlich zu den Phase-5-Pflichtbegriffen"
    requirement: "GLOS-03, D-14, D-17"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#Glossarverlinkung auf den Inhaltsseiten (GLOS-03, D-16, D-17)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Kein getippter Betrag, Prozentwert, gruppierte Zahl oder Roh-HTML-Direktive in irgendeiner .vue-Datei, inklusive aller Phase-6-Komponenten"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#Keine getippten Zahlen in den Templates (UI-05, T-05-40, T-05-41)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Die Hinweisbox 'Was nicht im Haushalt steht' steht auf /ausgaben (ausgaben), /einnahmen (einnahmen) und /rat-entscheidet (kurz); der Anker nicht_im_haushalt ist in GLOSSAR_SCHLUESSEL, in texte.glossar und der Pipeline-Text nennt PDF-Seiten"
    requirement: UI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/hinweis.test.ts#Glossaranker nicht_im_haushalt (UI-04, D-18)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/hinweis.test.ts#HinweisNichtImHaushalt auf /ausgaben (UI-04, D-18)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Phasen-Gate: pytest, ruff check und format, alle.py --jahr 2026 ohne Diff und ohne untracked Dateien, Gesamtstatus grün, App-Kette (type-check, lint, format:check, test, build)"
    verification:
      - kind: other
        ref: "uv run --directory pipeline pytest -q (545 passed, 1 skipped; der Skip test_formatiere separat mit verlinktem node_modules: 23 passed)"
        status: pass
      - kind: other
        ref: "ruff check . und ruff format --check . (46 Dateien)"
        status: pass
      - kind: other
        ref: "alle.py --jahr 2026, git diff --stat und git status --porcelain unter daten und app/src/data leer, konsistenz.md Gesamtstatus: grün"
        status: pass
      - kind: other
        ref: "App-Kette in Scratch-Kopie: type-check, lint, format:check, test (36 Dateien, 1393 Tests), build"
        status: pass
    human_judgment: false
  - id: D5
    description: "End-of-Phase-Walkthrough aller Phase-6-Seiten im Browser (1280 px und 360 px, Maus und Tastatur)"
    verification: []
    human_judgment: true
    rationale: "Die Sandbox hat keinen Browser; der Walkthrough steht offen für /gsd-verify-work (Liste siehe Übergabe an Phase 7 und Abschnitt Offene Human-Checks)"
---

# Phase 6 Plan 12: Quelltext- und Hinweis-Abdeckung und Phasen-Gate Summary

**Die Quelltext-Tests führen jetzt neun Inhaltsseiten und vier zusätzliche Pflicht-Glossarbegriffe, hinweis.test.ts sichert den Anker nicht_im_haushalt, und der CI-identische Phasen-Gate (pytest, ruff, reproduzierbares alle.py, Gesamtstatus grün, App-Kette) ist grün.**

## Performance

- **Duration:** ca. 40 min (davon rund 6 min der volle pytest-Lauf)
- **Tasks:** 2 (Task 1 Tracer, Task 2 Gate)
- **Files modified:** 2 (beide Testdateien)

## Accomplishments

- `quelltext.test.ts`: `INHALTSSEITEN` um `EntwicklungPage`, `InvestitionenPage`, `RatEntscheidetPage`, `StellenplanPage` erweitert (neun Seiten, je mindestens ein `GlossarBegriff`); `PFLICHT_SCHLUESSEL` um `haushaltssicherung`, `verpflichtungsermaechtigung`, `vzae`, `entgeltgruppen` erweitert. Die bestehenden Schlüssel blieben erhalten. Die Pflichtliste wird weiterhin gegen `GLOSSAR_SCHLUESSEL` auf Tippfehler geprüft.
- Die Template-Prüfung auf getippte Zahlen und die Roh-HTML-Direktive läuft per `import.meta.glob` über jede `.vue`-Datei und deckt damit alle Phase-6-Komponenten ab (UI-05, T-06-30, T-06-31); sie war grün, ohne dass Seiten- oder Komponentendateien geändert werden mussten.
- `hinweis.test.ts`: neuer Block „Glossaranker nicht_im_haushalt“ mit drei Tests: Schlüssel in `GLOSSAR_SCHLUESSEL`; Begriff in `texte.glossar` mit mindestens einer PDF-Seite; Sammeltest, dass `/ausgaben` (`ausgaben`), `/einnahmen` (`einnahmen`) und `/rat-entscheidet` (`kurz`) die Box einbinden und die Komponente auf `#nicht_im_haushalt` verlinkt. Die Prüfung, dass der Pipeline-Text `nicht_im_haushalt` PDF-Seiten nennt, stand bereits aus 06-03 und blieb unverändert.
- Es gab keinen fehlenden Glossarbegriff auf einer Seite (Schritt 3 der Aktion, „stop and report“, musste nicht greifen): `EntwicklungPage` verlinkt `haushaltssicherung`, `InvestitionenPage` `finanzplan` und `verpflichtungsermaechtigung`, `RatEntscheidetPage` `bindungsgrad`, `StellenplanPage` `vzae` und `entgeltgruppen`.

## Task Commits

1. **Task 1: Tracer, Quelltext- und Hinweis-Abdeckung der vier neuen Seiten** - `f64e07f` (test)
2. **Task 2: Phasen-Gate und Abschlussdurchgang** - kein Code-Commit (`quelltext.test.ts` wurde in Task 2 nicht geändert; es entsteht nur dieser SUMMARY-Commit)

`commits: 1` ist aus `plan_head_before..HEAD` gemessen und zählt den Task-1-Commit ohne den Metadaten-Commit dieser Datei.

## Tracer-Gate

Nach Task 1 lief die `<verify>`-Kette (quelltext-, hinweis-, glossar-, menue-Tests: 130 passed; type-check, lint, format:check) in einer Scratch-Kopie grün, danach folgte Task 2. Es gibt kein `<human-check>` im Tracer, daher kein Checkpoint (`HUMAN_VERIFY_MODE` end-of-phase). Die Acceptance-Greps (vier Seitennamen, `'entgeltgruppen'`, `'vzae'`, `nicht_im_haushalt`) bestanden.

## Phasen-Gate (Task 2)

| Prüfung | Ergebnis |
| --- | --- |
| `uv run --directory pipeline pytest -q` | 545 passed, 1 skipped (der Skip ist `test_port_wie_format_ts`, braucht `app/node_modules/typescript`); mit temporär verlinktem Linux-`node_modules` lief `test_formatiere.py` separat: 23 passed. Link vor dem Commit entfernt. |
| `ruff check .` und `ruff format --check .` | grün (46 Dateien formatiert) |
| `alle.py --jahr 2026` | exit 0; `git diff --stat --exit-code -- daten app/src/data` leer; `git status --porcelain --untracked-files=all` leer |
| `konsistenz.md` | `Gesamtstatus: grün` |
| App-Kette in Scratch-Kopie (Linux-`node_modules`, Lockfile identisch zum committeten, kein Netz, daher kein `npm ci`) | type-check, lint, format:check grün; test: 36 Dateien, 1393 Tests grün; build erfolgreich (bekannte Chunk-Größen-Warnung, 1,75 MB) |

## Dokumentierte Abweichungen

Die vier Nutzerentscheidungen vom 2026-10-05 sind in den Plänen jeweils als „user decision N“ geführt; die Nummern gelten **je Plan** und bezeichnen nicht dieselbe Entscheidung. Zusammenstellung der in 06-01 bis 06-11 dokumentierten Abweichungen von UI-SPEC, Kontext oder Plan:

| Abweichung | Umgesetzt in | Quelle |
| --- | --- | --- |
| Jahresergebnis-Säulen auf `/entwicklung` lesen `zeilen.ergebnis_nach_minderaufwand` statt `zeilen.jahresergebnis`; Untertitel „nach globalem Minderaufwand“, Linien bleiben „vor“ (Defizit 2029 −3,56 Mio. €) | 06-05 | Nutzerentscheidung 1 |
| Maßnahmen werden nach `(produkt, massnahme_id)` statt `massnahme_id` gebündelt (11 Kennungen kommen unter mehreren Produkten vor), erst nach Art filtern, dann bündeln; Abweichung von D-07 | 06-06 | Nutzerentscheidung 2 |
| Rücklagen: Achsenunterschrift „Bestand zu Jahresbeginn“ wie S. 311; Rückgangswerte wie auf S. 23 gedruckt (1,8 / 4,2 / 4,7 / 10 %), die UI-SPEC-Behauptung „jeweils unter 5 %“ entfällt; HSK-Schwellen 25 % und 5 % als Zitat des Vorberichts (S. 23), keine eigene Rechtsbewertung | 06-01, 06-04, 06-08 | Nutzerentscheidung 3 |
| Liquiditätskredite stehen nicht im Stapel und nicht im Schuldenstand (gesamt = Investitionskredite + NRW.Bank), null als Strich, nie als 0; die 656-€-Kachel trägt kein „berechnet“, weil der Wert gedruckt vorliegt; „berechnet“ folgt allein `schuldenstand.berechnet` (2027 bis 2029) | 06-09 | Nutzerentscheidung 4 |
| Stellengruppen absteigend nach gedruckter `position` sortiert (1 → 14, A 8 → B 3, S 11 → S 12), Abweichung vom UI-SPEC-Wortlaut „aufsteigend“ | 06-11 | Nutzerentscheidung 4 (anderer Plan), RESEARCH Pitfall 7 |
| Chevron der Menügruppe als Inline-SVG, keine neue Icon-Datei unter `app/public/icons` | 06-02 | Nutzerentscheidung 4 (anderer Plan) |
| Überschuss-Liste ohne das Finanzierungsprodukt 160101 (nur 011202, 011204, 110101); D-01 überstimmt UI-SPEC E5 | 06-10 | D-01 |
| Ortsteil-Textfilter („Brock“) ist nicht Teil der Phase (ERW-02) | 06-06 | Nutzerentscheidung 4 (06-06) |
| Fachliche Abnahme der sieben Erklär- und Glossartexte (D-20) ohne Korrekturen („freigegeben“) | 06-04 | Checkpoint |

Auto-Korrekturen in den Plänen (Rule 1 bis 3, jeweils im SUMMARY des Plans): 06-02 (RED-Gerüst, Fensterrand-Klemmung der Menüliste, `liquiditaetskredite` in `SCHULDEN_FARBEN`), 06-04 (`_JAHRWERTIGE_ABGELEITETE` in `test_formatiere.py`), 06-05 (4), 06-06 (2), 06-09 (4), 06-10 (2), 06-11 (4).

Abweichungen in diesem Plan: keine. Der Plan wurde wie geschrieben ausgeführt; als reine Ablaufabweichung lief die App-Kette in einer Scratch-Kopie mit vorhandenem Linux-`node_modules` statt mit `npm ci` (kein Netz, Lockfile identisch).

**Total deviations (06-12):** 0.

## Offene Human-Checks (konsolidiert, für /gsd-verify-work)

Der End-of-Phase-Walkthrough wurde **nicht** ausgeführt und gilt **nicht** als bestanden: In der Linux-Sandbox gibt es keinen Browser, und `app/node_modules` im Hauptcheckout enthält macOS-Binaries. Er ist auf dem Host auszuführen (`npm --prefix app ci` einmal unter macOS, dann `npm --prefix app run dev`), bei 1280 px und 360 px, nur mit Maus und Tastatur, Befund je Seite.

Gesamtliste aus dem Plan und den SUMMARYs 06-01 bis 06-11:

- **Kopfmenü und Drawer (06-02):** „Mehr wissen“ öffnen, Escape (Fokus zurück), Klick außen, aktiver Zustand bei aktiver Unterseite, Enter und Leertaste; bei 360 px Drawer-Gruppe, Liste bleibt im Viewport (Fensterrand-Klemmung).
- **/entwicklung (06-05, 06-08):** Linien und Jahresergebnis-Säulen (Defizit 2029 −3,56 Mio. € nach Minderaufwand), fünf Posten-Karten, Zweizeilen-Achse („Ist“, „Ansatz“, „Planung“) bei 360 px lesbar (RESEARCH A3, Überlappung wahrscheinlich, Entscheidung beim Walkthrough: Abkürzungen, Drehung oder schmalere y-Achse), Direktbeschriftung der Linien (`endLabel`), Platz für „Defizit 3,56 Mio. €“ bei 240 px Höhe, Raster `minmax(300px, 1fr)` ergibt bei 1152 px drei Spalten (ggf. `minmax(340px, 1fr)`), linker Rand der Diagramme; Rücklagen „Bestand zu Jahresbeginn“ mit Summen, Rückgang 1,8 / 4,2 / 4,7 / 10 % mit gestrichelter Schwellenlinie, Beschriftung innerhalb des Diagramms; Polster-Text ohne Aussage über Jahre nach dem letzten Planjahr.
- **/investitionen (06-06, 06-07, 06-09):** Filter nur per Tastatur, `?pb=` und `?art=` ohne neue Verlaufseinträge, `/#/investitionen?art=xyz` wird bereinigt, Leerzustand mit „Filter zurücksetzen“, Balkenklick öffnet das Produkt, Tabelle scrollt bei 360 px im eigenen Container, lange Bereichsnamen im aufgeklappten `wa-select` lesbar; größte Maßnahmen und Tabelle; Kachel Schuldenstand 7,71 Mio. € und 656 € (ohne „berechnet“), VE 11,6 Mio. € mit Fälligkeiten (Säulen 2027 und 2028); beide Finanzierungsdiagramme mit Legende, bei 360 px nur größter Wert je Jahr; Schuldenstand mit Streifenmuster und „berechnet“ genau bei 2027 bis 2029, kein Liquiditätskredit-Segment, Satz zu den Jahren ohne Liquiditätskredite; „So wurde gerechnet“ bricht um; Tabellen scrollen nur im eigenen Container.
- **/rat-entscheidet (06-07, 06-10):** Bindungsgrad-Balken 13,3 Mio. € mit Beschriftung, Aufklapper mit Produktbalken (Mount-Zeitpunkt beim ersten `wa-show`, Layout der aufgeklappten Diagramme, RESEARCH A2), Überschuss-Tabelle (drei Produkte), Kitas, Kreisumlage-Kacheln und Satz, Einzelzuschüsse (zwei Quellgruppen), Kurzhinweis BBO/TEO am Seitenende, Fokusreihenfolge.
- **/stellenplan (06-11):** Kacheln 62,91 / 62,13 / 56,63 VZÄ, Teil-Säulen mit Legende, Fluchtung der Bereichsdiagramme bei 1280 px und Stapelung bei 360 px, drei Gruppendiagramme in der Reihenfolge 1 → 14, A 8 → B 3, S 11 → S 12, Glossarlinks VZÄ und Entgeltgruppen.
- **/ausgaben und /einnahmen (06-03):** Hinweisbox BBO/TEO am Ende, Aufklapper „Was sind BBO und TEO?“ öffnet und zeigt Text mit PDF-Seiten; bei 360 px kein Umbruchfehler.
- **Übergreifend:** kein horizontales Seiten-Scrollen bei 360 px, zweizeilige Achsen bei 360 px lesbar.

## Übergabe an Phase 7

- **UI-SPEC-Backstop-Truths für den Phase-7-Smoke-Test (Playwright):**
  - Ladezustand: Charts zeigen `wa-skeleton`, solange `laedt` gesetzt ist, und erscheinen ohne Layout-Sprung (UI-SPEC loading E1, E2, E3, E8, E9, E10).
  - Fehlerzustand: Ein Renderfehler eines Charts zeigt den Fehlertext statt einer leeren Fläche (UI-SPEC error E1, E2, E3, E4, E7, E8, E9, E10).
  - E11 (Hinweisbox BBO/TEO) ist befüllt: Box steht auf `/ausgaben`, `/einnahmen`, `/rat-entscheidet`, Glossaranker `nicht_im_haushalt` existiert. Das ist per Unit-Test belegt; der Verifier führt die Backstop-Truths bis zum Smoke-Test als `human_needed`.
  - In der UI-SPEC als gegenstandslos verworfen (statische JSON-Imports, kein Laufzeit-Laden): loading E4, E5, E6, E7, E10, E11, E12; error E5, E6, E10, E11.
- **Offene Token-Hygiene aus `05-UI-REVIEW.md` (weiterhin Phase 7, kosmetisch):** `font-weight: 600` fest in `App.vue` (Zeilen 215, 240) statt `var(--wa-font-weight-bold)`; `--wa-font-weight-semibold` in `GlossarListe.vue` und `GlossarPage.vue` (zwei Gewichte laut UI-SPEC); `--wa-font-size-xl`; `--wa-space-3xs` (`App.vue`, `GlossarListe.vue`) und `--wa-space-2xl` (`GlossarListe.vue`) außerhalb der UI-SPEC-Skala. In Phase 6 nicht angefasst.
- **Chunk-Größe:** Der Build warnt vor einem Chunk von 1,75 MB (gzip 454 kB); Code-Splitting (dynamischer Import je Route) ist ein Phase-7-Thema.
- **Daten-Hand-off:** `alle.py --jahr 2026` ist reproduzierbar; `app/src/data/*.json` und `daten/` sind eingecheckt und sauber.
- **Hinweis für Worktree-Läufe:** `test_port_wie_format_ts` braucht `app/node_modules/typescript` und wird ohne dieses Verzeichnis übersprungen; auf dem Host mit installiertem `node_modules` läuft er mit.

## Files Created/Modified

- `app/src/lib/__tests__/quelltext.test.ts` - neun Inhaltsseiten, vier zusätzliche Pflichtschlüssel
- `app/src/lib/__tests__/hinweis.test.ts` - Glossaranker-Prüfungen und Sammeltest der Platzierungen

## Known Stubs

None. Beide Dateien sind reine Tests; die geprüften Seiten wurden in 06-02 bis 06-11 verdrahtet.

## Threat Flags

None. Keine neue Angriffsfläche. T-06-30 (getippte Zahlen) und T-06-31 (Roh-HTML-Direktive) sind durch die Template-Prüfung über alle `.vue`-Dateien mitigiert; T-06-SC: keine neue Abhängigkeit, die Scratch-Kopie nutzte das committete Lockfile.

## Self-Check: PASSED

- `app/src/lib/__tests__/quelltext.test.ts`, `app/src/lib/__tests__/hinweis.test.ts` vorhanden; Commit `f64e07f` liegt auf dem Branch.
- Acceptance-Kriterien: Greps (vier Seitennamen, `'entgeltgruppen'`, `'vzae'`, `nicht_im_haushalt`), `grep 'Gesamtstatus: grün'`, ruff check und format: bestanden; die SUMMARY enthält die Abschnitte „Dokumentierte Abweichungen“ und „Übergabe an Phase 7“.

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
