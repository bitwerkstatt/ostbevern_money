---
status: complete
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
  artifacts: []
  missing: []
