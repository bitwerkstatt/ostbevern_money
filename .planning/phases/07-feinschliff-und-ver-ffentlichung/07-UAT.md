---
status: diagnosed
phase: 07-feinschliff-und-ver-ffentlichung
source: [07-VERIFICATION.md]
started: 2026-10-07T07:47:37Z
updated: 2026-10-07T08:02:15.332Z
---

## Current Test

[testing complete]

## Tests

### 1. Kacheln auf dem eigenen Gerät (/, /investitionen, /rat-entscheidet, /stellenplan bei 360, 400, 600, 768 und 1280 px)
expected: Jeder Betrag und jeder Knopf „Quelle“ liegt innerhalb der grauen Kachel; kein waagerechtes Scrollen der Seite.
result: pass

### 2. Korrektur veröffentlichen und öffentliche URL prüfen
expected: Nach Push und grünem CI-Deploy zeigt https://bitwerkstatt.github.io/ostbevern_money/ den Kachel-Fix; keine 404 (Icons, Belegbild unter /ostbevern_money/quellen/), Reload von /#/ausgaben und /#/ueber funktioniert, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei.
result: issue
reported: "Der Smoketest auf Github scheitert: [ci] › e2e/kacheln.spec.ts:324:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /rat-entscheidet — Error: /rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px). 1 failed, 80 passed (1.2m). Process completed with exit code 1."
severity: blocker

## Summary

total: 2
passed: 1
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-07-2
  truth: "Nach Push und grünem CI-Deploy zeigt https://bitwerkstatt.github.io/ostbevern_money/ den Kachel-Fix; keine 404 (Icons, Belegbild unter /ostbevern_money/quellen/), Reload von /#/ausgaben und /#/ueber funktioniert, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei."
  status: failed
  reason: "User reported: Der Smoketest auf Github scheitert: [ci] › e2e/kacheln.spec.ts:324:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /rat-entscheidet — Error: /rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px). 1 failed, 80 passed (1.2m). Process completed with exit code 1."
  severity: blocker
  test: 2
  root_cause: "Zwei Bedingungen zusammen: (1) Die Kachelbeträge nutzen nur system-ui; 07-13 kalibrierte die Mindestspaltenbreite 13rem im Playwright-Docker-Image, wo system-ui auf die CJK-Schrift WenQuanYi Zen Hei fällt (141,1 px), während der GitHub-Runner ubuntu-latest DejaVu Sans Bold rendert (164,0 px). (2) Das Raster repeat(auto-fit, minmax(min(100%, 13rem), 1fr)) erzeugt an jedem Spaltensprung (480, 720, 952 px) exakt 208 px breite Spalten; jedes li erbt aus Web Awesomes native.css margin-inline-start 1.125em (18 px), das .om-kachelraster > li nicht zurücksetzt → Inhalt 208 − 18 − 32 = 158 px < 164 px."
  artifacts:
    - path: "app/src/styles/basis.css"
      issue: ".om-kachelraster 13rem gegen falsche Schrift kalibriert; .om-kachelraster > li setzt Web-Awesome-li-Einzug (18 px) nicht zurück"
    - path: "app/e2e/kacheln.spec.ts"
      issue: "BREITEN deckt nur den 2-Spalten-Sprung (480) ab, nicht 720 und 952"
    - path: ".github/workflows/ci.yml"
      issue: "app-Job läuft auf ubuntu-latest mit anderen Schriften als die lokale Kalibrier-Umgebung"
  missing:
    - "margin: 0 (bzw. margin-inline-start: 0) für .om-kachelraster > li"
    - "Mindestspaltenbreite gegen DejaVu Sans Bold neu kalibrieren (mit li-Margin 0: ≥ 212 px ≈ 13.25rem für 16 px Reserve)"
    - "Kalibrier- und CI-Umgebung angleichen (z. B. DejaVu im lokalen Image oder CI-e2e im Playwright-Container mit DejaVu)"
    - "Spaltensprünge 720 und 952 px in BREITEN aufnehmen"
  debug_session: ".planning/debug/kachel-kreisumlage-480px.md"
