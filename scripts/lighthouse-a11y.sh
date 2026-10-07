#!/usr/bin/env bash
# Einmaliger Lighthouse-Lauf (nur Kategorie "accessibility") je Route von Ostbevern Money.
#
# Nutzung nach D-13 (Phase 7): einmalige Messung für den Verifikationsbericht, Ziel je Route >= 95
# (A11Y-04). Das Skript läuft NICHT in der CI und lighthouse steht NICHT in app/package.json.
#
# Ablauf (nichts davon berührt app/node_modules des Arbeitsverzeichnisses):
#   1. Scratch-Kopie von app/ (ohne node_modules und dist), `npm ci`, `npm run build-only`.
#   2. lighthouse@13.5.0 mit --ignore-scripts in ein eigenes Scratch-Verzeichnis installieren
#      (Paketprüfung durch die Nutzerin bzw. den Nutzer vor der ersten Nutzung: Plan 07-12, Task 1).
#   3. Ein `docker run` des Playwright-Images: `vite preview` auf Port 4173, CHROME_PATH auf das
#      Chromium des Images, je Route ein Lighthouse-Lauf mit --only-categories=accessibility.
#
# Ausgabe (stdout, eine Zeile je Route): "<Route> <Wert 0-100> <ids fehlgeschlagener binärer Audits>".
# Ein Lauf, der keinen Wert liefert, erscheint als "FAIL <Route>". Fortschritt geht nach stderr.
# Exit-Code 0 immer, außer das Skript selbst bricht ab; die Bewertung (>= 95, 11 Routen) macht der
# Aufrufer (siehe <verify> in 07-12-PLAN.md).
#
# Die Routenliste spiegelt die elf Routen der UI-SPEC; eine neue Route muss hier von Hand ergänzt
# werden (Werkzeug für den Einmalgebrauch). Der Produktcode folgt der Regel aus app/e2e/routen.ts:
# erstes Produkt nach Code mit Grundzahl, Erläuterung und Maßnahme.
#
# Umgebung:
#   LH_SCRATCH  Elternverzeichnis für die Scratch-Kopien (Standard: $TMPDIR bzw. /tmp). Das Skript
#               legt darin immer ein frisches eigenes Unterverzeichnis an und löscht am Ende nur
#               dieses, nie LH_SCRATCH selbst oder fremden Inhalt.
#   LH_KEEP=1   Scratch-Unterverzeichnis am Ende behalten
set -euo pipefail

BILD="mcr.microsoft.com/playwright:v1.63.0-noble"
LIGHTHOUSE_VERSION="13.5.0"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BASIS="${LH_SCRATCH:-${TMPDIR:-/tmp}}"
mkdir -p "$BASIS"
S="$(mktemp -d "$BASIS/lighthouse-a11y.XXXXXX")" # immer ein frisches, eigenes Verzeichnis

aufraeumen() {
  if [ "${LH_KEEP:-0}" != "1" ]; then
    # Nie ein leeres, Wurzel- oder Home-Verzeichnis löschen (Schutz vor Fehlbelegung von $S).
    case "${S:-}" in
      "" | "/" | "$HOME" | "$HOME/")
        echo "Scratch-Verzeichnis '$S' wird aus Sicherheitsgründen nicht gelöscht" >&2
        return 0
        ;;
    esac
    # Vom Container angelegte Dateien können root gehören; ein Fehlschlag ist unkritisch.
    rm -rf "$S" 2>/dev/null || true
  else
    echo "Scratch-Verzeichnis behalten: $S" >&2
  fi
}
trap aufraeumen EXIT

echo "Scratch-Kopie von app/ nach $S" >&2
tar -C "$REPO_ROOT" --exclude=app/node_modules --exclude=app/dist -cf - app | tar -xf - -C "$S"

# Produktcode nach der Regel aus app/e2e/routen.ts (aus den App-Daten, nicht von Hand).
PRODUKT="$(
  node -e '
    const fs = require("node:fs");
    const dir = process.argv[1];
    const lies = (d) => JSON.parse(fs.readFileSync(dir + "/" + d, "utf-8"));
    const mitMassnahme = new Set(lies("investitionen.json").massnahmen.map((m) => m.produkt));
    const code = lies("produkte.json")
      .filter((p) => p.grundzahlen.length > 0 && p.erlaeuterungen.length > 0 && mitMassnahme.has(p.code))
      .map((p) => p.code)
      .sort()[0];
    if (code === undefined) { console.error("Kein Produkt mit Grundzahl, Erläuterung und Maßnahme"); process.exit(1); }
    process.stdout.write(code);
  ' "$REPO_ROOT/app/src/data"
)"
echo "Produktseite: $PRODUKT" >&2

echo "npm ci und Build (nur Vite) in der Scratch-Kopie" >&2
npm --prefix "$S/app" ci --no-audit --no-fund >&2
npm --prefix "$S/app" run build-only >&2

echo "lighthouse@$LIGHTHOUSE_VERSION (--ignore-scripts) in $S/lh" >&2
mkdir -p "$S/lh"
(cd "$S/lh" && npm init -y >/dev/null && npm i "lighthouse@$LIGHTHOUSE_VERSION" --ignore-scripts --no-audit --no-fund >&2)

# Skript im Container: Preview starten, Chromium des Playwright-Images verwenden.
cat > "$S/lh/run.sh" <<'EOS'
set -u
cd /work/app
npx vite preview --port 4173 --strictPort >/tmp/preview.log 2>&1 &
PREVIEW_PID=$!
for _ in $(seq 1 30); do
  if node -e 'fetch("http://localhost:4173/").then((r) => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))'; then
    break
  fi
  sleep 1
done
export CHROME_PATH
CHROME_PATH=$(ls -d /ms-playwright/chromium-*/chrome-linux*/chrome | head -1)
echo "Chromium: $CHROME_PATH" >&2
for r in '' einnahmen ausgaben "produkt/$PRODUKT" geldfluss entwicklung investitionen rat-entscheidet stellenplan glossar ueber; do
  rm -f /tmp/lh.json
  if ! node /work/lh/node_modules/lighthouse/cli/index.js "http://localhost:4173/#/$r" \
      --only-categories=accessibility --chrome-flags="--headless=new --no-sandbox" \
      --output=json --output-path=/tmp/lh.json --quiet 2>/tmp/lh.err; then
    echo "FAIL ${r:-/}"
    tail -n 3 /tmp/lh.err >&2
    continue
  fi
  ROUTE="${r:-/}" node -e '
    const j = require("/tmp/lh.json");
    const bad = Object.values(j.audits)
      .filter((x) => x.scoreDisplayMode === "binary" && x.score === 0)
      .map((x) => x.id);
    console.log(process.env.ROUTE, Math.round(j.categories.accessibility.score * 100), bad.join(","));
  '
done
kill "$PREVIEW_PID" 2>/dev/null || true
EOS

echo "Lighthouse je Route im Container $BILD" >&2
docker run --rm --ipc=host -e "PRODUKT=$PRODUKT" -v "$S":/work "$BILD" bash /work/lh/run.sh
