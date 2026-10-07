# Phase 4: Manuelle Daten und App-Daten - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-02
**Phase:** 04-manuelle-daten-und-app-daten
**Areas discussed:** Kreis-und-Land-Herauslösung, Manuelle Tabellen: Einheit & Prüfung, Schulden/Rücklagen/VE, Erklärtexte & Zahlen-Platzhalter, Stellenplan-Struktur, Zuschnitt von haushalt.json, CI-Diff-Prüfung

---

## Kreis-und-Land-Herauslösung

| Option | Description | Selected |
|--------|-------------|----------|
| Ganze Z. 15 von 160101 | Der Block entspricht eurogenau TP 160101 Z. 15. Geprüft wird gegen die Σ der drei Vorberichtsposten. | ✓ |
| Summe der drei T€-Werte | Der Block wird aus dem Vorbericht gebildet und ist nicht eurogenau. | |

| Option | Description | Selected |
|--------|-------------|----------|
| T€-Werte, als gerundet markiert | Unterposten ×1000, Kennzeichen „gerundet“, S. 46 | ✓ |
| Kreisumlage als Rest | Kreisumlage = Z. 15 − GewSt-Umlage − KH-Umlage | |
| Keine Unterposten im Block | Aufschlüsselung nur separat | |

| Option | Description | Selected |
|--------|-------------|----------|
| Eigener Top-Knoten neben den PB | synthetischer Knoten KL, PB 16/PG 1601/160101 reduziert | ✓ |
| Unterknoten von PB 16 | PB 16 bleibt vollständig | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rein nach Formel, Überschuss markiert | Aufwand − Erträge für alle Knoten, `ueberschuss: true` | ✓ |
| Allgemeine Deckungsmittel ausklammern | Sonderregel für Steuern und Schlüsselzuweisung | |

**Notes:** Geprüft ist, dass TP 160101 Z. 15 in allen Jahren genau den drei Umlagen entspricht.

---

## Manuelle Tabellen: Einheit & Prüfung

| Option | Description | Selected |
|--------|-------------|----------|
| T€ wie gedruckt | `betrag_teur`, ×1000 erst in Schritt 07 | ✓ |
| Euro (×1000 beim Abschreiben) | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Langformat | eine Zeile je Posten/Jahr, zentrales Schema | ✓ |
| Breit wie gedruckt | Jahre als Spalten | |

| Option | Description | Selected |
|--------|-------------|----------|
| Zweistufig | Σ Posten = Gesamtzeile exakt; Gesamt ×1000 vs Planzeile ±1.000 € | ✓ |
| Nur Σ Posten gegen Planzeile | ±1 T€ auf die Summe | |

| Option | Description | Selected |
|--------|-------------|----------|
| Die fünf aus der Spez. | 2.1.4, 2.1.6, 2.2.1, 2.2.3, 2.2.6 | ✓ |
| Alle Ergebnisplan-Tabellen 2.1.3–2.2.7 | | |
| Fünf + Sonst. Erträge (2.1.7) | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Einmalig abschreiben, dann von Hand gepflegt | | ✓ |
| Automatischer Pipeline-Schritt | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Errechnet: netto + Rückstellung | 11.472.478 €, gegengeprüft gegen „11,5 Mio.“ | ✓ |
| Gedruckter Text „11,5 Mio. €“ | | |
| Beide speichern | | |

---

## Schulden, Rücklagen, VE (S. 309–311)

| Option | Description | Selected |
|--------|-------------|----------|
| Manuell + Querprüfungen | Querprüfungen gegen GFP, GEP Z. 28 und `ve_faelligkeiten.csv` | ✓ |
| Per Koordinaten extrahieren | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Kaufmännisch auf int-Euro runden | | ✓ |
| Als int-Cent speichern | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Fortschreiben, als berechnet markiert | 2027–2029 = Vorjahr + Z. 33 − Z. 35 | ✓ |
| Nur gedruckte Stände | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Wie Vorbericht: Kredite + NRW.Bank | 7.710 T€, ≈ 656 € je Einwohner | ✓ |
| Nur Investitionskredite | ≈ 586 € je Einwohner | |
| Beides speichern | | |

---

## Erklärtexte & Zahlen-Platzhalter

| Option | Description | Selected |
|--------|-------------|----------|
| Platzhalter mit Datenschlüssel | App formatiert, Schritt 07 validiert Schlüssel | ✓ |
| Pipeline setzt fertige Zahlen ein | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Nur Platzhalter, abgeleitete Werte benannt | Ziffern-Test schlägt bei nackten Zahlen fehl | ✓ |
| Platzhalter, Ausnahmen mit Seitenbeleg | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Vorbericht-Themen für Phase 5 und 6 | ca. 8–10 Texte | ✓ |
| Nur die drei aus MANU-08 | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Claude entwirft, du liest gegen | Checkpoint im Plan | ✓ |
| Nur automatisch geprüft | | |

---

## Stellenplan-Struktur

| Option | Description | Selected |
|--------|-------------|----------|
| int in Hundertstel | `stellen_hundertstel` | ✓ |
| Dezimalzahl (float) | | |

| Option | Description | Selected |
|--------|-------------|----------|
| S. 284–289 vollständig, S. 290 mit | Nachwuchskräfte als eigener Teil, nicht in der Stellensumme | ✓ |
| S. 284–289 ohne S. 290 | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Gegenprobe beim Parsen + Kreuzprüfung | Summenzeilen, Σ PB-Übersicht = Teil A/B, Beamte = 8 | ✓ |
| Nur Sollwert und Gesamtsummen | | |

---

## Zuschnitt von haushalt.json

| Option | Description | Selected |
|--------|-------------|----------|
| Die vier aus DATA-01 + kleine Zusatzdateien | inkl. `texte.json`, Typen zentral | ✓ |
| Eine einzige haushalt.json | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Ergebnisplan + ausgewählte Finanzplan-Zeilen getrennt | getrennte Schlüssel | ✓ |
| Nur Ergebnisplan | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Inkl. Finanzergebnis, vor Minderaufwand | Aufwand = Z. 17 + 20, Erträge = Z. 10 + 19 | ✓ |
| Nur ordentlich (Z. 17 / Z. 10) | | |

---

## CI-Diff-Prüfung

| Option | Description | Selected |
|--------|-------------|----------|
| Eigener Schritt im pipeline-Job, daten/ + app/src/data/ | git diff --exit-code plus ungetrackte Dateien | ✓ |
| Eigener paralleler CI-Job | | |

---

## Claude's Discretion

- Spaltenlisten der neuen CSVs, Dateiaufteilung für Schulden, Eigenkapital und VE, Feldstruktur von `meta.json`
- JSON-Struktur im Detail, Platzhalter-Syntax, Modulaufteilung, Aufteilung von Regel 5, Code des KL-Knotens

## Deferred Ideas

- 2.1.7 Sonstige Erträge/Konzessionsabgaben und weitere Vorberichtstabellen (bei Bedarf Phase 5)
- Darstellung Kreisumlage brutto/netto (Phase 5)
