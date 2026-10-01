# Ostbevern Money – Spezifikation

**Stand:** 01.10.2026
**Quelle:** `Haushalt 2026 komplett.pdf` (Gemeinde Ostbevern, 400 Seiten, erzeugt mit ProFIS+, Satzungsbeschluss vom 03.03.2026)
**Vorbild:** „Münster Money“, Münsterhack '26 – https://github.com/codeformuenster/haushalt-muenster-2026, live unter https://codeformuenster.org/haushalt-muenster-2026/#/

Dieses Dokument ist die Arbeitsgrundlage für die Umsetzung in Claude Code. Es beschreibt Ziel, Datenquelle, fachliche Fallstricke, Datenmodell, Extraktionspipeline, App-Seiten, Prüfregeln und Umsetzungsphasen. Die Zahlen in Anhang B sind aus dem PDF abgelesen und gegengerechnet. Sie dienen als Sollwerte für automatische Tests.

---

## 1. Ziel und Leitfragen

Eine statische Webanwendung erklärt den Bürgerinnen und Bürgern von Ostbevern den Haushalt 2026. Sie beantwortet zwei Leitfragen:

1. **Wo kommt das Geld der Gemeinde her?**
2. **Wofür wird es ausgegeben?**

Ergänzend soll die App zeigen:

- wie sich Einnahmen und Ausgaben von 2024 bis 2029 entwickeln,
- was investiert wird und wie das finanziert ist,
- worüber der Rat tatsächlich entscheiden kann (freiwillige gegenüber pflichtigen Aufgaben),
- spielerische Zugänge (Planspiel, Schätzduell, „Was kostet …?“).

### Nicht-Ziele (Version 1)

- Keine Haushalte anderer Jahre außer den Spalten, die im PDF 2026 stehen (Ist 2024, Ansatz 2025, Ansatz 2026, Planung 2027–2029).
- Kein Backend und keine Nutzerkonten. Alles ist statisch und läuft auf GitHub Pages.
- Keine tiefe Darstellung der Wirtschaftspläne von BBO (Bäder- und Beteiligungsgesellschaft) und TEO AöR (Abwasser). Sie werden nur als Hinweis erwähnt.
- Keine Darstellung der Fachbereichsbudgets (Anhang S. 377–400). Sie sind eine organisatorische Doppelung der Produktsicht.

---

## 2. Die Quelle: Aufbau des PDFs

**Seitennummern:** Im Hauptteil (bis S. 283) ist die PDF-Seite gleich der gedruckten Seitenzahl. Die Anlagen haben teils eine eigene Zählung. Im Code werden ausschließlich **PDF-Seiten** (1-basiert) verwendet.

| Kapitel | PDF-Seiten | Nutzen für die App |
|---|---|---|
| Leitbild | 6 | ggf. Startseite |
| Haushaltssatzung (Gesamtbeträge, Kredite, **Hebesätze** § 6) | 7–9 | Kennzahlen, Planspiel |
| Statistische Angaben (Fläche, Bevölkerung als Grafik, Schülerzahlen) | 10 | Kontext, Pro-Kopf-Werte |
| Vorbericht (Erläuterungen, **Tabellen nach Steuerart und Transferempfänger**) | 13–60 | Einnahmen-Detail, Transfers, Erklärtexte |
| **Gesamtergebnisplan** | 62 | Hauptsicht Ertrags- und Aufwandsarten |
| **Gesamtfinanzplan** | 63 | Zahlungsflüsse, Investitionen, Kredite |
| **Teilpläne**: Produktbereich → (Produktgruppe) → Produkt | 65–282 | Sicht nach Aufgaben, Produktinfos, Investitionen |
| Stellenplan und Stellenübersicht | 284–290 | Stellenplan-Seite |
| Haushaltsquerschnitte nach Produktbereichen | 291–300 | Kontrollsummen, nicht als Primärquelle |
| Ergebnis- und Finanzrechnung 2024, Bilanz 2024 | 301–306 | optional |
| Zuwendungen an Fraktionen | 307 | optional |
| Verpflichtungsermächtigungen, Verbindlichkeiten, Eigenkapital | 309–311 | Investitionen und Schulden |
| Wirtschaftspläne BBO und TEO AöR | 312–375 | nur Hinweis |
| Kostenstellenplan, Budgets nach Fachbereichen | 376–400 | nicht verwenden |

### 2.1 Gliederung der Teilpläne

- **15 Produktbereiche (PB):** 01–06 und 08–16. Es gibt keinen PB 07 (Gesundheit) und keinen PB 17 (Stiftungen).
- **63 Produkte** mit sechsstelligem Code (z. B. `030101`).
- **Produktgruppen (PG)** werden nur gedruckt, wenn eine Gruppe mehr als ein Produkt enthält (z. B. `0106`, `0110`, `0112`, `0301`, `0501`, `0602`, `0902`, `1201`). Sonst gilt: PG-Code = die ersten vier Ziffern des Produktcodes, PG-Name = Produktname. Die Pipeline muss die PG-Ebene deshalb **synthetisch ergänzen**.
- Die vollständige Liste mit Startseiten steht in **Anhang A**. Sie stammt aus dem Inhaltsverzeichnis (S. 2–5).

Typische Seitenfolge **je Produktbereich**:

1. Teilergebnisplan (aggregiert)
2. Teilfinanzplan (aggregiert)
3. „Investitionen“: Liste der Investitionsmaßnahmen aller Produkte des PB, über mehrere Seiten mit „Fortsetzung folgt . . .“

Typische Seitenfolge **je Produkt**:

1. **Produktinformationen** mit diesen Feldern:
   - Fachbereich, Verantwortliche/r, Sachbearbeiter/innen, Gremium
   - Produktbeschreibung, Leistungen (Aufzählung mit ``)
   - Auftragsgrundlage
   - **Bindungsgrad** (`pflichtig`, `freiwillig`, `teils pflichtig teils freiwillig`, `teils freiwillig teils pflichtig`); bei allen 63 Produkten vorhanden
   - Klassifizierung (`extern`, `intern`, `extern und intern`)
   - Zielgruppe, Ziele
   - **Grundzahlen**: Tabelle mit Einheit und Ist-Werten 2022–2025, z. B. Schüler/innen, Klassen, Steuerarten
2. **Teilergebnisplan**, danach Freitext „**Erläuterung zu Nr. …**“ mit Einzelposten in der Form `66.500 C Strom, Nahwärme, …`
3. **Teilfinanzplan**
4. **Investitionsmaßnahmen** des Produkts (dieselben Maßnahmen wie auf der PB-Ebene)

### 2.2 Spalten der Plantabellen

- **Ergebnisplan:** `Ergebnis 2024 | Ansatz 2025 | Ansatz 2026 | Planung 2027 | Planung 2028 | Planung 2029` (6 Werte)
- **Finanzplan und Investitionen:** `Ergebnis 2024 | Ansatz 2025 | Ansatz 2026 | VE 2026 | Planung 2027 | Planung 2028 | Planung 2029` (7 Werte; VE = Verpflichtungsermächtigung)
- „Ergebnis 2024“ ist laut Vorbericht ein **vorläufiges** Rechnungsergebnis.
- Das Eurozeichen wird als `C` ausgelesen („in C“, „66.500 C“).
- Zahlenformat deutsch: `1.234.567`, negative Werte mit `-`, gelegentlich `–` für „kein Wert“.

---

## 3. Fachliche Grundlagen und Fallstricke

Diese Punkte müssen Pipeline **und** App berücksichtigen.

### 3.1 Ergebnisplan oder Finanzplan

- **Ergebnisplan:** Erträge und Aufwendungen, also auch Buchungen ohne Geldfluss (Abschreibungen, Auflösung von Sonderposten). Er bestimmt, ob der Haushalt ausgeglichen ist. **Er ist die Hauptsicht der App** für „Woher“ und „Wofür“.
- **Finanzplan:** Ein- und Auszahlungen inklusive Investitionen und Krediten. Er wird für Investitionen, Kredite und Liquidität verwendet.
- Die beiden Pläne werden in einem Diagramm nie gemischt.
- Beispiel für die Abweichung: öffentlich-rechtliche Leistungsentgelte 2026 betragen im Ergebnisplan 2.390.607 €, im Finanzplan 1.927.222 €.

### 3.2 Zeilennummern unterscheiden sich zwischen Gesamt- und Teilplänen

| Inhalt | Gesamtergebnisplan | Teilergebnisplan |
|---|---|---|
| Ordentliche Erträge/Aufwendungen, Finanzergebnis, Jahresergebnis | 01–26 | 01–26 (identisch) |
| Globaler Minderaufwand | **27** | **30** |
| Ergebnis nach Minderaufwand | **28** | **31** |
| Erträge aus internen Leistungsbeziehungen | – | **27** |
| Aufwendungen aus internen Leistungsbeziehungen | – | **28** |
| Ergebnis mit inneren Verrechnungen | – | **29** |
| Verrechnung mit allgemeiner Rücklage (nachrichtlich) | 29–33 | – |

**Regeln:**

- Den Parser über **Zeilennummer + Plantyp** schlüsseln, nicht über den Zeilentext allein.
- **Interne Leistungsbeziehungen (TP 27/28) nie in Summen aufnehmen.** Ohne sie ergeben die Teilpläne exakt den Gesamtplan (geprüft).
- Teilpläne lassen **Zeilen mit dem Wert null weg** (z. B. fehlt Zeile 01 Steuern in fast allen PB). Fehlende Zeilen bedeuten 0, nicht „unbekannt“.

### 3.3 Globaler Minderaufwand

- Pauschal eingeplante Einsparung: 600.000 € im Jahr 2026.
- Steht im Gesamtplan (Z. 27) und anteilig in den Teilplänen (TP Z. 30).
- Die App zeigt Aufwendungen **vor** Minderaufwand und den Minderaufwand als eigenen, erklärten Posten.
- Das in der Satzung genannte Jahresergebnis −2.353.506 € ist der Wert **nach** Minderaufwand.

### 3.4 Kreisumlage: der wichtigste inhaltliche Unterschied zu Münster

- Ostbevern ist kreisangehörig (Kreis Warendorf). Allgemeine Kreisumlage und Jugendamtsumlage sind mit rund 38 % aller Aufwendungen der größte Posten.
- Der Ansatz 2026 im Haushalt beträgt **10.147 T€ netto**. Die Umlage selbst liegt bei rund 11,5 Mio. €, wird aber durch die Auflösung einer Rückstellung von 1.325.478 € entlastet (Vorbericht S. 46, Fußnote 3).
- Die Umlage ist im Produkt **160101 Allgemeine Finanzwirtschaft** (PB 16, Zeile 15 Transferaufwendungen) gebucht. Dort stehen auch Gewerbesteuerumlage (654 T€) und Krankenhausinvestitionsumlage (200 T€).
- Münster ist kreisfrei und hat diesen Posten nicht.

**Anforderung:** In allen Ausgabensichten wird aus PB 16 eine eigene Kategorie **„Weitergabe an Kreis und Land“** herausgelöst, mit Erklärtext:

- Kreisumlage: finanziert Aufgaben des Kreises, vor allem Soziales und Jugendamt
- Gewerbesteuerumlage
- Krankenhausinvestitionsumlage

Der Rest von PB 16 (Zinsen, Personal, Sonstiges) bleibt als „Allgemeine Finanzwirtschaft“ stehen.

### 3.5 Einnahmen liegen fast vollständig in PB 16

20,09 von 27,04 Mio. € ordentlichen Erträgen stehen in PB 16 (Steuern, Schlüsselzuweisung, Konzessionsabgaben). Eine Einnahmensicht nach Produktbereich wie in Münster ist deshalb wenig aussagekräftig. Die Einnahmenseite der App gliedert **nach Ertragsart und Steuerart**.

### 3.6 Sonderposten

„Auflösung von Sonderposten“ (2026 rund 0,9 Mio. € in Zeile 02, insgesamt rund 1,6 Mio. €) ist ein Ertrag **ohne Geldfluss**. Er verteilt früher erhaltene Investitionszuschüsse über die Nutzungsdauer. Die App erklärt das im Glossar und kennzeichnet den Posten.

### 3.7 Außerhalb des Kernhaushalts

- **Abwasser:** Abwasserbetrieb TEO AöR. Die Abwassergebühren erscheinen nicht im Haushalt. Die Gemeinde erhält eine Eigenkapitalverzinsung (2026 rund 300 T€, Zeile 19).
- **Hallenbad:** BBO. Im Haushalt erscheint nur der Verlustausgleich (2026: 270 T€; laut Wirtschaftsplan BBO faktisch 915 T€ inklusive Überschuss der Stadtwerke).
- Die App weist auf beides hin („Was nicht im Haushalt steht“).

### 3.8 Bekannte Datenauffälligkeiten

| Stelle | Befund | Umgang |
|---|---|---|
| Vorbericht S. 46, Transfertabelle | Im Text „10.1473“: Fußnotenziffer 3 klebt an 10.147 | in der manuellen CSV korrigieren, Fußnote als Anmerkung |
| Vorbericht S. 28, Zuwendungen | Summe 3.109 T€ (Einzelwerte 890 + 1.323 + 895 = 3.108) gegenüber Gesamtergebnisplan Z. 02: 3.113.200 € | Gesamtplan ist maßgeblich; Differenz von rund 4 T€ in `befunde.md` dokumentieren und in der App als „Sonstige“ ausweisen |
| Investitionsmaßnahmen | stehen dreifach im PDF: PB-Liste, Produktseite, Fachbereichsbudget | **nur aus den Produktseiten** extrahieren, mit der PB-Liste abgleichen |
| Investitionszeilen | Kontobezeichnung klebt an der ersten Zahl („…/Fzg.50.126“), mehrzeilige Bezeichnungen („über 800\nEUR“) | Spalten über x-Koordinaten bestimmen (siehe 5.3) |
| Investitionen mit VE | Zusatzzeile `(Kassenwirksamkeit) (2.000.000) – –` | als Fälligkeit der VE erkennen, nicht als Betrag summieren |
| Einwohnerzahl | Vorbericht S. 24/25: 11.741 (IT.NRW, 30.06.2024); Grafik S. 10 endet bei 11.469 | **offen** (Abschnitt 10); Wert in `meta.json` konfigurierbar |
| Querschnitte S. 291 ff. | Im Textauslesen laufen Zeilen ineinander | nur als Kontrolle, mit pdfplumber über Koordinaten |
| Grundzahlen „Ist 2025“ | Stichtag uneinheitlich („Stand 30.06.“ bzw. „Stand Ende 2025“) | Hinweis aus dem PDF übernehmen |

---

## 4. Datenmodell

Alle aufbereiteten Daten liegen im **Langformat**: eine Zeile je Wert. Das ist für polars und pandas gut zu verarbeiten, und die App erzeugt daraus ein kompaktes JSON. Beträge werden in **ganzen Euro (int)** gespeichert. Jede Zeile trägt `pdf_seite` für Quellenbelege.

### 4.1 Gemeinsame Felder

| Feld | Typ | Beispiel |
|---|---|---|
| `jahr` | int | 2026 |
| `wertart` | enum | `ergebnis` (Ist 2024), `ansatz` (2025, 2026), `planung` (2027–2029), `ve` (Verpflichtungsermächtigung 2026) |
| `betrag` | int | 2060000 |
| `pdf_seite` | int | 62 |

### 4.2 Dateien in `daten/aufbereitet/`

**`hierarchie.csv`** – eine Zeile je Knoten

```
ebene,code,name,eltern_code,pdf_seite_start
PB,03,Schulträgeraufgaben,,145
PG,0301,Schulische Einrichtungen und schülerbezogene Leistungen,03,150
P,030101,Ambrosius-Grundschule,0301,151
```

- Synthetische PG (siehe 2.1) erhalten `synthetisch=true`.
- Produktnamen aus dem Inhaltsverzeichnis sind teils in GROSSBUCHSTABEN. Den Namen aus der Produktseite nehmen; dort ist er normal geschrieben.

**`produkte.json`** – Produktinformationen je Produkt

```json
{
  "code": "030101",
  "name": "Ambrosius-Grundschule",
  "pb": "03", "pg": "0301",
  "fachbereich": "Fachbereich I/Schulen",
  "verantwortlich": "…",
  "gremium": "Bildungs-, Generationen- und Sozialausschuss",
  "beschreibung": "…",
  "leistungen": ["Betrieb der Ambrosius-Grundschule", "…"],
  "auftragsgrundlage": "…",
  "bindungsgrad": "teils",
  "bindungsgrad_original": "teils pflichtig teils freiwillig",
  "klassifizierung": "extern",
  "zielgruppe": "…",
  "ziele": "…",
  "erlaeuterungen": [
    {"zu_zeilen": [13, 16], "betrag": 66500, "text": "Strom, Nahwärme, Wasser, Abwasser"}
  ],
  "pdf_seiten": [151, 152, 153, 154]
}
```

- `bindungsgrad` wird normalisiert auf `pflichtig | freiwillig | teils`.
- **Datenschutz:** Namen von Mitarbeitenden (Verantwortliche/r, Sachbearbeiter/innen) werden extrahiert, aber **nicht in die App ausgeliefert**. Die App zeigt nur Fachbereich und Gremium.

**`grundzahlen.csv`** – Kennzahlen je Produkt

```
produkt,bezeichnung,einheit,jahr,wert,hinweis,pdf_seite
030101,Schüler/innen,Anz.,2024,342,"Schuljahr 2024/2025",151
160101,Gewerbesteuer (Im Teilplan Zeile 01),EUR,2023,4771497,,280
```

**`ergebnisplan.csv`** – Gesamtplan und alle Teilpläne

```
ebene,code,zeile,zeile_name,jahr,wertart,betrag,pdf_seite
GESAMT,,01,Steuern und ähnliche Abgaben,2026,ansatz,18443000,62
PB,01,13,Aufwendungen für Sach- und Dienstleistungen,2026,ansatz,924950,66
P,030101,13,Aufwendungen für Sach- und Dienstleistungen,2026,ansatz,342400,152
```

- `zeile` ist die Nummer **im jeweiligen Plantyp** (siehe 3.2). Zusätzlich gibt es eine Spalte `zeile_kanonisch` mit einheitlichen Schlüsseln wie `steuern`, `zuwendungen`, …, `globaler_minderaufwand`, `interne_ertraege`.
- Summenzeilen (10, 17, 18, 21, 22, 26, 28/29/31) werden mit extrahiert, um sie zu prüfen, und mit `ist_summe=true` markiert.

**`finanzplan.csv`** – gleiches Schema, Gesamt- und Teilfinanzpläne, inklusive `wertart=ve`.

**`investitionen.csv`**

```
produkt,massnahme_id,massnahme_name,konto,konto_name,richtung,jahr,wertart,betrag,pdf_seite
030101,AIB00001,Baumaßnahmen an der Ambrosius-Grundschule,785111,Auszahl. f. d. Abwickl. Hochbaumaßnahmen,auszahlung,2026,ansatz,2000000,153
```

- `richtung` ist `einzahlung` oder `auszahlung`.
- Die Kontoklasse ergibt sich aus der ersten Ziffer: 6 = Einzahlung, 7 = Auszahlung.
- Die Fälligkeiten von VE aus „(Kassenwirksamkeit)“ landen in einer eigenen Datei `ve_faelligkeiten.csv`.

**`stellenplan.csv`**

```
teil,gruppe,produktbereich,jahr,stellen,pdf_seite
beamte,A 14,,2026,2.0,284
tarif,EG 9a,01,2026,…,288
```

- Teil A, Beamte (S. 284) und Teil B, Tarif (S. 285 ff.): Stellen 2026 und 2025 sowie besetzte Stellen am 30.06.2025.
- Stellenübersicht Teil A nach Produktbereichen (S. 287–289).
- Vermerke („künftig wegfallend“, „Sperrvermerk“) kommen in eine eigene Spalte.

### 4.3 Manuell gepflegte Tabellen in `daten/manuell/`

Diese Werte stehen nur im Fließtext oder in kleinen Vorberichtstabellen. Sie werden einmal abgeschrieben und **automatisch gegen die Planwerte geprüft**. Jede Datei hat eine Spalte `quelle` mit der PDF-Seite und ein README mit Begründung, wie in Münster.

| Datei | Inhalt | Quelle | Prüfung gegen |
|---|---|---|---|
| `steuerarten.csv` | Grundsteuer A/B, Gewerbesteuer, Einkommensteuer-Anteil, Umsatzsteuer-Anteil, Vergnügungssteuer, Hundesteuer, Kompensationszahlungen; 2024–2029 in T€ | Vorbericht 2.1.1, S. 27 | Summe = Gesamtergebnisplan Z. 01 (Toleranz ±1 T€ je Jahr) |
| `zuwendungen.csv` | Schlüsselzuweisung, Zuweisungen für laufende Zwecke, Auflösung von Sonderposten | Vorbericht 2.1.2, S. 28 | Z. 02 (bekannte Differenz, siehe 3.8) |
| `transferaufwendungen.csv` | Wasser- und Bodenverband, Kitas, Kinder- und Jugendwerk, Offener Ganztag, Zuschüsse, Sozialleistungen, Gewerbesteuerumlage, Krankenhausinvestitionsumlage, Kreisumlage (netto, mit Fußnote), Verlustübernahme BBO | Vorbericht 2.2.5, S. 45–46 | Summe = Z. 15 |
| `kita_zuschuesse.csv` | Trägeranteil je Kita (7 Einrichtungen, Summe 559 T€) | S. 46 | = Zeile „Zuschüsse an Kindertageseinr.“ |
| `weitere_vorberichtstabellen.csv` | Leistungsentgelte (2.1.4), Kostenerstattungen (2.1.6), Personal (2.2.1), Sachaufwand (2.2.3), Sonstige Aufwendungen (2.2.6) | S. 29–50 | jeweilige Zeile des Gesamtplans |
| `meta.json` | Einwohnerzahl (mit Stichtag und Quelle), Hebesätze (A 242 %, B 554 %, Gewerbesteuer 418 %), Fläche 89,6 km², Satzungsdatum, Kreisumlage brutto/netto, Hebesätze der Kreisumlage (36,3 % / 21 %) | S. 8–10, 24, 46 | – |
| `texte/erklaerungen.md` | kurze, geprüfte Erklärtexte aus dem Vorbericht, z. B. Einbruch der Schlüsselzuweisung, Schwankung der Gewerbesteuer, Entwicklung der Kreisumlage | Vorbericht | – |

Für die Steuern gibt es zusätzlich **Ist-Werte 2022–2025** aus den Grundzahlen von Produkt 160101 (S. 280). Sie werden automatisch extrahiert, nicht manuell abgeschrieben.

### 4.4 App-Daten in `app/src/data/`

Ein Build-Skript erzeugt aus `daten/aufbereitet/` und `daten/manuell/` diese Dateien:

- `haushalt.json`: Hierarchie, Ergebniswerte je Knoten (Zeilen 01–17, 19, 20, 30 für alle Jahre), kanonische Kategorien inklusive „Weitergabe an Kreis und Land“, Steuerarten, Zuwendungen, Transferaufschlüsselung, Meta-Daten
- `produkte.json`: ohne Personennamen
- `investitionen.json`
- `stellenplan.json`
- `planspiel.json`: Hebel und Basiswerte, siehe 6.7
- `quellen.json`: Schlüssel → `{pdf_seite, bbox, bild}` für die Quellenleiste

Die Struktur von `planspiel.json` soll sich möglichst an Münsters `planspiel.json` anlehnen: `zeilen[]`, `gesamt{jahr: []}`, `produktbereiche[]`, `produktgruppen[{code, name, werte{jahr: []}}]`. So lassen sich die Komponenten übernehmen.

---

## 5. Extraktionspipeline (Python)

### 5.1 Werkzeuge

- Python ≥ 3.12, **uv** als Projekt- und Abhängigkeitsverwaltung, wie in Münster
- `pdfplumber` (Wörter mit Koordinaten), `polars`, `typer` (Kommandozeile), `pytest`
- optional `pypdfium2` oder `pdftoppm` zum Rendern der Quellenbelege als WebP

### 5.2 Ablauf

```
uv run pipeline/01_seiten_klassifizieren.py   # PDF-Seite -> Typ, PB, Produkt
uv run pipeline/02_plaene_extrahieren.py      # Gesamt- und Teilpläne -> ergebnisplan.csv, finanzplan.csv
uv run pipeline/03_produktinfos.py            # Produktinformationen, Grundzahlen, Erläuterungen
uv run pipeline/04_investitionen.py           # Investitionsmaßnahmen, VE-Fälligkeiten
uv run pipeline/05_stellenplan.py
uv run pipeline/06_pruefen.py                 # Konsistenzprüfung -> daten/pruefberichte/konsistenz.md
uv run pipeline/07_app_daten.py               # JSON für die App
uv run pipeline/08_quellenbelege.py           # Seitenbilder + quellen.json (bei Bedarf)
uv run pipeline/alle.py                       # 01–07 in Reihenfolge
```

### 5.3 Seitenklassifikation (Schritt 01)

Jede Seite wird anhand der Kopfzeilen eingeordnet:

- `Produktbereich <NN> <Name>`, optional `Produkt <NNNNNN> <Name>`
- danach eine der Überschriften `Produktinformationen`, `Teilergebnisplan`, `Teilfinanzplan`, `Investitionen` oder `Investitionsmaßnahmen (in C)`

Ergebnis ist `daten/zwischen/seiten.csv` (`pdf_seite, typ, pb, pg, produkt`). Fortsetzungsseiten („Fortsetzung folgt . . .“) übernehmen den Kontext der vorherigen Seite.

**Akzeptanz:** Die Startseiten aller 63 Produkte stimmen mit Anhang A überein.

### 5.4 Planzeilen parsen (Schritt 02)

- Zeilen haben die Form `<NN> <Operator?> <Bezeichnung> <6 oder 7 Zahlen>`.
- Die Zahlen werden **von rechts** gelesen: Die letzten 6 bzw. 7 Token sind Beträge. Klebt ein Betrag an der Bezeichnung, trennt ein Regex am Übergang Buchstabe/Punkt → Ziffer.
- Robuster ist die Spaltenzuordnung über die x-Koordinaten der Spaltenköpfe (`Ergebnis 2024`, `Ansatz 2025`, …) mit `pdfplumber.extract_words()`. **Dieser Weg ist bevorzugt**, auch für Investitionen und Stellenplan.
- Bei Teilplänen mit Fortsetzung („Nr.“-Kopf auf der Folgeseite) wird über die Seiten fortgesetzt.

### 5.5 Prüfregeln (Schritt 06)

Alle Prüfungen laufen in `pytest` **und** erzeugen einen Markdown-Bericht. Abweichungen über 1 € sind Fehler, außer sie sind in `befunde.md` als bekannt dokumentiert.

1. **Zeilenformeln** je Plan: Z. 10 = Summe 01–09; Z. 17 = Summe 11–16; Z. 18 = 10 − 17; Z. 21 = 19 − 20; Z. 22 = 18 + 21; Z. 26 = 22 + 25. Finanzplan: Z. 09, 16, 17, 23, 30, 31, 32, 37, 38.
2. **Produkte → PG → PB:** Die Summe der Produkt-Teilpläne ergibt den PB-Teilplan, je Zeile und Jahr.
3. **PB → Gesamt:** Die Summe der 15 PB ergibt den Gesamtergebnisplan (Z. 01–17, 19, 20; ohne TP 27/28). Für 2026 bereits geprüft: Erträge 27.042.063 €, Aufwendungen 30.255.569 €.
4. **Satzung:** Erträge gesamt (Z. 10 + 19) = 27.502.063 €; Aufwendungen gesamt (Z. 17 + 20) = 30.455.569 €; Finanzplan-Summen laut § 1 (Anhang B).
5. **Manuelle Tabellen** gegen Planzeilen (4.3).
6. **Investitionen:** Summe der Maßnahmen je Produkt = Teilfinanzplan Z. 23 bzw. 30; Summe aller Maßnahmen = Gesamtfinanzplan Z. 23/30 (2026: 7.224.830 € / 12.280.484 €).
7. **Querschnitte (S. 291 ff.):** Werte je PG gegen die eigenen Aggregate (Kontrolle der Extraktion).
8. **Vollständigkeit:** 63 Produkte mit Produktinformationen, Bindungsgrad, Teilergebnisplan und Teilfinanzplan.

### 5.6 Quellenbelege

Wie in Münster (`quellen.py`): Zu Werten, die die App prominent zeigt, wird die Zeile im PDF gesucht. Ihr Rechteck wird gespeichert und die Seite als WebP gerendert (2 px je PDF-Punkt, Qualität 60). Die App öffnet den Beleg in einer Seitenleiste („Quelle anzeigen“).

---

## 6. Die App

### 6.1 Technik

- **Übernahme des Münster-Stacks:** Vue 3, TypeScript, Vite, Web Awesome (UI), ECharts über `vue-echarts`, Hash-Router, Deployment über GitHub Actions auf GitHub Pages
- Wiederverwendbare Komponenten aus Münster (vorbehaltlich Lizenzklärung, Abschnitt 10):
  - `PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`
  - `GlossarBegriff`, `BegriffeListe`, `ProduktAkkordeon`, `QuelleSeitenleiste`
  - `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts`
  - die Sankey-Komponente als Ausgangspunkt
- Die App liest nur die generierten JSON-Dateien. Es gibt keine CSV-Verarbeitung im Browser (Münster parst teils CSV zur Laufzeit; das entfällt hier).
- Sprache: Deutsch, einheitliche Anrede (offen: „du“ oder „Sie“, Abschnitt 10).
- Barrierefreiheit wie in Münster: Fokussteuerung beim Routenwechsel, ausreichende Kontraste, Tabellenalternative zu jedem Diagramm, `prefers-reduced-motion`.
- Responsiv ab 360 px Breite.

### 6.2 Seitenübersicht

| Route | Seite | Leitfrage | Pendant in Münster |
|---|---|---|---|
| `/` | Start | Einstieg, Kennzahlen | Start |
| `/einnahmen` | **Woher kommt das Geld?** | 1 | (neu; in Münster nur im Sankey) |
| `/ausgaben` | **Wofür wird es ausgegeben?** | 2 | Überblick |
| `/geldfluss` | Geldfluss (Sankey) | 1 + 2 | Ein- & Ausgaben |
| `/entwicklung` | Entwicklung 2024–2029 | Kontext | (neu) |
| `/investitionen` | Investitionen und Schulden | Kontext | ersetzt „Bezirke“ |
| `/rat-entscheidet` | Worüber entscheidet der Rat? | Kontext | ersetzt „Zuschüsse“ |
| `/planspiel` | Planspiel: Bring das Minus auf null | Spiel | Planspiel |
| `/was-kostet` | Was kostet …? | Spiel | 1 Mio. € |
| `/schaetzduell` | Schätzduell | Spiel | Mehr oder weniger |
| `/stellenplan` | Wer arbeitet für die Gemeinde? | Kontext | Stellenplan |
| `/glossar` | Glossar und alle Produkte | Hilfe | Glossar |

### 6.3 Start (`/`)

- **Kennzahlenband 2026:**
  - Erträge 27,5 Mio. €, Aufwendungen 30,5 Mio. €, Defizit 2,35 Mio. € (nach Minderaufwand)
  - Investitionen 12,3 Mio. €, neue Kredite 5,2 Mio. €
  - pro Einwohner: Aufwand ≈ 2.594 €, Steuern ≈ 1.571 € (bei 11.741 Einwohnern)
- Zwei große Einstiegskacheln zu den Leitfragen
- Kurzer Hinweis auf die Kreisumlage als größten Posten
- Teaser für Planspiel und Schätzduell

### 6.4 Woher kommt das Geld? (`/einnahmen`)

**Ebene 1:** Ertragsarten 2026 als horizontale Balken oder Donut mit Prozentanteil:

| Ertragsart | Mio. € |
|---|---|
| Steuern | 18,44 |
| Zuwendungen | 3,11 |
| Öffentlich-rechtliche Entgelte | 2,39 |
| Sonstige ordentliche Erträge | 1,94 |
| Kostenerstattungen | 0,76 |
| Finanzerträge | 0,46 |
| Privatrechtliche Entgelte | 0,39 |

**Ebene 2:** Ein Klick öffnet die Aufschlüsselung:

- **Steuern:**
  - Gewerbesteuer 7,80 · Einkommensteuer-Anteil 6,83 · Grundsteuer B 2,06 · Umsatzsteuer-Anteil 0,89 · Kompensation 0,66 · Grundsteuer A 0,09 · Hundesteuer 0,07 · Vergnügungssteuer 0,06 (Mio. €)
  - Hebesätze anzeigen (B 554 %, Gewerbesteuer 418 %)
  - Erklärung, welche Steuern die Gemeinde selbst festlegt (Grund-, Gewerbe-, Hunde- und Vergnügungssteuer) und welche Anteile an Bundes- und Landessteuern sind
- **Zuwendungen:** Schlüsselzuweisung, Zuweisungen für laufende Zwecke (mit Beispielen aus dem Vorbericht: Offener Ganztag, Infrastrukturpauschale), Sonderposten (Hinweis: kein Geldfluss)
- **Sonstige ordentliche Erträge:** Konzessionsabgaben (Strom, Gas, Wasser aus den Grundzahlen 160101) und weitere, soweit belegbar

**Ebene 3, Zeitreihe je Steuerart 2022–2029:** Ist 2022–2024 aus den Grundzahlen, 2025–2029 aus der Vorberichtstabelle. Ist- und Planwerte sind visuell unterscheidbar (durchgezogen oder gestrichelt). Erklärtexte:

- Gewerbesteuer: 2023 Einbruch auf 4,8 Mio. €, starke Schwankungen
- Schlüsselzuweisung: sinkt 2026 auf 890 T€, **weil** die Gewerbesteuer 2024 hoch war

**Investive Einnahmen** stehen separat und klar abgegrenzt („fließen nicht in den laufenden Haushalt“):

- Investitionspauschale 1,53 Mio. €, Schulpauschale 0,41 Mio. €, Sportpauschale 0,06 Mio. €
- Grundstücksverkäufe 2,25 Mio. €, Beiträge 1,24 Mio. €
- Kredite 5,2 Mio. €

### 6.5 Wofür wird es ausgegeben? (`/ausgaben`)

- **Hauptdiagramm:** Kacheldiagramm (Treemap) der ordentlichen Aufwendungen 2026 mit Drilldown Aufgabenbereich → Produktgruppe → Produkt.
  - „Weitergabe an Kreis und Land“ ist eine eigene Top-Kachel (siehe 3.4), farblich abgesetzt und mit Info-Callout.
  - „Globaler Minderaufwand“ wird nicht als Kachel gezeigt, sondern als Hinweis unter dem Diagramm.
- **Umschalter Kennzahl:**
  - „Aufwand“ (brutto)
  - „Zuschussbedarf“ (Aufwand − Erträge des Produkts, also was aus Steuern finanziert werden muss). Bei einem Überschuss erscheint ein eigener Hinweis.
- **Zweite Sicht, nach Aufwandsart:** Transferaufwendungen 13,76 / Sach- und Dienstleistungen 7,02 / Personal 5,20 / Abschreibungen 2,76 / Sonstige 1,25 / Versorgung 0,26 / Zinsen 0,20 (Mio. €).
  - Transferaufwendungen aufklappbar mit der Tabelle aus dem Vorbericht: Kreisumlage, Offener Ganztag, Kitas (einzeln), Kinder- und Jugendwerk, Gewerbesteuerumlage, Asylbewerberleistungen, BBO, …
  - Abschreibungen mit Hinweis „Wertverlust von Gebäuden und Straßen, kein Geldfluss“
- **Produktdetail** (Klick auf ein Produkt):
  - Beschreibung, Leistungen, Bindungsgrad, Gremium
  - Mini-Tabelle des Teilergebnisplans 2024–2029
  - Erläuterungsposten (z. B. „84.900 € Reinigung“)
  - Grundzahlen mit abgeleiteten Pro-Kopf-Werten, z. B. Zuschussbedarf je Schüler/in (berechnet, nicht im PDF; so kennzeichnen)
  - Investitionen des Produkts
  - Quellenlink

### 6.6 Geldfluss (`/geldfluss`)

Sankey 2026 (Ergebnisplan):

- **Links:** Ertragsarten. Steuern sind in Steuerarten aufgeteilt (Gewerbesteuer, Einkommensteuer, Grundsteuer, übrige). Daneben Schlüsselzuweisung, sonstige Zuwendungen, Gebühren und Entgelte, Sonstige, Finanzerträge.
- **Mitte:** Knoten „Gemeindehaushalt“.
- **Rechts:** „Weitergabe an Kreis und Land“, die Aufgabenbereiche (PB ohne Umlagen) und Zinsen.
- **Ausgleich:** Damit der Sankey bilanziert, steht links ein Knoten **„Defizit (Entnahme aus Rücklagen)“** mit 2,35 Mio. € und rechts der Minderaufwand als Gegenposten. Das Ganze ist erklärt.
- **Interaktion:** Hover hebt Pfade hervor, Klick auf einen Aufgabenbereich führt zur Ausgabenseite.
- Auf schmalen Bildschirmen wird statt des Sankeys eine Tabelle oder gestapelte Balken gezeigt (Münster hat das bereits gelöst).

### 6.7 Planspiel (`/planspiel`)

- **Ziel:** Das Jahresergebnis 2026 von −2.353.506 € auf mindestens 0 bringen.
- **Aufbau:** Hebel als Karten in vier Gruppen wie in Münster: Mehr einnehmen / Sparen / Mehr ausgeben / Schulden und Investitionen.
- Jede Karte zeigt:
  - die Wirkung in €
  - eine Einordnung (Vergleichswerte mit Quellenbeleg)
  - die Folgen in Klartext

| Hebel | Basis (2026) | Rechenregel (vereinfacht) |
|---|---|---|
| Grundsteuer-B-Hebesatz | 2.060.000 € bei 554 % | ≈ 3.718 € je Hebesatzpunkt. Zusätzlich: Mehrbelastung pro Haushalt grob schätzen (optional, Annahmen offenlegen) |
| Gewerbesteuer-Hebesatz | 7.800.000 € bei 418 % | ≈ 18.660 € je Punkt. Die Gewerbesteuerumlage hängt am Grundbetrag und steigt nicht mit; Kreisumlage und Schlüsselzuweisung rechnen mit fiktiven Hebesätzen (GFG NRW). **Fachlich verifizieren**, im Spiel als „vereinfacht“ kennzeichnen |
| Hundesteuer | 66.000 € | prozentuale Erhöhung |
| Hallenbad / BBO-Verlustausgleich | 270.000 € | Eintrittspreise erhöhen oder Öffnungszeiten kürzen, prozentual |
| Freiwillige Aufgaben kürzen | Summe des Zuschussbedarfs aller Produkte mit Bindungsgrad „freiwillig“ | prozentuale Kürzung |
| Wiederbesetzungssperre | Personalaufwand 5.204.054 € | x % |
| Gebäudeunterhaltung aufschieben | Erläuterungsposten Unterhaltung (Summe aus Produkterläuterungen) | x %, Folge: Sanierungsstau |
| Kreisumlage senken | 10.147.000 € | **nicht möglich**, Info-Karte: Die Höhe legt der Kreis fest |
| Grundstücke verkaufen | 2.245.830 € im Finanzplan | Info-Karte: verbessert die Liquidität, **nicht** das Ergebnis |
| Mehr ausgeben (z. B. Kita-Zuschüsse, Vereinsförderung) | Vorberichtswerte | negative Wirkung |

- **Anzeige:** Fortschrittsbalken bis zum Ausgleich, Liste der getroffenen Entscheidungen, „Zurücksetzen“, Teilen per URL-Parameter (Zustand im Hash).

### 6.8 Was kostet …? (`/was-kostet`)

- Betrag wählbar, Standard **100.000 €**, Auswahl 50.000 / 100.000 / 250.000 / 500.000 / 1 Mio. €.
- Gezeigt wird, welche Produkte sich mit dem Betrag ein Jahr lang finanzieren ließen (Zuschussbedarf ≤ Betrag) und welchen Anteil der Betrag an größeren Produkten deckt.
- Zusätzliche Vergleiche, z. B. „= x € je Einwohner“ und „= y Hebesatzpunkte Grundsteuer B“.

### 6.9 Schätzduell (`/schaetzduell`)

- Logik aus Münster `lib/mehrOderWeniger.ts`: Paare von Produkten mit Zuschussbedarf > 0, Mindestfaktor zwischen beiden, eine Serie zählt richtige Antworten.
- Datenbasis: 63 Produkte. „Allgemeine Finanzwirtschaft“ und Produkte mit Überschuss sind ausgeschlossen.
- Klick auf einen Produktnamen zeigt die Produktinfo.

### 6.10 Investitionen und Schulden (`/investitionen`)

- **Liste und Balken** der Investitionsmaßnahmen 2026–2029, filterbar nach Aufgabenbereich und Art (Bau, Grundstücke, Fahrzeuge und Ausstattung). Gezeigt werden die größten Maßnahmen, z. B. Schulbaumaßnahmen Ambrosius-, Franz-von-Assisi- und Josef-Annegarn-Schule, Feuerwehrgerätehaus Brock, Baugebiet Kohkamp III.
- **Verpflichtungsermächtigungen:** 11,6 Mio. € mit Fälligkeiten (S. 25, S. 309).
- **Finanzierung:** Investitionseinzahlungen (Zuweisungen, Verkäufe, Beiträge), dazu Kredite. Zeitreihe Kreditaufnahme und Tilgung 2024–2029.
- **Schuldenstand** (S. 24/25, S. 310): rund 7,7 Mio. € Ende 2025, ≈ 656 € je Einwohner.
- Optional: Kennzeichnung „Ortsteil Brock“ für Maßnahmen, die Brock im Namen tragen (einfacher Textfilter).

### 6.11 Worüber entscheidet der Rat? (`/rat-entscheidet`)

- **Hauptdiagramm:** Zuschussbedarf 2026, aufgeteilt nach Bindungsgrad (pflichtig / teils / freiwillig) als gestapelter Balken. Darunter die Produkte je Kategorie.
- **Zusatzblock „Was der Rat nicht beeinflussen kann“:** Kreisumlage, Gewerbesteuerumlage, gesetzliche Sozialleistungen.
- **Einzelzuschüsse aus dem Vorbericht:**
  - Kita-Träger (einzeln), Kinder- und Jugendwerk, Offener Ganztag, kulturtragende Vereine (23 T€)
  - VHS (5 T€), Sportförderung (28 T€), Musikschule (JeKits 8 T€) usw.
- **Hinweis:** Der Bindungsgrad ist eine Selbstauskunft der Verwaltung je Produkt. Auch in pflichtigen Produkten gibt es Gestaltungsspielraum bei der Höhe.

### 6.12 Entwicklung 2024–2029 (`/entwicklung`)

- Linien für Erträge, Aufwendungen und Jahresergebnis 2024–2029 (Ist / Ansatz / Planung unterscheidbar). Das Defizit wächst bis 2029 auf −3,56 Mio. €.
- Zeitreihe ausgewählter Posten: Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen.
- Ausgleichsrücklage und allgemeine Rücklage (S. 311): Wie lange reicht das Polster?

### 6.13 Stellenplan (`/stellenplan`)

- Kennzahlen: Stellen gesamt 2026 (Beamte 8, Tarif und Sozial- und Erziehungsdienst laut S. 285–289) gegenüber 2025 und gegenüber besetzten Stellen am 30.06.2025.
- Verteilung nach Aufgabenbereich (Stellenübersicht Teil A) und nach Entgelt- bzw. Besoldungsgruppe.
- Personalaufwand je Aufgabenbereich aus den Teilplänen (Z. 11) daneben.
- Bewusst einfacher als der Münster-Stellenatlas: keine Gehaltsschätzung in Version 1.

### 6.14 Glossar (`/glossar`)

- Begriffe, mindestens: Ergebnisplan, Finanzplan, Ertrag/Aufwand, Ein-/Auszahlung, Produkt, Produktbereich, Transferaufwendungen, Kreisumlage, Jugendamtsumlage, Gewerbesteuerumlage, Schlüsselzuweisung, Hebesatz, Sonderposten, Abschreibungen, globaler Minderaufwand, Ausgleichsrücklage, allgemeine Rücklage, Verpflichtungsermächtigung, Bindungsgrad, Zuschussbedarf, NKF, Haushaltssicherung.
- Darunter alle 63 Produkte mit Beschreibung (Akkordeon, wie Münster `ProduktAkkordeon`).
- `GlossarBegriff`-Links aus allen Seiten.

### 6.15 Gemeinsame UI-Elemente

- Jahr-Umschalter (2024 Ist … 2029 Planung) auf Ausgaben, Einnahmen und Geldfluss; Standard ist 2026.
- „Quelle anzeigen“ an allen Kennzahlen und Tabellenzeilen mit Beleg.
- Fußzeile mit Stand der Daten, Link zum Original-PDF der Gemeinde, Hinweis „inoffizielles Projekt“ und Kontakt.

---

## 7. Repository-Struktur (Vorschlag)

```
ostbevern_money/
├── CLAUDE.md                     # Kurzanleitung für Claude Code (Befehle, Konventionen)
├── README.md
├── discussion/                   # Spezifikation, Notizen
├── raw_data/
│   └── haushalt-2026.pdf         # Quelle (aktuell: discussion/Haushalt 2026 komplett.pdf)
├── pipeline/                     # Python, uv-Projekt
│   ├── pyproject.toml
│   ├── ostbevern/                # Bibliothek: pdf.py, zahlen.py, plaene.py, …
│   ├── 01_seiten_klassifizieren.py … 08_quellenbelege.py
│   └── tests/
├── daten/
│   ├── zwischen/                 # seiten.csv, Rohextrakte (generiert)
│   ├── aufbereitet/              # CSV/JSON gemäß Abschnitt 4 (generiert, eingecheckt)
│   ├── manuell/                  # von Hand gepflegt, mit README
│   └── pruefberichte/            # konsistenz.md (generiert), befunde.md (manuell)
└── app/                          # Vue-Projekt
    ├── src/{pages,components,data,lib,charts}
    └── public/quellen/           # WebP-Seitenausschnitte
```

**Konventionen:**

- Generierte Dateien werden eingecheckt, damit die App ohne Pipeline baubar ist. Die CI prüft, dass `pipeline/alle.py` keinen Diff erzeugt.
- Bezeichner im Code und in den Daten auf Deutsch ohne Umlaute (`ertraege`, `zuschussbedarf`), wie in Münster.
- Beträge als `int` in Euro. Formatierung (z. B. „2,35 Mio. €“) nur in der App.

---

## 8. Qualität und Tests

- **Pipeline:** `pytest` mit den Prüfregeln aus 5.5 und den Sollwerten aus Anhang B. Zusätzlich gibt es Unit-Tests für Zahlenparser (deutsches Format, Minus, `–`, angeklebte Beträge) und Seitenklassifikation.
- **App:** `vue-tsc` (Typprüfung), ESLint. Optional Playwright-Smoke-Test: Jede Route rendert ohne Konsolenfehler, das Diagramm enthält Daten.
- **Inhalt:** Jeder Erklärtext mit einer Zahl verweist auf eine PDF-Seite. Zahlen in Texten werden aus den Daten erzeugt, nicht fest eingetippt.

---

## 9. Umsetzungsphasen

| Phase | Inhalt | Ergebnis / Abnahme |
|---|---|---|
| **P0 Setup** | Repo-Struktur, `CLAUDE.md`, uv-Projekt, PDF nach `raw_data/`, Vue-Grundgerüst (Übernahme aus Münster nach Lizenzklärung) | `uv run pytest` und `npm run build` laufen leer durch |
| **P1 Kernzahlen** | Seitenklassifikation; Gesamtergebnisplan, Gesamtfinanzplan, Teilergebnispläne (PB, Produkt) | Prüfregeln 1–4 grün; Sollwerte aus Anhang B getroffen |
| **P2 Details** | Produktinformationen inklusive Bindungsgrad, Grundzahlen, Erläuterungen; Teilfinanzpläne; Investitionen | Prüfregeln 6–8 grün; 63 Produkte vollständig |
| **P3 Manuelles** | Vorberichtstabellen, `meta.json`, Stellenplan, Erklärtexte | Prüfregel 5 grün; `befunde.md` gepflegt |
| **P4 Leitfragen** | Seiten Start, Einnahmen, Ausgaben, Geldfluss, Glossar | Beide Leitfragen in der App beantwortet; Review mit dir |
| **P5 Kontext** | Investitionen, Rat entscheidet, Entwicklung, Stellenplan | – |
| **P6 Spiele** | Planspiel, Was kostet, Schätzduell | Rechenregeln fachlich geprüft |
| **P7 Feinschliff** | Quellenbelege, Barrierefreiheit, Mobilansicht, Texte, Deployment GitHub Pages | Lighthouse-Barrierefreiheit ≥ 95; öffentliche URL |

---

## 10. Offene Fragen

1. **Lizenz Münster-Code:** Das Repo `codeformuenster/haushalt-muenster-2026` enthält **keine LICENSE-Datei**. Vor der Übernahme von Code die Erlaubnis von Code for Münster einholen bzw. dort eine Lizenz (z. B. MIT) ergänzen lassen. Alternativ nur Konzepte übernehmen.
2. **Einwohnerzahl** für Pro-Kopf-Werte: 11.741 (Vorbericht, 30.06.2024) oder 11.469 (Grafik S. 10, Stichtag unklar)? Eventuell den aktuellen Wert von IT.NRW nutzen.
3. **Anrede:** „du“ oder „Sie“? Münster mischt beides (Planspiel „du“, übrige Seiten „Sie“).
4. **Hosting und Name:** GitHub Pages unter welchem Account oder welcher Organisation? Projektname „Ostbevern Money“?
5. **Abstimmung mit der Gemeinde:** Soll die Kämmerei vorab informiert werden oder die Inhalte gegenlesen (Erklärtexte, Planspiel-Vereinfachungen)?
6. **Planspiel-Rechenregeln:** Wirkung von Hebesatzänderungen auf Umlagen und Schlüsselzuweisung fachlich bestätigen lassen.
7. **BBO/TEO:** Sollen Bad und Abwasser in einer späteren Version eine eigene Seite bekommen?
8. **Aktualisierung:** Soll die Pipeline so generisch sein, dass sie den Haushalt 2027 ohne Änderungen verarbeitet (gleiches ProFIS-Layout)?

---

## Anhang A – Produktverzeichnis (aus dem Inhaltsverzeichnis, PDF-Startseite)

PB = Produktbereich, PG = Produktgruppe (nur gedruckt, wenn mehrere Produkte), sechsstellig = Produkt.

| Code | Bezeichnung | Seite |
|---|---|---|
| **01** | **Innere Verwaltung** | 66 |
| 010101 | Politische Gremien | 72 |
| 010201 | Verwaltungsführung | 74 |
| 010301 | Gleichstellung von Frau und Mann | 76 |
| 010401 | Beschäftigtenvertretung/Personalrat | 79 |
| 010501 | Durchführung gesetzlich vorgeschriebener und übertragener Prüfungen | 81 |
| 0106 | Zentrale Dienste | 83 |
| 010601 | Zentrale Dienste für Organisationseinheiten im Hause und Dritter | 84 |
| 010602 | Bauhof | 88 |
| 010603 | Zentrale Dienste für Beteiligungen und verbundene Unternehmen | 92 |
| 010701 | Presse- und Öffentlichkeitsarbeit | 94 |
| 010801 | Gemeinde-/Städtepartnerschaften | 96 |
| 010901 | Personalmanagement | 98 |
| 0110 | Finanzmanagement und Rechnungswesen | 102 |
| 011001 | Finanzmanagement und Geschäftsbuchführung | 103 |
| 011002 | Zahlungsabwicklung und Vollstreckung | 105 |
| 011003 | Steuerveranlagung sowie Wasser- und Bodenverbandsgebühren | 107 |
| 011101 | Dienstleistung im Bereich IT | 109 |
| 0112 | Grundstücks- und Gebäudemanagement | 112 |
| 011201 | Bauunterhaltung von kommunal genutzten Gebäuden | 113 |
| 011202 | Bereitstellung und Bewirtschaftung von Gebäuden | 116 |
| 011203 | Baumaßnahmen | 118 |
| 011204 | Bereitstellung und Bewirtschaftung von Grundstücken | 120 |
| **02** | **Sicherheit und Ordnung** | 124 |
| 020101 | Allgemeine Gefahrenabwehr | 127 |
| 020201 | Gewerbewesen | 130 |
| 020301 | Verkehrsangelegenheiten | 132 |
| 020401 | Einwohnerangelegenheiten | 134 |
| 020501 | Standesamtswesen | 136 |
| 020601 | Wahlen und Abstimmungen | 138 |
| 020701 | Feuer- und Bevölkerungsschutz | 140 |
| **03** | **Schulträgeraufgaben** | 145 |
| 0301 | Schulische Einrichtungen und schülerbezogene Leistungen | 150 |
| 030101 | Ambrosius-Grundschule | 151 |
| 030102 | Franz-von-Assisi-Grundschule | 155 |
| 030103 | Josef-Annegarn-Schule | 158 |
| 030104 | Offene Ganztagsgrundschule, ganztägige Förder- und Betreuungsangebote | 162 |
| 030201 | Schülerbeförderung | 165 |
| 030301 | Zentrale Leistungen für Schüler/innen und am Schulleben Beteiligte | 167 |
| **04** | **Kultur** | 169 |
| 040101 | Kulturförderung, Heimatpflege | 171 |
| 040201 | Volkshochschule und sonstige Weiterbildung | 174 |
| 040301 | Schule für Musik im Kreis Warendorf | 176 |
| **05** | **Soziale Leistungen** | 178 |
| 0501 | Gesetzliche Leistungen | 180 |
| 050102 | Leistungen nach dem Asylbewerberleistungsgesetz | 181 |
| 050103 | Leistungen der Sozialhilfe nach SGB XII | 183 |
| 050201 | Zuschüsse an Dritte im Bereich des sozialen Lebens | 185 |
| 050301 | Dienstleistung und Beratung | 188 |
| 050401 | Demographie | 190 |
| **06** | **Kinder-, Jugend- und Familienhilfe** | 192 |
| 060101 | Unterstützung von Kindertagesstätten anderer Träger | 194 |
| 0602 | Kinder- und Jugendarbeit | 196 |
| 060201 | Jugendzentrum und Unterstützung Dritter im Bereich der Jugendarbeit | 197 |
| 060202 | Sportfreianlagen und Kinderspielplätze | 200 |
| **08** | **Sportförderung** | 203 |
| 080101 | Beverhalle, Förderung des Vereins- und Breitensports | 205 |
| **09** | **Räumliche Planung und Entwicklung, Geoinformationen** | 208 |
| 090101 | Räumliche Planung und Entwicklung | 211 |
| 0902 | Grundstücksneuordnung und grundstücksbezogene Ordnungsmaßnahmen | 214 |
| 090201 | Grundstücksneuordnung und -ordnungsmaßnahmen | 215 |
| 090202 | Grundstücksbezogene Informationen | 218 |
| **10** | **Bauen und Wohnen** | 220 |
| 100101 | Maßnahmen der Bauordnung | 222 |
| 100201 | Denkmalschutz und Denkmalpflege | 224 |
| 100301 | Wohnungsbau- und Wohnraumförderung, Wohnraumsicherung und -versorgung | 226 |
| 100401 | Unterkunft für Flüchtlinge und Asylbewerber | 228 |
| **11** | **Ver- und Entsorgung** | 231 |
| 110101 | Abfallbeseitigung und -entsorgung | 232 |
| **12** | **Verkehrsflächen und -anlagen** | 234 |
| 1201 | Öffentliche Verkehrsflächen und Verkehrsanlagen | 240 |
| 120101 | Bau von Straßen, Wegen, Plätzen und sonstigen Verkehrsanlagen | 241 |
| 120102 | Unterhaltung von Straßen, Wegen, Plätzen und sonstigen Verkehrsanlagen | 247 |
| 120201 | ÖPNV | 250 |
| 120301 | Straßenreinigung | 253 |
| **13** | **Natur- und Landschaftspflege** | 255 |
| 130101 | Natur- und Landschaftsschutz | 258 |
| 130201 | Öffentliche Grünanlagen | 261 |
| 130301 | Friedhofs- und Bestattungswesen | 264 |
| **14** | **Umweltschutz** | 268 |
| 140101 | Umwelt- und Klimaschutz, Mobilität | 269 |
| **15** | **Wirtschaft und Tourismus** | 271 |
| 150101 | Wirtschaftsförderung | 273 |
| 150102 | Touristische Öffentlichkeitsarbeit | 276 |
| **16** | **Allgemeine Finanzwirtschaft** | 278 |
| 160101 | Allgemeine Finanzwirtschaft | 280 |

---

## Anhang B – Sollwerte für Tests (Ansatz 2026, in €)

### B.1 Gesamtergebnisplan (S. 62)

| Z. | Position | 2024 Ist | 2025 | 2026 | 2027 | 2028 | 2029 |
|---|---|---:|---:|---:|---:|---:|---:|
| 01 | Steuern und ähnliche Abgaben | 19.614.808 | 17.964.000 | 18.443.000 | 19.866.000 | 20.801.000 | 21.721.000 |
| 02 | Zuwendungen und allgemeine Umlagen | 4.333.024 | 4.967.048 | 3.113.200 | 4.472.920 | 4.521.039 | 4.210.051 |
| 03 | Sonstige Transfererträge | 36.321 | 0 | 0 | 0 | 0 | 0 |
| 04 | Öffentlich-rechtliche Leistungsentgelte | 2.325.683 | 2.429.355 | 2.390.607 | 2.376.355 | 2.433.697 | 2.551.035 |
| 05 | Privatrechtliche Leistungsentgelte | 449.398 | 360.201 | 389.800 | 389.800 | 389.800 | 389.800 |
| 06 | Kostenerstattungen und Kostenumlagen | 812.781 | 686.150 | 762.070 | 770.970 | 760.720 | 781.750 |
| 07 | Sonstige ordentliche Erträge | 2.764.446 | 2.106.281 | 1.943.386 | 1.689.885 | 2.346.161 | 1.182.136 |
| 10 | **Ordentliche Erträge** | 30.336.461 | 28.513.035 | 27.042.063 | 29.565.930 | 31.252.417 | 30.835.772 |
| 11 | Personalaufwendungen | 4.629.147 | 4.977.200 | 5.204.054 | 5.448.900 | 5.666.700 | 5.893.100 |
| 12 | Versorgungsaufwendungen | 463.579 | 373.400 | 258.000 | 265.700 | 273.800 | 281.900 |
| 13 | Aufwendungen für Sach- und Dienstleistungen | 6.471.265 | 6.961.896 | 7.023.472 | 6.578.021 | 6.658.705 | 6.713.846 |
| 14 | Bilanzielle Abschreibungen | 2.882.133 | 2.957.773 | 2.758.142 | 2.576.817 | 2.831.331 | 2.808.031 |
| 15 | Transferaufwendungen | 14.523.567 | 13.782.286 | 13.764.981 | 15.756.800 | 16.232.800 | 16.746.800 |
| 16 | Sonstige ordentliche Aufwendungen | 1.581.389 | 1.430.600 | 1.246.920 | 1.242.220 | 1.797.908 | 2.399.795 |
| 17 | **Ordentliche Aufwendungen** | 30.551.079 | 30.483.155 | 30.255.569 | 31.868.458 | 33.461.244 | 34.843.472 |
| 18 | Ordentliches Ergebnis | −214.618 | −1.970.120 | −3.213.506 | −2.302.528 | −2.208.827 | −4.007.700 |
| 19 | Finanzerträge | 559.158 | 320.000 | 460.000 | 390.000 | 390.000 | 390.000 |
| 20 | Zinsen und ähnliche Aufwendungen | 152.549 | 246.000 | 200.000 | 350.000 | 600.000 | 600.000 |
| 26 | Jahresergebnis | 191.990 | −1.896.120 | −2.953.506 | −2.262.528 | −2.418.827 | −4.217.700 |
| 27 | Globaler Minderaufwand | 0 | −564.600 | −600.000 | −620.000 | −660.000 | −660.000 |
| 28 | **Jahresergebnis nach Minderaufwand** | 191.990 | −1.331.520 | −2.353.506 | −1.642.528 | −1.758.827 | −3.557.700 |

### B.2 Gesamtfinanzplan 2026 (S. 63) / Satzung § 1

| Position | Betrag |
|---|---:|
| Einzahlungen aus laufender Verwaltungstätigkeit (Z. 09) | 24.703.192 |
| Auszahlungen aus laufender Verwaltungstätigkeit (Z. 16) | 27.697.627 |
| Einzahlungen aus Investitionstätigkeit (Z. 23) | 7.224.830 |
| Auszahlungen aus Investitionstätigkeit (Z. 30) | 12.280.484 |
| davon Baumaßnahmen (Z. 25) | 7.915.000 |
| Kreditaufnahme (Z. 33) | 5.200.000 |
| Tilgung (Z. 35) | 450.000 |
| Verpflichtungsermächtigungen | 11.600.000 |
| Liquide Mittel Ende 2026 (Z. 41) | 4.199.420 |

### B.3 Teilergebnispläne 2026 je Produktbereich (geprüft: Summe = Gesamtplan)

| PB | Ord. Erträge | Ord. Aufwendungen | Ergebnis mit inneren Verrechnungen (TP Z. 29) |
|---|---:|---:|---:|
| 01 | 1.749.837 | 4.519.223 | −2.719.206 |
| 02 | 281.179 | 1.370.587 | −1.090.858 |
| 03 | 1.693.437 | 4.223.552 | −2.531.015 |
| 04 | 31.403 | 200.452 | −170.399 |
| 05 | 423.865 | 876.486 | −602.721 |
| 06 | 64.800 | 1.399.575 | −1.336.775 |
| 08 | 133.014 | 289.454 | −156.440 |
| 09 | 0 | 133.250 | −115.550 |
| 10 | 287.022 | 667.090 | −235.018 |
| 11 | 1.226.952 | 1.166.412 | 6.150 |
| 12 | 932.209 | 3.463.589 | −2.533.570 |
| 13 | 63.300 | 504.281 | −449.731 |
| 14 | 50.000 | 110.200 | −60.200 |
| 15 | 12.045 | 202.737 | −118.138 |
| 16 | 20.093.000 | 11.128.681 | 9.250.219 |
| **Σ** | **27.042.063** | **30.255.569** | |

### B.4 Steuerarten (Vorbericht S. 27, T€)

| Steuerart | 2024 Ist | 2025 | 2026 | 2027 | 2028 | 2029 |
|---|---:|---:|---:|---:|---:|---:|
| Grundsteuer A | 160 | 130 | 90 | 90 | 90 | 90 |
| Grundsteuer B | 1.851 | 2.000 | 2.060 | 2.285 | 2.312 | 2.340 |
| Gewerbesteuer | 9.511 | 7.165 | 7.800 | 8.300 | 8.800 | 9.300 |
| Anteil Einkommensteuer | 6.471 | 7.002 | 6.830 | 7.421 | 7.784 | 8.134 |
| Anteil Umsatzsteuer | 855 | 879 | 887 | 931 | 954 | 974 |
| Vergnügungssteuer | 54 | 50 | 55 | 55 | 55 | 55 |
| Hundesteuer | 65 | 65 | 66 | 66 | 66 | 66 |
| Kompensationszahlungen | 648 | 673 | 655 | 718 | 740 | 762 |
| **Summe** | 19.615 | 17.964 | 18.443 | 19.866 | 20.801 | 21.721 |

### B.5 Transferaufwendungen 2026 (Vorbericht S. 45–46, T€)

| Posten | 2026 |
|---|---:|
| Wasser- und Bodenverband | 152 |
| Zuschüsse an Kindertageseinrichtungen | 559 |
| Zuschuss an das Kinder- und Jugendwerk | 300 |
| Zuschuss an die OGS | 871 |
| Zuschüsse für laufende Zwecke | 120 |
| Sozialleistungen (Asylbewerberleistungsgesetz) | 491 |
| Gewerbesteuerumlage | 654 |
| Krankenhausinvestitionsumlage | 200 |
| Kreisumlage (netto, Fußnote 3) | 10.147 |
| Verlustübernahme BBO | 270 |
| **Summe** | **13.764** |

### B.6 Weitere Eckwerte

- Hebesätze 2026: Grundsteuer A 242 %, Grundsteuer B 554 %, Gewerbesteuer 418 %
- Kreisumlage-Hebesätze des Kreises Warendorf 2026: 36,3 % (Vorjahr 33 %); Jugendamtsumlage 21 % (Vorjahr 20,3 %)
- Schlüsselzuweisung 2026: 890 T€ (2025: 2.807 T€)
- Verringerung Ausgleichsrücklage 2.132.213 €, Verringerung allgemeine Rücklage 221.293 € (Satzung § 4)
- Höchstbetrag Liquiditätskredite 10.000.000 € (Satzung § 5)
- Investitionskredite Ende 2025 ≈ 7,7 Mio. € ≈ 656 € je Einwohner (11.741 Einwohner)
- Stellen Beamte 2026: 8 (S. 284)
