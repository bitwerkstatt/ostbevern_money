---
phase: 07-feinschliff-und-veroeffentlichung
reviewed: 2026-10-07T14:00:00Z
depth: standard
files_reviewed: 24
files_reviewed_list:
  - .github/workflows/ci.yml
  - app/e2e/kacheln.spec.ts
  - app/src/lib/__tests__/kennzahlen.test.ts
  - app/src/lib/kennzahlen.ts
  - daten/zwischen/belegbilder_schwaerzung.json
  - pipeline/08_quellenbelege.py
  - pipeline/ostbevern/belegbilder.py
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/quellen.py
  - pipeline/tests/test_belegbilder.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_quellen.py
  - scripts/lighthouse-a11y.sh
  - README.md
  - app/package.json
  - app/tsconfig.node.json
  - app/src/lib/aufwandsarten.ts
  - app/src/lib/schulden.ts
  - app/src/components/StellenNachGruppe.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/SteuerZeitreihe.vue
  - app/src/config.ts
  - app/src/styles/basis.css
  - scripts/e2e-wie-ci.sh
findings:
  critical: 0
  warning: 1
  info: 13
  total: 14
status: issues_found
---

# Phase 7: Code Review Report

**Reviewed:** 2026-10-07
**Depth:** standard
**Files Reviewed:** 24 (13 Dateien des Fix-Diffs `a866275..HEAD` plus die Dateien der weitergeführten Info-Befunde)

## Summary

Inkrementelle Nachprüfung der Fix-Commits `cbbf3db..3db0795` (CR-02, WR-01 bis WR-07). CR-01 bleibt nach Nutzerentscheidung vom 2026-10-07 unverändert und wird hier nicht erneut gemeldet.

Die Korrekturen sind im Kern richtig und vollständig. Geprüft habe ich sie durch Lesen des Diffs und der Gegenstellen. Außerdem sind `pytest` für `test_belegbilder.py`, `test_konfiguration.py` und `test_quellen.py` (130 Tests) und die Zählung der Fingerprints in `daten/zwischen/belegbilder_schwaerzung.json` gelaufen. App-Werkzeug und Playwright habe ich in der Sandbox nicht ausgeführt.

- **CR-02 (`lighthouse-a11y.sh`):** Das Skript legt immer ein eigenes Unterverzeichnis per `mktemp -d` an, und der Trap löscht nur dieses. `LH_SCRATCH` wird nie gelöscht. Der Schutz vor `""`, `/` und `$HOME` ist beim Aufbau mit `mktemp` nicht erreichbar, schadet aber nicht.
- **WR-01 (Schwärz-Fingerprint):** Die Logik stimmt. Neu gerendert wird bei fehlendem Bild, bei `neu` und bei geändertem Fingerprint. Ein vorhandenes Bild ohne Fingerprint wird nur übernommen, und der Fingerprint wird erst nach dem Schreiben gespeichert. In der eingecheckten Datei stehen 231 Seiten: 168 mit dem Fingerprint der leeren Rechteckliste, 63 mit Rechtecken. Offen bleibt die Robustheit beim Lesen der Datei (WR-08).
- **WR-02 (atomares Schreiben):** `.tmp` plus `replace` plus `finally`-Aufräumen ist korrekt. Der Test deckt den Abbruch ab.
- **WR-03 (Indexfehler):** Die drei benannten Stellen sind abgesichert. Schwestern derselben Fehlerklasse bleiben (IN-13).
- **WR-04 (leere Listen):** `LEERE_LISTE_ERLAUBT` ist eng gefasst. `pruefwoerter = []` und `kennzahlen_ergebnisplan = []` werden abgewiesen. In `2026.toml` ist `schwaerzen_nach` die einzige leere Liste.
- **WR-05 (Kennzeichnung „berechnet“):** `berechnet` wird für `ertraege` und `aufwendungen` gesetzt, so wie es die Nutzerentscheidung vorgibt. Die Etikett-Zeile bricht um, weil das `BerechnetEtikett` ein Inline-Block ist. Das ist auf der Seite der Pro-Kopf-Kacheln schon erprobt. Dort verlängert sich nur die Höhe.
- **WR-06 und WR-07 (E2E):** Beide Änderungen sind plausibel. Neu ist der Workflow-Schritt für die Schrift (siehe IN-12 zu den Grenzen der Prüfung).

Neu offen sind eine WARNING (WR-08) und zwei Info-Punkte (IN-12, IN-13). Kein neuer BLOCKER.

Hinweis zur Fortschreibung: IN-01 bis IN-11 sind unverändert offen und mit ihren Original-IDs und -Titeln übernommen. Zeilennummern, die sich durch die Fixes verschoben haben, sind angepasst (IN-09, IN-11). Kein Befund ist entfallen.

## Warnings

### WR-08: Eine beschädigte oder von Hand geänderte `belegbilder_schwaerzung.json` bricht Schritt 08 mit rohem Traceback ab

**File:** `pipeline/ostbevern/belegbilder.py:55-72`
**Issue:** Die neue Datei ist eingecheckt, generiert und damit ein typischer Kandidat für Merge-Konflikte (Konfliktmarker `<<<<<<<` in 231 Zeilen). `_lies_fingerprints` ruft `json.loads` ohne Absicherung auf. Ein Syntaxfehler löst `json.JSONDecodeError` aus, und `08_quellenbelege.py:48-55` fängt nur `QuellenFehler`, `BelegbildFehler` und die weiteren Projektfehler, nicht `ValueError`. Das Ergebnis ist ein Traceback statt `Fehler: …` mit Exit 1, also genau die Fehlerklasse, die WR-03 gerade bereinigt hat. `_schreibe_fingerprints` sortiert außerdem mit `int(e[0])`. Ein nicht numerischer Schlüssel (von Hand geändert, Fremdwerte) wirft ebenfalls `ValueError`, und zwar erst am Ende des Laufs, nachdem Bilder neu gerendert wurden. Die Prüfung `isinstance(daten, dict)` deckt nur die Obertypen ab. Ein Wert, der kein String ist, wird still per `str(wert)` umgedeutet und führt zu einem unnötigen Neurendern.
**Fix:**
```python
try:
    daten = json.loads(pfad.read_text(encoding="utf-8"))
except (OSError, ValueError) as fehler:
    raise BelegbildFehler(f"{pfad.name}: nicht lesbar ({fehler}); aus Git wiederherstellen") from fehler
if not isinstance(daten, dict) or not all(
    str(k).isdecimal() and isinstance(v, str) for k, v in daten.items()
):
    raise BelegbildFehler(f"{pfad.name}: erwartet ein JSON-Objekt Seite -> Fingerprint-String")
```
Dazu ein Test mit kaputtem JSON, der `BelegbildFehler` erwartet.

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

### IN-09: Die behauptete Mindestreserve von 16 px wird nirgends geprüft und hängt an den Daten

**File:** `app/src/styles/basis.css:20-25`, `app/e2e/kacheln.spec.ts:197-198,271,384` (Zeilen seit den Fixes verschoben)
**Issue:** Der CSS-Kommentar begründet 13,25rem mit „mindestens 16 px Reserve“. `reserve` und `spurreserve` werden aber nur protokolliert; geprüft wird lediglich `>= -0,5 px`. Die Reserve entspricht etwa einer Ziffer in DejaVu Sans Bold bei `--wa-font-size-l`. Ein anderer Jahrgang mit einem Betrag wie „rd. 100,1 Mio. €“ kann daher die Test-CI brechen, obwohl Layout und Kalibrierung unverändert sind (Nutzerschriften sind meist schmaler als DejaVu, die Praxis ist also unkritisch). Der Zusammenhang zwischen Daten und Mindestspur ist nirgends dokumentiert.
**Fix:** Entweder eine Mindestreserve prüfen (`spurreserve >= 8`) und beim Jahrgangswechsel im README als Prüfpunkt vermerken, oder den Kommentar ehrlich formulieren („gemessene Reserve bei den Daten 2026“).

### IN-10: `e2e-wie-ci.sh` führt ohne Argumente alle Playwright-Projekte aus und lädt ohne Zeitlimit über HTTP

**File:** `scripts/e2e-wie-ci.sh:83-100,57-61`
**Issue:** Das Skript heißt „wie CI“, startet ohne weitere Argumente aber `npx playwright test` mit allen Projekten (`ci`, `mobil`, `texte`); die CI nutzt `--project=ci`. Der Download per `curl -fsSL` hat kein `--max-time` und nutzt unverschlüsseltes HTTP (die feste SHA-256 fängt Manipulation ab, ein hängender Spiegel blockiert aber unbegrenzt).
**Fix:** `if ! printf '%s\n' "$@" | grep -q -- '--project'; then set -- --project=ci "$@"; fi` vor dem `docker run` und `curl --max-time 60 --retry 2`.

### IN-11: Neue Spec ist nicht prettier-konform, und `format:check` sieht `e2e/` nicht

**File:** `app/e2e/kacheln.spec.ts:244`, `app/package.json:18-19` (Zeile seit den Fixes verschoben, vorher 227)
**Issue:** `prettier --check e2e/kacheln.spec.ts` meldet einen Verstoß (überlange `befunde.push`-Zeile mit `overflow-x`). Die CI fällt nicht darüber, weil `format:check` nur `src/` prüft (siehe IN-07). Ebenso trägt der Schritt „Smoke-Test (Playwright + axe)“ in `ci.yml` jetzt auch den Breitentest, der Name ist veraltet.
**Fix:** `prettier --write e2e/kacheln.spec.ts`, `format`/`format:check` auf `src/ e2e/` erweitern (löst IN-07 teilweise) und den Schrittnamen in „Browser-Tests (Playwright + axe + Kachelbreiten)“ ändern.

### IN-12: Die Schriftprüfung der CI ist schwächer als ihre Beschreibung (Teilzeichenfolge, Version nur protokolliert)

**File:** `app/e2e/kacheln.spec.ts:36,466-473`, `.github/workflows/ci.yml:96-106`
**Issue:** Die Spec prüft `schrift` mit `toContain('DejaVu Sans')`. Der Test trifft auch `DejaVu Sans Mono`, `DejaVu Sans Condensed` oder `DejaVu Sans ExtraLight`, die andere Zeichenbreiten haben. `schriftDerBetraege` fügt mehrere Plattformschriften zu einem String zusammen, sodass ein Fallback-Glyph aus DejaVu die Prüfung erfüllt, obwohl der Betrag überwiegend in einer anderen Schrift steht. Der Workflow installiert `fonts-dejavu-core` ohne Version (bewusst, siehe Fix-Bericht) und gibt die Version nur aus. Der Kommentar nennt 2.37-8 als Kalibrierstand, aber nichts bricht, wenn der Runner eine andere Version liefert. `fc-match sans-serif` ist außerdem nur ein Indiz für die Auswahl von `system-ui` in Chromium; es hat in der CI noch nie auf einem echten Runner gelaufen (Hinweis „requires human verification“ im Fix-Bericht).
**Fix:** Die Spec exakt gegen `^DejaVu Sans \(` (Familienname vor der PostScript-Klammer) für alle gemeldeten Einträge prüfen oder die Liste der Plattformschriften auf genau einen Eintrag begrenzen. Im Workflow die Version vergleichen: `test "$(dpkg-query -W -f='${Version}' fonts-dejavu-core)" = "2.37-8"` mit klarer Meldung, oder im Kommentar festhalten, dass die Version nur informativ ist. Den ersten echten Lauf auf dem Runner abwarten, bevor `main` damit geschützt wird.

### IN-13: Die Absicherung aus WR-03 ist lückenhaft platziert, und gleichartige Zugriffe bleiben ungeschützt

**File:** `pipeline/ostbevern/quellen.py:374-379`, `:1121`, `:1061`
**Issue:**
- In `finde_tabellenzeile` steht die neue Prüfung `0 <= ziel_index < len(werte)` hinter `if not kandidaten: return None, GRUND_NICHT_GEFUNDEN`. Ein zu kurzes `werte` bleibt unbemerkt, solange keine Kandidatenzeile gefunden wird, und fällt erst auf, sobald eine gefunden wird. Das Verhalten hängt vom PDF-Inhalt ab.
- `name = teil["posten_name"][0]` in Zeile 1121 hat dieselbe Fehlerklasse wie die behobenen Stellen: Eine leere Gruppe führt zu `IndexError` statt `QuellenFehler`.
- Für die neue Prüfung in `_sammle_vorbericht` (Zeile 1056-1060, `ist_gesamt` fehlt) gibt es keinen Test; der Fix-Bericht nennt das selbst.
**Fix:** Die Prüfung der Indexgrenze an den Funktionsanfang verlegen. Eine Gruppe `teil` vor Zeile 1121 auf `height == 0` prüfen und `QuellenFehler` auslösen. Für den `ist_gesamt`-Fall einen Test mit einer Tabelle ohne Gesamtzeile ergänzen.

---

_Reviewed: 2026-10-07T14:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
