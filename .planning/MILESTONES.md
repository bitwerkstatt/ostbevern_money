# Milestones

## v1.0 MVP (Shipped: 2026-10-07)

**Delivered:** Öffentliche, statische App unter https://bitwerkstatt.github.io/ostbevern_money/, die den Haushalt 2026 der Gemeinde Ostbevern mit den Leitfragen „Woher?“ und „Wofür?“ erklärt. Jede Zahl stammt aus einer geprüften Python-Pipeline über das 400-seitige ProFIS+-PDF.

**Phases completed:** 7 phases (1–7), 68 plans, 160 tasks
**Timeline:** 7 days (2026-10-01 → 2026-10-07), 674 commits
**Code:** ~25.500 LOC Python (Pipeline), ~29.900 LOC TypeScript/Vue (App inkl. e2e)
**Git range:** `31105eb` (initial commit) → `01c7311`

**Key accomplishments:**
- Pipeline klassifiziert alle 400 PDF-Seiten und extrahiert Gesamt- und Teilpläne, Produktinformationen, Grundzahlen, Erläuterungen, Investitionen, VE-Fälligkeiten und den Stellenplan über Koordinaten-Parser. Alle Jahrgangswerte stehen in `jahrgaenge/2026.toml`.
- Die zehn Prüfregeln sind grün, z. B. Formelketten über 6550 Werte, Anhang-B-Sollwerte, Querschnitte, Investitionssummen und Vollständigkeit aller 63 Produkte. Jede gedruckte Abweichung ist einzeln mit Seite in `befunde.md` belegt. `alle.py` erzeugt `daten/` und `app/src/data/` byte-identisch, die CI prüft das.
- Leitfragen-Seiten: Start mit Kennzahlen, Einnahmen, Ausgaben mit Treemap-Drilldown und herausgelöster „Weitergabe an Kreis und Land“, Produktseiten für alle 63 Produkte, Geldfluss-Sankey und Glossar.
- Kontextseiten: Entwicklung 2024–2029 mit Rücklagen, Investitionen und Schulden, „Worüber entscheidet der Rat?“, Stellenplan und der Hinweis „Was nicht im Haushalt steht“.
- Quellenbelege: 2496 Werte sind mit Zeilenrechteck auf gerenderten, geschwärzten PDF-Seiten belegt und lassen sich über „Quelle anzeigen“ öffnen.
- Barrierefreiheit und Betrieb: Lighthouse-a11y 100 auf allen 11 Routen, axe-Smoke-Test und 360-px-Prüfungen in Playwright, Du-Anrede-Wächter. Der Deploy auf GitHub Pages läuft nur nach grüner CI.

**Closeout:** override_closeout
- Kein Milestone-Audit (`/gsd-audit-milestone`) durchgeführt. Der Nutzer hat entschieden, ohne Audit abzuschließen.
- Known verification overrides: 7 Phasen mit Verifikationsstatus „stale“ (VERIFICATION.md älter als spätere Commits), vom Nutzer akzeptiert. 0 Artefakte acknowledged, 0 aus früheren Abschlüssen übernommen.
- Drei Debug-Sessions (`glossar-sprung-scrollt-zu-weit`, `kachel-kreisumlage-480px`, `produkt-glossarbegriff-ueberlappung`) hat der Nutzer beim Abschluss als gelöst markiert.
- Anforderungen: 85/85 v1-Anforderungen abgehakt.

**Nachtrag 2026-10-09 (v1.0.1, Phase 9):** Audit und Re-Verifikation in v1.0.1 / Phase 9 nachgeholt. Der Bericht `.planning/v1.0-MILESTONE-AUDIT.md` prüft v1.0 und v1.0.1 gemeinsam (Status `tech_debt`, keine offene Lücke der Kernaussage, 97 von 102 Anforderungen ohne Vorbehalt, die übrigen fünf mit begründet zurückgestellten Browser- und Screenreader-Belegen). Die sieben Verifikationen der Phasen 1–7 sind erneuert und stehen nicht mehr auf „stale“. `04-SECURITY.md` liegt mit `threats_open: 0` vor. Der Closeout-Text darüber bleibt als historischer Stand unverändert.

---
