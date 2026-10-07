---
status: testing
phase: 07-feinschliff-und-ver-ffentlichung
source: [07-VERIFICATION.md]
started: 2026-10-07T07:47:37Z
updated: 2026-10-07T07:47:37Z
---

## Current Test

number: 1
name: Kacheln auf dem eigenen Gerät (/, /investitionen, /rat-entscheidet, /stellenplan bei 360, 400, 600, 768 und 1280 px)
expected: |
  Jeder Betrag und jeder Knopf „Quelle“ liegt innerhalb der grauen Kachel; kein waagerechtes Scrollen der Seite.
awaiting: user response

## Tests

### 1. Kacheln auf dem eigenen Gerät (/, /investitionen, /rat-entscheidet, /stellenplan bei 360, 400, 600, 768 und 1280 px)
expected: Jeder Betrag und jeder Knopf „Quelle“ liegt innerhalb der grauen Kachel; kein waagerechtes Scrollen der Seite.
result: [pending]

### 2. Korrektur veröffentlichen und öffentliche URL prüfen
expected: Nach Push und grünem CI-Deploy zeigt https://bitwerkstatt.github.io/ostbevern_money/ den Kachel-Fix; keine 404 (Icons, Belegbild unter /ostbevern_money/quellen/), Reload von /#/ausgaben und /#/ueber funktioniert, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
