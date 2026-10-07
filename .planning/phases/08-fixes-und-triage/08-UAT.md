---
status: testing
phase: 08-fixes-und-triage
source: [08-VERIFICATION.md]
started: 2026-10-07T22:15:00Z
updated: 2026-10-07T22:15:00Z
---

## Current Test

number: 1
name: Screenreader-Ansage des Tabellennamens bei 360 px auf /ausgaben (VoiceOver oder NVDA)
expected: |
  In eine Datentabelle navigieren, deren Rahmen bei 360 px scrollt. Der Name der Tabelle wird beim
  Betreten von Region und Tabelle nicht störend doppelt vorgelesen (A11Y-03). Wird er es, soll nur
  eines der beiden Elemente (Region oder Caption) den Namen tragen.
awaiting: user response

## Tests

### 1. Screenreader-Ansage des Tabellennamens bei 360 px auf /ausgaben (VoiceOver oder NVDA)
expected: Der Name der Tabelle wird beim Betreten von Region und Tabelle nicht störend doppelt vorgelesen (A11Y-03). Wird er es, soll nur eines der beiden Elemente (Region oder Caption) den Namen tragen.
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
