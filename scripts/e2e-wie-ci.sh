#!/usr/bin/env bash
# Playwright-Lauf mit der Schrift von GitHub Actions (Lücke G-07-2, Plan 07-14).
#
# Warum: Die Breiten der Kennzahl-Kacheln hängen von der Systemschrift hinter `system-ui` ab. Im
# nackten Playwright-Image fällt `system-ui` auf die CJK-Schrift WenQuanYi Zen Hei zurück (rund
# 16 % schmaler als DejaVu Sans Bold auf dem Runner ubuntu-24.04). Die 13rem-Kalibrierung aus
# Plan 07-13 war dadurch zu eng, und die CI scheiterte bei „Kreisumlage“ auf /rat-entscheidet.
# Dieses Skript startet Playwright im selben Image, installiert aber vorher das Schriftpaket des
# Runners (fonts-dejavu-core, fest gepinnt und per SHA-256 geprüft). Jede lokale Messung und jede
# Kalibrierung der Kachelbreiten läuft ausschließlich hierüber.
#
# Nutzung:
#   scripts/e2e-wie-ci.sh <app-verzeichnis> [playwright-argumente …]
#   Beispiel: scripts/e2e-wie-ci.sh /tmp/scratch/app --project=ci e2e/kacheln.spec.ts
#
# Voraussetzung: <app-verzeichnis> ist eine installierte und gebaute Kopie von app/ mit
# Linux-node_modules (`npm ci` und `npm run build-only` in einer Scratch-Kopie; auf macOS beides
# im selben Image, weil app/node_modules dort macOS-Binärdateien enthält). Das Skript ändert
# nichts an der App außer den Testausgaben (test-results, playwright-report).
#
# Umgebung:
#   E2E_SCHRIFT_CACHE  Verzeichnis für das heruntergeladene Schriftpaket
#                      (Standard: ${XDG_CACHE_HOME:-$HOME/.cache}/ostbevern-money)
#
# Der Exit-Code ist der von Playwright (2: ungültiges Verzeichnis, 1: Prüfsumme stimmt nicht).
# Fortschritt geht nur nach stderr, stdout trägt die Ausgabe von Playwright unverändert. Das
# Skript läuft nicht in der CI: Der Runner bringt die Schrift selbst mit.
set -euo pipefail

BILD="mcr.microsoft.com/playwright:v1.63.0-noble"
# Version und Prüfsumme stammen aus dem Paketindex Ubuntu noble (main); das Paket gehört zum
# Image ubuntu-24.04 von GitHub.
SCHRIFT_PAKET="fonts-dejavu-core_2.37-8_all.deb"
SCHRIFT_URL="http://archive.ubuntu.com/ubuntu/pool/main/f/fonts-dejavu/${SCHRIFT_PAKET}"
SCHRIFT_SHA256="40049660c194f3b8a2541fc7369efebb10e9f94bdac836a2f38fafedd10fa73a"

if [ "$#" -lt 1 ]; then
  echo "Nutzung: $0 <app-verzeichnis> [playwright-argumente …]" >&2
  exit 2
fi

APP_DIR_ARG="$1"
shift

fehlt=""
if [ ! -d "$APP_DIR_ARG" ]; then
  fehlt="das Verzeichnis selbst"
elif [ ! -f "$APP_DIR_ARG/package.json" ]; then
  fehlt="package.json"
elif [ ! -x "$APP_DIR_ARG/node_modules/.bin/playwright" ]; then
  fehlt="node_modules/.bin/playwright (npm ci in der Scratch-Kopie ausführen)"
elif [ ! -f "$APP_DIR_ARG/dist/index.html" ]; then
  fehlt="dist/index.html (npm run build-only in der Scratch-Kopie ausführen)"
fi
if [ -n "$fehlt" ]; then
  echo "Ungültiges App-Verzeichnis „$APP_DIR_ARG“: es fehlt $fehlt." >&2
  exit 2
fi
APP_DIR="$(cd "$APP_DIR_ARG" && pwd)"

CACHE="${E2E_SCHRIFT_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/ostbevern-money}"
PAKET="$CACHE/$SCHRIFT_PAKET"
mkdir -p "$CACHE"

if [ ! -f "$PAKET" ]; then
  echo "Lade $SCHRIFT_PAKET nach $CACHE" >&2
  TEMP="$PAKET.tmp.$$"
  curl -fsSL "$SCHRIFT_URL" -o "$TEMP"
  mv "$TEMP" "$PAKET"
fi

if command -v sha256sum >/dev/null 2>&1; then
  ISTWERT="$(sha256sum "$PAKET" | cut -d' ' -f1)"
else
  ISTWERT="$(shasum -a 256 "$PAKET" | cut -d' ' -f1)"
fi
if [ "$ISTWERT" != "$SCHRIFT_SHA256" ]; then
  rm -f "$PAKET"
  echo "Prüfsumme von $SCHRIFT_PAKET stimmt nicht." >&2
  echo "  erwartet: $SCHRIFT_SHA256" >&2
  echo "  gefunden: $ISTWERT" >&2
  exit 1
fi

echo "Playwright im Image $BILD mit DejaVu Sans ($SCHRIFT_PAKET)" >&2

# apt wird nicht benutzt (der Spiegel des Images ist nicht überall erreichbar): dpkg-deb -x legt
# die Schriftdateien und die fontconfig-Konfiguration an dieselben Orte wie eine Installation.
docker run --rm --ipc=host \
  -e CI=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "$APP_DIR":/work \
  -w /work \
  -v "$PAKET":/schriften/fonts-dejavu-core.deb:ro \
  "$BILD" \
  bash -c '
    set -u
    dpkg-deb -x /schriften/fonts-dejavu-core.deb /
    fc-cache -f
    echo "Schrift für sans-serif: $(fc-match sans-serif)" >&2
    status=0
    npx playwright test "$@" || status=$?
    for verzeichnis in test-results playwright-report; do
      if [ -e "$verzeichnis" ]; then
        chown -R "$HOST_UID:$HOST_GID" "$verzeichnis" 2>/dev/null || true
      fi
    done
    exit "$status"
  ' bash "$@"
