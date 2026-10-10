---
phase: quick-261010-bvz
plan: 01
subsystem: app
tags: [css, layout, kennzahl-kachel, e2e]
status: complete
requirements:
  - QUICK-261010-bvz
key-files:
  modified:
    - app/src/components/KennzahlKachel.vue
    - app/e2e/kacheln.spec.ts
commits: 1
plan_head_before: c5b521820cc492e645ade4cc70c2b3ba8b8fc837
plan_head_after: 577a89c34633354dab16e9fcfac77469dd24ca0a
actuals:
  tasks: 2
  commits: 1
---

# Quick 261010-bvz: Quelle-Knopf der Kennzahl-Kacheln am unteren Rand fixiert

Der Quelle-Knopf (Icon plus „Quelle“) liegt in jeder Kennzahl-Kachel jetzt am unteren Inhaltsrand der grauen Box (Innenabstand `--wa-space-m`), sodass er in einer Rasterreihe auf gleicher Höhe endet, egal wie viele Zeilen Bezeichnung oder Zeile umbrechen.

## Ursache

Die Deklaration `margin-top: auto` an `.om-kennzahl__zeile` war wirkungslos: `.om-kennzahl p { margin: 0 }` ist spezifischer und setzte den oberen Außenabstand auf 0. Der freie Platz der Flex-Spalte landete deshalb unter dem Knopf.

## Änderung

- `KennzahlKachel.vue`: wirkungslose Deklaration an `.om-kennzahl__zeile` entfernt. `.om-kennzahl__quelle` hat jetzt `display: flex; margin-top: auto; padding-top: var(--wa-space-xs)`, mit Kommentar zur Spezifitätsursache. JSDoc der Prop `quelle` ergänzt. Die Zeile „{Wertart} {jahr} · PDF-Seite {n}“ bleibt direkt unter dem Betrag.
- `kacheln.spec.ts`: neue Prüfung „Quelle-Knopf endet bei …“ je Kachel (Unterkante gegen Inhaltsbereich) und neuer Abschnitt (k) „Reihen im Gleichlauf“ (Spannweite der Kachelhöhen und der Knopf-Unterkanten je Rasterreihe, Toleranz 0,5 px). Kopfkommentar ergänzt. Der Abschnitt heißt (k), weil (j) in der Spec schon vergeben ist (Plan nannte (j)).

## Red -> Green

- RED (vor dem CSS-Fix, `scripts/e2e-wie-ci.sh … --project=ci e2e/kacheln.spec.ts`): 4 von 5 Tests rot (alle vier Kachelrouten), 268 Befunde, ausschließlich neue. Beispiele: `/ @ 1280 px`: Reihe bei 293.6 px, Knöpfe enden bei 447.4 bis 477.8 px; `/stellenplan @ 1280 px`: Knöpfe enden bei 426.6 bis 447.6 px („Stellen 2025“ endet 426.6 px, Inhaltsbereich 447.6 px); `/ @ 488 px`: Reihe bei 879.5 px, Knöpfe 1054.3 bis 1077.5 px.
- GREEN (nach dem Fix): `e2e/kacheln.spec.ts` 5/5 grün, alle Routen und Breiten.

## Prüfungen (Scratch-Kopie mit Linux-node_modules)

type-check, lint, format:check, Vitest (2207 Tests) und build grün. Gesamte Playwright-Suite des Projekts ci über `scripts/e2e-wie-ci.sh`: 89/89 grün.

## Commits

- `577a89c` fix(quick-261010-bvz): Quelle-Knopf der Kennzahl-Kacheln am unteren Rand fixiert (nur die zwei Dateien)

Task 2 erzeugte keinen Commit (keine Korrekturen nötig).

## Deviations from Plan

Abschnittsbuchstabe (k) statt (j) in der Spec (Namenskollision). Sonst keine.

## Offen

Die Sichtprüfung (human-check: Startseite bei 1280/768/360 px, /stellenplan bei 1280 px) wurde nicht im Browser gemacht; die automatisierte Layoutprüfung deckt sie über alle Breiten von 360 bis 1440 px ab.

## Known Stubs

None.

## Self-Check: PASSED

Beide geänderten Dateien vorhanden, Commit 577a89c im Branch, Arbeitsbaum unter app/scripts/daten/pipeline sauber.
