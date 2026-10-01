# Phase 3: Details - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-01
**Phase:** 03-details
**Areas discussed:** Erläuterungsposten, Investitionen, Personennamen & Freitexte, Grundzahlen & Querschnitte

---

## Erläuterungsposten

**Was gilt als Posten?**

| Option | Description | Selected |
|--------|-------------|----------|
| Nur führender Betrag | Posten beginnt mit Betrag + C; Unterbeträge bleiben im Text; Zeilen ohne Betrag als Freitext | ✓ |
| Auch Unterbeträge einzeln | Jeder Betrag im Text als eigener Posten mit Kennzeichen „zusatz“ | |
| Ganzer Block als Text | Nur Text + Zeilenbezug, kein Betrag | |

**Blöcke ohne „zu Nr.“**

| Option | Description | Selected |
|--------|-------------|----------|
| Mit leerem zu_zeilen | Übernehmen als allgemeiner Hinweis | ✓ |
| Abbruch nach D-08 | Sonderfälle im Code als bekannt eintragen | |
| Weglassen | Nur Blöcke mit „zu Nr.“ | |

**Ablage**

| Option | Description | Selected |
|--------|-------------|----------|
| Beides: CSV + JSON | erlaeuterungen.csv als Quelle, eingebettet in produkte.json | ✓ |
| Nur produkte.json | wie Spez. 4.2 | |
| Nur CSV | Zusammenführung in Phase 4 | |

**Prüfung gegen Plan**

| Option | Description | Selected |
|--------|-------------|----------|
| Nur Plausibilität | Zeilen existieren; kein Posten > Summe der bezogenen Zeilen 2026; Verstoß bricht ab | ✓ |
| Keine Prüfung | nur extrahieren | |
| Summen-Prüfung | Summe der Posten = Zeile (fachlich falsch wegen „u. a.“) | |

---

## Investitionen

**Umfang Regel 6**

| Option | Description | Selected |
|--------|-------------|----------|
| Alle Jahre + VE | alle 7 Spalten | ✓ |
| Nur Ansatz 2026 | nur Roadmap-Sollwert | |
| Ansatz + Planung, ohne Ergebnis 2024 | vorläufiges Ergebnis auslassen | |

**Abgleich mit der PB-Investitionsliste**

| Option | Description | Selected |
|--------|-------------|----------|
| Ja, als Teil von Regel 6 | IDs + Beträge je Maßnahme, PB-Liste nicht ausgeliefert | ✓ |
| Nein, Summenprüfung reicht | | |
| Nur IDs abgleichen | | |

**Art-Kategorie**

| Option | Description | Selected |
|--------|-------------|----------|
| Ja, Spalte `art` aus Konto | feste NKF-Kontengruppen-Zuordnung im Code, unbekanntes Konto bricht ab | ✓ |
| Nein, erst in Phase 4/5 | | |

**Saldozeilen**

| Option | Description | Selected |
|--------|-------------|----------|
| Prüfen, nicht speichern | Gegenprobe beim Parsen, hilft bei ID/Name-Trennung | ✓ |
| Mit ist_summe speichern | | |
| Ignorieren | | |

---

## Personennamen & Freitexte

**Personennamen**

| Option | Description | Selected |
|--------|-------------|----------|
| Nur im Speicher, nie schreiben | Felder erkennen und verwerfen; Test sichert ab | ✓ |
| In daten/aufbereitet/produkte.json | wie Spez. 4.2, Entfernung erst in Phase 4 | |
| In separater, ignorierter Datei | lokal verfügbar, nicht im Repo | |

**Freitext-Aufbereitung**

| Option | Description | Selected |
|--------|-------------|----------|
| Fließtext, Trennung auflösen | Trennstrich vor Kleinbuchstabe entfernen, sonst behalten; Leistungen als Liste | ✓ |
| Zeilen 1:1 erhalten | | |
| Fließtext, Trennstriche immer entfernen | | |

**Feldtyp Ziele/Auftragsgrundlage**

| Option | Description | Selected |
|--------|-------------|----------|
| String, Zeilen mit Leerzeichen | wie Spez. 4.2 | ✓ |
| Liste, Heuristik | | |
| Liste der Rohzeilen | | |

---

## Grundzahlen & Querschnitte

**Stichtags- und Fußnotenhinweise**

| Option | Description | Selected |
|--------|-------------|----------|
| Je Zeile, auf betroffenes Jahr | Stichtag nur an 2025, allgemeine Fußnoten an allen Jahren | ✓ |
| Je Zeile, alle Hinweise für alle Jahre | | |
| Separate Datei je Produkt | | |

**„–“-Werte und Gruppenüberschriften**

| Option | Description | Selected |
|--------|-------------|----------|
| „–“ weglassen, Gruppe als Spalte | analog D-11; Spalte `gruppe`; C → EUR | ✓ |
| „–“ als leerer Wert | | |
| Überschrift als Teil der Bezeichnung | | |

**Umsetzung Regel 7**

| Option | Description | Selected |
|--------|-------------|----------|
| Als CSV in daten/zwischen/ | querschnitte.csv eingecheckt, nur Kontrolle | ✓ |
| Nur im Speicher | | |

**Geprüfte Querschnitt-Spalten**

| Option | Description | Selected |
|--------|-------------|----------|
| Alle Spalten + GESAMTSUMME | 7 Ergebnis- + 11 Finanzplan-Kennzahlen je PG, GESAMTSUMME gegen PB | ✓ |
| Nur Erträge/Aufwendungen/Ergebnis | | |
| Nur GESAMTSUMME je PB | | |

---

## Claude's Discretion

- Spaltenlisten und Sortierung der neuen CSVs, Kodierung von Listen in CSV-Zellen
- Struktur und Prüfung von `ve_faelligkeiten.csv`
- Vokabular von `art` und Kontengruppen-Zuordnung
- Mapping der Querschnitt-Kennzahlen auf Planzeilen
- Bindungsgrad-Normalisierung, mehrseitige Produktinformationen, Modulaufteilung, Ausgestaltung von Regel 8

## Deferred Ideas

Keine.
