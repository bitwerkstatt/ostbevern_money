---
status: testing
phase: 06-kontext-seiten
source: [06-VERIFICATION.md]
started: 2026-10-06T08:27:03Z
updated: 2026-10-06T08:27:03Z
---

## Current Test

number: 1
name: Rücklagen-Fußnote auf /entwicklung lesen und mit PDF S. 311 nachrechnen (Entscheidung zum Review-Restpunkt WR-01)
expected: |
  Mit Fehlbetrag 2.353.506 minus Ausgleichsrücklage 2.132.213 = 221.293, plus Betrag der Verrechnung 476.327 = 697.620, geteilt durch 39.522.991 = 1,77 %. Die Fußnote sagt "zuzüglich der Verrechnung" ohne Vorzeichenhinweis; der gedruckte Wert auf S. 311 ist -476.327. Entscheiden: ausreichend (Beträge-Lesart) oder Vorzeichen-Zusatz in rueckgangFormelText() gewünscht.
awaiting: user response

## Tests

### 1. Rücklagen-Fußnote auf /entwicklung lesen und mit PDF S. 311 nachrechnen (Entscheidung zum Review-Restpunkt WR-01)
expected: Rechnung ergibt 1,77 % in der Beträge-Lesart; Entscheidung, ob ein Vorzeichen-Zusatz gewünscht ist.
result: [pending]

### 2. End-of-Phase-Walkthrough aller vier Seiten bei 1280 px und 360 px, nur Maus und Tastatur (Liste in 06-12-SUMMARY.md "Offene Human-Checks", ergänzt um 06-17)
expected: Kein horizontales Scrollen bei 360 px; zweizeilige Achsen lesbar; Direktbeschriftung und "Defizit 3,56 Mio. EUR" haben Platz; Filter per Tastatur bedienbar; /investitionen?pb=04 meldet "1 Maßnahme · zusammen …"; Aufklapper "Produkte hinter dem Balken" mit korrekt dimensionierten Diagrammen; Stellen-Diagramme fluchten bei 1280 px und stapeln bei 360 px.
result: [pending]

### 3. Menü "Mehr wissen": öffnen, Escape (Fokus zurück), Klick außen, Enter/Leertaste, aktiver Zustand; bei 360 px Drawer-Gruppe; erneutes Öffnen und Resize
expected: Wie in 06-02-SUMMARY beschrieben; Liste bleibt bei jedem Öffnen und nach Resize im Viewport.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
