# Phase 6: Kontext-Seiten - Research

**Researched:** 2026-10-05
**Domain:** Vue-3-Frontend (Web Awesome, ECharts Bar/Line/MarkLine, Hash-Router mit URL-Filterzustand) auf bereits generierten JSON-Daten, plus kleiner Pipeline-Anteil (eine fehlende Vorberichtstabelle, zwei Schwellenwerte, neue Pipeline-Texte und Glossarbegriffe)
**Confidence:** HIGH für Datenlage und Prüfregeln (alle Zahlen gegen JSON und PDF-Seiten geprüft); MEDIUM für Layout-Annahmen bei 360 px (siehe Assumptions Log)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Worüber entscheidet der Rat? (RAT-01…04)**
- **D-01:** **Bindungsgrad-Balken ohne 160101, nur positiver Zuschussbedarf.** Produkt 160101 „Allgemeine Finanzwirtschaft“ (2026: −20.225.500 € Zuschussbedarf, dort liegen Steuern und Schlüsselzuweisung) ist die Finanzierungsquelle und erscheint nicht im gestapelten Balken. Ein Satz erklärt das. Produkte mit Überschuss (2026: 011202, 011204, 110101) stehen als eigene kleine Liste „bringen mehr ein, als sie kosten“ unter dem Balken. Der Balken summiert nur Produkte mit Zuschussbedarf > 0. Werte kommen ausschließlich aus `ergebnisplan[code].berechnet.zuschussbedarf` bzw. `ueberschuss` und werden nicht neu gerechnet (P5 D-05). Hintergrund: Ohne diese Regel ergäbe „pflichtig“ 2026 −13,9 Mio. €. Welche Produkte ausgeschlossen bzw. als Überschuss gelistet werden, wird aus den Daten abgeleitet (Vorzeichen bzw. ein benannter Ausschluss für 160101 an genau einer Stelle), nicht als Liste von Codes in der Komponente.
- **D-02:** **Die Weitergabe an Kreis und Land (KL) erscheint nur im Block „Was der Rat nicht beeinflussen kann“** (RAT-02), nicht als Segment im Bindungsgrad-Balken. KL ist kein Produkt und hat keinen Bindungsgrad. Der Block nennt Kreisumlage, Gewerbesteuerumlage (aus `KL.*`) und die gesetzlichen Sozialleistungen (`vorbericht.transferaufwendungen.sozialleistungen`) und stellt die Größenordnung dem Balken gegenüber.
- **D-03:** **Die fehlenden Einzelzuschüsse werden aus dem Vorbericht abgeschrieben.** Kulturtragende Vereine (23 T€), VHS (5 T€), Sportförderung (28 T€), Musikschule/JeKits (8 T€) u. a. kommen in eine neue manuelle Tabelle unter `daten/manuell/`. Es gelten die Regeln aus P4/P5: `betrag_teur`, Langformat, Seitenbeleg `quelle`, README-Begründung und Regel 5 gegen eine Planzeile, wo eine passende Zeile existiert. Der Researcher bestimmt Vorberichtsseite und Zuordnung (vermutlich Aufschlüsselung von „Zuschüsse für lfd. Zwecke“, 120 T€). Vorhandene Daten werden wiederverwendet: `kita_zuschuesse` (einzeln), Kinder- und Jugendwerk und OGS aus `transferaufwendungen`. Der Weg führt über Schritt 07 → `haushalt.json` → `vorbericht` → `typen.ts`.
- **D-04:** **Produkte je Bindungsgrad als drei Aufklapper** (`wa-details`), jeweils mit horizontalen Balken der Produkte, absteigend nach Zuschussbedarf, in PB-Farben (P5 D-08). Jedes Produkt verlinkt auf `/produkt/:code` (P5 D-09). Die `DatenTabelle` ist die Alternative.
- **D-05:** Der Hinweis zu RAT-04 („Der Bindungsgrad ist eine Selbstauskunft der Verwaltung; auch in pflichtigen Produkten gibt es Spielraum bei der Höhe“) ist ein Pipeline-Erklärtext mit Seitenverweis.

**Investitionen und Schulden (INV-01…04)**
- **D-06:** **Arten-Filter: Bau · Grundstücke · Fahrzeuge/Ausstattung · Sonstige.** „Sonstige“ fasst `finanzanlagen`, `investitionszuschuesse` und `immaterielles` zusammen. So fehlt keine Auszahlung, und die Summe aller Auszahlungen trifft die GFP-Zeile `auszahlungen_investitionen`; ein Test prüft das. Der zweite Filter ist der Aufgabenbereich (PB). Beide Filter sind per Tastatur bedienbar.
- **D-07:** **Liste und Balken zeigen die Summe 2026–2029 je Maßnahme.** Zeilen mit derselben `massnahme_id` werden über die Konten gebündelt und nach der Summe 2026–2029 sortiert. Die Jahreswerte stehen in der Tabelle bzw. im Detail. Der globale `?jahr=`-Umschalter gilt auf dieser Seite nicht. Die Maßnahmen verlinken auf `/produkt/:code`.
- **D-08:** **Einzahlungen je Maßnahme erscheinen nur im Finanzierungsblock**, nicht in Liste und Balken (keine Netto-Rechnung). Der Finanzierungsblock zeigt die Investitionseinzahlungen (GFP-Zeilen, ggf. mit der Aufteilung aus P5 D-03) sowie die Zeitreihe von Kreditaufnahme und Tilgung 2024–2029 aus `investitionen.finanzierung`. Finanzplan und Ergebnisplan stehen nie im selben Diagramm.
- **D-09:** **Der Schuldenstand 2026–2029 wird gezeigt und als berechnet gekennzeichnet.** 2024/2025 sind gedruckt (S. 310). Die Jahre 2026–2029 tragen `BerechnetEtikett` mit der Formel aus `schuldenstand.formel`. Die Kennzahl oben ist der Stand Ende 2025: 7,71 Mio. € gesamt bzw. 656 € je Einwohner. Ein datengetriebener Satz erklärt den Anstieg durch die geplanten Kredite. Dass Liquiditätskredite ab 2027 fehlen (`null`), wird kenntlich gemacht und nicht als 0 dargestellt.
- **D-10:** Die Verpflichtungsermächtigungen (11,6 Mio. €, Summe `ve_faelligkeiten`) werden mit ihren Fälligkeiten je Jahr gezeigt, dazu der vorhandene Text `verpflichtungsermaechtigungen`.

**Entwicklung 2024–2029 (ENTW-01…03)**
- **D-11:** **Erträge und Aufwendungen als Linien, das Jahresergebnis als Balken um die Null-Linie** (2024: +191.990 €, 2029: −3.557.700 €). Ist, Ansatz und Planung sind wie in P5 D-01/D-10 unterscheidbar und stehen als Etikett bzw. im Tooltip. Der globale Minderaufwand wird wie auf `/geldfluss` erklärt (Text `globaler_minderaufwand`), und es ist klar, ob das Ergebnis vor oder nach Minderaufwand gezeigt wird.
- **D-12:** **Die Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal und Zinsen laufen einheitlich 2024–2029.** Es gibt keinen Quellmix mit den Grundzahlen 2022–2023; diese bleiben `/einnahmen` vorbehalten. Für dasselbe Jahr gilt dieselbe Quelle wie in P5 D-01 (z. B. Gewerbesteuer aus `vorbericht.steuerarten`).
- **D-13:** **Die fünf Posten stehen als kleine Einzeldiagramme** (Liniendiagramme mit eigener y-Achse) mit Veränderung 2024 → 2029 in %. Auf schmalen Bildschirmen stehen sie untereinander. Jede Reihe hat eine Tabellenalternative.
- **D-14:** **„Wie lange reicht das Polster?“ wird mit Fakten bis 2029 und den HSK-Schwellen beantwortet.** Gestapelte Balken zeigen die Ausgleichsrücklage und die allgemeine Rücklage 2024–2029 aus `haushalt.eigenkapital`. Ein datengetriebener Satz lautet etwa: „Die Ausgleichsrücklage ist 2026 aufgebraucht, danach sinkt die allgemeine Rücklage bis 2029 um X %.“ Die Verringerung der allgemeinen Rücklage je Jahr wird in % gezeigt, mit den Schwellen der Haushaltssicherung als Bezug (§ 76 GO NRW: mehr als 25 % in einem Jahr bzw. mehr als 5 % in zwei aufeinanderfolgenden Jahren). Ein Glossar-Link führt zu „Haushaltssicherung“. **Es gibt keine eigene Prognose über 2029 hinaus.** Der Researcher prüft den genauen Wortlaut und die Bezugsgröße der Schwellen. Die Schwellenwerte stehen mit Quelle in den Daten bzw. der Konfiguration, nicht als Literal in der Komponente. Die Formulierung darf keine rechtliche Bewertung vorwegnehmen („Schwelle“, nicht „muss ein HSK aufstellen“).

**Stellenplan (STEL-01…03)**
- **D-15:** **Drei Kennzahlkacheln plus gruppierte Balken nach Teil.** Die Kacheln zeigen Stellen 2026 (62,91), 2025 (62,13) und besetzt am 30.06.2025 (56,63), dazu die Differenzen als berechnet. Die gruppierten Balken je Teil (Beamte, Tarif, Sozial- und Erziehungsdienst) zeigen jeweils die drei Werte. Nachwuchskräfte stehen als Hinweis daneben. Alle Summen werden aus `stellenplan.json` abgeleitet; die Zeilen mit `produktbereich` (Stellenübersicht nach PB) dürfen nicht doppelt gezählt werden.
- **D-16:** **Stellen und Personalaufwand je Aufgabenbereich als zwei Balken je PB nebeneinander:** Stellen 2026 in VZÄ und Personalaufwand aus TP Z. 11 (`personalaufwendungen` je PB, 2026), mit getrennten Achsen und in PB-Farbe (P5 D-08). **Es gibt keinen berechneten Aufwand je Stelle**, weil das einer Gehaltsschätzung nahekäme (Out of Scope). Die Aufteilung nach PB gibt es nur für 2026; die Seite sagt das.
- **D-17:** **Die Verteilung nach Gruppe hat einen Abschnitt je Teil:** Besoldung (A/B), Entgelt (E 1–14) und S-Gruppen, jeweils aufsteigend sortiert. Ein kurzer Glossar-Eintrag erklärt die Gruppen.

**Was nicht im Haushalt steht (UI-04)**
- **D-18:** **Eine wiederverwendbare Hinweisbox** mit dem vorhandenen Text `nicht_im_haushalt` (S. 14/33/46/48) steht auf `/ausgaben` (Hallenbad, Verlustübernahme), `/einnahmen` (Abwassergebühren fehlen) und in Kurzform auf `/rat-entscheidet`. Dazu kommt ein Anker im Glossar. Es gibt keine eigene Route.

**Übergreifend**
- **D-19:** Neue Routen `/entwicklung`, `/investitionen`, `/rat-entscheidet` und `/stellenplan` stehen im Dropdown „Mehr wissen“. Dafür wird `MenueEintrag` zu einer Vereinigung erweitert, wie in `app/src/lib/menue.ts` vorgesehen. `MENUE` bleibt die einzige Quelle für die horizontale Liste und den Drawer. Seitentitel stehen in `meta.titel`, und die Fokussteuerung beim Routenwechsel bleibt erhalten.
- **D-20:** Neue Erklärtexte (u. a. RAT-04, Überschuss-Liste, Polster-Satz, Schuldenanstieg, Glossar „Haushaltssicherung“ und Gruppen) sind Pipeline-Texte mit Platzhaltern `{{schluessel|kuerzel}}` und Seitenverweis. Der Executor entwirft sie, ein **Checkpoint** legt sie dir zur fachlichen Abnahme vor (wie P4 D-17 / P5 D-15). Berechnete Werte in Sätzen (Prozente, Differenzen) stammen aus den Daten, nicht von Hand.

### Claude's Discretion
- Komponentenschnitt und Namen (z. B. `BindungsgradBalken`, `MassnahmenListe`, `RuecklagenBalken`, `HinweisNichtImHaushalt`) sowie Composables
- Genaue Diagrammformen innerhalb der Entscheidungen (Farben aus `echartsTheme.ts`, Decals, Achsen), Reihenfolge der Abschnitte je Seite
- Reihenfolge der Einträge im Dropdown „Mehr wissen“
- Ob die Markierung „Ortsteil Brock“ (Spez. 6.10, optional) als einfacher Textfilter mitkommt
- Ob neue Daten (Bündelung je Maßnahme, Summen je Bindungsgrad) in der Pipeline (Schritt 07) oder in `app/src/lib/` entstehen, solange die Werte aus `berechnet` gelesen und Summen gegen die Planzeilen getestet werden

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope. (Nicht Teil dieser Phase laut Phasengrenze: „Quelle anzeigen“ mit WebP-Seiten, Lighthouse-Abnahme, Deployment — alles Phase 7 — sowie Spiele, v2.)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ENTW-01 | Erträge, Aufwendungen, Jahresergebnis 2024–2029, Ist/Ansatz/Planung unterscheidbar | Daten vollständig in `haushalt.json` (`ergebnisplan.GESAMT.berechnet.{ertraege,aufwand}`, `zeilen.{jahresergebnis,ergebnis_nach_minderaufwand,globaler_minderaufwand}`). **Konflikt UI-SPEC vs. ROADMAP bei „vor/nach Minderaufwand“, siehe Open Question 1.** |
| ENTW-02 | Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen | Alle fünf Reihen 2024–2029 vorhanden (Quellen siehe „Data Needs Matrix“). Kein Pipeline-Anteil. Kreisumlage 2026 ist netto (Fußnote S. 46), Pitfall 6. |
| ENTW-03 | Ausgleichs- und allgemeine Rücklage, wie lange das Polster reicht | `haushalt.eigenkapital` vorhanden; **Spaltensemantik und Jahr-Zuordnung der Rückgangs-% durch S. 23/24/311 geklärt (Pitfall 1)**; neu: zwei Schwellenwerte in `meta.json` (Quelle S. 23), Abgeleitet-Formeln für den Polster-Satz. |
| INV-01 | Maßnahmen 2026–2029 als Liste und Balken, filterbar nach PB und Art | `investitionen.massnahmen` (137 Zeilen). **Bündelungsschlüssel muss `(produkt, massnahme_id)` sein, nicht `massnahme_id` allein (Pitfall 2).** Summen je Art und gesamt = GFP-Zeilen 2025–2029 exakt (Test). |
| INV-02 | Verpflichtungsermächtigungen 11,6 Mio. € mit Fälligkeiten | `investitionen.ve_faelligkeiten` (8 Zeilen, Σ 11.600.000; 2027: 9.400.000, 2028: 2.200.000 = S. 309). Text `verpflichtungsermaechtigungen` existiert. |
| INV-03 | Finanzierung und Zeitreihe Kreditaufnahme/Tilgung 2024–2029 | `investitionen.finanzierung.zeilen` + `haushalt.finanzplan.GESAMT.zeilen.*` (Aufteilung der Einzahlungen). Kein Pipeline-Anteil. |
| INV-04 | Schuldenstand gesamt und je Einwohner | `investitionen.schuldenstand` vorhanden. **`gesamt` enthält die Liquiditätskredite nicht (Pitfall 3).** 656 € ist auf S. 25 gedruckt. |
| RAT-01 | Zuschussbedarf nach Bindungsgrad als gestapelter Balken mit Produkten | `produkte[].bindungsgrad` (31/15/17) + `berechnet.zuschussbedarf`; Summen 2026 vorab berechnet (Tabelle unten). Kein Pipeline-Anteil. |
| RAT-02 | Block „Was der Rat nicht beeinflussen kann“ | `lib/kreisumlage.ts` (`KL.*`) + `vorbericht.transferaufwendungen.sozialleistungen`. Kein Pipeline-Anteil. |
| RAT-03 | Einzelzuschüsse aus dem Vorbericht | **Neue manuelle Tabelle nötig: Vorbericht S. 47, 8 Posten, Σ = 120 T€ = Posten „Zuschüsse für lfd. Zwecke“ 2026 (exakt).** Kita, Kinder- und Jugendwerk, OGS sind schon da. |
| RAT-04 | Hinweis „Bindungsgrad ist Selbstauskunft“ | Neuer Pipeline-Text (D-05, D-20, Checkpoint). Zahlenfrei möglich. |
| STEL-01 | Stellen 2026 vs. 2025 vs. besetzt 30.06.2025 | `stellenplan.json` vollständig; 62,91 / 62,13 / 56,63 verifiziert. Float-Drift-Pitfall (Pitfall 5). |
| STEL-02 | Verteilung nach Aufgabenbereich und nach Gruppe | PB-Zeilen (`produktbereich`) und Teil-A/B-Zeilen vorhanden, beide Summen 62,91. Sortierung der Gruppen: Pitfall 7. |
| STEL-03 | Personalaufwand je Aufgabenbereich (TP Z. 11) | `ergebnisplan[pb].zeilen.personalaufwendungen[haushaltsjahr]`; Σ über die 15 PB = 5.204.054 = GESAMT. Kein Pipeline-Anteil. |
| UI-04 | Hinweis „Was nicht im Haushalt steht“ (BBO, TEO) | Text `nicht_im_haushalt` existiert (S. 14/33/46/48), wird heute nirgends angezeigt. Neu: Komponente, Einbau auf drei Seiten, Glossarbegriff. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Quelle: `/Users/thma/repos/bitwerkstatt/ostbevern_money/.claude/CLAUDE.md` (der übergeordnete `/Users/thma/repos/bitwerkstatt/CLAUDE.md` betrifft nur die Sandbox-Umgebung).

- **Deutsche Bezeichner ohne Umlaute** in Code und Daten (`ertraege`, `zuschussbedarf`). **Beträge als int-Euro**, Formatierung ausschließlich über `app/src/charts/format.ts`. **Nur 1-basierte `pdf_seite`.**
- **Keine Jahrgangswerte im Code:** Haushaltsjahr, Seitenbereiche, Spaltenköpfe, erwartete Anzahlen in `pipeline/jahrgaenge/{jahr}.toml`; gelesen nur über `ostbevern.konfiguration.lade_jahrgang`/`lade_sollwerte`. Die App bezieht den Jahrgang aus `app/src/data/`.
- **Du-Anrede** in allen App-Texten. **Zahlen in Texten aus Daten**, jeder erklärende Text mit Zahl verweist auf eine PDF-Seite.
- Pipeline-Skripte sind dünne typer-Einstiegspunkte, Logik in `pipeline/ostbevern/`. Fachliche Regeln (Zeilenformeln, Minderaufwand, Ausschluss TP 27/28) bleiben im Code. **Generierte Daten unter `daten/` werden eingecheckt.**
- Basiskomponenten behalten Münster-Namen und -Props (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts`, `bildschirm.ts`).
- **Farben nur über `--wa-*`-Tokens**, Chartfarben nur aus `echartsTheme.ts`. CSS-Klassen mit Präfix `om-`. Beispielwerte nur hinter `ChartCard`-Flag `beispieldaten`. **Keine Drittanbieter-Requests zur Laufzeit.**
- **Beim Commit nur explizit benannte Pfade stagen.**
- Befehle: `uv run --directory pipeline pytest|ruff check .|ruff format .|python alle.py --jahr 2026`; App: `npm --prefix app run type-check|lint|format:check|test|build`. App-Checks laufen im Linux-Sandbox **in einer Scratch-Kopie** (macOS-Binaries in `app/node_modules`).
- Genauigkeit: Abweichungen > 1 € gegenüber Planwerten sind Fehler, außer in `befunde.md` dokumentiert. Datenschutz: keine Mitarbeitendennamen ausliefern (`stellenplan.json` trägt nur Amtsbezeichnungen, verifiziert).
- Barrierefreiheit: Lighthouse a11y ≥ 95 (Abnahme in Phase 7), Fokussteuerung, Kontraste, `prefers-reduced-motion`, ab 360 px.
- GSD-Workflow: Dateiänderungen nur über GSD-Befehle (für die Planung/Ausführung zuständig, nicht für diese Recherche).
- Zusätzlich gelten die `stiltokens.test.ts`-Regeln (keine undefinierten `--wa-*`-Tokens) und die Token-Hygiene aus `05-UI-REVIEW.md` (UI-SPEC Spacing-Abschnitt): in neuem Code kein `font-weight: 600`, kein `--wa-font-weight-semibold`, kein `--wa-font-size-xl`, kein `--wa-space-3xs`/`-2xl`.

## Summary

**Fast alle Daten für Phase 6 liegen schon in `app/src/data/*.json`.** Phase 6 ist überwiegend App-Arbeit (vier Seiten, Menügruppe, ~14 Komponenten, Lib-Module mit Tests). Der Pipeline-Anteil ist klein und klar umrissen: (1) **eine** neue manuelle Tabelle (Einzelzuschüsse, Vorbericht **S. 47**, Σ 120 T€ exakt gleich dem Transferposten „Zuschüsse für lfd. Zwecke“), (2) **zwei Schwellenwerte** (25 %, 5 %) als `meta.json`-Einträge mit Quelle **S. 23**, (3) neue Pipeline-Texte und Abgeleitet-Formeln (Polster-Satz, Schuldenanstieg, RAT-04, Überschuss-Satz, Hinweisbox-Leitsätze), (4) drei neue Glossarbegriffe (`nicht_im_haushalt`, `vzae`, `entgeltgruppen`). Alles andere (Stellenplan, Investitionen, Schuldenstand, VE, Rücklagen, Bindungsgrad) ist extrahiert und bereits gegen Plan-/Satzungswerte geprüft.

**Vier Funde ändern den Plan gegenüber CONTEXT/UI-SPEC** und brauchen eine Entscheidung vor dem Coden (Details im Abschnitt Open Questions und Pitfalls): (a) UI-SPEC zeigt als „Jahresergebnis“ die Zeile **vor** Minderaufwand (2029: −4.217.700 €), ROADMAP SC 1, Spez. 6.12 und D-11 nennen aber **−3.557.700 €** (nach Minderaufwand); (b) `massnahme_id` ist **nicht eindeutig** über Produkte (11 IDs kommen unter mehreren Produkten vor), die Bündelung braucht `(produkt, massnahme_id)`; (c) der Schuldenstand `gesamt` (7,71 Mio. €) **enthält die Liquiditätskredite nicht**, ein Stapel mit Liquiditätskrediten und „Gesamtsumme über der Säule“ würde 7,71 Mio. € widersprechen; (d) die UI-SPEC-Annahme „Rückgang 2027–2029 jeweils unter 5 %“ ist **falsch**: der Vorbericht druckt auf **S. 23** die Rückgänge der allgemeinen Rücklage je Haushaltsjahr (2026: 1,77 %, 2027: 4,23 %, 2028: 4,73 %, **2029: 10,04 %**); eine naive Spaltendifferenz verschöbe alle Werte um ein Jahr.

Die offene Frage „Stichtag der Spalten auf S. 311“ ist **geklärt**: Die Rücklagenzeilen sind Bestände **zu Beginn** des Jahres, das Jahresergebnis gehört zum Jahr selbst, `Summe Eigenkapital` ist der Bestand am Jahresende. Beleg: Σ der Spalte stimmt in allen sechs Jahren exakt, und S. 24 sagt „Die Allgemeine Rücklage wird Ende 2026 noch einen Bestand von rd. 38,8 Mio. € ausweisen“ = Spalte 2027 (38.825.371 €). Auch die HSK-Schwellen stehen im Wortlaut auf **S. 23** (Vorbericht zitiert § 76 GO NRW) und der Vorbericht stellt dort selbst fest, dass keine Verpflichtung zu einem HSK besteht; die App darf das als „Laut Vorbericht“ wiedergeben.

**Primary recommendation:** Pipeline-Arbeit auf drei kleine Pläne begrenzen (Einzelzuschüsse-Tabelle; Meta-Schwellen plus Texte/Glossar mit Abnahme-Checkpoint), alle Rechenlogik (Bündelung, Bindungsgrad-Summen, Rückgang %, Stellen-Summen) als reine, getestete Funktionen in `app/src/lib/` (Muster `zeitreihen.ts`/`drilldown.ts`), die vier Seiten danach parallel bauen, und die vier Konflikte (Minderaufwand, Bündelungsschlüssel, Liquiditätskredite, Rückgangs-Jahrzuordnung) **vorab** in den Plänen festschreiben.

## Data Needs Matrix (Pipeline vs. App)

Kernfrage des Orchestrators: Was liefert die Pipeline heute **nicht**? Alle Werte unten wurden diese Session aus `app/src/data/*.json` gelesen (Python/Node) und gegen PDF-Seiten (pdfplumber auf `raw_data/haushalt-2026.pdf`, 1-basiert) geprüft.

| # | Bedarf | Status | Quelle (`pdf_seite`) | Prüfregel / Test | Arbeit |
|---|--------|--------|----------------------|------------------|--------|
| 1 | Erträge, Aufwendungen, Jahresergebnis 2024–2029 | **vorhanden** | GEP S. 62 | Regeln 1–4 grün (Phase 2) | nur App |
| 2 | Kreisumlage, Gewerbesteuer, Schlüsselzuweisung 2024–2029 | **vorhanden** (`vorbericht.transferaufwendungen.kreisumlage`, `.steuerarten.gewerbesteuer`, `.zuwendungen.schluesselzuweisung`) | S. 46, 27, 28 | Regel 5 grün | nur App |
| 3 | Personal, Zinsen 2024–2029 | **vorhanden** als GEP-Zeilen `personalaufwendungen`, `zinsaufwendungen` (eurogenau). Keine Vorberichtstabelle für Zinsen. | S. 62 (GEP); `vorbericht.personal` S. 34 nur als T€-Kontrolle | Regel 5 (`personal` vs. GEP Z. 11) | nur App; Quelle = GEP wie `/ausgaben` |
| 4 | Ausgleichs-/allgemeine Rücklage 2024–2029 | **vorhanden** (`haushalt.eigenkapital`) | S. 311 | Regel 5 `eigenkapital`, `satzung_paragraf4`; Summenidentität je Spalte (diese Session: alle 6 Jahre exakt) | nur App |
| 5 | **HSK-Schwellen 25 % / 5 %** | **FEHLT** | **S. 23** (Wortlaut, zitiert § 76 GO NRW) | neuer pytest: Werte und `quelle` in `meta.json` | **Pipeline (klein):** zwei `meta.vorbericht_werte`-Einträge (`einheit: "prozent"`, `quelle: 23`), README-Absatz |
| 6 | Gedruckte Rückgänge der allgemeinen Rücklage (1,77 / 4,23 / 4,73 / 10,04 %) | **FEHLT** (nur als Kontrollwerte nötig) | **S. 23** (Tabelle „Abbau/Zuführung Allgemeine Rücklage“, Abschnitt „Entwicklung aus Sicht des Haushaltes 2026“) | vitest: App-Rechnung gerundet auf 2 Stellen = gedruckte Werte (Sollwerte im Test) | App-Test; optional Eckwert |
| 7 | Maßnahmen 2026–2029, Art, PB | **vorhanden** (137 Zeilen, `art` je **Konto-Zeile**) | Produktseiten (`massnahme.pdf_seite`) | Regel 6 grün; Summen je Art und gesamt = GFP-Zeilen **2025–2029 exakt** (diese Session geprüft); 2024 Ist weicht dokumentiert ab (befunde: −490.612 / −142.826) | nur App (Bündelung in `lib/`) |
| 8 | VE-Fälligkeiten | **vorhanden** (8 Zeilen, 11.600.000) | S. 309 (Fälligkeiten), S. 25 (11,6 Mio.) | Regel 5 `ve_uebersicht` vs. `ve_faelligkeiten`, vs. GFP VE | nur App |
| 9 | Finanzierung, Kredit/Tilgung 2024–2029 | **vorhanden** (`finanzierung.zeilen`, GFP-Zeilen in `haushalt.finanzplan`) | S. 63 | Regel 5 `kredite_fortschreibung` | nur App |
| 10 | Schuldenstand 2024–2029, je Einwohner | **vorhanden** (`schuldenstand`, `berechnet = [false,false,false,true,true,true]`) | S. 310, S. 24/25 | Regel 9 `pro_kopf_verschuldung_vorjahr` = 656 | nur App |
| 11 | Stellen 2026/2025/besetzt, nach Teil, Gruppe, PB | **vorhanden** (`stellenplan.json`, 162 Zeilen) | S. 284–290 | Regel 9 `stellen_beamte`, Regel 10; Σ Teil = Σ PB = Σ Gruppe (diese Session: 62,91 / 62,13 / 56,63); S. 34: 8,0 + 54,91 = 62,91 | nur App |
| 12 | Personalaufwand je PB 2026 | **vorhanden** (`ergebnisplan[pb].zeilen.personalaufwendungen`) | Teilergebnispläne PB | Regel 2/3; Σ 15 PB = 5.204.054 = GESAMT (diese Session) | nur App |
| 13 | Bindungsgrad je Produkt | **vorhanden** (`produkte[].bindungsgrad`: 31 pflichtig / 15 teils / 17 freiwillig) | Produktseiten, z. B. S. 72 | Regel 8 (Vollständigkeit) | nur App |
| 14 | **Einzelzuschüsse (RAT-03)** | **FEHLT** (Kita einzeln, Kinder- und Jugendwerk 300, OGS 871 sind da) | **S. 47**, Absatz „Die Zuschüsse für lfd. Zwecke (120 T€) enthalten …“ | **Regel 5 (neu):** Σ Posten = Posten `zuschuesse_laufende_zwecke` 2026 = 120 T€, wie `kita_zuschuesse` gegen `zuschuesse_kindertageseinrichtungen` | **Pipeline:** neue CSV + Regel 5 + README + Schritt 07 + `typen.ts` unverändert |
| 15 | Erklärtexte RAT-04, Überschuss, Polster, Schuldenanstieg, Hinweisbox-Leitsätze | **FEHLEN** (Entwürfe in UI-SPEC) | siehe Texte | `pruefe_text`, `loese_auf`, Seitenverweis, Node-Gegenprobe | **Pipeline-Texte** + Abnahme-Checkpoint (D-20) |
| 16 | Glossar `nicht_im_haushalt`, `vzae`, `entgeltgruppen` | **FEHLEN** (`haushaltssicherung` existiert schon, S. 23) | S. 14/33/46/48; S. 34/35; S. 284 ff. | `glossar.test.ts` beidseitig (Tupel ↔ Daten) | Pipeline-Text + `GLOSSAR_SCHLUESSEL` |

**Die acht Posten von S. 47** (verbatim gelesen, 1-basierte PDF-Seite 47): kulturtragende Vereine 23 T€, VHS 5 T€, „Eigenanteil JeKits-Pauschale an die Schule für Musik“ 8 T€, Sportförderrichtlinie 28 T€, „Zuschüsse an Dritte im Bereich des sozialen Lebens“ 23 T€, Schulsozialarbeit 24 T€, Ferienfreizeit der Jugendlichen 8 T€, Restaurierung privater Denkmale 1 T€. 23+5+8+28+23+24+8+1 = **120** T€. [VERIFIED: PDF S. 47 und `transferaufwendungen` „Zuschüsse für lfd. Zwecke 183 203 120 117 112 112“ auf S. 46]

## Architectural Responsibility Map

Die App ist rein statisch (kein Backend); die „Tiers“ sind hier Pipeline (Build-Zeit), App-Lib (reine Funktionen), Komponenten, Router.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Extraktion/Abschrift der Einzelzuschüsse, HSK-Schwellen | Pipeline (`daten/manuell/`, Schritt 07) | — | Konvention: Handdaten mit `quelle`, README, Regel 5, kein PDF-Zugriff zur Laufzeit |
| Erklärtexte, Glossar, Abgeleitet-Formeln | Pipeline (`texte.py`, `erklaerungen.md`, `glossar.md`) | App (`rendereAbsatz`) | Zahlen nur als Platzhalter, Formatierung nur in `format.ts` |
| Maßnahmen bündeln/filtern, Bindungsgrad-Summen, Rückgang %, Stellen-Summen | App-Lib (`app/src/lib/*.ts`, reine Funktionen) | Tests (vitest) | Werte kommen aus `berechnet`/JSON, Summen werden gegen Planzeilen getestet (CONTEXT-Discretion) |
| Diagrammoptionen (Builder) | App-Lib / `charts/*.ts` | `BaseChart` | Muster `horizontaleBalkenOption`, `zuschussBalkenOption`: Builder bekommt fertige Texte, Tooltips nur über `tooltipZeilen` |
| Filterzustand `pb`/`art` | Router (URL-Query, `router.replace`) | Lib (`leseMassnahmenFilter`) | Muster `leseAnsicht`/`useAnsicht`; Allowlist, Bereinigung ungültiger Werte |
| Menügruppe „Mehr wissen“ | `lib/menue.ts` (einzige Quelle) | `App.vue`/`MenueGruppe.vue` | D-19: Liste und Drawer aus einer Quelle |
| Seiten, Abschnitte, Tabellenalternativen | Seitenkomponenten (`pages/*.vue`) | `ChartCard`, `DatenTabelle` | Gemeinsamer Rahmen aus Phase 5 |

## Standard Stack

### Core (alles bereits installiert, **keine neuen Pakete nötig**)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vue | 3.5.43 (Lockfile) | Komponenten, Composables | Projektstack [VERIFIED: `app/package-lock.json`] |
| vue-router | 5.3.1 | Hash-Router, Query-Zustand | Projektstack [VERIFIED: `app/package-lock.json`] |
| echarts | 6.1.0 | Balken, Linien, MarkLine | Projektstack; `MarkLineComponent` exportiert aus `echarts/components` [VERIFIED: `node_modules/echarts/types/dist/components.d.ts`, „install$40 as MarkLineComponent“] |
| vue-echarts | 8.3.1 | `BaseChart`-Wrapper | Projektstack [VERIFIED: `app/package-lock.json`] |
| @awesome.me/webawesome | 3.14.0 | `wa-details`, `wa-callout`, `wa-select`, `wa-radio-group`, `wa-tag`, … | alle benötigten Komponenten sind in `app/src/main.ts` bereits importiert [VERIFIED: `main.ts` Zeilen 4–19] |
| vitest | 5.0.3 | App-Tests (Node-Umgebung, kein DOM) | Phase-5-Entscheidung; Baseline diese Session: 25 Dateien, 1031 Tests grün, < 1 s [VERIFIED: Lauf in Scratch-Kopie] |
| pytest / uv / polars / pdfplumber | uv 0.9.26, pdfplumber 0.11.10, Python ≥ 3.12 | Pipeline-Tests | Baseline diese Session: 528 Tests grün in 321 s (Sandbox) [VERIFIED: Lauf] |

**Zu ändern an `echartsTheme.ts` (Korrektur zur UI-SPEC):** `BarChart` und `LineChart` sind **bereits** registriert; zu ergänzen ist nur `MarkLineComponent` (Schwellenlinie). `GraphicComponent` wird nicht gebraucht (Direktbeschriftung über `label`). [VERIFIED: `echartsTheme.ts` Zeilen 9–31]

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `wa-dropdown` für „Mehr wissen“ | eigenes Disclosure (Button + `aria-expanded` + Linkliste) | UI-SPEC entscheidet bewusst fürs Disclosure (kein `role="menu"`); bleibt so |
| Maßnahmen-Bündelung in Pipeline | Bündelung in `lib/investitionen.ts` | CONTEXT-Discretion; App-Lib vermeidet Doppelhaltung von Logik in Python und TS und braucht keinen neuen JSON-Schnitt. **Empfehlung: App-Lib.** |
| Neues Formatkürzel `prozent2` (zwei Nachkommastellen wie S. 23) | vorhandenes `prozent` (max. 1 Nachkommastelle) | `prozent2` wäre an drei Stellen zu pflegen (`format.ts`, `texte.py::FORMATKUERZEL`, `lib/texte.ts::KUERZEL`) plus `test_formatiere.py`. **Empfehlung: bei `prozent`** (4,2 % statt 4,23 %); 10,04 % erscheint als „10 %“. Entscheidung am Checkpoint möglich. |

**Installation:** keine. (`npm ci` in einer Scratch-Kopie ist nur für Checks nötig; die Registry ist erreichbar [VERIFIED: HTTP 200 von registry.npmjs.org].)

**Version verification:** Versionen aus `app/package-lock.json` gelesen; Registry-Abfragen entfallen, da nichts installiert wird.

## Package Legitimacy Audit

Diese Phase installiert **keine** externen Pakete (weder npm noch PyPI). Der Legitimacy-Seam wurde deshalb nicht aufgerufen.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | — | keine neuen Pakete |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

Hinweis: Das Symbol `chevron-down` (UI-SPEC) wäre eine neue SVG-Datei unter `app/public/icons/solid/` im Stil der vorhandenen Font-Awesome-Free-7.3.1-Icons (CC BY 4.0, Lizenzkommentar im SVG). Sie liegt **nicht** in `node_modules`. Empfehlung: ein eigenes, im Repo gezeichnetes Inline-SVG bzw. eine CSS-Form im `MenueGruppe`-Component statt eines Pakets oder externen Downloads (kein Lizenzthema, keine Netzabhängigkeit); siehe Assumption A1.

## Architecture Patterns

### System Architecture Diagram

```
raw_data/haushalt-2026.pdf
   │  (einmalige Abschrift, Phase-4-Muster)
   ├─ S. 47 ──► daten/manuell/zuschuesse_lfd_zwecke.csv ─┐   (NEU, Regel 5 vs. transferaufwendungen.zuschuesse_laufende_zwecke)
   ├─ S. 23 ──► daten/manuell/meta.json  vorbericht_werte.hsk_schwelle_* ─┤   (NEU, 2 Werte)
   │                                                       │
   ├─ vorhandene Extraktion (Phase 2–4) ───────────────────┤
   │   daten/aufbereitet/*.csv, daten/manuell/*.csv        │
   ▼                                                       ▼
 pipeline/07_app_daten.py (ostbevern/app_daten.py, texte.py)
   │  + erklaerungen.md / glossar.md (NEU: Texte, Abgeleitet-Formeln, 3 Glossarbegriffe)
   ▼
 app/src/data/{haushalt,investitionen,stellenplan,produkte,texte}.json   ──► typen.ts / daten.ts (unverändert, außer neue Tabelle erscheint nur als weiterer Schlüssel in `vorbericht`)
   │
   ▼  reine Funktionen (vitest-getestet), lesen nur `berechnet`/Rohwerte
 app/src/lib/ { entwicklung, ruecklagen, investitionen, schulden, bindungsgrad, stellen, zuschuesse, menue }
   │                      ▲ Query: ?pb=&art= (nur /investitionen), router.replace
   ▼                      │
 app/src/charts/ (Builder, Theme: +MarkLine, BINDUNG_FARBEN, BERECHNET_DECAL, SCHWELLE_FARBE)
   ▼
 app/src/components/ (ChartCard › BaseChart / DatenTabelle / wa-details / wa-callout)
   ▼
 app/src/pages/ { Entwicklung, Investitionen, RatEntscheidet, Stellenplan }Page.vue
   ▼  Router (4 neue Routen, meta.titel)  +  MENUE (Union Link | Gruppe) ─► App.vue Kopfmenü + Drawer
 Einbau HinweisNichtImHaushalt: AusgabenPage, EinnahmenPage, RatEntscheidetPage(kurz); Glossaranker nicht_im_haushalt
```

### Recommended Project Structure

```
daten/manuell/
├── zuschuesse_lfd_zwecke.csv        # NEU (Name Empfehlung; Muster kita_zuschuesse.csv, nur Haushaltsjahr)
├── meta.json                        # + vorbericht_werte.hsk_schwelle_ein_jahr / hsk_schwelle_zwei_jahre
└── texte/{erklaerungen,glossar}.md  # + neue Abschnitte
pipeline/ostbevern/
├── schema.py        # + ZUSCHUESSE_LFD_ZWECKE_CSV
├── pruefung.py      # + Regel-5-Querprüfung (Σ Posten = Transferposten), + CSV im Lader (~Z. 2549)
├── app_daten.py     # + Eintrag in `vorbericht_quellen` (Z. 971, nach kita_zuschuesse)
└── texte.py         # + ABGELEITET-Formeln (Polster, Schuldenanstieg, ggf. Überschuss)
pipeline/tests/      # test_manuell, test_pruefung, test_app_daten (Reihenfolge der vorbericht-Schlüssel), test_texte
app/src/
├── lib/             # entwicklung.ts, ruecklagen.ts, investitionen.ts, schulden.ts, bindungsgrad.ts, stellen.ts, zuschuesse.ts (+ menue.ts erweitert)
│   └── __tests__/   # je Modul ein Test; menue.test.ts, glossar.test.ts, quelltext.test.ts anpassen
├── components/      # laut UI-SPEC „Phase 6 Components“ (Namen Empfehlung)
└── pages/           # vier neue Seiten
```

### Pattern 1: Maßnahmen bündeln (Schlüssel `(produkt, massnahme_id)`, nur Auszahlungen, Summe der Planjahre ab Haushaltsjahr)

**What:** Zeilen derselben Maßnahme über Konten zusammenfassen. **Nicht** allein über `massnahme_id`: 11 IDs kommen unter mehreren Produkten vor (z. B. `KLIMA1` unter 8 Produkten mit verschiedenen PV-Anlagen, `AIBH012` unter 011204, 020701, 090101). [VERIFIED: Auswertung `investitionen.json` diese Session: `ids with >1 (produkt,name)`: `KLIMA1`, `BGAFB4`, `AIBH012`, `BAUG001`, `GRDST006`, `GRDST012`, `GRDST013`, `GRDST015`, `STRAß019`, `AIB00001`, `GRDST016`]
**Ergebnis:** 89 Auszahlungs-Maßnahmen, davon **59 mit Summe ≠ 0** in 2026–2029; Σ = 36.361.784 € = Σ GFP `auszahlungen_investitionen` 2026–2029 (12.280.484 + 16.803.100 + 6.565.600 + 712.600). Die 30 Maßnahmen mit Summe 0 (nur 2024/2025 oder 0) gehören nicht in die Liste (sie hätten Balkenlänge 0). Einzige negative Zahl: `011204/011204` 2024 Ist −213.001 (nicht im Anzeigezeitraum).
**Art-Filter auf Konto-Ebene:** `art` hängt an der Konto-Zeile; 8 Maßnahmen haben gemischte Arten (z. B. `STRAß022`: `bau` + `grundstuecke`, `FAHRZ002`: `ausstattung` + `investitionszuschuesse`). Deshalb erst nach `art`/`pb` filtern, **dann** bündeln, damit die gefilterte Summe nur die Konten der gewählten Art enthält; so bleibt „Σ je Art = GFP-Zeile“ gültig. Die Tabellenspalte „Art“ zeigt die Arten der gezeigten Konten.
**Quellen der Art-Werte** (verbatim, Auszahlungen): `('auszahlung', 'ausstattung'): 37, ('auszahlung', 'grundstuecke'): 29, ('auszahlung', 'bau'): 28, ('auszahlung', 'finanzanlagen'): 2, ('auszahlung', 'investitionszuschuesse'): 2, ('auszahlung', 'immaterielles'): 1` [VERIFIED: Auswertung `investitionen.json`; `typen.ts` Z. 286–288 nennt `art: string | null`]
**Gegenprobe je Art und Jahr 2025–2029 (exakt, diese Session):** `bau` = GFP `baumassnahmen`; `grundstuecke` = `erwerb_grundstuecke_gebaeude` (2025–2029; 2024 Ist: 409.499 vs. 409.500); `ausstattung` = `erwerb_bewegliches_anlagevermoegen`; `finanzanlagen` = `erwerb_finanzanlagen`; `investitionszuschuesse` = `aktivierbare_zuwendungen`; `immaterielles` = `sonstige_investitionsauszahlungen`. Der Test verwendet **2026–2029** (Anzeigezeitraum) bzw. 2025–2029; 2024 Ist ist wegen dokumentierter Befunde (`befunde.md`: −490.612 € Z. 23, −142.826 € Z. 30) ausgenommen.

```typescript
// Quelle: Struktur nach lib/drilldown.ts / lib/zeitreihen.ts (reine Funktion, liest nur JSON)
import { investitionen, haushalt } from '@/data/daten'
import type { Massnahme } from '@/data/typen'

export type Art = 'bau' | 'grundstuecke' | 'ausstattung' | 'sonstige'
/** Einzige Zuordnung Konto-Art -> Filterart (D-06); jede nicht genannte Art ist „sonstige“. */
const ART_FILTER: ReadonlyMap<string, Art> = new Map([
  ['bau', 'bau'],
  ['grundstuecke', 'grundstuecke'],
  ['ausstattung', 'ausstattung'],
])
export function filterArt(art: string | null): Art {
  return (art !== null && ART_FILTER.get(art)) || 'sonstige'
}
export interface Vorhaben { produkt: string; id: string; name: string; pb: string; summe: number; jahre: (number | null)[] }
export function baueVorhaben(sicht: { pb: string | null; art: Art | null }): Vorhaben[] {
  const ab = haushalt.jahre.indexOf(haushalt.haushaltsjahr) // Planjahre = ab Haushaltsjahr, nicht „2026“ im Code
  const je = new Map<string, Vorhaben>()
  for (const m of investitionen.massnahmen) {
    if (m.richtung !== 'auszahlung') continue
    if (sicht.pb !== null && m.pb !== sicht.pb) continue
    if (sicht.art !== null && filterArt(m.art) !== sicht.art) continue
    const schluessel = `${m.produkt}/${m.massnahme_id}`
    // … je Schlüssel Jahreswerte addieren, summe = Σ werte[ab..]
  }
  return [...je.values()].filter((v) => v.summe !== 0).sort((a, b) => b.summe - a.summe)
}
```

### Pattern 2: Bindungsgrad-Summen (D-01) ohne Neuberechnung

**What:** je Produkt `berechnet.zuschussbedarf[jahrIndex]`; Balken summiert nur Werte > 0; Überschuss-Liste = Werte < 0; ein einziger benannter Ausschluss für das Finanzierungsprodukt (160101) „an genau einer Stelle“. Namen/PB-Farben aus Daten (`produkt.pb`, `farbeFuerPb`).
**Erwartete Werte 2026** [VERIFIED: Auswertung `haushalt.json` + `produkte.json` diese Session]:

| Bindungsgrad | Produkte (>0) | Σ Zuschussbedarf >0 | Produkte ≤ 0 |
|---|---|---|---|
| pflichtig (31) | 29 | 6.358.143 | 110101 (−60.540), 160101 (−20.225.500) |
| teils (15) | 15 | 4.491.669 | — |
| freiwillig (17) | 15 | 2.436.628 | 011202 (−59.900), 011204 (−988.175) |
| **Σ Balken** | 59 | **13.286.440** | Überschussliste (ohne 160101): −1.108.615 |

Ohne die Vorzeichenregel ergäbe „pflichtig“ 6.358.143 − 20.286.040 = −13.927.897 (= „−13,9 Mio. €“ aus D-01 bestätigt). **Der Balkenwert 13,3 Mio. € ist nicht der Gesamt-Zuschussbedarf** (`GESAMT.berechnet.zuschussbedarf[2026]` = 2.953.506): der Satz unter dem Balken muss das klarstellen, sonst stolpern Leser:innen über die Differenz (die 20,2 Mio. € Überschuss aus 160101 und KL 11,0 Mio. liegen nicht im Balken).
**Spec-Konflikt:** UI-SPEC-Backstop sagt „Überschussliste enthält genau die Produkte mit negativem Zuschussbedarf“; D-01 nennt für 2026 nur 011202, 011204, 110101 (ohne 160101). **D-01 gilt**: der benannte Ausschluss greift in Balken **und** Liste. Der Code `160101` existiert bereits als `ZEITREIHEN_PRODUKT` in `lib/zeitreihen.ts` („Produkt, dessen Grundzahlen die Steuerarten … führt“); entweder dieselbe Konstante wiederverwenden oder in eine gemeinsame Stelle (`lib/produkt.ts`) verschieben, nicht ein zweites Literal anlegen. Ein Test sichert: Konstante verweist auf ein Produkt mit Zuschussbedarf < 0 im Haushaltsjahr.

### Pattern 3: Rückgang der allgemeinen Rücklage und HSK-Bezug (D-14)

**Semantik (verifiziert):** `eigenkapital.posten[*].werte[i]` ist für die Rücklagenzeilen der Bestand **zu Jahresbeginn**, `jahresergebnis` das Ergebnis des Jahres, `gesamt_vorbericht.werte[i]` = Σ Eigenkapital am **Jahresende**. Beleg 1: `Summe(t) = AR(t) + Verrechnung(t) + Ausgleich(t) + JE(t)` gilt in allen sechs Spalten exakt (39.522.991 − 476.327 + 2.132.213 − 2.353.506 = 38.825.371 für 2026). Beleg 2: S. 24 „Die Allgemeine Rücklage wird Ende 2026 noch einen Bestand von rd. 38,8 Mio. € ausweisen“ = Spalte 2027 (38.825.371). Beleg 3: Satzung § 4 (S. 9) nennt die Verringerung der Ausgleichsrücklage **2026** (2.132.213 €), Spalte 2027 ist 0. Der bestehende Abgeleitet-Wert `ausgleichsruecklage_minderung_haushaltsjahr` nutzt dieselbe Lesart (Stand Haushaltsjahr minus Stand Folgejahr). [VERIFIED: PDF S. 311, 24, 9; `erklaerungen.md`; `texte.py` Z. 275–280]

**Gedruckte Sollwerte (S. 23):** „Entwicklung aus Sicht des Haushaltes 2026 … Nach der Konsolidierung“: Abbau/Zuführung Allgemeine Rücklage: 2026 −1,77 v. H. (Fußnote: inkl. Verrechnung NKF-CUIG 476.327 €), 2027 −4,23, 2028 −4,73, **2029 −10,04**. Der Satz dort: „Da nicht in zwei aufeinanderfolgenden Haushaltsjahren ein Eigenkapitalverzehr von über 5 v. H. zu verzeichnen ist, ergibt sich keine Verpflichtung zur Aufstellung eines Haushaltssicherungskonzeptes. Dieses wird jedoch nur durch die Erträge aus den Grundstücksverkäufen erreicht.“ [VERIFIED: PDF S. 23, verbatim]

**Formel (alle vier Jahre reproduzieren die gedruckten Werte, Rundung 2 Stellen, diese Session):**
`abbau(t) = max(0, −JE(t) − Ausgleich(t)) − Verrechnung(t)` (Verrechnung ist im Druck negativ), `rueckgang(t) = abbau(t) / AR(t)`. Ergebnis: 2026 697.620 / 39.522.991 = 1,765 %; 2027 1.642.528 / 38.825.371 = 4,231 %; 2028 1.758.827 / 37.182.843 = 4,730 %; 2029 3.557.700 / 35.424.016 = 10,043 %. Für `t < letztes Jahr` ist dasselbe `AR(t) − AR(t+1)`; der Test prüft beide Wege gegeneinander. Zusätzlich: Entnahme 2026–2029 gesamt = 221.293 + 6.959.055 = 7.180.348 € = „insgesamt 7,2 Mio. €“ (S. 24).
**Jahr-Zuordnung:** Der Rückgang gehört zu dem Jahr, dessen Spalte er berechnet (S. 23: „Jahr 2026 → 1,77“). **Nicht** „Rückgang gegenüber Vorjahr“ als Spaltendifferenz zur Vorspalte beschriften (verschöbe alles um ein Jahr und ließe 2029 aus). Das Diagramm zeigt die Planjahre ab Haushaltsjahr (2026–2029; 2024/2025 haben AR unverändert, Rückgang 0, Spalte 2025 trägt das widersprüchliche JE 0,00, siehe `befunde.md`).
**Schwellen:** Wortlaut S. 23 (zitiert § 76 GO NRW): „… um mehr als ein Viertel verringert wird oder in zwei aufeinanderfolgenden Haushaltsjahren geplant ist, den in der Schlussbilanz des Vorjahres auszuweisenden Ansatz der Allgemeinen Rücklage jeweils um mehr als ein Zwanzigstel zu verringern.“ Bezugsgröße = Ansatz der allgemeinen Rücklage in der Schlussbilanz des Vorjahres = `AR(t)` (Beginn des Jahres). Sekundärquellen nennen zusätzlich einen dritten Auslöser (allgemeine Rücklage im mittelfristigen Planungszeitraum aufgebraucht) und Änderungen durch das 3. NKF-Weiterentwicklungsgesetz [CITED: lexmea.de/en/gesetz/go-nrw/76, haufe.de, ifv.de — nur über Suchzusammenfassungen, die Gesetzestexte selbst lieferten HTTP 403]. Die App gibt nur **S. 23** wieder („Laut Vorbericht …“), nennt keine eigene Bewertung. Die Werte stehen als `meta.vorbericht_werte.hsk_schwelle_ein_jahr` (25) und `.hsk_schwelle_zwei_jahre` (5), `einheit: "prozent"`, `quelle: 23`; `_meta_eintragen` macht sie automatisch als `meta.vorbericht_werte.<schluessel>` für Textplatzhalter verfügbar (`|prozent` erwartet ganze Prozentpunkte). `lies_meta_json` prüft für `vorbericht_werte` nur ein Schlüsselnamensmuster (`_VORBERICHT_WERTE_SCHLUESSEL_MUSTER`) und die Blattregeln (`wert` ganzzahlig, `einheit` ∈ {`personen`, `ha`, `prozent`, `promille`, `euro`, `datum`}, `quelle` ≥ 1); eine Allowlist je Schlüssel gibt es dort nicht, die Schwellen brauchen also keine Schemaänderung [VERIFIED: `manuell.py` Z. 19, 55–80, 142–150; `texte.py` `_meta_eintragen`].
**Zwei-Jahres-Regel in den Daten:** 2028 = 4,73 %, 2029 = 10,04 %: nur 2029 liegt über 5 %. Das ist die Aussage des Vorberichts („nicht in zwei aufeinanderfolgenden Jahren“); die App zeigt Werte und Schwellen nebeneinander und kennzeichnet das Zitat. Die UI-SPEC-Aussage „jeweils unter 5 %“ (Offene Annahme 3) ist zu streichen.
**Polster-Satz:** Das „Jahr, ab dem die Ausgleichsrücklage aufgebraucht ist“ ist **Spalte der ersten 0 minus 1** (Ende 2026), nicht die Spalte selbst. Abgeleitet-Formel Vorschlag: `ausgleichsruecklage_aufgebraucht_jahr` (Format `jahr`) und `allgemeine_ruecklage_abbau_gesamt` (Summe `abbau` über die Planjahre, Format `mio`/`prozent`). Bisherige Texte nutzen Jahreszahlen im Schlüssel (`schulden.gesamt.2025`); für Texte über „das letzte Planjahr“ ist `jahr.letztes_jahr` als neuer Schlüssel sinnvoll (Konvention „keine Jahrgangswerte“), in `textwerte()` aus `jahre[-1]`.

### Pattern 4: Filterzustand in der URL (`pb`, `art`) nach `ansicht.ts`

`leseAnsicht` liest defensiv, nimmt nur Allowlist-Werte, setzt `bereinigt`, `useAnsicht` entfernt Ungültiges per `router.replace` und behält fremde Schlüssel und `hash`. Dasselbe Muster für `/investitionen`: `art` nur aus `bau | grundstuecke | ausstattung | sonstige`, `pb` nur aus den PB-Codes, die Auszahlungs-Maßnahmen haben (11 Stück: 01, 02, 03, 04, 06, 08, 09, 10, 12, 13, 15). Nachschlagen über `Map`/`Set`, nie Objekt-Indexierung (Prototyp-Schlüssel, Sicherheit V5). Filterwechsel = `router.replace` (kein Verlaufseintrag), `afterEach` ändert bei reinem Query-Wechsel weder Fokus noch Titel (`to.path === from.path && !to.hash` → return).

### Pattern 5: `MENUE` als Vereinigung (D-19)

```typescript
// Quelle: app/src/lib/menue.ts (bestehend) erweitert; Routennamen aus 06-UI-SPEC „Routes and URL State“
export interface MenueLink { typ: 'link'; name: string; text: string; mitJahr: boolean }
export interface MenueGruppe { typ: 'gruppe'; text: string; eintraege: readonly MenueLink[] }
export type MenueEintrag = MenueLink | MenueGruppe
export const MENUE: readonly MenueEintrag[] = [
  { typ: 'link', name: 'start', text: 'Start', mitJahr: false },
  { typ: 'link', name: 'einnahmen', text: 'Woher?', mitJahr: true },
  { typ: 'link', name: 'ausgaben', text: 'Wofür?', mitJahr: true },
  { typ: 'link', name: 'geldfluss', text: 'Geldfluss', mitJahr: true },
  { typ: 'gruppe', text: 'Mehr wissen', eintraege: [
    { typ: 'link', name: 'entwicklung', text: 'Entwicklung', mitJahr: false },
    { typ: 'link', name: 'investitionen', text: 'Investitionen', mitJahr: false },
    { typ: 'link', name: 'rat-entscheidet', text: 'Rat entscheidet', mitJahr: false },
    { typ: 'link', name: 'stellenplan', text: 'Stellenplan', mitJahr: false },
  ] },
  { typ: 'link', name: 'glossar', text: 'Glossar', mitJahr: false },
]
```
`App.vue` rendert heute `v-for="eintrag in MENUE" :key="eintrag.name"` und `menueZiel(eintrag)`; beides muss auf die Union umgestellt werden (Schlüssel für Gruppe = `text`). `menue.test.ts` prüft heute die flache Reihenfolge und `mitJahr` genau für `einnahmen`, `ausgaben`, `geldfluss`; der Test ist anzupassen (Reihenfolge, Routenname existiert im Router, jede Route der Phase im Menü, kein doppelter Name über Gruppen hinweg). [VERIFIED: `menue.ts` Z. 1–25, `App.vue` Template-Abschnitte `<nav v-if="!schmal">` und `wa-drawer`, `menue.test.ts`]

### Pattern 6: Stellen-Summen in Hundertstel (kein Float-Drift)

Jede Summe als ganze Hundertstel (`Math.round(x * 100)`) rechnen und erst zur Anzeige durch 100 teilen. Beleg: `Σ stellen` der Teil-A/B-Zeilen 2026 ergibt in JavaScript 62,91, die Summe derselben Werte über die PB-Zeilen **62,90999999999999**, 2025 **62,129999999999995**, besetzt **56,62999999999999** [VERIFIED: Node-Lauf diese Session]. Nur Zeilen mit `merkmal === 'stellen'` (bzw. `'besetzt'`) summieren: `davon_ausgesondert` (B 3, 1,0) und die vier Nachwuchs-Zeilen (`stellen: null`) dürfen nie eingehen. Zwei Summenwege müssen übereinstimmen: Σ Teil A/B (ohne `produktbereich`) = Σ Zeilen mit `produktbereich` (2026: 8 + 52,26 + 2,65 = 62,91; PB-Summen je Teil identisch). Weitere Gegenprobe aus dem PDF: S. 34 „8,0 Stellen für Beamtinnen und Beamte … sowie 54,91 vollzeitverrechnete Stellen für tariflich Beschäftigte (einschl. Sozial- und Erziehungsdienst)“ und S. 35 „Erhöhung um rd. 0,8 VZÄ“ (62,91 − 62,13 = 0,78). [VERIFIED: PDF S. 34/35]

### Pattern 7: Neue manuelle Tabelle `zuschuesse_lfd_zwecke` (Muster `kita_zuschuesse`)

Berührungspunkte (jeweils gelesen, nicht nur gesucht): `schema.py` (Konstante analog `KITA_ZUSCHUESSE_CSV`, Z. 49), `pruefung.py` (Import Z. 42, Lader Z. 2549, Querprüfung analog `_pruefe_regel5_kita_gegen_transfer` Z. 1043 ff. samt Konstante `REGEL5_KITA_POSTEN` Z. 1040 und dem Aufruf Z. 1461), `app_daten.py` (`vorbericht_quellen` Z. 971 direkt nach `kita_zuschuesse`; `gep_zeile` bleibt `None`, da keine GEP-Zeile), README-Abschnitt in `daten/manuell/README.md`, Tests `test_manuell.py` (Tabellenmenge/(jahr,wertart)), `test_pruefung.py` (grün + manipulierte Abweichung rot), `test_app_daten.py` (Reihenfolge der `vorbericht`-Schlüssel), danach `alle.py --jahr 2026` und Commit der regenerierten `daten/` und `app/src/data/*.json` (CI-Reproduzierbarkeitsgate). Format wie `kita_zuschuesse.csv`: Spalten `tabelle,position,posten,posten_name,ist_gesamt,jahr,wertart,betrag_teur,anmerkung,quelle`, nur Haushaltsjahr, `wertart` `ansatz` aus den Jahrgangs-Spaltenköpfen (nie von Hand), Gesamtzeile `ist_gesamt=true` mit 120 und `quelle=47`; die Gesamtzahl „120 T€“ ist im Fließtext von S. 47 gedruckt. Posten-Schlüssel nach README-Regel (klein, Umlaute ausgeschrieben, Nicht-Alphanumerisches zu `_`): z. B. `kulturtragende_vereine`, `vhs`, `jekits_eigenanteil_schule_fuer_musik`, `sportfoerderrichtlinie`, `zuschuesse_dritte_soziales_leben`, `schulsozialarbeit`, `ferienfreizeit_jugendliche`, `restaurierung_private_denkmale`. Die Schlüsselzuweisungs-Falle der Phase 4 gilt hier nicht: es gibt keine Rundungsdifferenz (Σ = Gesamt = Transferposten = 120).
**Anzeige:** „Weitere Zuschüsse“ der UI-SPEC kombiniert Kinder- und Jugendwerk (300, `zuschuss_kinder_jugendwerk`, Text S. 46: „rd. 288 T€ + rd. 12 T€“) und OGS (871) mit diesen acht Posten. Die acht sind **Teil** von „Zuschüsse für lfd. Zwecke“ (120), KJW und OGS sind **eigene** Transferposten; die Karte nennt die Herkunft je Gruppe (Seitenverweis S. 46 bzw. S. 47), sonst wirkt die Liste wie eine einzige Summe.

### Anti-Patterns to Avoid

- **Bündeln über `massnahme_id` allein** (Pitfall 2). **`gesamt` des Schuldenstands plus Liquiditätskredite addieren** (Pitfall 3).
- **Jahreszahlen im Quelltext** (`2026`, `2029`, „2027–2029 berechnet“): Wertart, berechnet-Flag, Planjahre immer aus `haushalt.jahre/wertarten` bzw. `schuldenstand.berechnet` ableiten.
- **Zahlen in Templates tippen** (`quelltext.test.ts` sperrt `\d … Mio./€/%` und gruppierte Zahlen im `<template>`; außerhalb Templates, z. B. Konstanten wie `15` für „größte 15“ in `<script>`, ist es erlaubt, sollte aber benannt sein).
- **Chart-Klick ohne Tastaturpfad:** Klick auf Balken → Produkt braucht die Tabelle mit Produktlinks.
- **Eigene Prozent- oder Euro-Formate** statt `format.ts`; **eigene Tooltip-HTML** statt `tooltipZeilen`; **`v-html`**.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Zahlenformat (Euro, Mio., %, VZÄ, Jahr) | `toLocaleString`-Aufrufe in Komponenten | `charts/format.ts` (`euro`, `euroKurz`, `prozent`, `vzae`, `jahr`, `formatiere`) | UI-05; `prozent` erwartet Bruch 0–1, `formatiere(…,'prozent')` ganze Prozentpunkte |
| Tooltips | String-Verkettung mit HTML | `charts/tooltip.ts::tooltipZeilen` | T-05-12 (XSS), ECharts setzt Formatter-Ergebnis als HTML |
| Horizontale Balken mit Direktwert | neue Balken-Builder | `charts/balken.ts::horizontaleBalkenOption`, `balkenHoehe` | Produktbalken, Maßnahmen, Stellen/Personal je PB; liefert `Zeilenzahl × 40 + 48 px`, Namensumbruch, `overflow: 'break'` |
| Zeitreihen-Stile Ist/Ansatz/Planung | neue Stil-Tabelle | Stil-Logik aus `SteuerZeitreihe.vue` (`STILE`, `LEGENDE_TEXT`) in ein gemeinsames Modul **herausziehen**, nicht kopieren | drei Komponenten dieser Phase brauchen sie |
| Deutsche Sortierung | `localeCompare` ohne Locale / Codepunktvergleich | `Intl.Collator('de')` (wie `glossar.ts`) | Umlaute |
| Abfrage-Validierung | `route.query.x as string` | Muster `leseAnsicht` (Allowlist, `erster()`, `bereinigt`) | Sicherheit V5 |
| Tabellenalternative | eigene `<table>` | `DatenTabelle` (`spalten`, `zeilen`, Slot `zelle`, `fussnote`, `leer*`) | Leerzustand, „–“/„kein Wert“, `gerundet` |
| Aufklapper, Hinweise | eigenes Akkordeon/Alert | `wa-details`, `wa-callout` | bereits importiert, zugänglich |
| Glossarverlinkung | Links von Hand | `GlossarBegriff` (Union `GlossarSchluessel` ⇒ Tippfehler = Typfehler) | `glossar.test.ts` prüft Verwendungen |
| Platzhaltertexte | String-Templates mit Zahlen | Pipeline-Text + `ErklaerText`/`rendereAbsatz` | Ziffernregel, Seitenverweis, Node-Gegenprobe |
| Schwellenlinie im Diagramm | `graphic`-Overlay | `markLine` an der Balkenserie | folgt der Achse automatisch |

**Key insight:** Alle Phase-6-Seiten sind Kombinationen vorhandener Bausteine; die Gefahr liegt in der **Datensemantik** (Schlüssel, Spaltenjahr, Summen), nicht in Optik. Jede Zahl, die auf der Seite steht, braucht einen Test gegen eine Planzeile oder gedruckte Zahl.

## Common Pitfalls

### Pitfall 1: Rücklagen-Spalten und Rückgangs-% um ein Jahr verschoben
**What goes wrong:** `Rückgang(t) = AR(t−1) − AR(t)` (UI-SPEC-Wortlaut „gegenüber Vorjahr“) ordnet 1,77 % dem Jahr 2027 zu (Vorbericht: 2026), lässt 2029 (10,04 %) aus und lässt die Aussage „unter 5 %“ falsch erscheinen.
**Why it happens:** Rücklagenzeilen sind Bestände zu Jahresbeginn, das Jahresergebnis steht in derselben Spalte (S. 311, Summe = Jahresende).
**How to avoid:** Pattern 3; Test gegen die vier gedruckten Werte aus S. 23; Spaltenüberschrift „Rückgang im Jahr“ statt „gegenüber Vorjahr“; Diagrammachse „Bestand zu Jahresbeginn“ (Caption).
**Warning signs:** Maximum des Rückgangs-Diagramms < 5 %; Balken für 2029 fehlt.

### Pitfall 2: `massnahme_id` ist nicht eindeutig
**What goes wrong:** Bündeln über `massnahme_id` allein fasst z. B. acht verschiedene PV-Anlagen (`KLIMA1`) oder dieselbe Baumaßnahme über mehrere Produkte zusammen, der Link auf `/produkt/:code` ist mehrdeutig.
**How to avoid:** Schlüssel `produkt/massnahme_id`; Test: Anzahl Gruppen = 89 (Auszahlung), davon 59 mit Summe ≠ 0; Σ = 36.361.784. **Deviation von D-07/UI-SPEC („massnahme_id“) ist am Plan festzuhalten.**
**Warning signs:** Eine Maßnahme verlinkt auf das „falsche“ Produkt; Test Σ je Art ≠ GFP.

### Pitfall 3: Schuldenstand `gesamt` enthält keine Liquiditätskredite
**What goes wrong:** Gestapelte Säule Investitionskredite + NRW.Bank + Liquiditätskredite mit „Gesamtsumme über der Säule“ ergibt 2025 8,13 Mio. €, die Kennzahl daneben sagt 7,71 Mio. €.
**Why it happens:** `gesamt = investitionskredite + nrw_bank` (2025: 6.879.000 + 831.000 = 7.710.000; Liquiditätskredite 418.000 stehen separat) und der Vorbericht (S. 24) definiert den Schuldenstand genauso, ohne Liquiditätskredite. [VERIFIED: `schuldenstand` und PDF S. 24, 310]
**How to avoid (Empfehlung):** Säulen = Investitionskredite + NRW.Bank mit Summenbeschriftung `gesamt`; Liquiditätskredite (nur 2024–2026 gedruckt, danach `null`) als eigene Zeile in Tabelle und Caption („kurzfristig, nicht im Schuldenstand“), nicht gestapelt. D-09 („Liquiditätskredite ab 2027 fehlen, nicht als 0“) bleibt erfüllt. **Dies ändert UI-SPEC E9; Entscheidung am Plan.**

### Pitfall 4: Jahresergebnis vor oder nach Minderaufwand
**What goes wrong:** UI-SPEC (Untertitel „vor globalem Minderaufwand“) lässt den Balken aus `zeilen.jahresergebnis` lesen: 2024 +191.990, 2025 −1.896.120, 2026 −2.953.506, … 2029 **−4.217.700**. ROADMAP SC 1, Spez. 6.12 („Defizit wächst bis 2029 auf −3,56 Mio. €“), D-11 (2029: −3.557.700) und die Startseite („Defizit nach Minderaufwand“, `ergebnis_nach_minderaufwand`) nennen die Werte **nach** Minderaufwand: −191.990… 2029 **−3.557.700**; Satzung § 4 und S. 311/S. 23 ebenfalls. [VERIFIED: `haushalt.json` `ergebnisplan.GESAMT.zeilen`, `kennzahlen.ts` Z. 80–120]
**Folge:** Erträge/Aufwendungen aus `berechnet` (`ertraege`, `aufwand`) schließen den globalen Minderaufwand **nicht** ein (2029: 31.225.772 − 35.443.472 = −4.217.700). Linien (vor) und Balken (nach) liegen deshalb nicht auf derselben Differenz.
**How to avoid:** siehe Open Question 1 (Empfehlung: Balken = `ergebnis_nach_minderaufwand`, Linien wie `/start`, Callout mit `globaler_minderaufwand` und der Differenz; Tabelle zeigt beide Ergebniszeilen und den Minderaufwand).

### Pitfall 5: Float-Drift bei VZÄ-Summen
Siehe Pattern 6. Tests mit `toBe(6291)` auf Hundertstel statt `toBe(62.91)`.

### Pitfall 6: Kreisumlage 2026 ist netto und wirkt wie eine Entlastung
**What goes wrong:** Die Reihe 11.212 / 10.163 / **10.147** / 11.932 / 12.349 / 12.807 T€ zeigt 2026 einen Rückgang; Veränderung 2024 → 2029 (+14,2 %) klingt harmlos. Fußnote S. 46: Rückstellung 1.325.478 € aufgelöst, Umlage 2026 liegt bei 11,5 Mio. €; `meta.kreisumlage.brutto` = 11.472.478.
**How to avoid:** Caption in der Kreisumlage-Karte (Platzhalter aus `meta.kreisumlage.*`, Seitenverweis S. 46) und `gerundet`-Kennzeichnung („rd.“) der Werte (T€ × 1000). Die Reihe bleibt in den Daten netto (Quelle `vorbericht.transferaufwendungen.kreisumlage`, identisch mit `KL.kreisumlage`).

### Pitfall 7: Gruppensortierung „aufsteigend“ widerspricht der gedruckten Position
**What goes wrong:** D-17 verlangt aufsteigende Sortierung, UI-SPEC „aufsteigend nach der gedruckten `position`“. Die gedruckte Reihenfolge läuft **absteigend** (Tarif: Position 1 = „14“, … 12 = „1“; Beamte: B 3, A 14, A 13, A 12, A 10, A 8; S-Gruppen: S 12, S 11). Aufsteigend nach `position` ergäbe E 14 zuerst.
**How to avoid:** Absteigend nach `position` sortieren (ergibt 1 → 14, A 8 → B 3, S 11 → S 12; `9a < 9b < 9c` stimmt, weil 9c Position 4, 9b 5, 9a 6 hat), nicht per Regex. Test mit den erwarteten Gruppenfolgen. Tarif-Labels sind nackte Zahlen („14“, „9c“), die Überschrift „Entgelt“ trägt „E“ nicht; im Glossar `entgeltgruppen` erklären.

### Pitfall 8: Synthetischer Knoten `KL` ist `ebene: "PB"`
**What goes wrong:** Filter `ebene === 'PB'` liefert 16 Knoten inklusive „Weitergabe an Kreis und Land“ (Personalaufwand 0). `farbeFuerPb` kennt `KL`, wirft also nicht. Stellen/Personal/Maßnahmen-Filter würden KL als Aufgabenbereich führen.
**How to avoid:** Aufgabenbereiche wie in `kennzahlen.ts`: `knoten.ebene === 'PB' && knoten.eltern === 'GESAMT' && !knoten.synthetisch`.

### Pitfall 9: `texte.json` führt nur verwendete Werte, Formatkürzel sind an drei Stellen fixiert
**What goes wrong:** Neuer Platzhalter ohne Schlüssel in `textwerte()` oder ABGELEITET → `TexteFehler` (gewollt); neues Formatkürzel wird nur an einer Stelle ergänzt → `test_formatkuerzel_wie_format_ts` rot. Jede Textänderung ändert `texte.json` und muss regeneriert und eingecheckt werden (CI-Gate).
**How to avoid:** Keine neuen Kürzel (nur `euro|mio|zahl|jahr|prozent|promille|vzae`); neue Formeln in `ABGELEITET` mit relativen Namen (`…_haushaltsjahr`, `…_letztes_jahr`); Texte mit `Quelle: S. n, S. m` (einzelne Seiten, keine Spannen); nach jeder Änderung `alle.py --jahr 2026` und `git diff --exit-code -- daten app/src/data`. Beachte: der Überschuss-Satz der UI-SPEC enthält einen Betrag, dessen Regel („ohne 160101“) auch die App braucht; entweder den Satz ohne Zahl formulieren oder die Summe in Python **und** TS rechnen und gegeneinander testen (Doppelhaltung vermeiden: Empfehlung zahlenfreier Pipeline-Satz plus Betrag in der Tabelle).

### Pitfall 10: `ErklaerText` blendet Texte mit Platzhaltern aus, wenn `jahr` gesetzt und ≠ Haushaltsjahr
Auf den vier neuen Seiten **kein** `jahr`-Prop übergeben (es gibt keinen Jahr-Umschalter); sonst erscheint der Text nie oder immer nach Jahrbindung. (`textFuerJahr` in `lib/texte.ts`.)

### Pitfall 11: Diagramme in geschlossenen `wa-details` und Zweizeilen-Achse bei 360 px
Drei Produktbalken-Diagramme liegen in geschlossenen Aufklappern. `BaseChart` nutzt `autoresize`; trotzdem Layout beim Öffnen visuell prüfen, notfalls Diagramm erst nach `wa-show` rendern ([ASSUMED], A2). Die Zweizeilen-Achse „2026 / Planung“ mit sechs Kategorien braucht bei 14 px ca. 52 px je Wort „Planung“; bei 360 px stehen nach y-Achse und Rand etwa 250 px für sechs Kategorien (≈ 41 px) zur Verfügung: **Überlappung wahrscheinlich** ([ASSUMED], A3). Absicherung: `overflow: 'break'`/`interval: 0`, manuelle 360-px-Prüfung als Verifikationsschritt, Fallback gekürzte Wertart („Plan“).

### Pitfall 12: Baseline-Dauer
Die volle Pipeline-Suite braucht in dieser Sandbox ca. 5,5 Minuten (528 Tests). Pläne sollen gezielte Dateien (`pytest tests/test_manuell.py tests/test_pruefung.py tests/test_app_daten.py tests/test_texte.py -x -q`) als Task-Verifikation und die volle Suite nur als Wellen-/Phasengate nutzen. [VERIFIED: Lauf `528 passed in 321.34s`]

## Code Examples

### Rückgang der allgemeinen Rücklage (reine Funktion, getestet gegen S. 23)

```typescript
// Quelle: Eigenkapitalübersicht S. 311; Formel verifiziert gegen S. 23 (Abbau/Zuführung, v. H.)
import { haushalt } from '@/data/daten'

function posten(schluessel: string): readonly number[] {
  const p = haushalt.eigenkapital.posten.find((e) => e.posten === schluessel)
  if (p === undefined) throw new Error(`eigenkapital.posten fehlt: ${schluessel}`)
  return p.werte.map((w) => w ?? 0)
}
/** Anteil (0–1), mit dem die allgemeine Rücklage im Jahr `i` sinkt; Bezug: Bestand zu Jahresbeginn. */
export function rueckgang(i: number): number {
  const ar = posten('allgemeine_ruecklage')[i]!
  const ausgleich = posten('ausgleichsruecklage')[i]!
  const verrechnung = posten('verrechnung_bilanzierungshilfe')[i]! // im Druck negativ
  const ergebnis = posten('jahresergebnis')[i]!
  const abbau = Math.max(0, -ergebnis - ausgleich) - verrechnung
  return ar === 0 ? 0 : abbau / ar
}
// vitest: Math.round(rueckgang(i) * 10000) / 100 für die Planjahre = 1.77, 4.23, 4.73, 10.04 (S. 23)
```
Die Posten-Schlüssel stammen aus der Ausgabe `allgemeine_ruecklage`, `verrechnung_bilanzierungshilfe`, `sonderruecklagen`, `ausgleichsruecklage`, `bilanzieller_verlustvortrag`, `jahresergebnis` [VERIFIED: `haushalt.json` `eigenkapital.posten` diese Session].

### Zweizeilige Jahresachse (Wertart als primärer Träger)

```typescript
// Quelle: UI-SPEC „Chart Contract“, Wertart-Mapping aus lib/jahr.ts (WERTART_NAMEN: ergebnis→Ist, ansatz→Ansatz, planung→Planung)
xAxis: {
  type: 'category',
  data: haushalt.jahre.map((j, i) => `${jahr(j)}\n${wertartName(haushalt.wertarten[i]!)}`),
  axisLabel: { interval: 0, hideOverlap: false },
}
```

### Schwellenlinie

```typescript
// markLine: BarSeriesOption.markLine (echarts 6.1.0 types: MarkLine1DDataItemOption { yAxis?: number | string })
markLine: {
  silent: true, symbol: 'none',
  lineStyle: { color: SCHWELLE_FARBE, width: 2, type: [6, 4] },
  label: { formatter: schwelleBeschriftung, position: 'insideEndTop' },
  data: [{ yAxis: schwelleProzent }], // aus meta.vorbericht_werte.hsk_schwelle_zwei_jahre, nie als Literal
}
```
Registrierung: `MarkLineComponent` in `use([...])` von `echartsTheme.ts` ergänzen (einzige Stelle).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `grid.containLabel` | `outerBoundsMode: 'same'` + `outerBoundsContain: 'axisLabel'` | ECharts 6 | bereits im Bestand (`balken.ts`, `SteuerZeitreihe.vue`); in neuen Optionen so übernehmen |
| `wa-dropdown` für Navigation | Disclosure-Muster | UI-SPEC Phase 6 | `role="menu"` ist Anwendungsmenü-Semantik |
| Quellmix Grundzahlen + Vorbericht (`SteuerZeitreihe`) | einheitlich 2024–2029 (D-12) | Phase 6 | `PostenZeitreihe` darf **nicht** `baueZeitreihe` unverändert aufrufen (die Funktion hängt Grundzahl-Jahre 2022–2023 an); eigene Reihe aus `haushalt.jahre` bauen |

**Deprecated/outdated:** `grid.containLabel` (ECharts 6), feste `font-weight: 600` und `--wa-font-weight-semibold` (Token-Hygiene).

## Scoping Recommendation for the Planner

Vorschlag zur Zerlegung (Wellen, Abhängigkeiten; Plan-Anzahl und Zuschnitt bleiben Planerentscheidung):

1. **Welle 1 (Pipeline, parallel zu App-Fundament):**
   - *Plan A, Einzelzuschüsse (RAT-03):* CSV, Schema, Regel 5, README, Schritt 07, Tests, regenerierte Daten. Kein Checkpoint nötig (reine Abschrift, Σ = 120 T€ exakt).
   - *Plan B, Meta-Schwellen, Texte, Glossar (ENTW-03, RAT-04, UI-04, STEL, INV-04):* `meta.json` (+2), ABGELEITET-Formeln, neue Abschnitte in `erklaerungen.md`/`glossar.md`, `GLOSSAR_SCHLUESSEL`-Tupel, Tests; endet mit **Checkpoint** (blocking-human) zur fachlichen Abnahme (D-20). Wegen der Abnahme früh einplanen, damit die Seiten-Pläne danach nur noch auf feste Schlüssel verweisen.
   - *Plan C, App-Fundament:* `menue.ts`-Union + `App.vue`/`MenueGruppe` + Router (4 Routen), `echartsTheme.ts` (+`MarkLineComponent`, `BINDUNG_FARBEN`, `BERECHNET_DECAL`, `SCHWELLE_FARBE`), gemeinsames Zeitreihen-Stilmodul, `HinweisNichtImHaushalt`, Tests (`menue`, `farben`, `stiltokens`, `quelltext`-Seitenliste).
2. **Welle 2 (vier unabhängige Seiten, parallel):** Entwicklung (Lib `entwicklung.ts` + `ruecklagen.ts`), Investitionen (`investitionen.ts` + `schulden.ts` + Filter), Rat entscheidet (`bindungsgrad.ts` + `zuschuesse.ts` + Block), Stellenplan (`stellen.ts`). Jede Seite: Lib + Test zuerst, dann Komponenten, dann Seite.
3. **Welle 3 (Integration/Gate):** Hinweisbox in `/ausgaben` und `/einnahmen`, Glossar-Anker, `quelltext.test.ts`-Listen, Reproduzierbarkeitsgate, vollständige App-Kette in Scratch-Kopie, manuelle 360-px-Prüfung (Achsen, Menü), Human-Verify am Phasenende (`human_verify_mode: end-of-phase`).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `chevron-down` als eigenes Inline-SVG/CSS statt Font-Awesome-Datei ist lizenz- und netzseitig unproblematisch (Font Awesome Free 7.3.1 ist CC BY 4.0; die Datei liegt nicht in `node_modules`) | Package Legitimacy Audit | gering: nur Optik/Lizenzhinweis |
| A2 | `BaseChart` (`autoresize`) rendert Diagramme in anfangs geschlossenen `wa-details` nach dem Öffnen korrekt | Pitfall 11 | mittel: leere/zu schmale Balken im Aufklapper; Fallback: Diagramm erst bei `wa-show` mounten |
| A3 | Die Zweizeilen-Achse („2026 / Planung“) überlappt bei 360 px mit sechs Kategorien; Fallback „Plan“ | Pitfall 11 | mittel: Barrierefreiheit/Lesbarkeit; durch manuelle 360-px-Prüfung abfangen |
| A4 | Der dritte HSK-Auslöser (allgemeine Rücklage im Planungszeitraum aufgebraucht) und Änderungen durch das 3. NKF-Weiterentwicklungsgesetz stammen nur aus Suchzusammenfassungen von Sekundärquellen (Gesetzestexte HTTP 403); **die App zitiert nur S. 23** | Pattern 3 | gering, solange die App keinen eigenen Rechtsstand behauptet; bei Aufnahme eines dritten Auslösers erst gegen gesetze.nrw.de prüfen |
| A5 | „Der Bindungsgrad ist eine Selbstauskunft der Verwaltung“: das PDF druckt den Bindungsgrad als Feld der Produktinformationen (z. B. S. 72), nennt ihn aber nicht „Selbstauskunft“; die Formulierung stammt aus `SPEZIFIKATION.md` §6.11 | Phase Requirements RAT-04 | gering; Text geht durch den Abnahme-Checkpoint |
| A6 | „Abwassergebühren erscheinen nicht im Haushalt“ (Hinweisbox `einnahmen`) stammt aus `SPEZIFIKATION.md` §3.7; das PDF belegt nur den separaten TEO-Wirtschaftsplan (S. 14) und die Eigenkapitalverzinsung (S. 33). Auf S. 36 steht „Abwassergebühren 296 … 363“ als **Aufwand** der Gemeinde (Sachaufwand), das widerspricht der Aussage nicht (Ertragsseite fehlt) | UI-04 | gering; Wortlaut am Checkpoint bestätigen |
| A7 | Das Rückgangs-Diagramm zeigt nur die Planjahre ab Haushaltsjahr (2026–2029, wie S. 23); 2024/2025 entfallen | Pattern 3 | gering; Gestaltungsentscheidung im Plan festhalten |
| A8 | Die Verwendung von `prozent` (1 Nachkommastelle) statt zwei Nachkommastellen wie S. 23 ist für Leser:innen akzeptabel | Standard Stack, Alternatives | gering; sonst `prozent2` an drei Stellen ergänzen |

## Open Questions

1. **Jahresergebnis-Balken: vor oder nach globalem Minderaufwand?** (Pitfall 4)
   - Was wir wissen: UI-SPEC (approved) liest `zeilen.jahresergebnis` (vor; 2029: −4.217.700 €). ROADMAP SC 1, Spez. 3.3/6.12, D-11, Startseite, Satzung § 4, S. 23 und S. 311 nennen −3.557.700 € (nach; 2026: −2.353.506 €). Erträge/Aufwand der Linien (`berechnet`) sind ohne Minderaufwand und ergeben die „vor“-Differenz.
   - Unklar: welche Variante der Nutzer will.
   - **Empfehlung:** Balken = `zeilen.ergebnis_nach_minderaufwand` (stimmt mit Satzung, ROADMAP und `/start` überein, 2029 = −3.557.700). Linien bleiben „vor Minderaufwand“ wie `/start`. Karte nennt „nach globalem Minderaufwand“; Callout (Text `globaler_minderaufwand`) erklärt die Differenz; die Tabelle zeigt Erträge, Aufwendungen, Ergebnis vor Minderaufwand, globalen Minderaufwand und Ergebnis nach Minderaufwand. UI-SPEC-Untertitel und -Callout entsprechend anpassen. Vor der Umsetzung kurz bestätigen lassen (billig, bevor Komponenten stehen).
2. **Bündelungsschlüssel `(produkt, massnahme_id)` statt `massnahme_id`** (Pitfall 2): technisch zwingend (Links auf `/produkt/:code`, KLIMA1). **Empfehlung:** so umsetzen und in der Plan-Aufgabe als bewusste Abweichung von D-07/UI-SPEC vermerken; Zeilen mit Summe 0 (2026–2029) nicht listen.
3. **Liquiditätskredite im Schuldenstand-Diagramm** (Pitfall 3): **Empfehlung:** nicht stapeln, Gesamtsumme = `gesamt`, Liquiditätskredite als Tabellenzeile/Caption (nur bis Ende des Haushaltsjahres gedruckt, danach „–“).
4. **Beschriftung der Rücklagen-Säulen:** gedruckte Spalte (Bestand zu Jahresbeginn, Wertart der Spalte) oder abgeleiteter Bestand zum Jahresende (Ende t = Spalte t+1; Ende 2029 = Summe Eigenkapital 31.866.316 €)? **Empfehlung:** gedruckte Spalten mit Caption „Bestand zu Jahresbeginn“ (keine abgeleiteten Werte, 1:1 prüfbar), Polster-Satz in Jahresende-Sprache („Ende 2026“). Am Abnahme-Checkpoint mit vorlegen.
5. **Prozent-Genauigkeit** (A8): 1 oder 2 Nachkommastellen. Empfehlung 1 (kein neues Formatkürzel).
6. **Etikett „berechnet“ an Pro-Kopf-Schulden:** 656 € steht auf S. 25 gedruckt („rund 656 €“); `pro_kopf` ist abgerundet (7.710.000 // 11.741). **Empfehlung:** Kachel Ende 2025 ohne Etikett mit Seitenverweis S. 25; für 2026 ff. (nicht gedruckt) Etikett „berechnet“. Der Gesamtbetrag 7,71 Mio. € ist die Summe zweier gedruckter T€-Werte (S. 310: 6.879 + 831) und im Text als „ungefähr 7,7 Mio. €“ gedruckt (S. 24).
7. **„Ortsteil Brock“-Filter:** nicht in Phase 6; REQUIREMENTS führt ihn als v2 (ERW-02). Empfehlung: weglassen.
8. **Chevron-Icon** (A1): eigenes SVG/CSS statt Download.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | App-Tests/Build | ✓ | 22.22.1 (`app/.nvmrc`: 22) | — |
| npm + Registry | `npm ci` in Scratch-Kopie | ✓ | Registry HTTP 200 | — |
| uv | Pipeline | ✓ | 0.9.26 (= CI-Pin) | — |
| Python-venv `pipeline/.venv` (pdfplumber 0.11.10, polars, typer) | PDF-Lesen, pytest | ✓ | Python ≥ 3.12 | — |
| `raw_data/haushalt-2026.pdf` | Abschrift S. 47, Prüfung | ✓ | 1-basierte Seiten lesbar | — |
| `app/node_modules` im Repo | App-Checks | ✗ (macOS-Binaries) | — | **Scratch-Kopie:** `S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app \| tar -xf - -C "$S" && npm --prefix "$S/app" ci --no-audit --no-fund` (wie Phase 5) |
| Externe Gesetzestexte (recht.nrw.de, gesetze.io) | Gegenprüfung § 76 GO NRW | ✗ (HTTP 403 bzw. Netzwerkrichtlinie) | — | S. 23 des Vorberichts zitiert den Wortlaut; Gegenprüfung am Checkpoint durch den Nutzer |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** `app/node_modules` (Scratch-Kopie), Gesetzestext-Zugriff (S. 23).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | vitest 5.0.3 (App, `environment: 'node'`, `include: ['src/**/__tests__/*.test.ts']`) und pytest (Pipeline) |
| Config file | `app/vitest.config.ts`, `app/tsconfig.vitest.json`; `pipeline/pyproject.toml` |
| Quick run command | App: Scratch-Kopie, dann `npm --prefix "$S/app" run test -- <datei>` (Baseline 25 Dateien/1031 Tests, < 1 s). Pipeline: `uv run --directory pipeline pytest tests/<datei>.py -x -q` |
| Full suite command | `uv run --directory pipeline pytest -q` (≈ 5,5 min, 528 Tests) **plus** `uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data` (kein Diff, keine untracked) **plus** App-Kette in Scratch-Kopie (`npm ci`, `type-check`, `lint`, `format:check`, `test`, `build`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ENTW-01 | Reihen = `haushalt.jahre`; Balken nach Minderaufwand (2029: −3.557.700), Erträge/Aufwand wie `/start`; Wertart je Jahr aus Daten | unit | vitest `entwicklung.test.ts` | ❌ Wave 0 |
| ENTW-02 | Quellen je Posten identisch zu `/einnahmen` bzw. `/ausgaben`; Veränderung 2024→2029 %; Guard Ausgangswert 0/`null` → „–“; Kreisumlage 2026 netto vermerkt | unit | vitest `entwicklung.test.ts` | ❌ Wave 0 |
| ENTW-03 | `rueckgang(i)` = gedruckte S.-23-Werte (1,77/4,23/4,73/10,04); Σ-Identität je Spalte; Jahr der ersten 0 minus 1 = Ausgleichsrücklage aufgebraucht; Schwellen aus `meta.vorbericht_werte` mit `quelle` 23; kein festes Jahr im Quelltext | unit + pytest | vitest `ruecklagen.test.ts`; `pytest tests/test_manuell.py -k hsk` | ❌ Wave 0 |
| INV-01 | 89 Gruppen / 59 mit Summe ≠ 0; Σ 2026–2029 = Σ GFP `auszahlungen_investitionen`; Σ je Art = jeweilige GFP-Zeile (2025–2029); Filter `pb`/`art` Allowlist, ungültig → „Alle“; jede Zeile hat Produktlink | unit | vitest `investitionen.test.ts` | ❌ Wave 0 |
| INV-02 | Σ `ve_faelligkeiten` = 11.600.000 = `ve.gesamt`; Σ 2027 = 9.400.000, 2028 = 2.200.000; jede VE-Zeile findet ihre Maßnahme (`produkt`, `massnahme_id`) | unit | vitest `investitionen.test.ts` | ❌ Wave 0 |
| INV-03 | Zeitreihen-Länge = `jahre`; Σ Einzahlungs-Aufteilung = `einzahlungen_investitionen` (2025–2029 exakt, 2024 ±1 €); nie im selben Diagramm wie Ergebnisplan (Strukturtest über Optionen) | unit | vitest `investitionen.test.ts` | ❌ Wave 0 |
| INV-04 | `gesamt = investitionskredite + nrw_bank`; Etikett „berechnet“ genau bei `berechnet[i] === true`; `null` bleibt „–“; 656 = Regel 9 | unit + pytest | vitest `schulden.test.ts`; vorhandener Regel-9-Test | ❌ Wave 0 (vitest) |
| RAT-01 | Segmente 6.358.143 / 4.491.669 / 2.436.628; Σ = Σ positiver Zuschussbedarfe ohne Finanzierungsprodukt; Überschussliste = Produkte < 0 ohne Finanzierungsprodukt; keine Neuberechnung (Werte = `berechnet`) | unit | vitest `bindungsgrad.test.ts` | ❌ Wave 0 |
| RAT-02 | KL-Kacheln = `lib/kreisumlage.ts`; Sozialleistungen = `vorbericht...sozialleistungen`; Kachel mit 0/`null` entfällt | unit | vitest `kreisumlage.test.ts` (erweitert) / neu | ✅ erweitern |
| RAT-03 | Σ acht Posten × 1000 = Transferposten `zuschuesse_laufende_zwecke` 2026 (120.000); Σ Kita = 559.000; Regel 5 grün und bei Manipulation rot | pytest + unit | `pytest tests/test_manuell.py tests/test_pruefung.py tests/test_app_daten.py -k zuschuess -q`; vitest `zuschuesse.test.ts` | ❌ Wave 0 |
| RAT-04 | Text existiert, trägt Seitenverweis, passt Ziffernregel | pytest | `pytest tests/test_texte.py -q` | ✅ erweitern |
| STEL-01 | Hundertstel-Summen 62,91 / 62,13 / 56,63; Differenzen; `davon_ausgesondert` und Nachwuchs nicht gezählt | unit | vitest `stellen.test.ts` | ❌ Wave 0 |
| STEL-02 | Σ Teil = Σ PB = Σ Gruppe (6291); Gruppenfolge je Teil; KL nicht als Aufgabenbereich | unit | vitest `stellen.test.ts` | ❌ Wave 0 |
| STEL-03 | Σ Personalaufwand je PB = `GESAMT` = 5.204.054; gleiche Zeilenreihenfolge in beiden Diagrammen; kein Aufwand je Stelle im Quelltext | unit + Quelltext | vitest `stellen.test.ts`, `quelltext.test.ts` | ❌ Wave 0 |
| UI-04 | Komponente auf `/ausgaben`, `/einnahmen`, `/rat-entscheidet`; Glossarschlüssel `nicht_im_haushalt` existiert; Text `nicht_im_haushalt` hat Schlüssel und Seiten | unit (Quelltext/Daten) | vitest `quelltext.test.ts`, `glossar.test.ts` | ✅ erweitern |
| Menü (D-19) | Union, Reihenfolge, jeder Routenname existiert, keine Doppelten, `mitJahr` nur für drei Seiten | unit | vitest `menue.test.ts` | ✅ anpassen |

### Sampling Rate

- **Per task commit:** gezielte vitest-Datei in der Scratch-Kopie plus `type-check`/`lint`/`format:check`; für Pipeline-Tasks gezielte pytest-Dateien.
- **Per wave merge:** volle Pipeline-Suite + Reproduzierbarkeitsgate + komplette App-Kette (Scratch-Kopie).
- **Phase gate:** alles grün, dazu Texte am Checkpoint abgenommen, manuelle 360-px-Prüfung und Menü-Tastaturtest, vor `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `app/src/lib/__tests__/{entwicklung,ruecklagen,investitionen,schulden,bindungsgrad,stellen,zuschuesse}.test.ts`
- [ ] `app/src/lib/__tests__/menue.test.ts`, `glossar.test.ts`, `quelltext.test.ts`, `farben.test.ts` anpassen (neue Seiten, drei Glossarschlüssel, neue Grafikfarben ≥ 3:1)
- [ ] `pipeline/tests/test_manuell.py`, `test_pruefung.py`, `test_app_daten.py`, `test_texte.py` erweitern (neue Tabelle, Regel 5, Schlüsselreihenfolge, Meta-Schwellen, neue Texte/Formeln)
- [ ] Framework-Installation: keine (vitest/pytest vorhanden)

*Manuell zu prüfen (nicht automatisierbar in dieser Phase, Playwright folgt in Phase 7):* Zweizeilige Achsen und Menüliste bei 360 px, Escape/Fokusrückgabe der Menügruppe, Tabellen-/Tastaturpfad der Produktlinks, fachliche Abnahme der Texte.

## Security Domain

`security_enforcement` ist aktiviert (ASVS Level 1, Block bei `high`). Die App ist statisch ohne Backend, Nutzerkonten oder Eingabefelder mit Persistenz; relevant sind Query-Parameter, Textausgabe und Lieferkette.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — (keine Konten) |
| V3 Session Management | no | — |
| V4 Access Control | no | — (öffentliche Daten) |
| V5 Input Validation | **yes** | `?pb=`/`?art=` nur über Allowlist (`Map`/`Set`), Bereinigung per `router.replace`, wie `leseAnsicht`/`leseJahr`; Pipeline: `pruefe_text`, `lies_meta_json`-Blattregeln |
| V6 Cryptography | no | — |
| V10/V14 Konfiguration/Lieferkette | yes | keine neuen Abhängigkeiten; Icons selbst gehostet, keine Drittanbieter-Requests |

### Known Threat Patterns for Vue + ECharts (statisch)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XSS über Tooltip-HTML (ECharts setzt Formatter-Ergebnis als HTML) | Tampering | ausschließlich `tooltipZeilen`/`htmlSicher`; Produkt- und Maßnahmennamen kommen aus Daten und laufen durch denselben Weg |
| XSS über Erklärtexte | Tampering | Texte nur per Textinterpolation (`ErklaerText`), kein `v-html` (`quelltext.test.ts` sperrt die Direktive in allen `.vue`), HTML-Zeichen in Pipeline-Texten verboten (`pruefe_text`) |
| Prototype-Pollution/Schlüssel-Kollision über Query oder Daten-Schlüssel | Tampering | Lookup nur über `Map`/`Set`/`Object.hasOwn`, `Object.fromEntries` für bereinigte Queries (Muster `ansicht.ts`) |
| Falsche Zahl in Bürgerinformation (Integrität, Core Value) | Tampering | Summen-/Identitätstests gegen Planzeilen und gedruckte Zahlen (Test Map oben); Abnahme-Checkpoint für Texte |
| Personenbezogene Daten | Information Disclosure | neue Einzelzuschuss-Tabelle enthält nur Verwendungszwecke, keine Namen; `stellenplan.json` trägt nur Amtsbezeichnungen (z. B. „Bürgermeister/in“), keine Namen [VERIFIED: Auswertung `stellenplan.json`] |
| Kompromittierte Abhängigkeit | Spoofing/Tampering | keine neuen Pakete in Phase 6 |

## Sources

### Primary (HIGH confidence)
- `raw_data/haushalt-2026.pdf` (1-basierte Seiten, mit pdfplumber gelesen): S. 14, 23, 24, 25, 33, 34, 35, 36, 46, 47, 48, 72, 290, 309, 310, 311
- Repo-Daten, diese Session ausgewertet: `app/src/data/{haushalt,investitionen,stellenplan,produkte,texte}.json`, `typen.ts`, `daten.ts`; `daten/manuell/{README.md,meta.json,texte/*.md}`, `daten/pruefberichte/befunde.md`
- Repo-Code: `app/src/lib/{menue,zeitreihen,kreisumlage,kennzahlen,jahr,texte,glossar,ansicht,berechnung,bildschirm}.ts`, `charts/{balken,echartsTheme,format,tooltip}.ts`, Komponenten `BaseChart`, `ChartCard`, `KennzahlKachel`, `DatenTabelle`, `ErklaerText`, `SteuerZeitreihe`, `ZuschussBalken`; `App.vue`, `main.ts`, `router/index.ts`; Tests `menue`, `quelltext`, `glossar`, `stiltokens`; Pipeline `ostbevern/{texte,manuell,app_daten,pruefung,schema}.py`, `jahrgaenge/2026_sollwerte.toml`
- Planungsdokumente: `06-CONTEXT.md`, `06-UI-SPEC.md`, `REQUIREMENTS.md`, `STATE.md`, `05-VALIDATION.md`, `discussion/SPEZIFIKATION.md` §3.3, 3.4, 3.7, 6.10–6.15, B.6
- `node_modules` (Scratch-Kopie, Versionen = `package-lock.json`): `echarts/types/dist/{components,echarts}.d.ts` (MarkLineComponent, MarkLine-Optionen)
- Testläufe diese Session: vitest 25 Dateien/1031 Tests grün; `vue-tsc --build` grün; pytest 528 Tests grün (321 s)

### Secondary (MEDIUM confidence)
- [CITED: lexmea.de/en/gesetz/go-nrw/76; haufe.de GO NRW § 76; ifv.de Fritze 2024 „Haushaltsausgleich und Haushaltssicherung nach dem 3. NKFWG“] — nur Suchzusammenfassungen (Seiten selbst HTTP 403): Auslöser Viertel/Zwanzigstel und weiterer Auslöser „allgemeine Rücklage im Planungszeitraum aufgebraucht“

### Tertiary (LOW confidence)
- Keine tragenden Aussagen. Layout-Annahmen bei 360 px (A2, A3) sind als `[ASSUMED]` markiert.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — keine neuen Pakete, Versionen aus Lockfile, Registrierung von `MarkLineComponent` an den Typen geprüft.
- Datenlage/Pipeline-Umfang: HIGH — jede Zahl gegen JSON und PDF-Seite geprüft; Identitäten (Σ Art = GFP, Σ Stellen, Eigenkapital-Spalten) rechnerisch bestätigt.
- Architecture: HIGH — Muster aus Phase 5 (Lib-Funktionen, Query-Zustand, Builder) direkt übertragbar.
- Pitfalls: HIGH für Datensemantik (verifiziert), MEDIUM für Layout (360 px, geschlossene Aufklapper).
- Rechtlicher Wortlaut § 76 GO NRW: MEDIUM — Wortlaut der Schwellen durch S. 23 belegt, übrige Rechtsfragen nicht geprüft und von der App nicht behauptet.

**Research date:** 2026-10-05
**Valid until:** 2026-11-04 (Datenstand fest: Haushalt 2026; Abhängigkeiten gepinnt)

