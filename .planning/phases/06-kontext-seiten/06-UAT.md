---
status: complete
phase: 06-kontext-seiten
source: [06-VERIFICATION.md]
started: 2026-10-06T08:27:03Z
updated: 2026-10-06T08:39:14Z
---

## Current Test

[testing complete]

## Tests

### 1. Rücklagen-Fußnote auf /entwicklung lesen und mit PDF S. 311 nachrechnen (Entscheidung zum Review-Restpunkt WR-01)
expected: Rechnung ergibt 1,77 % in der Beträge-Lesart; Entscheidung, ob ein Vorzeichen-Zusatz gewünscht ist.
result: pass

### 2. End-of-Phase-Walkthrough aller vier Seiten bei 1280 px und 360 px, nur Maus und Tastatur (Liste in 06-12-SUMMARY.md "Offene Human-Checks", ergänzt um 06-17)
expected: Kein horizontales Scrollen bei 360 px; zweizeilige Achsen lesbar; Direktbeschriftung und "Defizit 3,56 Mio. EUR" haben Platz; Filter per Tastatur bedienbar; /investitionen?pb=04 meldet "1 Maßnahme · zusammen …"; Aufklapper "Produkte hinter dem Balken" mit korrekt dimensionierten Diagrammen; Stellen-Diagramme fluchten bei 1280 px und stapeln bei 360 px.
result: pass

### 3. Menü "Mehr wissen": öffnen, Escape (Fokus zurück), Klick außen, Enter/Leertaste, aktiver Zustand; bei 360 px Drawer-Gruppe; erneutes Öffnen und Resize
expected: Wie in 06-02-SUMMARY beschrieben; Liste bleibt bei jedem Öffnen und nach Resize im Viewport.
result: pass

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
