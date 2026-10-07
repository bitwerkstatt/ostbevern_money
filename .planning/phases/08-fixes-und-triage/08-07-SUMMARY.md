---
phase: 08-fixes-und-triage
plan: 07
subsystem: testing
tags: [vitest, import.meta.glob, quelltext-waechter, rd-regel, stiltokens]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-02/08-04/08-05 haben die rd.-Regel in charts/format.ts zentralisiert und die Altkopien entfernt"
provides:
  - "rdregel.test.ts: Waechter, der jede neue handgebaute rd.-Kopie ausserhalb von charts/format.ts findet (D-22, TXT-04)"
  - "stiltokens.test.ts nennt beide Grenzen des Token-Waechters und meldet dynamische Namen auf '-' statt sie als fehlend zu zaehlen (05/IN-04)"
  - "Jeder Quelltext-Test mit ?raw traegt einen Begruendungskommentar (D-14, 06/IN-09)"
affects: [08-12, 08-06]

actuals:
  tokens: 6500
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Quelltext-Waechter: Kommentare entfernen, dann gezielt nach der verbotenen Schreibweise suchen; Proben fail-first im selben File"
    - "Begruendungskommentar 'Warum Quelltext:' direkt ueber jedem ?raw-Import, endend mit (D-14)"

key-files:
  created:
    - app/src/lib/__tests__/rdregel.test.ts
  modified:
    - app/src/lib/__tests__/stiltokens.test.ts
    - app/src/lib/__tests__/ruecklagen.test.ts
    - app/src/lib/__tests__/quelltext.test.ts
    - app/src/lib/__tests__/duanrede.test.ts
    - app/src/lib/__tests__/menue.test.ts
    - app/src/lib/__tests__/hinweis.test.ts
    - app/src/lib/__tests__/glossar.test.ts
    - app/src/lib/__tests__/quelle.test.ts
    - app/src/lib/__tests__/quelle-kacheln.test.ts
    - app/src/lib/__tests__/quelle-kontext.test.ts
    - app/src/lib/__tests__/quelle-leitfragen.test.ts
    - app/src/lib/__tests__/quelle-ui-abdeckung.test.ts
    - app/src/lib/__tests__/kennzahlen.test.ts
    - app/src/lib/__tests__/stellen.test.ts
    - app/src/lib/__tests__/entwicklung.test.ts
    - app/src/lib/__tests__/schulden.test.ts
    - app/src/lib/__tests__/bindungsgrad.test.ts

key-decisions:
  - "Der Detektor rdKopien() liegt lokal in rdregel.test.ts, nicht in der App: Er ist reine Testhilfe und aendert keinen Produktionscode"
  - "Block- und Zeilenkommentare werden nur am Zeilenanfang oder nach Leerraum entfernt, damit https:// und Glob-Muster in Zeichenketten nicht als Kommentar zaehlen"
  - "stiltokens.test.ts meldet dynamische Tokennamen ueber ctx.skip(Meldung) in einem eigenen Test: sichtbar als uebersprungen mit Namensliste, nie ein Fehlalarm"

patterns-established:
  - "Waechter-Tests pruefen mit einer Mindestdateizahl, dass der Glob nicht leer lief"
  - "Waechter-Tests pruefen zusaetzlich, dass der Detektor in der erlaubten Datei (format.ts) trifft, er also nicht blind ist"

requirements-completed: [TXT-04, TRI-04]

coverage:
  - id: D1
    description: "Waechter-Test gegen neue rd.-Kopien ausserhalb von charts/format.ts, mit Proben fail-first belegt"
    requirement: TXT-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/rdregel.test.ts"
        status: pass
    human_judgment: false
  - id: D2
    description: "Token-Waechter nennt seine Grenzen und ueberspringt Namen auf '-' mit klarer Meldung (05/IN-04)"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stiltokens.test.ts#meldet Namen auf „-“ als dynamisch"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-14-Quelltextpruefung der Formelprosa aus ruecklagen.test.ts entfernt; Vorzeichen-Kommentar zu 06/WR-01 eindeutig"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts"
        status: pass
    human_judgment: true
    rationale: "Ob der Vorzeichen-Kommentar fuer den naechsten Autor eindeutig lesbar ist, ist eine Leseurteil-Frage"
  - id: D4
    description: "Jeder Quelltext-Test mit ?raw (ausser menueVersatz.test.ts aus 08-06) traegt einen D-14-Begruendungskommentar"
    requirement: TRI-04
    verification:
      - kind: other
        ref: "for f in $(grep -l '?raw' ...); do grep -q D-14 $f; done"
        status: pass
    human_judgment: true
    rationale: "Ob jede Begruendung die Konvention treffend benennt, prueft nur ein Leser"

duration: 25min
completed: 2026-10-07
status: complete
plan_head_before: d7e46f410d0503f7ae5b21d85919376c55857325
plan_head_after: 4b45a0773b42c89eba2abda00027c56489d10a60
---

# Phase 8 Plan 07: Waechter gegen rd.-Kopien und begruendete Quelltext-Tests Summary

**Neuer Waechter-Test rdregel.test.ts (import.meta.glob ?raw, Kommentare entfernt, fail-first gegen die Vorphasen-SteuerZeitreihe.vue) sperrt die rd.-Regel auf charts/format.ts; dazu Token-Waechter-Grenzen und D-14-Begruendungen in allen Quelltext-Tests.**

## Performance

- **Duration:** 25 min
- **Completed:** 2026-10-07T18:56:12Z
- **Tasks:** 3 (Task 2 in zwei Commits)
- **Files modified:** 18 (1 neu, 17 geaendert), nur Tests, kein Produktionscode

## Accomplishments

- `rdregel.test.ts`: Detektor `rdKopien()` findet „rd.“ (kein Buchstabe oder Ziffer davor) mit Leerzeichen, U+00A0, ` `/`\xa0`-Escape, `&nbsp;` oder Anfuehrungszeichen dahinter. Es gibt 9 Fund-Proben und 10 Sauber-Proben (Doc-Kommentare mit „rd.“, URL, Glob-Muster, „Standard.“). Der echte Scan laeuft ueber 104 Quelldateien (125 Tests) und ist auf dem aktuellen Code gruen.
- Fail-first belegt: Mit `SteuerZeitreihe.vue` aus Commit 0e7a642 (`<span v-if=…>rd. </span>`) faellt der Test mit der Fundstelle durch.
- Absicherung gegen Blindheit: Mindestdateizahl (Glob > 100, Scan > 80) und ein Test, dass der Detektor in `charts/format.ts` selbst trifft.
- `stiltokens.test.ts` (05/IN-04): Kopfkommentar nennt beide Grenzen, `verwendeteTokens` ueberspringt Namen auf „-“, `dynamischeTokens` und ein eigener Test melden sie per `skip(Meldung)`.
- `ruecklagen.test.ts`: Quelltextpruefung der Formelprosa samt Glob entfernt (`rueckgangFormelText` deckt das Verhalten); Kommentar zu `nachgerechnet` nennt das Vorzeichen eindeutig (06/WR-01, D-17).
- 16 Testdateien mit Quelltext-Zugriff tragen einen „Warum Quelltext“-Kommentar mit (D-14); bindungsgrad und schulden nennen zusaetzlich, dass der Block bewusst die Verdrahtung pinnt (06/IN-09).

## Task Commits

1. **Task 1: Waechter gegen neue rd.-Kopien (05/WR-01, TXT-04)** - `9994371` (test)
2. **Task 2a: Grenzen des Token-Waechters (05/IN-04)** - `567fde7` (test)
3. **Task 2b: Quelltext-Tests begruendet, Vorzeichen-Kommentar (06/IN-09, 06/WR-01)** - `81fcd86` (test)
4. **Task 3: Begruendungskommentare in den uebrigen Quelltext-Tests (06/IN-09)** - `4b45a07` (test)

**Plan metadata:** folgt als `docs(08-07)`-Commit dieser Datei.

## Decisions Made

- Detektor lokal im Test, kein neuer Produktionscode.
- Kommentare werden nur nach Leerraum oder am Zeilenanfang entfernt (Schutz fuer `https://` und Glob-Muster). Bekannte Grenze: ein `//` nach Leerraum innerhalb einer Zeichenkette gilt als Kommentar.
- Sanity-Schwelle: Der Plan nennt „mehr als 100 gescannte Dateien“. Nach Abzug von Tests und `format.ts` bleiben 104 Dateien, daher gilt die 100 fuer den ganzen Glob und 80 fuer die gescannten Dateien, damit ein spaeter entfernter Datei-Satz den Test nicht ohne Not bricht.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] stiltokens.test.ts braucht selbst einen D-14-Kommentar**
- **Found during:** Task 3 (zweiter Verify-Befehl, Schleife ueber alle `?raw`-Dateien)
- **Issue:** Die Schleife meldete `stiltokens.test.ts` ohne Begruendung; Task 2 nannte nur die Grenzen, nicht die D-14-Begruendung.
- **Fix:** „Warum Quelltext“-Absatz im Kopfkommentar ergaenzt (nur Kommentar).
- **Files modified:** app/src/lib/__tests__/stiltokens.test.ts
- **Committed in:** 4b45a07

---

**Total deviations:** 1 auto-fixed (1 blocking). **Impact:** Nur Kommentar, kein Scope-Zuwachs.

## Issues Encountered

- `app/src/lib/__tests__/menueVersatz.test.ts` hat einen `?raw`-Import ohne D-14-Begruendung, gehoert aber 08-06 und wurde nicht angefasst. Die Schleife aus Task 3 meldet deshalb in diesem Worktree `ohne Begruendung: …/menueVersatz.test.ts`. Nach dem Merge von 08-06 sollte dessen Datei den Kommentar tragen; sonst als Rest in 08-12 vermerken.
- Die Acceptance-Pruefung `grep -c "D-14" quelltext.test.ts` ist allein nicht aussagekraeftig: Die Datei enthielt „D-14“ schon in einem Phase-6-Kommentar. Der neue Begruendungskommentar steht trotzdem dort.

## Self-Check

- Alle erzeugten und geaenderten Dateien existieren; die vier Commits liegen auf dem Worktree-Branch.
- Scratch-App (rsync aus dem Worktree): `vitest` 48 Dateien / 2145 Tests gruen, `lint`, `format:check`, `type-check` ohne Befund.
- Fail-first (SteuerZeitreihe.vue aus 0e7a642) rot, aktueller Code gruen.
- `alle.py --jahr 2026` laesst `daten/`, `app/src/data/` und `app/public/quellen` unveraendert (Worktree sauber).

## Self-Check: PASSED

## Known Stubs

None.

## Threat Flags

None. Nur Testdateien geaendert, keine neue Angriffsflaeche. T-08-12 ist mit Kommentarabzug, Proben, Mindestdateizahl und Fail-first-Lauf mitigiert.

## Next Phase Readiness

- TXT-04 ist mit diesem Waechter abgeschlossen (Autoritaet 08-02, Kopien 08-04/08-05). 05/IN-04 und der Kommentarteil von 06/IN-09 sind behoben, 06/WR-01 im Test geklaert; 08-12 schreibt die Disposition.
- Hinweis fuer 08-12: Das Vorzeichen-Kommentar im Quelltext `ruecklagen.ts` gehoert 08-10.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
