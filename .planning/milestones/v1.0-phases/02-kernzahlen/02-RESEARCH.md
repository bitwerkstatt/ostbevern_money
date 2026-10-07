# Phase 2: Kernzahlen - Research

**Researched:** 2026-10-01
**Domain:** PDF-Datenextraktion (pdfplumber/polars) aus einem ProFIS+-Haushaltsplan; Konsistenzprüfung gegen dokumentierte Sollwerte
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Prüfbericht und befunde.md**
- D-01: Die Prüflogik liegt einmal in der Bibliothek (`ostbevern/pruefung.py` o. ä.). Zwei Einstiege nutzen sie: `pipeline/06_pruefen.py` (läuft in `alle.py`) schreibt `daten/pruefberichte/konsistenz.md`. pytest ruft dieselbe Logik auf, prüft per Assert und schreibt den Bericht ebenfalls (Erfolgskriterium 5).
- D-02: `daten/pruefberichte/befunde.md` ist Markdown für Menschen. Jeder Befund hat Begründung und PDF-Seite. Die Datei enthält eine **maschinenlesbare Schlüsseltabelle**, die der Code parst. Die Spalten sind sinngemäß Regel, Ebene, Code, Zeile, Jahr und erwartete Abweichung in €. Mensch und Maschine nutzen dieselbe Datei; eine zweite Datei gibt es nicht.
- D-03: `konsistenz.md` enthält je Regel eine Statuszeile (grün/rot, Anzahl geprüfter Werte). Im Detail stehen nur Abweichungen und bekannte Befunde, keine vollständige Soll/Ist-Matrix. So bleibt der Diff stabil.
- D-04: Tritt ein Befund aus `befunde.md` nicht mehr auf, ist er **veraltet, und das gilt als Fehler**. Die Datei darf keine Fehler still verdecken.
- D-05: Ein Befund deckt eine Abweichung nur ab, wenn der **Betrag passt**. Weicht die tatsächliche Differenz um mehr als 1 € von der dokumentierten ab, ist das ein neuer Fehler.

**Teststrategie**
- D-06: Die Prüfregel-Tests (Regeln 1–4, Sollwerte, Anhang-A-Startseiten) lesen die **eingecheckten CSVs** unter `daten/zwischen/` und `daten/aufbereitet/`, nicht das PDF. Dass CSV und PDF zusammenpassen, sichert ab Phase 4 die CI-Diff-Prüfung von `alle.py` (PRUEF-10).
- D-07: Die Unit-Tests für Seitenklassifikation und Planzeilen-Parser lesen **ausgewählte echte PDF-Seiten** aus `raw_data/haushalt-2026.pdf`, z. B. 62, 63, 66, 83, 86 und Fortsetzungsseiten. Der Zahlenparser wird mit reinen String-Tests geprüft.
- D-08: Kann die Extraktion eine Planzeile oder Planseite nicht lesen, **bricht sie sofort mit PDF-Seite und Zeile ab**. Beispiele: falsche Anzahl an Werten, unbekannte Zeilennummer, Text passt nicht zum Wörterbuch. Nichts wird still übersprungen. Ausnahme ist die Seitenklassifikation, siehe D-17.
- D-09: `pipeline/alle.py` führt in Phase 2 die Schritte **01 → 02 → 06** in Reihenfolge aus. Spätere Phasen hängen ihre Schritte an.

**Datentreue im Langformat**
- D-10: Beträge werden **mit dem gedruckten Vorzeichen** gespeichert. Aufwendungen sind positiv (Z. 17), der Minderaufwand ist negativ (GEP Z. 27 = −600.000), Ergebnisse tragen ihr Vorzeichen. Der gedruckte **Operator** (`+`, `-`, `=`, `+/-`) steht in einer eigenen Spalte. Die Zeilenformeln der Prüfregeln kennen die Rechenrichtung. — Reversibility: costly.
- D-11: Zeilen, die das PDF nicht druckt, kommen **nicht in die CSV**. Jede CSV-Zeile entspricht einer gedruckten Zeile mit `pdf_seite`. Prüfungen und spätere Schritte behandeln Fehlendes als 0. Gedruckte Nullzeilen, z. B. „09 Bestandsveränderungen 0 0 0“, werden normal übernommen.
- D-12: `zeile_name` und `zeile_kanonisch` kommen aus einem **festen Wörterbuch im Code**. Es ist je Plantyp (Gesamtergebnisplan, Teilergebnisplan, Gesamtfinanzplan, Teilfinanzplan) nach Zeilennummer geschlüsselt und gilt als fachliche Regel (Phase 1 D-07). Der gelesene PDF-Text wird leerzeichenunabhängig dagegen geprüft, denn pdfplumber liefert z. B. „ZuwendungenundallgemeineUmlagen“. Passt er nicht, bricht die Extraktion nach D-08 ab.

**Produktgruppen-Ebene**
- D-13: Die 8 gedruckten PG (0106, 0110, 0112, 0301, 0501, 0602, 0902, 1201) haben eigene Teilpläne, z. B. S. 83. Diese werden als `ebene=PG` mit `pdf_seite` extrahiert. **Regel 2 prüft zweistufig:** Σ Produkte = PG und Σ PG = PB, je Zeile und Jahr.
- D-14: **Synthetische PG** (eine PG mit nur einem Produkt, nicht gedruckt) erscheinen in `hierarchie.csv` mit `synthetisch=true`. Der Code besteht aus den ersten 4 Ziffern des Produktcodes, der Name ist der Produktname. Sie **bekommen auch Planzeilen** in `ergebnisplan.csv` und `finanzplan.csv`. Das sind Kopien der Produktzeilen mit `ebene=PG`, der bool-Spalte `synthetisch=true` und der `pdf_seite` der Produktseite. Gedruckte Zeilen tragen `synthetisch=false`. Regel 2 behandelt die synthetischen PG wie gedruckte (trivial grün), Regel 3 summiert nur PB.
- D-15: Die Namen in `hierarchie.csv` stammen aus den **Kopfzeilen der Planseiten**, z. B. „Produkt 010601 Zentrale Dienste für Organisationseinheiten im / Hause und Dritter“. Mehrzeilige Namen werden zusammengeführt. Die Kopfzeilen haben normale Leerzeichen.

**Seitenklassifikation**
- D-16: `seiten.csv` enthält **alle 400 Seiten**. Außerhalb der Gesamt- und Teilpläne ist `typ` der Kapitelname aus `[seitenbereiche]` der Jahrgangsdatei, z. B. `vorbericht`, `stellenplan`, `querschnitte`. PB, PG und Produkt bleiben dort leer.
- D-17: Im Teilplanbereich gilt ein **feines Typ-Vokabular**, sinngemäß `produktinformationen`, `grundzahlen`, `teilergebnisplan`, `erlaeuterungen`, `teilfinanzplan`, `investitionen_pb`, `investitionen_produkt` usw. Phase 3 braucht Grundzahlen und Erläuterungen ohnehin. Fortsetzungsseiten erben den Kontext. Eine Seite im Teilplanbereich, die keinem Muster entspricht, bekommt `typ=unbekannt`. Sie wird in `konsistenz.md` gelistet, und der Lauf geht weiter. Das ist eine bewusste Ausnahme zu D-08. Die Plan-Extraktion bricht aber weiterhin ab, wenn eine erwartete Planseite fehlt oder nicht lesbar ist.

**Sollwerte**
- D-18: Phase 2 füllt `pipeline/jahrgaenge/2026_sollwerte.toml` mit **Anhang B, wie er dokumentiert ist**: B.1 vollständig (alle Tabellenzeilen, 6 Jahre), B.2 (Werte 2026), B.3 je PB (ordentliche Erträge, ordentliche Aufwendungen, TP Z. 29), Satzung § 1 (vorhanden). Fehlende Zeilen von S. 62/63 werden nicht zusätzlich abgeschrieben. Die Regeln 1–3 sichern den Rest über Konsistenz.
- D-19: Das Anhang-A-Produktverzeichnis (Codes und Startseiten von PB, gedruckten PG und Produkten) steht ebenfalls in `2026_sollwerte.toml`. Es dient als Sollwert für den Startseiten-Test und nicht als Steuerung der Extraktion.
- D-20: Der Executor überträgt die Sollwerte aus `discussion/SPEZIFIKATION.md` Anhang A/B. Eine zusätzliche menschliche Gegenprüfung gegen das PDF ist nicht vorgesehen. Tippfehler fallen über die Konsistenzregeln auf.

**CSV-Konventionen**
- D-21: Alle CSVs unter `daten/zwischen/` und `daten/aufbereitet/` folgen denselben Regeln: UTF-8 ohne BOM, Komma, LF, Kopfzeile; Codes/Zeilennummern als Strings mit führender Null; bool als `true`/`false`, Beträge als int; feste Spaltenreihenfolge und deterministische Sortierung. — Reversibility: costly.
- D-22: Die Schemas (Spalten und polars-Typen je Datei) stehen zentral in einem Bibliotheksmodul. Schreiben und Lesen laufen darüber, auch in den Tests.

### Claude's Discretion
- Genaue Spaltenliste von `ergebnisplan.csv` und `finanzplan.csv` über Spez. 4.2 hinaus, z. B. Name der Operator-Spalte und Position von `synthetisch`, `ist_summe` und `zeile_kanonisch`
- Konkrete Schlüssel für `zeile_kanonisch` und das genaue Typ-Vokabular in `seiten.csv`
- Spaltenzuordnung über x-Koordinaten (bevorzugt nach Spez. 5.4), Behandlung mehrzeiliger Kopfzeilen und Fortsetzung von Teilplänen über Seiten hinweg
- Modulaufteilung in `ostbevern/` (z. B. `zahlen.py`, `pdf.py`, `seiten.py`, `plaene.py`, `pruefung.py`, `schema.py`)
- Schreibweise der Schlüsseltabelle in `befunde.md` und Aufbau von `konsistenz.md` im Rahmen von D-02/D-03
- Ob neue Kopfzeilen-Muster (z. B. `Produktgruppe`) nötig sind; sie kommen in `2026.toml` — **Research finding: ja, siehe Common Pitfalls/Code Examples unten, bereits mit echter PDF-Seite verifiziert.**
- Wie pytest und `06_pruefen.py` beim Schreiben des Berichts dieselbe Ausgabe erzeugen, ohne sich zu stören

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXTR-01 | Zahlenparser: deutsches Format, Minus, „–“ als „kein Wert“, angeklebte Beträge, `C` als Eurozeichen (Unit-Tests) | Verified real occurrences of `–` (Grundzahlen/Investitionen pages), ASCII minus in plan tables, `C` as currency marker on every plan page header (`in C`). See Code Examples/Pitfalls. |
| EXTR-02 | `seiten.csv` (Seite, Typ, PB, PG, Produkt); Fortsetzungsseiten erben Kontext; Anhang-A-Startseiten stimmen | Verified header patterns (`Produktbereich`, `Produkt`, missing `Produktgruppe`), verified Anhang-A startpages against real PDF pages (66, 83, 84, 150, 280), verified `Fortsetzung folgt...` marker. |
| EXTR-03 | `hierarchie.csv`: 15 PB, alle PG (`synthetisch`), 63 Produkte mit Namen aus Produktseite | Computed PG counts from Anhang A (8 printed + 40 synthetic = 48 PG) as a cross-check target; verified multi-line product/PG header wrapping. |
| EXTR-04 | Gesamt-/Teilergebnispläne im Langformat, `zeile`/`zeile_kanonisch`/`ist_summe`/`pdf_seite`, x-Koordinaten, fehlende Zeilen = 0 | Verified exact word-level layout of pages 62, 66, 83, 86 incl. the **critical PB/PG row-18–26 omission finding**. |
| EXTR-05 | Gesamt-/Teilfinanzpläne inkl. VE-Spalte in `finanzplan.csv` | Verified page 63/66/83 Finanzplan layout, duplicate „2026“ header text (Ansatz vs. VE) requiring x-coordinate-based column mapping. |
| PRUEF-01 | Zeilenformeln je Plan (Regel 1) | Verified formula texts printed in PDF (e.g. `Z.26+27-28`) and the row-omission pitfall that breaks a literal implementation. |
| PRUEF-02 | Produkt → PG → PB Summen (Regel 2) | Verified PG grouping counts and the synthetic-PG pass-through (D-14) against real Anhang-A data. |
| PRUEF-03 | 15 PB → Gesamt (Regel 3) | Verified against B.3 Anhang-B row for PB 01 (`-2.719.206`) matching page 66 exactly. |
| PRUEF-04 | Anhang-B-Sollwerte (B.1–B.3, Satzung §1) | Verified every B.1/B.2/B.3 figure quoted in CONTEXT.md against the real PDF pages 62/63/66. |
| PRUEF-09 | pytest erzeugt `konsistenz.md`; Abweichungen > 1 € ohne `befunde.md`-Eintrag scheitern | See Validation Architecture section; existing pytest config in `pipeline/pyproject.toml` reused as-is. |
</phase_requirements>

## Summary

Phase 2 is a pure data-extraction/validation phase with **no new external dependencies** — it builds entirely on the already-approved `pdfplumber`/`polars`/`typer`/`pytest` stack from Phase 1. The research for this phase is therefore not a library/ecosystem question but a **domain-verification question**: does the real PDF actually look the way `discussion/SPEZIFIKATION.md` and `02-CONTEXT.md` describe it? To answer that, this research opened `raw_data/haushalt-2026.pdf` directly with `pdfplumber` (already installed in `pipeline/.venv`) and dumped word-level layouts of the canonical sample pages named in D-07 (62, 63, 66, 83, 84–86) plus several additional Teilergebnisplan/Teilfinanzplan start pages (145–146, 150, 192–193, 278–280) to confirm the page-layout assumptions hold consistently, not just for one example.

The single most important finding, verified across four independent PB/PG samples (pages 66, 83, 145, 150), is that **PB-level and PG-level Teilergebnispläne never print rows 18–26** (Ordentliches Ergebnis, Finanzergebnis, Jahresergebnis) even when their computed value is non-zero — they jump straight from row 17 to row 27. Yet the printed formula for row 29 (`ErgebnismitinnerenVerrechnungen(Z.26+27-28)`) still references row 26. A naive implementation of D-11's "fehlende Zeilen = 0" rule for this specific row breaks Prüfregel 1 by roughly the full ordinary-result amount (millions of €, not a 1 €-class deviation) for every PB and printed PG. The planner must design the row-29 formula check to walk the implied chain (`Z18 = Z10 − Z17`, then `Z22`, then `Z26`) rather than look up a literal CSV row — see Common Pitfall 1 below. The second major finding, verified across five independent PB/PG start pages, is that **Teilergebnisplan and Teilfinanzplan always share a single physical PDF page** at PB/PG/Produkt level — `seiten.csv`'s one-`typ`-per-page model cannot represent this; the plan-extraction step must scan a page's own word stream for both section headers rather than trust a 1:1 page→plantyp mapping from `seiten.csv`.

A third concrete, previously-undecided finding (flagged as "Claude's Discretion" in CONTEXT.md) is now resolved empirically: a `Produktgruppe`-header regex **is** needed in `2026.toml` (format `Produktgruppe 0106 Zentrale Dienste`, confirmed on pages 83 and 150) since the current config only defines `produktbereich` and `produkt` patterns.

**Primary recommendation:** Reuse the Phase 1 module/config pattern exactly (dünne typer-Skripte, Logik in `ostbevern/`, Jahrgangswerte nur in TOML via `lade_jahrgang`/`lade_sollwerte`); split the new library into `zahlen.py` (reines String-Parsing, keine PDF-Abhängigkeit), `pdf.py` (pdfplumber-Wrapper, liefert Wörter mit Koordinaten), `seiten.py` (Schritt 01), `plaene.py` (Schritt 02, inkl. Zeilen-Wörterbuch), `pruefung.py` (Schritt 06, D-01); add the `Produktgruppe` header pattern and a `pg` kopfzeile key to `2026.toml`; and build Regel 1's row-29/31-equivalent checks around a formula-chain evaluator, not literal row lookups.

## Architectural Responsibility Map

This is a single-tier offline batch pipeline (no browser/API/CDN tiers apply). The relevant "tiers" are pipeline stages:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PDF-Worterkennung mit Koordinaten | `ostbevern/pdf.py` (pdfplumber-Wrapper) | — | Einzige Stelle, die `pdfplumber` importiert; Isolation erleichtert Mocking in Tests, die eigene Fixtures statt des PDFs nutzen |
| Zahlen-/Operator-Parsing (Strings → int/Operator) | `ostbevern/zahlen.py` | — | Reines String-Parsing ohne PDF-Abhängigkeit (D-07: Unit-Tests sind reine String-Tests) |
| Seitenklassifikation (Schritt 01) | `ostbevern/seiten.py` | `ostbevern/pdf.py` | Liest Kopfzeilen je Seite, kennt `[seitenbereiche]`/`[kopfzeilen]` aus der Jahrgangsdatei |
| Planzeilen-Extraktion (Schritt 02) | `ostbevern/plaene.py` | `ostbevern/pdf.py`, `ostbevern/zahlen.py` | Enthält das Zeilen-Wörterbuch (D-12) und die x-Koordinaten-Spaltenzuordnung (Spez. 5.4) |
| Konsistenzprüfung + Berichte (Schritt 06) | `ostbevern/pruefung.py` | `ostbevern/schema.py` | Einmal implementiert, zweimal aufgerufen (D-01); liest ausschließlich CSVs, nie das PDF (D-06) |
| CSV-Schema (Spalten, polars-Typen) | `ostbevern/schema.py` | — | Zentrale Quelle für Schreiben **und** Lesen (D-22), verhindert z. B. `"01"` → `1` |
| Jahrgangs-/Sollwert-Konfiguration | `ostbevern/konfiguration.py` (Phase 1, unverändert) | — | Bereits vorhanden; Phase 2 erweitert nur die TOML-Inhalte, nicht das Lademodul (bis auf ggf. neue validierte Schlüssel für `kopfzeilen.produktgruppe`) |
| Generierte CSV/MD-Ausgaben | `daten/zwischen/`, `daten/aufbereitet/`, `daten/pruefberichte/` | — | Eingecheckt, damit App und CI ohne Pipeline-Lauf funktionieren (Spez. 7) |

## Standard Stack

### Core (bereits in Phase 1 installiert — keine neuen Pakete)

| Library | Version (installiert) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pdfplumber | 0.11.10 [VERIFIED: `uv run python -c "import pdfplumber; print(pdfplumber.__version__)"`, this session] | Wortweise PDF-Extraktion mit Koordinaten (`extract_words()`, `extract_text()`) | Münster-Vorbild nutzt denselben Ansatz; liefert x0/top je Wort, Voraussetzung für Spez. 5.4 |
| polars | 1.44.2 [VERIFIED: `uv run python -c "import polars; print(polars.__version__)"`, this session] | CSV-Erzeugung/-Lesen im Langformat | Bereits Phase-1-Standard; `write_csv()` erzeugt BOM-frei und mit LF ohne Zusatzparameter [VERIFIED: dieser Session, siehe Code Examples] |
| typer | 0.27.2 (Pin aus `pyproject.toml`) | Dünne CLI-Einstiegspunkte `01_…`/`02_…`/`06_…` | Bereits Phase-1-Standard (`alle.py`) |
| pytest | ≥9.1.1 (dev-Gruppe) | Unit-/Konsistenztests inkl. `konsistenz.md`-Erzeugung (D-01) | Bereits Phase-1-Standard, Config in `pipeline/pyproject.toml` |

### Supporting
Keine zusätzlichen Pakete nötig. `re` (stdlib) für Kopfzeilen-/Operator-Regex, `dataclasses`/`tomllib` (stdlib) bereits in `konfiguration.py` verwendet.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pdfplumber.extract_words()` + eigene Spaltenzuordnung | `pdfplumber.extract_tables()` | Tabellenerkennung über Linien funktioniert nicht zuverlässig, da die Planseiten **keine Gitterlinien** zeichnen (reiner Fließtext mit Spaltenausrichtung); Spez. 5.4 empfiehlt explizit Koordinaten statt Tabellenerkennung |
| `re`-basiertes Zahlen-Parsing | `babel`/`locale`-Module für deutsches Zahlenformat | Unnötige neue Abhängigkeit für ein stabiles, eng begrenztes Format (Tausenderpunkt, Minus, `–`, `C`); ein kleines handgeschriebenes Modul mit Unit-Tests (EXTR-01) ist hier angemessen, kein „Hand-Roll“-Antipattern (siehe Don't Hand-Roll unten, wo es *nicht* gelistet ist) |

**Installation:** keine (`uv sync --directory pipeline` aus Phase 1 reicht).

## Package Legitimacy Audit

**Nicht anwendbar.** Phase 2 installiert keine neuen externen Pakete; alle verwendeten Bibliotheken (`pdfplumber`, `polars`, `typer`, `pytest`) wurden bereits in Phase 1 geprüft und sind in `pipeline/pyproject.toml`/`pipeline/uv.lock` gepinnt. Keine Aktion nötig.

## Architecture Patterns

### System Architecture Diagram

```
raw_data/haushalt-2026.pdf (400 Seiten, 1-basiert)
        │
        ▼
┌───────────────────────────┐
│ ostbevern/pdf.py           │  pdfplumber.open() einmal je Lauf,
│ (Wörter mit x0/top je Seite)│  liefert (text, x0, top) Tupel
└───────────┬────────────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│ Schritt 01: ostbevern/seiten.py             │  Kopfzeilen-Regex aus 2026.toml
│  → erkennt PB/PG/Produkt/Seitentyp je Seite │  (produktbereich, produktgruppe NEU,
│  → Fortsetzung erbt Kontext (D-17)          │   produkt, seitentypen, fortsetzung)
└───────────┬─────────────────────────────────┘
            │ daten/zwischen/seiten.csv
            ▼
┌───────────────────────────────────────────┐
│ Schritt 02: ostbevern/plaene.py             │  Zeilen-Wörterbuch (D-12) je Plantyp;
│  → scannt JEDE Teilplanseite nach BEIDEN    │  x-Koordinaten-Spaltenzuordnung
│    Abschnitts-Headern (Teilergebnis-        │  (Spez. 5.4); zahlen.py für Beträge
│    /Teilfinanzplan) statt 1 Typ/Seite       │  (EXTR-01)
│  → synthetische PG-Kopien (D-14)            │
└───────────┬─────────────────────────────────┘
            │ daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan}.csv
            ▼
┌───────────────────────────────────────────┐
│ Schritt 06: ostbevern/pruefung.py (D-01)    │  liest NUR CSVs (D-06), nie das PDF
│  → Regel 1 (Formeln, inkl. Formel-Kette     │  → daten/pruefberichte/konsistenz.md
│    für fehlende Zwischenzeilen 18-26)       │  → prüft gegen befunde.md (D-02, D-04, D-05)
│  → Regel 2 (Produkt→PG→PB)                  │
│  → Regel 3 (PB→Gesamt ohne TP27/28)         │
│  → Regel 4 (Anhang-B-Sollwerte)             │
└───────────┬─────────────────────────────────┘
            │
            ▼
   pytest (ruft dieselbe pruefung.py-Logik, assert statt nur Bericht)
```

### Recommended Project Structure
```
pipeline/
├── ostbevern/
│   ├── konfiguration.py   # Phase 1, unverändert (ggf. + kopfzeilen.produktgruppe)
│   ├── zahlen.py          # NEU: Zahlen-/Operator-Parser, reine Strings
│   ├── pdf.py             # NEU: pdfplumber-Wrapper (Wörter je Seite mit Koordinaten)
│   ├── seiten.py          # NEU: Schritt 01 Logik
│   ├── plaene.py          # NEU: Schritt 02 Logik + Zeilen-Wörterbuch
│   ├── pruefung.py        # NEU: Schritt 06 Logik (D-01), Formelprüfung + Berichte
│   └── schema.py          # NEU: CSV-Spalten/-Typen zentral (D-22)
├── 01_seiten_klassifizieren.py   # NEU: dünner typer-Einstieg
├── 02_plaene_extrahieren.py      # NEU: dünner typer-Einstieg
├── 06_pruefen.py                 # NEU: dünner typer-Einstieg
├── alle.py                # erweitert um 01→02→06 (D-09)
└── tests/
    ├── test_zahlen.py     # NEU: reine String-Tests (D-07)
    ├── test_seiten.py     # NEU: liest echte PDF-Seiten (D-07)
    ├── test_plaene.py     # NEU: liest echte PDF-Seiten (D-07)
    ├── test_pruefung.py   # NEU: liest eingecheckte CSVs (D-06)
    └── test_hierarchie.py # NEU: Anhang-A-Startseiten-Abgleich (liest CSVs, D-06)
```

### Pattern 1: x-Koordinaten-Spaltenzuordnung statt Text-Splitting
**What:** Spaltenköpfe (`Ergebnis`, `Ansatz`, `Ansatz`, `Planung`, `Planung`, `Planung` / `2024…2029`) werden per `page.extract_words()` einmalig je Seite gelesen; ihre `x0`-Position definiert die Spaltengrenzen. Jede Zahl auf einer Datenzeile wird anhand ihres eigenen `x0` der nächstgelegenen Kopf-Spalte zugeordnet, nicht über Zählen von Leerzeichen oder Tokens.
**When to use:** Für jede Plan-/Investitions-/Stellenplan-Tabelle (Spez. 5.4 empfiehlt dies ausdrücklich als bevorzugten Weg).
**Why (verified this session):** Der Finanzplan-Kopf enthält **zweimal** den Text „2026“ (Ansatz 2026 und VE 2026) — ein reiner Text-Abgleich der Jahreszahl ist nicht eindeutig, aber die x-Positionen sind es.
```python
# Verified this session via pdfplumber.open(...).pages[65].extract_words()
# top=538: Nr.@44 | Ein-undAuszahlungsartenin@60 | C@175 | Ergebnis@234 | Ansatz@286 | Ansatz@334 | VE@390 | Planung@428 | Planung@476 | Planung@524
# top=548: 2024@242 | 2025@290 | 2026@339 | 2026@387 | 2027@435 | 2028@483 | 2029@531
# -> sechs "Ansatz/VE"-Spalten sind nur über ihre x0-Reihenfolge (286,334,390,428,476,524)
#    eindeutig von links nach rechts den Jahren/Wertarten zuzuordnen, nicht über den Text "2026".
```

### Pattern 2: Operator-Erkennung mit robustem Regex statt Wort-Zählung
**What:** Der Operator (`+`, `-`, `=`, `+/-`) steht nicht immer als eigenes pdfplumber-„Wort“ vor der Bezeichnung — er kann an die Bezeichnung angeklebt sein, und Zeile 01 kann **ganz ohne** Operator gedruckt sein.
**When to use:** Beim Parsen jeder Planzeile, bevor der Bezeichnungstext gegen das Wörterbuch (D-12) geprüft wird.
**Verified this session (pdfplumber word dump, page 66):**
```
top=273: 09@44 | +/-Bestandsveränderungen@57 | 0@313 | ...
```
Hier ist `"+/-Bestandsveränderungen"` **ein einziges** Wort-Token (kein Leerzeichen im PDF zwischen Operator und Text) — während auf derselben Seite z. B. `11@44 | -@60 | Personalaufwendungen@68` Operator und Text getrennte Tokens sind. Zusätzlich fehlt der Operator auf **Zeile 01 im Gesamtergebnisplan** komplett:
```
# page 62: "01 SteuernundähnlicheAbgaben 19.614.808 ..."   -> kein Operatorsymbol gedruckt
# page 63 (Gesamtfinanzplan!): "01 + SteuernundähnlicheAbgaben 19.406.548 ..." -> Operator "+" IST gedruckt
```
Empfehlung: Operator-Erkennung per Regex `^(?P<op>\+/-|\+|-|=)?(?P<rest>.*)$` auf das erste Text-Token NACH der Zeilennummer anwenden (nicht nach Zusammensetzung aus mehreren Tokens), und ein fehlender Operator ist ein gültiger, kein fehlerhafter Zustand (leere Operator-Spalte).

### Pattern 3: Plan-Extraktion scannt Seiten-Abschnitte, nicht Seiten-Typen 1:1
**What:** Teilergebnisplan und Teilfinanzplan teilen sich **immer** dieselbe physische PDF-Seite auf PB-, PG- und Produktebene (siehe Common Pitfall 2). `plaene.py` muss pro klassifizierter Teilplan-Seite nach BEIDEN Abschnitts-Headern suchen und den Wortstrom an der y-Position (`top`) des jeweils nächsten Headers aufteilen, statt sich auf einen einzigen `typ`-Wert aus `seiten.csv` zu verlassen.
**When to use:** Immer bei `typ=teilergebnisplan`/`typ=teilfinanzplan`-klassifizierten Seiten im Teilplanbereich.

### Anti-Patterns to Avoid
- **Reine `extract_text()`-Verarbeitung für Planzeilen:** `extract_text()` liefert unzuverlässige Leerzeichen (z. B. mal `"+/- Bestandsveränderungen"` mit Leerzeichen auf S. 62, mal `"+/-Bestandsveränderungen"` ohne auf S. 66/83 — beide Formen verifiziert diese Session). Für Zeilennummer/Operator/Bezeichnung/Beträge immer `extract_words()` mit Koordinaten nutzen.
- **„Erste Zeile hat immer einen Operator" annehmen:** Siehe Pattern 2 — Zeile 01 im Gesamtergebnisplan hat keinen, im Gesamtfinanzplan aber doch.
- **Fehlende Zwischenzeile pauschal als 0 in Formelprüfungen einsetzen:** Siehe Common Pitfall 1 — bei PB/PG-Teilergebnisplänen ist das für die Zeilen 18–26 fachlich falsch.
- **`seiten.csv`-`typ` als 1:1-Schalter für die Plan-Extraktion verwenden:** Siehe Pattern 3/Common Pitfall 2.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV-Schreiben/-Lesen mit stabilem UTF-8/LF/kein-BOM-Format | eigene CSV-Writer-Funktion | `polars.DataFrame.write_csv()` / `polars.read_csv(schema_overrides=...)` | Bereits ohne Zusatzparameter BOM-frei und LF-terminiert [VERIFIED diese Session], `schema_overrides` erzwingt `Utf8` für Codes mit führender Null (D-21/D-22) |
| TOML-Laden/-Validieren der Jahrgangs-/Sollwertdatei | neues Lademodul | `ostbevern.konfiguration.lade_jahrgang`/`lade_sollwerte` (Phase 1) | Bereits vorhanden, validiert, getestet; Phase 2 ergänzt nur Inhalte, keine Logik |
| PDF-Tabellenerkennung über Gitterlinien | eigene Linienerkennung oder `extract_tables()` | `extract_words()` + x-Koordinaten (Pattern 1) | Die Planseiten zeichnen keine Tabellenlinien; `extract_tables()` liefert hier leere/falsche Ergebnisse |
| Deutsches Zahlenformat-Parsing über `locale.atof` | OS-`locale`-Abhängigkeit (instabil in CI) | kleines, getestetes Regex-Modul `zahlen.py` | `locale` ist plattform-/CI-abhängig und deckt die projektspezifischen Sonderfälle (`–`, angeklebte `C`) nicht automatisch ab |

**Key insight:** Die eigentliche Komplexität dieser Phase liegt nicht in „welche Bibliothek", sondern im exakten, durch echte PDF-Stichproben verifizierten Verständnis der ProFIS+-Layout-Eigenheiten (geteilte Seiten, ausgelassene Zwischenzeilen, inkonsistente Operator-Darstellung). Jede Abkürzung hier (z. B. „Formel X prüfen, Zwischenzeile fehlt also 0 einsetzen") erzeugt stille, großflächige Falschprüfungen statt eines sauberen Fehlschlags.

## Common Pitfalls

### Pitfall 1: PB-/PG-Teilergebnispläne drucken niemals die Zeilen 18–26 — auch wenn sie ungleich null sind
**What goes wrong:** Eine naive Implementierung von D-11 („fehlende Zeilen gelten als 0") lässt Prüfregel 1 für die Formel `Z29 = Z26+27-28` systematisch um Millionenbeträge danebenliegen, für praktisch jeden PB und jede gedruckte PG.
**Why it happens:** Verifiziert an vier unabhängigen Stichproben (Seite 66 PB01, Seite 83 PG0106, Seite 150 PG0301 — Header vorhanden, Seite 145/192/278 PB03/06/16), die alle identisch diesem Muster folgen: Nach Zeile 17 („= OrdentlicheAufwendungen") folgt direkt Zeile 27 („+ ErträgeausinternenLeistungsbeziehungen"), die Zeilen 18–26 fehlen komplett im Text — es ist **kein** Extraktionsfehler, sondern das tatsächliche Seitenlayout (wortweise mit `top`/`x0` verifiziert, siehe unten). Gleichzeitig referenziert die gedruckte Formel von Zeile 29 explizit „(Z.26+27-28)". Nachrechnen bestätigt, dass Z26 fachlich **nicht** 0 ist, sondern implizit `Z10 − Z17` (plus ggf. Finanzergebnis, falls dieses an dieser Ebene ungleich 0 wäre):
```
# PB 01, 2026 (verifiziert aus raw_data/haushalt-2026.pdf Seite 66):
Z10 (OrdentlicheErträge)      = 1.749.837
Z17 (OrdentlicheAufwendungen) = 4.519.223
# => Z18 = Z10 - Z17 = -2.769.386   (NICHT gedruckt)
Z27 (interne Erträge)         =    74.040
Z28 (interne Aufwendungen)    =    23.860
Z29 gedruckt                  = -2.719.206
# Formel-Kette bestätigt: -2.769.386 + 74.040 - 23.860 = -2.719.206  ✓ exakt
# Naive "fehlend=0"-Prüfung ergäbe: 0 + 74.040 - 23.860 = 50.180  ✗ (Abweichung > 2,7 Mio. €)
```
Produktebene ist **anders**: Seite 86 (Produkt 010601) druckt Zeile 18/22/26 sehr wohl (mit Wert, nicht 0) und lässt nur die tatsächlich-null Zeilen 19–21/23–25 weg — dort ist D-11 direkt anwendbar.
**How to avoid:** Die Regel-1-Prüfung für die „Ergebnis mit inneren Verrechnungen"-Zeile (TP Z. 29 bzw. Gesamt-Äquivalent) muss den Wert der Vorgänger-Summenzeile **über die Formel-Kette herleiten** (`Z18=Z10−Z17`, `Z21=Z19−Z20` [0 falls fehlend], `Z22=Z18+Z21`, `Z26=Z22+Z25` [0 falls fehlend]), statt eine evtl. nicht in der CSV vorhandene Zeile 18/22/26 als 0 zu interpretieren. Dieser Chain-Resolver gehört in `pruefung.py` und sollte über alle Ebenen (PB, PG, Produkt) hinweg denselben Code nutzen, unabhängig davon, ob die Zwischenzeilen tatsächlich als CSV-Zeilen existieren.
**Warning signs:** Prüfregel 1 scheitert bei **jedem** PB/PG mit einer Abweichung in Millionenhöhe (nicht 1-2 €) — das ist das Erkennungsmerkmal dieses spezifischen, systematischen Fehlers gegenüber einem echten Dateninkonsistenz-Befund.

### Pitfall 2: Teilergebnisplan und Teilfinanzplan teilen sich eine PDF-Seite
**What goes wrong:** `seiten.csv` kann pro Seite nur einen `typ` tragen; die Plan-Extraktion (Schritt 02) würde bei einer 1:1-Zuordnung „Seite X = Teilergebnisplan" den anschließenden Teilfinanzplan auf derselben Seite verpassen oder fälschlich dem nächsten `typ` zuordnen.
**Why it happens:** Verifiziert an **fünf** unabhängigen PB-/PG-Startseiten (66, 83, 145, 150, 192, 278 — alle identisch): Nach den Teilergebnisplan-Zeilen folgt auf derselben physischen Seite sofort `"Teilfinanzplan"` als neuer Abschnitts-Header mit eigenem Spaltenkopf, ohne Seitenumbruch. Das „Investitionen"-Kapitel beginnt dagegen zuverlässig auf einer **neuen** Seite (67, 146, 193, 279 — ebenfalls verifiziert).
**How to avoid:** Pattern 3 (oben) anwenden: `plaene.py` sucht pro als teilplan-relevant klassifizierter Seite nach allen vorhandenen Abschnitts-Headern (`Teilergebnisplan`, `Teilfinanzplan`) und verarbeitet jeden Abschnitt separat anhand seiner `top`-Position. `seiten.csv`s `typ`-Spalte kann weiterhin einen Primärtyp tragen (z. B. den ersten gefundenen Header) — Schritt 02 darf sich aber nicht ausschließlich darauf verlassen.
**Warning signs:** Fehlende oder doppelt gezählte Teilfinanzplan-Zeilen für PB/PG-Ebenen, obwohl die Seite laut `seiten.csv` korrekt klassifiziert wurde.

### Pitfall 3: `Produktgruppe`-Kopfzeile fehlt im aktuellen Muster-Satz
**What goes wrong:** `pipeline/jahrgaenge/2026.toml` definiert `kopfzeilen.produktbereich` und `kopfzeilen.produkt`, aber **kein** Muster für `Produktgruppe`. Ohne dieses Muster kann `seiten.py` gedruckte PG-Startseiten (S. 83, 150, …) nicht erkennen und sie fielen entweder auf `typ=unbekannt` (nach D-17 toleriert, aber fachlich falsch) oder würden der falschen Ebene zugeordnet.
**Why it happens:** Verifiziert auf Seite 83 (`"Produktgruppe 0106 Zentrale Dienste"`) und Seite 150 (`"Produktgruppe 0301 Schulische Einrichtungen und schülerbezogene"`, zweizeilig umgebrochen wie bei Produktnamen, D-15).
**How to avoid:** `2026.toml` um `kopfzeilen.produktgruppe = '^Produktgruppe (\d{4}) (.+)$'` ergänzen und `ostbevern/konfiguration.py`s `Kopfzeilen`-Dataclass/Validierung entsprechend erweitern (neuer Pflichtschlüssel oder optionaler Schlüssel mit Default — Planner-Entscheidung, aber muss zentral in der TOML stehen, nicht im Code, gemäß Projekt-Konvention).
**Warning signs:** Alle 8 gedruckten PG-Seiten landen in `seiten.csv` mit `typ=unbekannt` statt `teilergebnisplan`.

### Pitfall 4: „Nachrichtlich"-Zusatzzeilen (Z. 29–33) im Gesamtergebnisplan
**What goes wrong:** Seite 62 druckt nach Zeile 28 einen Abschnitt „Nachrichtlich: Verrechnung von Erträgen und Aufwendungen mit der allgemeinen Rücklage" mit eigenen Zeilen 29–33 — ohne dass diese Zeilennummern im normalen Gesamtergebnisplan-Nummernkreis (01–28) liegen oder in Anhang B.1 als Sollwert vorkommen (B.1 endet bei Zeile 28). Trifft `plaene.py`s Wörterbuch (D-12) hier keine explizite Vorkehrung, bricht die Extraktion nach D-08 mit „unbekannte Zeilennummer" ab, sobald sie Zeile 29 auf der Gesamtergebnisplan-Seite erreicht.
**Why it happens:** Verifiziert per Wort-Dump von Seite 62 (siehe Code Examples): Zeilen 29–33 sind real gedruckt, inklusive eines auffälligen Vorzeichendrehers zwischen Zeile 31 (`-6.328` für 2024) und der Summenzeile 33 (`6.328` für 2024) — Zeile 33 "Verrechnungssaldo(Z.29bis32)" hat augenscheinlich das umgekehrte Vorzeichen der Summe ihrer Bestandteile.
**How to avoid:** Das Zeilen-Wörterbuch für `gesamtergebnisplan` um die Schlüssel 29–33 (`zeile_kanonisch` z. B. `nachrichtlich_*`) erweitern, damit D-08 nicht greift — aber diese Zeilen **nicht** in Regel 1/Anhang-B-Prüfungen einbeziehen, da weder Spez. 5.5 noch Anhang B.1 sie dafür vorsehen. Der Abschnitts-Header „Nachrichtlich: …" selbst (keine Zeilennummer) muss vom Zeilen-Parser als Nicht-Datenzeile erkannt und übersprungen werden, ohne D-08 auszulösen.
**Warning signs:** `06_pruefen.py`/`alle.py` bricht beim Parsen von Seite 62 mit „unbekannte Zeilennummer 29" ab, obwohl alle Sollwert-relevanten Zeilen (01–28) korrekt sind.

## Code Examples

### Spaltenköpfe lesen und Spalten x-Koordinaten-basiert zuordnen
```python
# Source: pdfplumber 0.11.10, verifiziert in dieser Session gegen
# raw_data/haushalt-2026.pdf, Seite 66 (PB01 Teilergebnisplan + Teilfinanzplan)
import pdfplumber

with pdfplumber.open("raw_data/haushalt-2026.pdf") as pdf:
    page = pdf.pages[65]  # 0-indiziert, PDF-Seite 66
    words = page.extract_words()
    # Beobachtete Struktur je Zeile (top gerundet, x0 gerundet):
    # top=155: Nr.@44 | Ertrags-undAufwandsartenin@60 | C@179 | Ergebnis@278 | Ansatz@330 | Ansatz@378 | Planung@423 | Planung@471 | Planung@519
    # top=165:                                                 2024@286 | 2025@334 | 2026@382 | 2027@430 | 2028@478 | 2029@526
    # top=181: 02@44 | +@59 | ZuwendungenundallgemeineUmlagen@68 | 187.015@289 | 210.752@337 | 145.681@385 | 142.679@433 | 120.882@481 | 118.768@529
```

### Operator kann ohne Leerzeichen an den Text angeklebt sein (verifiziert)
```python
# Seite 66, top=273: EIN Wort-Token "+/-Bestandsveränderungen" (kein Leerzeichen im PDF)
# Seite 62, top=273 (analoge Zeile): ZWEI Wort-Token "+/-" und "Bestandsveränderungen"
import re

OPERATOR_MUSTER = re.compile(r"^(\+/-|\+|-|=)")

def trenne_operator(erstes_wort: str) -> tuple[str | None, str]:
    treffer = OPERATOR_MUSTER.match(erstes_wort)
    if treffer:
        operator = treffer.group(1)
        rest = erstes_wort[len(operator):]
        return operator, rest
    return None, erstes_wort  # z. B. Zeile 01 im Gesamtergebnisplan: kein Operator gedruckt
```

### polars erzeugt bereits BOM-freie, LF-terminierte CSVs mit erhaltenen führenden Nullen
```python
# Source: polars 1.44.2, ausgeführt in dieser Session
import polars as pl

df = pl.DataFrame(
    {"code": ["01", "0106"], "betrag": [100, -50]},
    schema={"code": pl.Utf8, "betrag": pl.Int64},
)
csv_bytes = df.write_csv().encode("utf-8")
assert not csv_bytes.startswith(b"\xef\xbb\xbf")  # kein BOM
assert b"\r\n" not in csv_bytes                    # LF, kein CRLF
# -> entspricht D-21 ohne Zusatzkonfiguration; beim Lesen schema_overrides={"code": pl.Utf8}
#    verwenden, sonst interpretiert polars "01" als Int 1.
```

## State of the Art

Nicht anwendbar im klassischen Sinn (kein sich schnell bewegendes Web-Framework). Die einzige relevante „Versionsfrage" ist, ob sich das ProFIS+-Layout zwischen Jahrgängen ändert — dafür existiert bereits die Jahrgangskonfiguration (Phase 1, D-06 bis D-09), die genau für diesen Zweck gebaut wurde.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Die Finanzergebnis-Zeilen (19–21) sind bei allen 15 PB tatsächlich 0 (d. h. Z26-Herleitung vereinfacht sich überall zu `Z10−Z17`), nicht nur bei PB01 — nur PB01/PG0106/PG0301/PB03/PB06/PB16-Startseiten wurden stichprobenhaft geprüft, nicht alle 15+8 Teilpläne einzeln | Common Pitfall 1 | Falls ein PB doch Finanzerträge/Zinsen bucht (laut B.3-Tabelle hat z. B. PB11 ein positives „Ergebnis mit inneren Verrechnungen" von 6.150 € — plausibler Kandidat für einen Ausnahmefall), muss die Formel-Kette auch Z19–21 aus der CSV lesen, falls dort doch gedruckt; der generische Chain-Resolver in Common Pitfall 1 deckt diesen Fall bereits ab, solange er alle potenziell vorhandenen Zwischenzeilen abfragt statt nur Z10/Z17 |
| A2 | Die „Nachrichtlich"-Zeilen 29–33 sollten im Zeilen-Wörterbuch aufgenommen, aber von Regel 1/Anhang-B-Prüfungen ausgeschlossen werden (Pitfall 4) | Common Pitfall 4 | Falls der Planer stattdessen entscheidet, diese Zeilen komplett zu ignorieren (Extraktion bricht nach Zeile 28 ab, ignoriert den Rest der Seite), ist das ebenfalls D-08-konform, solange der Abbruchpunkt bewusst vor Zeile 29 gesetzt wird statt erst beim Scheitern des Wörterbuch-Lookups |
| A3 | Alle 15 PB haben genau die in B.3 gelistete Struktur (Teilergebnisplan + Teilfinanzplan auf einer Seite), auch PB 02, 04, 05, 08–15 wurden nicht einzeln mit Wort-Koordinaten verifiziert, nur deren Kopfzeilen-Reihenfolge per `extract_text()` | Architecture Patterns / Pitfall 2 | Geringes Risiko, da das Muster bei allen 5 unabhängig geprüften PB/PG (01, 03, 06, 16, PG 0106, PG 0301) exakt gleich war; ein abweichender PB würde beim Testen mit echten Seiten (D-07) sofort auffallen |

**Hinweis:** Alle übrigen Werte in diesem Dokument (B.1–B.3-Zahlen, Anhang-A-Seiten, PG-Zählung) wurden gegen die echte PDF-Datei bzw. das vollständig gelesene `discussion/SPEZIFIKATION.md` geprüft und sind `[VERIFIED]`/`[CITED]`, nicht `[ASSUMED]`.

## Open Questions

1. **Wie werden die „Nachrichtlich"-Zeilen 29–33 im Gesamtergebnisplan behandelt?**
   - What we know: Sie sind real gedruckt (verifiziert), nicht Teil von Anhang B.1 oder Spez. 5.5 Regel 1, zeigen einen auffälligen Vorzeichendreher.
   - What's unclear: Ob der Planer sie als eigene `zeile_kanonisch`-Einträge mitextrahiert (empfohlen, siehe Pitfall 4) oder die Extraktion der Gesamtergebnisplan-Seite bewusst bei Zeile 28 stoppt.
   - Recommendation: Im Zeilen-Wörterbuch aufnehmen (verhindert D-08-Abbruch), aber von allen Prüfregeln ausnehmen; der Vorzeichendreher selbst ist kein Phase-2-Scope-Item (keine Sollwert-Anforderung betrifft ihn), kann aber als Kandidat für `befunde.md` vorgemerkt werden, falls eine spätere Phase diese Zeilen doch prüft.

2. **Muss `kopfzeilen.produktgruppe` ein Pflichtschlüssel in `KonfigurationsFehler`-Validierung werden, oder optional mit Default?**
   - What we know: Das Muster wird für 8 von 400 Seiten gebraucht (gedruckte PG); es existiert in der aktuellen `2026.toml` noch nicht.
   - What's unclear: Ob künftige Jahrgänge (Phase-2-Ziel: Wiederverwendbarkeit für 2027, Spez. Abschnitt 10 Frage 8) immer PG-Kopfzeilen drucken oder das Muster manchmal fehlen könnte.
   - Recommendation: Als Pflichtschlüssel behandeln wie `produktbereich`/`produkt` (gleiche Fehlerbehandlung in `konfiguration.py`), da 2026 es definitiv braucht; spätere Jahrgänge können das Muster einfach nicht matchen lassen, wenn sie keine PG drucken.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `raw_data/haushalt-2026.pdf` | Alle Extraktionsschritte, D-07-Tests | ✓ [VERIFIED: `ls -la raw_data/`, this session] | 9.116.953 Bytes, 400 Seiten (bereits in Phase 1 geprüft) | — |
| pdfplumber | Schritt 01/02, PDF-Tests | ✓ [VERIFIED: this session] | 0.11.10 | — |
| polars | Schritt 01/02/06, CSV-I/O | ✓ [VERIFIED: this session] | 1.44.2 | — |
| typer, pytest | CLI-Einstiege, Tests | ✓ (Phase 1 geprüft, `pyproject.toml`) | typer ≥0.27.2, pytest ≥9.1.1 | — |

**Missing dependencies with no fallback:** keine.
**Missing dependencies with fallback:** keine.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest ≥9.1.1 (bereits installiert, Phase 1) |
| Config file | `pipeline/pyproject.toml` `[tool.pytest.ini_options]` (`testpaths=["tests"]`, `pythonpath=["."]`) |
| Quick run command | `uv run --directory pipeline pytest tests/test_zahlen.py` (oder gezielte Datei je Task) |
| Full suite command | `uv run --directory pipeline pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXTR-01 | Zahlenparser: dt. Format, Minus, `–`, angeklebte Beträge, `C` | unit (reine Strings, D-07) | `uv run --directory pipeline pytest tests/test_zahlen.py -x` | ❌ Wave 0 |
| EXTR-02 | `seiten.csv` korrekt, Anhang-A-Startseiten stimmen | unit (echte PDF-Seiten, D-07) + CSV-Test (D-06) | `uv run --directory pipeline pytest tests/test_seiten.py tests/test_hierarchie.py -x` | ❌ Wave 0 |
| EXTR-03 | `hierarchie.csv` 15 PB/48 PG/63 Produkte korrekt | unit (CSV, D-06) | `uv run --directory pipeline pytest tests/test_hierarchie.py -x` | ❌ Wave 0 |
| EXTR-04 | `ergebnisplan.csv` Langformat korrekt | unit (echte PDF-Seiten, D-07) | `uv run --directory pipeline pytest tests/test_plaene.py -k ergebnisplan -x` | ❌ Wave 0 |
| EXTR-05 | `finanzplan.csv` inkl. VE Langformat korrekt | unit (echte PDF-Seiten, D-07) | `uv run --directory pipeline pytest tests/test_plaene.py -k finanzplan -x` | ❌ Wave 0 |
| PRUEF-01 | Zeilenformeln grün (inkl. Formel-Kette Pitfall 1) | unit (eingecheckte CSVs, D-06) | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel1 -x` | ❌ Wave 0 |
| PRUEF-02 | Produkt→PG→PB-Summen grün | unit (eingecheckte CSVs, D-06) | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel2 -x` | ❌ Wave 0 |
| PRUEF-03 | PB→Gesamt (ohne TP27/28) grün | unit (eingecheckte CSVs, D-06) | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel3 -x` | ❌ Wave 0 |
| PRUEF-04 | Anhang-B-Sollwerte getroffen | unit (eingecheckte CSVs + `2026_sollwerte.toml`, D-06) | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel4 -x` | ❌ Wave 0 |
| PRUEF-09 | `konsistenz.md` wird erzeugt, Befund-Policy (D-04/D-05) | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -k konsistenzbericht -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** gezielte `pytest`-Datei für das gerade bearbeitete Modul (siehe Tabelle oben)
- **Per wave merge:** `uv run --directory pipeline pytest` (voll)
- **Phase gate:** volle Suite grün vor `/gsd-verify-work`; zusätzlich `uv run --directory pipeline ruff check .` und `ruff format --check .` (CLAUDE.md-Konvention)

### Wave 0 Gaps
- [ ] `tests/test_zahlen.py` — deckt EXTR-01 (reine String-Tests, D-07)
- [ ] `tests/test_seiten.py` — deckt EXTR-02, liest echte PDF-Seiten (D-07), inkl. Fixtures für Seiten 62/63/66/83/84-86/150
- [ ] `tests/test_hierarchie.py` — deckt EXTR-03, Anhang-A-Startseiten-Abgleich gegen eingecheckte CSVs (D-06)
- [ ] `tests/test_plaene.py` — deckt EXTR-04/05, liest echte PDF-Seiten (D-07)
- [ ] `tests/test_pruefung.py` — deckt PRUEF-01 bis PRUEF-09, liest eingecheckte CSVs (D-06), inkl. Formel-Kette aus Pitfall 1
- [ ] Keine Framework-Installation nötig — pytest bereits vorhanden

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V1 Architecture | nein | Kein Netzwerkdienst, reine lokale Batch-Pipeline |
| V2 Authentication | nein | Kein Login, kein Benutzerkonzept |
| V3 Session Management | nein | Keine Sessions |
| V4 Access Control | nein | Einzelbenutzer-CLI, kein Mehrbenutzerzugriff |
| V5 Input Validation | ja | PDF-Inhalt und TOML-Konfiguration werden als strukturierte, aber potenziell fehlerhafte Eingabe behandelt: `lade_jahrgang`/`lade_sollwerte` validieren Schlüssel/Typen vollständig (Phase 1, bereits verifiziert), neue Extraktionslogik bricht bei unerwartetem Inhalt sofort ab statt stillschweigend falsche Werte zu erzeugen (D-08) |
| V6 Cryptography | nein | Keine Kryptographie im Scope |
| V12 Files/Resources | ja (bereits umgesetzt) | `pdf_pfad` wird als relativer Pfad erzwungen und gegen Pfad-Traversal außerhalb von `PROJEKT_WURZEL` geprüft — `[VERIFIED: pipeline/ostbevern/konfiguration.py:133-143]`: <br>`pdf_pfad_relativ = Path(pdf_pfad_roh)` … `if pdf_pfad_relativ.is_absolute(): raise KonfigurationsFehler(...)` … `if not pdf_pfad.is_relative_to(PROJEKT_WURZEL): raise KonfigurationsFehler(...)` |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Pfad-Traversal über `pdf_pfad`/Jahrgangsdatei | Tampering | Bereits umgesetzt in `konfiguration.py` (siehe oben, V12) — Phase 2 fügt keine neuen Pfad-Eingaben hinzu, nutzt dasselbe Lademodul |
| Fehlerhaftes/unerwartetes PDF-Layout führt zu stillschweigend falschen Finanzzahlen | Tampering/Repudiation (Datenintegrität) | D-08 abort-fast-Policy: unbekannte Zeilennummer/Spaltenzahl/Text-Mismatch bricht sofort mit PDF-Seite+Zeile ab, statt 0 oder einen Default einzusetzen |
| Veraltete `befunde.md`-Einträge verschleiern neue, echte Fehler | Repudiation | D-04: nicht mehr auftretender Befund gilt selbst als Fehler; D-05: Betrag muss exakt (±1 €) passen |

## Sources

### Primary (HIGH confidence)
- `raw_data/haushalt-2026.pdf` — direkt mit `pdfplumber.open()` in dieser Session geöffnet und Wort-für-Wort inspiziert (Seiten 62, 63, 66, 67, 83, 84, 85, 86, 99, 120, 125, 134, 136, 138, 140, 143, 145, 146, 150, 192, 193, 278, 279, 280) `[VERIFIED]`
- `discussion/SPEZIFIKATION.md` — vollständig gelesen (alle 813 Zeilen) `[CITED]`, insbesondere §2–5.5 und Anhang A/B
- `pipeline/ostbevern/konfiguration.py`, `pipeline/alle.py`, `pipeline/jahrgaenge/2026.toml`, `pipeline/jahrgaenge/2026_sollwerte.toml`, `pipeline/pyproject.toml`, `pipeline/tests/*.py` — vollständig gelesen `[VERIFIED]`
- pdfplumber 0.11.10 / polars 1.44.2 — Version und API-Verhalten (`extract_words()`, `read_csv(schema_overrides=...)`, `write_csv()` BOM/LF-Verhalten) in dieser Session direkt ausgeführt `[VERIFIED]`

### Secondary (MEDIUM confidence)
– keine (keine Web-Recherche nötig für diese Phase; reine Domänen-/Codebasis-Verifikation)

### Tertiary (LOW confidence)
– keine

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — keine neuen Pakete, alle Versionen in dieser Session direkt geprüft
- Architecture: HIGH — zentrale Architekturaussagen (geteilte Teilplan-Seiten, fehlende Zeilen 18–26) an mehreren unabhängigen echten PDF-Seiten verifiziert, nicht nur einer Stichprobe
- Pitfalls: HIGH — alle vier Pitfalls mit exakten Wort-/Koordinaten-Dumps aus dem echten PDF belegt und gegen Anhang-B-Zahlen nachgerechnet

**Research date:** 2026-10-01
**Valid until:** stabil, solange sich `raw_data/haushalt-2026.pdf` nicht ändert (kein Ablaufdatum im üblichen Sinn; bei Wechsel auf Haushalt 2027 vollständig neu verifizieren, da ProFIS+-Layout-Änderungen nicht ausgeschlossen sind, Spez. Abschnitt 10 Frage 8)
