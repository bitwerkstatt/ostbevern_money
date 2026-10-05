---
status: complete
phase: 05-leitfragen-seiten
source: [05-VERIFICATION.md]
started: 2026-10-04T14:37:16Z
updated: 2026-10-05T18:10:00Z
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
result: pass
retest_of: G-05-4 (resolved by 05-16)
previously_reported: "Auf den Produktseiten liegen Glossarbegriffshülle (\"Bindungsgrad\") und Glossarbegriff (\"teils pflichtig, teils freiwillig\") leicht übereinder (Überschneidung)"

### 5. Geldfluss-Seite je Jahr 2024 bis 2029 ansehen (Plan 05-12)
expected: Sankey bilanziert (Defizit und Minderaufwand links, Überschuss rechts in 2024), Knotenbeschriftungen überlappen bei 700 bis 1280 px nicht, Lesehilfe passt zum Jahr
result: pass

### 6. Glossar öffnen, Sprungmarken und GlossarBegriff-Links aus Seiten testen (Plan 05-13, 05-15)
expected: Link scrollt zum Begriff und setzt den Fokus, Tooltip zeigt den ersten Satz bei Hover und Fokus, Produktakkordeon klappt auf und „Produkt öffnen“ führt zur Produktseite
result: pass
retest_of: G-05-6 (resolved by 05-16)
previously_reported: "Nach dem Klick auf einen Begriff scrollt die Seite zu weit nach oben, das fokussierte Element ist dadurch nicht sichtbar."

### 7. Tastatur- und Skip-Link-Prüfung (Plan 05-07)
expected: Skip-Link „Zum Inhalt springen“ erscheint als erstes fokussierbares Element und springt zum Hauptinhalt; Fokusring überall sichtbar
result: pass

### 8. Fußzeile: Kontakt und Link zum Original-PDF festlegen oder bewusst als Platzhalter belassen (UI-03, ROADMAP SC 1)
expected: Entscheidung des Entwicklers: Die Fußzeile verweist heute auf `kontakt-noch-nicht-festgelegt@example.invalid` und `https://haushaltsplan-noch-nicht-festgelegt.invalid/` (app/src/config.ts). Nutzerentscheidung D-17 verschiebt die echten Werte nach Phase 7; kein Test oder CI-Schritt erzwingt das (IN-09)
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-05-4
  status: resolved
  resolved_by: 05-16-PLAN.md
  resolved_at: 2026-10-05
  truth: "Produktseiten: Abschnittsreihenfolge laut UI-SPEC, Tabelle scrollt bei 360 px mit fester erster Spalte, Zurück-Link führt zur selben Ebene und demselben Jahr; Glossarbegriff und Wert überlappen nicht"
  reason: "User reported: Auf den Produktseiten liegen Glossarbegriffshülle (\"Bindungsgrad\") und Glossarbegriff (\"teils pflichtig, teils freiwillig\") leicht übereinder (Überschneidung)"
  severity: cosmetic
  test: 4
  root_cause: "Im „Auf einen Blick“-Block der Produktseite hat das dt eine kondensierte Zeilenhöhe (1.2 bei font-size-s), dd hat margin 0 und es gibt keinen Abstand zwischen Label und Wert. Seit Plan 05-15 (86ce67e) ist „Bindungsgrad“ ein GlossarBegriff mit text-underline-offset 4px; die gepunktete Unterstreichung liegt unterhalb der dt-Linienbox und wird auf die obere Kante des wa-tag (Rahmen + Füllung) im dd gezeichnet."
  artifacts:
    - path: "app/src/pages/ProduktPage.vue"
      issue: "Zeilen 91-98 und 232-240: dt line-height condensed, dd margin 0, kein Label/Wert-Abstand"
    - path: "app/src/components/GlossarBegriff.vue"
      issue: "Zeilen 36-37: fester text-underline-offset 4px ragt bei kondensierter Zeilenhöhe aus der Linienbox"
  missing:
    - "Abstand zwischen dt und dd im Blick-Block (z. B. dd margin-block-start var(--wa-space-2xs) oder Zeile als Flex-Spalte mit gap)"
    - "Optional: text-underline-offset in GlossarBegriff relativ (z. B. 0.2em)"
  debug_session: .planning/debug/produkt-glossarbegriff-ueberlappung.md

- gap_id: G-05-6
  status: resolved
  resolved_by: 05-16-PLAN.md
  resolved_at: 2026-10-05
  truth: "GlossarBegriff-Link scrollt zum Begriff und setzt den Fokus; der fokussierte Begriff ist danach sichtbar"
  reason: "User reported: Nach dem Klick auf einen Begriff scrollt die Seite zu weit nach oben, das fokussierte Element ist dadurch nicht sichtbar."
  severity: major
  test: 6
  root_cause: "Router-scrollBehavior gibt { el: ziel } ohne top-Offset zurück; vue-router scrollt per window.scrollTo auf y=0 und ignoriert scroll-margin-top. Dort verdeckt der sticky, deckende wa-page-Header den fokussierten Begriff. Zusätzlich ist scroll-margin-top in GlossarListe.vue ungültig, weil der Token --wa-space-md nicht existiert (richtig: --wa-space-m)."
  artifacts:
    - path: "app/src/router/index.ts"
      issue: "Zeilen 99-103: scrollBehavior ohne top-Offset für Hash-Ziele"
    - path: "app/src/components/GlossarListe.vue"
      issue: "Zeile 56: undefinierter Token --wa-space-md macht scroll-margin-top ungültig"
  missing:
    - "Header-Offset beim Hash-Scroll berücksichtigen (top aus computed scrollMarginTop bzw. --header-height, oder scrollIntoView statt Router-Scroll)"
    - "Token --wa-space-md durch --wa-space-m ersetzen"
    - "Test: scrollBehavior liefert für Hash-Ziele einen Offset; optional Test, dass alle var(--wa-*) existieren"
    - "Prüfen: EinnahmenPage.vue:446 scroll-margin-top berücksichtigt Headerhöhe ebenfalls nicht"
  debug_session: .planning/debug/glossar-sprung-scrollt-zu-weit.md
