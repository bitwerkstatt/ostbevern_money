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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | – | 7 | Erstes Projekt mit GSD. Strikte Sollwert-Prüfung, Wächter-Tests für Konventionen. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 545 pytest + 1576 vitest (Stand 06-17) + Playwright | – | Lighthouse nur als Einmal-Werkzeug |

### Top Lessons (Verified Across Milestones)

1. (erst nach weiteren Meilensteinen)
