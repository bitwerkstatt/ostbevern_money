# Phase 2: Kernzahlen - Context

**Gathered:** 2026-10-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Die Pipeline liest aus `raw_data/haushalt-2026.pdf` alle Ergebnis- und Finanzpläne (Gesamt, PB, PG, Produkt) und weist ihre Korrektheit automatisch nach:
- **01 Seitenklassifikation:** `daten/zwischen/seiten.csv` für alle 400 Seiten. Dazu kommt `hierarchie.csv` mit 15 PB, allen PG (gedruckt und synthetisch) und 63 Produkten.
- **Zahlenparser:** deutsches Format, Minus, „–“ als „kein Wert“, angeklebte Beträge, `C` als Eurozeichen; mit Unit-Tests
- **02 Pläne extrahieren:** `ergebnisplan.csv` und `finanzplan.csv` (inklusive VE-Spalte) im Langformat
- **06 Prüfen:** Prüfregeln 1–4, Anhang-B-Sollwerte (B.1–B.3, Satzung § 1), Bericht `daten/pruefberichte/konsistenz.md` und `befunde.md`

Nicht in dieser Phase: Produktinformationen, Grundzahlen, Erläuterungen und Investitionsmaßnahmen (Phase 3), manuelle Tabellen, Stellenplan, App-JSON und die CI-Diff-Prüfung (Phase 4). Die Prüfregeln 5–8 folgen später.

</domain>

<decisions>
## Implementation Decisions

### Prüfbericht und befunde.md
- **D-01:** Die Prüflogik liegt einmal in der Bibliothek (`ostbevern/pruefung.py` o. ä.). Zwei Einstiege nutzen sie: `pipeline/06_pruefen.py` (läuft in `alle.py`) schreibt `daten/pruefberichte/konsistenz.md`. pytest ruft dieselbe Logik auf, prüft per Assert und schreibt den Bericht ebenfalls (Erfolgskriterium 5).
- **D-02:** `daten/pruefberichte/befunde.md` ist Markdown für Menschen. Jeder Befund hat Begründung und PDF-Seite. Die Datei enthält eine **maschinenlesbare Schlüsseltabelle**, die der Code parst. Die Spalten sind sinngemäß Regel, Ebene, Code, Zeile, Jahr und erwartete Abweichung in €. Mensch und Maschine nutzen dieselbe Datei; eine zweite Datei gibt es nicht.
- **D-03:** `konsistenz.md` enthält je Regel eine Statuszeile (grün/rot, Anzahl geprüfter Werte). Im Detail stehen nur Abweichungen und bekannte Befunde, keine vollständige Soll/Ist-Matrix. So bleibt der Diff stabil.
- **D-04:** Tritt ein Befund aus `befunde.md` nicht mehr auf, ist er **veraltet, und das gilt als Fehler**. Die Datei darf keine Fehler still verdecken.
- **D-05:** Ein Befund deckt eine Abweichung nur ab, wenn der **Betrag passt**. Weicht die tatsächliche Differenz um mehr als 1 € von der dokumentierten ab, ist das ein neuer Fehler.

### Teststrategie
- **D-06:** Die Prüfregel-Tests (Regeln 1–4, Sollwerte, Anhang-A-Startseiten) lesen die **eingecheckten CSVs** unter `daten/zwischen/` und `daten/aufbereitet/`, nicht das PDF. Dass CSV und PDF zusammenpassen, sichert ab Phase 4 die CI-Diff-Prüfung von `alle.py` (PRUEF-10).
- **D-07:** Die Unit-Tests für Seitenklassifikation und Planzeilen-Parser lesen **ausgewählte echte PDF-Seiten** aus `raw_data/haushalt-2026.pdf`, z. B. 62, 63, 66, 83, 86 und Fortsetzungsseiten. Der Zahlenparser wird mit reinen String-Tests geprüft.
- **D-08:** Kann die Extraktion eine Planzeile oder Planseite nicht lesen, **bricht sie sofort mit PDF-Seite und Zeile ab**. Beispiele: falsche Anzahl an Werten, unbekannte Zeilennummer, Text passt nicht zum Wörterbuch. Nichts wird still übersprungen. Ausnahme ist die Seitenklassifikation, siehe D-17.
- **D-09:** `pipeline/alle.py` führt in Phase 2 die Schritte **01 → 02 → 06** in Reihenfolge aus. Spätere Phasen hängen ihre Schritte an.

### Datentreue im Langformat
- **D-10:** Beträge werden **mit dem gedruckten Vorzeichen** gespeichert. Aufwendungen sind positiv (Z. 17), der Minderaufwand ist negativ (GEP Z. 27 = −600.000), Ergebnisse tragen ihr Vorzeichen. Der gedruckte **Operator** (`+`, `-`, `=`, `+/-`) steht in einer eigenen Spalte. Die Zeilenformeln der Prüfregeln kennen die Rechenrichtung. — **Reversibility:** costly — Phase 4 (App-JSON), die Prüfregeln und alle Konsumenten verlassen sich auf diese Vorzeichenkonvention.
- **D-11:** Zeilen, die das PDF nicht druckt, kommen **nicht in die CSV**. Jede CSV-Zeile entspricht einer gedruckten Zeile mit `pdf_seite`. Prüfungen und spätere Schritte behandeln Fehlendes als 0. Gedruckte Nullzeilen, z. B. „09 Bestandsveränderungen 0 0 0“, werden normal übernommen.
- **D-12:** `zeile_name` und `zeile_kanonisch` kommen aus einem **festen Wörterbuch im Code**. Es ist je Plantyp (Gesamtergebnisplan, Teilergebnisplan, Gesamtfinanzplan, Teilfinanzplan) nach Zeilennummer geschlüsselt und gilt als fachliche Regel (Phase 1 D-07). Der gelesene PDF-Text wird leerzeichenunabhängig dagegen geprüft, denn pdfplumber liefert z. B. „ZuwendungenundallgemeineUmlagen“. Passt er nicht, bricht die Extraktion nach D-08 ab.

### Produktgruppen-Ebene
- **D-13:** Die 8 **gedruckten PG** (0106, 0110, 0112, 0301, 0501, 0602, 0902, 1201) haben eigene Teilpläne, z. B. S. 83. Diese werden als `ebene=PG` mit `pdf_seite` extrahiert. **Regel 2 prüft zweistufig:** Σ Produkte = PG und Σ PG = PB, je Zeile und Jahr.
- **D-14:** **Synthetische PG** (eine PG mit nur einem Produkt, nicht gedruckt) erscheinen in `hierarchie.csv` mit `synthetisch=true`. Der Code besteht aus den ersten 4 Ziffern des Produktcodes, der Name ist der Produktname. Sie **bekommen auch Planzeilen** in `ergebnisplan.csv` und `finanzplan.csv`. Das sind Kopien der Produktzeilen mit `ebene=PG`, der bool-Spalte `synthetisch=true` und der `pdf_seite` der Produktseite. Gedruckte Zeilen tragen `synthetisch=false`. Regel 2 behandelt die synthetischen PG wie gedruckte (trivial grün), Regel 3 summiert nur PB.
- **D-15:** Die Namen in `hierarchie.csv` stammen aus den **Kopfzeilen der Planseiten**, z. B. „Produkt 010601 Zentrale Dienste für Organisationseinheiten im / Hause und Dritter“. Mehrzeilige Namen werden zusammengeführt. Die Kopfzeilen haben normale Leerzeichen.

### Seitenklassifikation
- **D-16:** `seiten.csv` enthält **alle 400 Seiten**. Außerhalb der Gesamt- und Teilpläne ist `typ` der Kapitelname aus `[seitenbereiche]` der Jahrgangsdatei, z. B. `vorbericht`, `stellenplan`, `querschnitte`. PB, PG und Produkt bleiben dort leer.
- **D-17:** Im Teilplanbereich gilt ein **feines Typ-Vokabular**, sinngemäß `produktinformationen`, `grundzahlen`, `teilergebnisplan`, `erlaeuterungen`, `teilfinanzplan`, `investitionen_pb`, `investitionen_produkt` usw. Phase 3 braucht Grundzahlen und Erläuterungen ohnehin. Fortsetzungsseiten erben den Kontext. Eine Seite im Teilplanbereich, die keinem Muster entspricht, bekommt **`typ=unbekannt`**. Sie wird in `konsistenz.md` gelistet, und der Lauf geht weiter. Das ist eine bewusste Ausnahme zu D-08. Die Plan-Extraktion bricht aber weiterhin ab, wenn eine erwartete Planseite fehlt oder nicht lesbar ist.

### Sollwerte
- **D-18:** Phase 2 füllt `pipeline/jahrgaenge/2026_sollwerte.toml` mit **Anhang B, wie er dokumentiert ist**:
  - B.1 vollständig (alle Tabellenzeilen, 6 Jahre)
  - B.2 (Werte 2026)
  - B.3 je PB (ordentliche Erträge, ordentliche Aufwendungen, TP Z. 29)
  - Satzung § 1 (vorhanden)

  Fehlende Zeilen von S. 62/63 werden nicht zusätzlich abgeschrieben. Die Regeln 1–3 sichern den Rest über Konsistenz.
- **D-19:** Das **Anhang-A-Produktverzeichnis** (Codes und Startseiten von PB, gedruckten PG und Produkten) steht ebenfalls in `2026_sollwerte.toml`. Es dient als Sollwert für den Startseiten-Test und nicht als Steuerung der Extraktion.
- **D-20:** Der Executor überträgt die Sollwerte aus `discussion/SPEZIFIKATION.md` Anhang A/B. Eine zusätzliche menschliche Gegenprüfung gegen das PDF ist nicht vorgesehen. Tippfehler fallen über die Konsistenzregeln auf.

### CSV-Konventionen
- **D-21:** Alle CSVs unter `daten/zwischen/` und `daten/aufbereitet/` folgen denselben Regeln:
  - Zeichensatz UTF-8 ohne BOM, Komma als Trennzeichen, LF als Zeilenende, mit Kopfzeile
  - Codes und Zeilennummern sind **Strings mit führender Null** („03“, „0106“, „030101“, „01“)
  - bool als `true`/`false`, Beträge als int
  - feste Spaltenreihenfolge und deterministische Sortierung (sinngemäß ebene, code, zeile, jahr, wertart), damit Diffs stabil bleiben — **Reversibility:** costly — Ab Phase 4 hängen die CI-Diff-Prüfung und die App-JSON-Erzeugung an diesem Format.
- **D-22:** Die Schemas (Spalten und polars-Typen je Datei) stehen **zentral in einem Bibliotheksmodul**. Schreiben und Lesen laufen darüber, auch in den Tests. So wird z. B. „01“ nie zu 1.

### Claude's Discretion
- Genaue Spaltenliste von `ergebnisplan.csv` und `finanzplan.csv` über Spez. 4.2 hinaus, z. B. Name der Operator-Spalte und Position von `synthetisch`, `ist_summe` und `zeile_kanonisch`
- Konkrete Schlüssel für `zeile_kanonisch` und das genaue Typ-Vokabular in `seiten.csv`
- Spaltenzuordnung über x-Koordinaten (bevorzugt nach Spez. 5.4), Behandlung mehrzeiliger Kopfzeilen und Fortsetzung von Teilplänen über Seiten hinweg
- Modulaufteilung in `ostbevern/` (z. B. `zahlen.py`, `pdf.py`, `seiten.py`, `plaene.py`, `pruefung.py`, `schema.py`)
- Schreibweise der Schlüsseltabelle in `befunde.md` und Aufbau von `konsistenz.md` im Rahmen von D-02/D-03
- Ob neue Kopfzeilen-Muster (z. B. `Produktgruppe`) nötig sind; sie kommen in `2026.toml`
- Wie pytest und `06_pruefen.py` beim Schreiben des Berichts dieselbe Ausgabe erzeugen, ohne sich zu stören

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §2, §2.1, §2.2 — PDF-Aufbau, Gliederung der Teilpläne (PB/PG/Produkt, synthetische PG), Spalten der Plantabellen, `C` als Eurozeichen
- `discussion/SPEZIFIKATION.md` §3.1–3.3 — Ergebnis- und Finanzplan, unterschiedliche Zeilennummern in Gesamt- und Teilplänen (GP 27/28 und TP 27–31), Ausschluss von TP 27/28, fehlende Zeilen = 0, Minderaufwand
- `discussion/SPEZIFIKATION.md` §3.8 — bekannte Datenauffälligkeiten (Kandidaten für `befunde.md`)
- `discussion/SPEZIFIKATION.md` §4.1, §4.2 — gemeinsame Felder (`jahr`, `wertart`, `betrag`, `pdf_seite`), Schema von `hierarchie.csv`, `ergebnisplan.csv` und `finanzplan.csv`
- `discussion/SPEZIFIKATION.md` §5.2–5.5 — Skriptfolge, Seitenklassifikation, Planzeilen-Parsing (x-Koordinaten), Prüfregeln 1–4
- `discussion/SPEZIFIKATION.md` Anhang A — Produktverzeichnis mit Startseiten (Quelle für D-19)
- `discussion/SPEZIFIKATION.md` Anhang B.1–B.3 — Sollwerte (Quelle für D-18)

### Projektplanung
- `.planning/REQUIREMENTS.md` — EXTR-01 bis EXTR-05, PRUEF-01 bis PRUEF-04, PRUEF-09
- `.planning/ROADMAP.md` — Phase 2, Erfolgskriterien 1–5
- `.planning/phases/01-setup/01-CONTEXT.md` — D-06 bis D-10 (Jahrgangskonfiguration, `--jahr`, Skriptaufbau)
- `.claude/CLAUDE.md` — Befehle und Konventionen (u. a. `uv run --directory pipeline …`)

### Quelle und Konfiguration
- `raw_data/haushalt-2026.pdf` — Quell-PDF (400 Seiten)
- `pipeline/jahrgaenge/2026.toml` — Spaltenköpfe, Seitenbereiche, Kopfzeilen-Muster, Anzahlen
- `pipeline/jahrgaenge/2026_sollwerte.toml` — wird in Phase 2 vervollständigt

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pipeline/ostbevern/konfiguration.py`: `lade_jahrgang`, `lade_sollwerte`, `STANDARD_JAHR`, `PROJEKT_WURZEL`, `KonfigurationsFehler`, Dataclasses `Jahrgang`, `Seitenbereich`, `Kopfzeilen`, `Anzahlen`. Neue Konfigurationsschlüssel, etwa für Anhang A oder ein PG-Kopfzeilenmuster, brauchen dort Validierung.
- `pipeline/alle.py`: typer-Einstieg mit `--jahr`. Hier werden die Schritte 01/02/06 angehängt (D-09).
- `pipeline/tests/`: `test_konfiguration.py`, `test_rauchtest.py`, `test_alle.py` als Muster für neue Tests

### Established Patterns
- Dünne typer-Skripte mit `--jahr`, die Logik liegt in `ostbevern/`
- Jahrgangswerte nur in TOML, gelesen über den Lader. Fachliche Regeln stehen im Code.
- ruff (E, F, I, UP, B), Zeilenlänge 100. pytest mit `pythonpath = ["."]`.
- Deutsche Bezeichner ohne Umlaute

### PDF-Beobachtungen (Stichprobe)
- `extract_text()` liefert Zeilentexte ohne Leerzeichen („AufwendungenfürSach-undDienstleistungen“). Kopfzeilen wie „Produktbereich 01 Innere Verwaltung“ haben dagegen Leerzeichen.
- Produktnamen in der Kopfzeile können über zwei Zeilen laufen (S. 84–86).
- Gedruckte PG haben einen eigenen Teilergebnisplan mit der Kopfzeile „Produktgruppe 0106 Zentrale Dienste“ (S. 83).
- Die Spaltenköpfe stehen auf zwei Zeilen („Ergebnis Ansatz …“ / „2024 2025 …“).
- Die PB-Investitionsliste (z. B. S. 67) folgt direkt auf den PB-Teilergebnisplan. Sie ist für Phase 2 nur zu klassifizieren.
- Formelhinweise im Text, z. B. „OrdentlichesErgebnis(Z.10+17)“: Die Aufwendungen sind positiv gedruckt, Z. 18 = Z. 10 − Z. 17.

### Integration Points
- Ausgaben: `daten/zwischen/seiten.csv`, `daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan}.csv`, `daten/pruefberichte/{konsistenz,befunde}.md`
- Phase 3 nutzt `seiten.csv`, z. B. die Typen `produktinformationen`, `grundzahlen`, `erlaeuterungen` und `investitionen_produkt`, und das CSV-Schema-Modul.

</code_context>

<specifics>
## Specific Ideas

- Sollwert-Beispiele: GEP Z. 28 2026 = −2.353.506 €; GFP Z. 23 = 7.224.830 €, Z. 30 = 12.280.484 €, Z. 33 = 5.200.000 €, Z. 41 = 4.199.420 €; Σ PB Erträge 27.042.063 €, Σ PB Aufwendungen 30.255.569 €; Satzung § 1 Erträge 27.502.063 €, Aufwendungen 30.455.569 €
- Die Datei `befunde.md` soll Fehler nie still verdecken (D-04, D-05).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-kernzahlen*
*Context gathered: 2026-10-01*
