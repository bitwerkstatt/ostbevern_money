---
status: complete
phase: 01-setup
source: [01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md, 01-04-SUMMARY.md, 01-05-SUMMARY.md]
started: 2026-10-01T12:00:00Z
updated: 2026-10-01T12:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Kaltstart der App
expected: Nach `rm -rf app/node_modules/.vite`, `npm --prefix app ci` und `npm --prefix app run dev` startet der Server fehlerfrei; die Startseite lädt mit Kopfzeile, Navigation, PageIntro (Jahr aus jahrgang.json) und Beispieldiagramm, die Konsole bleibt fehlerfrei.
result: pass

### 2. Paketfreigabe (01-01 D1)
expected: Die im 01-01-SUMMARY dokumentierte Freigabe aller 26 Pakete (5 PyPI, 21 npm) mit geprüften Quell-Repos und ohne postinstall-Skripte entspricht deiner Entscheidung; installiert ist genau diese Liste.
result: pass

### 3. App-Shell bei 360 px (01-03 D4)
expected: Bei 360 px Viewport bricht die Navigation um, es gibt keinen horizontalen Seiten-Scroll, die PageIntro-Überschrift bricht ohne Überlauf um, der aktive Nav-Link ist goldbraun, der Münster-Money-Credit im Footer ist sichtbar und verlinkt, `#/gibt-es-nicht` leitet zur Startseite um, und der Network-Tab zeigt keine Drittanbieter-Hosts.
result: pass

### 4. BaseChart-Zustände Laden/Fehler/Leer (01-04 D3)
expected: Mit vorübergehend gesetztem `:laedt="true"` zeigt BaseChart einen `<wa-skeleton effect="sheen">` in Diagrammgröße statt Canvas; mit `:fehler="true"` das Dreieck-Ausrufezeichen-Icon und den deutschen Fehlertext statt leerem Canvas; die Karte „Echte Haushaltszahlen" zeigt „Noch keine Daten" zentriert.
result: pass

### 5. Beispieldiagramm und DatenTabelle, voll und 360 px (01-04 D5)
expected: Erste Balken in Ostbevern-Gold, negativer Balken „Bereich D" in Danger-Farbe, deutsche Betragsformatierung in Tooltip/Achse, Beispieldaten-Hinweis sichtbar; bei 360 px werden die Balken horizontal, Hinweis und Tabelle laufen nie seitlich über, die Spalte „Bereich" bleibt beim horizontalen Scrollen fixiert; DatenTabelle mit `:laedt="true"` zeigt drei Skeleton-Zeilen statt leerer Tabelle.
result: pass

### 6. Paketliste dokumentiert (01-01 D2)
expected: Approved package list (names, versions, registry URLs) recorded so plans 01-02 and 01-03 install exactly that list
result: pass
source: automated
coverage_id: 01-01-D2

### 7. Tracer-Slice Pipeline (01-02 D1)
expected: Tracer slice: renamed PDF -> minimal Jahrgangsdatei -> lade_jahrgang -> Rauchtest proves the PDF exists with the expected page count, all from config
result: pass
source: automated
coverage_id: 01-02-D1

### 8. Jahrgangs- und Sollwertdatei (01-02 D2)
expected: Jahrgangsdatei and Sollwertdatei complete, with full key/type/bounds validation and a named German KonfigurationsFehler for every malformed case
result: pass
source: automated
coverage_id: 01-02-D2

### 9. alle.py, ruff, daten/-Layout (01-02 D3)
expected: alle.py validates any --jahr (default STANDARD_JAHR), ruff (check + format) is clean across pipeline/, daten/ layout exists and is tracked
result: pass
source: automated
coverage_id: 01-02-D3

### 10. App-Gerüst baut (01-03 D1)
expected: Vue 3 app skeleton (TS, Vite, Web Awesome, vue-echarts, hash router) scaffolds and builds
result: pass
source: automated
coverage_id: 01-03-D1

### 11. type-check, lint, format:check (01-03 D2)
expected: vue-tsc and ESLint run clean in the CI scripts (type-check, lint, format:check)
result: pass
source: automated
coverage_id: 01-03-D2

### 12. StartPage und Hash-Router (01-03 D3)
expected: StartPage renders PageIntro with the year sourced from jahrgang.json through the hash router; unknown hash routes redirect to start
result: pass
source: automated
coverage_id: 01-03-D3

### 13. format.ts (01-04 D1)
expected: format.ts is the single source of number formatting and matches the plan's golden values exactly
result: pass
source: automated
coverage_id: 01-04-D1

### 14. echartsTheme.ts (01-04 D2)
expected: echartsTheme.ts registers only the needed ECharts modules and the ostbevern-money theme reading WA tokens
result: pass
source: automated
coverage_id: 01-04-D2

### 15. ChartCard und Beispieldaten-Hinweis (01-04 D4)
expected: ChartCard renders title/description/source/pdf chrome and is the sole renderer of the mandatory Beispieldaten notice
result: pass
source: automated
coverage_id: 01-04-D4

### 16. CI-Workflow (01-05 D1)
expected: ci.yml exists with exactly the two parallel jobs pipeline/app, SHA-pinned actions, replaying the locally proven commands
result: pass
source: automated
coverage_id: 01-05-D1

### 17. CLAUDE.md-Dokumentation (01-05 D2)
expected: .claude/CLAUDE.md documents commands and conventions; GSD-managed blocks unchanged; no root CLAUDE.md
result: pass
source: automated
coverage_id: 01-05-D2

### 18. README und LICENSE (01-05 D3)
expected: README.md and LICENSE (MIT, 2026 Thomas Manthey) complete the repo structure with Münster Money credit and quick-start commands
result: pass
source: automated
coverage_id: 01-05-D3

## Summary

total: 18
passed: 18
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
