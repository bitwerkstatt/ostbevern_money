---
phase: 07-feinschliff-und-veroeffentlichung
reviewed: 2026-10-07T00:00:00Z
depth: standard
files_reviewed: 98
files_reviewed_list:
  - .github/workflows/ci.yml
  - README.md
  - app/.gitignore
  - app/.prettierignore
  - app/e2e/interaktion.spec.ts
  - app/e2e/inventar.spec.ts
  - app/e2e/mobil.spec.ts
  - app/e2e/quelle.spec.ts
  - app/e2e/routen.ts
  - app/e2e/smoke.spec.ts
  - app/e2e/textliste.spec.ts
  - app/package.json
  - app/playwright.config.ts
  - app/src/App.vue
  - app/src/components/AufwandsartBalken.vue
  - app/src/components/BaseChart.vue
  - app/src/components/BerechnetEtikett.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/EbenenTabelle.vue
  - app/src/components/EinstiegsKachel.vue
  - app/src/components/ErtragsBalken.vue
  - app/src/components/GlossarListe.vue
  - app/src/components/KennzahlKachel.vue
  - app/src/components/NichtBeeinflussbarBlock.vue
  - app/src/components/PostenZeitreihe.vue
  - app/src/components/QuelleKnopf.vue
  - app/src/components/QuelleSeite.vue
  - app/src/components/QuelleSeitenleiste.vue
  - app/src/components/SankeyDiagramm.vue
  - app/src/components/StellenNachBereich.vue
  - app/src/components/StellenNachGruppe.vue
  - app/src/components/SteuerZeitreihe.vue
  - app/src/components/WertartEtikett.vue
  - app/src/components/ZuschussListe.vue
  - app/src/components/datenTabelle.ts
  - app/src/config.ts
  - app/src/data/daten.ts
  - app/src/data/typen.ts
  - app/src/lib/aufwandsarten.ts
  - app/src/lib/ebenenBeleg.ts
  - app/src/lib/einnahmen.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/kennzahlen.ts
  - app/src/lib/menue.ts
  - app/src/lib/produkt.ts
  - app/src/lib/quelle.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/lib/zeitreihen.ts
  - app/src/lib/zuschuesse.ts
  - app/src/pages/AusgabenPage.vue
  - app/src/pages/EinnahmenPage.vue
  - app/src/pages/GlossarPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/ProduktPage.vue
  - app/src/pages/StartPage.vue
  - app/src/pages/StellenplanPage.vue
  - app/src/pages/UeberPage.vue
  - app/src/router/index.ts
  - app/src/styles/basis.css
  - app/tsconfig.e2e.json
  - app/tsconfig.json
  - pipeline/08_quellenbelege.py
  - pipeline/alle.py
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/belegbilder.py
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/pdf.py
  - pipeline/ostbevern/produkte.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/quellen.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/texte.py
  - pipeline/pyproject.toml
  - scripts/lighthouse-a11y.sh
findings:
  critical: 2
  warning: 5
  info: 8
  total: 15
status: issues_found
---

# Phase 7: Code Review Report

**Reviewed:** 2026-10-07
**Depth:** standard
**Files Reviewed:** 98 (Testdateien unter `__tests__/` und `pipeline/tests/` nur auf Zuverlässigkeit überflogen, nicht Zeile für Zeile)

## Summary

Geprüft wurden der Quellenbeleg-Pfad (Pipeline-Schritt 08, `belegbilder.py`, `quellen.py`; App-Seite `lib/quelle.ts`, `QuelleKnopf`, `QuelleSeite`, `QuelleSeitenleiste`), CI und Veröffentlichung (`ci.yml`, README), das Lighthouse-Skript, die Datenaufbereitung der Seiten und die Phase-7-Änderungen an `pruefung.py`, `texte.py`, `app_daten.py` und `konfiguration.py`.

Der Kern ist sauber gebaut. Die Suche nach Zeilenrechtecken rät nie, sondern liefert bei Mehrdeutigkeit `bbox: null`. Die Prüfung gegen die Schwärzflächen ist konsequent. Die Schlüsselgrammatik ist zwischen Pipeline und App identisch. Es gibt kein `v-html`, kein `eval` und keine Drittanbieter-Requests. Die gerenderten Seiten `s072` und `s074` habe ich stichprobenartig angesehen: Verantwortliche/r und Sachbearbeiter/innen sind korrekt und deckend geschwärzt.

Zwei Befunde zählen als BLOCKER:
- Auf PDF-Seite 9 werden Namen und Unterschriften ausgeliefert.
- Das Lighthouse-Skript löscht ein vom Nutzer übergebenes Verzeichnis.

Daneben gibt es einen Workflow-Fallstrick bei der Schwärzung und mehrere Robustheitslücken in der Pipeline.

**Querverweis (bekannt, nicht neu untersucht):** Der Kachel-Überlauf der Startseite zwischen 360 und 600 px durch `.om-zahl { white-space: nowrap }` in `app/src/styles/basis.css:12-16` ist als BLOCKER in `07-UI-REVIEW.md` nachgehalten.

## Critical Issues

### CR-01: Namen und Unterschriften zweier Personen stehen ungeschwärzt in einem ausgelieferten Belegbild

**File:** `app/public/quellen/s009.webp` (erzeugt von `pipeline/ostbevern/quellen.py:1427-1434`, Konfiguration `pipeline/jahrgaenge/2026.toml:209-210`)
**Issue:** Der Projektgrundsatz lautet: „Mitarbeitendennamen werden extrahiert, aber nicht ausgeliefert.“ Der eigene Bericht `daten/pruefberichte/quellenbelege.md` (Datenschutz-Prüfliste) meldet für Seite 9 „Bürgermeister“ und „Kämmerin“ mit `geschwärzt = nein`. Das Bild `s009.webp` zeigt am Seitenende den Satzungsabschluss mit Klarnamen („Julia Klein, Kämmerin“, „Karl Piochowiak, Bürgermeister“) und beiden handschriftlichen Unterschriften. Die Kämmerin ist Verwaltungsmitarbeiterin. Die Seite wird über `seite:9` und die `meta:satzung.*`-Belege (Satzungsbeschluss) tatsächlich referenziert und deshalb gerendert und veröffentlicht.

`schwaerzen_nach = []` ist „bewusst leer“. Die Prüfliste ist aber nur ein Bericht: Kein Test und keine CI-Prüfung schlägt an, wenn ein Treffer ungeschwärzt bleibt. AR-08 deckt nur das öffentliche Roh-PDF im Repo ab. Es deckt nicht die ausdrückliche Zusage „nicht ausgeliefert“. Falls die Namen der Amtsträger bewusst bleiben sollen, muss das als Entscheidung dokumentiert werden. Die Unterschriften sind biometrische Merkmale und sollten trotzdem weg.

Auf den übrigen Treffer-Seiten (17, 18, 32, 48, 75, 95) habe ich nur Amtsbezeichnungen, Fließtext und „Telefonbucheintrag“ gesehen, also falsch-positive Treffer.
**Fix:** Eine seitenbezogene Schwärzkonfiguration einführen, weil `schwaerzen_nach` (Folgezeile eines Etiketts) die Namenszeilen unter den Unterschriften nicht trifft. Zum Beispiel in `2026.toml`:
```toml
[layout.quellenbelege]
schwaerzen_bereiche = [ { seite = 9, rechtecke = [[90, 700, 300, 780], [400, 700, 600, 780]] } ]
```
`_Schwaerzung.fuer` führt diese Rechtecke mit den Personenfeldern zusammen. Danach alle Bilder dieser Seiten mit `--neu-rendern` neu erzeugen (siehe WR-01). Zusätzlich die Prüfliste zum Test machen: Ein Treffer ohne Schwärzung und ohne Eintrag in einer Allowlist (`pruefwoerter_ok = [{ seite = 18, stichwort = "Bürgermeister" }]`) bricht Schritt 08 ab.

### CR-02: `lighthouse-a11y.sh` löscht ein vom Nutzer übergebenes `LH_SCRATCH`-Verzeichnis vollständig

**File:** `scripts/lighthouse-a11y.sh:35-52`
**Issue:** Die Kopfdokumentation nennt `LH_SCRATCH` ein „vorhandenes Verzeichnis für die Scratch-Kopien“. Das Skript legt es bei Bedarf mit `mkdir -p` an und behandelt es dann wie ein eigenes Wegwerfverzeichnis. Der `EXIT`-Trap führt `rm -rf "$S"` aus, sofern nicht `LH_KEEP=1` gesetzt ist. Wer `LH_SCRATCH=$HOME/work ./scripts/lighthouse-a11y.sh` aufruft (der dokumentierte Weg), verliert beim Skriptende das gesamte Verzeichnis samt fremdem Inhalt. Der Trap greift auch bei einem Abbruch durch `set -e`. `LH_SCRATCH=/` oder ein leerer, aber falsch gesetzter Pfad wäre fatal. Die Fehlerunterdrückung `2>/dev/null || true` verdeckt zusätzlich, dass root-eigene Container-Dateien stehen bleiben.
**Fix:** Nur ein selbst angelegtes Unterverzeichnis löschen und `LH_SCRATCH` nur als Elternverzeichnis verwenden:
```bash
BASIS="${LH_SCRATCH:-${TMPDIR:-/tmp}}"
mkdir -p "$BASIS"
S="$(mktemp -d "$BASIS/lighthouse-a11y.XXXXXX")"   # immer ein frisches, eigenes Verzeichnis
```
Der Trap löscht dann nur `$S`. Zusätzlich vor dem `rm -rf` prüfen, dass `$S` nicht leer ist und nicht `/` oder `$HOME` entspricht.

## Warnings

### WR-01: Geänderte Schwärzung wirkt nicht auf vorhandene Bilder (veraltete, ungeschwärzte Datei bleibt erhalten)

**File:** `pipeline/ostbevern/belegbilder.py:87-96`, `pipeline/alle.py:176`, `.github/workflows/ci.yml:57-63`
**Issue:** `rendere_seiten` rendert nur Seiten, deren Datei fehlt (`neu or not exists`). `alle.py` ruft Schritt 08 ohne `neu_rendern` auf, und CI prüft nur, dass `alle.py` unter `app/public/quellen` nichts anlegt oder ändert. Trägt jemand später ein Etikett in `schwaerzen_nach` ein (der Bericht fordert das ausdrücklich: „trägt es in `schwaerzen_nach` ein“) oder ändert er die Personenfeld-Erkennung, bleibt das alte, womöglich ungeschwärzte Bild liegen. Weder Pipeline noch CI melden das. Die Prüfung am Funktionsanfang gilt nur für `produktinformationen`-Seiten ohne Rechtecke und prüft nicht den Inhalt vorhandener Dateien.
**Fix:** Einen Schwärzungs-Fingerprint je Seite in `quellen.json` oder in einer Datei `app/public/quellen/.schwaerzung.json` ablegen (Hash der Rechtecke je Seite). `rendere_seiten` rendert dann jede Seite neu, deren Fingerprint von dem der vorhandenen Datei abweicht. Mindestens in `quellenbelege.md` und in den Hilfetext von `08_quellenbelege.py` den Hinweis „nach Änderung der Schwärzung `--neu-rendern` aufrufen“ aufnehmen.

### WR-02: `rendere_seiten` schreibt nicht atomar; ein Abbruch hinterlässt ein kaputtes Bild, das nie erneuert wird

**File:** `pipeline/ostbevern/belegbilder.py:96-113`
**Issue:** `bild.save(pfad, "WEBP", ...)` schreibt direkt ins Ziel. Bricht der Lauf mitten im Schreiben ab (Strg-C, Plattenvoll, Container-Kill), steht eine abgeschnittene `.webp` im Verzeichnis. Beim nächsten Lauf gilt sie wegen `.exists()` als vorhanden und wird nicht erneuert. Das widerspricht dem sonst konsequent atomaren Schreiben (`schreibe_app_json` nutzt tempfile + `os.replace`). Die App zeigt dann im Seitenbild den Fehlerhinweis, CI merkt es nicht.
**Fix:**
```python
tmp = pfad.with_suffix(".webp.tmp")
bild.save(tmp, "WEBP", quality=WEBP_QUALITAET, method=WEBP_METHODE)
tmp.replace(pfad)
```
Ein `try/finally` räumt die Temp-Datei bei Fehlern weg.

### WR-03: Unbehandelte Indexfehler in der Beleg-Suche umgehen die `QuellenFehler`-Behandlung

**File:** `pipeline/ostbevern/quellen.py:371`, `:1045`, `:652`; `pipeline/08_quellenbelege.py:36-47`, `pipeline/alle.py:150-165`
**Issue:** Mehrere Stellen setzen gültige Eingaben voraus und werfen sonst rohe `IndexError`s:
- `finde_tabellenzeile` liest `werte[ziel_index]` (Zeile 371). Ist die Werteliste kürzer als die Jahre, folgt ein `IndexError`.
- `_sammle_vorbericht` liest `gesamt_df["posten_name"][0]` (Zeile 1045), obwohl `gesamt["quelle"]` nur geprüft wird, nicht ob die CSV eine `ist_gesamt`-Zeile hat.
- `finde_stellenzeile` ruft `gruppe.split()[0]` auf (Zeile 652). Eine leere oder rein aus Leerraum bestehende Gruppenbezeichnung einer Nachwuchszeile führt zum Absturz.

`08_quellenbelege.py` und `alle.py` fangen nur die dokumentierten Fehlerklassen und geben bei den obigen Fällen einen Traceback statt `Fehler: …` mit Exit 1 aus.
**Fix:** Die Eingaben vor dem Zugriff prüfen und als `QuellenFehler` melden, zum Beispiel:
```python
if ziel_index >= len(werte):
    raise QuellenFehler(f"Tabellenzeile {bezeichnung!r}: kein Wert für Jahresindex {ziel_index}")
...
if gesamt_df.height == 0:
    raise QuellenFehler(f"Tabelle {tabelle}: gesamt_vorbericht.quelle gesetzt, aber keine ist_gesamt-Zeile")
...
woerter = gruppe.split()
if not woerter:
    raise QuellenFehler(f"{schluessel}: leere Gruppenbezeichnung")
```

### WR-04: Leere Listen sind jetzt für jeden `[layout.*]`-Schlüssel erlaubt, auch für die Datenschutz-Prüfwörter

**File:** `pipeline/ostbevern/konfiguration.py:381-391`, `pipeline/jahrgaenge/2026.toml:209`
**Issue:** Für `schwaerzen_nach = []` wurde die Validierung global gelockert: Jede Layout-Liste darf jetzt leer sein. Bisher fing der Ladevorgang so Tippfehler und ein versehentliches Leeren ab. Ein leeres `pruefwoerter = []` schaltet die Datenschutz-Prüfliste lautlos ab. Der Bericht enthält dann einfach keine Treffer und sieht „sauber“ aus. Auch in `layout.investitionen` und anderen Bereichen würden leere Listen jetzt durchgehen.
**Fix:** Die Lockerung auf eine ausdrückliche Allowlist beschränken, zum Beispiel `LEERE_LISTE_ERLAUBT = {("quellenbelege", "schwaerzen_nach")}`, und für `pruefwoerter` eine nicht-leere Liste verlangen. Alle anderen Schlüssel behalten die alte Prüfung.

### WR-05: Startseiten-Kacheln „Erträge“ und „Aufwendungen“ tragen kein „berechnet“, die Seitenleiste nennt sie aber „nicht im PDF“

**File:** `app/src/lib/kennzahlen.ts:117-138`, `app/src/lib/quelle.ts:162-172`
**Issue:** `baueKennzahlen` setzt für Erträge und Aufwendungen `berechnet: false`, übergibt aber eine `herleitung` („Ordentliche Erträge (Zeile 10) plus Finanzerträge (Zeile 14)“). `belegHinweis` wertet jede Nicht-`null`-Herleitung als berechneten Wert. Die Seitenleiste zeigt dann „Berechneter Wert – Dieser Wert steht nicht im PDF. Er wird berechnet: …“. Die Kachel selbst zeigt kein „berechnet“-Etikett. Dasselbe gilt für `ebenenBeleg` im Modus Aufwand mit Zinsen. Die Kachel und ihre Quellenansicht widersprechen sich also auf der wichtigsten Seite der App, für den Kernwert „jede Zahl ist belegt“. Der Test `kennzahlen.test.ts:57-61` hält „nur die beiden Pro-Kopf-Werte sind berechnet“ ausdrücklich fest.
**Fix:** Eine Linie ziehen. Entweder `berechnet: true` für alle Kacheln mit Herleitung und den Test anpassen. Oder die Herleitungstexte so formulieren, dass `belegHinweis` für gedruckte Summenzeilen die Art `markiert` zurückgibt (eigenes Feld `summe` statt Herleitung) und der Satz „Dieser Wert steht nicht im PDF“ nur bei echten Berechnungen erscheint.

## Info

### IN-01: Spalte „geschwärzt“ der Datenschutz-Prüfliste gilt je Seite, nicht je Treffer

**File:** `pipeline/ostbevern/quellen.py:1365-1367`
**Issue:** Eine Seite mit Schwärzung zeigt für jeden Treffer „ja“, auch wenn der Treffer in einer Zeile steht, die nicht geschwärzt ist (z. B. Seite 79, „Bürgermeister“ in den Zeilen 31 und 45). Die Spalte suggeriert mehr Schutz, als sie belegt.
**Fix:** Die Zeile des Treffers mit den Schwärzflächen der Seite vergleichen (`_schneidet`) und nur dann „ja“ schreiben.

### IN-02: `minderaufwandHinweis` formuliert bei positivem GEP-Wert einen negativen „Minderaufwand“

**File:** `app/src/lib/aufwandsarten.ts:172-182`
**Issue:** `betrag = -wert` wird nur für `wert === 0` ausgeschlossen. Ist die Zeile in einem Jahr positiv (Mehraufwand), steht im Satz „globalen Minderaufwand von −… €“. Bei den heutigen Daten tritt das nicht auf.
**Fix:** `if (wert >= 0) return null`, oder den Satz an das Vorzeichen anpassen.

### IN-03: `istAufwandsart` vergleicht Zeilennummern als Zeichenketten

**File:** `app/src/lib/aufwandsarten.ts:30-35`
**Issue:** `nummer >= '11' && nummer <= '16'` ist ein lexikographischer Vergleich. Er funktioniert für zweistellige Nummern, bricht aber bei Nummern wie `"1"`, `"100"` oder `"15a"` stillschweigend.
**Fix:** Eine Menge `new Set(['11','12','13','14','15','16','20'])` verwenden, wie es an anderen Stellen schon üblich ist.

### IN-04: Fest codierter Farbwert in `StellenNachGruppe`

**File:** `app/src/components/StellenNachGruppe.vue:36`
**Issue:** `KATEGORIE_FARBEN[1] ?? '#545868'` verletzt die Konvention „Chartfarben ausschließlich aus `echartsTheme.ts`“. Der Rückfall ist tote Verzweigung, solange die Palette mindestens zwei Einträge hat.
**Fix:** Den Rückfall entfernen oder in `echartsTheme.ts` als benannte Konstante ablegen.

### IN-05: `schulden.ts` erfindet im Tooltip Nullwerte

**File:** `app/src/lib/schulden.ts:337-340`
**Issue:** `euro(reihen.investitionskredite[index] ?? 0)` und die drei Folgezeilen zeigen bei fehlendem Wert „0 €“, entgegen der Regel „nie 0 erfinden“. Die Längenprüfung in `baueSchuldenstand` macht den Fall unerreichbar, der Rückfall ist aber irreführend, falls die Prüfung je entfällt.
**Fix:** Bei `undefined` den Tooltip mit `KEIN_WERT` füllen oder die Zeile weglassen.

### IN-06: Quell-Seitenleiste nennt bei Zeitreihen nur das Jahr als Bezeichnung

**File:** `app/src/components/DatenTabelle.vue:70-74`, `app/src/components/SteuerZeitreihe.vue:96-104`
**Issue:** `zeilenBezeichnung` nimmt den Wert der ersten sichtbaren Spalte. In der Tabelle der Steuer-Zeitreihe ist das nur „2026“. Knopfname („Quelle anzeigen: 2026, PDF-Seite 31“) und Kopfzeile der Seitenleiste nennen dann nicht, um welche Steuerart es geht, obwohl die Auswahl nur im Formular steht.
**Fix:** Der Tabelle eine optionale Prop `bezeichnungPraefix` geben, in `SteuerZeitreihe` etwa den Namen der gewählten Steuerart.

### IN-07: Veralteter und lockerer Rahmen

**File:** `README.md:5`, `app/package.json:6-22,45-47`, `app/tsconfig.node.json`, `.github/workflows/ci.yml:17-19`
**Issue:**
- Das README nennt als „Stand“ noch „Phase 1: Gerüst …“, die App ist inzwischen veröffentlichungsreif.
- `format:check` prüft nur `src/`, nicht `e2e/` und `scripts/`.
- `engines.node` verlangt Node 22, `tsconfig.node.json` erbt von `@tsconfig/node24`.
- Der Workflow startet auf `push` und `pull_request` jeweils alle Jobs, ein Branch mit offenem PR läuft doppelt.
**Fix:** README-Abschnitt „Stand“ aktualisieren, `prettier --check src/ e2e/` verwenden, die Node-Basis vereinheitlichen und `push` auf `branches: [main]` beschränken (PRs decken die übrigen ab).

### IN-08: Beleg-Link auf die Gemeinde-PDF ist an einen inhaltsgebundenen Pfad geknüpft

**File:** `app/src/config.ts:42-43`
**Issue:** `ORIGINAL_PDF_URL` enthält den Hash-Pfad `/_Resources/Persistent/3/2/6/0/3260f0ed…/Haushalt%202026%20komplett.pdf`. Ersetzt die Gemeinde die Datei (Korrektur, Nachtragshaushalt), liefert die URL 404. Dann brechen alle „Seite n im Original-PDF öffnen“-Links, ohne dass Tests es merken (die Smoke-Tests prüfen nur Anfragen an den eigenen Server).
**Fix:** Einen kleinen CI- oder Release-Check (HEAD-Request) für die URL einplanen oder im README die Pflege der URL als Aufgabe beim Jahrgangswechsel festhalten.

---

_Reviewed: 2026-10-07_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
