# Phase 5: Leitfragen-Seiten - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-04
**Phase:** 05-leitfragen-seiten
**Areas discussed:** Datenlücken Einnahmen, Treemap & Zuschussbedarf, Navigation/Jahr/Detail, Glossar & Fußzeile

---

## Datenlücken Einnahmen

**Quelle der Steuer-Zeitreihe** (GZ 2024 Gewerbesteuer 8,42 Mio. € vs. Vorbericht 9,51 Mio. €)

| Option | Description | Selected |
|--------|-------------|----------|
| 22–23 GZ, ab 24 VB | 2022–2023 Grundzahlen, 2024–2029 Vorbericht (GEP-konform) | ✓ |
| Spez. wörtlich | Ist 2022–2024 aus GZ, ab 2025 Vorbericht | |
| Beide zeigen | Vorbericht-Reihe + GZ-Punkt mit Befund | |

**Gewerbesteuer-Text mit GZ-Platzhalter 2024**

| Option | Description | Selected |
|--------|-------------|----------|
| Platzhalter auf Vorbericht | Umstellen + Test, Nutzer nimmt ab | ✓ |
| Text unverändert | Text und Diagramm widersprechen sich | |

**Investive Einnahmen / Pauschalen**

| Option | Description | Selected |
|--------|-------------|----------|
| Pauschalen manuell nachtragen | daten/manuell/, Regel 5 gegen GFP | ✓ |
| Nur GFP-Zeilen | ohne Aufschlüsselung | |

**Konzessionsabgaben / Sonstige ordentliche Erträge 2026**

| Option | Description | Selected |
|--------|-------------|----------|
| Vorbericht 2.1.7 abschreiben | gegen GEP Z. 07 prüfen | ✓ |
| GZ-Ist mit Jahreshinweis | 2025-Werte als „zuletzt bekannt“ | |
| Nur Summe | kein Drilldown | |

---

## Treemap & Zuschussbedarf

| Frage | Optionen | Gewählt |
|-------|----------|---------|
| Überschüsse im Zuschussbedarf-Modus | Separate Überschuss-Liste / Kachel mit 0 / Balken statt Treemap | Balken statt Treemap |
| Drilldown-Navigation | Eigene Brotkrumen für beide Sichten / ECharts nativ | Eigene Brotkrumen |
| KL-Callout | Kurz + Aufklapper / Nur kurzer Satz / Ausführlich inline | Kurz + Aufklapper |
| Farbgebung | Farbe je PB / Einfarbig nach Betrag / Du entscheidest | Farbe je PB |

---

## Navigation, Jahr & Detail

| Frage | Optionen | Gewählt |
|-------|----------|---------|
| Produktdetail | Route /produkt/:code / Drawer / Dialog | Route /produkt/:code |
| Jahr-Umschalter | Global + URL / Je Seite / Global im Speicher | Global + URL |
| Sankey-Ausgleich | Knoten wechselt Seite / Sankey nur Plan-Jahre | Knoten wechselt Seite |
| Mobile Alternative | Zwei gestapelte Balken / Nur Tabelle / Sankey vertikal | Zwei gestapelte Balken |
| Kopfmenü | Leitfragen vorn, Rest gruppiert / Flache Liste / Du entscheidest | Leitfragen vorn |

---

## Glossar & Fußzeile

| Frage | Optionen | Gewählt |
|-------|----------|---------|
| Ort der Glossartexte | Pipeline-Texte wie Phase 4 / Direkt in der App | Pipeline-Texte |
| Kontakt | GitHub-Issues / E-Mail / beides | E-Mail — Adresse „später“ (konfigurierbarer Platzhalter, Gate vor Phase 7) |
| GlossarBegriff-Links | Tooltip + Link / Nur Link / Popover | Tooltip + Link |
| Datenstand | Satzungsbeschluss + PDF-Link / zusätzlich Build-Datum | Satzungsbeschluss + PDF-Link |

---

## Claude's Discretion

- Ebene 1 Einnahmen (Balken/Donut), Aufbau Startseite, Sicht nach Aufwandsart, Sankey-Knotenliste, Farbwerte, Komponentenschnitt, Struktur neuer Tabellen, `formatiere()`-Fallback

## Deferred Ideas

- Spiel-Teaser auf Startseite (v2)
- Kontakt-E-Mail festlegen (vor Phase 7)
- GitHub-Issues als Kontaktweg (Phase 7)
