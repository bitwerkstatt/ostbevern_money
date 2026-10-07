---
phase: 06-kontext-seiten
plan: 14
subsystem: app-menue
tags: [vue, menue, positionierung, wr-01, gap-closure, vitest]

requires:
  - phase: 06-kontext-seiten
    provides: "06-02: MenueGruppe.vue (Disclosure-Gruppe Mehr wissen, D-19)"
provides:
  - "app/src/lib/menueVersatz.ts: ListenMessung, listenVersatz(), randAusMaximalbreite() als reine Positionierungslogik"
  - "MenueGruppe.positioniere() misst einmal, liest den angewandten Versatz (style.left) und weist den absoluten Versatz zu"
  - "menueVersatz.test.ts: Review-Spur der zweiten Öffnung, Resize in beide Richtungen, Randfälle, Fixpunkt- und Idempotenz-Raster, Quelltexttest der Verdrahtung"
affects: [verify-work, phase-07]

actuals:
  tokens: 2400
  tasks: 2
  commits: 3
plan_head_before: 8878f321a08314d99cc6781fd257d9afb061c958
plan_head_after: 5922ca46682a9b6feec8a3827e7f20864d2c240d

tech-stack:
  added: []
  patterns:
    - "Positionierung als reine Funktion über das gemessene Rechteck minus den bereits angewandten Versatz: das Ergebnis ist absolut und vom vorherigen Versatz unabhängig (Fixpunkt)"

key-files:
  created:
    - app/src/lib/menueVersatz.ts
    - app/src/lib/__tests__/menueVersatz.test.ts
  modified:
    - app/src/components/MenueGruppe.vue

key-decisions:
  - "Der angewandte Versatz wird aus element.style.left gelesen, nicht aus dem reaktiven Wert: das gemessene Rechteck enthält den inline geschriebenen Wert, auch wenn Vue einen neueren noch nicht geflusht hat"
  - "Keine neue Abhängigkeit und keine DOM-Testumgebung; die Logik ist rein und läuft im bestehenden Node-Environment"

requirements-completed: [ENTW-01, INV-01, RAT-01, STEL-01]

duration: 15min
completed: 2026-10-06
status: complete

coverage:
  - id: D1
    description: "Zweites Öffnen liefert denselben Versatz wie das erste (Review-Spur WR-01); der alte Algorithmus lieferte 0"
    requirement: "WR-01, D-19, UI-SPEC E12"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menueVersatz.test.ts#listenVersatz (WR-01, UI-SPEC E12)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Resize: breiteres Fenster gibt 0, schmaleres den Versatz mit rechter Kante bei Fensterbreite minus Rand; Fixpunkt über ein Raster veralteter Versätze und Idempotenz"
    requirement: "WR-01"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menueVersatz.test.ts#Resize und Fixpunkt (WR-01)"
        status: pass
    human_judgment: false
  - id: D3
    description: "positioniere() delegiert an listenVersatz/randAusMaximalbreite, setzt den reaktiven Versatz nicht mehr vor dem Messen auf 0, liest style.left und wird von wechsle() und dem Resize-Handler erreicht"
    requirement: "WR-01"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menueVersatz.test.ts#Verdrahtung in MenueGruppe.vue"
        status: pass
    human_judgment: false
  - id: D4
    description: "Im Browser bei 360-1024 px bleibt die Liste bei jedem Öffnen und beim Resize vollständig im Viewport"
    requirement: "D-19, UI-SPEC E12"
    verification:
      - kind: manual
        ref: "Phasen-Abschluss-Walkthrough (06-VERIFICATION.md behavior_unverified_items); kein Browser in der Sandbox"
        status: not_run
    human_judgment: true
---

# Phase 6 Plan 14: Menüliste bleibt im Fenster (WR-01) Summary

**Reine Funktion listenVersatz() leitet den absoluten Versatz der "Mehr wissen"-Liste aus Basisposition (Rechteck minus angewandter Versatz), Fensterbreite und Rand ab; MenueGruppe.positioniere() misst einmal und weist ihn zu.**

## Performance

- **Duration:** ca. 15 min
- **Completed:** 2026-10-06
- **Tasks:** 2 (Tracer plus Absicherung)
- **Files modified:** 3

## Accomplishments

- WR-01 geschlossen: Die Liste behält ihr inline `left` auch geschlossen (`v-show`). Der alte Code setzte den reaktiven Versatz auf 0 und maß sofort, das Rechteck trug aber noch den alten Versatz; beim zweiten Öffnen und beim Resize kam deshalb keine Korrektur und die Liste lief wieder über den Fensterrand. Jetzt hängt das Ergebnis nicht mehr vom vorherigen Versatz ab.
- Das Verhalten ist ohne Browser testbar: 139 Tests (Review-Spur, Randfälle, 3 Rechtecke x 7 veraltete Versätze x 3 Fensterbreiten je für Fixpunkt und Idempotenz, Quelltext-Verdrahtung).
- Disclosure-Semantik, Template, ARIA und CSS blieben unverändert.

## Task Commits

1. **Task 1 RED:** `e3087eb` test(06-14): Versatz der Menüliste ohne veralteten Offset (WR-01)
2. **Task 1 GREEN:** `7978131` fix(06-14): Menüliste bleibt bei jedem Öffnen im Fenster (WR-01)
3. **Task 2:** `5922ca4` test(06-14): Resize und Fixpunkt der Menüliste (WR-01)

## Deviations from Plan

None - plan executed exactly as written. Die Charakterisierungstests aus Task 2 liefen beim ersten Lauf grün, es war keine Korrektur nötig.

## Verification

- Scratch-Kopie von `app/` mit symlinkter Linux-`node_modules` (identische Lockfile, kein Netzwerk für `npm ci`; die Umgebung ist wie bei 06-02 bis 06-12). Grün: vitest (menueVersatz, menue, quelltext: 99 Tests; menueVersatz plus menue: 146 Tests), type-check, lint, format:check, build (nur die bekannte Chunk-Größenwarnung).
- Nicht ausgeführt: Browser-Prüfung bei 360-1024 px (Backstop-Wahrheit, bleibt im Phasen-Abschluss-Walkthrough).

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

- FOUND: app/src/lib/menueVersatz.ts, app/src/lib/__tests__/menueVersatz.test.ts, app/src/components/MenueGruppe.vue
- FOUND commits: e3087eb, 7978131, 5922ca4
