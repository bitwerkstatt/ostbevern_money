# Ostbevern Money

Ostbevern Money erklärt dir den Haushalt 2026 der Gemeinde Ostbevern. Die App beantwortet zwei Leitfragen: **Wo kommt das Geld der Gemeinde her?** und **Wofür wird es ausgegeben?** Jede Zahl, die du hier siehst, hat eine Python-Pipeline aus dem veröffentlichten Haushalts-PDF extrahiert und automatisch gegen die Planwerte geprüft. Dies ist ein **inoffizielles Projekt** und steht in keiner Verbindung zur Gemeindeverwaltung.

## Stand

Die Phasen 1 bis 7 sind umgesetzt: Pipeline mit Prüfregeln, alle Seiten der App, Quellenbelege, Barrierefreiheit, Browser-Tests und der CI-Workflow mit Veröffentlichung auf GitHub Pages. Online geht die App, sobald das Repository auf GitHub angelegt und `main` gepusht ist (Abschnitt „Veröffentlichung auf GitHub Pages“).

## Aufbau

- `raw_data/` — das Quell-PDF des Haushalts
- `pipeline/` — die Python-Pipeline, die das PDF ausliest und prüft
- `daten/` — von der Pipeline erzeugte und geprüfte Daten
- `app/` — die Vue-3-Webanwendung
- `discussion/SPEZIFIKATION.md` — die fachliche Spezifikation

## Schnellstart

```bash
uv sync --directory pipeline
uv run --directory pipeline pytest
npm --prefix app ci
npm --prefix app run dev
npm --prefix app run build
```

Alle Befehle und Konventionen stehen in [`.claude/CLAUDE.md`](.claude/CLAUDE.md).

### Browser-Tests mit der Schrift der CI

Der Breitentest der Kennzahl-Kacheln (`app/e2e/kacheln.spec.ts`) misst gerenderte Beträge und hängt deshalb von der Systemschrift ab. GitHub Actions läuft auf `ubuntu-24.04` und rendert mit DejaVu Sans; im nackten Playwright-Image wäre es eine andere, schmalere Schrift, und die Messung wäre wertlos. Damit du lokal dieselben Zahlen bekommst, startest du die Browser-Tests über `scripts/e2e-wie-ci.sh`. Das Skript braucht Docker, lädt das Schriftpaket einmal nach `~/.cache/ostbevern-money` (die Prüfsumme ist fest eingetragen) und ändert nichts an der App.

Bereite dafür eine Kopie von `app/` mit Linux-Abhängigkeiten und einem Build vor (`npm ci` und `npm run build-only`). Auf macOS führst du beides im Image `mcr.microsoft.com/playwright:v1.63.0-noble` aus, weil `app/node_modules` dort macOS-Binärdateien enthält. Dann:

```bash
scripts/e2e-wie-ci.sh <Verzeichnis-der-Kopie> --project=ci
```

## Veröffentlichung auf GitHub Pages

Die App ist eine statische Seite ohne Backend. Der Workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) baut sie und veröffentlicht sie auf GitHub Pages, sobald der Stand auf `main` liegt und alle Prüfungen grün sind. Ein Pull Request oder ein anderer Branch veröffentlicht nie etwas. Das Anlegen des Repositories und der erste Push sind bewusst deine Handgriffe, damit nichts ungewollt öffentlich wird:

1. Lege in deinem GitHub-Account oder in der Organisation `bitwerkstatt` ein **öffentliches** Repository mit dem Namen `ostbevern_money` an, ohne README, `.gitignore` oder Lizenz (die gibt es hier schon).
2. Trage es als Remote `origin` ein und pushe `main`:

   ```bash
   git remote add origin https://github.com/bitwerkstatt/ostbevern_money.git
   git push -u origin main
   ```

3. Öffne im Repository **Settings → Pages** und stelle **Source** auf **„GitHub Actions“**. Kostenlose Organisationen brauchen für Pages ein öffentliches Repository; prüfe in den Einstellungen der Organisation, dass Pages erlaubt ist.
4. Öffne den Reiter **Actions**. Der Workflow „CI“ prüft Pipeline und App, führt den Smoke-Test aus (jede Seite, Konsole, Netzwerk, Barrierefreiheit mit axe) und veröffentlicht erst danach. Ist der Lauf grün, findest du die App unter **https://bitwerkstatt.github.io/ostbevern_money/**. Liegt das Repository in einem anderen Account, ersetze `bitwerkstatt` durch dessen Namen.

Schlägt eine Prüfung fehl, bleibt die bisherige Seite unverändert online. Du kannst den Workflow auch von Hand starten: **Actions → CI → Run workflow** auf dem Branch `main`.

Die App funktioniert unter jedem Unterpfad: Vite baut mit `base: './'` und die App nutzt den Hash-Router, deshalb ist keine Anpassung nötig, wenn das Repository anders heißt.

## Pflege beim Jahrgangswechsel

Neben der Pipeline-Konfiguration (`pipeline/jahrgaenge/{jahr}.toml`) prüfst du bei einem neuen Haushaltsjahr diese Stellen von Hand:

- **Link auf das Original-PDF:** `ORIGINAL_PDF_URL` in `app/src/config.ts` zeigt auf eine Datei der Gemeinde mit inhaltsgebundenem Pfad. Ersetzt die Gemeinde die Datei (Korrektur, Nachtragshaushalt), liefert der alte Link 404, und alle Links „Seite n im Original-PDF öffnen“ laufen ins Leere, ohne dass ein Test es merkt. Öffne die URL deshalb vor jeder Veröffentlichung einmal und trage bei einem neuen Jahrgang die neue Adresse ein.

## Lizenz

MIT, siehe [`LICENSE`](LICENSE).

## Dank

Inspiriert von [Münster Money (Code for Münster)](https://github.com/codeformuenster/haushalt-muenster-2026). Es wurde kein Code übernommen — die Komponentennamen folgen nur der Vorlage.

Die selbst gehosteten Icons stammen von Font Awesome Free (CC BY 4.0).
