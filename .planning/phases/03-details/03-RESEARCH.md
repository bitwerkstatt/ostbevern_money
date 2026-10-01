# Phase 3: Details - Research

**Researched:** 2026-10-01
**Domain:** PDF-Datenextraktion (pdfplumber-Koordinatenparsing) für Produktinformationen, Grundzahlen, Erläuterungen, Investitionen und Haushaltsquerschnitte; Erweiterung der bestehenden Prüfpipeline um Regeln 6–8
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Erläuterungsposten**
- **D-01:** Ein Posten beginnt mit einem führenden Betrag und dem Eurozeichen `C`, z. B. „66.500 C Strom, Nahwärme, …“. Der Posten bekommt `betrag` (int) und `text`. Unterbeträge im Text, etwa „(zusätzlich 55.000 C aus Rückstellungen …)“, bleiben Teil des Textes und werden **nicht** als eigene Posten gezählt. Zeilen ohne führenden Betrag kommen als Freitext ohne Betrag in den Block, z. B. Einleitung „In den Ansätzen sind u. a. enthalten:“ oder Schlusssätze „u. a. Erstattungen an die BBO …“. Mehrzeilige Postentexte werden zusammengeführt.
- **D-02:** Blöcke **ohne „zu Nr. …“** (z. B. S. 184, Sozialhilfe nach SGB XII) werden mit **leerem `zu_zeilen`** übernommen. Sie gelten als allgemeiner Hinweis zum Produkt. Varianten der Kopfzeile wie „Zu Nr.“, „zu Nr. 02 und 13“ und „Nr. 13 und Nr. 16“ werden auf eine Liste von Zeilennummern normalisiert. Die Nummern sind Strings mit führender Null (Phase 2 D-21).
- **D-03:** Erläuterungen liegen an **zwei Stellen**. Die Quelle für Prüfungen und Diffs ist `daten/aufbereitet/erlaeuterungen.csv` im Langformat, sinngemäß mit den Spalten `produkt, block, position, zu_zeilen, betrag, text, pdf_seite`. Dabei ist `betrag` bei Freitextzeilen leer, `zu_zeilen` ist eine Liste in einer Spalte (Kodierung nach Claudes Ermessen). Zusätzlich wird alles wie in Spez. 4.2 unter `erlaeuterungen` in `produkte.json` eingebettet.
- **D-04:** Die Erläuterungen werden **nur auf Plausibilität** geprüft, nicht auf Summen, denn die Posten sind ausdrücklich „u. a. enthalten“. Erstens muss jede Zeile in `zu_zeilen` im Teilergebnisplan des Produkts gedruckt sein. Zweitens darf kein einzelner Posten die Summe der bezogenen Zeilen im Ansatz 2026 übersteigen. Ein Verstoß **bricht ab** (Phase 2 D-08), mit PDF-Seite.

**Investitionen**
- **D-05:** Regel 6 prüft alle sieben Spalten: Ergebnis 2024, Ansatz 2025, Ansatz 2026, VE 2026, Planung 2027–2029. Erstens muss die Summe der Maßnahmen je Produkt die Teilfinanzplan-Zeilen Z. 23 (Einzahlungen) und Z. 30 (Auszahlungen) ergeben. Zweitens muss die Summe aller Maßnahmen die Gesamtfinanzplan-Zeilen Z. 23/30 ergeben (2026: 7.224.830 € / 12.280.484 €). Abweichungen über 1 € sind Fehler, außer sie stehen in `befunde.md`.
- **D-06:** Die PB-Investitionslisten (Seitentyp `investitionen_pb`) werden mit demselben Parser gelesen, aber **nicht ausgeliefert**. Sie sind Teil von Regel 6: Maßnahmen-IDs und Beträge je Maßnahme, Konto, Jahr und Wertart müssen mit den Produktseiten übereinstimmen. Eine Maßnahme, die nur in einer der beiden Quellen vorkommt, ist ein Fehler. Quelle für `investitionen.csv` sind weiterhin **ausschließlich die Produktseiten** (Spez. 3.8).
- **D-07:** `investitionen.csv` erhält eine Spalte `art`, abgeleitet über eine feste Zuordnung der Kontengruppen nach NKF aus dem Konto (fachliche Regel im Code, keine Jahrgangskonfiguration). Ein unbekanntes Konto bricht ab (D-08). Phase 5 nutzt `art` für den Filter auf `/investitionen` (Spez. 6.10). — **Reversibility: costly**
- **D-08:** Die gedruckten Zwischen- und Saldozeilen werden beim Parsen als Gegenprobe geprüft, aber nicht gespeichert. Kontozeilen müssen die Ein-/Auszahlungszeile ergeben, diese den Saldo der Maßnahme, und alle Maßnahmen zusammen den Saldo Investitionstätigkeit. Ein Verstoß bricht ab. Die Saldozeile „Saldo <ID>“ trennt Maßnahmen-ID und Namen sicher (Beispiel: „BGA0301014Betriebs-u.Geschäftsausst.…“ → ID `BGA0301014`). In `investitionen.csv` stehen nur Kontozeilen.

**Personennamen und Freitexte**
- **D-09:** Personennamen aus „Verantwortliche/r“ und „Sachbearbeiter/innen“ werden beim Parsen als Felder erkannt, danach **verworfen** und nie in eine Datei geschrieben, auch nicht unter `daten/`. Ein Test stellt sicher, dass `produkte.json` keine Schlüssel `verantwortlich`/`sachbearbeiter` enthält und dass in `daten/` keine der gelesenen Namen vorkommen. **Bewusste Verschärfung** gegenüber Spez. 4.2/PROJECT.md. — **Reversibility: reversible**
- **D-10:** Freitexte werden als lesbarer Fließtext gespeichert (Beschreibung, Auftragsgrundlage, Zielgruppe, Ziele, Leistungen, Erläuterungstexte). Leerzeichen werden mit `extract_words(x_tolerance=1)` wiederhergestellt. PDF-Zeilen werden mit Leerzeichen verbunden. Silbentrennung: „-“ am Zeilenende vor Kleinbuchstabe wird entfernt; vor Großbuchstabe oder „und/oder/sowie“ bleibt es stehen.
- **D-11:** Feldtypen in `produkte.json`: `leistungen` ist eine Liste (ein Eintrag je `(cid:15)`-Punkt, Folgezeilen angehängt). `beschreibung`, `auftragsgrundlage`, `zielgruppe`, `ziele` sind Strings. Mehrere Zeilen ohne Aufzählungszeichen werden mit Leerzeichen verbunden, ohne Heuristik zur Punkteaufteilung.

**Grundzahlen**
- **D-12:** `grundzahlen.csv` hat eine Spalte `hinweis` je Wert, auf das betroffene Jahr bezogen. „Stand 30.06.“ gilt nur für jahr=2025. Eine überschreibende Fußnote (z. B. „Ist-Wert 2025: Stand Ende 2025“) ersetzt ihn für dieses Produkt. Allgemeine Fußnoten stehen an allen Jahren des Produkts.
- **D-13:** Ein „–“-Wert erzeugt keine Zeile. Eine gedruckte 0 bleibt 0. Gruppenüberschriften ohne Werte (z. B. S. 265 „Nutzung Friedhofshalle“) kommen in eine Spalte `gruppe` der folgenden Zeilen und bilden keine eigene Zeile. Mehrzeilige Bezeichnungen werden zusammengeführt. Einheit „C“ wird zu `EUR`, andere Einheiten bleiben wie gedruckt. Steuer-Istwerte stehen mit Bezeichnung und Zeilenhinweis wie gedruckt, z. B. „Gewerbesteuer (Im Teilplan Zeile 01)“.

**Querschnitte und Regel 7**
- **D-14:** Querschnitte S. 291–300 werden per Koordinaten nach `daten/zwischen/querschnitte.csv` extrahiert und eingecheckt, Langformat mit sinngemäß `pb, pg, plan, kennzahl, betrag, pdf_seite`. Werte sind Ansatz 2026, GESAMTSUMME bekommt eigenen Marker. Regel 7 liest die CSV wie andere Prüfregeln. Reine Kontrollquelle, nie App-Datenquelle.
- **D-15:** Regel 7 prüft alle Spalten: 7 Ergebnisplan-Kennzahlen und 11 Finanzplan-Kennzahlen inklusive VE. Je PG (gedruckt und synthetisch) gegen eigene PG-Teilpläne; GESAMTSUMME gegen PB-Teilplan. Bekannte Abweichungen nach Phase 2 D-02/D-05-Mechanismus in `befunde.md`.

### Claude's Discretion
- Genaue Spaltenlisten und Sortierung von `erlaeuterungen.csv`, `grundzahlen.csv`, `investitionen.csv`, `ve_faelligkeiten.csv` und `querschnitte.csv` (zentrales Schema-Modul, Phase 2 D-22-Konventionen).
- Kodierung von Listen in CSV-Zellen (z. B. `zu_zeilen`).
- Typ von `grundzahlen.wert`, falls Dezimalwerte vorkommen (int-Konvention gilt für Euro-Beträge).
- Struktur von `ve_faelligkeiten.csv` (Zuordnung der Klammerwerte zu Jahren über x-Koordinaten) und ob deren Summe gegen die VE 2026 der Maßnahme geprüft wird.
- Konkretes Vokabular von `art` und die Kontengruppen-Zuordnung (D-07).
- Mapping der Querschnitt-Kennzahlen auf Planzeilen und der Name der Spalte `kennzahl`.
- Normalisierung des Bindungsgrads (`pflichtig | freiwillig | teils`); ein unbekannter Wert bricht ab.
- Umgang mit Produktinformationen über zwei Seiten (64 Seiten `produktinformationen` bei 63 Produkten) und mit Investitionsmaßnahmen, die schon auf der Teilfinanzplan-Seite beginnen (S. 153).
- Modulaufteilung in `ostbevern/` (z. B. `produkte.py`, `investitionen.py`, `querschnitte.py`, `freitext.py`) und die Erweiterung von `alle.py` auf 01 → 02 → 03 → 04 → 06.
- Ausgestaltung von Regel 8 (Vollständigkeit) auf Basis von `produkte.json`, `ergebnisplan.csv` und `finanzplan.csv`.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope. Not in this phase: manuelle Vorberichtstabellen, Prüfregel 5, Stellenplan, `meta.json`, App-JSON (`07_app_daten.py`), CI-Diff-Prüfung (alle Phase 4).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXTR-06 | Produktinformationen aller 63 Produkte in `produkte.json` (Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Bindungsgrad normalisiert+original, Klassifizierung, Zielgruppe, Ziele, PDF-Seiten) | Verified real page 151/280 text confirms field layout and Silbentrennungs-/Leerzeichen-Problem; `freitext.py` utility pattern recommended below |
| EXTR-07 | `grundzahlen.csv` mit Einheit, Jahr, Stichtagshinweis, Steuer-Istwerte 2022–2025 aus 160101 | Verified page 280 (Gewerbesteuer 2023 = 4.771.497 €) and page 265 (Gruppenüberschrift) confirm exact row shapes in Pitfalls 5/6 |
| EXTR-08 | Erläuterungsposten je Produkt mit Betrag, Text, Zeilenbezug | Verified page 152 (single `zu Nr.` block) and page 184 (two blocks, one without `zu Nr.`) confirm D-01–D-04 parsing rules; Pitfall 4 |
| EXTR-09 | Investitionsmaßnahmen nur aus Produktseiten in `investitionen.csv`; „(Kassenwirksamkeit)“ in `ve_faelligkeiten.csv` | Verified pages 146/147/153/154 confirm ID collision (D-08), multi-block-per-ID on PB lists, embedded investment section on teilfinanzplan page; Pitfalls 2/3/7 |
| PRUEF-06 | Investitionssummen je Produkt = Teilfinanzplan Z. 23/30; Summe aller = Gesamtfinanzplan (7.224.830 € / 12.280.484 €) | Extends existing `pruefung.py` Regel-Pattern (Planwerte, Pruefpunkt, Abgleich gegen befunde.md) — architecture documented below |
| PRUEF-07 | Querschnitte S. 291 ff. stimmen mit eigenen PG-Aggregaten überein | Verified page 291 structure (7 Ergebnisplan- + 11 Finanzplan-Kennzahlen) confirms D-15's column counts exactly |
| PRUEF-08 | Vollständigkeit: 63 Produkte mit Produktinformationen, Bindungsgrad, Teilergebnisplan, Teilfinanzplan | `hierarchie.csv`/`seiten.csv` from Phase 2 already provide the product set to validate against |
</phase_requirements>

## Summary

Phase 3 is a pure extension of the existing `pipeline/ostbevern/` codebase — it introduces **no new external dependencies**. `pdfplumber` 0.11.10, `polars` 1.44.2, `typer` 0.27.2 and `pytest` 9.1.1 are already locked in `pipeline/uv.lock` from Phase 1/2 and were confirmed importable this session. The implementation work is almost entirely new thin parser modules (`produkte.py`, `investitionen.py`, `querschnitte.py`, a shared `freitext.py` utility) that call into already-built, already-tested infrastructure: `ostbevern.pdf.PdfDokument` for word-coordinate access, `ostbevern.zahlen` for German number parsing, `ostbevern.zeilen.normalisiere_bezeichnung` for label matching, and `ostbevern.schema` for CSV I/O. `pruefung.py` gets three new rule functions following the exact `_pruefe_regelN` pattern already used for Regeln 1–4.

This session verified the phase's technical claims directly against the source PDF (`raw_data/haushalt-2026.pdf`, pages 145–154, 184, 265, 280, 291) rather than relying on the spec description alone, and surfaced several concrete parsing hazards not fully spelled out in CONTEXT.md: (1) investment measure blocks can repeat the same ID multiple times on a single PB-level page with separate partial Saldo lines (page 146, `AIB00001` twice); (2) the Investitionsmaßnahmen table can start mid-page directly after a Teilfinanzplan block on a page classified `typ=teilfinanzplan` in `seiten.csv`, not only on dedicated `investitionen_*` pages (page 153); (3) a product page can carry two distinct Erläuterung blocks, one with no `zu Nr.` header and one with (page 184); (4) the "(Kassenwirksamkeit)" fälligkeiten row carries exactly as many parenthesized values as there are Planung-columns (3), anchored at the Planung 2027/2028/2029 x-coordinates, not at Ergebnis/Ansatz/VE.

**Primary recommendation:** extend `ostbevern/` with four new thin modules following the established `plaene.py`/`seiten.py` architecture (pure functions over `PdfDokument` + `Jahrgang`, dataclass-based `*Fehler` exceptions, fail-fast with PDF-Seite in every error message), write all new CSVs through `ostbevern.schema`'s central I/O, and resolve the two architecture-sensitive open questions below (querschnitte.py's PDF access vs. `pruefung.py`'s CSV-only contract; investitionen.py's page-scan scope) explicitly in the plan before task breakdown.

## Architectural Responsibility Map

This project has no web-tier architecture (no browser/SSR/CDN) — Phase 3 is pipeline-only. Tiers are adapted to the project's own data-flow architecture (PDF → Pipeline → `daten/` → App-JSON, per `.claude/CLAUDE.md` Architecture section).

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Produktinformationen (Felder, Bindungsgrad, Klassifizierung) | PDF-Parsing (`ostbevern/produkte.py`, neu) | Shared Utility (`ostbevern/freitext.py`, neu) | Braucht Wortkoordinaten derselben Seite wie Grundzahlen (S. 151); Freitext-Rekonstruktion ist eine eigenständige, wiederverwendbare Fähigkeit |
| Grundzahlen (inkl. Steuer-Istwerte 160101) | PDF-Parsing (`ostbevern/produkte.py`) | Schema/IO (`schema.py`) | Gleiche Seite/Tabelle wie Produktinformationen; eigene CSV-Ausgabe über das zentrale Schema |
| Erläuterungsposten | PDF-Parsing (`ostbevern/produkte.py` oder eigenes Teilmodul) | Schema/IO | Liegt direkt im Anschluss an den Teilergebnisplan (S. 152) — braucht denselben Seitenzugriff wie `plaene.lies_abschnitte`, aber eigene Block-Erkennung |
| Investitionsmaßnahmen + VE-Fälligkeiten | PDF-Parsing (`ostbevern/investitionen.py`, neu) | Schema/IO | x-Koordinaten-Parser nach dem Muster von `plaene._ordne_werte`; braucht Zugriff auf Produkt- **und** PB-Seiten für die Gegenprobe (D-06) |
| Querschnitte (Kontrollquelle) | PDF-Parsing (`ostbevern/querschnitte.py`, neu) | Schema/IO (`daten/zwischen/`, nicht `aufbereitet/`) | Reine Kontrolldatei, nie App-Datenquelle (Spez. §2); **Architekturkonflikt**, siehe Open Questions |
| Prüfregeln 6–8 | Prüfung (`pruefung.py`, erweitert) | — | Liest ausschließlich CSVs, nie das PDF (bestehendes, im Docstring festgelegtes Architekturprinzip von `pruefung.py`) |
| Freitext-Rekonstruktion (Leerzeichen, Silbentrennung, Aufzählungen) | Shared Utility (`ostbevern/freitext.py`, neu) | — | Von `produkte.py` genutzt; eigenständiges Modul vermeidet Duplikation, analog zu `zahlen.py` als reinem String-Utility-Modul |
| Datenschutzfilter (Namen verwerfen, D-09) | PDF-Parsing (`ostbevern/produkte.py`) | Test-Suite (`test_produkte.py`) | Muss als Parse-Zeit-Verhalten umgesetzt werden (Name nie in ein dict/DataFrame schreiben), nicht als nachträglicher Filter — sonst Datenschutzlücke bei künftigen Feldern |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pdfplumber | 0.11.10 [VERIFIED: `uv run python -c "import pdfplumber; print(pdfplumber.__version__)"` this session] | Wortweise PDF-Extraktion mit Koordinaten | Bereits einzige PDF-Bibliothek im Projekt (`ostbevern/pdf.py`); Phase 3 fügt keine neue Importquelle hinzu |
| polars | 1.44.2 [VERIFIED: same command] | DataFrame/CSV-IO | Bereits zentrales Schema-Modul (`schema.py`) nutzt es durchgängig |
| typer | 0.27.2 [VERIFIED: same command] | CLI-Einstiegspunkte `03_produktinfos.py`, `04_investitionen.py` | Identisches Muster wie `01_seiten_klassifizieren.py`/`02_plaene_extrahieren.py` |
| pytest | 9.1.1 [VERIFIED: same command] | Testsuite inkl. Prüfregeln | Bereits etabliert; neue Tests folgen `test_plaene.py`/`test_seiten.py`-Mustern |

### Supporting

Keine zusätzlichen Pakete nötig. `ruff` 0.16.9 [VERIFIED: `uv run ruff --version`] ist bereits als Lint/Format-Werkzeug konfiguriert (Zeilenlänge 100, `.claude/CLAUDE.md`).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `extract_words(x_tolerance=1)` für Freitext | `extract_text()` mit nachträglicher Heuristik | Verworfen — verifiziert dieser Session: `extract_text()` liefert „DieGemeindeOstbevernistTrägerder…“ ohne Leerzeichen (S. 151); eine nachträgliche Worttrennungs-Heuristik ist unzuverlässiger als die bereits in der Stichprobe erprobte `x_tolerance=1`-Lösung (CONTEXT D-10) |
| Eigenes PDF-Rendering für Quellenbelege (`pypdfium2`/`pdftoppm`) | — | Nicht Teil dieser Phase (Spez. 5.6/DATA-04 gehört zu Phase 7); nicht recherchiert |

**Installation:** keine — alle Pakete sind bereits in `pipeline/pyproject.toml`/`pipeline/uv.lock` gepinnt (`uv sync --directory pipeline` reicht).

## Package Legitimacy Audit

Nicht anwendbar — Phase 3 führt **keine neuen externen Pakete** ein. Alle Funktionalität nutzt pdfplumber/polars/typer/pytest, die bereits in `pipeline/uv.lock` gesperrt und in Phase 1 (SETUP-02) geprüft sind.

**Packages removed due to [SLOP] verdict:** keine
**Packages flagged as suspicious [SUS]:** keine

## Architecture Patterns

### System Architecture Diagram

```
raw_data/haushalt-2026.pdf
        │
        ├─ S.151 (produktinformationen+grundzahlen) ──┐
        ├─ S.152 (teilergebnisplan+Erläuterung)   ─────┼──► ostbevern/produkte.py
        ├─ S.153/154 (teilfinanzplan+investitionen) ───┼──► ostbevern/investitionen.py
        ├─ S.146-149 (investitionen_pb je PB)      ─────┤        (Gegenprobe gg. PB-Liste, D-06)
        └─ S.291-300 (querschnitte je PB)          ─────┴──► ostbevern/querschnitte.py
                                                             │
                     ┌───────────────────────────────────────┤
                     ▼                                       ▼
   daten/aufbereitet/{produkte.json,              daten/zwischen/querschnitte.csv
     grundzahlen.csv, erlaeuterungen.csv,              (Kontrollquelle, nie App-Quelle)
     investitionen.csv, ve_faelligkeiten.csv}
                     │                                       │
                     └───────────────┬───────────────────────┘
                                      ▼
                    ostbevern/pruefung.py (Regeln 6, 7, 8 neu neben 1-4)
                       liest NUR CSVs aus daten/{aufbereitet,zwischen}
                       + daten/pruefberichte/befunde.md (bekannte Abweichungen)
                                      │
                                      ▼
                    daten/pruefberichte/konsistenz.md (grün/rot je Regel)
```

### Recommended Project Structure

```
pipeline/
├── 03_produktinfos.py          # dünner typer-Einstieg → ostbevern.produkte.extrahiere_produkte
├── 04_investitionen.py         # dünner typer-Einstieg → ostbevern.investitionen.extrahiere_investitionen
├── ostbevern/
│   ├── freitext.py             # neu: extract_words-Join, Silbentrennung, (cid:15)-Split (Shared Utility)
│   ├── produkte.py             # neu: Produktinformationen + Grundzahlen + Erläuterungen → produkte.json/grundzahlen.csv/erlaeuterungen.csv
│   ├── investitionen.py        # neu: investitionen.csv + ve_faelligkeiten.csv, inkl. PB-Gegenprobe (D-06)
│   ├── querschnitte.py         # neu: querschnitte.csv (S.291-300)
│   ├── pruefung.py             # erweitert: _pruefe_regel6, _pruefe_regel7, _pruefe_regel8
│   └── schema.py               # erweitert: neue Spalten-Dicts + schreibe_*/lies_*-Paare
└── tests/
    ├── test_freitext.py        # neu
    ├── test_produkte.py        # neu
    ├── test_investitionen.py   # neu
    ├── test_querschnitte.py    # neu
    └── test_pruefung.py        # erweitert um Regeln 6-8
```

### Pattern 1: Koordinatenbasiertes Spaltenparsen wiederverwenden

**What:** Die 7-Spalten-Investitionstabelle hat exakt denselben Spaltenkopf wie der Teilfinanzplan (`jahrgang.spalten["investitionen"]` ist in `2026.toml` bereits identisch zu `finanzplan` definiert). `plaene._ordne_werte` (x-Koordinaten-Zuordnung mit Toleranz = halber Spaltenabstand) ist direkt wiederverwendbar oder als Vorlage zu kopieren.
**When to use:** Jede Zeile der Investitionsmaßnahmen-Tabelle (Kontozeilen) und die „(Kassenwirksamkeit)“-Zeile (nur 3 der 7 Spalten belegt).
**Example (verified gegen S. 153, diese Session gelesen):**
```
785111Auszahl.f.d.Abwickl.Hochbaumaßnah- 5.224 1.885.000 2.000.000 2.000.000 2.000.000 0 0
men
(Kassenwirksamkeit) (2.000.000) – –
```
Quelle: `raw_data/haushalt-2026.pdf` S. 153, `extract_text()` dieser Session gelesen. Die Konto-Zeile belegt alle 7 Spalten (Ergebnis2024=5.224 … Planung2029=0); die Kassenwirksamkeit-Zeile belegt nur die letzten 3 (Planung2027=2.000.000, Planung2028=–, Planung2029=–) und muss über x1-Nähe zu den `jahreswoerter`-x1-Werten zugeordnet werden, nicht über Tokenreihenfolge von links.

### Pattern 2: Fail-fast mit PDF-Seite in jeder Fehlermeldung

**What:** Jede neue `*Fehler`-Klasse (`ProdukteFehler`, `InvestitionenFehler`, `QuerschnitteFehler`) folgt `PlaeneFehler`/`SeitenFehler`: `ValueError`-Subklasse, Meldung beginnt mit `f"S. {pdf_seite}: …"`.
**When to use:** Jede Unstimmigkeit, die laut CONTEXT D-04/D-08 abbrechen muss (fehlende `zu_zeilen`-Referenz, Erläuterungsposten über der Zeilensumme, unbekanntes Konto in `art`-Zuordnung, Gegenprobe-Mismatch PB vs. Produkt).
**Source:** `ostbevern/plaene.py` `PlaeneFehler`, bereits im Code dieser Session gelesen.

### Pattern 3: Zentrale Schema/IO-Erweiterung statt Ad-hoc-CSV

**What:** `schema.py` bekommt neue `dict[str, pl.PolarsDataType]`-Konstanten (`PRODUKTE_SPALTEN`-äquivalente Felder in JSON statt CSV, `GRUNDZAHLEN_SPALTEN`, `ERLAEUTERUNGEN_SPALTEN`, `INVESTITIONEN_SPALTEN`, `VE_FAELLIGKEITEN_SPALTEN`, `QUERSCHNITTE_SPALTEN`) plus `schreibe_*_csv`/`lies_*_csv`-Paare, analog zu `schreibe_plan_csv`/`lies_plan_csv`.
**When to use:** Jede neue CSV-Ausgabe dieser Phase. `produkte.json` ist kein CSV — braucht eigene JSON-Schreibfunktion (deterministische Key-Reihenfolge, UTF-8, LF, analog zum atomaren Schreibmuster in `pruefung.schreibe_konsistenzbericht`).
**Source:** `ostbevern/schema.py`, bereits im Code dieser Session gelesen.

### Pattern 4: Saldo-Zeile als zweite Lesephase für Maßnahmen-ID/Name-Trennung

**What:** Eine Investitionsmaßnahme kann nicht allein aus der Header-Zeile zuverlässig in ID und Name zerlegt werden, weil IDs sich als Präfix überschneiden (`BGA030101` vs. `BGA0301014`, verifiziert S. 153 — beide Maßnahmen existieren im selben Produkt). Die Saldo-Zeile am Blockende (`SaldoBGA0301014`) druckt die ID ohne angehängten Namenstext und ist die einzige zuverlässige Quelle; der Parser muss daher den ganzen Block puffern, bis die Saldo-Zeile gelesen ist, und erst dann ID/Name aufteilen.
**When to use:** `investitionen.py`-Blockparser.
**Source:** CONTEXT D-08 (Spezifikationsentscheidung) + direkt gegen S. 153 dieser Session verifiziert.

### Pattern 5: Mehrfach-Block-Scan statt Ein-Block-Annahme

**What:** Sowohl Erläuterungsblöcke (Pitfall 4) als auch Investitionsmaßnahmen-Header (Pitfall 2) können **mehrfach** auf derselben Seite auftreten — nicht nur nacheinander über Seitenwechsel. Der Parser darf nie `die erste gefundene Instanz` als vollständig behandeln, sondern muss wie `plaene.lies_abschnitte` die ganze Seite nach wiederholten Headern scannen.
**When to use:** `produkte.py` (Erläuterungsblöcke), `investitionen.py` (Maßnahmen-Header auf PB-Listen).
**Source:** Direkt gegen S. 184 und S. 146 dieser Session verifiziert (siehe Pitfalls 2 und 4).

### Anti-Patterns to Avoid

- **`extract_text()` für Freitextfelder nutzen:** Verifiziert S. 151 — liefert zusammengeklebten Text ohne Leerzeichen. Immer `extract_words(x_tolerance=1)` und zeilenweise Join nutzen (D-10).
- **Investitionsmaßnahmen nur auf `typ=investitionen_*`-Seiten suchen:** Verifiziert S. 153 (`typ=teilfinanzplan` laut `seiten.csv`) enthält bereits eine eingebettete `Investitionsmaßnahmen(in C)`-Tabelle nach der letzten Teilfinanzplan-Zeile. Siehe Pitfall 7/Open Question 1.
- **Eine Maßnahmen-ID als eindeutigen Schlüssel für einen einzigen Block behandeln:** Verifiziert S. 146 — `AIB00001` erscheint zweimal mit je eigenem, nur partiellem Saldo. Blöcke müssen pro Vorkommen, nicht pro ID, verarbeitet werden; `investitionen.csv` (Granularität: je Kontozeile) verträgt das ohne Konflikt.
- **Gewerbesteuer-Istwerte und reguläre Grundzahlen mit derselben Zeilenerkennung parsen, ohne den Zeilenhinweis im Bezeichnungstext zu belassen:** Verifiziert S. 280 — „Gewerbesteuer(ImTeilplanZeile01)“ ist Teil des gedruckten Labels, nicht strukturiert zu zerlegen (D-13 verlangt „wie gedruckt“).
- **`pruefung.py` direkt PDF lesen lassen, um `querschnitte.csv` zu erzeugen:** bricht die dokumentierte Invariante „liest ausschließlich CSVs, nie das PDF“ (Docstring, Zeile 5 des Moduls). Siehe Open Question 1.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deutsches Zahlenformat, „–“, angeklebte Beträge, `C`/`€` | Neuer Regex-Parser | `ostbevern.zahlen.lies_betrag` / `trenne_angeklebten_betrag` | Deckt exakt diese Grammatik bereits ab, inkl. Unicode-Minus (EXTR-01, bereits getestet) |
| Wortkoordinaten-Zugriff auf PDF-Seiten | Neuer pdfplumber-Wrapper | `ostbevern.pdf.PdfDokument.zeilen()` | Cached bereits, gruppiert nach `top`, sortiert nach `x0` — identischer Zugriffsweg wie Phase 2 |
| CSV-Schema, Spaltenreihenfolge, UTF-8/LF-Schreiben | Ad-hoc `df.write_csv()`-Aufrufe | `ostbevern.schema.schreibe_csv`/`lies_csv`-Muster | Zentrale Schema-Durchsetzung bereits Konvention (D-21/D-22 aus Phase 2) |
| Zeilennamen-Abgleich tolerant gegenüber Umbrüchen/Bindestrichen | Neue Normalisierung | `ostbevern.zeilen.normalisiere_bezeichnung` | Entfernt bereits Leerzeichen/Formelhinweis/Bindestriche konsistent |
| Konsistenzbericht-Markdown, Befunde-Abgleich | Neuer Report-Generator | `ostbevern.pruefung.rendere_konsistenzbericht` / `gleiche_befunde_ab` (durch neue `Pruefpunkt`-Instanzen aus Regel 6-8 einfach erweitert) | Hält eine einzige Quelle der Abgleichssemantik (Toleranz, Veraltete-Befunde-Erkennung) |
| Multi-Abschnitt-Seiten-Scan (mehrere Blöcke pro Seite) | Eigene State-Machine von Grund auf | Muster von `plaene.lies_abschnitte` kopieren/anpassen | Löst bereits exakt dasselbe Problem (mehrere Teilplan-Abschnitte pro Seite mit Fortsetzungslogik) |

**Key insight:** Fast alles, was Phase 3 benötigt — Zahlenparsing, Wortkoordinaten-Zugriff, CSV-Schema, Befunde-Abgleich, Markdown-Report — existiert bereits in `ostbevern/`. Die Implementierung besteht fast ausschließlich aus neuen, dünnen Parser-Modulen, die bestehende Utilities aufrufen, nicht aus neuer Infrastruktur.

## Common Pitfalls

### Pitfall 1: `extract_text()` zerstört Wortzwischenräume
**What goes wrong:** Freitext wie Produktbeschreibung wird unlesbar zusammengeklebt.
**Why it happens:** pdfplumber fügt beim reinen Textextrakt keine Leerzeichen zwischen eng stehenden Wörtern ein.
**How to avoid:** `extract_words(x_tolerance=1)` nutzen und Wörter mit Leerzeichen verbinden (D-10).
**Warning signs:** Verifiziert S. 151 dieser Session: `extract_text()` liefert „DieGemeindeOstbevernistTrägerderAmbrosius-Grundschule.“

### Pitfall 2: Maßnahmen-ID/Name-Trennung ohne Saldo-Zeile ist mehrdeutig
**What goes wrong:** Ein naiver Greedy-Split am Übergang Ziffer→Buchstabe trennt `BGA0301014Betriebs-u.Geschäftsausst....` fehlerhaft, weil auch `BGA030101` (ohne die `4`) eine gültige, tatsächlich im selben Produkt vorkommende ID ist.
**Why it happens:** IDs sind alphanumerisch ohne festes Längenschema; ein Präfix einer längeren ID kann selbst eine gültige kürzere ID sein.
**How to avoid:** Block puffern und erst anhand der Fußzeile `Saldo<ID>` (ohne angeklebten Namenstext) die exakte ID bestimmen (D-08, Pattern 4).
**Warning signs:** Verifiziert S. 153 dieser Session: `BGA030101Betriebs-undGeschäftsausstattung` und `BGA0301014Betriebs-u.Geschäftsausst.f.dieBauunterhalt.` stehen als zwei separate Blöcke auf derselben Seite.

### Pitfall 3: „(Kassenwirksamkeit)“-Zeile ist an den letzten 3 Spalten verankert, nicht an den ersten
**What goes wrong:** Eine Position-von-links-Zuordnung weist die Werte den falschen Jahren (Ergebnis/Ansatz statt Planung) zu.
**Why it happens:** Die Zeile druckt nur 3 Klammerwerte für 3 der 7 Spalten (typischerweise die VE-Fälligkeiten der Folgejahre); die anderen 4 Spalten bleiben leer, nicht nullgefüllt-von-links.
**How to avoid:** x-Koordinaten-Zuordnung wie `plaene._ordne_werte` nutzen, nie Tokenindex.
**Warning signs:** Verifiziert S. 146/147/153 dieser Session: `(Kassenwirksamkeit) (1.000.000) (1.000.000) –` (S. 147, Maßnahme AIBH005: Planung2027=1.000.000, Planung2028=1.000.000, Planung2029=0) und `(Kassenwirksamkeit) (2.000.000) – –` (S. 146/153, Maßnahme AIB00001: Planung2027=2.000.000, Planung2028=0, Planung2029=0) — die Werte entsprechen exakt den gedruckten Planung-Spaltenwerten der zugehörigen Kontozeile.

### Pitfall 4: Mehrere Erläuterungsblöcke pro Seite, nicht alle mit „zu Nr.“
**What goes wrong:** Ein Parser, der nach dem ersten `Erläuterung`-Treffer aufhört, verliert nachfolgende `zu Nr.`-Blöcke auf derselben Seite.
**Why it happens:** Das PDF druckt pro Teilergebnisplan beliebig viele Erläuterungsblöcke hintereinander; nicht jeder hat eine `zu Nr.`-Kopfzeile.
**How to avoid:** Ganze Seite nach wiederholten Block-Startmustern scannen (Pattern 5), jeden Block bis zum nächsten Block-Start oder bis `Teilfinanzplan` sammeln.
**Warning signs:** Verifiziert S. 184 dieser Session: ein generischer `Erläuterung …`-Block ohne `zu Nr.` (Freitext „Die gewährte Sozialhilfe nach SGB XII wird nicht im Haushalt der Gemeinde aufgeführt…“) gefolgt direkt von einem zweiten Block `zu Nr. 16` mit reinem Freitext-Posten „Lizenzgebühr für die Software.“ (kein führender Betrag).

### Pitfall 5: Grundzahlen-Gruppenüberschriften haben weder Einheit noch Werte
**What goes wrong:** Eine Zeilenerkennung, die auf „endet mit 4 Zahlen“ prüft, überspringt die Überschriftzeile korrekt — verwirft sie aber eventuell ganz, statt sie in die `gruppe`-Spalte der folgenden Zeilen zu übernehmen (D-13).
**Why it happens:** Die Überschrift druckt nur den Bezeichnungstext, keine Einheit, keine Jahreswerte.
**How to avoid:** Zeilen ohne Einheit/Werte als `gruppe`-Kontext für alle folgenden Zeilen bis zur nächsten Gruppenüberschrift oder Seitenende merken.
**Warning signs:** Verifiziert S. 265 dieser Session: „NutzungFriedhofshalle“ ohne Einheit/Werte, gefolgt von zwei Zeilen mit Einheit `Anz.` und 4 Jahreswerten.

### Pitfall 6: Steuer-Istwerte (160101) tragen den Zeilenverweis im Bezeichnungstext selbst
**What goes wrong:** Eine Parsing-Logik, die versucht, „(Im Teilplan Zeile 01)“ als separates strukturiertes Feld herauszulösen, widerspricht D-13 („wie gedruckt“) und erschwert künftige Jahrgänge mit abweichendem Klammertext.
**Why it happens:** Die Spezifikation verlangt den Zeilenhinweis als Teil der `bezeichnung`-Spalte, nicht als eigenes Feld.
**How to avoid:** Die komplette Bezeichnung inklusive Klammertext unverändert in `grundzahlen.bezeichnung` übernehmen.
**Warning signs:** Verifiziert S. 280 dieser Session: Gewerbesteuer 2023 = 4.771.497 € [VERIFIED: S. 280, `extract_text()` dieser Session, Zeile „Gewerbesteuer(ImTeilplanZeile01) C 9.737.018 4.771.497 8.418.043 7.853.736“] — stimmt exakt mit dem in CONTEXT.md genannten Sollwert überein.

### Pitfall 7: Investitionsmaßnahmen können auf einer `typ=teilfinanzplan`-Seite beginnen
**What goes wrong:** Ein Parser, der Investitionsdaten ausschließlich von `seiten.csv`-Zeilen mit `typ∈{investitionen_produkt,investitionen_pb}` liest, verpasst Maßnahmen, die direkt im Anschluss an den letzten Teilfinanzplan-Wert auf derselben, als `teilfinanzplan` klassifizierten Seite gedruckt sind.
**Why it happens:** Die Seitenklassifikation (Phase 2, `seiten.py`) bestimmt den `typ` einer Seite ausschließlich über die **erste** Inhaltszeile; folgt später auf derselben Seite ein weiterer Abschnitt mit eigenem Titel („Investitionsmaßnahmen(in C)“), bleibt der Seiten-`typ` unverändert.
**How to avoid:** `investitionen.py` darf sich nicht auf `seiten.csv`-Filterung allein verlassen; es muss — analog zu `plaene.lies_abschnitte` — die Zeilen jeder Teilfinanzplan- **und** jeder Investitionen-klassifizierten Seite nach dem Submuster `Investitionsmaßnahmen(inC)` durchsuchen.
**Warning signs:** Verifiziert S. 153 dieser Session: `seiten.csv` klassifiziert S. 153 als `teilfinanzplan,03,0301,030101` (bestätigt per `grep` dieser Session), dennoch druckt dieselbe Seite nach der letzten Teilfinanzplan-Zeile `SaldoausInvestitionstätigkeit -13.258 …` sofort `Investitionsmaßnahmen(inC)` mit der ersten Maßnahme `AIB00001`.

### Pitfall 8: Eine Maßnahmen-ID kann auf einer PB-Liste mehrfach als eigener Block erscheinen
**What goes wrong:** Ein Parser, der Blöcke nach ID dedupliziert oder zusammenführt, verliert Kontozeilen oder erzeugt einen falschen, nicht nachvollziehbaren Gesamtsaldo.
**Why it happens:** Die PB-Investitionsliste druckt Einzahlungs- und Auszahlungsseite derselben Maßnahme teils als zwei separate, nicht benachbarte Header-Blöcke mit je eigener, nur partieller Saldo-Zeile.
**How to avoid:** Jeden Header-Treffer als neuen Block öffnen (nicht nach ID mergen); `investitionen.csv` ist ohnehin auf Kontozeilen-Granularität (`produkt, massnahme_id, konto, …`) angelegt und verträgt mehrere Zeilen derselben ID konfliktfrei.
**Warning signs:** Verifiziert S. 146 dieser Session: `AIB00001BaumaßnahmenanderAmbrosius-Grundschule` erscheint zweimal — einmal mit Konto `785111` (Auszahlung, eigener Saldo `-5.224…`), einmal mit Konto `681011` (Einzahlung, eigener Saldo `0, 467.000, 467.000…`).

## Code Examples

### PDF-Wortzugriff für Freitext (Muster aus D-10, gegen S. 151 verifiziert)
```python
# Quelle: ostbevern/pdf.py (bereits im Repo, diese Session gelesen) — Muster für freitext.py
from ostbevern.pdf import PdfDokument

with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
    zeilen = dokument.zeilen(151)
    # zeilen[i].text verbindet Wörter mit Leerzeichen (echte Lücken, z. B. Kopfzeilen)
    # zeilen[i].text_ohne_leerzeichen entspricht extract_text()-Verhalten (keine Lücken)
    # Für Fließtext: eigenes Freitext-Join über zeilen[i].woerter mit " ".join(w.text for w in ...)
```

### Zahlenparsing wiederverwenden (bereits getestet, EXTR-01)
```python
# Quelle: ostbevern/zahlen.py (bereits im Repo, diese Session gelesen)
from ostbevern.zahlen import lies_betrag, trenne_angeklebten_betrag

betrag = lies_betrag("4.771.497")       # -> 4771497
betrag_leer = lies_betrag("–")          # -> None (kein Wert, D-13)
rest, betrag_text = trenne_angeklebten_betrag("über800EUR123.000")  # angeklebter Betrag
```

### Zeilenformel-Prüfmuster für neue Regeln (Vorlage aus Regel 1/3)
```python
# Quelle: ostbevern/pruefung.py _pruefe_regel3 (bereits im Repo, diese Session gelesen)
# Regel 6/7/8 folgen demselben Pruefpunkt/Regelergebnis-Rückgabemuster:
@dataclass(frozen=True)
class Pruefpunkt:
    regel: int
    plan: str
    ebene: str
    code: str
    zeile: str
    jahr: int
    wertart: str
    soll: int
    ist: int
    pdf_seite: int | None
    # .abweichung = ist - soll; TOLERANZ_EURO = 1; Abgleich via gleiche_befunde_ab()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| — | — | — | Keine Technologiewechsel relevant für diese Phase — reine Fortsetzung des in Phase 1/2 etablierten Stacks |

**Deprecated/outdated:** Keine Funde.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `produkte.py` sollte Produktinformationen, Grundzahlen und Erläuterungen gemeinsam verarbeiten (ein Modul statt drei), weil sie auf denselben zwei Seiten (151/152) liegen | Architecture Patterns, Recommended Project Structure | Gering — reine Organisationsentscheidung, von CONTEXT.md Claude's Discretion ausdrücklich freigegeben; falsch gewählt kostet nur Refactoring, keine Datenqualität |
| A2 | Querschnitte-Extraktion sollte als eigener PDF-lesender Aufruf vor `pruefung.pruefe_alles` laufen (z. B. im `06_pruefen.py`-Entrypoint, nicht in `pruefung.py` selbst), um die „liest nie das PDF“-Invariante von `pruefung.py` zu erhalten | Open Questions 1 | Mittel — falsch gelöst, verletzt die Architektur-Invariante stillschweigend oder erzwingt einen Doppel-Lauf; sollte im Plan explizit entschieden werden |
| A3 | Die drei Klammerwerte der „(Kassenwirksamkeit)“-Zeile entsprechen immer den Planung 2027/2028/2029-Spalten (nie Ergebnis/Ansatz/VE) | Pitfall 3 | Mittel — wenn in anderen Fällen (z. B. bei Maßnahmen mit VE, aber ohne Ansatz 2026) die Position abweicht, muss die x-Koordinaten-Zuordnung trotzdem korrekt bleiben; nur an 3 Beispielen verifiziert (S. 146/147/153), nicht an allen 12 „(Kassenwirksamkeit)“-Zeilen im PDF |
| A4 | Modul-/Dateinamen `produkte.py`, `investitionen.py`, `querschnitte.py`, `freitext.py` sind sinnvolle Wahl | Recommended Project Structure | Gering — von CONTEXT.md als Beispiel vorgeschlagen (Claude's Discretion), Namenskonvention konsistent mit bestehenden Modulen |

**Wenn diese Tabelle leer wäre:** Alle Claims wären verifiziert oder zitiert — ist hier nicht der Fall, A1-A4 benötigen Bestätigung im Plan oder bei Diskussion.

## Open Questions

1. **Wie löst `querschnitte.py` den Konflikt mit `pruefung.py`'s "liest nie das PDF"-Invariante?**
   - What we know: `pruefung.py`'s Docstring (Zeile 5, diese Session gelesen) sagt explizit „Dieses Modul liest ausschließlich CSVs, nie das PDF“. `querschnitte.csv` muss aber aus dem PDF extrahiert werden (S. 291-300), und CONTEXT.md listet dafür keinen eigenen nummerierten Pipeline-Schritt (Spez. 5.2 Ablauf kennt keinen `05_querschnitte.py`; der `alle.py`-Kettenhinweis aus CONTEXT.md lautet ausdrücklich „01 → 02 → 03 → 04 → 06“, ohne neue Nummer).
   - What's unclear: Ob die Extraktion (a) als eigener, PDF-lesender Aufruf am Anfang von `06_pruefen.py`'s typer-Entrypoint erfolgt (vor `pruefung.pruefe_alles`, das CSV-only bleibt), oder (b) als Unterschritt innerhalb von `03_produktinfos.py`/`04_investitionen.py` versteckt wird, obwohl inhaltlich unabhängig, oder (c) die Invariante bewusst für Regel 7 aufgeweicht wird.
   - Recommendation: Option (a) — `querschnitte.extrahiere_querschnitte(jahrgang)` als eigener PDF-lesender Aufruf in `06_pruefen.py` **vor** `pruefung.pruefe_alles(jahr)`, analog zu wie `alle.py`'s `main()` bereits Schritt 01 (PDF) und Schritt 06 (CSV) im selben Entrypoint, aber als getrennte Funktionsaufrufe, kombiniert. `pruefung.py` selbst bleibt CSV-only; nur sein aufrufender Entrypoint-Code bekommt einen zusätzlichen PDF-lesenden Schritt davor. Der Plan sollte das explizit festhalten, damit kein zukünftiger Entwickler die Invariante versehentlich bricht.

2. **Deckt eine einzelne Stichprobe (12 „(Kassenwirksamkeit)“-Zeilen laut CONTEXT.md) alle x-Koordinaten-Varianten ab?**
   - What we know: Alle 3 dieser Session geprüften Beispiele (S. 146, 147, 153) zeigen Klammerwerte exakt an den letzten 3 (Planung-)Spalten.
   - What's unclear: Ob eine Maßnahme mit VE, aber ohne Planungs-Fortsetzung in 2029 (z. B. VE läuft nur über 2027) eine andere Spaltenbelegung zeigt, die die x-Koordinaten-Toleranz aus `plaene._ordne_werte` (halber Spaltenabstand) an ihre Grenzen bringt.
   - Recommendation: Vor Implementierung alle 12 „(Kassenwirksamkeit)“-Zeilen im PDF per Koordinaten-Dump prüfen (ein kleines Scratch-Skript wie das in dieser Session verwendete reicht); falls Variationen auftreten, `ve_faelligkeiten.csv`-Struktur entsprechend generalisieren (Claude's Discretion laut CONTEXT.md ohnehin offen).

3. **Produktinformationen über zwei Seiten (64 Seiten bei 63 Produkten, laut CONTEXT.md Discretion-Punkt) — welches Produkt hat die zusätzliche Seite?**
   - What we know: CONTEXT.md nennt die Diskrepanz (64 `produktinformationen`-Seiten für 63 Produkte) als offenen Diskretionspunkt, aber nicht, welches Produkt betroffen ist.
   - What's unclear: Ob es sich um eine echte zweiseitige Produktinformationen-Seite handelt (z. B. langer Leistungskatalog) oder um einen Klassifikationsartefakt aus Phase 2.
   - Recommendation: `grep ",produktinformationen," daten/zwischen/seiten.csv | wc -l` und Gruppierung nach `produkt`-Spalte zeigt das betroffene Produkt eindeutig; sollte als erster Planungsschritt (Wave 0 oder früher Task) geklärt werden, bevor `produkte.py` die „eine Seite pro Produkt“-Annahme hart codiert.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pdfplumber | Alle PDF-Parsing-Module dieser Phase | ✓ [VERIFIED diese Session] | 0.11.10 | — |
| polars | CSV/Schema-IO | ✓ [VERIFIED diese Session] | 1.44.2 | — |
| typer | CLI-Einstiegspunkte 03/04 | ✓ [VERIFIED diese Session] | 0.27.2 | — |
| pytest | Prüfregeln + neue Tests | ✓ [VERIFIED diese Session] | 9.1.1 | — |
| ruff | Lint/Format | ✓ [VERIFIED diese Session] | 0.16.9 | — |
| uv | Projekt-/Abhängigkeitsverwaltung | ✓ [VERIFIED diese Session] | 0.9.26 | — |
| raw_data/haushalt-2026.pdf | Alle Parser | ✓ [VERIFIED diese Session, 400 Seiten gelesen] | — | — |

**Missing dependencies with no fallback:** keine.
**Missing dependencies with fallback:** keine.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED diese Session] |
| Config file | `pipeline/pyproject.toml` (bestehend aus Phase 1) |
| Quick run command | `uv run --directory pipeline pytest tests/test_produkte.py tests/test_investitionen.py tests/test_querschnitte.py -x` |
| Full suite command | `uv run --directory pipeline pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXTR-06 | Alle 63 Produkte vollständig in `produkte.json`, inkl. normalisiertem Bindungsgrad | integration (echte PDF-Seite) | `pytest tests/test_produkte.py -x` | ❌ Wave 0 |
| EXTR-06 | Keine Personennamen in `produkte.json` oder sonst unter `daten/` (D-09) | unit/integration | `pytest tests/test_produkte.py::test_keine_personennamen -x` | ❌ Wave 0 |
| EXTR-07 | `grundzahlen.csv` inkl. Steuer-Istwerte, Gewerbesteuer 2023 = 4.771.497 € | integration (S. 280) | `pytest tests/test_produkte.py::test_steuer_istwerte_160101 -x` | ❌ Wave 0 |
| EXTR-08 | Erläuterungsposten mit Betrag/Text/Zeilenbezug, inkl. Mehrfachblock-Fall (S. 184) | integration | `pytest tests/test_produkte.py::test_erlaeuterung_ohne_zu_nr -x` | ❌ Wave 0 |
| EXTR-09 | `investitionen.csv` nur aus Produktseiten; ID-Trennung über Saldo-Zeile korrekt (BGA030101 vs. BGA0301014) | integration | `pytest tests/test_investitionen.py::test_massnahme_id_trennung -x` | ❌ Wave 0 |
| EXTR-09 | „(Kassenwirksamkeit)“-Zeilen landen in `ve_faelligkeiten.csv`, nicht in Summen | unit/integration | `pytest tests/test_investitionen.py::test_kassenwirksamkeit_ausgeschlossen -x` | ❌ Wave 0 |
| PRUEF-06 | Investitionssummen je Produkt = TFP Z. 23/30; Gesamtsumme 2026 = 7.224.830 €/12.280.484 € | integration (CSV-only, wie Regel 1-4) | `pytest tests/test_pruefung.py::test_regel6 -x` | ❌ Wave 0 |
| PRUEF-07 | Querschnitte S. 291 ff. = eigene PG-Aggregate | integration | `pytest tests/test_pruefung.py::test_regel7 -x` | ❌ Wave 0 |
| PRUEF-08 | 63 Produkte vollständig mit allen Pflichtfeldern | integration | `pytest tests/test_pruefung.py::test_regel8 -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run --directory pipeline pytest tests/test_<modul>.py -x`
- **Per wave merge:** `uv run --directory pipeline pytest`
- **Phase gate:** Volle Suite grün vor `/gsd-verify-work`; zusätzlich `uv run --directory pipeline python alle.py --jahr 2026` muss `konsistenz.md` grün für Regeln 1-4, 6-8 liefern (Regel 5 bleibt Phase 4)

### Wave 0 Gaps
- [ ] `tests/test_freitext.py` — covers Silbentrennung, `(cid:15)`-Split, Leerzeichen-Rekonstruktion
- [ ] `tests/test_produkte.py` — covers EXTR-06, EXTR-07, EXTR-08, D-09-Datenschutztest
- [ ] `tests/test_investitionen.py` — covers EXTR-09, Maßnahmen-ID-Trennung, Kassenwirksamkeit
- [ ] `tests/test_querschnitte.py` — covers PRUEF-07-Datenquelle
- [ ] `tests/test_pruefung.py`-Erweiterung — covers PRUEF-06, PRUEF-07, PRUEF-08 (neue `_pruefe_regel6/7/8`-Testfälle neben bestehenden Regel-1-4-Tests)
- [ ] Framework-Install: keiner nötig — pytest bereits vorhanden

## Security Domain

Dieses Projekt ist eine rein lokale, offline laufende Python-CLI-Pipeline ohne Netzwerkzugriff, Authentifizierung oder Mehrbenutzerbetrieb (`.claude/CLAUDE.md`: „Keine Drittanbieter-Requests zur Laufzeit“). Die meisten ASVS-Kategorien sind daher strukturell nicht anwendbar.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Kein Login, keine Benutzerkonten in der Pipeline |
| V3 Session Management | no | Kein Server/Sitzungen |
| V4 Access Control | no | Lokales CLI-Tool, kein Mehrbenutzerzugriff |
| V5 Input Validation | yes | PDF-Inhalt wird als teilweise untrusted (Struktur kann vom erwarteten Muster abweichen) behandelt: jeder unerwartete Wert bricht fail-fast ab (D-08-Konvention, bereits etabliertes Muster in `plaene.py`/`seiten.py`). Neu: `art`-Zuordnung (D-07) muss bei unbekanntem Konto abbrechen statt stillschweigend zu klassifizieren. |
| V6 Cryptography | no | Keine Kryptografie im Scope dieser Phase |

### Known Threat Patterns for diesen Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unbeabsichtigte Offenlegung personenbezogener Daten (Mitarbeitendennamen) | Information Disclosure | D-09: Namen werden beim Parsen erkannt, aber nie in `daten/` geschrieben; Test prüft Abwesenheit in `produkte.json` und im gesamten `daten/`-Baum (nicht nur im JSON) |
| CSV-Formel-Injektion in Freitextfeldern (`=`, `+`, `-`, `@` am Zellenanfang), falls `erlaeuterungen.csv`/`grundzahlen.csv` später in Tabellenkalkulation geöffnet wird | Tampering (indirekt, über Drittsoftware) | Aus dem PDF extrahierte Beträge/Texte beginnen laut Stichprobe nie mit diesen Zeichen; dennoch empfiehlt sich, `schema.py`'s `_pruefe_keine_leeren_strings`-Muster um eine Warnung (kein Hard-Fail, da legitime Werte wie „-123“ vorkommen können) zu erweitern — **[ASSUMED]**, nicht Teil der CONTEXT.md-Entscheidungen, nur als Härtungsvorschlag für den Planner |

## Sources

### Primary (HIGH confidence)
- `raw_data/haushalt-2026.pdf` Seiten 145-154, 184, 265, 280, 291 — direkt per `pdfplumber.extract_text()` dieser Session gelesen (Skript: `scratchpad/dump_page.py`)
- `pipeline/ostbevern/{pdf,zahlen,plaene,seiten,schema,pruefung,konfiguration,zeilen}.py` — vollständig dieser Session gelesen
- `pipeline/jahrgaenge/2026.toml`, `pipeline/jahrgaenge/2026_sollwerte.toml` — dieser Session gelesen
- `daten/zwischen/seiten.csv`, `daten/pruefberichte/befunde.md` — dieser Session per `grep`/`cat` geprüft
- `discussion/SPEZIFIKATION.md` §2, §2.1, §2.2, §3.8, §4.1-4.4, §5.1-5.6, Anhang A — vollständig dieser Session gelesen
- `uv run python -c "import pdfplumber, polars, typer, pytest"` — Versionsausgabe dieser Session

### Secondary (MEDIUM confidence)
— keine, alle Befunde direkt verifiziert (kein externer Websuche-Zugriff konfiguriert: `brave_search`/`exa_search`/`tavily_search`/`ref_search`/`firecrawl`/`jina`/`perplexity` stehen alle auf `false` in `.planning/config.json`, und die Domäne ist rein projektintern)

### Tertiary (LOW confidence)
— keine

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — bereits etabliert, Versionen dieser Session direkt geprüft
- Architecture: HIGH — basiert auf vollständig gelesenem Bestandscode und direkt gegen das Quell-PDF verifizierten Beispielen
- Pitfalls: HIGH für Pitfalls 1-8 (alle gegen reale PDF-Seiten dieser Session verifiziert); MEDIUM für die Verallgemeinerbarkeit über alle 12 „(Kassenwirksamkeit)“-Zeilen (nur 3 Stichproben geprüft, siehe Open Question 2)

**Research date:** 2026-10-01
**Valid until:** 60 Tage (stabile, projektinterne Domäne ohne externe Versionsabhängigkeiten; PDF-Quelle ändert sich nicht)
