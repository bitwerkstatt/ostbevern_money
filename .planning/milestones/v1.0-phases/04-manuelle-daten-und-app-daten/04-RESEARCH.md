# Phase 4: Manuelle Daten und App-Daten - Research

**Researched:** 2026-10-02
**Domain:** Python-Datenpipeline (manuelle Vorbericht-Abschrift, PDF-Koordinatenparser für den Stellenplan, Konsistenzprüfung, App-JSON-Generierung) für eine statische Vue-App ohne Backend
**Confidence:** HIGH (fast alles ist Erweiterung bestehender, im Repo gelesener Muster; die einzigen MEDIUM/LOW-Punkte stehen im Assumptions Log)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Weitergabe an Kreis und Land (DATA-02)**
- D-01: Block „Weitergabe an Kreis und Land" ist eurogenau gleich TP 160101 Z. 15, für alle Jahre 2024–2029. Eine Prüfung (Teil von Regel 5) stellt sicher, dass TP 160101 Z. 15 je Jahr der Summe der drei Vorberichtsposten aus `transferaufwendungen.csv` entspricht (×1000, Toleranz ±1.000 € je Posten, ±3.000 € für die Summe).
- D-02: Die drei Unterposten sind die Vorberichtswerte × 1000, als gerundet gekennzeichnet (`gerundet: true`, Quelleinheit T€, PDF-Seite 46). Die App zeigt sie als „rd.". Die Blocksumme bleibt der eurogenaue Planwert aus D-01.
- D-03: Der Block ist ein eigener synthetischer Top-Knoten auf PB-Ebene (z. B. `code: "KL"`, `synthetisch: true`). PB 16, PG 1601, Produkt 160101 werden um TP Z. 15 reduziert; PB 16 heißt „Allgemeine Finanzwirtschaft". Reversibility: costly (Phase 5/6 bauen auf dieser Knotenstruktur auf).
- D-04: Zuschussbedarf wird für jeden Knoten ohne Ausnahme rein nach Formel berechnet (D-23). „Allgemeine Finanzwirtschaft" bekommt dadurch einen großen negativen Wert (`ueberschuss: true`). Keine Sonderregel für allgemeine Deckungsmittel.

**Manuelle Tabellen (MANU-01 bis MANU-07, PRUEF-05)**
- D-05: Vorberichtstabellen in T€ wie gedruckt, Spalte `betrag_teur` (int). Erst Schritt 07 rechnet ×1000 und setzt `gerundet`.
- D-06: Manuelle CSVs im Langformat: `tabelle/posten, jahr, wertart, betrag_teur, anmerkung, quelle`. CSV-Konventionen aus Phase 2 D-21, zentrales Schema-Modul (D-22). „2024 vorl. RE" → `wertart=ergebnis`.
- D-07: Regel 5 prüft zweistufig: (a) Summe der Posten = gedruckte Gesamtzeile exakt in T€ (Gesamtzeile wird mit abgeschrieben); (b) Gesamtzeile×1000 gegen GEP-Planzeile, Toleranz ±1.000 €. Bekannte Abweichungen: Zuwendungen 2026 Stufe (a) Σ3.108 vs. gedruckt „Gesamt" 3.109; Stufe (b) 3.109 T€ vs. 3.113.200 € (Δ 4.200 €, App weist als „Sonstige" aus). Kita-Tabelle gegen „Zuschüsse an Kindertageseinr." (559) in `transferaufwendungen.csv`. Fußnote an 10.147 wird korrigiert, als Anmerkung.
- D-08: `weitere_vorberichtstabellen.csv` enthält genau die fünf Tabellen aus Spez. 4.3 (Leistungsentgelte 2.1.4, Kostenerstattungen 2.1.6, Personal 2.2.1, Sachaufwand 2.2.3, Sonstige Aufwendungen 2.2.6), je mit Aufschlüsselung und Gesamtzeile, geprüft gegen die jeweilige GEP-Zeile. 2.1.7 gehört NICHT zu Phase 4.
- D-09: Manuelle Dateien werden einmal abgeschrieben (Executor darf pdfplumber zum Ablesen nutzen); kein Pipeline-Schritt überschreibt sie danach. README unter `daten/manuell/` begründet die Werte je Datei.
- D-10: `meta.json` Kreisumlage brutto = netto + Rückstellungsauflösung = 10.147.000 + 1.325.478 = 11.472.478 €, als berechnet/gerundet gekennzeichnet, Quelle S. 46, Gegenprüfung gegen Fußnotentext „11,5 Mio. €" (±50 T€). Jeder Wert in `meta.json` trägt seine Quelle.

**Schulden, Rücklagen, VE (S. 24/25, 309–311)**
- D-11: Verbindlichkeiten (S. 310), Eigenkapital (S. 311), VE-Übersicht (S. 309, S. 25) manuell nach `daten/manuell/` (wie D-09). Regel 5 prüft quer: Investitionskredite Ende 2026 = Ende 2025 + GFP Z. 33 − GFP Z. 35 = 6.879+5.200−450 = 11.629 T€; Jahresergebnis S. 311 = GEP Z. 28 je Jahr; Verringerung Ausgleichs-/allgemeine Rücklage = Satzung § 4 (2.132.213 € / 221.293 €); VE-Fälligkeiten S. 309 = `ve_faelligkeiten.csv`, VE-Summe = 11.600 T€ = GFP-VE 2026.
- D-12: Cent-Beträge S. 311 kaufmännisch auf int-Euro gerundet. −2.353.505,75 → −2.353.506 (trifft Satzung/GEP Z. 28). TEUR-Werte S. 310 bleiben `betrag_teur`.
- D-13: Schuldenstand 2027–2029 fortgeschrieben: Investitionskredite Ende Jahr = Vorjahr + GFP Z. 33 − Z. 35, als `berechnet: true` mit Formelhinweis. 2024–2026 gedruckt von S. 310, 2026 gegen Formel geprüft.
- D-14: Schuldenstand/Pro-Kopf nach Vorbericht-Definition: Investitionskredite + abgerufene NRW.Bank-Mittel (Transferverbindlichkeit). Ende 2025 = 6.879+831 = 7.710 T€ ≈ 656 € (11.741 Einwohner, S. 24/25, Anhang B.6, Sollwert-Test). NRW.Bank-Anteil bleibt für die Fortschreibung konstant (berechnet). Liquiditätskredite (S. 310 Z. 3) getrennt.

**Erklärtexte (MANU-08, Vorbereitung UI-05)**
- D-15: Zahlen in `texte/erklaerungen.md` ausschließlich Platzhalter mit Datenschlüssel/Formathinweis (`{{zuwendungen.schluesselzuweisung.2026|mio}}`). Schritt 07 parst, prüft Schlüsselexistenz (sonst Abbruch), schreibt Text+Werte als JSON. Die App setzt Werte ein und formatiert (`format.ts`); die Pipeline formatiert nie. Abgeleitete Zahlen werden als benannte, berechnete Werte erzeugt (z. B. `abgeleitet.schluesselzuweisung_rueckgang_2026`). Test findet nackte Ziffern (Ausnahmen: Jahreszahlen, Paragraphen, Seitenverweise). Jeder Text verweist auf eine PDF-Seite. Reversibility: costly (Vertrag Pipeline/Textdatei/App-Komponente).
- D-16: Phase 4 schreibt alle Vorbericht-Erklärtexte für Phase 5/6 (ca. 8–10): Schlüsselzuweisung, Gewerbesteuer, Kreisumlage (netto/brutto, Hebesätze), Grundsteuer/Hebesätze, Sonderposten (kein Geldfluss), globaler Minderaufwand, Defizit/Rücklagen, Schulden, VE, BBO/TEO. Glossarbegriffe bleiben Phase 5. Alle Texte in Du-Anrede.
- D-17: „Geprüft" heißt: Executor entwirft die Texte, ein Checkpoint im Plan legt sie dem Nutzer zur fachlichen Abnahme vor, bevor sie committet werden. Platzhalter-Test und Ziffern-Test sichern die Zahlen.

**Stellenplan (EXTR-10)**
- D-18: Stellenwerte als int in Hundertstel (`stellen_hundertstel`, 52,26 → 5226). JSON/App teilen durch 100. Reversibility: costly.
- D-19: Umfang S. 284–290: Teil A Beamte (284), Teil B Tarif (285), Teil B Sozial-/Erziehungsdienst (286), drei PB-Übersichten (287–289). Teil A/B je Gruppe: Stellen 2026, Stellen 2025, besetzt 30.06.2025, „davon ausgesondert" (nur Beamte), Vermerke in eigener Spalte. S. 290 (Nachwuchskräfte) als eigener `teil`: Personen „vorgesehen 2026" und „beschäftigt am 01.10.2025", eigener Stichtag, zählt NICHT zur Stellensumme.
- D-20: Prüfung wie Phase 3 D-08: gedruckte „insgesamt"/„Summe"-Zeilen gegengeprüft, nicht gespeichert, Verstoß bricht mit PDF-Seite ab. Kreuzprüfung: Summe PB-Übersicht je Gruppe = Stellen 2026 aus Teil A/B. Gedruckte Rundungsdifferenzen der VZÄ-Anteile → befunde.md mit Seitenbeleg. Sollwert Beamte 2026 = 8 in `2026_sollwerte.toml`, plus weitere B.6-Eckwerte (Hebesätze, Schlüsselzuweisung, Pro-Kopf-Verschuldung).

**App-Daten (DATA-01, DATA-03)**
- D-21: Dateischnitt `app/src/data/`: `haushalt.json` (Hierarchie inkl. KL-Knoten, Planwerte je Knoten, Steuerarten, Zuwendungen inkl. „Sonstige", Transferaufschlüsselung, Kita-Zuschüsse, weitere Vorberichtstabellen, meta, Rücklagen/Eigenkapital), `produkte.json` (aus `daten/aufbereitet/`, schon ohne Namen), `investitionen.json` (Maßnahmen mit `art`, VE, Fälligkeiten, Finanzierung, Schuldenstand), `stellenplan.json`, eine Zusatzdatei für Erklärtexte (z. B. `texte.json`). TypeScript-Typen zentral (z. B. `app/src/data/typen.ts`). Test bestätigt keine Personennamen in keiner App-Datei. Reversibility: costly.
- D-22: `haushalt.json` trennt Ergebnis-/Finanzplan in getrennten Schlüsseln: `ergebnisplan` (je Knoten PB/PG/P/KL/GESAMT, Zeilen 01–17, 19, 20, Minderaufwand TP 30/GEP 27, Summen, alle Jahre/Wertarten), `finanzplan` (nur GESAMT-Ebene: Z. 23, 25, 30, 33, 35, VE, Liquide Mittel). TP 27/28 gehen nicht in die App.
- D-23: Aufwand = Z. 17+Z. 20; Erträge = Z. 10+Z. 19; Zuschussbedarf = Aufwand−Erträge (= −Z. 26), vor Minderaufwand, ohne TP 27/28. 2026-Summe = 30.455.569 € Aufwand (Satzung). Minderaufwand eigener erklärter Posten. Zuschussbedarf und alle berechneten Werte gekennzeichnet (`berechnet: true`). Test: Summe der Top-Knoten (15 PB, PB 16 reduziert, plus KL) = GESAMT.

**CI-Diff (PRUEF-10)**
- D-24: `alle.py`: 01→02→03→04→Querschnitte→05→06→07. CI prüft in eigenem Schritt im `pipeline`-Job nach pytest: `uv run python alle.py`, dann `git diff --exit-code -- daten app/src/data` plus Prüfung auf ungetrackte Dateien. `daten/manuell/` eingeschlossen (darf sich nie verändern). JSON-Ausgabe deterministisch (feste Schlüsselreihenfolge, UTF-8, LF, abschließender Zeilenumbruch).

### Claude's Discretion
- Genaue Spaltenlisten/Sortierung aller neuen CSVs (`steuerarten.csv`, `zuwendungen.csv`, `transferaufwendungen.csv`, `kita_zuschuesse.csv`, `weitere_vorberichtstabellen.csv`, Dateien für Verbindlichkeiten/Eigenkapital/VE-Übersicht, `stellenplan.csv`)
- Ob Schulden, Eigenkapital, VE-Übersicht eigene Dateien oder Tabellen in `weitere_vorberichtstabellen.csv` sind
- Feldstruktur von `meta.json` (Wert + Quelle je Feld)
- Konkrete JSON-Struktur von `haushalt.json` usw. (Werte je Jahr als Objekt oder Arrays entlang `jahre`-Liste); Münster nur als Vorlage
- Konkrete Platzhalter-Syntax und Formatkürzel (D-15), Name/Struktur der Text-JSON
- Aufbau des README unter `daten/manuell/`
- Modulaufteilung in `ostbevern/` (z. B. `manuell.py`, `stellenplan.py`, `app_daten.py`, `texte.py`) und neue Skripte `05_stellenplan.py`/`07_app_daten.py`
- Ob Regel 5 eine Regel mit Unterprüfungen ist oder in 5a/5b/… aufgeteilt wird
- Codevergabe für den KL-Knoten und die drei Unterposten

### Deferred Ideas (OUT OF SCOPE)
- Abschreiben von 2.1.7 (Sonstige ordentliche Erträge, Konzessionsabgaben) und weiterer Vorberichtstabellen (Privatrechtliche Entgelte, Finanzerträge, Versorgung, Abschreibungen, Zinsen, Investitionstabellen 3.2–3.4) — bei Bedarf Phase 5 (EINN-04/EINN-06)
- Kreisumlage brutto/netto in der Anzeige — Darstellung Phase 5 (Callout AUSG-02)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MANU-01 | `steuerarten.csv` (8 Steuerarten, 2024–2029, T€) | Anhang B.4 verbatim unten; `schema.py`/`konfiguration.py` Erweiterungsmuster |
| MANU-02 | `zuwendungen.csv` (Schlüsselzuweisung, laufende Zwecke, Sonderposten) | S. 28-Zahlen in Sollwertdatei bereits vorhanden (GEP Z. 02); Pitfall „Zuwendungsdifferenz" dokumentiert |
| MANU-03 | `transferaufwendungen.csv` inkl. Kreisumlage netto/Fußnote | S. 45/46 Volltext verbatim gelesen (siehe PDF-Funde unten); B.5 |
| MANU-04 | `kita_zuschuesse.csv` (7 Einrichtungen, Σ 559 T€) | S. 46 Volltext verbatim gelesen |
| MANU-05 | `weitere_vorberichtstabellen.csv` (5 Tabellen) | Spez. 4.3-Tabelle; Pitfall Sachaufwand-Differenz 2027–2029 |
| MANU-06 | `meta.json` (Einwohner, Hebesätze, Fläche, Satzungsdatum, Kreisumlage brutto/netto) | S. 8/9 (Satzung) und S. 24/25 verbatim gelesen; Kreuzprüfungs-Formel für Satzung §4 hergeleitet |
| MANU-07 | `quelle`-Spalte + README je manueller Datei | Muster aus Phase 2/3 CSV-Konventionen (`schema.py`), README-Analogie zu Münster |
| MANU-08 | Geprüfte Erklärtexte (`texte/erklaerungen.md`) | Platzhalter-Pattern + Checkpoint-Workflow unten |
| PRUEF-05 | Manuelle Tabellen vs. Planzeilen | Zweistufige Toleranz-Architektur + `lies_befunde`-Enum-Constraint (Pitfall) unten |
| EXTR-10 | `stellenplan.csv` (Teil A/B, Stellenübersicht) | S. 284–290 Volltext verbatim gelesen; `ordne_spalten`-Grenzen (Pitfall) |
| DATA-01 | `haushalt.json`, `produkte.json`, `investitionen.json`, `stellenplan.json` | Architektur-Diagramm + Code-Beispiele (`schreibe_produkte_json`-Muster) unten |
| DATA-02 | „Weitergabe an Kreis und Land" als eigene Kategorie | D-01–D-04 bereits verbindlich; Umsetzungsmuster (app_daten.py-only transform) unten |
| DATA-03 | Zuschussbedarf berechnet/gekennzeichnet | D-23-Formel; `zeilen.py`-FORMELN als Referenz |
| PRUEF-10 | `alle.py` reproduzierbar, CI-Diff | Bestehendes `alle.py`/CI-Muster, Erweiterung dokumentiert |
</phase_requirements>

## Summary

Phase 4 ist zu 95 % **Erweiterung bestehender, bereits im Repo etablierter Muster** — kein neues Framework, keine neue Bibliothek, kein neuer Architekturstil. Die drei fachlich neuen Bausteine sind: (1) ein Koordinatenparser für den Stellenplan (S. 284–290), der dieselbe `ordne_spalten`/`Textzeile`-Infrastruktur wie `investitionen.py`/`querschnitte.py` nutzt, aber mit **sparse** (lückenhaften) Zeilen umgehen muss — ein Unterschied zu allen bisherigen Parsern, die volle Zeilen erzwingen; (2) eine zweistufige Toleranzprüfung (Regel 5) für Vorbericht-T€-Tabellen gegen GEP-Zeilen, die eine neue Toleranzgröße (±1.000 €) neben der bestehenden `TOLERANZ_EURO=1` einführt und auf das bestehende, **strikt validierende** `befunde.md`-Schema (`EBENEN`/`WERTARTEN`-Enums) abgebildet werden muss; (3) ein Platzhalter-Parser für `texte/erklaerungen.md`, der nach demselben Fail-Fast-Prinzip wie alle Extraktionsschritte funktioniert (unbekannter Schlüssel → Abbruch).

Die Personennamen-Sicherung (Erfolgskriterium 4) ist **kein neuer Mechanismus**: `produkte.lies_personennamen` plus der bestehende `test_keine_personennamen`-Scan über `DATEN_WURZEL.rglob("*")` müssen nur um `app/src/data/` erweitert werden. Die atomare, deterministische JSON-Schreiblogik (`schreibe_produkte_json`) ist das direkte Vorbild für die neuen `app/src/data/*.json`-Writer. Die Recherche hat außerdem eine offene Frage aus CONTEXT.md D-14 anhand des Original-PDFs **aufgelöst**: S. 310 druckt den NRW.Bank-Anteil für Ende 2026 direkt (746 T€) — er ist für 2026 kein Assumption, sondern ein Druckwert; nur die Fortschreibung 2027–2029 bleibt eine Annahme.

**Primary recommendation:** Jede neue Datei/jeder neue Prüfschritt hängt sich strikt an ein bestehendes Modul an (`schema.py` für Spalten/IO, `konfiguration.py` für TOML, `pruefung.py` für Regel 5, `produkte.py`-Testmuster für Personennamen) statt neue Abstraktionen zu erfinden; die einzige wirklich neue Low-Level-Technik ist der sparse-row-Stellenplan-Parser.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Manuelle Vorbericht-Tabellen (CSV + README) | Build-Time Pipeline (Python) | — | Einmalige Abschrift, danach statische, eingecheckte Eingabedaten; kein Laufzeitcode |
| Stellenplan-Extraktion (PDF → CSV) | Build-Time Pipeline (Python) | — | Reiner Koordinatenparser, analog zu `investitionen.py`/`plaene.py` |
| Prüfregel 5 (Konsistenz) | Build-Time Pipeline (Python) | — | Liest ausschließlich CSVs/TOML (D-06-Invariante aus Phase 2), nie das PDF erneut |
| KL-Knoten-Split, Zuschussbedarf-Berechnung | Build-Time Pipeline (Python, `07_app_daten.py`) | — | Reine Datentransformation; **nicht** in `daten/aufbereitet/hierarchie.csv` (die bleibt von Phase 2/3 unverändert, CI-Diff-stabil) |
| Platzhalter-Auflösung in Erklärtexten | Build-Time Pipeline (Python, `07_app_daten.py`) | — | Schlüssel→Wert-Auflösung ist Build-Zeit; **Formatierung** (`format.ts`) bleibt explizit App-Zeit (D-15) |
| Zahlenformatierung („Mio. €", VZÄ, %) | Browser/Client (`app/src/charts/format.ts`) | — | Bereits etabliert (UI-05); Pipeline liefert nur Rohwerte + Formathinweis |
| CI-Diff-Prüfung | Build/CI (GitHub Actions) | — | Reproduzierbarkeits-Gate, kein Laufzeitverhalten |
| Statische JSON-Artefakte (`app/src/data/*.json`) | Static Data Artifact | Browser/Client (Konsum ab Phase 5/6) | Diese Phase erzeugt nur die Artefakte; Konsum ist explizit außerhalb des Scopes |

## Standard Stack

### Core

Keine neuen Abhängigkeiten. Phase 4 erweitert ausschließlich bereits deklarierte Pipeline- und App-Module.

| Library | Version (verifiziert) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pdfplumber | `>=0.11.10` [VERIFIED: pipeline/pyproject.toml:7] | Wortkoordinaten für den Stellenplan-Parser | Bereits einzige PDF-Zugriffsbibliothek (`ostbevern/pdf.py`) |
| polars | `>=1.44.2` [VERIFIED: pipeline/pyproject.toml:8] | CSV-Schema/IO für alle neuen Tabellen | Zentrales `schema.py`-Modul nutzt es bereits durchgängig |
| typer | `>=0.27.2` [VERIFIED: pipeline/pyproject.toml:9] | `05_stellenplan.py`, `07_app_daten.py` als dünne CLI-Einstiege | Bestehendes Muster aller nummerierten Skripte |
| pytest | `>=9.1.1` [VERIFIED: pipeline/pyproject.toml:14] | Neue Testdateien (`test_manuell.py`, `test_stellenplan.py`, `test_app_daten.py`) | Einzige Teststrategie im Projekt (D-06) |
| tomllib (stdlib) | Python ≥3.12 | Erweiterung von `2026_sollwerte.toml` um B.4–B.6 | `konfiguration.py` ist die einzige Stelle, die `tomllib` importiert |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| TypeScript (App, keine neue Lib) | `~6.0.0` [VERIFIED: app/package.json] | Zentrale Typen für `app/src/data/*.json` (`typen.ts`) | Für D-21 (Claude's Discretion: Typstruktur) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `tomllib`-Erweiterung von `2026_sollwerte.toml` | Eigene `.json`/`.yaml`-Sollwertdatei für B.4–B.6 | Bricht mit dem bestehenden Single-Source-Pattern (`lade_sollwerte`); kein Vorteil, nicht empfohlen |
| Eigener Markdown-Parser für Regel-5-Befunde | Bestehenden `lies_befunde`/`_SCHLUESSELTABELLE_KOPF`-Mechanismus wiederverwenden | Ein zweites Dateiformat würde D-02 („Mensch und Maschine nutzen dieselbe Datei") brechen — nicht empfohlen |
| Neues JS-Test-Framework (vitest) nur für den „keine Personennamen"-Test der App-JSONs | Bestehenden Python/pytest-Scan (`test_keine_personennamen`) auf `app/src/data/` erweitern | App-JSONs sind reine Build-Artefakte ohne Laufzeitlogik; ein Pipeline-seitiger Test prüft sie ohne neue Werkzeugkette einzuführen (siehe Validation Architecture) |

**Installation:**
```bash
# Keine Installation nötig — alle Pakete sind bereits in pipeline/pyproject.toml deklariert
# und via pipeline/uv.lock gepinnt. `uv sync --directory pipeline` reicht.
```

**Version verification:** Durchgeführt — siehe Tabelle oben, alle Versionen stammen aus dem bereits im Repo vorhandenen `pipeline/pyproject.toml` bzw. `app/package.json` (gelesen in dieser Sitzung), keine Registry-Abfrage nötig, da keine neue Abhängigkeit hinzukommt.

## Package Legitimacy Audit

**Nicht anwendbar.** Phase 4 installiert keine neuen externen Pakete (weder `pip`/`uv add` noch `npm install`). Alle verwendeten Bibliotheken sind bereits deklarierte, gepinnte Abhängigkeiten aus Phase 1–3 (`pipeline/pyproject.toml`, `pipeline/uv.lock`, `app/package.json`, `app/package-lock.json`). Der Plan sollte keinen Task enthalten, der eine neue Abhängigkeit hinzufügt; sollte sich während der Umsetzung doch ein Bedarf zeigen (z. B. für Quellenbelege-Rendering, das aber laut CONTEXT.md explizit **nicht** Teil dieser Phase ist), muss das Gate nachträglich durchlaufen werden.

**Packages removed due to [SLOP] verdict:** keine
**Packages flagged as suspicious [SUS]:** keine

## Architecture Patterns

### System Architecture Diagram

```
raw_data/haushalt-2026.pdf
        │
        ├──(Executor liest S. 27/28/45-46/8-9/24-25/309-311 von Hand,
        │   darf pdfplumber zum Ablesen nutzen, D-09)
        │                                             ┌─────────────────────────┐
        │                                             │ daten/manuell/           │
        │                                             │  steuerarten.csv         │
        │                                             │  zuwendungen.csv         │
        │                                             │  transferaufwendungen.csv│
        │                                             │  kita_zuschuesse.csv     │
        │                                             │  weitere_vorbericht...   │
        │                                             │  verbindlichkeiten.csv   │
        │                                             │  eigenkapital.csv        │
        │                                             │  ve_uebersicht.csv       │
        │                                             │  meta.json               │
        │                                             │  README.md               │
        │                                             └───────────┬─────────────┘
        │                                                         │ (eingecheckt,
        │                                                         │  nie überschrieben)
        ├──(05_stellenplan.py liest S. 284-290               ▼
        │   über jahrgang.seitenbereiche["stellenplan"],
        │   KEIN seiten.csv-Zwischenschritt nötig)
        ▼
  daten/aufbereitet/stellenplan.csv
        │
        │        daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan,
        │        investitionen,ve_faelligkeiten,produkte.json}.csv  (Phase 2/3, unverändert)
        │                        │
        ▼                        ▼
  ┌─────────────────────────────────────────────────┐
  │ 06_pruefen.py / pruefung.pruefe_alles             │
  │  Regel 5 (neu): manuelle Tabellen vs. Planzeilen  │
  │  Stellenplan-Kreuzprüfung (neu, D-20)             │
  │  Regeln 1-4, 6-8 (unverändert aus Phase 2/3)      │
  └───────────────────────┬───────────────────────────┘
                           ▼
          daten/pruefberichte/{konsistenz,befunde}.md
                           │
     texte/erklaerungen.md (Platzhalter, Executor-Entwurf
        + Nutzer-Checkpoint vor Commit, D-17)
                           │
                           ▼
  ┌─────────────────────────────────────────────────┐
  │ 07_app_daten.py (NEU)                             │
  │  - liest alle obigen Quellen (nur CSV/JSON/TOML)  │
  │  - baut KL-Knoten (nur hier, nie in hierarchie.csv)│
  │  - berechnet Zuschussbedarf je Knoten (D-23)       │
  │  - löst Platzhalter in erklaerungen.md auf         │
  │  - schreibt atomar, deterministisch (wie           │
  │    schreibe_produkte_json: tempfile + os.replace)  │
  └───────────────────────┬───────────────────────────┘
                           ▼
            app/src/data/
              haushalt.json  produkte.json
              investitionen.json  stellenplan.json
              texte.json  typen.ts (TS-Typen, handgeschrieben)
                           │
                           ▼
            (Konsum ab Phase 5/6 — AUSSERHALB dieser Phase)

  CI (pipeline-Job, neuer Schritt nach pytest, D-24):
    uv run python alle.py
    git diff --exit-code -- daten app/src/data
    git status --porcelain (ungetrackte Dateien prüfen)
```

### Recommended Project Structure
```
pipeline/
├── 05_stellenplan.py        # dünner typer-Einstieg, --jahr
├── 07_app_daten.py          # dünner typer-Einstieg, --jahr
├── ostbevern/
│   ├── manuell.py           # liest daten/manuell/*, Regel-5-Formeln, Kreuzprüfungen
│   ├── stellenplan.py       # PDF-Koordinatenparser S. 284-290
│   ├── app_daten.py         # KL-Split, Zuschussbedarf, JSON-Writer
│   └── texte.py             # Platzhalter-Parser/-Auflösung für erklaerungen.md
├── tests/
│   ├── test_manuell.py      # Regel-5-Tests, liest eingecheckte manuelle CSVs
│   ├── test_stellenplan.py  # PDF-Tests gegen S. 284-290 (wie test_investitionen.py)
│   └── test_app_daten.py    # App-JSON-Tests inkl. erweitertem Personennamen-Scan
daten/
├── manuell/
│   ├── steuerarten.csv, zuwendungen.csv, transferaufwendungen.csv,
│   │   kita_zuschuesse.csv, weitere_vorberichtstabellen.csv,
│   │   verbindlichkeiten.csv, eigenkapital.csv, ve_uebersicht.csv, meta.json
│   └── README.md
└── aufbereitet/
    └── stellenplan.csv
app/src/data/
├── haushalt.json, produkte.json, investitionen.json, stellenplan.json, texte.json
└── typen.ts
texte/
└── erklaerungen.md
```

### Pattern 1: Sparse-Row-Spaltenzuordnung für den Stellenplan (NEU gegenüber Phase 2/3)
**What:** `ordne_spalten` (spalten.py) ordnet Wörter dem nächstgelegenen x1-Anker zu, OHNE zu verlangen, dass alle Anker belegt sind — die Funktion selbst wirft nur bei Toleranzüberschreitung oder Anker-Kollision. Die **Aufrufer** `investitionen.py` und `querschnitte.py` fügen jedoch jeweils zusätzlich `if len(zugeordnet) != anzahl_spalten: raise ...` hinzu, weil dort jede Zeile alle Spalten füllt.
**When to use:** Für die Stellenübersichts-Tabellen S. 287–289 (Kreuzprüfung-Matrix) und teilweise S. 284–286, wo eine Zeile oft nur 1–3 von vielen möglichen Spalten belegt (verifiziert: PB 11 „Ver- und Entsorgung 0,01" und PB 16 „Allgemeine Finanzwirtschaft 0,06" auf S. 287 haben je nur einen Wert von 13 möglichen Spalten).
**Example:**
```python
# Quelle: pipeline/ostbevern/spalten.py (gelesen in dieser Sitzung) + Anpassung für
# Stellenplan: KEINE len(zugeordnet) == len(anker_x1)-Prüfung, fehlende Spalten = 0/None,
# analog zum "fehlende Zeile = 0"-Prinzip aus Phase 2 D-11, hier aber auf Zellenebene.
amount_woerter = [w for w in zeile.woerter if ist_betrag_oder_vzae(w.text)]
zugeordnet = ordne_spalten(amount_woerter, anker_x1)  # kann unvollständig sein — das ist hier OK
werte = {besoldungsgruppe[i]: zugeordnet[i].text for i in zugeordnet}  # fehlende i -> kein Eintrag
```

### Pattern 2: Hundertstel-exakte Dezimalparsing (D-18)
**What:** `zahlen.lies_kennzahl` liefert `(float, nachkommastellen)` — für Stellen-VZÄ (immer genau 2 Nachkommastellen gedruckt) ist das Risiko, dass `round(wert * 100)` bei Werten wie `6,38` durch Float-Repräsentation (`6.38 * 100 == 637.9999999999999` in manchen Fällen) einen Off-by-one-Fehler erzeugt.
**When to use:** Jede Umwandlung einer gedruckten Stellenplan-Dezimalzahl in `stellen_hundertstel` (D-18).
**Example:**
```python
# Quelle: Eigene Herleitung aus pipeline/ostbevern/zahlen.py (gelesen in dieser Sitzung,
# siehe _KENNZAHL_MUSTER). Nicht `round(lies_kennzahl(text)[0] * 100)` verwenden — das
# parst über float. Stattdessen auf der STRING-Repräsentation arbeiten:
def lies_stellen_hundertstel(text: str) -> int | None:
    wert = lies_kennzahl(text)  # (float, nachkommastellen) | None
    if wert is None:
        return None
    _, nachkommastellen = wert
    if nachkommastellen != 2:
        raise ZahlenFehler(f"Stellenwert ohne exakt 2 Nachkommastellen: {text!r}")
    ganzzahl_teil, dezimal_teil = text.strip().replace("−", "-").split(",")
    vorzeichen = -1 if ganzzahl_teil.startswith("-") else 1
    ziffern = ganzzahl_teil.lstrip("-").replace(".", "") + dezimal_teil
    return vorzeichen * int(ziffern)
```

### Pattern 3: Regel-5-Befunde im bestehenden Enum-Schema (Pitfall, siehe unten)
**What:** `lies_befunde` (pruefung.py) validiert `ebene in EBENEN` (`"GESAMT","PB","PG","P"`) und `wertart in WERTARTEN` (`"ergebnis","ansatz","ve","planung"`) strikt — ein unbekannter Wert bricht mit `PruefungsFehler` ab. Regel 5 vergleicht aber **Vorbericht-Tabellen**, die keine PB/PG/P-Knoten sind.
**When to use:** Jedes Regel-5-Pruefpunkt/Befund-Tripel.
**Example:**
```python
# Quelle: Muster aus pipeline/ostbevern/pruefung.py _pruefe_regel4_satzung (gelesen in
# dieser Sitzung) — dort wird code="" und ebene="GESAMT" für Satzungs-Formeln verwendet,
# während `plan` den fachlichen Kontext trägt ("satzung"). Regel 5 folgt demselben Muster:
punkt = Pruefpunkt(
    regel=5,
    plan="vorbericht_transferaufwendungen",  # fachlicher Kontext statt neuer Ebene
    ebene="GESAMT",
    code="",
    zeile="kreisumlage_netto",               # Posten-Schlüssel statt GEP-Zeilennummer
    jahr=2026,
    wertart="ansatz",                        # "2024 vorl. RE" -> "ergebnis" (D-06)
    soll=soll_betrag,
    ist=ist_betrag,
    pdf_seite=46,
)
```

### Pattern 4: Atomares, deterministisches JSON-Schreiben (Vorlage für `07_app_daten.py`)
**What:** `schreibe_produkte_json` (schema.py) schreibt sortiert, mit fester Schlüsselreihenfolge, über `tempfile.mkstemp` + `os.replace`, UTF-8 ohne BOM, LF, abschließender Zeilenumbruch — exakt die D-24-Anforderung für CI-Diff-Stabilität.
**When to use:** Jeder neue `app/src/data/*.json`-Writer in `07_app_daten.py`.
**Example:**
```python
# Quelle: pipeline/ostbevern/schema.py:321-350 (gelesen in dieser Sitzung), Muster
# 1:1 übertragbar auf haushalt.json/investitionen.json/stellenplan.json/texte.json:
inhalt = json.dumps(geordnete_struktur, ensure_ascii=False, indent=2) + "\n"
deskriptor, temp_pfad_str = tempfile.mkstemp(dir=pfad.parent, prefix=".haushalt-", suffix=".tmp")
with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
    datei.write(inhalt)
os.replace(temp_pfad, pfad)
```

### Anti-Patterns to Avoid
- **Hierarchie.csv für den KL-Split mutieren:** Der KL-Knoten und die PB-16-Reduktion sind ausschließlich eine Transformation in `07_app_daten.py` beim Schreiben von `haushalt.json`. `daten/aufbereitet/hierarchie.csv` bleibt byte-identisch zu Phase 2/3 — sonst bricht die CI-Diff-Prüfung (D-24) rückwirkend für bereits abgeschlossene Phasen.
- **Formatierung in der Pipeline:** D-15 verbietet explizit, dass die Pipeline Zahlen formatiert („Mio. €" etc.) — das bleibt `app/src/charts/format.ts` vorbehalten. Platzhalter liefern Rohwert + Formatkürzel, nie einen fertigen String.
- **Toleranz-Konstante wiederverwenden ohne Prüfung:** `pruefung.TOLERANZ_EURO = 1` (Euro) ist für Regel 1–4/6–8 korrekt, aber Regel 5 Stufe (b) braucht ±1.000 € — eine eigene, lokale Konstante (analog zu `investitionen._TOLERANZ_EURO`) ist nötig, nicht `TOLERANZ_EURO` überschreiben.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Dezimal→Hundertstel-Konversion | `round(float * 100)` | String-basiertes Parsing (Pattern 2 oben) | Float-Rundungsfehler sind bei Geld-/Stellenwerten ein bekannter Fehlerklasse; das Projekt verwendet bereits durchgängig int-Werte für genau diesen Zweck (D-18, wie `betrag: int` für Euro) |
| x-Koordinaten-Spaltenzuordnung | Eigener Nearest-Neighbor-Algorithmus | `ostbevern.spalten.ordne_spalten` | Bereits gehärtet (Toleranz-, Kollisionslogik), von `investitionen.py`/`querschnitte.py` genutzt — Phase 2 CONTEXT.md nennt es ausdrücklich „als Vorlage gedacht" für spätere Parser |
| Markdown-Befundtabelle für Regel 5 | Neues zweites „Findings"-Dateiformat | `pruefung.lies_befunde`/`_SCHLUESSELTABELLE_KOPF` (bestehend) | D-02: „Mensch und Maschine nutzen dieselbe Datei; eine zweite Datei gibt es nicht" — gilt unverändert für Regel 5 |
| Personennamen-Erkennung in App-JSONs | Neue Regex-/NLP-Heuristik | `produkte.lies_personennamen` + bestehenden `test_keine_personennamen`-Scan auf `app/src/data/` erweitern (`DATEN_WURZEL` → zusätzlich `PROJEKT_WURZEL / "app/src/data"`) | Die Dreifachsicherung aus Phase 3 (D-09) ist bereits exakt für diesen Zweck gebaut; eine zweite Implementierung würde zwei Wahrheiten über „was ist ein Name" schaffen |
| TOML-Sollwert-Parsing für B.4–B.6 | Eigener Loader | `konfiguration.lade_sollwerte` erweitern (neue optionale Top-Level-Tabellen, wie `haushaltsquerschnitt_pg`/`stichproben` bereits vorgemacht) | `tomllib` ist laut Modul-Docstring „nur hier" importiert; `_pruefe_nur_ganzzahlen` validiert automatisch mit |
| Atomares JSON-Schreiben | `json.dump(datei, ...)` direkt | `schreibe_produkte_json`-Muster (tempfile + os.replace) | D-24 verlangt Determinismus und verhindert abgebrochene Halbschreibungen, die die CI-Diff-Prüfung verfälschen würden |
| CI-Diff-Erkennung | Hash-Vergleich / eigenes Diff-Tool | `git diff --exit-code -- daten app/src/data` + `git status --porcelain` für ungetrackte Dateien | Einfachstes, bereits von Git bereitgestelltes Primitiv; exakt das, was D-24 beschreibt |

**Key insight:** Jedes der oben genannten Probleme hat in Phase 1–3 bereits eine geprüfte, getestete Lösung bekommen. Das Risiko in Phase 4 ist nicht fehlendes Tooling, sondern **Parallelimplementierungen**, die beim nächsten Jahrgang (2027) auseinanderlaufen.

## Common Pitfalls

### Pitfall 1: `ordne_spalten`-Vollständigkeitsprüfung passt nicht auf Stellenübersichten
**What goes wrong:** Ein 1:1 kopierter Aufrufer-Stil aus `investitionen.py`/`querschnitte.py` (`if len(zugeordnet) != anzahl_spalten: raise`) lässt JEDE Zeile mit weniger als allen Spalten scheitern — bei den Stellenübersichten (S. 287–289) ist das aber der Normalfall.
**Why it happens:** Die bisherigen Tabellen (Investitionen, Querschnitte) sind dicht (jede Spalte hat immer einen Wert oder „–"); die Stellenübersicht ist eine dünn besetzte Matrix (PB × Besoldungs-/Entgeltgruppe).
**How to avoid:** Für die PB-Übersichtstabellen die Vollständigkeitsprüfung weglassen; fehlende Zuordnung heißt „kein Eintrag für diese Kombination" (keine Zeile schreiben), nicht Fehler (siehe Pattern 1).
**Warning signs:** Der Parser bricht bereits auf S. 287 Zeile „11 Ver- und Entsorgung 0,01" ab.

### Pitfall 2: Mehrzeilige PB-Namen verschieben den Wert in die falsche visuelle Zeile
**What goes wrong:** Verifiziert auf S. 288: „09 Räumliche Planung u. Ent-" und „wicklung, Geoinformationen 0,06" stehen auf zwei `top`-Gruppen; der Zahlenwert hängt an der ZWEITEN Namenszeile, nicht an der mit der PB-Nummer.
**Why it happens:** `PdfDokument._gruppiere_zeilen` gruppiert nach `top`-Toleranz 2.0 — ein mehrzeiliger Name erzeugt zwei `Textzeile`-Objekte, von denen nur eines Beträge trägt.
**How to avoid:** Wie bei `investitionen.py`/Produktnamen: Name-Fortsetzungszeilen vor der ersten Betragszeile sammeln (siehe `_OffenerBlock.header_fortsetzung`-Muster), erst beim Auftreten von Beträgen den Block abschließen.
**Warning signs:** PB-Code taucht in der CSV mit leerem oder falschem Namen auf.

### Pitfall 3: Block-Fußnoten vs. zeilengebundene Vermerke nicht verwechseln
**What goes wrong:** S. 285 hat eine ZEILENGEBUNDENE Vermerk-Spalte (z. B. „9a ... 0,46 VZÄ mit Sperrvermerk" direkt in derselben Zeile), S. 286 dagegen hat einen BLOCKWEITEN Fußnotentext nach der Tabelle („Eine Stelle an der Josef-Annegarn-Schule … Matching-Verfahren …"), der keiner einzelnen Zeile zugeordnet ist.
**Why it happens:** Beide Textarten sehen im extrahierten Text ähnlich aus (Fließtext nach der letzten Datenzeile); nur die x0-Position (innerhalb der Vermerke-Spaltenzone vs. linksbündig ab Tabellenrand) unterscheidet sie zuverlässig.
**How to avoid:** Vermerke nur übernehmen, wenn ihr erstes Wort rechts der Vermerke-Spaltenanker-x0 beginnt UND auf derselben `top`-Gruppe wie die zugehörige Datenzeile liegt; alles andere ist ein Block-Hinweis fürs README, nicht für die CSV-Spalte.
**Warning signs:** Eine Vermerke-Spalte enthält ganze Sätze mit Schulnamen statt kurzer Vermerke wie „künftig wegfallend (05.2029)".

### Pitfall 4: Satzung-§-4-Kreuzprüfung nicht direkt aus der Eigenkapital-Tabelle ablesbar
**What goes wrong:** Die rohen Jahresdeltas der Eigenkapital-Übersicht (S. 311: Allgemeine Rücklage 2025→2026 unverändert, Ausgleichsrücklage 2025→2026 unverändert) ergeben **nicht** direkt 2.132.213 € / 221.293 € (Satzung § 4) — ein naiver Delta-Vergleich schlägt fehl.
**Why it happens:** [VERIFIED: raw_data/haushalt-2026.pdf S. 311, gelesen in dieser Sitzung] Die Tabelle zeigt zusätzliche Bewegungen (z. B. „Einmalige Verrechnung Bilanzierungshilfe -476.327,00" im Jahr 2026), die den reinen Rücklagenverzehr überlagern. Die korrekte Formel (hergeleitet aus denselben Seitenwerten): `Verringerung Ausgleichsrücklage (2.132.213,17) + Verringerung allgemeine Rücklage (221.292,58) = |Jahresergebnis 2026| (2.353.505,75)`, kaufmännisch gerundet `2.132.213 + 221.293 = 2.353.506` — exakt GEP Z. 28.
**How to avoid:** Regel 5/D-11 implementiert die Kreuzprüfung als `Satzung_§4.ausgleichsruecklage + Satzung_§4.allgemeine_ruecklage == |GEP Z. 28 (2026)|` (gerundet), NICHT als Differenz zweier Jahre in der Eigenkapitalübersicht.
**Warning signs:** Ein Delta-basierter Test auf `eigenkapital.csv` scheitert trotz korrekt abgeschriebener Werte.

### Pitfall 5: NRW.Bank-Anteil ist über die Jahre NICHT konstant (löst eine offene CONTEXT.md-Frage)
**What goes wrong:** CONTEXT.md D-14 flaggt als offen: „Ob 746 T€ Ende 2026 der NRW.Bank-Anteil ist, muss die Recherche klären, bevor D-14 ‚konstant' fortschreibt."
**Resolution:** [VERIFIED: raw_data/haushalt-2026.pdf S. 310, gelesen in dieser Sitzung] Zeile „6. Verbindlichkeiten aus Transferleistungen" druckt genau drei Spalten: **1.221** (Ende 2024) / **831** (Ende 2025) / **746** (Ende 2026) TEUR — exakt die auf S. 24 im Fließtext genannten „rd. 831 T€" für Ende 2025. Der Ende-2026-Wert (746 T€) ist also **direkt gedruckt**, keine Annahme. Erst die Fortschreibung 2027–2029 (keine weiteren Spalten auf S. 310) erfordert die „konstant"-Annahme aus D-14 — und sollte dafür 746 T€ (nicht 831 T€) als Startwert nehmen.
**How to avoid:** `verbindlichkeiten.csv` übernimmt alle drei gedruckten Werte (1.221/831/746 T€) für die Zeile „Verbindlichkeiten aus Transferleistungen"; die Fortschreibungsformel (D-14) hält ab 2027 den **zuletzt gedruckten** Wert (746 T€) konstant, nicht den Ende-2025-Wert.
**Warning signs:** Pro-Kopf-Verschuldung 2027–2029 nutzt versehentlich 831 statt 746 T€ als Sockel.

### Pitfall 6: Zuwendungsdifferenz hat ZWEI Stufen mit unterschiedlichem Vorzeichen-Charakter
**What goes wrong:** D-07 beschreibt zwei unabhängige, beide dokumentationspflichtige Abweichungen bei Zuwendungen 2026: Stufe (a) Posten-Summe (3.108) vs. gedruckte Gesamtzeile (3.109) — Δ 1 T€, reiner Druckfehler/Rundung im Vorbericht selbst; Stufe (b) Gesamtzeile×1000 (3.109.000) vs. GEP Z. 02 (3.113.200) — Δ 4.200 €, eine andere Art Abweichung (Planwert-Diskrepanz).
**Why it happens:** Zwei verschiedene Prüfungen mit unterschiedlichen Quellen (Vorbericht-Innenkonsistenz vs. Vorbericht-gegen-GEP) werden leicht als eine Abweichung missverstanden.
**How to avoid:** Zwei getrennte `befunde.md`-Einträge mit unterschiedlichem `zeile`-Schlüssel (z. B. `zuwendungen_posten_summe` für (a), `zuwendungen_gep_z02` für (b)), nicht eine zusammengefasste Begründung.
**Warning signs:** `gleiche_befunde_ab` matcht den falschen Befund, weil beide denselben `schluessel` verwenden.

### Pitfall 7: `05_stellenplan.py` braucht keinen `seiten.csv`-Durchlauf
**What goes wrong:** Ein Executor könnte versuchen, den Stellenplan wie Produktseiten über `seiten.csv`-Typen zu klassifizieren (Muster aus `investitionen.py`/`produkte.py`).
**Why it happens:** Alle Phase-3-Parser lesen ihre Seitenmenge über `seiten.csv`-Filter (`pl.col("typ").is_in(...)`).
**How to avoid:** Stellenplan-Seiten sind laut `[seitenbereiche].stellenplan = {von=284, bis=290}` [VERIFIED: pipeline/jahrgaenge/2026.toml:33] bereits exakt abgegrenzt; `05_stellenplan.py` öffnet das PDF direkt über `jahrgang.seitenbereiche["stellenplan"]` (wie `querschnitte.py` es für seinen Bereich tut), ganz ohne Seitentyp-Vokabular-Erweiterung in `[kopfzeilen.seitentypen]`.
**Warning signs:** Unnötige Änderung an `PFLICHT_SEITENTYPEN`/`2026.toml` für ein Problem, das der Seitenbereich bereits löst.

## Code Examples

### Erweiterung des bestehenden Personennamen-Tests auf App-Daten
```python
# Quelle: pipeline/tests/test_produkte.py:196-226 (gelesen in dieser Sitzung), Muster für
# eine Erweiterung (neue Testdatei test_app_daten.py oder Parametrisierung des Scans):
from ostbevern.konfiguration import PROJEKT_WURZEL

APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"

def test_keine_personennamen_in_app_daten(jahrgang, kontext) -> None:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        namen = lies_personennamen(dokument, jahrgang, seiten, hierarchie)
    nadeln = {text for _seite, text in namen} | {
        "".join(text.split()) for _seite, text in namen
    }
    for pfad in APP_DATEN_WURZEL.rglob("*.json"):
        inhalt = pfad.read_text(encoding="utf-8")
        for nadel in nadeln:
            assert nadel not in inhalt, f"{pfad}: Personenname gefunden"
```

### Regel-5-Toleranzkonstante getrennt von `TOLERANZ_EURO`
```python
# Quelle: Muster aus pipeline/ostbevern/investitionen.py:52 (_TOLERANZ_EURO = 1,
# eigenständig definiert "damit investitionen.py nicht von pruefung.py abhängt") —
# dasselbe Prinzip für Regel 5 in pruefung.py selbst, aber mit eigenem Namen:
REGEL5_TOLERANZ_POSTEN_T_EURO = 1      # Stufe (a): Summe vs. gedruckte Gesamtzeile, in T€
REGEL5_TOLERANZ_GEP_EURO = 1000        # Stufe (b): Gesamtzeile x1000 vs. GEP-Zeile, in €
```

### Platzhalter-Parser-Grundgerüst (D-15, fail-fast wie alle Extraktionsschritte)
```python
# Eigener Entwurf nach dem Fail-Fast-Prinzip aus D-08 (Phase 2) / D-08 (Phase 3):
import re

_PLATZHALTER_MUSTER = re.compile(r"\{\{([a-z0-9_.]+)\|([a-z]+)\}\}")

def loese_platzhalter_auf(text: str, werte: dict[str, int | float]) -> tuple[str, dict]:
    """Ersetzt jeden {{schluessel|format}}-Platzhalter; bricht bei unbekanntem Schlüssel ab
    (D-15: "Schritt 07 parst die Texte und prüft, dass jeder Schlüssel existiert, sonst
    bricht er ab")."""
    verwendete: dict[str, tuple[int | float, str]] = {}

    def _ersetze(treffer: re.Match[str]) -> str:
        schluessel, format_kuerzel = treffer.group(1), treffer.group(2)
        if schluessel not in werte:
            raise TexteFehler(f"Unbekannter Datenschlüssel: {schluessel!r}")
        verwendete[schluessel] = (werte[schluessel], format_kuerzel)
        return treffer.group(0)  # Rohtext bleibt erhalten; App ersetzt zur Laufzeit (D-15)

    _PLATZHALTER_MUSTER.sub(_ersetze, text)
    return text, verwendete
```

## State of the Art

Nicht anwendbar im klassischen Sinn (kein sich schnell änderndes externes Ökosystem). Die einzige relevante Verschiebung ist **intern**: Mit Phase 4 wird die Pipeline von einem reinen PDF→CSV-Extraktor zu einem PDF+Handdaten→App-JSON-Generator. Kein Alt-Muster wird abgelöst; alle Phase-2/3-Module bleiben wie sie sind.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | „Verbindlichkeiten aus Transferleistungen" (S. 310, Zeile 6) entspricht in voller Höhe (nicht nur näherungsweise) dem NRW.Bank-Anteil für Flüchtlingsunterkünfte in allen drei gedruckten Jahren (1.221/831/746 T€) | Pitfall 5 | Gering: Die Projektkonvention (D-14) behandelt diesen Wert ohnehin als „den von der Gemeinde selbst genannten" Pro-Kopf-Wert; selbst falls die Zeile geringfügig mehr als nur NRW.Bank-Mittel enthält, bleibt der Vorbericht die fachliche Quelle, nicht eine eigene Pipeline-Interpretation |
| A2 | Blockweite Fußnoten (z. B. S. 286 Matching-Verfahren-Hinweis) gehören ins README unter `daten/manuell/` bzw. `stellenplan`-README, nicht in eine CSV-Spalte | Pitfall 3 | Mittel: Falls der Plan stattdessen eine Freitext-Spalte je Block erwartet, ändert sich die Stellenplan-CSV-Struktur; Claude's Discretion laut CONTEXT.md deckt die genaue Spaltenliste aber ohnehin ab |
| A3 | `stellenplan.csv`-Teil „nachwuchskraefte" (S. 290) braucht eigene Spalten (`vorgesehen_2026`, `beschaeftigt_01_10_2025`), da Stichtag und Werttyp (Personen statt VZÄ) von Teil A/B abweichen | Pattern/Struktur | Gering: Reine Schemafrage, von Regel-5/Kreuzprüfungstests sofort sichtbar, falls falsch |

**Risiko-Einordnung:** Alle drei Annahmen sind strukturell, nicht fachlich — ein falscher Ansatz würde durch die eigenen Prüfregeln (Kreuzprüfung D-20, CI-Diff D-24) sofort als Testfehler sichtbar, nicht als stiller Datenfehler in der Bürgerinformation.

## Open Questions

1. **Exakte Formel für `verbindlichkeiten.csv`-Fortschreibung 2027–2029 (NRW.Bank-Anteil)**
   - What we know: Ende 2026 = 746 T€ ist gedruckt (Pitfall 5); D-14 sagt „konstant" für die Fortschreibung.
   - What's unclear: Ob „konstant bei 746 T€" oder „konstant bei 831 T€" gemeint war, als D-14 geschrieben wurde (die Formulierung in CONTEXT.md nennt nur 831 T€ als Beispiel für Ende 2025).
   - Recommendation: Plan sollte 746 T€ (letzter gedruckter Wert) als Fortschreibungssockel für 2027–2029 festlegen und dies explizit im README/`befunde.md` dokumentieren — ein Confirmation-Checkpoint mit dem Nutzer ist hier sinnvoll, da D-14 als „costly reversibility" (Satzungsnahe Zahl für STEL/INV-Seiten in Phase 6) markiert ist.

2. **Vermerke-Spalte vs. Block-Hinweis bei S. 285/286 (Sperrvermerk-Fall vs. Matching-Verfahren-Fall)**
   - What we know: S. 285 hat einen eindeutig zeilengebundenen Vermerk; S. 286 hat einen eindeutig blockweiten Hinweis.
   - What's unclear: Ob es Grenzfälle auf anderen, hier nicht gelesenen Seiten (ggf. keine weiteren im 7-Seiten-Bereich) gibt, die weder eindeutig zeilen- noch blockgebunden sind.
   - Recommendation: Der Executor sollte beim Parsen jede Zeile ohne Beträge nach der letzten Datenzeile eines Blocks explizit als „Hinweis" (nicht Vermerk) klassifizieren und bei Unsicherheit abbrechen (Fail-Fast-Prinzip, D-08-Stil), statt eine Heuristik zu raten.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pdfplumber (Python, via uv) | Stellenplan-Parser, manuelle Abschrift | ✓ | 0.11.10+ [VERIFIED: pipeline/pyproject.toml] | — |
| uv | Pipeline-Ausführung | ✓ (im Sandbox-Image, `uv run --directory pipeline` erfolgreich getestet) | — | — |
| poppler-utils (`pdftoppm`) | NICHT benötigt in dieser Phase (nur für Quellenbelege, Phase 7/DATA-04) | ✗ (in dieser Sandbox fehlend, während der Recherche festgestellt) | — | Kein Fallback nötig — außerhalb des Scopes dieser Phase |
| Node.js / npm | App-seitige TS-Typen (`typen.ts`), `type-check`/`lint`/`build` | ✓ (`app/.nvmrc`, `app/package-lock.json` vorhanden) | Node `^22.18.0` [VERIFIED: app/package.json] | — |
| GitHub Actions Runner | CI-Diff-Schritt (D-24) | ✓ (bestehender `pipeline`-Job) | — | — |

**Missing dependencies with no fallback:** keine (poppler-utils betrifft eine spätere Phase, nicht diese)
**Missing dependencies with fallback:** keine

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest ≥9.1.1 [VERIFIED: pipeline/pyproject.toml:14] |
| Config file | `pipeline/pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths=["tests"]`, `pythonpath=["."]`) |
| Quick run command | `uv run --directory pipeline pytest tests/test_manuell.py -x` (bzw. `test_stellenplan.py`/`test_app_daten.py`) |
| Full suite command | `uv run --directory pipeline pytest` |

Kein neues JS-Test-Framework nötig: `app/src/data/*.json` sind reine Build-Artefakte ohne Laufzeitlogik in dieser Phase; die bestehende App-CI (`type-check`, `lint`, `build`) deckt ab, dass `typen.ts` mit den erzeugten JSONs kompatibel bleibt (TypeScript-Typfehler bei Strukturabweichung), während der Personennamen-Scan und alle Inhaltsprüfungen in pytest laufen (siehe Don't Hand-Roll).

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MANU-01..05 | Manuelle CSVs haben korrekte Spalten, `quelle`, Werte lesbar | unit | `pytest tests/test_manuell.py -k schema -x` | ❌ Wave 0 |
| MANU-06 | `meta.json` Felder + Quelle vorhanden, Kreisumlage-brutto-Formel stimmt | unit | `pytest tests/test_manuell.py -k meta -x` | ❌ Wave 0 |
| MANU-07 | Jede manuelle Datei hat `quelle`-Spalte; README existiert und erwähnt jede Datei | unit | `pytest tests/test_manuell.py -k readme -x` | ❌ Wave 0 |
| MANU-08 | `erklaerungen.md`: keine nackten Ziffern (außer Jahr/§/Seite), jeder Platzhalter-Schlüssel existiert | unit | `pytest tests/test_texte.py -x` | ❌ Wave 0 |
| PRUEF-05 | Regel 5 Stufe (a)/(b) grün bzw. bekannte Befunde passen | integration | `pytest tests/test_manuell.py -k regel5` (ruft `pruefung.pruefe_alles` wie `test_pruefung.py`) | ❌ Wave 0 |
| EXTR-10 | `stellenplan.csv` Summenzeilen gegengeprüft, Kreuzprüfung PB-Übersicht = Teil A/B, Beamte 2026 = 8 | unit+integration | `pytest tests/test_stellenplan.py -x` | ❌ Wave 0 |
| DATA-01 | `app/src/data/*.json` existieren, sind valides JSON, keine Personennamen | unit | `pytest tests/test_app_daten.py -x` | ❌ Wave 0 |
| DATA-02 | KL-Knoten-Summe = TP 160101 Z. 15 je Jahr; PB-16-Rest = „Allgemeine Finanzwirtschaft" | unit | `pytest tests/test_app_daten.py -k kl_knoten` | ❌ Wave 0 |
| DATA-03 | Zuschussbedarf je Knoten = Formel; Summe Top-Knoten = GESAMT; `berechnet: true` gesetzt | unit | `pytest tests/test_app_daten.py -k zuschussbedarf` | ❌ Wave 0 |
| PRUEF-10 | `alle.py` läuft 01→07 ohne Fehler; danach kein `git diff` | integration (manuell, D-24 ist CI-seitig) | `uv run --directory pipeline python alle.py && git diff --exit-code -- daten app/src/data` | ✓ `alle.py` existiert, Schritte 05/07 fehlen noch |

### Sampling Rate
- **Per task commit:** gezielter `pytest tests/test_<modul>.py -x`
- **Per wave merge:** `uv run --directory pipeline pytest`
- **Phase gate:** Volle Pipeline-Suite grün, dann `uv run --directory pipeline python alle.py` lokal + `git diff --exit-code -- daten app/src/data` (simuliert D-24), zusätzlich `npm --prefix app run type-check` (prüft `typen.ts` gegen die neuen JSONs)

### Wave 0 Gaps
- [ ] `pipeline/tests/test_manuell.py` — deckt MANU-01..07, PRUEF-05
- [ ] `pipeline/tests/test_stellenplan.py` — deckt EXTR-10
- [ ] `pipeline/tests/test_texte.py` — deckt MANU-08
- [ ] `pipeline/tests/test_app_daten.py` — deckt DATA-01..03, erweitert Personennamen-Scan
- [ ] Erweiterung der bestehenden `conftest.py`-Fixtures (`jahrgang`, `pdf_klassifikation`) um ggf. eine `manuelle_daten`-Fixture, falls mehrere Testdateien dieselben CSVs lesen

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | nein | Kein Login, statische Site ohne Backend |
| V3 Session Management | nein | Keine Sessions |
| V4 Access Control | nein | Keine Zugriffsebenen; alle App-Daten sind öffentlich |
| V5 Input Validation | ja | Fail-Fast-Parsing (PDF-Text, manuelle CSVs, Platzhalter-Schlüssel) — jeder unbekannte/unplausible Wert bricht mit Seitenangabe ab (D-08-Muster), statt still einen Default zu setzen |
| V6 Cryptography | nein | Keine Kryptographie im Scope |

### Known Threat Patterns for {stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unbeabsichtigte Preisgabe von Personennamen in eingecheckten/ausgelieferten Dateien | Information Disclosure | Dreifachsicherung aus Phase 3 (D-09), erweitert auf `app/src/data/`: (1) Personenfelder werden nie in ein Dict/eine Datenklasse geschrieben, (2) Schema-Allowlist (`PRODUKT_SCHLUESSEL`) lehnt unerwartete Schlüssel ab, (3) `test_keine_personennamen`-Scan über alle Dateien unter `daten/` UND `app/src/data/` |
| Platzhalter-Injection in `erklaerungen.md` (ein falscher/böswilliger Schlüssel liefert einen unbeabsichtigten Wert) | Tampering | Strikte Allowlist-Validierung: jeder `{{schluessel|format}}` muss exakt in der von `07_app_daten.py` bereitgestellten Werttabelle existieren, sonst Abbruch (D-15) — kein dynamisches `eval`/Attributzugriff |
| Stille Datenkorruption durch Float-Rundung bei Geld-/Stellenwerten | Tampering (unbeabsichtigt) | Durchgängige int-Konvention (int-Euro, `stellen_hundertstel`), String-basiertes Parsing statt Float-Multiplikation (Pattern 2) |

## Sources

### Primary (HIGH confidence)
- `raw_data/haushalt-2026.pdf` S. 7–9 (Satzung §1–7), S. 24–25 (Rücklagen/Kredite/VE), S. 45–46 (Transferaufwendungen/Kita/Kreisumlage-Fußnote), S. 284–290 (Stellenplan/Stellenübersicht), S. 309–311 (VE-Übersicht, Verbindlichkeiten, Eigenkapital) — verbatim gelesen via `pdfplumber` in dieser Sitzung
- `pipeline/ostbevern/{schema,pruefung,konfiguration,zeilen,investitionen,spalten,zahlen,pdf,freitext,produkte}.py` — gelesen in dieser Sitzung
- `pipeline/jahrgaenge/{2026.toml,2026_sollwerte.toml}` — gelesen in dieser Sitzung
- `pipeline/tests/{conftest.py,test_rauchtest.py,test_alle.py,test_produkte.py}` — gelesen in dieser Sitzung
- `discussion/SPEZIFIKATION.md` §3, §4, §5.2, Anhang B.1–B.6 — gelesen in dieser Sitzung
- `.github/workflows/ci.yml`, `app/package.json`, `app/src/charts/format.ts`, `app/src/data/jahrgang.json` — gelesen in dieser Sitzung
- `.planning/{REQUIREMENTS.md,STATE.md}`, `.planning/phases/{04-manuelle-daten-und-app-daten/04-CONTEXT.md,03-details/03-CONTEXT.md,02-kernzahlen/02-CONTEXT.md}` — gelesen in dieser Sitzung

### Secondary (MEDIUM confidence)
— keine (keine Web-Recherche nötig, da die gesamte fachliche Grundlage im Repo liegt)

### Tertiary (LOW confidence)
— keine

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH – keine neuen Abhängigkeiten, alle Versionen direkt aus Projektdateien gelesen
- Architecture: HIGH – jedes Muster stammt aus bereits implementiertem, getestetem Code derselben Codebasis
- Pitfalls: HIGH für Stellenplan-/Satzungs-/NRW.Bank-Funde (verbatim PDF-Lektüre dieser Sitzung); MEDIUM für die Annahme, dass Zeile 6 (S. 310) vollständig dem NRW.Bank-Anteil entspricht (siehe Assumptions Log A1)

**Research date:** 2026-10-02
**Valid until:** Stabil bis zum nächsten Jahrgangswechsel (Haushalt 2027, ERW-03, v2) — keine zeitlich befristete externe Abhängigkeit
