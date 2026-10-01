# Phase 2: Kernzahlen - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-01
**Phase:** 2-Kernzahlen
**Areas discussed:** Prüfbericht & befunde.md, Tests: PDF oder CSV, Datentreue im Langformat, Produktgruppen-Ebene, Seitenklassifikation-Umfang, Sollwerte vervollständigen, CSV-Konventionen

---

## Prüfbericht & befunde.md

| Option | Description | Selected |
|--------|-------------|----------|
| Bibliothek + beide | Logik in ostbevern/pruefung.py; 06_pruefen.py und pytest schreiben den Bericht | ✓ |
| Nur pytest | Bericht als Nebenprodukt von pytest | |
| Nur 06_pruefen.py | Skript schreibt, pytest prüft nur | |

| Option | Description | Selected |
|--------|-------------|----------|
| Markdown + Schlüsseltabelle | Eine Datei, parsbare Tabelle | ✓ |
| Separate TOML + md | befunde.toml + Erläuterungen | |
| Du entscheidest | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Zusammenfassung + Abweichungen | Status je Regel, Details nur bei Abweichungen | ✓ |
| Vollständige Matrix | Jeder Wert mit Soll/Ist | |

| Option | Description | Selected |
|--------|-------------|----------|
| Veralteter Befund = Fehler | | ✓ |
| Warnung im Bericht | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Betrag muss passen (±1 €) | | ✓ |
| Nur Schlüssel | | |

---

## Tests: PDF oder CSV

| Option | Description | Selected |
|--------|-------------|----------|
| Eingecheckte CSVs | Schnell, PDF-Abgleich über CI-Diff ab Phase 4 | ✓ |
| PDF bei jedem Lauf | Frische Extraktion je pytest-Lauf | |
| Beides, PDF als Marker | Zusätzlicher markierter PDF-Test | |

| Option | Description | Selected |
|--------|-------------|----------|
| Echte PDF-Seiten | Unit-Tests auf ausgewählten Seiten | ✓ |
| Synthetische Wortlisten | | |
| Du entscheidest | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Sofort abbrechen | Mit Seite und Zeile | ✓ |
| Sammeln, dann abbrechen | | |
| Warnung, weiterlaufen | | |

| Option | Description | Selected |
|--------|-------------|----------|
| alle.py führt 01/02/06 aus | | ✓ |
| Erst Phase 4 | | |

---

## Datentreue im Langformat

| Option | Description | Selected |
|--------|-------------|----------|
| Vorzeichen wie gedruckt | Operator als eigene Spalte | ✓ |
| Normalisiert | Aufwand negativ | |

| Option | Description | Selected |
|--------|-------------|----------|
| Nullzeilen weglassen | Fehlend = 0 | ✓ |
| Mit 0 auffüllen | Kennzeichen gedruckt=false | |

| Option | Description | Selected |
|--------|-------------|----------|
| Festes Wörterbuch | PDF-Text wird dagegen geprüft | ✓ |
| Aus dem PDF rekonstruiert | Leerzeichen wiederherstellen | |

---

## Produktgruppen-Ebene

| Option | Description | Selected |
|--------|-------------|----------|
| Gedruckte PG extrahieren + zweistufig prüfen | | ✓ |
| Nur klassifizieren | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Synthetische PG nur in hierarchie.csv | | |
| Auch Planzeilen | Kopien der Produktzeilen | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| Namen aus Kopfzeilen der Planseiten | | ✓ |
| Anhang A / Inhaltsverzeichnis | | |

| Option | Description | Selected |
|--------|-------------|----------|
| bool-Spalte synthetisch | pdf_seite der Produktseite | ✓ |
| Eigene ebene PG_SYNTH | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Anhang A in 2026_sollwerte.toml | | ✓ |
| In 2026.toml | | |
| Aus dem Inhaltsverzeichnis gelesen | | |

---

## Seitenklassifikation-Umfang

| Option | Description | Selected |
|--------|-------------|----------|
| Alle 400 Seiten | Kapitelname als typ außerhalb der Teilpläne | ✓ |
| Nur Teil- und Gesamtpläne | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Feines Typ-Vokabular | inkl. grundzahlen, erlaeuterungen, investitionen_pb/_produkt | ✓ |
| Grob nach Spez. 5.3 | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Unbekannte Seite = Abbruch | | |
| typ=unbekannt, weiterlaufen | Im Bericht gelistet | ✓ |

---

## Sollwerte vervollständigen

| Option | Description | Selected |
|--------|-------------|----------|
| Anhang B wie dokumentiert | B.1 komplett, B.2, B.3, Satzung, Anhang A | ✓ |
| S. 62/63 vollständig abschreiben | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Executor + menschliche Stichprobe | | |
| Nur Executor | Konsistenzregeln fangen Tippfehler | ✓ |

---

## CSV-Konventionen

| Option | Description | Selected |
|--------|-------------|----------|
| Standard-Set | UTF-8, Komma, LF, Codes als Strings mit führender Null, deterministische Sortierung | ✓ |
| Du entscheidest | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Zentrales polars-Schema im Code | | ✓ |
| Nein | | |

---

## Claude's Discretion

- Genaue Spaltenliste, `zeile_kanonisch`-Schlüssel, Typ-Vokabular im Detail
- Spaltenzuordnung per x-Koordinaten, Fortsetzungsseiten
- Modulaufteilung in `ostbevern/`, Format der befunde-Schlüsseltabelle und von konsistenz.md

## Deferred Ideas

Keine.
