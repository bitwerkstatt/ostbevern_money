---
phase: "9"
art: basislauf
head: 1d0df35da1842daec515b40dd62f8d918e240105
erstellt: 2026-10-09T06:24:00Z
pytest_passed: 681
pytest_skipped: 0
alle_py: byte-identisch
vitest_tests: 2162
e2e_ci_passed: 89
e2e_mobil_passed: 41
e2e_texte_passed: 1
---

# Phase 9: Basislauf (D-23)

Ein Lauf der vollständigen CI-Kette auf dem Code nach Welle 1 (Pläne 09-01 und 09-02). `head` im Frontmatter ist der Commit, dessen Code getestet wurde. Die Verifier prüfen mit `git diff --quiet <head> HEAD -- pipeline app daten scripts .github`, dass sich seitdem kein Codepfad geändert hat. Vor und nach dem Lauf war `git status --porcelain -- pipeline app daten scripts .github` leer (der Lauf hat nichts verändert).

Alle Zahlen in diesem Dokument stammen aus Befehlen, die in diesem Plan gelaufen sind.

## Pipeline

Arbeitsverzeichnis: Worktree des Executors auf `head`. Plattform Linux, Python 3.12 (uv 0.9.26).

### 1. Umgebung und statische Prüfungen

```
$ uv sync --locked --directory pipeline
exit 0
$ (cd pipeline && uv run ruff check .)
All checks passed!
exit 0
$ (cd pipeline && uv run ruff format --check .)
51 files already formatted
exit 0
```

Dauer: unter 1 s für alle drei Befehle zusammen (Wanduhr, ganze Sekunden; die Umgebung war aus dem uv-Cache warm).

### 2. Volle pytest-Suite

```
$ uv run --directory pipeline pytest -p no:cacheprovider -rs -q
681 passed in 350.31s (0:05:50)
exit 0
```

- Keine `SKIPPED`-Zeile in der Ausgabe, `pytest_skipped: 0`.
- Hinweis zum ersten Lauf: Der erste Lauf auf einer frischen Worktree-Kopie ohne `app/node_modules` endete mit `680 passed, 1 skipped in 350.66s`. Übersprungen wurde `tests/test_formatiere.py:463` (`test_port_wie_format_ts`), weil `app/node_modules/typescript/package.json` fehlte. Der Skip ist umgebungsbedingt (kein Codefehler). Daraufhin lief `npm ci` in `app/` (Linux, `node_modules` ist über `app/.gitignore` ausgeschlossen) und die volle Suite wurde erneut gestartet. Maßgeblich ist dieser zweite Lauf mit 681 Tests und null Skips. Die CI-Pipeline-Stufe hat kein `node_modules` und überspringt diesen Test regulär; hier lief er mit.

### 3. Reproduzierbarkeit: alle.py

```
$ uv run --directory pipeline python alle.py --jahr 2026
exit 0
Dauer: 29 s
```

Entscheidende Ausgabezeilen (unverändert aus der Ausgabe kopiert):

```
Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.
Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte.
Schritt 02: 14899 Planzeilen geschrieben.
Schritt 03: 63 Einträge geschrieben: daten/aufbereitet/produkte.json
Schritt 03: 827 Einträge geschrieben: daten/aufbereitet/grundzahlen.csv
Schritt 03: 229 Einträge geschrieben: daten/aufbereitet/erlaeuterungen.csv
Schritt 04: 959 Zeilen geschrieben: daten/aufbereitet/investitionen.csv
Schritt 04: 8 Zeilen geschrieben: daten/aufbereitet/ve_faelligkeiten.csv
Schritt 04: 959 Zeilen geschrieben: daten/zwischen/investitionen_pb.csv
Querschnitte: 1152 Werte geschrieben.
Schritt 05: 162 Zeilen geschrieben: daten/aufbereitet/stellenplan.csv
Schritt 07: geschrieben: app/src/data/haushalt.json
Schritt 07: geschrieben: app/src/data/stellenplan.json
Schritt 07: geschrieben: app/src/data/produkte.json
Schritt 07: geschrieben: app/src/data/investitionen.json
Schritt 07: geschrieben: app/src/data/texte.json
Schritt 08: 2496 Belege, 33 ohne Markierung, 231 Seiten, 0 Bilder neu gerendert
```

Prüfregeln 1 bis 10 (Schritt 06), jede aus der Ausgabe kopiert:

```
Schritt 06: Regel 1: grün (6593 Werte)
Schritt 06: Regel 2: grün (7994 Werte)
Schritt 06: Regel 3: grün (114 Werte)
Schritt 06: Regel 4: grün (259 Werte)
Schritt 06: Regel 5: grün (150 Werte)
Schritt 06: Regel 6: grün (1964 Werte)
Schritt 06: Regel 7: grün (1152 Werte)
Schritt 06: Regel 8: grün (820 Werte)
Schritt 06: Regel 9: grün (12 Werte)
Schritt 06: Regel 10: grün (19 Werte)
Schritt 06: Veraltete Befunde: 0
```

### 4. Byte-Identität nach alle.py

```
$ git diff --stat --exit-code -- daten app/src/data
(leer)
exit 0
$ git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen
(leer)
exit 0
```

Ergebnis Pipeline: alle Schritte grün, `daten/`, `app/src/data/` und `app/public/quellen` byte-identisch beziehungsweise unverändert (`alle_py: byte-identisch`).

## App (Scratch-Kopie)

Die App-Kette lief in einer Scratch-Kopie von `app/` (`rsync` ohne `node_modules`, `dist`, `test-results`, `playwright-report`), weil `app/node_modules` im Worktree nur für den pytest-Test `test_port_wie_format_ts` installiert wurde. Die Kopie wurde nach dem zweiten alle.py-Lauf angelegt, `app/src/data` entspricht also dem Stand von `head`. Node v22.22.1.

| Befehl | Exit | Dauer | Entscheidende Ausgabe |
| --- | --- | --- | --- |
| `npm ci --no-audit --no-fund` | 0 | 2 s | ohne Meldung |
| `npm run type-check` | 0 | 4 s | `vue-tsc --build` ohne `error TS` |
| `npm run lint` | 0 | 1 s | `eslint .` ohne Meldung |
| `npm run format:check` | 0 | 2 s | „All matched files use Prettier code style!“ |
| `npm run test` | 0 | 1 s | `Test Files  49 passed (49)`, `Tests  2162 passed (2162)`, Vitest v5.0.3, Dauer laut Vitest 1.52 s |
| `npm run build` | 0 | 5 s | „✓ 1069 modules transformed.“, „✓ built in 458ms“ |

Der Build meldet nur die bekannte Warnung „Some chunks are larger than 500 kB after minification“ (`index-*.js` 2.035 kB, gzip 489 kB). Das ist kein Fehler und kein Befund dieses Plans.

## Playwright

Alle drei Projekte liefen über `scripts/e2e-wie-ci.sh <scratch>/app --project=… --reporter=list` im Image `mcr.microsoft.com/playwright:v1.63.0-noble` mit DejaVu Sans (`fonts-dejavu-core_2.37-8_all.deb`, Prüfsumme im Skript). Das Projekt `texte` gehört nicht zum CI-Job; es ist enthalten, weil Wahrheiten aus Phase 5 und 6 darauf beruhen.

| Projekt | Exit | Zusammenfassung | Dauer (Wanduhr) |
| --- | --- | --- | --- |
| `ci` | 0 | `89 passed (31.8s)` | 34 s |
| `mobil` | 0 | `41 passed (44.3s)` | 47 s |
| `texte` | 0 | `1 passed (1.2s)` | 4 s |

Hinweis: `mobil` und `texte` liefen beim ersten Versuch zeitgleich (zwei parallele Aufrufe auf derselben Scratch-Kopie); beide waren grün. `texte` wurde danach allein wiederholt, die Zahl oben stammt aus diesem Einzellauf. Die Titelliste von `ci` und `mobil` stammt aus dem jeweils einzigen Lauf.

Die Verifier zitieren einzelne Tests aus diesen Listen (Datei:Zeile › Titel), statt Playwright selbst zu starten. Die Listen sind nach Laufnummer sortiert, ohne Zeitangaben.

### Projekt `ci` (89 Tests)

- e2e/kacheln.spec.ts:465:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /
- e2e/inventar.spec.ts:39:3 › Inventar /: jedes Diagramm hat Tabelle und Beschreibung
- e2e/quelle.spec.ts:121:3 › Quelle anzeigen an der Start-Kachel Erträge › Klick öffnet die Seitenleiste mit Bild und Markierung, Escape gibt den Fokus zurück
- e2e/interaktion.spec.ts:60:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › Enter und Leertaste öffnen und schließen die Liste, aria-expanded und aria-controls stimmen
- e2e/smoke.spec.ts:138:5 › Smoke / › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/interaktion.spec.ts:87:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › Escape schließt die offene Liste, der Fokus liegt auf dem Schalter
- e2e/interaktion.spec.ts:102:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › Tab läuft ohne Fokusfalle durch die Links, das Verlassen der Gruppe schließt die Liste
- e2e/quelle.spec.ts:139:3 › Quelle anzeigen an der Start-Kachel Erträge › Enter und Leertaste öffnen die Seitenleiste, der Schließen-Knopf gibt den Fokus zurück
- e2e/interaktion.spec.ts:135:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › ein Klick außerhalb schließt die Liste
- e2e/interaktion.spec.ts:145:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › ein Routenwechsel schließt die Liste
- e2e/smoke.spec.ts:185:5 › Smoke / › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/inventar.spec.ts:39:3 › Inventar /einnahmen: jedes Diagramm hat Tabelle und Beschreibung
- e2e/interaktion.spec.ts:159:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › auf einer aktiven Unterseite trägt der Eintrag aria-current page und der Schalter aria-current true
- e2e/interaktion.spec.ts:179:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › die geöffnete Liste bleibt nach dem Öffnen und nach einem Resize im Fenster, style.left passt zur Lage
- e2e/quelle.spec.ts:158:3 › Quelle anzeigen an der Start-Kachel Erträge › beim Öffnen liegt der Fokus im Dialog der Seitenleiste, der erste Tab-Stopp ist Schließen
- e2e/kacheln.spec.ts:465:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /investitionen
- e2e/quelle.spec.ts:186:3 › Quelle anzeigen an der Start-Kachel Erträge › zeigt Wertzeile, Hinweis zum berechneten Wert und den seitengenauen Original-Link
- e2e/interaktion.spec.ts:242:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › die Gruppe nutzt weder role menu noch role menuitem
- e2e/inventar.spec.ts:39:3 › Inventar /ausgaben: jedes Diagramm hat Tabelle und Beschreibung
- e2e/quelle.spec.ts:203:3 › Quelle anzeigen an der Start-Kachel Erträge › ersetzt das Bild bei einem Ladefehler durch den Hinweis mit Link ins Original
- e2e/interaktion.spec.ts:248:3 › Menügruppe „Mehr wissen“ (Desktop, D-19) › bis 699 px zeigt der Drawer die Gruppe als Überschrift mit vier sichtbaren Links
- e2e/smoke.spec.ts:191:5 › Smoke / › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/quelle.spec.ts:218:3 › Quelle anzeigen an der Start-Kachel Erträge › setzt bei reduzierter Bewegung Übergänge und Drawer-Dauern auf null
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/quelle.spec.ts:238:3 › Quelle anzeigen an der Start-Kachel Erträge › alle Anfragen gehen an den Preview-Server (keine Drittanbieter)
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /einnahmen: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/quelle.spec.ts:262:3 › Weitere Auslöser der Seitenleiste › ein Tabellenzeilen-Knopf auf /ausgaben öffnet sich mit Enter und gibt den Fokus zurück
- e2e/inventar.spec.ts:39:3 › Inventar /geldfluss: jedes Diagramm hat Tabelle und Beschreibung
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /ausgaben: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /geldfluss: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/quelle.spec.ts:294:3 › Weitere Auslöser der Seitenleiste › eine Stellenplan-Zeile öffnet eine Querformatseite mit der Markierung im Bild
- e2e/kacheln.spec.ts:465:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /rat-entscheidet
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /entwicklung: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/smoke.spec.ts:138:5 › Smoke /einnahmen › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/inventar.spec.ts:39:3 › Inventar /entwicklung: jedes Diagramm hat Tabelle und Beschreibung
- e2e/quelle.spec.ts:335:3 › Weitere Auslöser der Seitenleiste › ein Beleg nur mit Seite nennt „Zeile nicht automatisch markiert“ und zeichnet keine Markierung
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /investitionen: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/quelle.spec.ts:364:3 › Weitere Auslöser der Seitenleiste › eine Pro-Kopf-Kachel zeigt „Berechneter Wert“ mit der Herleitung
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /rat-entscheidet: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/smoke.spec.ts:185:5 › Smoke /einnahmen › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /stellenplan: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/inventar.spec.ts:39:3 › Inventar /investitionen: jedes Diagramm hat Tabelle und Beschreibung
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /glossar: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/kacheln.spec.ts:465:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /stellenplan
- e2e/interaktion.spec.ts:278:5 › Fokus und Titel bei jedem Routenwechsel (A11Y-02) › Route /ueber: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „– Ostbevern Money“
- e2e/interaktion.spec.ts:314:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Link der aktuellen Seite: Drawer zu, aria-expanded false, Fokus auf der Überschrift
- e2e/inventar.spec.ts:39:3 › Inventar /rat-entscheidet: jedes Diagramm hat Tabelle und Beschreibung
- e2e/smoke.spec.ts:191:5 › Smoke /einnahmen › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/interaktion.spec.ts:320:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Link einer anderen Seite: Route wechselt, Fokus auf der Überschrift
- e2e/inventar.spec.ts:39:3 › Inventar /stellenplan: jedes Diagramm hat Tabelle und Beschreibung
- e2e/kacheln.spec.ts:514:3 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kachelrouten: genau diese Routen zeigen Kennzahl-Kacheln
- e2e/interaktion.spec.ts:324:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Escape schließt den Drawer, der Fokus kehrt zum Menüknopf zurück
- e2e/inventar.spec.ts:39:3 › Inventar /glossar: jedes Diagramm hat Tabelle und Beschreibung
- e2e/smoke.spec.ts:138:5 › Smoke /ausgaben › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/interaktion.spec.ts:328:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Ctrl-Klick auf einen Link: öffnet neuen Tab, Drawer bleibt offen, Fokus nicht auf h1 (WR-02)
- e2e/inventar.spec.ts:39:3 › Inventar /ueber: jedes Diagramm hat Tabelle und Beschreibung
- e2e/interaktion.spec.ts:334:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Shift-Klick auf einen Link: öffnet neues Fenster, Drawer bleibt offen, Fokus nicht auf h1 (WR-02)
- e2e/smoke.spec.ts:185:5 › Smoke /ausgaben › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/inventar.spec.ts:39:3 › Inventar /produkt/010601: jedes Diagramm hat Tabelle und Beschreibung
- e2e/interaktion.spec.ts:345:3 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › /investitionen: überlaufende Rahmen sind benannte Regionen mit Tabstopp, die Seite scrollt nicht
- e2e/smoke.spec.ts:191:5 › Smoke /ausgaben › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/interaktion.spec.ts:393:3 › Reduzierte Bewegung bei Web-Awesome-Komponenten (A11Y-02) › die Quell-Seitenleiste öffnet ohne Übergang
- e2e/interaktion.spec.ts:407:3 › Reduzierte Bewegung bei Web-Awesome-Komponenten (A11Y-02) › der Menü-Drawer (360 px) öffnet ohne Übergang
- e2e/interaktion.spec.ts:419:3 › Reduzierte Bewegung bei Web-Awesome-Komponenten (A11Y-02) › ein wa-details „Tabelle anzeigen“ öffnet ohne Übergang
- e2e/interaktion.spec.ts:453:3 › Maßnahmenfilter auf /investitionen (06/IN-05, T-08-18) › ein gültiger Aufgabenbereich verringert die Zahl der Maßnahmen, ein ungültiger verschwindet aus der URL
- e2e/smoke.spec.ts:138:5 › Smoke /geldfluss › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /geldfluss › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /geldfluss › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /entwicklung › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /entwicklung › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /entwicklung › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /investitionen › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /investitionen › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /investitionen › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /rat-entscheidet › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /rat-entscheidet › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /rat-entscheidet › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /stellenplan › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /stellenplan › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /stellenplan › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /glossar › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /glossar › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /glossar › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /ueber › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /ueber › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /ueber › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)
- e2e/smoke.spec.ts:138:5 › Smoke /produkt/010601 › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten
- e2e/smoke.spec.ts:185:5 › Smoke /produkt/010601 › axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA
- e2e/smoke.spec.ts:191:5 › Smoke /produkt/010601 › axe: auch mit geöffneten Bereichen (Tabellen in wa-details)

### Projekt `mobil` (41 Tests)

- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /einnahmen
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /ausgaben
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /geldfluss
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /entwicklung
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /investitionen
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /rat-entscheidet
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /stellenplan
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /glossar
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /ueber
- e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /produkt/010601
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf / keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /einnahmen
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /einnahmen keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /ausgaben
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /ausgaben keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /geldfluss
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /geldfluss keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /entwicklung
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /entwicklung keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /investitionen
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /investitionen keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /rat-entscheidet
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /rat-entscheidet keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /stellenplan
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /stellenplan keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /glossar
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /glossar keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /ueber
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /ueber keinen Verstoß
- e2e/mobil.spec.ts:181:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › Rahmen mit Rolle und genau einem Namen auf /produkt/010601
- e2e/mobil.spec.ts:194:5 › Tabellenrahmen bei 360 px (A11Y-01, A11Y-03) › axe meldet bei geöffneten Bereichen auf /produkt/010601 keinen Verstoß
- e2e/mobil.spec.ts:223:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Link der aktuellen Seite: Drawer zu, aria-expanded false, Fokus auf der Überschrift
- e2e/mobil.spec.ts:229:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Link einer anderen Seite: Route wechselt, Fokus auf der Überschrift
- e2e/mobil.spec.ts:233:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Escape schließt den Drawer, der Fokus kehrt zum Menüknopf zurück
- e2e/mobil.spec.ts:237:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Ctrl-Klick auf einen Link: öffnet neuen Tab, Drawer bleibt offen, Fokus nicht auf h1 (WR-02)
- e2e/mobil.spec.ts:243:3 › Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21) › Shift-Klick auf einen Link: öffnet neues Fenster, Drawer bleibt offen, Fokus nicht auf h1 (WR-02)
- e2e/mobil.spec.ts:251:3 › 360 × 640 mit geöffneter Leiste und geöffnetem Menü (A11Y-03) › mit geöffneter Quell-Leiste auf /
- e2e/mobil.spec.ts:281:3 › 360 × 640 mit geöffneter Leiste und geöffnetem Menü (A11Y-03) › mit geöffnetem Menü-Drawer
- e2e/mobil.spec.ts:311:3 › 360 × 640 mit geöffneter Leiste und geöffnetem Menü (A11Y-03) › eine Querformatseite scrollt nur im eigenen Rahmen, nicht die Seite

### Projekt `texte` (1 Test)

- e2e/textliste.spec.ts:118:1 › schreibt die Textliste je Route nach test-results/textliste.md

## Verifikationsstatus vor der Re-Verifikation

Ausgabe von `node .claude/gsd-core/bin/gsd-tools.cjs query verification.status <Verzeichnis> --pick status` (vor den Re-Verifikationen von Welle 3, auf `head`). `stale` heißt: Quelldateien, die der Verifier abdeckte, haben sich nach dem letzten Verifier-Lauf geändert; die Phase braucht eine neue Verifikation.

| Verzeichnis | verification.status |
| --- | --- |
| `.planning/milestones/v1.0-phases/01-setup` | stale |
| `.planning/milestones/v1.0-phases/02-kernzahlen` | stale |
| `.planning/milestones/v1.0-phases/03-details` | stale |
| `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten` | stale |
| `.planning/milestones/v1.0-phases/05-leitfragen-seiten` | stale |
| `.planning/milestones/v1.0-phases/06-kontext-seiten` | stale |
| `.planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung` | stale |
| `.planning/phases/08-fixes-und-triage` | passed |

Phase 8 (`08-fixes-und-triage`) steht auf `passed`; die Phasen 01 bis 07 stehen auf `stale`.

## npm audit

Registry erreichbar, beide Abfragen lieferten ein Ergebnis (Scratch-Kopie, `package-lock.json` unverändert).

| Befehl | Exit | Ergebnis |
| --- | --- | --- |
| `npm audit --omit=dev` | 0 | `found 0 vulnerabilities` (Produktionsabhängigkeiten: 0 Funde) |
| `npm audit` | 1 | `4 high severity vulnerabilities` (alle Abhängigkeiten) |

Die vier Funde mit Schweregrad hoch sind eine Kette ausschließlich in Entwicklungsabhängigkeiten: `braces` (GHSA-vfj7-8cjw-p6xm, Stack-Erschöpfung bei tief verschachtelten Mustern) → `micromatch` → `fast-glob` → `@vue/eslint-config-typescript`. `npm audit fix --force` würde `@vue/eslint-config-typescript@14.0.1` installieren (Breaking Change). Nichts davon gelangt in das ausgelieferte Bündel. Es wurde nichts installiert oder geändert; die Bewertung gehört in die Pläne 09-04 bis 09-13.

## Hinweise für die Verifier

- Die Verifier von 09-04 bis 09-10 zitieren diese Datei. Sie führen nur lesende Prüfungen aus: `git`, `grep` und eine benannte pytest- oder vitest-Auswahl in ihrer eigenen Scratch-Kopie.
- Sie starten weder `alle.py` noch die volle pytest-Suite noch Playwright. Alle drei laufen nur hier (und im Abschlusslauf), weil parallele Läufe in dieselben Verzeichnisse schreiben und denselben Port benutzen würden.
- Beweis, dass der Code seit dem Lauf unverändert ist: `git diff --quiet <head> HEAD -- pipeline app daten scripts .github` (Exit 0). Ändert sich ein Codepfad, gilt die Evidenz hier nicht mehr für diesen Pfad.
- Eine volle pytest-Suite läuft ohne Skip nur, wenn `app/node_modules/typescript` vorhanden ist (siehe Abschnitt „Pipeline“, Test `test_port_wie_format_ts`). Die CI-Pipeline-Stufe hat dieses Verzeichnis nicht und überspringt den Test regulär; wer ihn einzeln braucht, installiert `npm ci` in seiner Scratch-Kopie.
- Zahlen aus diesem Lauf: 681 pytest-Tests (0 Skips), 10 Prüfregeln grün, „Veraltete Befunde: 0“, 2162 Vitest-Tests in 49 Dateien, Playwright `ci` 89, `mobil` 41, `texte` 1.
