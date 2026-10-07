---
phase: 07
review: 07-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: accepted
    title: "Namen und Unterschriften zweier Personen stehen ungeschwärzt in einem ausgelieferten Belegbild"
  - id: CR-02
    severity: critical
    disposition: open
    title: "`lighthouse-a11y.sh` löscht ein vom Nutzer übergebenes `LH_SCRATCH`-Verzeichnis vollständig"
  - id: WR-01
    severity: warning
    disposition: open
    title: "Geänderte Schwärzung wirkt nicht auf vorhandene Bilder (veraltete, ungeschwärzte Datei bleibt erhalten)"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`rendere_seiten` schreibt nicht atomar; ein Abbruch hinterlässt ein kaputtes Bild, das nie erneuert wird"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Unbehandelte Indexfehler in der Beleg-Suche umgehen die `QuellenFehler`-Behandlung"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Leere Listen sind jetzt für jeden `[layout.*]`-Schlüssel erlaubt, auch für die Datenschutz-Prüfwörter"
  - id: WR-05
    severity: warning
    disposition: open
    title: "Startseiten-Kacheln „Erträge“ und „Aufwendungen“ tragen kein „berechnet“, die Seitenleiste nennt sie aber „nicht im PDF“"
  - id: IN-01
    severity: info
    disposition: open
    title: "Spalte „geschwärzt“ der Datenschutz-Prüfliste gilt je Seite, nicht je Treffer"
  - id: IN-02
    severity: info
    disposition: open
    title: "`minderaufwandHinweis` formuliert bei positivem GEP-Wert einen negativen „Minderaufwand“"
  - id: IN-03
    severity: info
    disposition: open
    title: "`istAufwandsart` vergleicht Zeilennummern als Zeichenketten"
  - id: IN-04
    severity: info
    disposition: open
    title: "Fest codierter Farbwert in `StellenNachGruppe`"
  - id: IN-05
    severity: info
    disposition: open
    title: "`schulden.ts` erfindet im Tooltip Nullwerte"
  - id: IN-06
    severity: info
    disposition: open
    title: "Quell-Seitenleiste nennt bei Zeitreihen nur das Jahr als Bezeichnung"
  - id: IN-07
    severity: info
    disposition: open
    title: "Veralteter und lockerer Rahmen"
  - id: IN-08
    severity: info
    disposition: open
    title: "Beleg-Link auf die Gemeinde-PDF ist an einen inhaltsgebundenen Pfad geknüpft"
---

# Phase 07 — Code Review Disposition

- **CR-01 accepted:** Seite 9 (Haushaltssatzung, Unterzeichner Bürgermeister/Kämmerin) wurde vom Nutzer in der 07-10-Abnahme ausdrücklich freigegeben (07-10-SUMMARY, 07-SECURITY AR-03).
- Alle übrigen Befunde sind **open** und gehen in die Nacharbeit nach Phase 7 (zusammen mit dem UI-Blocker aus 07-UI-REVIEW).
