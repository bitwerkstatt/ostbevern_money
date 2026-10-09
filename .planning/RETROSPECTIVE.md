# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-10-07
**Phases:** 7 | **Plans:** 68 (160 tasks) | **Sessions:** nicht erfasst

### What Was Built
- PDF-Pipeline (Schritte 01–08) mit Koordinaten-Parsern für alle Plantypen, Produktinformationen, Investitionen und Stellenplan. Alle Jahrgangswerte stehen in der TOML-Konfiguration.
- Zehn Prüfregeln gegen Gesamtplan, Satzung und Anhang-B-Sollwerte. Abweichungen sind einzeln in `befunde.md` belegt, die Ausgabe ist byte-reproduzierbar.
- Vue-App mit elf Routen: Leitfragen-Seiten (Start, Einnahmen, Ausgaben, Produkt, Geldfluss, Glossar) und Kontextseiten (Entwicklung, Investitionen, Rat, Stellenplan, Über)
- Quellenbelege für 2496 Werte auf gerenderten, geschwärzten PDF-Seiten
- Lighthouse-a11y 100, axe-Smoke-Test, GitHub-Pages-Deploy hinter grüner CI

### What Worked
- Unabhängige Sollwerte (Anhang B) als Referenz. Bei Abweichungen wurde erst das PDF geprüft und dann korrigiert. So fielen auch Fehler in der Referenz selbst auf, z. B. PB 09/15 Z. 29.
- Strikte 1-€-Toleranz ohne pauschale Ausnahmen. Jede Rundungsdifferenz bekommt einen Seitenbeleg und bleibt damit nachvollziehbar.
- Wächter-Tests für Konventionen: getippte Zahlen, `v-html`, `--wa-*`-Tokens, Typografie, Du-Anrede. Damit wurden Konventionen maschinell durchgesetzt statt per Review.
- Horizontale Schichten (Pipeline vor App). Ab Phase 5 waren die Daten stabil, die App-Phasen mussten keine Datenfehler mehr jagen.
- Alle 7 Phasen-Verifikationen passed, UAT in 5 Phasen

### What Was Inefficient
- Viele Gap-Closure-Pläne in Phase 5–7 (16/17/14 Pläne statt ~5). UI-Feinheiten wie Sticky-Header-Sprünge, Token-Hygiene und Kachelbreiten wurden erst im UAT und im UI-Review sichtbar.
- G-07-2: Das Kachelraster war gegen die Fallback-Schrift des Playwright-Images kalibriert, nicht gegen die des GitHub-Runners. Das brauchte einen zusätzlichen Plan und ein eigenes Skript, um die CI-Schrift lokal nachzustellen.
- macOS-Binaries in `app/node_modules` im Linux-Sandbox. App-Checks liefen deshalb dauerhaft in einer Scratch-Kopie.
- Die Phasen-Verifikationen wurden durch spätere Commits „stale“, und es gab kein Milestone-Audit vor dem Abschluss.

### Patterns Established
- Jahrgangswerte nur über `lade_jahrgang`/`lade_sollwerte`, fachliche Regeln im Code
- `pruefung.py` bleibt CSV/JSON-only, PDF-lesende Kontrollquellen sind eigene Extraktionsschritte
- Platzhalter-Vertrag `{{schluessel|kuerzel}}` zwischen Pipeline und `format.ts`, mit Node-Gegenprobe
- Beleg-Schlüssel nur über `belegSchluessel`, mit Vertragstest gegen `quellen.json`
- Layout-Messungen in der CI-Umgebung (Schrift, Runner-Image gepinnt)

### Key Lessons
1. Layout-Prüfungen mit der Schrift der Ziel-Umgebung kalibrieren. Lokale Messungen sind sonst wertlos.
2. Konventionen früh als Tests festschreiben. Nachträgliche Bereinigung, etwa der Phase-5-Token in Phase 7, kostet mehr.
3. UI-Review und UAT schon während der App-Phasen einplanen, nicht erst am Phasenende. Das spart Gap-Closure-Runden.
4. Vor dem Meilenstein-Abschluss `/gsd-audit-milestone` laufen lassen, damit die Verifikation aktuell ist.

### Cost Observations
- Model mix: nicht erfasst (Profil „adaptive“)
- Sessions: nicht erfasst
- Notable: 674 Commits in 7 Tagen. Etwa 1/6 der Commits sind Fixes und Gap-Closures.

---

## Milestone: v1.0.1 — Restpunkte

**Shipped:** 2026-10-09
**Phases:** 2 | **Plans:** 28 (69 tasks) | **Sessions:** nicht erfasst

### What Was Built
- Alle 28 offenen Review-Befunde aus v1.0 haben eine Disposition, die Ledger 01, 05 und 06 stehen auf `open: 0`.
- Texte über Zahlen stimmen auch in Grenzfällen: Jahreszahlen nur als Platzhalter, die rd.-Regel steht nur noch in `format.ts`, die Lesehilfe unterscheidet vier Bilanzfälle und abgeleitete Summen tragen „berechnet“.
- Barrierefreiheit: DatenTabelle-Regionen haben genau einen Namen, das Drawer-Menü schließt bei 360 px bei jedem Link.
- Die Security-Prüfung von Phase 4 ist nachgeholt (21 Threats closed), die Verifikationen 01–08 sind erneuert, und das Milestone-Audit ist auf `tech_debt` abgeschlossen.

### What Worked
- Ledger mit Commit-Hash je Befund. Die Triage war dadurch belegbar statt behauptet.
- Querschnittsbedingung „alle.py byte-identisch“ für jeden Plan. Reine Refactorings blieben nachweislich ohne Wirkung auf die Zahlen.
- Die drei Lücken der Kernaussage, die das Audit gefunden hat, wurden fail-first behoben, jeweils mit einem vorher roten Test.

### What Was Inefficient
- Phase 9 hatte 16 Pläne für eine reine Audit- und Verifikationsphase. Die Berichte wurden nach jedem Fix erneut stale und brauchten Nachträge.
- Der Code-Review von Phase 9 hat 6 neue Befunde erzeugt, die beim Abschluss ohne Disposition bleiben. Das widerspricht dem eigenen Meilensteinziel.

### Patterns Established
- Fingerprint-v3/`covered_digest` in VERIFICATION.md, damit „stale“ maschinell erkennbar ist
- Gepinnter CI-Gesamtlauf (`09-BASISLAUF.md`) als gemeinsame Evidenz für alle Re-Verifikationen

### Key Lessons
1. Den Code-Review der letzten Phase eines Meilensteins mit einplanen. Sonst bleibt am Ende ein neues offenes Ledger übrig.
2. Re-Verifikationen erst nach dem letzten Code-Fix schreiben, um Stale-Nachträge zu vermeiden.

### Cost Observations
- Model mix: nicht erfasst (Profil „adaptive“)
- Sessions: nicht erfasst
- Notable: 217 Commits in 3 Tagen, ohne neue Funktionen.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | – | 7 | Erstes Projekt mit GSD. Strikte Sollwert-Prüfung, Wächter-Tests für Konventionen. |
| v1.0.1 | – | 2 | Reiner Qualitätsmeilenstein: Review-Ledger, Security nachgeholt, Audit vor dem Abschluss. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 545 pytest + 1576 vitest (Stand 06-17) + Playwright | – | Lighthouse nur als Einmal-Werkzeug |
| v1.0.1 | 681 pytest + 2162 vitest + Playwright (ci 89, mobil 41) | – | – |

### Top Lessons (Verified Across Milestones)

1. (erst nach weiteren Meilensteinen)
