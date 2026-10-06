---
phase: 06-kontext-seiten
plan: 04
subsystem: pipeline-texte
tags: [texte, glossar, abgeleitet, polster, schulden, hsk, d-20]

requires:
  - phase: 06-kontext-seiten
    provides: "06-01: meta.vorbericht_werte.hsk_schwelle_ein_jahr / hsk_schwelle_zwei_jahre"
provides:
  - "texte.py: jahr.letztes_jahr und sieben ABGELEITET-Formeln fuer Polster und Schuldenanstieg"
  - "erklaerungen.md: bindungsgrad_selbstauskunft, ueberschuss_produkte, polster, schulden_anstieg (abgenommen)"
  - "glossar.md: nicht_im_haushalt, vzae, entgeltgruppen (abgenommen)"
  - "app/src/data/texte.json regeneriert; GLOSSAR_SCHLUESSEL um drei Begriffe erweitert"
affects: [06-05, 06-06, 06-07]

actuals:
  tokens: 30000
  tasks: 3
  commits: 2

plan_head_before: 0094bff21346ad5ff9315e86e2fbb928e81d29eb
plan_head_after: 319ef84b11460739b01cd33a6b54b7543e720a95

tech-stack:
  added: []
  patterns:
    - "Jahreswertige ABGELEITET-Formeln werden in test_formatiere.py ueber _JAHRWERTIGE_ABGELEITETE als Jahresnamensraum behandelt"

key-files:
  created: []
  modified:
    - pipeline/ostbevern/texte.py
    - pipeline/tests/test_texte.py
    - pipeline/tests/test_formatiere.py
    - daten/manuell/texte/erklaerungen.md
    - daten/manuell/texte/glossar.md
    - app/src/data/texte.json
    - app/src/lib/glossar.ts

key-decisions:
  - "Polster-Text zitiert den Vorbericht (laut Vorbericht), keine eigene rechtliche Bewertung, keine Aussage ueber die Zeit nach dem letzten Planjahr"
  - "haushaltssicherung bleibt unveraendert (Schwellen stehen nur im polster-Text)"

requirements-completed: [RAT-04, ENTW-03, INV-04, STEL-02, UI-04, RAT-01]

duration: continuation
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 04: Polster-, Schulden- und Glossartexte Summary

**Sieben abgenommene Erklaer- und Glossartexte (Polster mit HSK-Schwellen, Schuldenanstieg, RAT-04-Selbstauskunft, VZAe, Entgeltgruppen, nicht_im_haushalt) mit sieben getesteten ABGELEITET-Formeln, in texte.json veroeffentlicht.**

## Accomplishments

- Task 1 (Tracer, Commit 50d5372, aus dem Vorgaenger-Worktree uebernommen): `jahr.letztes_jahr` und die Formeln `ausgleichsruecklage_aufgebraucht_jahr`, `allgemeine_ruecklage_ende_letztes_jahr`, `allgemeine_ruecklage_rueckgang_bis_letztes_jahr`, `schulden_gesamt_vorjahr`, `schulden_gesamt_letztes_jahr`, `kreditaufnahme_ab_haushaltsjahr`, `tilgung_ab_haushaltsjahr`, getestet an den echten Daten.
- Task 2: Fachliche Abnahme (D-20, blocking-human) durch den Nutzer: "freigegeben".
- Task 3 (Commit 319ef84): Die abgenommenen Entwuerfe wurden unveraendert veroeffentlicht, `texte.json` per `alle.py --jahr 2026` regeneriert, `GLOSSAR_SCHLUESSEL` um `nicht_im_haushalt`, `vzae`, `entgeltgruppen` erweitert. Neue Tests: `_PHASE6_SCHLUESSEL`/`_PHASE6_GLOSSAR`, `test_phase6_texte_ohne_platzhalter`, `test_polster_ohne_rechtliche_bewertung`, `test_schulden_anstieg_richtung`, `test_glossar_phase6_begriffe`.

## Entscheidungen aus der Abnahme

Antwort des Nutzers am Checkpoint (woertlich): "freigegeben"

Aufloesung: Alle sieben Entwuerfe (bindungsgrad_selbstauskunft, ueberschuss_produkte, polster, schulden_anstieg, nicht_im_haushalt, vzae, entgeltgruppen) wurden OHNE Korrekturen freigegeben, einschliesslich des polster-Satzes "Laut Vorbericht wird das jedoch nur durch die Erträge aus Grundstücksverkäufen erreicht." und der Formulierung "zum Beispiel beim Umfang und beim Standard der Leistung". Der optionale Punkt 6 (soll `haushaltssicherung` die Schwellen ueber die neuen meta-Platzhalter nennen) wurde nicht gefragt; es gilt der Default, `haushaltssicherung` bleibt unveraendert.

## Task Commits

1. Task 1 (Tracer): `50d5372` feat(06-04): Polster- und Schuldenformeln in texte.py (D-14, D-09)
2. Task 2: Checkpoint, kein Commit
3. Task 3: `319ef84` feat(06-04): abgenommene Erklärtexte und Glossarbegriffe veröffentlichen (D-20)

(`commits: 2` ist ab Basis 0094bff gemessen und zaehlt die beiden Task-Commits; der Summary-Commit folgt danach.)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_formatiere.py (CR-01) lehnte `abgeleitet.ausgleichsruecklage_aufgebraucht_jahr|jahr` ab**
- **Found during:** Task 3, vollstaendiger pytest-Lauf (`test_erklaerungen_rendern_korrekt`, `test_texte_json_rendert_korrekt`)
- **Issue:** Die Pruefung erlaubte das Kuerzel `jahr` nur im Namensraum `jahr.`. Der plangemaesse Platzhalter fuer die jahreswertige Formel lag im Namensraum `abgeleitet.`; ohne `|jahr` wuerde "2.026" erscheinen.
- **Fix:** In `pipeline/tests/test_formatiere.py` die Konstante `_JAHRWERTIGE_ABGELEITETE` eingefuehrt und in `_verstoesse` als Jahresnamensraum behandelt. Eine Endungsregel `_jahr` wurde bewusst verworfen, weil `..._letztes_jahr` Betraege liefert.
- **Files modified:** pipeline/tests/test_formatiere.py
- **Commit:** 319ef84

## Verification

- Pipeline: `pytest` gesamt gruen nach dem Fix (544 passed im Lauf vor dem Fix, die beiden einzigen Fehler waren die oben genannten; `test_formatiere.py` danach 23 passed, `test_texte.py` 75 passed), `ruff check` und `ruff format --check` gruen.
- App-Kette im Scratch-Copy mit Linux-node_modules: type-check, lint, format:check, vitest (1068 passed), build gruen.
- Reproduzierbarkeit: `alle.py --jahr 2026` nach dem Commit erneut gelaufen, `git status` sauber (kein Diff, keine untracked Pfade unter `daten` und `app/src/data`).

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

- 50d5372 und 319ef84 liegen auf dem Branch; texte.py, test_texte.py, erklaerungen.md, glossar.md, texte.json, glossar.ts vorhanden.
