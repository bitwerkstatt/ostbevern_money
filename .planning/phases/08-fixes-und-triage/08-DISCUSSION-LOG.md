# Phase 8: Fixes und Triage - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-07
**Phase:** 08-fixes-und-triage
**Areas discussed:** Jahreszahlen in Texten, Lesehilfe und Rundung, Fehlende/abgeleitete Werte, Hygiene-Grenze

---

## Jahreszahlen in Texten

**Historische Jahre**

| Option | Description | Selected |
|--------|-------------|----------|
| Mischung | Relative Schlüssel für Jahre mit Bezug zum Haushaltsjahr, feste Schlüssel (`jahr.fest_2022`) für Ereignisjahre | ✓ |
| Nur relative Versätze | Generisch, aber feste Ereignisjahre wandern mit | |
| Texte umformulieren | Historische Jahre fallen weg | |

**Jahrneutralität**

| Option | Description | Selected |
|--------|-------------|----------|
| jahr.* bindet nicht | `istJahrneutral` ignoriert `jahr.`-Platzhalter | ✓ |
| Pro Abschnitt markieren | Neues Feld „Jahrneutral: ja“ | |

**Titel prüfen**

| Option | Description | Selected |
|--------|-------------|----------|
| Ja, Titel mitprüfen | Lückenlose Ziffernregel | ✓ |
| Nein, nur Absätze | Prüfumfang wie bisher | |

---

## Lesehilfe und Rundung

**Satz bei Ausgleich durch Minderaufwand**

| Option | Description | Selected |
|--------|-------------|----------|
| „Erst der Minderaufwand …“ | Nennt Ursache und Betrag | ✓ |
| „Nur rechnerisch …“ | Betont die Planannahme | |

**Rundungsdifferenzen (2024: 2 €, 2028: 1 €)**

| Option | Description | Selected |
|--------|-------------|----------|
| Text lassen | `texte.json` bleibt byte-identisch | ✓ |
| Zusatz im Text | „bis auf Rundungsdifferenzen“, ändert `texte.json` | |

**Minderaufwand > 0**

| Option | Description | Selected |
|--------|-------------|----------|
| Beide werfen | Einheitlich laut bei Datenfehler | ✓ |
| Beide blenden aus | Tolerant, aber still | |
| Lassen wie es ist | Nur Ledger-Eintrag | |

---

## Fehlende/abgeleitete Werte

| Frage | Optionen | Gewählt |
|-------|----------|---------|
| Fehlende Einwohnerzahl | Laut abbrechen / Sichtbarer Hinweis | Laut abbrechen |
| Stellenplan-Kachelsummen „berechnet“ | Ja, alle Summen / Nur Differenzen | Ja, alle Summen |
| Quellseiten je Kachel | Seiten der gezeigten Werte / Nur Haushaltsjahr-Seiten | Seiten der gezeigten Werte |
| „Zusammen rd. …“ berechnet | Nur wenn berechnet / Immer | Nur wenn berechnet |

---

## Hygiene-Grenze

| Frage | Optionen | Gewählt |
|-------|----------|---------|
| Schwelle „kostet wenig“ | Alles Kleine beheben / Nur Triviales | Alles Kleine beheben |
| 06/IN-09 Quelltexttests | Playwright statt neues Paket / happy-dom + @vue/test-utils / deferred | Playwright statt neues Paket |
| 01/IN-03 beispieldaten | Flag behalten, Icon korrigieren (JSON löschen) / Alles entfernen | Flag behalten, Icon korrigieren |
| 05/IN-02 Slot-Modus | Kommentar, Slot bleibt / Slot-Modus entfernen / MutationObserver | **Slot-Modus entfernen** (gegen die Empfehlung, bewusste Abweichung von den Münster-Props) |

---

## Claude's Discretion

- Barrierefreiheit (A11Y-01…03) nach der vorgeschlagenen Voreinstellung: `beschriftung` Pflicht, ein Name per `aria-labelledby`, Menü schließt bei jedem Link-Klick ohne Fokus-Rücksprung. Vom Nutzer ohne Diskussion übernommen.
- Die Ledger-Dispositionen ohne Code-Arbeit wie vorgeschlagen (01/IN-01, 05/IN-07, 05/IN-09 fixed, 06/WR-01 skipped).
- Schlüsselnamen der `jahr.`-Platzhalter, Wortlaut des Minderaufwand-Satzes, Kurzvariante für `euroKurz`, 06/IN-02 entfernen oder umstellen, Zuschnitt der Pläne.

## Deferred Ideas

Keine.
