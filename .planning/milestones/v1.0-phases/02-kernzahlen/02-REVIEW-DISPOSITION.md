---
phase: 02
review: 02-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`_synthetische_pg_datensaetze` keeps a `plantyp` parameter that is now dead code"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`befunde.md`'s Regel-1 sign description is still inverted relative to the code"
  - id: IN-01
    severity: info
    disposition: skipped
    title: "Duplicate derivation of the D-14 PG-resolution rule in tests vs. production code"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "`_pruefe_regel4_b1` can raise an unhandled `IndexError` instead of a clear `PruefungsFehler` if `spalten` and `jahre` ever go out of sync"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`lies_befunde`'s hand-rolled Markdown table parser has no defence against a `|` inside `begruendung`"
open: 0
total: 5
recorded: 2026-10-01T16:53:08.685Z
---

# Phase 02: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 02-REVIEW-FIX.md, commit 39214cf (verified in 07-02: no `plantyp` parameter left in `_synthetische_pg_datensaetze`) |
| WR-02 | warning | fixed | 02-REVIEW-FIX.md, commit 1f5cfaa (verified in 07-02: `befunde.md` says "Regel 1: Formelkette minus gedruckte Summe") |
| IN-01 | info | skipped | review's own reason "No action required now"; the duplicate D-14 derivation in the tests stays as an independent oracle (07-02, D-20) |
| WR-03 | warning | fixed | commit ee7f4ae (07-02): length guard in `_pruefe_regel4_b1`, test `test_regel4_b1_laengenabweichung_bricht_mit_beiden_laengen_ab` |
| IN-02 | info | fixed | commit ee7f4ae (07-02): `lies_befunde` splits only on unescaped pipes and names line plus hint, tests `test_lies_befunde_unmaskierte_pipe_in_begruendung_nennt_zeilennummer` and `test_lies_befunde_maskierte_pipe_in_begruendung_ist_gueltig` |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

## Nachtrag Phase 7 (D-20)

Triage in Plan 07-02, aus den Review-Dateien und der Git-Historie neu hergeleitet. Die Review-IDs wurden beim erneuten Review wiederverwendet, deshalb passte die D-20-Liste der CONTEXT.md nicht zu diesem Ledger. Die Tabelle oben führt die Befunde der aktuellen `02-REVIEW.md` (WR-03 und IN-02 stammen aus der früheren Review und sind hier mit denselben Inhalten weitergeführt). Zwei weitere Befunde der früheren Review (Commit 4b96997, Datei `02-REVIEW.md`) tragen IDs, die hier schon vergeben sind:

| Frühere ID | Severity | Disposition | Source |
|------------|----------|-------------|--------|
| WR-02 (frühere Review) | warning | fixed | commit ee7f4ae (07-02): Kommentar zu PB 09/15 Z. 29 in `2026_sollwerte.toml` nennt die unabhängig gedruckten Querschnittswerte auf PDF-Seite 296 und 299 als Gegenprobe, Werte unverändert |
| IN-01 (frühere Review) | info | fixed | commit ee7f4ae (07-02): `REGEL3_ZEILEN`-Kommentar in `pruefung.py` benennt jede ausgenommene Zeile (18, 21-33), nur Kommentar |
