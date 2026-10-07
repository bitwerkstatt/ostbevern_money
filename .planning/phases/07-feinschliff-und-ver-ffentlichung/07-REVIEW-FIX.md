---
phase: 07-feinschliff-und-veroeffentlichung
fixed_at: 2026-10-07T13:00:00Z
review_path: .planning/phases/07-feinschliff-und-ver-ffentlichung/07-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 7
skipped: 1
status: partial
---

# Phase 7: Code Review Fix Report

**Fixed at:** 2026-10-07
**Source review:** .planning/phases/07-feinschliff-und-ver-ffentlichung/07-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (CR-01, CR-02, WR-01 bis WR-07; Info-Befunde sind außerhalb des Umfangs)
- Fixed: 7
- Skipped: 1 (CR-01, Nutzerentscheidung)

**Verifikation (Ort):** Die Fixes wurden in einem isolierten Worktree (`.claude/worktrees/rf-07-…`) gemacht und danach per Fast-Forward auf `main` übernommen; der Worktree ist entfernt. Pipeline-Prüfungen liefen im Worktree (eigenes `uv sync --locked`), App-Prüfungen in einer Scratch-Kopie von `app/` mit frischem `npm ci` (Linux, Node 22.22.1), weil `app/node_modules` im Repo macOS-Binärdateien enthält. Die Läufe sind aus dem Hauptverzeichnis nicht ohne Weiteres reproduzierbar.

- `uv run --directory pipeline pytest`: 636 passed, 1 skipped (der Test gegen `app/node_modules/typescript` wird im Worktree übersprungen, weil dort kein `node_modules` liegt).
- `ruff check .` und `ruff format --check .`: grün.
- `uv run --directory pipeline python alle.py --jahr 2026`: `git status` für `daten/` und `app/src/data/` danach sauber; einzige Änderung ist die neue Datei `daten/zwischen/belegbilder_schwaerzung.json` (WR-01, eingecheckt). `app/public/quellen` unverändert, 0 Bilder neu gerendert.
- App (Scratch-Kopie): `type-check`, `lint`, `format:check`, `test` (1968 Tests) grün; zusätzlich `tsc -p tsconfig.e2e.json` und ESLint auf `e2e/kacheln.spec.ts` fehlerfrei.
- **Playwright-E2E (`npm run test:e2e`) wurde NICHT ausgeführt.** In der Sandbox gibt es keine Playwright-Browser. Verifiziert ist nur, dass `playwright test --list` die Spec lädt (5 Tests). Die Änderungen an `kacheln.spec.ts` (WR-06, WR-07) und am Workflow-Schritt (WR-06, YAML geparst) sind nicht gegen einen echten Runner geprüft.
- Bekannt, nicht von mir verursacht: `prettier --check e2e/kacheln.spec.ts` meldet weiterhin die Zeile `befunde.push(…overflow-x…)` (IN-11, außerhalb des Umfangs; `format:check` prüft `e2e/` nicht).

## Fixed Issues

### CR-02: `lighthouse-a11y.sh` löscht ein vom Nutzer übergebenes `LH_SCRATCH`-Verzeichnis vollständig

**Files modified:** `scripts/lighthouse-a11y.sh`
**Commit:** cbbf3db
**Applied fix:** `LH_SCRATCH` ist jetzt nur das Elternverzeichnis (Standard `$TMPDIR` bzw. `/tmp`); das Skript legt per `mktemp -d "$BASIS/lighthouse-a11y.XXXXXX"` immer ein eigenes Unterverzeichnis an, und der `EXIT`-Trap löscht nur dieses. Zusätzlich verweigert der Trap das Löschen bei leerem Pfad, `/` oder `$HOME`. Kopfkommentar angepasst. `bash -n` fehlerfrei; das Skript selbst (Docker) wurde nicht ausgeführt.

### WR-01: Geänderte Schwärzung wirkt nicht auf vorhandene Bilder

**Files modified:** `pipeline/ostbevern/belegbilder.py`, `pipeline/ostbevern/quellen.py`, `pipeline/08_quellenbelege.py`, `pipeline/tests/test_belegbilder.py`, `daten/zwischen/belegbilder_schwaerzung.json` (neu)
**Commit:** 86f1858
**Applied fix:** `rendere_seiten` bekommt `fingerprint_pfad`. Je Seite wird ein Hash der (auf 2 Nachkommastellen gerundeten) Schwärzungsrechtecke gespeichert; weicht er vom gespeicherten Wert ab, wird das vorhandene Bild neu gerendert. Ein vorhandenes Bild ohne gespeicherten Fingerprint wird nur übernommen (nicht neu gerendert), damit die veröffentlichten Bilder unverändert bleiben. Neu gerenderte Seiten bekommen ihren Fingerprint erst nach erfolgreichem Schreiben. Der Fingerprint liegt bewusst in `daten/zwischen/` statt unter `app/public/quellen`, damit nichts zusätzlich ausgeliefert wird. Hilfetext von `--neu-rendern` nennt das. Zwei neue Tests (geänderte Schwärzung rendert neu; Übernahme ohne Fingerprint).
**Hinweis:** Das ist eine Änderung an generierten Daten (eine neue, kleine JSON-Datei, 231 Seiten); veröffentlichte Bilder und `app/src/data` sind unverändert. Der Fingerprint ersetzt keinen Beweis, dass bereits vorhandene Bilder zur aktuellen Schwärzung passen (sie werden beim ersten Lauf übernommen).

### WR-02: `rendere_seiten` schreibt nicht atomar

**Files modified:** `pipeline/ostbevern/belegbilder.py`, `pipeline/tests/test_belegbilder.py`
**Commit:** 3134eae
**Applied fix:** Das Bild wird in `<name>.webp.tmp` geschrieben und per `Path.replace` an den Zielnamen verschoben; ein `finally` löscht die Temp-Datei. Neuer Test simuliert einen Abbruch beim Schreiben und prüft, dass nichts im Zielverzeichnis bleibt.

### WR-03: Unbehandelte Indexfehler in der Beleg-Suche

**Files modified:** `pipeline/ostbevern/quellen.py`, `pipeline/tests/test_quellen.py`
**Commit:** 3e56398
**Applied fix:** `finde_tabellenzeile` prüft `ziel_index` gegen `len(werte)`, `_sammle_vorbericht` prüft auf eine vorhandene `ist_gesamt`-Zeile, `finde_stellenzeile` prüft die Gruppenbezeichnung der Nachwuchszeile; jeweils `QuellenFehler` mit klarer Meldung. Tests für den ersten und dritten Fall. Der Fall `ist_gesamt` hat keinen eigenen Test (nur über die Gesamtpipeline erreichbar).

### WR-04: Leere Listen für jeden `[layout.*]`-Schlüssel erlaubt

**Files modified:** `pipeline/ostbevern/konfiguration.py`, `pipeline/tests/test_konfiguration.py`
**Commit:** 93a4720
**Applied fix:** Neue Konstante `LEERE_LISTE_ERLAUBT = {("quellenbelege", "schwaerzen_nach")}`; alle anderen Listen (insbesondere `pruefwoerter`) müssen wieder mindestens einen Eintrag haben. Neuer Test für `pruefwoerter = []` und `kennzahlen_ergebnisplan = []`.

### WR-05: Kacheln „Erträge“ und „Aufwendungen“ ohne „berechnet“

**Files modified:** `app/src/lib/kennzahlen.ts`, `app/src/lib/__tests__/kennzahlen.test.ts`
**Commit:** 3adbedf (plus ee70fc0, siehe unten)
**Nutzerentscheidung:** Die Summen der Startseite bleiben exakt wie sie sind (Erträge = Zeile 10 + Zeile 19 = 27.502.063 €, Aufwendungen = Zeile 17 + Zeile 20). Es wird nichts an den berechneten Werten geändert und nicht auf Zeile 10/17 umgestellt. Der Fix beschränkt sich darauf, beide Kacheln als „berechnet“ zu kennzeichnen, passend zur Seitenleiste („nicht im PDF“).
**Applied fix:** `berechnet: true` für die Kacheln `ertraege` und `aufwendungen` (die Kachel zeigt dadurch das `BerechnetEtikett`). Der Test hält jetzt fest: berechnet sind `ertraege`, `aufwendungen` und die beiden Pro-Kopf-Werte, und `berechnet` gilt genau dann, wenn eine Herleitung vorhanden ist. Zunächst hatte ich in 3adbedf zusätzlich einen Hinweis „(berechnet)“ in `EbenenTabelle.vue` ergänzt; das ging über die Nutzerentscheidung hinaus und wurde in ee70fc0 wieder zurückgenommen. Die Ausgaben-Tabelle (Zeilen mit Zinsen) trägt damit weiterhin kein eigenes „berechnet“-Etikett, die Seitenleiste nennt sie aber „berechnet“. Das bleibt eine offene Inkonsistenz, falls gewünscht.
**Status:** fixed: requires human verification (Entscheidung über die Linie „berechnet“ und optische Wirkung der zwei zusätzlichen Etiketten auf der Startseite; E2E/Lighthouse nicht gelaufen).

### WR-06: Schriftannahme der Breitenkalibrierung wird nicht hergestellt oder geprüft

**Files modified:** `.github/workflows/ci.yml`, `app/e2e/kacheln.spec.ts`
**Commit:** ef612e9
**Applied fix:** Neuer Workflow-Schritt „Schrift der Kalibrierung sicherstellen“ (nach `playwright install --with-deps`, weil dieser weitere Schriften installiert): installiert `fonts-dejavu-core`, gibt die Version aus und bricht mit klarer Meldung ab, wenn `fc-match sans-serif` nicht DejaVu Sans liefert. Die Spec prüft pro Route, dass die gerenderte Schrift `DejaVu Sans` enthält (`KALIBRIERSCHRIFT`), mit der Meldung „Schrift weicht von der Kalibrierung ab …“. Der Kommentar „Festes Runner-Image“ wurde korrigiert. Abweichung vom Vorschlag: Das Paket wird nicht per `=2.37-8` gepinnt (Risiko, dass die exakte apt-Version auf dem Runner nicht existiert); stattdessen wird die installierte Version protokolliert.
**Status:** fixed: requires human verification (nur auf einem echten GitHub-Runner prüfbar; ob `fc-match` dort nach Playwright-`--with-deps` DejaVu Sans liefert, ist ungeprüft).

### WR-07: Breitentest ohne eigene Zeitgrenze

**Files modified:** `app/e2e/kacheln.spec.ts`
**Commit:** 3db0795
**Applied fix:** Benannte Konstante `LAYOUT_WARTEZEIT_MS` (statt der festen 2000 in `warteAufLayout`, per `evaluate`-Argument übergeben) und `test.describe.configure({ timeout: 60_000 + BREITEN.length * LAYOUT_WARTEZEIT_MS })`, damit die gesammelte Befundliste auch im Fehlerfall ausgegeben wird. Typ- und Lint-Prüfung grün, Test selbst nicht ausgeführt (siehe oben).

## Skipped Issues

### CR-01: Namen und Unterschriften zweier Personen stehen ungeschwärzt in einem ausgelieferten Belegbild

**File:** `app/public/quellen/s009.webp` (erzeugt von `pipeline/ostbevern/quellen.py`, Konfiguration `pipeline/jahrgaenge/2026.toml:209-210`)
**Reason:** Übersprungen, Nutzerentscheidung: akzeptiert, bleibt wie es ist (öffentliche Satzung, Amtsträger unterzeichnen in ihrer Amtsrolle). Weder Bild, Schwärzungskonfiguration noch Schwärzlogik wurden geändert.
**Original issue:** Seite 9 zeigt am Seitenende Klarnamen und handschriftliche Unterschriften von Kämmerin und Bürgermeister; die Datenschutz-Prüfliste meldet „geschwärzt = nein“, und es gibt keinen Test, der ungeschwärzte Treffer ohne Freigabe abfängt. (Der Vorschlag einer Allowlist `pruefwoerter_ok` wurde nicht umgesetzt, da CR-01 vollständig außerhalb des Umfangs bleibt; die Entscheidung ist hier dokumentiert.)

---

_Fixed: 2026-10-07_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
