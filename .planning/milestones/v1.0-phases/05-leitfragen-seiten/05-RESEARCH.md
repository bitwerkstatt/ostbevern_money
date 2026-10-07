# Phase 5: Leitfragen-Seiten - Research

**Researched:** 2026-10-04
**Domain:** Vue-3-Frontend (Web Awesome, ECharts Treemap/Sankey/Line/Bar, Hash-Router mit URL-Zustand) auf generierten JSON-Daten, plus kleiner Pipeline-Anteil (zwei fehlende Vorberichtstabellen, Glossartexte)
**Confidence:** HIGH (fast alles ist Erweiterung gelesener Repo-Muster und gegen Quellcode/PDF geprüft); MEDIUM an einzelnen Stellen, die im Assumptions Log stehen

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Datenlücken Einnahmen (EINN-02…06)**
- **D-01:** Die **Zeitreihe je Steuerart 2022–2029** (EINN-05) nimmt **2022–2023 aus den Grundzahlen 160101** (Ist) und **2024–2029 aus `vorbericht.steuerarten`**. Grund: Die Grundzahlen 2024/2025 weichen vom Vorbericht ab (Gewerbesteuer 2024: GZ 8.418.043 € vs. Vorbericht vorl. RE 9.511.000 €). Die Vorberichtssumme trifft GEP Z. 01 2024 (19.614.808 €) bis auf Rundung. Bewusste Abweichung von Spez. 6.4 („Ist 2022–2024 aus den Grundzahlen“). Die Grundzahlen 2024/2025 werden für Steuerreihen nicht verwendet. Ist (2022–2024), Ansatz und Planung sind visuell unterscheidbar (z. B. durchgezogen/gestrichelt), die Wertart steht im Tooltip und in der Tabelle. Analog für die Schlüsselzuweisung (GZ Pos. 9 für 2022–2023, ab 2024 `vorbericht.zuwendungen`).
- **D-02:** Der Erklärtext `gewerbesteuer` in `daten/manuell/texte/erklaerungen.md` zitiert heute `{{grundzahlen.160101.1.2024|mio}}` (8,42 Mio. €). Phase 5 stellt diesen Platzhalter auf `vorbericht.steuerarten.gewerbesteuer.2024` um. Ein Test stellt sicher, dass Erklärtexte und die Steuer-Zeitreihe für dasselbe Jahr dieselbe Quelle nutzen (mindestens: kein `grundzahlen.160101.*`-Platzhalter für Jahre ≥ 2024). Der Nutzer nimmt den geänderten Satz im Glossar-Checkpoint (D-15) mit ab.
- **D-03:** Die **Aufteilung der investiven Einnahmen** (Investitionspauschale, Schulpauschale, Sportpauschale usw., Spez. 6.4) wird aus dem Vorbericht **manuell nach `daten/manuell/` abgeschrieben**. Es gelten die Regeln aus Phase 4: D-05 `betrag_teur`, D-06 Langformat, D-09 einmal abgeschrieben, README-Begründung, `quelle`-Seite. Regel 5 prüft sie gegen die passende GFP-Zeile (voraussichtlich `investitionszuwendungen`, Z. 18; der Researcher bestimmt die Vorberichtsseite und die genaue Zuordnung). Ein nicht aufgeschlüsselter Rest erscheint als berechnetes „Sonstige“. Grundstücksverkäufe, Beiträge und Kredite kommen direkt aus den GFP-Zeilen `veraeusserung_sachanlagen`, `beitraege` und `kreditaufnahme`. Die investiven Einnahmen stehen auf `/einnahmen` getrennt und klar abgegrenzt („fließen nicht in den laufenden Haushalt“, Finanzplan nie mit Ergebnisplan im selben Diagramm).
- **D-04:** **Vorbericht 2.1.7** (Sonstige ordentliche Erträge inkl. Konzessionsabgaben) wird ebenso manuell abgeschrieben, als neue Tabelle in `weitere_vorberichtstabellen.csv` oder als eigene Datei. Regel 5 prüft sie zweistufig (P4 D-07) gegen GEP Z. 07 `sonstige_ordentliche_ertraege`. Damit hat EINN-04 für 2026 echte Werte. Das war in Phase 4 ausdrücklich vertagt. Die neuen Tabellen laufen über Schritt 07 in `haushalt.json` → `vorbericht` und über `typen.ts`, ohne Typumwandlung.

**Ausgaben: Treemap & Zuschussbedarf (AUSG-01…04)**
- **D-05:** Im Modus „Aufwand“ gibt es eine Treemap (PB → PG → P, KL als Top-Kachel). Im Modus „Zuschussbedarf“ gibt es **statt der Treemap horizontale Balken** je Drilldown-Ebene, mit negativen Balken für Überschüsse (`berechnet.ueberschuss`). Überschüsse bekommen eine eigene Erklärung (AUSG-03), z. B. „Allgemeine Finanzwirtschaft: hier liegen die Steuern und die Schlüsselzuweisung“ oder Gebührenhaushalte. Die Werte werden nur aus `ergebnisplan[code].berechnet` gelesen und nicht neu gerechnet.
- **D-06:** **Eigene Brotkrumen-Navigation** gilt gemeinsam für Treemap und Balken („Alle Bereiche › PB › PG“). Beim Wechsel Aufwand ↔ Zuschussbedarf bleibt die Ebene erhalten. Die Tabellenalternative (`DatenTabelle`) zeigt immer die aktuelle Ebene. Der Drilldown ist per Tastatur bedienbar. Ein Klick auf ein Produkt öffnet `/produkt/:code` (D-09). Die native ECharts-Treemap-Navigation (`breadcrumb`, `roam`) wird nicht verwendet.
- **D-07:** **KL-Callout** („Weitergabe an Kreis und Land“): 1–2 kurze Sätze („Diesen Betrag reicht Ostbevern weiter und kann ihn nicht selbst steuern“), dazu die drei Unterposten als „rd.“ (P4 D-02) und ein Aufklapper mit dem Erklärtext `kreisumlage` aus `texte.json` (netto/brutto, Hebesätze). Der globale Minderaufwand erscheint als erklärter Hinweis unter dem Diagramm (Text `globaler_minderaufwand`), nicht als Kachel.
- **D-08:** **Farben:** Jede PB hat eine feste Farbe aus `echartsTheme.ts`, die Kinder erben sie in Abstufungen. KL bekommt einen eigenen, abgesetzten Akzent mit Muster bzw. Decal, damit die Kachel auch ohne Farbe erkennbar ist. Dieselbe PB→Farbe-Zuordnung gilt in Treemap, Balken, Sankey und mobilen Balken. Die Zuordnung steht zentral in `echartsTheme.ts`, und die Kontraste genügen dem a11y-Ziel.

**Navigation, Jahr & Produktdetail (AUSG-05, FLUSS-01…04, UI-01)**
- **D-09:** Das **Produktdetail ist eine eigene Route `/produkt/:code`**. Es ist verlinkbar aus Treemap, Balken, Glossar-Akkordeon und später aus Phase 6. Inhalt nach AUSG-05: Beschreibung, Leistungen, Bindungsgrad, Gremium, Teilergebnisplan 2024–2029 als Mini-Tabelle, Erläuterungen, Grundzahlen (berechnete Pro-Kopf-Werte gekennzeichnet), Investitionen des Produkts und Quellenlink (PDF-Seite). „Zurück“ führt zur Ausgabenseite auf der Ebene des Produkts (PB/PG im Query). Unbekannter Code → freundliche Fehlermeldung oder Redirect. — **Reversibility:** costly — Phase 6 und das Glossar verlinken auf dieses URL-Schema.
- **D-10:** Der **Jahr-Umschalter ist global und steht in der URL** (`?jahr=2027`, Hash-Router-Query). Er gilt auf `/einnahmen`, `/ausgaben` und `/geldfluss`. Ohne Parameter gilt das Haushaltsjahr aus den Daten (2026), ungültige Werte fallen darauf zurück. Links zwischen den Seiten (z. B. Sankey → Ausgaben) behalten das Jahr. Jeder angezeigte Wert trägt die Wertart aus `haushalt.wertarten` als Etikett (Ist/Ansatz/Planung). Die Jahresliste kommt aus `haushalt.jahre`, ist also nicht fest im Code. — **Reversibility:** costly — Das URL-Schema `?jahr=` wird von Links und Phase-6-Seiten mitbenutzt.
- **D-11:** **Sankey-Ausgleich je Jahr:** Bei einem Defizit steht links der Knoten „Defizit (Entnahme aus Rücklagen)“, bei einem Überschuss (z. B. 2024 Ist +191.990 €) rechts „Überschuss (Zuführung zur Rücklage)“. Der Minderaufwand erscheint nur bei einem Wert ≠ 0 als Gegenposten. Alles wird aus GEP `jahresergebnis`, `globaler_minderaufwand` und `ergebnis_nach_minderaufwand` abgeleitet, ohne Sonderfall für einzelne Jahre. Ein Test prüft für alle 6 Jahre, dass linke und rechte Summe gleich sind. Der Erklärtext (`defizit_ruecklagen`) muss zum Jahr passen; er wird nur bei Defizit gezeigt bzw. bekommt eine Überschuss-Variante. Hover hebt Pfade hervor, ein Klick auf einen Aufgabenbereich führt zu `/ausgaben?jahr=…` mit gewählter PB (FLUSS-03).
- **D-12:** **Mobile Alternative zum Sankey** (< Breakpoint aus `lib/bildschirm.ts`): zwei gleich lange gestapelte Balken, „Woher“ (Ertragsarten + ggf. Defizit) und „Wohin“ (KL, Aufgabenbereiche, Zinsen + ggf. Minderaufwand/Überschuss), in denselben Farben (D-08). Darunter steht die Tabelle.
- **D-13:** **Kopfmenü:** Start · Woher? · Wofür? · Geldfluss · Glossar. Phase 6 ergänzt eine Gruppe „Mehr wissen“ als Dropdown. Auf schmalen Bildschirmen öffnet sich das Menü als `wa-drawer`. Die Fokussteuerung beim Routenwechsel bleibt erhalten bzw. kommt dazu.

**Glossar & Fußzeile (GLOS-01…03, UI-03, UI-05)**
- **D-14:** Die **Glossartexte** (≥ 22 Begriffe aus Spez. 6.14) stehen als **Pipeline-Texte** in einer neuen Datei, z. B. `daten/manuell/texte/glossar.md`. Schritt 07 schreibt sie nach `texte.json` (oder in eine eigene Text-JSON). Es gelten dieselben Regeln wie in Phase 4: Platzhalter `{{schluessel|kuerzel}}`, Ziffern-Test, Du-Anrede, Seitenverweis bei Zahlen, stabiler Schlüssel je Begriff (Anker).
- **D-15:** Der Executor **entwirft** die Glossartexte, ein **Checkpoint** legt sie dem Nutzer zur fachlichen Abnahme vor dem Commit vor (wie P4 D-17). Im selben Checkpoint wird der geänderte Gewerbesteuer-Satz (D-02) abgenommen.
- **D-16:** **`GlossarBegriff`**: Der Begriff ist unterstrichen und zeigt bei Hover oder Fokus einen `wa-tooltip` mit dem ersten Satz der Definition. Ein Klick führt zu `/glossar#<schluessel>` und scrollt bzw. fokussiert den Begriff. Ein Test (oder Type-Check über einen Schlüsseltyp) stellt sicher, dass jeder in den Seiten verwendete Begriffsschlüssel existiert. Das Produktakkordeon (`ProduktAkkordeon`) listet alle 63 Produkte mit Beschreibung und Link zu `/produkt/:code`.
- **D-17:** **Kontakt in der Fußzeile:** eine **E-Mail-Adresse**, die heute noch nicht feststeht. Sie wird ein **konfigurierbarer Wert** (z. B. in einer App-Konfiguration bzw. `jahrgang.json`) mit erkennbarem Platzhalter. **Vor dem Deployment in Phase 7 muss sie gesetzt sein.** Der Phase-7-Plan bzw. -Smoke-Test muss einen Platzhalterwert zurückweisen.
- **D-18:** **Datenstand in der Fußzeile:** „Haushalt {jahr}, beschlossen am {meta.satzung.beschluss}“ mit Link zum Original-PDF der Gemeinde (URL konfigurierbar, nicht im Komponentencode), dazu der Hinweis „inoffizielles Projekt, keine Veröffentlichung der Gemeinde Ostbevern“ und der bestehende Münster-Dank. Es gibt kein Build-Datum.

### Claude's Discretion
- Darstellung der Ebene 1 auf `/einnahmen` (horizontale Balken oder Donut) und Aufklapp-Mechanik der Ebene 2 (`wa-details` o. Ä.)
- Aufbau der Startseite: Anordnung des Kennzahlenbands, Einstiegskacheln, Kreisumlage-Hinweis. Die Werte kommen aus GEP/GFP/meta: Pro-Kopf-Werte = Wert / `meta.einwohner`, als berechnet gekennzeichnet.
- Sicht nach Aufwandsart (AUSG-04): Diagrammform, Aufklapper Transferaufwendungen mit `vorbericht.transferaufwendungen` + `kita_zuschuesse`, Abschreibungen mit „kein Geldfluss“
- Genaue Knotenliste des Sankey links (Spez. 6.6: Steuern aufgeteilt in Gewerbe-, Einkommen-, Grundsteuer, übrige; Schlüsselzuweisung, sonstige Zuwendungen, Gebühren/Entgelte, Sonstige, Finanzerträge) im Rahmen der vorhandenen Daten
- Konkrete Farbwerte der PB-Palette, Breakpoints, Komponentenschnitt (z. B. `JahrUmschalter`, `Brotkrumen`, `SankeyDiagramm`, `KennzahlKachel`), Composable für den Jahr-Query
- Name und Struktur der neuen manuellen Tabellen und Text-JSON-Felder
- Wie `formatiere()` die offenen Review-Punkte WR-06/IN-01 (fehlender Fallback) beim Verdrahten in die Seiten löst

### Deferred Ideas (OUT OF SCOPE)
- Spiel-Teaser auf der Startseite (Spez. 6.3) — mit den Spielen in v2
- Kontakt-E-Mail festlegen — vor Phase 7 (Deployment-Gate, D-17)
- Repo-URL bzw. GitHub-Issues als zusätzlicher Kontaktweg — ggf. Phase 7, sobald ein Remote existiert

### Zusätzlich verbindlich: `05-UI-SPEC.md` (freigegeben, „locked“)
Der UI-Vertrag (Komponenten, Routen/URL-Zustand, Palette, Chart Contract, Copywriting, A11y) ist gesetzt. Diese Recherche zeigt, **wie** er umzusetzen ist, und nennt am Ende (Open Questions 1–3) drei Stellen, an denen der Vertrag der Wirklichkeit der Daten bzw. der Komponenten widerspricht. Das sind keine Neu-Entscheidungen, sondern Funde, die der Planer vor dem Schreiben der Pläne bestätigen lassen muss.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| START-01 | Kennzahlenband 2026 | Alle sieben Werte direkt aus `haushalt.json` herleitbar (Abschnitt „Kennzahlenband“); Pro-Kopf **gerundet** (2594/1571), nicht abgerundet; Seitenverweise 62/63/25 vorhanden |
| START-02 | Zwei Einstiege + Kreisumlage-Hinweis | KL-Wert aus `ergebnisplan.KL.berechnet.aufwand`; Satz „größter Aufgabenbereich“ muss KL ausschließen (Open Question 4) |
| EINN-01 | Ertragsarten mit Betrag und Anteil | GEP-Zeilen Z.01–07 + Z.19; **8 Zeilen im Jahr 2024** (Z.03 `sonstige_transferertraege` = 36.321), nicht fest 7 |
| EINN-02 | Steuern aufklappen, Hebesätze, selbst festgelegte Steuern | `vorbericht.steuerarten` + `meta.hebesaetze`; neuer Erklärtext „selbst festgelegt“ nötig (Pipeline-Text) |
| EINN-03 | Zuwendungen aufklappen, Sonderposten „kein Geldfluss“ | `vorbericht.zuwendungen` inkl. berechnetem Posten `sonstige`; Beispiele ohne Zahlen formulieren (Ziffernregel) |
| EINN-04 | Sonstige Erträge mit Konzessionsabgaben | **Vorbericht S. 33 (Tabelle 2.1.7)** manuell abschreiben; **Druckfehler 2028 (2.396 statt 2.346)**, siehe Pitfall 4 |
| EINN-05 | Zeitreihe je Steuerart 2022–2029 | GZ-Positionen 1–9 von 160101 + `vorbericht.steuerarten`; Ist/Ansatz/Planung als drei Serien |
| EINN-06 | Investive Einnahmen getrennt | **Vorbericht S. 52** (nur 2026 aufgeschlüsselt) + GFP Z.18/19/21/33; andere Jahre nur GFP-Zeilen |
| AUSG-01 | Treemap mit Drilldown | ECharts-Treemap mit flacher `data`-Liste je Ebene, Router-Query `pb`/`pg`; Decal-Support für KL **verifiziert** |
| AUSG-02 | KL-Kachel + Callout, Minderaufwand-Hinweis | KL ist Top-Knoten; drei Kinder sind „rd.“ (`gerundet`), Summe weicht 181 € vom Elternwert ab |
| AUSG-03 | Aufwand/Zuschussbedarf, Überschüsse erklärt | `berechnet.zuschussbedarf/ueberschuss`; 2026: PB 11 und PB 16 sind Überschuss; Erklärung datengetrieben pro Ebene |
| AUSG-04 | Aufwandsart, Transfer/Abschreibungen | 7 GEP-Zeilen summieren auf 30.455.569; `vorbericht.transferaufwendungen`, `kita_zuschuesse` (nur 2026) |
| AUSG-05 | Produktdetail | `produkte`, `ergebnisplan[code].zeilen`, `investitionen.massnahmen`; **Zeilenbeschriftungen fehlen im JSON** (Pitfall 9) |
| FLUSS-01 | Sankey 2026 | Reiner Builder `baueGeldfluss(jahrIndex)`; Steuerknoten über Plug „übrige Steuern“, sonst bilanziert 2024 nicht |
| FLUSS-02 | Defizit-Knoten + Minderaufwand-Gegenposten | **Rechnerisch bilanziert der Minderaufwand nur LINKS** (Open Question 1) |
| FLUSS-03 | Hover/Klick | `emphasis.focus: 'adjacency'`; Klick → Router; Tastaturpfad über Tabelle |
| FLUSS-04 | Schmale Bildschirme | `useSchmalerBildschirm()` + `GeldflussBalken` + Tabelle |
| GLOS-01 | ≥ 22 Begriffe | Parser-Erweiterung (`Quelle` optional ohne Zahlen), stabile Schlüssel, Union-Typ per Test abgesichert |
| GLOS-02 | 63 Produkte als Akkordeon | `produkte` (63, 15 PB), alle mit Beschreibung |
| GLOS-03 | `GlossarBegriff`-Links | `wa-tooltip for=…`, Router-Hash, `scroll-margin-top: var(--scroll-margin-top)` |
| UI-01 | Jahr-Umschalter | `useJahr()`; `wa-radio-group` + `wa-radio appearance="button"` (Attribut sitzt am `wa-radio`) |
| UI-03 | Fußzeile | Konfigurationswerte E-Mail/PDF-URL; PDF-URL ist unbekannt (Open Question 5) |
| UI-05 | Zahlen aus Daten, PDF-Seite | App-seitiger Platzhalter-Renderer (fehlt noch); Jahr-gebundene Texte (Pitfall 6) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Quelle: `/Users/thma/repos/bitwerkstatt/ostbevern_money/.claude/CLAUDE.md` (gelesen). Der Planer muss jede Zeile prüfen.

- **Stack:** Pipeline Python ≥ 3.12/uv/pdfplumber/polars/typer/pytest/ruff; App Vue 3, vue-router 5 (Hash), Vite, TypeScript, Web Awesome 3 (Komponenten einzeln in `main.ts` importieren, Icons selbst gehostet unter `app/public/icons`, Goldakzent `wa-brand-yellow`), ECharts 6 über vue-echarts 8 (nur in `echartsTheme.ts` registrierte Module), ESLint-Flat-Config + Prettier, Node 22.
- **Konventionen:** deutsche Bezeichner ohne Umlaute; Beträge int-Euro, Formatierung **ausschließlich** über `app/src/charts/format.ts`; nur 1-basierte PDF-Seiten (`pdf_seite`); **keine Jahrgangswerte im Code** (Jahrgangsdaten in `pipeline/jahrgaenge/{jahr}.toml`, Zugriff nur über `lade_jahrgang`/`lade_sollwerte`, Standardjahr nur in `STANDARD_JAHR`, jedes Pipeline-Skript nimmt `--jahr`); Du-Anrede durchgehend; Zahlen in Texten aus Daten, jeder erklärende Text mit Zahl verweist auf eine PDF-Seite.
- **Phasenkonventionen:** Pipeline-Skripte sind dünne typer-Einstiegspunkte, Logik in `pipeline/ostbevern/`; fachliche Regeln bleiben im Code; generierte Daten unter `daten/` werden eingecheckt; Basiskomponenten behalten Münster-Namen und -Props (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts`, `bildschirm.ts`); Farben nur über `--wa-*`-Tokens, Chartfarben nur aus `echartsTheme.ts`; CSS-Klassen-Präfix `om-`; Beispielwerte nur hinter `ChartCard`-Flag `beispieldaten`; keine Drittanbieter-Requests zur Laufzeit; beim Commit nur explizit benannte Pfade stagen.
- **Befehle:** `uv run --directory pipeline …` (nie `uv run pipeline/SKRIPT.py`); App-Befehle mit `npm --prefix app …`; CI lokal nachstellen wie in CLAUDE.md. Neu in dieser Phase: ein `test`-Schritt für die App (siehe Validation Architecture) muss in `.github/workflows/ci.yml` **und** in CLAUDE.md „Befehle“ aufgenommen werden.
- **Sprache/A11y/Genauigkeit:** App deutsch/Du; Pro-Kopf-Grundlage 11.741 Einwohner aus `meta.json`; Lighthouse a11y ≥ 95 (Endabnahme Phase 7), `prefers-reduced-motion`, responsiv ab 360 px; Abweichungen > 1 € gegenüber Planwerten sind Fehler, außer in `befunde.md` dokumentiert; Mitarbeitendennamen werden nicht ausgeliefert.
- **GSD-Workflow:** Dateiänderungen nur über GSD-Befehle (Executor-Pläne); kein direktes Editieren außerhalb.

## Summary

Phase 5 ist überwiegend **Frontend-Arbeit auf fertigen Daten**: Alle Zahlen der fünf Seiten lassen sich aus `app/src/data/haushalt.json`, `produkte.json`, `investitionen.json` und `texte.json` herleiten. Die Pipeline muss nur drei Dinge liefern: (1) zwei bisher fehlende Vorberichtstabellen (2.1.7 auf **S. 33**; investive Zuweisungen/Pauschalen auf **S. 52**), (2) neue bzw. geänderte Erklärtexte inklusive Glossar, (3) einen Pipeline-Test für D-02. Die eigentliche Komplexität liegt in vier Bereichen: ein korrekt bilanzierender Sankey-Builder, URL-Zustand (`jahr`/`modus`/`pb`/`pg`) mit Fokussteuerung im Hash-Router, die Erweiterung der Basiskomponenten (BaseChart, DatenTabelle, ChartCard, PageIntro) um das, was der UI-Vertrag verlangt, und eine App-seitige Testinfrastruktur, die es heute nicht gibt.

Die Recherche hat **sechs Fehler/Lücken im Bestand bzw. im Vertrag** gefunden, die ohne Vorwarnung Pläne brechen würden: (a) Der Minderaufwand bilanziert im Sankey rechnerisch nur auf der **linken** Seite (UI-SPEC/D-12 sagen rechts); (b) `wa-page` rendert selbst einen englischen Skip-Link `href="#main-content"`, der im Hash-Router auf die Startseite umleitet; (c) die Tabelle 2.1.7 druckt für 2028 **2.396 statt 2.346** (Druckfehler im PDF, Befund nötig); (d) die Pauschalen sind im PDF **nur für 2026** aufgeschlüsselt; (e) Pro-Kopf-Werte des Kennzahlenbands müssen **gerundet** werden (die Pipeline rundet Schulden pro Kopf **ab**); (f) `npm install vitest@4.x` bricht im Projekt mit einem Arborist-Fehler ab, `vitest@5.0.3` installiert und läuft (in Scratch-Kopie geprüft).

**Primary recommendation:** Wave 0 legt Test-Infrastruktur (vitest 5.0.3), Icons und die additiven Erweiterungen der Basiskomponenten/`echartsTheme.ts`/`format.ts` an; die Pipeline-Wave schreibt Tabellen, Befunde, Texte und das Glossar (mit Nutzer-Checkpoint); danach entstehen App-Rahmen (Router, Kopf/Fuß, `useJahr`) und die fünf Seiten, wobei jede Datenaufbereitung als **reine, getestete Funktion in `app/src/lib/`** gebaut wird (Sankey-Bilanz, Drilldown, Zeitreihen, Platzhalter-Renderer) und die `.vue`-Komponenten nur noch darstellen.

## Architectural Responsibility Map

Die App ist statisch (GitHub Pages, kein Backend). „API/Backend“ entspricht hier der **Build-Zeit-Pipeline**, „Browser“ der Vue-App.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Extraktion/Abschrift der Vorbericht-Tabellen (2.1.7, Pauschalen), Regel-5-Prüfung | Build-Pipeline (Python) | — | Core Value: jede Zahl durch Prüfregeln belegt; App darf nichts abschreiben |
| Erklär- und Glossartexte mit Platzhaltern, Ziffern-Test | Build-Pipeline | Browser (rendert Platzhalter über `format.ts`) | Pipeline formatiert nie (P4 D-15), App ist einzige Formatierungsstelle |
| Zeilenbeschriftungen (kanonischer Schlüssel → Name) | Build-Pipeline (`ZEILEN`) | Browser (nur Anzeige) | Einzige Quelle ist `ostbevern/zeilen.py`; App darf keine zweite Namenstabelle pflegen (Empfehlung, Pitfall 9) |
| Sankey-Knoten/Links, Drilldown-Ebenen, Ertragsarten, Zeitreihen | Browser (reine `lib/`-Funktionen) | — | Ableitungen aus `haushalt.json` je gewähltem Jahr; Jahr ist Laufzeit-Zustand |
| Jahr-/Modus-/Ebenen-Zustand | Browser (Router-Query) | — | URL ist Quelle der Wahrheit (D-10), Links müssen teilbar sein |
| Diagramm-Rendering, Hover-Highlight, Klick | Browser (ECharts/Canvas) | — | Canvas nicht fokussierbar → Tastaturpfad über DOM-Tabellen |
| Fokussteuerung, Titel, Live-Region, Skip-Link | Browser (Router-Hooks + `App.vue`) | — | Hash-Router ohne Seitenreload |
| Hosting, Auslieferung der JSON-Bundles | CDN/Static (GitHub Pages) | — | Kein Backend; JSON wird mit dem Bundle importiert |
| Kontakt-E-Mail, PDF-URL | Browser-Konfiguration (`app/src/…`) | Phase-7-Smoke-Test | D-17/D-18: konfigurierbar, Platzhalter erkennbar |

## Standard Stack

### Core (alles bereits installiert, Versionen aus `app/node_modules/*/package.json` gelesen)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| vue | ^3.5.42 | Komponenten | Projektvorgabe [VERIFIED: app/package.json] |
| vue-router | 5.3.1 | Hash-Router, Query-Zustand, `scrollBehavior` | Projektvorgabe; API wie vue-router 4 [VERIFIED: app/node_modules/vue-router/package.json] |
| @awesome.me/webawesome | 3.14.0 | UI-Komponenten (`wa-details`, `wa-drawer`, `wa-tooltip`, `wa-radio-group`, `wa-select`, `wa-tag`, `wa-card`, `wa-divider`) | Projektvorgabe [VERIFIED: node_modules package.json] |
| echarts | 6.1.0 | Treemap, Sankey, Line, Bar | Projektvorgabe [VERIFIED: node_modules package.json] |
| vue-echarts | 8.3.1 | `BaseChart`-Wrapper | Projektvorgabe [VERIFIED] |
| typescript / vue-tsc | ~6.0.0 / ^3.3.11 | `npm run type-check` mit `noUncheckedIndexedAccess: true` | [VERIFIED: app/package.json, app/tsconfig.app.json] |

### Supporting (neu)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| vitest | **5.0.3** (exakt pinnen) | App-seitige Unit-Tests für reine `lib/`-Funktionen, Kontrasttest der Palette, Sankey-Bilanz über alle 6 Jahre | Wave 0; Node-Umgebung genügt, kein DOM nötig |

**Installation (in einer Scratch-Kopie geprüft, siehe Environment Availability):**
```bash
# im Repo-Root; npm >= 10 verwenden (Sandbox hat npm 9.2.0, siehe Pitfall 12)
npm --prefix app install -D --save-exact vitest@5.0.3
```
Zusätzlich anlegen: `app/vitest.config.ts` (mergeConfig mit `./vite.config.ts` **mit Dateiendung**, `environment: 'node'`), `app/tsconfig.vitest.json` (für `src/**/__tests__/*`, in `tsconfig.json` referenzieren; `tsconfig.app.json` schließt `src/**/__tests__/*` bereits aus [VERIFIED: tsconfig.app.json]), Skript `"test": "vitest run"` in `app/package.json`, CI-Schritt in `.github/workflows/ci.yml`.

**Version verification:** `npm view vitest version` → 5.0.3, veröffentlicht 2026-09-30; Peer `vite: ^6.4.0 || ^7.0.0 || ^8.0.0`, Node `^22.12.0 || ^24.0.0 || >=26.0.0` [VERIFIED: npm registry]. In Scratch-Kopie von `app/` mit Projekt-`vite@8`: `npm ci` + `npx vitest run` mit einem Test, der `@/charts/format` und `@/data/daten` importiert, lief grün (2 Tests) [VERIFIED: lokaler Lauf 2026-10-04].

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| vitest 5.0.3 | vitest 4.1.11 | **Nicht installierbar** im Projekt/leerem Verzeichnis: `npm install -D vitest@4.1.11` bricht mit `Cannot read properties of null (reading 'edgesOut')` ab (npm 9.2.0 und 10.9.2); `--legacy-peer-deps` erzeugt ein unvollständiges Lockfile, `npm ci` scheitert („Missing: @types/react@19.3.0“) [VERIFIED: lokaler Lauf]. 5.0.1 scheiterte im Projekt ebenfalls, 5.0.3 nicht. |
| vitest | `node --test` + `tsx` | Keine neue Abhängigkeit, aber Alias `@/`-Auflösung und TS-Transpile müssten selbst gelöst werden; vitest teilt die Vite-Konfiguration |
| Playwright/Component-Tests | — | Gehört zu Phase 7 (QUAL-02); in dieser Phase nur manuelle Sichtprüfung (kein Browser in der Sandbox) |

## Package Legitimacy Audit

`gsd-tools query package-legitimacy check --ecosystem npm vitest` (2026-10-04):

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| vitest | npm | 5.0.3 vom 2026-09-30 (Projekt seit Jahren; 4.x/3.x-Linie älter) | Seam: `unknown-downloads` | github.com/vitest-dev/vitest | **SUS** (`too-new`, `unknown-downloads`) | **Flagged — Planer fügt vor der Installation `checkpoint:human-verify` ein.** `postinstall: null`; Maintainer u. a. antfu, yyx990803 (Vue/Vite-Team) [VERIFIED: npm registry]. Das SUS-Urteil beruht auf dem jungen `latest`-Tag, nicht auf dem Paketnamen. |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `vitest` [WARNING: flagged as suspicious — verify before using.] — Prüfpunkt für den Menschen: Versionsstand 5.0.3 gegen vitest.dev/GitHub-Release abgleichen, `package-lock.json`-Diff auf unerwartete Pakete prüfen.

Alle Icons sind keine Pakete (SVG-Dateien, siehe Pitfall 11). Keine weiteren neuen npm-/PyPI-Pakete.

## Architecture Patterns

### System Architecture Diagram

```
raw_data/haushalt-2026.pdf
      │  (einmalige manuelle Abschrift per pdfplumber-Lesen, D-09)
      ▼
daten/manuell/{sonstige_ertraege.csv | weitere_…csv, investitionszuwendungen.csv, meta.json,
               texte/erklaerungen.md, texte/glossar.md}
      │                                   ▲
      │        daten/aufbereitet/*.csv ───┤  (Schritte 01–05, unverändert)
      ▼                                   │
 06_pruefen  (Regel 5 neu: 2.1.7 gegen GEP Z.07; Pauschalen gegen GFP Z.18) ── befunde.md
      │ grün?
      ▼
 07_app_daten  ──►  app/src/data/{haushalt,produkte,investitionen,texte[,glossar]}.json
      │                                        │
      │                                        ▼
      │                      app/src/data/daten.ts (typisiert, ohne Typumwandlung)
      │                                        │
      │      ┌─────────────────────────────────┼───────────────────────────────┐
      │      ▼                                 ▼                               ▼
      │  lib/jahr.ts (useJahr, Query)   lib/*.ts reine Builder         lib/texte.ts (Platzhalter
      │      │                           (ertragsarten, drilldown,        → formatiere())
      │      │                            geldfluss, zeitreihen)                │
      │      ▼                                 ▼                               ▼
      │  Router-Query ?jahr&modus&pb&pg ─►  Seiten (Start, Einnahmen, Ausgaben, Produkt,
      │      ▲                              Geldfluss, Glossar)  ──►  Komponenten
      │      │                                                          │  BaseChart/ECharts (Canvas)
      │      └──── Klick/Link/Brotkrumen/Tabellen-Buttons ◄─────────────┘  DatenTabelle (Tastaturpfad)
      ▼
 App.vue: Kopfmenü/Drawer, Fußzeile (config.ts), Live-Region, Fokus nach Routenwechsel
      │
      ▼
 GitHub Pages (Phase 7)
```

### Recommended Project Structure

```
pipeline/
├── ostbevern/pruefung.py        # REGEL5_GEP_ZEILEN/WEITERE_VORBERICHTSTABELLEN erweitern, GFP-Zweig
├── ostbevern/app_daten.py       # neue Tabellen in `vorbericht_quellen`, evtl. zeilen_namen, glossar.json
├── ostbevern/texte.py           # Parser für glossar.md (Quelle optional ohne Zahl)
└── tests/                       # test_pruefung/test_app_daten/test_manuell/test_texte erweitern
daten/manuell/
├── sonstige_ertraege.csv  (oder Zeile in weitere_vorberichtstabellen.csv)
├── investitionszuwendungen.csv
├── meta.json                    # + vorbericht_werte.konzessionsabgabe_{strom,gas,wasser}
└── texte/{erklaerungen.md, glossar.md}
app/src/
├── config.ts                    # KONTAKT_EMAIL, PDF_URL, istPlatzhalter()
├── router/index.ts              # 6 benannte Routen, scrollBehavior, afterEach (Fokus/Titel/Live)
├── lib/
│   ├── jahr.ts                  # useJahr(), jahrLink()
│   ├── ansicht.ts               # modus/pb/pg parsen+bereinigen (Allowlist, siehe Security)
│   ├── drilldown.ts             # kinder(code), Pfad, Anteile — liest nur berechnet.*
│   ├── ertragsarten.ts          # Ebene 1/2, investive Einnahmen
│   ├── zeitreihen.ts            # GZ-Positionen→Posten, Ist/Ansatz/Planung
│   ├── geldfluss.ts             # baueGeldfluss(jahrIndex) → {knoten, links, summen}
│   ├── texte.ts                 # rendereAbsatz(absatz, werte) → string
│   └── bewegung.ts (oder in bildschirm.ts)  # useReducedMotion()
├── charts/ (echartsTheme.ts, format.ts erweitern)
├── components/                  # laut UI-SPEC „Phase 5 Components“
├── pages/                       # StartPage, EinnahmenPage, AusgabenPage, ProduktPage, GeldflussPage, GlossarPage
└── **/__tests__/*.test.ts       # vitest
```

### Pattern 1: URL-Zustand als einzige Quelle der Wahrheit (`useJahr`)
**What:** Jahr/Modus/Ebene stehen in `route.query`; Composables lesen defensiv, schreiben mit `router.replace` (Jahr/Modus) bzw. `router.push` (Drilldown).
**When to use:** `einnahmen`, `ausgaben`, `geldfluss`, `produkt`.
**Example:**
```typescript
// Quelle: vue-router-API (Query ist string | string[] | null) + haushalt.json (jahre)
import { computed } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import { haushalt } from '@/data/daten'

export function useJahr() {
  const route = useRoute()
  const router = useRouter()
  const jahr = computed(() => {
    const roh = Array.isArray(route.query.jahr) ? route.query.jahr[0] : route.query.jahr
    const zahl = roh == null ? NaN : Number(roh)
    return haushalt.jahre.includes(zahl) ? zahl : haushalt.haushaltsjahr
  })
  const index = computed(() => haushalt.jahre.indexOf(jahr.value))
  function setzeJahr(neu: number) {
    void router.replace({ query: { ...route.query, jahr: String(neu) } })
  }
  function jahrLink(ziel: RouteLocationRaw): RouteLocationRaw {
    return typeof ziel === 'string' ? ziel : { ...ziel, query: { ...ziel.query, jahr: String(jahr.value) } }
  }
  return { jahr, index, setzeJahr, jahrLink }
}
```
Ungültige Werte: Seite rendert mit dem Standard und bereinigt die URL per `router.replace` (UI-SPEC). `jahr` darf **nur** über `haushalt.jahre.includes(...)` akzeptiert werden, nie als Schlüssel in ein Objekt.

### Pattern 2: Reine Builder-Funktionen in `lib/`, Komponenten nur darstellen
**What:** Jede Ableitung (Ertragsarten, Drilldown-Ebene, Sankey, Zeitreihe) ist eine Funktion `(daten, jahrIndex) → Struktur`, ohne Vue/DOM. vitest prüft sie über alle `haushalt.jahre`.
**When to use:** immer; verhindert, dass die Bilanz-/Rundungslogik in Templates versickert, und macht D-11 („Test über alle 6 Jahre“) trivial.

### Pattern 3: Sankey-Builder (bilanzierend, datengetrieben)
**What:** Knoten und Links entstehen aus Datenzeilen, nicht aus Jahres-Sonderfällen.
**Algorithmus (empfohlen, Zahlen für 2026 gegengerechnet):**
- Linke Ertragsknoten aus `ergebnisplan.GESAMT.zeilen[…][i]`:
  - Steuern aufteilen: Gewerbesteuer, Anteil Einkommensteuer, Grundsteuer (A+B) aus `vorbericht.steuerarten.posten[].werte[i]`; **„übrige Steuern“ = Z.01 − Σ(drei) (Plug)**. Ohne Plug bilanziert 2024 nicht (Σ der acht T€-Posten = 19.615.000, GEP Z.01 = 19.614.808).
  - Zuwendungen: Schlüsselzuweisung (`vorbericht.zuwendungen`), „sonstige Zuwendungen“ = Z.02 − Schlüsselzuweisung (Plug).
  - Gebühren und Entgelte = Z.04 + Z.05; Finanzerträge = Z.19; „Sonstige“ = `ordentliche_ertraege` − (Steuern + Zuwendungen + Gebühren/Entgelte) (Plug, fängt Z.03/06/07/08/09 inkl. **Z.03 = 36.321 € in 2024** auf).
- Defizit-Knoten links = −`ergebnis_nach_minderaufwand`, falls < 0; Überschuss-Knoten rechts = `ergebnis_nach_minderaufwand`, falls > 0.
- **Minderaufwand-Knoten LINKS** (= −`globaler_minderaufwand`, falls ≠ 0), siehe Open Question 1.
- Mitte „Gemeindehaushalt“; rechte Knoten: KL (`ergebnisplan.KL.berechnet.aufwand[i]`), je PB (ohne KL, **PB 16 abzüglich Zinsen**, weil `berechnet.aufwand` dort Z.17+Z.20 enthält), „Zinsen“ = GEP `zinsaufwendungen`.
- Test: links = rechts für jedes Jahr mit **Toleranz 2 €** (2024: ΣPB-Aufwand = GEP −1, ΣPB-Erträge = GEP −1, 2028: ΣPB-Aufwand = GEP +1; im PDF gedruckte Rundung). Zusätzlich Test „kein Knoten mit Wert ≤ 0“.

**Gegenrechnung (alle Jahre, `python3` auf `haushalt.json`):** `ΣPB aufwand − GESAMT aufwand` = −1 (2024), 0, 0, 0, +1 (2028), 0; `Σ Erträge` −1 (2024), sonst 0; `Erträge − Aufwand − jahresergebnis` = 1 (2024), sonst 0; `jahresergebnis − globaler_minderaufwand − ergebnis_nach_minderaufwand` = 0 in allen Jahren [VERIFIED: Skript auf `app/src/data/haushalt.json`].

### Pattern 4: Treemap = eine flache Ebene je Ansicht, Navigation über den Router
**What:** `series[0].data` enthält nur die Kinder des aktuellen Knotens (kein `children`), `nodeClick: false`, `breadcrumb.show: false`, `roam: false`; Klick → `chartClick` → Router. Je Datensatz: `{ name, value, code, itemStyle: { color, decal? } }`.
**Verifiziert:** Knoten-`itemStyle.decal` erzeugt in Treemap, Sankey (Knoten) und Bar ein SVG-`<pattern>` auch **ohne** `AriaComponent`; ein Top-Level-`decal` am Datensatz tut es nicht [VERIFIED: ECharts-SVG-SSR-Lauf mit `echarts/core` + `SVGRenderer`, 2026-10-04].
**Beschriftung:** ECharts schneidet Treemap-Labels per `lineOverflow: 'truncate'` ab (`TreemapView.js:783-784`), blendet sie nicht aus. UI-SPEC verlangt „ausblenden statt abschneiden“ → pragmatisch `label.show` je Knoten über eine Flächenheuristik (`wert/summe × B × H ≥ 72×44 px`), Name bleibt im Tooltip und in `EbenenTabelle` [ASSUMED: Heuristik ist Annäherung, Squarify-Layout liefert keine exakte Vorab-Rechteckgröße].

### Pattern 5: Interne Links auf `wa-button`
```vue
<!-- Quelle: Vue-Router „RouterLink custom“-Muster [ASSUMED: Kombination mit wa-button (Link im Shadow-DOM) in Wave 0 per Spike prüfen] -->
<RouterLink :to="jahrLink({ name: 'ausgaben' })" custom v-slot="{ href, navigate }">
  <wa-button variant="brand" size="large" :href="href" @click="navigate">Ausgaben ansehen</wa-button>
</RouterLink>
```
Rückfall, falls der Spike scheitert: `RouterLink` mit `class="om-knopf"` im `wa-button`-Look (Tokens), UI-SPEC bleibt in Optik erfüllt.

### Anti-Patterns to Avoid
- **`wa-radio-group appearance="button"`:** Das Attribut `appearance` gehört zu **`wa-radio`**, nicht zur Gruppe [VERIFIED: `custom-elements.json` — `wa-radio`-Attribute `['value','appearance','size','disabled','name',…]`, `wa-radio-group`-Attribute `['label','hint','name','disabled','orientation','value','size','required',…]`]. UI-SPEC-Wortlaut deshalb als `<wa-radio appearance="button">` umsetzen.
- **Records mit URL-Schlüsseln indexieren:** `haushalt.ergebnisplan[route.query.pb]` liefert bei `__proto__`/`constructor` Objekt-Prototypen. Immer erst gegen eine aus `haushalt.knoten` gebaute `Map`/Allowlist prüfen (Security).
- **`echarts.color.lift(farbe, -0.1)` zum Abdunkeln:** In ECharts 6.1 multipliziert negatives `level` mit `1 − level` und **hellt auf** (`zrender/lib/tool/color.js:301-302`: `colorArr[i] = colorArr[i] * (1 - level) | 0`). `abstufung()` selbst implementieren (je Kanal `Math.round(c × (1 − p))`).
- **Zahlen in ECharts-HTML-Tooltips unescaped:** `formatter`-Strings werden als HTML gerendert; dynamische Namen mit `format.encodeHTML` (aus `echarts/core`) oder `valueFormatter` verwenden.
- **Jahr-gebundene Erklärtexte neben anderem Jahr anzeigen:** siehe Pitfall 6.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sankey-Layout, Hover-Nachbarschaft | Eigenes SVG-Layout | ECharts `sankey` (`emphasis.focus: 'adjacency'`, `layoutIterations`, `draggable: false`) | Ordnung/Knotenhöhen/Kurven; Optionen im SVG-SSR-Lauf akzeptiert [VERIFIED] |
| Treemap-Squarify | Eigenes Layout | ECharts `treemap` mit flacher Datenliste | Layout ist gelöst; Navigation bewusst extern (D-06) |
| Mobiles Menü, Escape, Fokusrückgabe | Eigenes Overlay | `wa-drawer` (`open`, `wa-hide`, `light-dismiss`) | Dialog-Semantik inklusive [VERIFIED: custom-elements.json] |
| Aufklapper/Akkordeon | Eigenes `<details>`-Gebilde | `wa-details` (`name` für exklusive Gruppen, Events `wa-show`/`wa-hide`) | Konsistente Optik/A11y |
| Tooltip an Fließtext-Begriffen | Eigenes Popover | `wa-tooltip for="<id>"` (Anker per ID, Escape schließt) | [VERIFIED: Attribut `for` in custom-elements.json] |
| Hash-Scroll `/glossar#begriff` | Eigenes `scrollIntoView` | `scrollBehavior(to) { if (to.hash) return { el: to.hash } }` + `scroll-margin-top: var(--scroll-margin-top)` | `wa-page` setzt die Variable (Kopfhöhe + 0,5 em) [VERIFIED: `chunk.FFR4H3XU.js:17`] |
| Skip-Link | Zweiten Link bauen | Den vorhandenen `wa-page`-Skip-Link überschreiben (Slot `skip-to-content`) und dessen Klick abfangen | siehe Pitfall 2 |
| Zahlen-/Prozentformat | Eigene `toLocaleString`-Aufrufe | `charts/format.ts` (`euro`, `euroKurz`, `prozent`, `formatiere`) | Einzige Formatierungsstelle; Pipeline-Test spiegelt sie |
| Platzhalter-Auflösung in Texten | Vorformatierte Zahlen in der Pipeline | App-Funktion mit demselben Regex wie `texte.py` + `formatiere()` | P4 D-15: Pipeline formatiert nie |
| Glossar-/Erklärtext-Parser | Neuer Markdown-Parser | `ostbevern.texte.lies_erklaerungen` verallgemeinern (Kopfzeile/Quelle-Regel parametrisieren) | Ziffern-Test, Schlüsselregeln, Tests existieren |
| Sortierung deutscher Begriffe | Eigener Vergleich | `Intl.Collator('de')` / `localeCompare('de')` (Ä/Ö/Ü korrekt: `aÄbÖüZ`) [VERIFIED: Node-Lauf] | Umlaute |
| Kontrastberechnung | Externe Bibliothek | 15-Zeilen-WCAG-Funktion im Test (Palette: 16 Farben × 3 Stufen) | Eine Zahl, kein Paket nötig |

**Key insight:** Das Risiko in dieser Phase liegt nicht in fehlenden Bibliotheken, sondern darin, dass Ableitungen (Bilanz, Plugs, Rundung, Jahr-Bindung) in Templates verstreut und ungeprüft landen. Alles Rechnerische gehört in getestete reine Funktionen.

## Common Pitfalls

### Pitfall 1: Minderaufwand rechts im Sankey bilanziert nie
**What goes wrong:** UI-SPEC/D-12 setzen „Globaler Minderaufwand“ rechts. Links = Erträge + Defizit(nach MA) = 29.855.569, rechts = Aufwand + MA = 31.055.569 (2026) — nie gleich, der Bilanz-Test (D-11) scheitert für alle Jahre mit MA ≠ 0 (2025–2029).
**Why:** `ergebnis_nach_minderaufwand` = `jahresergebnis` − `globaler_minderaufwand` (Z.28 = Z.26 − Z.27), die PB-Aufwände sind **vor** MA (Spez. 3.3). Der MA ist eine erwartete Einsparung, also eine Deckungsquelle.
**How to avoid:** MA-Knoten **links** (Quelle), Defizit-Knoten = −Z.28. Dann gilt Σ links = Erträge + (−Z.28) + (−Z.27) = Erträge − Z.26 = Aufwand = Σ rechts [VERIFIED: Rechnung für alle 6 Jahre]. Die Erklärung „So liest du das Diagramm“ sagt dann sinngemäß: „Aufwand = Erträge + Entnahme aus Rücklagen + pauschal eingeplante Einsparung“. Alternative, die UI-SPEC unverändert lässt, existiert nicht (ohne Defizit auf 2,95 Mio. zu ändern, was Spez. 6.6 widerspricht). → Open Question 1, Bestätigung einholen.
**Warning signs:** Bilanz-Test rot für 2025–2029.

### Pitfall 2: `wa-page` bringt einen englischen Skip-Link mit, der im Hash-Router „zurück zur Startseite“ führt
**What goes wrong:** `wa-page` rendert immer `<a href="#main-content" part="skip-to-content" class="wa-visually-hidden"><slot name="skip-to-content">Skip to content</slot></a>` [VERIFIED: `@awesome.me/webawesome/dist/chunks/chunk.POQQIIHO.js:213-214`]. Im Hash-Router wird `#main-content` zum Pfad `/main-content`: `if (pathFromHash[0] !== "/") pathFromHash = "/" + pathFromHash;` [VERIFIED: `vue-router/dist/vue-router.js:22`], der Catch-all (`router/index.ts`: `redirect: { name: 'start' }`) springt auf die Startseite. Das Problem existiert seit Phase 1 (`App.vue` nutzt `wa-page`).
**How to avoid:** (1) deutschen Text über `<span slot="skip-to-content">Zum Inhalt springen</span>` setzen (statt zweiten Skip-Link, sonst zwei Tab-Stopps; der ESLint-Eintrag `ignoreParents` muss `wa-page` weiter enthalten, ist er bereits); (2) am `wa-page`-Host einen `click`-Listener (Capture) registrieren, der bei `event.composedPath()` mit `a[part="skip-to-content"]` `preventDefault()` aufruft und `h1`/`#main-content` per `focus({ preventScroll: false })` fokussiert (`wa-page` legt `<div id="main-content" slot="skip-to-content-target">` selbst an, `tabindex="-1"` ergänzen). Spike in Wave 0.
**Warning signs:** Tab → Enter am Skip-Link ändert die Seite auf Start.

### Pitfall 3: Pro-Kopf-Rundung — Kennzahlenband rundet, Schulden-Pipeline rundet ab
**What goes wrong:** 30.455.569 / 11.741 = 2.593,95 → Erfolgskriterium „≈ 2.594 €“ verlangt **Runden** (`Math.round`); ganzzahlige Division liefert 2.593. Steuern 18.443.000 / 11.741 = 1.570,82 → 1.571 (Abrunden 1.570) [VERIFIED: `python3`]. Dagegen verwendet die Pipeline für Schulden pro Kopf bewusst `//` (656 € reproduziert den gedruckten Wert, `manuell.pro_kopf_euro`).
**How to avoid:** Eine einzige App-Funktion `proKopf(betrag, einwohner)` mit `Math.round`, getestet gegen 2594/1571; Schulden-Pro-Kopf **nicht** neu berechnen, sondern `investitionen.schuldenstand.pro_kopf` verwenden (Phase 6). Aufwand pro Kopf nimmt `berechnet.aufwand` (= Z.17 + Z.20, inkl. Zinsen), nicht Z.17 allein (2.577 €).

### Pitfall 4: Tabelle 2.1.7 (S. 33) druckt für 2028 den Gesamtwert 2.396 statt 2.346
**What goes wrong:** Posten 2028: 470 + 1.520 + 33 + 245 + 77 = **2.345**, gedruckte Gesamtzeile **2.396**, GEP Z.07 2028 = 2.346.161 € [VERIFIED: PDF S. 33 per pdfplumber **und** gerendertes Seitenbild; GEP aus `haushalt.json`]. Regel 5 wird dadurch rot: Stufe (a) −51.000 €, Stufe (b) +49.839 € (Toleranz 1.000 €).
**Weitere Abweichungen derselben Tabelle:** Stufe (a) 2024: Posten 2.766 vs. gedruckt 2.764 (+2.000 €); 2025: 2.107 vs. 2.106 (+1.000 €). Stufe (b) 2024/2025/2026/2027/2029 innerhalb ±1.000 € (−446/−281/−386/−885/−136).
**How to avoid:** Abschrift **wie gedruckt** (P4 D-05, auch 2.396), `befunde.md`-Einträge nach dem Muster der vorhandenen Zeilen (Wortlaut „Wortweise gegen das PDF verifiziert … Druckfehler im Vorbericht selbst“); in `baue_vorbericht_tabelle(..., sonstige=True)` entsteht der berechnete Posten „Sonstige“ für 2028 (GEP − Σ Posten = 1.161 €); die App zeigt die **Planzeile** als maßgeblich (CONTEXT „Specifics“: gewinnt die Quelle, die zum Gesamtplan passt).
**Warning signs:** `uv run … alle.py` bricht bei Schritt 06 ab, „Veraltete Befunde“ > 0, wenn ein Befund nicht mehr passt.

### Pitfall 5: Pauschalen gibt es im PDF nur für 2026
**What goes wrong:** S. 52 („Bei den Zuweisungen und Zuschüssen für Investitionen handelt es sich um:“) hat **eine** Spalte „2026 Gesamt T€“: Zuweisungen und Zuschüsse für Investitionen 3.742; Investitionspauschale 1.525; Schulpauschale 406; Sportpauschale 60; Feuerschutzpauschale 68; Förderung Mobilstation OT Brock (80 %) 510; Förderung Erweiterung OGS Ambrosius-Grundschule 467; Förderung Wirtschaftswege (70 %) 350; Förderung Austausch Leuchtköpfe (25 %) 75; Förderung barrierefreier Bahnhof (90 %) 162; Förderung Fahrradabstellanlage JAS (75 %) 119. Σ Pauschalen 2.059 + Förderungen 1.683 = 3.742 = GFP Z.18 2026 (3.742.000 €) ✓. Für 2027–2029 steht nur der Satz „In den Folgejahren sind die Pauschalen … veranschlagt“ [VERIFIED: PDF S. 52, GFP aus `haushalt.json`].
**How to avoid:** Tabelle wie `kita_zuschuesse` führen (eine Jahresspalte; andere Jahre `null`), Gesamtzeile 3.742 mitschreiben (Regel 5 Stufe (a) exakt, Stufe (b) gegen GFP Z.18 — dafür braucht Regel 5 einen **GFP-Zweig**, bisher nur Ergebnisplan, siehe Code Examples). Für Jahre ohne Aufschlüsselung zeigt `/einnahmen` nur die GFP-Zeilen; die Pauschalen-Zeilen erscheinen als „–“, „Sonstige (berechnet)“ trägt den gesamten Z.18-Wert. Das löst die „unresolved“-Zeile E6/partial im UI-SPEC (Annahme „Leerzustand je Zeile –“ ist damit bestätigt).
**Empfehlung zur Zuordnung:** alle 10 Zeilen abschreiben (dann ist „Sonstige“ in 2026 = 0 und die Summe exakt); das Chart zeigt Investitions-, Schul-, Sportpauschale einzeln, den Rest als „Sonstige (berechnet)“ — Diskretion des Planers (D-03 lässt beides zu).

### Pitfall 6: Jahr-gebundene Erklärtexte neben anderem Jahr
**What goes wrong:** `texte.json` enthält nur Werte des Haushaltsjahrs (2026) bzw. feste Jahresschlüssel; Texte wie `kreisumlage`, `globaler_minderaufwand`, `defizit_ruecklagen` nennen 2026-Zahlen. Wählt jemand `?jahr=2027`, würde ein unverändert eingeblendeter Text neben 2027-Zahlen stehen (Core-Value-Verstoß).
**How to avoid:** Curated Texte nur anzeigen, wenn `jahr === haushalt.haushaltsjahr` (oder explizit „Haushaltsplan {haushaltsjahr}“ beschriften); sonst eine **App-komponierte, zahlenneutrale oder aus den Daten des gewählten Jahres berechnete** Kurzaussage (Zahl über `formatiere()` aus `haushalt.json`, UI-SPEC erlaubt Oberflächentexte ohne Zahl im Komponentencode). `defizit_ruecklagen` hat zusätzlich Satzungsbezug nur für 2026. D-11 verlangt „muss zum Jahr passen“ — so erfüllbar.

### Pitfall 7: `DatenTabelle`/`BaseChart` tragen Phase-1-Platzhaltertexte
**What goes wrong:** Beide zeigen bei leerem Zustand „Noch keine Daten … ab Phase 2 automatisch aus dem PDF erzeugt“ (`BaseChart.vue:68-71`, `DatenTabelle.vue:56-59`); der Fehlertext nennt „GitHub Issues im Quell-Repository“ (`BaseChart.vue:63`), UI-SPEC verlangt „nutze den Kontakt in der Fußzeile“ und „Für {jahr} gibt es keine Einzelwerte“. `DatenTabelle` zeigt `null` **leer** (nur versteckter Text „kein Wert“), UI-SPEC verlangt sichtbares „–“. `alsZahl()` wirft bei `undefined` in numerischen Spalten (Seite stürzt ab) — Builder müssen `null` liefern, nie `undefined`.
**How to avoid:** Additive Props (`leerTitel`, `leerText`, Fehler-Slot-Default ersetzen), „–“ mit `aria-hidden` plus Screenreader-Text, **Zellen-Slot** für Buttons/Links/Etiketten: Scoped-CSS der Elternkomponente erreicht Slot-Inhalt nicht (`.om-tabelle th/td` in `DatenTabelle.vue` sind `scoped`), also die Tabellenzellen weiter in `DatenTabelle` rendern und über einen scoped Slot `#zelle="{ zeile, spalte, wert }"` erweitern (Props bleiben kompatibel, CLAUDE.md-Konvention).

### Pitfall 8: Jahr-Zeitreihe: Quellenwechsel und Wertart pro Jahr
**What goes wrong:** 2022–2023 stammen aus den Grundzahlen (`produkte.json`, Produkt 160101, Positionen 1–9), 2024–2029 aus `vorbericht.steuerarten`. Die Wertart für 2022/2023 fehlt in `haushalt.wertarten` (nur 2024–2029) → separat als „ergebnis“ führen. Grundzahl-Bezeichnungen tragen Rauschen („Gewerbesteuer (Im Teilplan Zeile 01)“, „Kompensationsleistung“ vs. „Kompensationszahlungen“), Positionsnummern sind layoutabhängig.
**How to avoid:** Eine Mapping-Tabelle `{ posten → grundzahlPosition }` an **einer** Stelle (`lib/zeitreihen.ts` oder Pipeline), abgesichert durch einen Test, der `bezeichnung`, `einheit === 'EUR'` und Produkt prüft. Pos. 1–8 = Gewerbesteuer, Grundsteuer A, Grundsteuer B, Anteil Einkommensteuer, Anteil Umsatzsteuer, Vergnügungssteuer, Hundesteuer, Kompensationsleistung; Pos. 9 = Schlüsselzuweisung [VERIFIED: `produkte.json`, 160101]. Die Vorbericht-Quelle (S. 27) belegt die Texte: „2022 … 9,7 Mio. €, … 2023 … 4,8 Mio. €, … 2024 auf 9,5 Mio. €“ [VERIFIED: PDF S. 27] — das stützt D-01/D-02.
**Doppelpunkt:** Im Übergangsjahr teilen sich Serien einen Punkt (UI-SPEC). Der gemeinsame Punkt braucht `symbol: 'none'` in der späteren Serie, der Tooltip eine eigene `formatter`-Logik, sonst erscheinen doppelte Zeilen.

### Pitfall 9: Zeilenbeschriftungen fehlen im JSON
**What goes wrong:** `haushalt.json` kennt nur kanonische Schlüssel (`steuern`, `oeffentlich_rechtliche_entgelte`, …), keine gedruckten Namen. Das Produktdetail („Teilergebnisplan 2024–2029“), `/einnahmen` Ebene 1 und Aufwandsart brauchen deutsche Bezeichnungen.
**How to avoid:** Pipeline gibt aus `ostbevern/zeilen.py::ZEILEN` einen Block `zeilen_namen` (Reihenfolge, Name, `ist_summe`) für Ergebnis- **und** Finanzplan nach `haushalt.json` — einzige Quelle der Wahrheit; `Haushalt`-Typ in `typen.ts` ergänzen (Test: jeder Schlüssel aus `ERGEBNISPLAN_APP_ZEILEN` hat einen Namen). Quote aus `app_daten.py:91-96`: `ERGEBNISPLAN_APP_ZEILEN: tuple[str, ...] = tuple(ZEILEN["gesamtergebnisplan"][f"{nummer:02d}"].kanonisch for nummer in range(1, 27)) + (ZEILEN["gesamtergebnisplan"]["27"].kanonisch, ZEILEN["gesamtergebnisplan"]["28"].kanonisch,)`. Alternative (App-Konstante mit Test) ist schwächer.

### Pitfall 10: `wa-details`/Lint — ESLint kennt nur zwei WA-Eltern für `slot`
`eslint.config.ts:29`: `'vue/no-deprecated-slot-attribute': ['error', { ignoreParents: ['wa-page', 'wa-callout'] }]` [VERIFIED]. Jede neue native `slot="…"`-Nutzung (`wa-details`-Summary, `wa-drawer`-Label, `wa-card` Header/Footer, `wa-select`) löst `npm run lint`-Fehler aus. In Wave 0 `ignoreParents` um `wa-details`, `wa-drawer`, `wa-card`, `wa-select`, `wa-button`, `wa-radio-group` erweitern.

### Pitfall 11: Nur drei Icons selbst gehostet
`app/public/icons/solid/` enthält `bars.svg`, `circle-info.svg`, `triangle-exclamation.svg` [VERIFIED: `ls`]. Der UI-Vertrag nennt weitere (Externer-Link-Hinweis u. a.). Ein fehlendes Icon lädt **nicht** von einem CDN (setIconPath), sondern bleibt leer. Benötigte SVGs aus Font Awesome Free 7.x kopieren (CC-BY-Kommentar in der Datei lassen); `arrow-up-right-from-square.svg` ist erreichbar (HTTP 200 von `raw.githubusercontent.com/FortAwesome/Font-Awesome/7.x/svgs/solid/`) [VERIFIED: curl]. System-Icons (`chevron`, `xmark`) von `wa-details`/`wa-drawer` sind eingebaut.

### Pitfall 12: Toolchain-Stolpersteine in der Sandbox
(a) Sandbox-`npm` = 9.2.0; neue Pakete mit `npm 10` installieren (lokal `npm install npm@10.9.2` in ein Hilfsverzeichnis, dann `node …/npm-cli.js`), sonst `edgesOut`-Absturz (nur bei vitest 4.x/5.0.1 beobachtet, 5.0.3 lief). (b) `app/node_modules` im gemounteten Repo enthält macOS-Binaries → App-Prüfungen in Scratch-Kopie (STATE.md). (c) Node 22.22.1 < 22.22.2: EBADENGINE-Warnungen bei vorhandenen Abhängigkeiten, harmlos. (d) Kein Browser vorhanden: Sichtprüfung/Lighthouse manuell bzw. Phase 7.

### Pitfall 13: `format.ts` muss eigenständig bleiben
`pipeline/tests/test_formatiere.py` transpiliert `app/src/charts/format.ts` mit `ts.transpileModule` und importiert es per `data:`-URL (`_NODE_SKRIPT`, Zeilen ~288-300) — **keine Imports in `format.ts`**, und `export type FormatKuerzel = …` muss einzeilig bleiben (`test_texte.py::test_formatkuerzel_wie_format_ts` liest per Regex `export type FormatKuerzel = ([^\n]+)`). Die Fallback-Erweiterung (WR-06/IN-01) also so bauen: nicht endlicher Wert → `'–'` (UI-SPEC), unbekanntes Kürzel → `throw` (WR-06), und das Python-Port `formatiere_port` + Tests mitziehen.

### Pitfall 14: Vorhandene Tests kodieren Tabellenmenge/Reihenfolge/Textumfang
`test_app_daten.py:181-191` fordert exakt `["steuerarten","zuwendungen","transferaufwendungen","kita_zuschuesse","leistungsentgelte","kostenerstattungen","personal","sachaufwand","sonstige_aufwendungen"]`; `test_manuell.py:256` vergleicht die Tabellenmenge mit `WEITERE_VORBERICHTSTABELLEN`; `test_texte.py:347` fordert `{text.schluessel …} == _D16_SCHLUESSEL`. Neue Tabellen/Texte erfordern gezielte Testanpassungen, sonst bricht CI.

### Pitfall 15: `.prettierignore` und CI-Diff
Neue generierte JSON-Dateien (z. B. `glossar.json`, falls getrennt) in `app/.prettierignore` eintragen (dort stehen die fünf bestehenden; `format:check` läuft über `src/`), sonst bricht `format:check`; die CI-Diff-Prüfung (`git diff --exit-code -- daten app/src/data`) verlangt, dass `alle.py` neue Dateien deterministisch erzeugt und sie eingecheckt sind.

### Pitfall 16: Treemap/Sankey-Knotenidentität und Klick
Sankey-Knoten werden über `name` identifiziert (muss eindeutig sein); Klicks liefern `params.dataType === 'node'`/`'edge'` und `params.data`. Eindeutige IDs (`pb:01`, `kl`, `ertrag:gewerbesteuer`) als `name`, Anzeigetext über `label.formatter` aus einem eigenen Feld, Zielcode als `data.code`. `BaseChart.emit('chartClick', params: unknown)` → Typ-Guard schreiben, nie `as any`.

### Pitfall 17: Anteile und „rd.“ in KL
KL (11.001.181 €) hat drei „rd.“-Kinder mit Σ 11.001.000 € (10.147.000 + 654.000 + 200.000); Differenz 181 € ist erwartet (`gerundet`, P4 D-02). Anteile je Ebene als Wert/Σ(gezeigte Kinder), Beträge als „rd. 10,1 Mio. €“ kennzeichnen (Flag `knoten.gerundet`).

### Pitfall 18: Zeitreihenachsen und `connectNulls`
Konzessionsabgaben/Pauschalen haben Lücken; `connectNulls: false` (UI-SPEC). Y-Achse bei 0 beginnen lassen (`min: 0`).

## Code Examples

### Platzhalter-Renderer (App-Seite, fehlt noch)
```typescript
// Regex und Vertrag gespiegelt von pipeline/ostbevern/texte.py:35
//   PLATZHALTER_MUSTER = re.compile(r"\{\{([a-z0-9_.]+)\|([a-z]+)\}\}")
import { formatiere, type FormatKuerzel } from '@/charts/format'
import { texte } from '@/data/daten'

const MUSTER = /\{\{([a-z0-9_.]+)\|([a-z]+)\}\}/g

export function rendereAbsatz(absatz: string): string {
  return absatz.replace(MUSTER, (_voll, schluessel: string, kuerzel: string) => {
    const wert = texte.werte[schluessel] // noUncheckedIndexedAccess: number | undefined
    return wert === undefined ? '–' : formatiere(wert, kuerzel as FormatKuerzel)
  })
}
```
Gerendert **als Text** (`{{ }}`-Interpolation), nie `v-html` (Ziffern-/HTML-Verbot der Pipeline, P4 T-04-17).

### Regel-5-Erweiterung (Pipeline)
Vorhanden (Quote, `pruefung.py:993-1002`):
```python
REGEL5_GEP_ZEILEN: dict[str, str] = {
    "steuerarten": "01",
    "zuwendungen": "02",
    "transferaufwendungen": "15",
    "leistungsentgelte": "04",
    "kostenerstattungen": "06",
    "personal": "11",
    "sachaufwand": "13",
    "sonstige_aufwendungen": "16",
}
```
und `WEITERE_VORBERICHTSTABELLEN` (`pruefung.py:1006-1012`): `("leistungsentgelte", "kostenerstattungen", "personal", "sachaufwand", "sonstige_aufwendungen")`.
Zu tun: (1) 2.1.7 als sechste Tabelle `sonstige_ertraege` in `WEITERE_VORBERICHTSTABELLEN` und `"sonstige_ertraege": "07"` in `REGEL5_GEP_ZEILEN`, `app_daten.py` liest sie automatisch über `zerlege_weitere_vorberichtstabellen` und `REGEL5_GEP_ZEILEN.get(tabelle)`; (2) Pauschalen als eigene Datei `investitionszuwendungen.csv` (wie `kita_zuschuesse`: keine GEP-Zeile, `planzeile`/`gesamt_plan` `null`) plus neuer Zweig in `_pruefe_regel5…`, der die Gesamtzeile des Haushaltsjahrs × 1000 gegen **GFP Z.18** vergleicht (`ZEILEN["gesamtfinanzplan"]["18"]` = `Zeilendefinition("Zuwendungen für Investitionsmaßnahmen", "investitionszuwendungen", False)`, `zeilen.py:144-146`); die Prüffunktion bekommt dafür ein zweites `Planwerte(finanzplan, datei="finanzplan")`. (3) `meta.json` → `vorbericht_werte`: Schlüsselmuster `^[a-z][a-z0-9_]*$` (`manuell.py:25`) erlaubt `konzessionsabgabe_strom|gas|wasser` (315/40/115 T€, S. 33, `einheit: euro`, `gerundet: true`); Kontrolle Σ = 470 T€ der Tabellenzeile.

### ECharts-Registrierung (Erweiterung von `echartsTheme.ts`)
Vorhanden (`echartsTheme.ts:12`): `use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])`. Ergänzen: `TreemapChart`, `SankeyChart`, `LineChart` (aus `echarts/charts`), `LegendComponent`, `AriaComponent` (aus `echarts/components`) [VERIFIED: ein Lauf mit `echarts/core` + `SVGRenderer` + `TreemapChart, SankeyChart, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent` rendert Decals ohne `AriaComponent`; Registrierung laut UI-SPEC trotzdem sinnvoll].
```typescript
export function abstufung(farbe: string, rang: number): string {
  const p = [0, 0.1, 0.2][rang % 3] ?? 0          // nur abdunkeln (UI-SPEC)
  const [r, g, b] = hexZuRgb(farbe)                // Tokens liefern Hex; bei Nicht-Hex → Ersatzwert
  return rgbZuHex(Math.round(r * (1 - p)), Math.round(g * (1 - p)), Math.round(b * (1 - p)))
}
```

### Treemap-Datensatz mit KL-Decal
```typescript
// itemStyle.decal am Datensatz [VERIFIED: SVG-SSR-Lauf, erzeugt <pattern>]
const KL_DECAL = { symbol: 'rect', dashArrayX: [1, 0], dashArrayY: [2, 5], rotation: Math.PI / 4,
                   color: 'rgba(255,255,255,0.45)' } // Farbe aus Token surface-default ableiten
data.push({ name: 'Weitergabe an Kreis und Land', value: wert, code: 'KL',
            itemStyle: { color: KL_FARBE, decal: KL_DECAL } })
```

### Router: Hash-Scroll, Fokus, Titel
```typescript
// scrollBehavior-Rückgabe { el: '#id' } nutzt document.getElementById (nur Light-DOM-Ziele) [VERIFIED: devtools-*.js scrollToPosition]
const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [/* start, einnahmen, ausgaben, produkt (path '/produkt/:code'), geldfluss, glossar + Catch-all */],
  scrollBehavior: (to) => (to.hash ? { el: to.hash, top: 0 } : { top: 0 }),
})
router.afterEach(async (to, from) => {
  document.title = `${to.meta.titel ?? ''} – Ostbevern Money`
  if (to.path === from.path && !to.hash) return        // reiner Query-Wechsel: Fokus nicht verschieben
  await nextTick()
  const ziel = to.hash ? document.getElementById(to.hash.slice(1)) : document.querySelector('h1')
  ziel?.setAttribute('tabindex', '-1'); ziel instanceof HTMLElement && ziel.focus({ preventScroll: !!to.hash })
})
```
`h1` braucht `tabindex="-1"` (in `PageIntro.vue` ergänzen; derzeit nicht gesetzt). Glossar-Abschnitte: `scroll-margin-top: var(--scroll-margin-top)`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Münster-Komponenten als Vorlage | eigene Komponenten, Münster-Namen/Props | Phase 1 (D-02/D-03) | Basiskomponenten nur additiv erweitern |
| `wa-page`-Navigationsdrawer | eigener `wa-drawer` im Kopf (D-13); `wa-page`-Nav bleibt ungenutzt (`disableNavigationToggle` wird automatisch `true`, wenn keine Navigation-Slots befüllt sind) [VERIFIED: `chunk.POQQIIHO.js` `updateNavigationToggleState`] | Phase 5 | Skip-Link-Fund beachten |
| vitest 3/4 | vitest 5 (Sept. 2026) | 2026-09-03 (5.0.0) | 4.x im Projekt nicht installierbar (Pitfall 12) |

**Deprecated/outdated:**
- UI-SPEC-Formulierung `wa-radio-group appearance="button"`: Attribut liegt am `wa-radio`.
- `jahrgang.json` (`{"haushaltsjahr": 2026}`) dupliziert `haushalt.haushaltsjahr` (Review IN-02-Muster); neue Seiten nutzen `haushalt.haushaltsjahr`, `StartPage.vue` verliert Demo-Inhalt (`beispieldaten.json`).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Minderaufwand gehört links (Quelle) und heißt dort „Globaler Minderaufwand (erwartete Einsparung)“; Zustimmung des Nutzers, dass der UI-SPEC-Wortlaut „rechts“ dafür abgeändert wird | Pitfall 1, Open Question 1 | Sankey bilanziert nicht oder zeigt gegen Spez. 6.6 abweichende Zahlen |
| A2 | `RouterLink custom` + `wa-button :href @click="navigate"` funktioniert (Link im Shadow-DOM) | Pattern 5 | Rückfall auf gestylten `RouterLink`, kleine Mehrarbeit |
| A3 | Flächenheuristik reicht, um Treemap-Beschriftungen kleiner Kacheln auszublenden | Pattern 4 | Abgeschnittene Labels bleiben sichtbar; Tooltip/Tabelle tragen den Namen trotzdem |
| A4 | Capture-Listener auf `wa-page`-Host kann den Klick des Shadow-DOM-Skip-Links per `composedPath()` abfangen | Pitfall 2 | Alternativ `wa-page` ohne Skip-Link-Part mit eigenem Link ersetzen (Spike) |
| A5 | Die Pauschalen-Tabelle S. 52 wird vollständig (10 Zeilen) abgeschrieben; „Sonstige (berechnet)“ nur für Jahre ohne Aufschlüsselung | Pitfall 5 | Chart-Zeilen weichen vom UI-SPEC ab, Planer entscheidet (D-03 offen) |
| A6 | Pro-Einheit-Werte im Produktdetail („Zuschussbedarf je Schüler/in“) nur für eine kleine, fachlich bestätigte Liste von Grundzahlen (Schüler/innen Produkte 030101/030102/040301, betreute Kinder 060101); generisch „je Einwohner“ für alle Produkte | Open Question 6 | Falsche Nenner (Anz. ≠ Personen) → irreführende Pro-Kopf-Werte |
| A7 | Der Zeitreihen-Mapping-Test (GZ-Position ↔ Bezeichnung) genügt statt Pipeline-Ableitung | Pitfall 8 | Spätere Jahrgänge verschieben Positionen; Test schlägt dann laut fehl (gewollt) |
| A8 | Original-PDF-Link: die Gemeinde-Seite `https://www.ostbevern.de/rathaus/politik/gemeindehaushalt.html` kommt per Websuche als Landingpage für den Haushalt vor; die direkte PDF-URL 2026 ist unbekannt (WebFetch dieser Seite: 403) | Open Question 5 | Fußzeilen-Link zeigt ins Leere; Nutzer muss URL liefern |
| A9 | „Ist“ für 2024 ist laut PDF-Spaltenkopf „vorl. RE“ (vorläufiges Rechnungsergebnis); die Wertart-Erklärung (UI-SPEC: „Ist: das Ergebnis eines abgeschlossenen Jahres“) sollte „vorläufig“ erwähnen | Open Question 3 | Leichte Ungenauigkeit gegenüber dem Quelldokument |

## Open Questions

1. **Minderaufwand links oder rechts im Sankey?** (blockiert Plan Geldfluss)
   - Know: Nur links (als Quelle) bilanziert er, ohne das Defizit auf 2,95 Mio. € (vor MA) zu ändern. Rechnung in Pitfall 1.
   - Unclear: UI-SPEC/D-12 und Spez. 6.6 schreiben „rechts“, vermutlich beiläufig.
   - Recommendation: Vor Planung vom Nutzer bestätigen lassen; Plan setzt links um, Mobil-Balken analog („Woher“ enthält den MA, „Wohin“ enthält ihn nicht).

2. **Skip-Link-Verhalten** — Planer sieht Spike in Wave 0 vor (Pitfall 2); kein Nutzerentscheid nötig, aber Auswirkung auf `App.vue` und Phase 7 (Lighthouse).

3. **Wertart „Ist“ für 2024 = „vorl. RE“** — Wortlaut der Wertart-Erklärung („Ist: das Ergebnis eines abgeschlossenen Jahres“) um „vorläufig“ ergänzen? Empfehlung ja (Genauigkeit, A9).

4. **Satz auf der Einstiegskachel „Den größten Anteil bekommt {Aufgabenbereich}“** — KL (11,0 Mio. €) ist der größte Top-Knoten, ist aber kein Aufgabenbereich und steht schon im Kreisumlage-Hinweis. Empfehlung: größten **PB ohne KL** nehmen (2026: PB 01 Innere Verwaltung, 4.519.223 €) und im Satz „Aufgabenbereich“ beibehalten.

5. **Original-PDF-URL und Kontakt-E-Mail** — beides fehlt (D-17/D-18). Empfehlung: `app/src/config.ts` mit Platzhalter (`kontakt-noch-nicht-festgelegt@example.invalid`, `.invalid` ist reserviert) und PDF-Platzhalter-URL; Phase 7 weist beide zurück. Vom Nutzer vor Phase 7 zu liefern.

6. **Welche Grundzahlen bekommen einen Pro-Einheit-Wert?** Einheiten im Bestand: „Anz.“ (135), „EUR“ (63), „%“ (7), „Schüler“ (1), … [VERIFIED: `produkte.json`]. „Anz.“ bezeichnet teils Personen (030101 „Schüler/innen“ 294/317/342/337 für 2022–2025), teils Objekte. Empfehlung: generische Spalte „Zuschussbedarf je Einwohner (berechnet)“ für jedes Produkt, Pro-Einheit nur für eine fachlich bestätigte Liste (im Text-Checkpoint mit abnehmen lassen). Zuschussbedarf gibt es 2024–2029, Grundzahlen-Ist nur 2022–2025 → Pro-Einheit nur für Jahre mit beiden Werten (2024, 2025).

7. **Jahre ohne Aufschlüsselung in der Pauschalen-Ansicht** — durch Pitfall 5 gelöst (Annahme A5 bestätigen).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | App-Build/Test | ✓ | 22.22.1 (`engines ^22.18.0`) | — |
| npm | Abhängigkeiten | ✓ (alt) | 9.2.0 (Sandbox); CI: Node-22-npm 10.x | `npm install npm@10.9.2` in Hilfsverzeichnis |
| uv + Pipeline-venv | Pipeline/pytest | ✓ | uv 0.9.26, `pipeline/.venv` Python 3.12 | — |
| pdfplumber (via venv) | Abschrift lesen (S. 33, S. 52) | ✓ | im venv | — |
| npm-Registry | vitest | ✓ | `npm view` erreichbar | — |
| raw.githubusercontent.com | Icon-Download | ✓ | HTTP 200 | — |
| ostbevern.de | PDF-URL ermitteln | ✗ | WebFetch 403 | Nutzer liefert URL (Open Question 5) |
| Browser (Chromium/Firefox) | Sichtprüfung, Lighthouse | ✗ | — | manuell durch Nutzer, Lighthouse in Phase 7 |
| Context7/Exa/Brave-MCP | Recherche | ✗ (in dieser Session nicht verfügbar) | — | lokale Quellen (node_modules, `custom-elements.json`, `llms.txt`), PDF |

**Missing dependencies with no fallback:** keine für die Ausführung; Browser fehlt für visuelle Abnahme (human-verify am Phasenende, `config.json`: `human_verify_mode: end-of-phase`).
**Missing dependencies with fallback:** npm 10 (Hilfsinstallation), PDF-URL (Platzhalter).

## Validation Architecture

> `workflow.nyquist_validation` ist `true` [VERIFIED: `.planning/config.json`].

### Test Framework

| Property | Value |
|----------|-------|
| Framework Pipeline | pytest (472 Tests aus Phase 4, `pipeline/tests/`) |
| Framework App | **vitest 5.0.3 (neu, Wave 0)** — bisher kein App-Test-Setup (`app/package.json` ohne `test`) |
| Config | `pipeline/pyproject.toml`; neu `app/vitest.config.ts`, `app/tsconfig.vitest.json` |
| Quick run | `uv run --directory pipeline pytest -q <datei>` bzw. in Scratch-Kopie `npm --prefix "$S/app" run test -- <datei>` |
| Full suite | `uv run --directory pipeline pytest -q` und die in der Aufgabenstellung genannte Scratch-Kopie-Kette (`npm ci && type-check && lint && format:check && test && build`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| START-01 | 7 Kennzahlen = 27,5 / 30,5 / 2,35 / 12,3 / 5,2 / 2.594 / 1.571 (Rundung, Seiten 62/63/25) | unit | `npm --prefix app run test -- kennzahlen` | ❌ Wave 0 |
| START-02/UI-03 | Einstiegssatz nutzt PB ohne KL; Fußzeile liest nur Konfiguration | unit | `… -- start config` | ❌ |
| EINN-01 | Ertragsarten dynamisch (8 Zeilen 2024), Σ Anteile = 100 % | unit | `… -- ertragsarten` | ❌ |
| EINN-02/03 | Steuer-/Zuwendungstabelle inkl. Plug „Sonstige“, Hebesätze aus `meta` | unit | `… -- ertragsarten` | ❌ |
| EINN-04 | Tabelle 2.1.7 in `haushalt.json`, Regel 5 grün mit dokumentierten Befunden | pytest | `uv run --directory pipeline pytest -q tests/test_pruefung.py tests/test_app_daten.py` | ✅ erweitern |
| EINN-05 | Zeitreihe: 8 Jahre, Quelle/Wertart je Jahr, Mapping-Guard (`bezeichnung`), kein `grundzahlen.160101.*` für Jahre ≥ 2024 in Texten (D-02) | unit + pytest | `… -- zeitreihen`; `pytest -q tests/test_texte.py` | ❌ / ✅ erweitern |
| EINN-06 | Pauschalen S. 52 exakt = GFP Z.18 2026; andere Jahre „–“ | pytest + unit | `pytest -q tests/test_pruefung.py` | ✅ erweitern |
| AUSG-01 | Drilldown: Kinder von GESAMT = 15 PB + KL; Summe je Ebene = Elternwert (KL ±181 €) | unit | `… -- drilldown` | ❌ |
| AUSG-02 | KL-Decal in Treemap-Option vorhanden | unit | `… -- treemap` | ❌ |
| AUSG-03 | Zuschussbedarf liest nur `berechnet.*`; Überschussknoten korrekt (2026: PB 11, PB 16) | unit | `… -- drilldown` | ❌ |
| AUSG-04 | 7 Aufwandsarten Σ = 30.455.569 (2026), Transfer-Detail | unit | `… -- aufwandsarten` | ❌ |
| AUSG-05 | Produktdetail: Abschnitte nur mit Daten, unbekannter Code → Fehlerzustand, `Object.prototype`-Schlüssel abgewiesen | unit | `… -- produkt` | ❌ |
| FLUSS-01/02 | Σ links = Σ rechts (≤ 2 €) für alle `haushalt.jahre`; kein Knoten ≤ 0; Defizit/Überschuss/MA nur bei ≠ 0 | unit | `… -- geldfluss` | ❌ |
| FLUSS-03/04 | Klick-Ziel `/ausgaben?jahr&pb`; Mobil-Balken: beide Balken gleiche Summe | unit | `… -- geldfluss` | ❌ |
| UI-01 | `useJahr`: Standard, ungültig, `haushalt.jahre`-Liste, Link-Weitergabe | unit | `… -- jahr` | ❌ |
| UI-05 | Platzhalter-Renderer = `formatiere`; fehlender Wert → „–“; Jahr-gebundene Texte | unit | `… -- texte` | ❌ |
| GLOS-01 | ≥ 22 Begriffe, eindeutige Schlüssel (`^[a-z][a-z0-9_]*$`), Ziffernregel, Quelle bei Zahl | pytest | `pytest -q tests/test_texte.py` | ✅ erweitern |
| GLOS-02 | 63 Produkte, 15 Gruppen, alle mit Beschreibung | unit | `… -- glossar` | ❌ |
| GLOS-03 | Jeder `GlossarBegriff`-Schlüssel (Union) existiert in der Glossar-JSON (Test über Quelltext-Scan) | unit | `… -- glossar` | ❌ |
| UI-Palette (D-08) | 16 Farben × 3 Stufen ≥ 4,5:1 gegen Weiß; jede PB aus Daten hat Farbe, keine überzähligen | unit | `… -- farben` | ❌ |
| WR-06/IN-01 | `formatiere`: nicht endlich → „–“, unbekanntes Kürzel → Fehler; Port-Parität | pytest | `pytest -q tests/test_formatiere.py` | ✅ erweitern |
| Reproduzierbarkeit | `alle.py` erzeugt keinen Diff in `daten`/`app/src/data` | CI | Verify-Befehl 2 aus der Aufgabenstellung | ✅ |
| UI-Verhalten (Fokus, Drawer, Skip-Link, Tooltips, 360 px, Kontrast) | — | **manuell (human-verify, Phasenende)**; automatisiert erst Phase 7 (Playwright/Lighthouse) | — | — |

### Sampling Rate
- **Per task commit:** betroffene pytest-Datei bzw. vitest-Datei (< 30 s)
- **Per wave merge:** vollständige pytest-Suite + vitest + `type-check`/`lint`/`format:check` in Scratch-Kopie
- **Phase gate:** alle drei Verify-Befehle aus der Aufgabenstellung grün (+ `npm run test`) vor `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `app/vitest.config.ts`, `app/tsconfig.vitest.json`, `package.json`-Skript `test`, CI-Schritt, CLAUDE.md-Befehlsliste
- [ ] vitest 5.0.3 installieren (nach `checkpoint:human-verify`, SUS-Hinweis)
- [ ] `__tests__`-Gerüste je Builder-Modul; Test-Hilfsfunktion „Kontrast“
- [ ] ESLint `ignoreParents` erweitern (Pitfall 10)
- [ ] Icons ergänzen (Pitfall 11)
- [ ] Spikes: `RouterLink custom` + `wa-button`; Skip-Link-Abfang; `wa-tooltip for` in Vue

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1` [VERIFIED: `.planning/config.json`]. Statische Seite ohne Auth, Sessions, Backend; relevant sind Eingabevalidierung der URL und Auslieferungshygiene.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | keine Konten |
| V3 Session Management | no | keine Sessions |
| V4 Access Control | no | rein öffentliche Daten |
| V5 Input Validation | **yes** | URL-Query/Param (`jahr`, `modus`, `pb`, `pg`, `:code`, Hash) nur gegen Allowlists aus den Daten (`haushalt.jahre`, `Map` der Knoten-Codes, `Set` der Glossarschlüssel); nie als Objektschlüssel/HTML verwenden |
| V6 Cryptography | no | keine |
| V10/V14 Konfiguration & Abhängigkeiten | yes | vitest nur als devDependency exakt gepinnt; keine Laufzeit-Drittanbieter-Requests (Icons/Fonts selbst gehostet); externe Links `target="_blank" rel="noopener noreferrer"` |
| V5.3 Output Encoding | yes | Texte als Text rendern (kein `v-html`), ECharts-Tooltip-Strings mit `encodeHTML`; `mailto:` nur aus fester Konfiguration |

### Known Threat Patterns for Vue/ECharts-SPA mit Hash-Router

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prototype-Zugriff über URL-Schlüssel (`/produkt/__proto__`, `?pb=constructor`) | Tampering | `Map`/`Object.hasOwn`-Prüfung gegen aus `knoten`/`produkte` gebaute Mengen; unbekannt → Fehlerzustand bzw. Standard + `router.replace` |
| Reflektiertes HTML über Query/Code in Texten oder Tooltips | Tampering/XSS | Interpolation statt `v-html`; `encodeHTML`; Fehlermeldung „Zum Code „{code}“ …“ nur als Text |
| Offener Redirect über Hash/Query | Spoofing | Router-interne Ziele mit Namen/Allowlist; externe URLs ausschließlich aus `config.ts` |
| Unbemerkte Platzhalter-Kontaktadresse im Produktivbetrieb | Repudiation/Info | `config.ts` mit `.invalid`-Domain + Phase-7-Gate (D-17) |
| Lieferkette (neues devDependency) | Tampering | `checkpoint:human-verify`, exakter Pin, Lockfile-Diff prüfen |

## Sources

### Primary (HIGH confidence)
- Repo gelesen: `CONTEXT.md`, `UI-SPEC.md`, `REQUIREMENTS.md`, `STATE.md`, `CLAUDE.md`, `discussion/SPEZIFIKATION.md` (§3, §6.1–6.6, 6.14, 6.15, Anhang B), `app/src/**` (App.vue, main.ts, router, lib, charts, components, data/typen.ts/daten.ts, StartPage), `app/package.json`, `tsconfig*.json`, `eslint.config.ts`, `.prettierignore`, `.github/workflows/ci.yml`, `pipeline/ostbevern/{pruefung,app_daten,texte,manuell,schema,zeilen}.py`, `pipeline/tests/*` (Auszüge), `daten/manuell/README.md`, `daten/manuell/texte/erklaerungen.md`, `daten/pruefberichte/befunde.md`, Phase-4-Review-Disposition
- Daten ausgewertet per Skript: `app/src/data/haushalt.json`, `produkte.json`, `investitionen.json`, `texte.json`
- PDF `raw_data/haushalt-2026.pdf` (pdfplumber + Seitenbild): S. 27, 28, 29, 31, 33, 52, 53
- `@awesome.me/webawesome@3.14.0`: `dist/custom-elements.json`, `dist/chunks/chunk.POQQIIHO.js` (`wa-page`), `chunk.FFR4H3XU.js` (Page-Styles), `dist/styles/color/palettes/default.css` (Palette)
- `vue-router@5.3.1`: `dist/vue-router.js`, `dist/devtools-*.js` (Hash-Location, `scrollToPosition`)
- `echarts@6.1.0`/`zrender`: `lib/chart/treemap/*`, `lib/chart/sankey/*`, `lib/visual/decal.js`, `zrender/lib/tool/color.js`; **eigene SVG-SSR-Läufe** (Decal in Treemap/Sankey/Bar, Sankey-Optionen, ohne `AriaComponent`)
- npm-Registry (`npm view vitest …`), lokale Läufe: `npm ci`, vitest-Install/-Lauf, Type-Check in Scratch-Kopie

### Secondary (MEDIUM confidence)
- `gsd-tools query package-legitimacy check` (vitest: SUS, `too-new`)
- WebSearch „Gemeinde Ostbevern Haushalt 2026 Haushaltsplan pdf“ (Landingpage `ostbevern.de/rathaus/politik/gemeindehaushalt.html`; direkte PDF-URL 2026 nicht gefunden)

### Tertiary (LOW confidence)
- Keine Websuche-only-Aussage steht als Tatsache im Dokument; unbestätigte Punkte stehen im Assumptions Log (A2–A9)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — alles installiert/gelesen; vitest-Befund durch Lauf belegt
- Architecture: HIGH für Datenableitungen (gegen JSON gerechnet), MEDIUM für UI-Details ohne Browser (A2–A4)
- Pitfalls: HIGH — 1, 2, 3, 4, 5, 9, 10, 11, 13, 14 direkt aus Code/PDF/Läufen belegt; 6, 7, 8 aus Code- und Datenlage abgeleitet

**Research date:** 2026-10-04
**Valid until:** 2026-11-03 (30 Tage; ECharts/WA/vitest sind schnell, Paketstände dann erneut prüfen)
