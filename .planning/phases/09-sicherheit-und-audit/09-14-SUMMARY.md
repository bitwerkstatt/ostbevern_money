---
phase: 09-sicherheit-und-audit
plan: 14
subsystem: testing
tags: [vitest, vue, audit, gap-closure, kernaussage]

requires:
  - phase: 09-sicherheit-und-audit
    provides: "Lückenliste mit drei fix-Zeilen (G-09-01 bis G-09-03) aus 09-13"
provides:
  - "Superlativ „größter Einzelposten“ nur, wenn die Daten ihn tragen (G-09-01)"
  - "„PDF-Seite“ bzw. „PDF-Seiten“ passend zur Zahl der Seiten in Erklärtexten, Überschusstexten und Kreisumlage-Callout (G-09-02)"
  - "Etikett „berechnet“ an der Gruppensumme „Grundsteuer (A+B)“ auf /geldfluss (G-09-03)"
  - "Lückenliste ohne fix-Zeile, alle drei Zeilen fixed mit Fix- und Test-Hash"
affects: [09-15]

actuals:
  tokens: 4519
  tasks: 2
  commits: 8

plan_head_before: e07b7a98ee607d456a4477cbe054d9fc8813642e
plan_head_after: d84bc073364af61c6ed9ff237e698cbc526e5850

tech-stack:
  added: []
  patterns:
    - "Reine Prüffunktion mit Datenzugriff in einer dünnen Hülle (pruefeGroessterEinzelposten / istGroessterEinzelposten), damit der Kipp-Fall ohne Jahrgangswerte testbar ist"
    - "Einheitlicher Seitentext über seitenText() statt „PDF-Seite {{ … }}“ im Template"

key-files:
  created:
    - app/src/lib/__tests__/hilfsfunktionen.test.ts
    - app/src/components/__tests__/erklaertext.test.ts
  modified:
    - app/src/lib/kreisumlage.ts
    - app/src/components/KreisumlageCallout.vue
    - app/src/lib/hilfsfunktionen.ts
    - app/src/components/ErklaerText.vue
    - app/src/pages/AusgabenPage.vue
    - app/src/lib/geldfluss.ts
    - app/src/lib/__tests__/kreisumlage.test.ts
    - app/src/lib/__tests__/geldfluss.test.ts
    - .planning/v1.0-MILESTONE-AUDIT.md

key-decisions:
  - "Bei null Seiten liefert seitenText einen leeren Text; ErklaerText blendet die Quellenzeile dann aus, statt „Quelle: PDF-Seite “ ohne Zahl zu zeigen"
  - "Die bestehende Erwartung berechnet: false für grundsteuer in geldfluss.test.ts wurde im Fix-Commit umgestellt und im Kommentar begründet; kein Wert und keine Toleranz geändert"
  - "quellenZeile und die lokalen Helfer in StellenplanPage.vue und ZuschussListe.vue blieben unberührt (kein Befund, G-09-16 IN-05 bleibt deferred)"

patterns-established:
  - "Rot-zuerst je Lückenzeile: test(09) mit rotem Ausgang im Commit-Text, dann fix(09), dann Zeile im Audit auf fixed"

requirements-completed: [AUD-01]

coverage:
  - id: D1
    description: "G-09-01: Der Superlativ „Der größte Einzelposten ist die Weitergabe an Kreis und Land“ auf der Startseite steht nur, wenn Weitergabe an Kreis und Land jeden Aufgabenbereich und die Kreisumlage jede Aufwandsart ohne Transferaufwendungen übertrifft; sonst der neutrale Satz"
    requirement: AUD-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/kreisumlage.test.ts#G-09-01 (sechs Jahre je zwei Tests, drei Kipp-Fälle)"
        status: pass
    human_judgment: false
  - id: D2
    description: "G-09-02: „PDF-Seite“ im Singular nur bei genau einer Seite, sonst „PDF-Seiten“ (18 von 21 Erklärtexten betroffen)"
    requirement: AUD-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/hilfsfunktionen.test.ts#G-09-02"
        status: pass
      - kind: integration
        ref: "app/src/components/__tests__/erklaertext.test.ts#G-09-02 (21 Texte, serverseitig gerendert)"
        status: pass
    human_judgment: false
  - id: D3
    description: "G-09-03: Gruppensumme „Grundsteuer (A+B)“ trägt in der Tabelle „Woher“ das Etikett „berechnet“, einzelne Posten nicht"
    requirement: AUD-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#G-09-03 (sechs Jahre)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Lückenliste: keine Zeile mehr auf fix, jede fixed-Zeile nennt Fix- und Test-Commit mit Id im Betreff"
    requirement: AUD-01
    verification:
      - kind: other
        ref: "Skriptprüfung aus 09-14-PLAN Task 1 und 2 (Beleg-Hash bekannt, Betreff nennt 09/G-09-NN, kein fix übrig)"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-09
status: complete
---

# Phase 9 Plan 14: Fixes der Kernaussage-Lücken Summary

**Drei Lücken der Kernaussage (Superlativ auf der Startseite, „PDF-Seite“ im Singular, fehlendes Etikett „berechnet“ an „Grundsteuer (A+B)“) mit je einem vorher roten Test behoben und im Audit mit Fix- und Test-Hash als fixed belegt; alle.py byte-identisch.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-10-09T07:04:00Z (geschätzt aus dem Anlegen des Worktrees)
- **Completed:** 2026-10-09T07:14:42Z
- **Tasks:** 2
- **Files modified:** 11 (9 geändert, 2 neu)

## Accomplishments

- G-09-01: `istGroessterEinzelposten(jahrIndex)` in `app/src/lib/kreisumlage.ts` (über die reine Funktion `pruefeGroessterEinzelposten`); `KreisumlageCallout.vue` nennt den Superlativ nur bei wahr, sonst „Weitergabe an Kreis und Land: …“. Für alle sechs Jahre der Daten ist er wahr und bleibt sichtbar.
- G-09-02: `seitenText(seiten)` in `app/src/lib/hilfsfunktionen.ts`; `ErklaerText.vue`, die Überschusstexte in `AusgabenPage.vue` und die Aufteilung im `KreisumlageCallout.vue` nutzen sie.
- G-09-03: `STEUER_GRUPPEN` mit mehr als einem Posten tragen `berechnet: true` (`app/src/lib/geldfluss.ts`); die Tabelle „Woher“ zeigt das Etikett durch die bestehende Spalte `berechnet`.
- Audit: alle drei Zeilen `fixed` mit „fixed in 09-14 (<Fix>, Test <Test>)“, Zeile „09-14: …“ unter der Lückenliste, Arbeitsliste „Für 09-14“ Punkt für Punkt abgehakt.

## Rote Testausgabe vor dem Fix (D-12)

G-09-01 (`app/src/lib/__tests__/kreisumlage.test.ts`, Commit 3f944a7):

```
 Test Files  1 failed (1)
      Tests  15 failed | 10 passed (25)
TypeError: pruefeGroessterEinzelposten is not a function
 ❯ src/lib/__tests__/kreisumlage.test.ts:90:12
```

G-09-02 (`hilfsfunktionen.test.ts`, `erklaertext.test.ts`, Commit 74fed1c):

```
 Test Files  2 failed (2)
      Tests  21 failed | 3 passed (24)
AssertionError: expected '<div class="om-erklaertext" …' to contain 'Quelle: PDF-Seiten 46, 47</p>'
Received: "… <p class="om-erklaertext__quelle" …>Quelle: PDF-Seite 46, 47</p></div>"
```

(18 von 21 Erklärtexten zeigten mehrere Seiten im Singular; die drei Tests der Hilfsfunktion scheiterten an der fehlenden Funktion.)

G-09-03 (`app/src/lib/__tests__/geldfluss.test.ts`, Commit b3b2658):

```
 Test Files  1 failed (1)
      Tests  6 failed | 88 passed (94)
AssertionError: grundsteuer: expected false to be true // Object.is equality
```

Nach dem jeweiligen Fix grün; Gesamtstand der App-Tests in der Scratch-Kopie: 51 Dateien, 2207 Tests grün.

## Task Commits

1. **Task 1: erste fix-Zeile (G-09-01), Querschnitt, Audit** - `3f944a7` (test, rot), `f8aef3f` (fix), `669ba4e` (docs, Audit auf fixed)
2. **Task 2: übrige fix-Zeilen**
   - G-09-02: `74fed1c` (test, rot), `ce5880e` (fix)
   - G-09-03: `b3b2658` (test, rot), `448e43d` (fix)
   - Lückenliste: `d84bc07` (docs)

**Plan metadata:** folgt als Commit „docs(09-14): complete Fixes der Kernaussage-Lücken plan“ (die Zahl `commits: 8` im Frontmatter zählt bis `d84bc07`, ohne diesen Commit).

## Files Created/Modified

- `app/src/lib/kreisumlage.ts` - `kreisumlageWert`, `pruefeGroessterEinzelposten`, `istGroessterEinzelposten`
- `app/src/components/KreisumlageCallout.vue` - Superlativ nur bei wahr, `seitenText` für die Aufteilung
- `app/src/lib/hilfsfunktionen.ts` - `seitenText`
- `app/src/components/ErklaerText.vue` - Quellenzeile über `seitenText`, bei leerer Seitenliste ausgeblendet
- `app/src/pages/AusgabenPage.vue` - Überschusstexte mit `seitenText`
- `app/src/lib/geldfluss.ts` - `berechnet: gruppe.posten.length > 1`
- `app/src/lib/__tests__/kreisumlage.test.ts`, `app/src/lib/__tests__/geldfluss.test.ts` - neue G-09-Tests; bestehende Erwartung für `grundsteuer` umgestellt
- `app/src/lib/__tests__/hilfsfunktionen.test.ts`, `app/src/components/__tests__/erklaertext.test.ts` - neu
- `.planning/v1.0-MILESTONE-AUDIT.md` - Lückenliste, Arbeitsliste, Zeile „09-14: …“

## Decisions Made

- `seitenText([])` liefert `''`; `ErklaerText` blendet die Quellenzeile dann aus. Alle 21 Texte der Daten nennen mindestens eine Seite, der Fall ist heute nicht sichtbar, verhindert aber „Quelle: “ ohne Zahl.
- Für G-09-02 genügt für die Callout-Aufteilung die Hilfsfunktion; heute nennt die Aufteilung nur Seite 46, der Text bleibt dort im Singular. Die Zeile ist damit zukunftssicher, ein roter Test war an dieser Stelle mit den Daten nicht möglich und wurde durch den ErklaerText-Test an der sichtbaren Stelle ersetzt.
- `quellenZeile` und die lokalen Seitentext-Helfer in `StellenplanPage.vue` und `ZuschussListe.vue` unterscheiden schon Singular und Plural; sie wurden nicht zusammengeführt (kein Befund, kein Eingriff).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Prettier-Formatierung nachgezogen**
- **Found during:** Task 2 (G-09-02)
- **Issue:** `npm run format:check` meldete `AusgabenPage.vue` (Zeilenumbruch des Spans) und einen langen Ausdruck in `hilfsfunktionen.test.ts`
- **Fix:** `prettier --write` in der Scratch-Kopie, Ergebnis zurückkopiert, vor dem jeweiligen Commit
- **Files modified:** `app/src/pages/AusgabenPage.vue`, `app/src/lib/__tests__/hilfsfunktionen.test.ts`
- **Committed in:** `ce5880e`, `74fed1c`

---

**Total deviations:** 1 auto-fixed (1 blocking, nur Formatierung)
**Impact on plan:** keine; kein Eingriff in Prüfregeln, Toleranz oder Daten. Es gab keinen Auslöser für das Größenlimit (drei fix-Zeilen, höchstens vier Quelldateien je Zeile).

## Issues Encountered

- Die App-Prüfungen liefen in einer Scratch-Kopie von `app/` mit eigenem `npm ci` (`node_modules` fehlen im Worktree); der Befehlssatz entspricht der Vorgabe (test, type-check, lint, format:check). Playwright und die volle pytest-Suite gehören zu 09-15.
- Bei G-09-01 änderte sich die Seite für die Jahre 2024 bis 2029 nicht sichtbar (Superlativ bleibt wahr); der Fix sichert nur den künftigen Jahrgang.

## Verifikation

- `uv run --directory pipeline ruff check .` und `ruff format --check .`: grün (51 Dateien).
- `uv run --directory pipeline python alle.py --jahr 2026`: Prüfregeln 1 bis 10 grün; `git diff --stat --exit-code -- daten app/src/data` leer; `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` leer. Toleranz und Prüfregeln unverändert.
- App in Scratch-Kopie: vitest 51 Dateien / 2207 Tests grün, `vue-tsc --build`, `eslint .`, `prettier --check src/ e2e/` ohne Befund.
- Skriptprüfung der Lückenliste (Beleg-Hash bekannt, Betreff nennt `09/G-09-NN`, keine Zeile auf `fix`): bestanden.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Threat Flags

None - keine neue Angriffsfläche; die Änderungen betreffen Anzeige-Logik und Tests.

## Next Phase Readiness

- 09-15 (Nachlauf und Abschlusslauf): Die Fixes berühren Dateien, die von den Verifikationsberichten der Phasen 05 und 06 abgedeckt sind (`KreisumlageCallout.vue`, `ErklaerText.vue`, `AusgabenPage.vue`, `geldfluss.ts`); 09-15 schreibt deren Fingerprints neu. Die Berichte wurden hier nicht bearbeitet. Das Frontmatter `status` des Audits bleibt für 09-15.
- Playwright (`scripts/e2e-wie-ci.sh`) wurde hier nicht ausgeführt; die sichtbare Änderung betrifft den Startseiten-Satz, die Quellenzeile der Erklärtexte und das Etikett in der Tabelle „Woher“.

## Self-Check: PASSED

- Dateien vorhanden: alle Einträge unter `key-files` (geprüft mit `[ -f ]` vor dem Commit).
- Commits im Verlauf: 3f944a7, f8aef3f, 669ba4e, 74fed1c, ce5880e, b3b2658, 448e43d, d84bc07.

---
*Phase: 09-sicherheit-und-audit*
*Completed: 2026-10-09*
