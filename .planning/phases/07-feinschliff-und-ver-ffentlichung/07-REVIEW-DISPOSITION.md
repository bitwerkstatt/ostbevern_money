---
phase: 07
review: 07-REVIEW.md
titles: json
findings:
  - id: WR-08
    severity: warning
    disposition: fixed
    title: "Eine beschädigte oder von Hand geänderte `belegbilder_schwaerzung.json` bricht Schritt 08 mit rohem Traceback ab"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "Spalte „geschwärzt“ der Datenschutz-Prüfliste gilt je Seite, nicht je Treffer"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`minderaufwandHinweis` formuliert bei positivem GEP-Wert einen negativen „Minderaufwand“"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "`istAufwandsart` vergleicht Zeilennummern als Zeichenketten"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "Fest codierter Farbwert in `StellenNachGruppe`"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "`schulden.ts` erfindet im Tooltip Nullwerte"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "Quell-Seitenleiste nennt bei Zeitreihen nur das Jahr als Bezeichnung"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "Veralteter und lockerer Rahmen"
  - id: IN-08
    severity: info
    disposition: fixed
    title: "Beleg-Link auf die Gemeinde-PDF ist an einen inhaltsgebundenen Pfad geknüpft"
  - id: IN-09
    severity: info
    disposition: fixed
    title: "Die behauptete Mindestreserve von 16 px wird nirgends geprüft und hängt an den Daten"
  - id: IN-10
    severity: info
    disposition: fixed
    title: "`e2e-wie-ci.sh` führt ohne Argumente alle Playwright-Projekte aus und lädt ohne Zeitlimit über HTTP"
  - id: IN-11
    severity: info
    disposition: fixed
    title: "Neue Spec ist nicht prettier-konform, und `format:check` sieht `e2e/` nicht"
  - id: IN-12
    severity: info
    disposition: fixed
    title: "Die Schriftprüfung der CI ist schwächer als ihre Beschreibung (Teilzeichenfolge, Version nur protokolliert)"
  - id: IN-13
    severity: info
    disposition: fixed
    title: "Die Absicherung aus WR-03 ist lückenhaft platziert, und gleichartige Zugriffe bleiben ungeschützt"
  - id: CR-01
    severity: critical
    disposition: deferred
    title: "Namen und Unterschriften zweier Personen stehen ungeschwärzt in einem ausgelieferten Belegbild"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "`lighthouse-a11y.sh` löscht ein vom Nutzer übergebenes `LH_SCRATCH`-Verzeichnis vollständig"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Geänderte Schwärzung wirkt nicht auf vorhandene Bilder (veraltete, ungeschwärzte Datei bleibt erhalten)"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`rendere_seiten` schreibt nicht atomar; ein Abbruch hinterlässt ein kaputtes Bild, das nie erneuert wird"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "Unbehandelte Indexfehler in der Beleg-Suche umgehen die `QuellenFehler`-Behandlung"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "Leere Listen sind jetzt für jeden `[layout.*]`-Schlüssel erlaubt, auch für die Datenschutz-Prüfwörter"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "Startseiten-Kacheln „Erträge“ und „Aufwendungen“ tragen kein „berechnet“, die Seitenleiste nennt sie aber „nicht im PDF“"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "Die Schriftannahme der Breitenkalibrierung wird in der CI weder hergestellt noch geprüft"
  - id: WR-07
    severity: warning
    disposition: fixed
    title: "Der Breitentest hat keine eigene Zeitgrenze; im Fehlerfall reißt er die Standardgrenze von 30 s und verliert seine Diagnose"
open: 0
total: 23
recorded: 2026-10-07T11:00:52.570Z
---

# Phase 07: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-08 | warning | fixed | 07-REVIEW-FIX.md |
| IN-01 | info | fixed | 07-REVIEW-FIX.md |
| IN-02 | info | fixed | 07-REVIEW-FIX.md |
| IN-03 | info | fixed | 07-REVIEW-FIX.md |
| IN-04 | info | fixed | 07-REVIEW-FIX.md |
| IN-05 | info | fixed | 07-REVIEW-FIX.md |
| IN-06 | info | fixed | 07-REVIEW-FIX.md |
| IN-07 | info | fixed | 07-REVIEW-FIX.md |
| IN-08 | info | fixed | 07-REVIEW-FIX.md |
| IN-09 | info | fixed | 07-REVIEW-FIX.md |
| IN-10 | info | fixed | 07-REVIEW-FIX.md |
| IN-11 | info | fixed | 07-REVIEW-FIX.md |
| IN-12 | info | fixed | 07-REVIEW-FIX.md |
| IN-13 | info | fixed | 07-REVIEW-FIX.md |
| CR-01 | critical | deferred | Nutzerentscheidung 2026-10-07: bleibt so — öffentliche Satzung, Amtsträger unterzeichnen in amtlicher Funktion; Bild s009.webp unverändert (not in the current review) |
| CR-02 | critical | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-01 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-02 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-03 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-05 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-06 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |
| WR-07 | warning | fixed | 07-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
