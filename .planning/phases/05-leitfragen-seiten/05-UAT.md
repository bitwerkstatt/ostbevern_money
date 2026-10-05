---
status: complete
phase: 05-leitfragen-seiten
source: [05-VERIFICATION.md]
started: 2026-10-04T14:37:16Z
updated: 2026-10-05T17:22:50Z
---

## Current Test

[testing complete]

## Tests

### 1. Kennzahlenband, Einstiege, Kreisumlage-Hinweis und Fußzeile auf der Startseite bei 360 px und 1280 px ansehen (Plan 05-08)
expected: Sieben Kacheln ohne horizontales Scrollen und ohne umbrechende Zahlen; „-2,35 Mio. €“ steht neben „Defizit“; „berechnet“-Etikett zeigt Tooltip bei Fokus; beide Einstiege und der Kreisumlage-Link navigieren
result: pass

### 2. Einnahmen-Seite im Browser durchgehen (Plan 05-09): Aufklapper, Klick auf Ertragsbalken, Zeitreihe je Steuerart, Jahr-Umschalter 2024 bis 2029, investive Einnahmen
expected: Ist und Plan in der Zeitreihe unterscheidbar (Linienart/Legende), Balkenklick öffnet und scrollt zur Aufschlüsselung, Tabellenalternativen erreichbar, Tooltips ohne Fehler
result: pass

### 3. Ausgaben-Treemap und Zuschuss-Balken optisch prüfen (Plan 05-10, 05-14)
expected: „Weitergabe an Kreis und Land“ ist farblich und per Streifenmuster abgesetzt und lesbar (siehe WR-03: Streifen sind möglicherweise vollständig deckend), Überschuss-Punkte, Beschriftungen passen, Tooltips korrekt
result: pass

### 4. Produktseite /#/produkt/030101, /#/produkt/160101 und ein Produkt ohne Investitionen öffnen (Plan 05-11)
expected: Abschnittsreihenfolge laut UI-SPEC, Tabelle scrollt bei 360 px mit fester erster Spalte, Zurück-Link führt zur selben Ebene und demselben Jahr
result: issue
reported: "Auf den Produktseiten liegen Glossarbegriffshülle (\"Bindungsgrad\") und Glossarbegriff (\"teils pflichtig, teils freiwillig\") leicht übereinder (Überschneidung)"
severity: cosmetic

### 5. Geldfluss-Seite je Jahr 2024 bis 2029 ansehen (Plan 05-12)
expected: Sankey bilanziert (Defizit und Minderaufwand links, Überschuss rechts in 2024), Knotenbeschriftungen überlappen bei 700 bis 1280 px nicht, Lesehilfe passt zum Jahr
result: pass

### 6. Glossar öffnen, Sprungmarken und GlossarBegriff-Links aus Seiten testen (Plan 05-13, 05-15)
expected: Link scrollt zum Begriff und setzt den Fokus, Tooltip zeigt den ersten Satz bei Hover und Fokus, Produktakkordeon klappt auf und „Produkt öffnen“ führt zur Produktseite
result: issue
reported: "Nach dem Klick auf einen Begriff scrollt die Seite zu weit nach oben, das fokussierte Element ist dadurch nicht sichtbar."
severity: major

### 7. Tastatur- und Skip-Link-Prüfung (Plan 05-07)
expected: Skip-Link „Zum Inhalt springen“ erscheint als erstes fokussierbares Element und springt zum Hauptinhalt; Fokusring überall sichtbar
result: pass

### 8. Fußzeile: Kontakt und Link zum Original-PDF festlegen oder bewusst als Platzhalter belassen (UI-03, ROADMAP SC 1)
expected: Entscheidung des Entwicklers: Die Fußzeile verweist heute auf `kontakt-noch-nicht-festgelegt@example.invalid` und `https://haushaltsplan-noch-nicht-festgelegt.invalid/` (app/src/config.ts). Nutzerentscheidung D-17 verschiebt die echten Werte nach Phase 7; kein Test oder CI-Schritt erzwingt das (IN-09)
result: pass

## Summary

total: 8
passed: 6
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-05-4
  truth: "Produktseiten: Abschnittsreihenfolge laut UI-SPEC, Tabelle scrollt bei 360 px mit fester erster Spalte, Zurück-Link führt zur selben Ebene und demselben Jahr; Glossarbegriff und Wert überlappen nicht"
  status: failed
  reason: "User reported: Auf den Produktseiten liegen Glossarbegriffshülle (\"Bindungsgrad\") und Glossarbegriff (\"teils pflichtig, teils freiwillig\") leicht übereinder (Überschneidung)"
  severity: cosmetic
  test: 4
  artifacts: []
  missing: []

- gap_id: G-05-6
  truth: "GlossarBegriff-Link scrollt zum Begriff und setzt den Fokus; der fokussierte Begriff ist danach sichtbar"
  status: failed
  reason: "User reported: Nach dem Klick auf einen Begriff scrollt die Seite zu weit nach oben, das fokussierte Element ist dadurch nicht sichtbar."
  severity: major
  test: 6
  artifacts: []
  missing: []
