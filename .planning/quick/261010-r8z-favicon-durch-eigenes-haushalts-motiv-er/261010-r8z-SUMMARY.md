---
phase: quick-261010-r8z
plan: 01
subsystem: app
tags: [favicon, svg, e2e]
status: complete
requirements: [QUICK-261010-r8z]
key-files:
  created:
    - app/public/favicon.svg
    - app/e2e/favicon.spec.ts
  modified:
    - app/index.html
  deleted:
    - app/public/favicon.ico
actuals:
  tasks: 2
  commits: 1
plan_head_before: bf3abdafbfa631d1cce78f1e577c9182447a892f
plan_head_after: 945c71460b818e6398fea27e2a7a3b3592853fa0
---

# Quick 261010-r8z: Eigenes Haushalts-Favicon statt Vue-Logo

Handgeschriebenes 16er-Raster-SVG (goldenes Haus mit dunklem Euro-Zeichen auf dunkelbrauner, abgerundeter Kachel, Web-Awesome-yellow 80 und 20) ersetzt das Vue-ICO; relativ verlinkt, in sich geschlossen, per neuer E2E-Spec abgesichert.

## Ergebnis

- `app/public/favicon.svg` neu, genau nach dem Entwurf im Plan (Kachel rx 3, Haus-Polygon, Euro-Bogen, zwei pixelgenaue Querbalken). Geometrie gegenüber dem Entwurf **nicht** geändert.
- `app/index.html`: genau ein Icon-Link `rel="icon" type="image/svg+xml" href="/favicon.svg"`; Build schreibt `href="./favicon.svg"`.
- `app/public/favicon.ico` entfernt (fehlt auch in `dist/`).
- `app/e2e/favicon.spec.ts`: ein Test (ein Icon-Link, Typ, relativer href, gleicher Ursprung, Status 200 und Content-Type, keine verbotenen Bausteine, Dekodierung mit 16 x 16 px).

## TDD

- **RED** (vor der Umstellung, Scratch-Kopie, Projekt ci): erste fehlschlagende Erwartung `expect(locator).toHaveAttribute('type', 'image/svg+xml')`, Link war `<link rel="icon" href="./favicon.ico"/>` ohne Typ.
- **GREEN** (nach Umstellung): `e2e/favicon.spec.ts` grün.

## Verifikation (Scratch-Kopie mit Linux-node_modules)

- type-check, lint, format:check: grün
- Vitest: 2207 Tests grün
- build: grün; `dist/index.html` enthält `href="./favicon.svg"`, `dist/favicon.svg` vorhanden, `dist/favicon.ico` fehlt
- Gesamte Playwright-Suite Projekt ci (`scripts/e2e-wie-ci.sh`): 90 von 90 grün

## Sichtprüfung der Lesbarkeit

Vorschaubilder (nicht eingecheckt): Übersicht `.../scratchpad/om/vorschau/uebersicht.png` (16/32/64/180 px auf `#ffffff`, `#dee1e6`, `#202124`, `#35363a`) und 8-fache Pixelvergrößerung `.../scratchpad/om/vorschau/zoom.png` (Session-Scratchpad). Urteil: Bei 16 px sind Hausform und beide Euro-Querbalken auf allen vier Hintergründen getrennt erkennbar; bei 180 px sauber, ohne Lücken oder schiefe Kanten.

## Fallback-Entscheidung: nur SVG

Kein ICO, PNG oder apple-touch-icon:
1. Kein Rasterwerkzeug in der Sandbox; eine per Chromium erzeugte Binärdatei wäre plattformabhängig, nicht in der CI reproduzierbar und liefe dem SVG davon.
2. Aktuelle Chrome-, Edge-, Firefox- und Safari-Versionen zeigen SVG-Favicons.
3. Das Vue-ICO als Fallback zeigte in alten Browsern das falsche Logo.
4. Die implizite ICO-Suche im Wurzelverzeichnis geht bei einer Pages-Projektseite an die Account-Wurzel; eine unverlinkte ICO brächte nichts.
iOS nimmt für den Homescreen ein eigenes Ersatzbild; bewusst so.

## Deviations from Plan

None - plan executed exactly as written. Task 2 erzeugte keine Korrekturen und damit keinen eigenen Commit.

## Offen (human-check)

App im Browser öffnen (hell und dunkel), Tab zeigt das neue Motiv; bei altem Icon Cache leeren. Nach dem nächsten Pages-Deployment unter dem Unterpfad wiederholen.

## Commits

- 945c714: feat(quick-261010-r8z): eigenes Haushalts-Favicon statt Vue-Logo

## Self-Check: PASSED
