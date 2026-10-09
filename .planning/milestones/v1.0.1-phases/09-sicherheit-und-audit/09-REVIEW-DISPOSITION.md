---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`istGroessterEinzelposten` wirft statt auf die neutrale Fassung zurückzufallen"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`seitenText` gibt Seitenlisten ungeordnet und ungeprüft aus; die Daten enthalten unsortierte Listen"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Der Superlativ der Startseite nennt als Quelle nur die Gesamtseite, nicht die Seiten, auf denen der Vergleich beruht"
  - id: IN-01
    severity: info
    disposition: open
    title: "Der Fallback-Zweig von `einleitung` ist ungetestet"
  - id: IN-02
    severity: info
    disposition: open
    title: "Region und Tabelle tragen denselben Namen"
  - id: IN-03
    severity: info
    disposition: open
    title: "Doppelter Wortlaut „Weitergabe an Kreis und Land:“ im Template"
open: 6
total: 6
recorded: 2026-10-09T07:47:15.955Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
