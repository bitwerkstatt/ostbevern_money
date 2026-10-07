---
phase: 07-feinschliff-und-veroeffentlichung
fixed_at: 2026-10-07T15:00:00Z
review_path: .planning/phases/07-feinschliff-und-ver-ffentlichung/07-REVIEW.md
iteration: 1
findings_in_scope: 14
fixed: 14
skipped: 0
status: all_fixed
---

# Phase 7: Code Review Fix Report

**Fixed at:** 2026-10-07
**Source review:** .planning/phases/07-feinschliff-und-ver-ffentlichung/07-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 14 (WR-08, IN-01 bis IN-13; Umfang `all`)
- Fixed: 14
- Skipped: 0

Nicht angefasst (Nutzerentscheidungen): CR-01 (Namen und Unterschriften auf Seite 9 bleiben, weder Bilder noch Schwärzung geändert) und die Summen auf der Startseite (nur die Kennzeichnung „berechnet“ auf den zwei Kacheln; keine Marker in `EbenenTabelle`).

**Verifikation (Ort):** Die Fixes wurden in einem isolierten Worktree (`.claude/worktrees/rf-07-…`) gemacht und per Fast-Forward auf `main` übernommen. Pipeline-Prüfungen liefen im Worktree (eigenes `uv sync --locked`), App-Prüfungen in einer Scratch-Kopie von `app/` mit frischem `npm ci` (Linux, Node 22.22.1, mit dem neuen `package-lock.json`), weil `app/node_modules` im Repo macOS-Binärdateien enthält. Die Läufe sind aus dem Hauptverzeichnis nicht ohne Weiteres reproduzierbar.

- `uv run --directory pipeline pytest`: 645 passed, 1 skipped (nach dem letzten Commit).
- `ruff check .` und `ruff format --check .`: grün.
- `uv run --directory pipeline python alle.py --jahr 2026`: nach IN-01 ändert sich nur `daten/pruefberichte/quellenbelege.md` (gewollt, siehe IN-01); `daten/` sonst und `app/src/data/` unverändert, 0 Bilder neu gerendert. Nach IN-13 erneut gelaufen: kein Diff.
- App (Scratch-Kopie, nach dem letzten App-Commit): `type-check`, `lint`, `format:check` (jetzt inklusive `e2e/`), `test` (1968 Tests), `build` grün; zusätzlich `tsc -p tsconfig.e2e.json --noEmit` und `eslint e2e/` fehlerfrei.
- **Playwright-E2E:** Lokal gelaufen über `scripts/e2e-wie-ci.sh` (Docker-Image `playwright:v1.63.0-noble` mit DejaVu Sans, Scratch-Kopie mit Linux-`node_modules` und Build vom letzten App-Stand): ohne `--project` startet das Skript jetzt nur `ci` (IN-10 bestätigt), 81 Tests grün inklusive der 5 Kachelbreiten-Tests; `--project=mobil` 14 grün, `--project=texte` 1 grün. Die verschärfte Schriftprüfung (IN-12) bestand, gemeldet wurde auf allen vier Routen genau `DejaVu Sans (DejaVuSans-Bold)`. **Nicht geprüft:** der echte GitHub-Runner (Workflow-Änderungen in `ci.yml` aus IN-07, IN-11, IN-12; die Paketversion und `fc-match` dort). Den ersten Lauf auf dem Runner vor dem Schutz von `main` abwarten.
- Der Pipeline-Test gegen `app/node_modules/typescript` (`test_formatiere.py`) wird im Worktree übersprungen, weil dort kein `node_modules` liegt.

## Fixed Issues

### WR-08: Eine beschädigte oder von Hand geänderte `belegbilder_schwaerzung.json` bricht Schritt 08 mit rohem Traceback ab

**Files modified:** `pipeline/ostbevern/belegbilder.py`, `pipeline/tests/test_belegbilder.py`
**Commit:** efb792e
**Applied fix:** `_lies_fingerprints` fängt `OSError` und `ValueError` beim Lesen und meldet `BelegbildFehler` („nicht lesbar … aus Git wiederherstellen“). Obertyp, nicht numerische Schlüssel und Nicht-String-Werte werden ebenfalls als `BelegbildFehler` abgewiesen, und zwar vor dem Rendern. Neuer parametrisierter Test (Konfliktmarker, Liste, Schlüssel `abc`, Zahlenwert), der zusätzlich prüft, dass kein Bild geschrieben wurde.

### IN-01: Spalte „geschwärzt“ der Datenschutz-Prüfliste gilt je Seite, nicht je Treffer

**Files modified:** `pipeline/ostbevern/quellen.py`, `pipeline/tests/test_quellen.py`, `daten/pruefberichte/quellenbelege.md`
**Commit:** 4d2f4bc
**Applied fix:** Die Prüfliste trägt je Treffer ein viertes Feld. Es ist `ja`, wenn die Mitte der Treffer-Zeile (und waagerechte Überlappung) in einem Schwärzrechteck der Seite liegt (`_zeile_geschwaerzt`). Die Mitte statt der ganzen Zeilenhöhe, damit der 2-pt-Rand eines Rechtecks nicht die Nachbarzeile mitzählt. Zwei neue Tests (Zeilenlogik, Berichtsformat). Der Bericht wurde neu erzeugt: acht Zeilen wechseln von `ja` auf `nein` (S. 74 Zeilen 5, 9, 14; S. 79 Zeilen 31, 45; S. 94 Zeile 5; S. 109 Zeile 29; S. 138 Zeile 14). Das ist nur der interne Prüfbericht, es ändern sich weder Bilder noch App-Daten. Hinweis für die Sichtung: Die Spalte benennt jetzt ehrlich, was nicht geschwärzt ist.

### IN-02: `minderaufwandHinweis` formuliert bei positivem GEP-Wert einen negativen „Minderaufwand“

**Files modified:** `app/src/lib/aufwandsarten.ts`
**Commit:** 53b96ac
**Applied fix:** `wert >= 0` (statt nur `=== 0`) liefert `null`; es gibt dann keinen Hinweis mit negativem Betrag. Bei den heutigen Daten (negativer Wert) ändert sich nichts, die bestehenden Tests sind grün. Kein neuer Test, weil die Daten fest sind und der Positivfall sich nur mit gemockten Daten erreichen ließe.

### IN-03: `istAufwandsart` vergleicht Zeilennummern als Zeichenketten

**Files modified:** `app/src/lib/aufwandsarten.ts`
**Commit:** c0d6a83
**Applied fix:** Menge `AUFWANDSART_NUMMERN` (`11`–`16`, `20`) mit `has` statt lexikographischem Vergleich.

### IN-04: Fest codierter Farbwert in `StellenNachGruppe`

**Files modified:** `app/src/charts/echartsTheme.ts`, `app/src/components/StellenNachGruppe.vue`, `app/src/components/StellenNachTeil.vue`
**Commit:** 3260357
**Applied fix:** `echartsTheme.ts` exportiert die benannten Konstanten `NEUTRAL_DUNKEL_FARBE` und `NEUTRAL_MITTEL_FARBE` (dieselben Tokens wie bisher, `KATEGORIE_FARBEN` nutzt sie). `StellenNachGruppe` verwendet sie ohne Hex-Rückfall. Dasselbe Muster (`?? '#545868'`, `?? '#9194a2'`) stand in der Schwesterkomponente `StellenNachTeil`; sie ist mit umgestellt. Die Farben sind unverändert.

### IN-05: `schulden.ts` erfindet im Tooltip Nullwerte

**Files modified:** `app/src/lib/schulden.ts`
**Commit:** da9da3b
**Applied fix:** Neue Hilfsfunktion `euroOderKeinWert`; fehlende Werte erscheinen im Tooltip als `KEIN_WERT` (–), nicht als „0 €“. Auch die Liquiditätszeile nutzt sie. Bei vollständigen Daten ist die Ausgabe identisch.

### IN-06: Quell-Seitenleiste nennt bei Zeitreihen nur das Jahr als Bezeichnung

**Files modified:** `app/src/components/DatenTabelle.vue`, `app/src/components/SteuerZeitreihe.vue`
**Commit:** 846c770
**Applied fix:** `DatenTabelle` hat die optionale Prop `bezeichnungPraefix`, die der Bezeichnung des Quellen-Knopfes vorangestellt wird. `SteuerZeitreihe` übergibt den Namen der gewählten Steuerart, der Knopf heißt dann z. B. „Quelle anzeigen: Gewerbesteuer 2026, PDF-Seite 31“ statt „… 2026 …“. Das ist der zugängliche Name und die Kopfzeile der Seitenleiste, kein Erklärtext. Andere Tabellen sind unverändert (Prop optional). Wenn die Formulierung anders sein soll (z. B. „Gewerbesteuer, 2026“), ist es eine Zeile in `zeilenBezeichnung`.

### IN-07: Veralteter und lockerer Rahmen

**Files modified:** `README.md`, `app/package.json`, `app/package-lock.json`, `app/tsconfig.node.json`, `.github/workflows/ci.yml`
**Commit:** 2cb379e
**Applied fix:** README-Abschnitt „Stand“ beschreibt jetzt Phasen 1 bis 7 und den noch offenen ersten Push. Node-Basis vereinheitlicht auf 22 (`.nvmrc`, `engines`, CI): `@tsconfig/node22` ^22.0.6 und `@types/node` ^22.20.5 statt der 24er-Pakete, `tsconfig.node.json` erbt von `@tsconfig/node22`. Die Lockdatei ändert nur diese Einträge (plus `undici-types`); `npm ci`, `type-check`, `lint`, `test` und `build` laufen damit grün. `push` startet nur noch auf `main` (Branches mit offenem Pull Request prüft `pull_request`). Der Teil „`format:check` prüft nur `src/`“ steht unter IN-11.

### IN-08: Beleg-Link auf die Gemeinde-PDF ist an einen inhaltsgebundenen Pfad geknüpft

**Files modified:** `README.md`
**Commit:** bf956ff
**Applied fix:** Neuer README-Abschnitt „Pflege beim Jahrgangswechsel“ hält fest, dass `ORIGINAL_PDF_URL` vor jeder Veröffentlichung einmal geöffnet und bei einem neuen Jahrgang erneuert wird. Einen automatischen HEAD-Request in der CI habe ich bewusst nicht ergänzt: Er würde die Veröffentlichung von der Erreichbarkeit einer fremden Website abhängig machen. Falls gewünscht, wäre ein eigener, nicht blockierender Job der saubere Weg.

### IN-09: Die behauptete Mindestreserve von 16 px wird nirgends geprüft und hängt an den Daten

**Files modified:** `app/src/styles/basis.css`, `README.md`
**Commit:** f3efd0a
**Applied fix:** Zweite Option des Befunds: Der CSS-Kommentar nennt die Reserve jetzt als „gemessen bei den Daten 2026“, beschreibt, dass der Test nur Überlauf prüft (>= -0,5 px) und die Reserve protokolliert, und verweist auf die Prüfung bei einem neuen Jahrgang. Dieselbe Prüfung steht als Punkt im README-Abschnitt „Pflege beim Jahrgangswechsel“. Eine harte Schwelle (`spurreserve >= 8`) habe ich nicht eingebaut, weil ich den E2E-Lauf hier nicht ausführen kann und eine falsch gesetzte Schwelle die Test-CI bricht.

### IN-10: `e2e-wie-ci.sh` führt ohne Argumente alle Playwright-Projekte aus und lädt ohne Zeitlimit über HTTP

**Files modified:** `scripts/e2e-wie-ci.sh`
**Commit:** f024de9
**Applied fix:** Ohne `--project` unter den Argumenten wird `--project=ci` vorangestellt (wie die CI); der Kopfkommentar beschreibt das. `curl` bekommt `--max-time 60 --retry 2`. HTTP bleibt (die feste SHA-256 prüft den Inhalt). Geprüft mit `bash -n`, der Argumentlogik (leer, nur Datei, explizites Projekt) und einem echten Lauf ohne `--project` (nur `ci`, 81 Tests).

### IN-11: Neue Spec ist nicht prettier-konform, und `format:check` sieht `e2e/` nicht

**Files modified:** `app/e2e/kacheln.spec.ts`, `app/e2e/smoke.spec.ts`, `app/package.json`, `.github/workflows/ci.yml`
**Commit:** a3f05af
**Applied fix:** `prettier --write` auf `e2e/` (neben `kacheln.spec.ts` meldete auch `smoke.spec.ts` einen reinen Formatierungsverstoß; es ändert sich nur der Umbruch). `format` und `format:check` prüfen jetzt `src/ e2e/`. Der CI-Schritt heißt „Browser-Tests (Playwright + axe + Kachelbreiten)“.

### IN-12: Die Schriftprüfung der CI ist schwächer als ihre Beschreibung (Teilzeichenfolge, Version nur protokolliert)

**Files modified:** `app/e2e/kacheln.spec.ts`, `.github/workflows/ci.yml`
**Commit:** 8523030
**Applied fix:** `schriftDerBetraege` liefert die Einträge einzeln; der Test verlangt, dass es mindestens einen gibt und jeder mit `DejaVu Sans (` beginnt. `DejaVu Sans Mono`, `Condensed` und Ersatzglyphen anderer Schriften fallen damit durch. Der beobachtete Wert in den Docker-Läufen von Plan 07-14 war überall genau `DejaVu Sans (DejaVuSans-Bold)`. Im Workflow-Schritt steht jetzt ein Kommentar: Die Paketversion wird nur ausgegeben (Kalibrierstand 2.37-8) und nicht erzwungen, damit ein Image-Update die Veröffentlichung nicht ohne Not blockiert; `fc-match` ist nur ein Indiz, verbindlich sind die Spec und der Breitentest. Eine harte Versionsprüfung wäre eine Entscheidung über das Blockieren von Deployments und ist offen gelassen. Die verschärfte Prüfung bestand lokal im Docker-Lauf; auf einem echten Runner ist sie noch nicht gelaufen (**requires human verification**: ersten Lauf abwarten, bevor `main` damit geschützt wird).

### IN-13: Die Absicherung aus WR-03 ist lückenhaft platziert, und gleichartige Zugriffe bleiben ungeschützt

**Files modified:** `pipeline/ostbevern/quellen.py`, `pipeline/tests/test_quellen.py`
**Commit:** 22ad206
**Applied fix:** In `finde_tabellenzeile` steht die Prüfung `0 <= ziel_index < len(werte)` jetzt am Funktionsanfang, unabhängig vom PDF-Inhalt (Test: keine passende Zeile, zu kurze Liste). Der Zugriff `teil["posten_name"][0]` in `_sammle_schuldenstand` war bereits durch `if teil.height == 0: raise QuellenFehler` abgesichert (der Befund bezog sich auf einen älteren Stand); dafür habe ich den gleichartigen Zugriff `produkt["pdf_seiten"][0]` in `_sammle_produkte` abgesichert (`QuellenFehler` bei leerer Liste, mit Test). Für den `ist_gesamt`-Fall in `_sammle_vorbericht` gibt es jetzt einen Test mit einer Tabelle ohne Gesamtzeile. Nach dem Lauf von `alle.py --jahr 2026`: kein Diff in `daten/` und `app/src/data/`.

## Skipped Issues

None — all findings were fixed.

---

_Fixed: 2026-10-07_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
