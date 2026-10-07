# Phase 5: Leitfragen-Seiten - Context

**Gathered:** 2026-10-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Die App beantwortet „Wo kommt das Geld her?“ und „Wofür wird es ausgegeben?“ laienverständlich auf fünf Seiten: Start (`/`), `/einnahmen`, `/ausgaben` (inkl. Produktdetail), `/geldfluss`, `/glossar` — plus Fußzeile, Kopfmenü und globaler Jahr-Umschalter. Jede Zahl stammt aus `app/src/data/*.json`. Ein kleiner Pipeline-Anteil ergänzt fehlende Vorberichtstabellen (Pauschalen, 2.1.7) und die Glossartexte.

Nicht in dieser Phase: Kontextseiten (Entwicklung, Investitionen/Schulden, Rat, Stellenplan — Phase 6), „Quelle anzeigen“-Seitenleiste/WebP-Belege und Lighthouse-Endabnahme (Phase 7), Spiele (v2; die Spiel-Teaser aus Spez. 6.3 entfallen auf der Startseite).

</domain>

<decisions>
## Implementation Decisions

### Datenlücken Einnahmen (EINN-02…06)
- **D-01:** Die **Zeitreihe je Steuerart 2022–2029** (EINN-05) nimmt **2022–2023 aus den Grundzahlen 160101** (Ist) und **2024–2029 aus `vorbericht.steuerarten`**. Grund: Die Grundzahlen 2024/2025 weichen vom Vorbericht ab (Gewerbesteuer 2024: GZ 8.418.043 € vs. Vorbericht vorl. RE 9.511.000 €). Die Vorberichtssumme trifft GEP Z. 01 2024 (19.614.808 €) bis auf Rundung. Bewusste Abweichung von Spez. 6.4 („Ist 2022–2024 aus den Grundzahlen“). Die Grundzahlen 2024/2025 werden für Steuerreihen nicht verwendet. Ist (2022–2024), Ansatz und Planung sind visuell unterscheidbar (z. B. durchgezogen/gestrichelt), die Wertart steht im Tooltip und in der Tabelle. Analog für die Schlüsselzuweisung (GZ Pos. 9 für 2022–2023, ab 2024 `vorbericht.zuwendungen`).
- **D-02:** Der Erklärtext `gewerbesteuer` in `daten/manuell/texte/erklaerungen.md` zitiert heute `{{grundzahlen.160101.1.2024|mio}}` (8,42 Mio. €). Phase 5 stellt diesen Platzhalter auf `vorbericht.steuerarten.gewerbesteuer.2024` um. Ein Test stellt sicher, dass Erklärtexte und die Steuer-Zeitreihe für dasselbe Jahr dieselbe Quelle nutzen (mindestens: kein `grundzahlen.160101.*`-Platzhalter für Jahre ≥ 2024). Der Nutzer nimmt den geänderten Satz im Glossar-Checkpoint (D-15) mit ab.
- **D-03:** Die **Aufteilung der investiven Einnahmen** (Investitionspauschale, Schulpauschale, Sportpauschale usw., Spez. 6.4) wird aus dem Vorbericht **manuell nach `daten/manuell/` abgeschrieben**. Es gelten die Regeln aus Phase 4: D-05 `betrag_teur`, D-06 Langformat, D-09 einmal abgeschrieben, README-Begründung, `quelle`-Seite. Regel 5 prüft sie gegen die passende GFP-Zeile (voraussichtlich `investitionszuwendungen`, Z. 18; der Researcher bestimmt die Vorberichtsseite und die genaue Zuordnung). Ein nicht aufgeschlüsselter Rest erscheint als berechnetes „Sonstige“. Grundstücksverkäufe, Beiträge und Kredite kommen direkt aus den GFP-Zeilen `veraeusserung_sachanlagen`, `beitraege` und `kreditaufnahme`. Die investiven Einnahmen stehen auf `/einnahmen` getrennt und klar abgegrenzt („fließen nicht in den laufenden Haushalt“, Finanzplan nie mit Ergebnisplan im selben Diagramm).
- **D-04:** **Vorbericht 2.1.7** (Sonstige ordentliche Erträge inkl. Konzessionsabgaben) wird ebenso manuell abgeschrieben, als neue Tabelle in `weitere_vorberichtstabellen.csv` oder als eigene Datei. Regel 5 prüft sie zweistufig (P4 D-07) gegen GEP Z. 07 `sonstige_ordentliche_ertraege`. Damit hat EINN-04 für 2026 echte Werte. Das war in Phase 4 ausdrücklich vertagt. Die neuen Tabellen laufen über Schritt 07 in `haushalt.json` → `vorbericht` und über `typen.ts`, ohne Typumwandlung.

### Ausgaben: Treemap & Zuschussbedarf (AUSG-01…04)
- **D-05:** Im Modus **„Aufwand“** gibt es eine Treemap (PB → PG → P, KL als Top-Kachel). Im Modus **„Zuschussbedarf“** gibt es **statt der Treemap horizontale Balken** je Drilldown-Ebene, mit negativen Balken für Überschüsse (`berechnet.ueberschuss`). Überschüsse bekommen eine eigene Erklärung (AUSG-03), z. B. „Allgemeine Finanzwirtschaft: hier liegen die Steuern und die Schlüsselzuweisung“ oder Gebührenhaushalte. Die Werte werden nur aus `ergebnisplan[code].berechnet` gelesen und nicht neu gerechnet.
- **D-06:** **Eigene Brotkrumen-Navigation** gilt gemeinsam für Treemap und Balken („Alle Bereiche › PB › PG“). Beim Wechsel Aufwand ↔ Zuschussbedarf bleibt die Ebene erhalten. Die Tabellenalternative (`DatenTabelle`) zeigt immer die aktuelle Ebene. Der Drilldown ist per Tastatur bedienbar. Ein Klick auf ein Produkt öffnet `/produkt/:code` (D-09). Die native ECharts-Treemap-Navigation (`breadcrumb`, `roam`) wird nicht verwendet.
- **D-07:** **KL-Callout** („Weitergabe an Kreis und Land“): 1–2 kurze Sätze („Diesen Betrag reicht Ostbevern weiter und kann ihn nicht selbst steuern“), dazu die drei Unterposten als „rd.“ (P4 D-02) und ein Aufklapper mit dem Erklärtext `kreisumlage` aus `texte.json` (netto/brutto, Hebesätze). Der globale Minderaufwand erscheint als erklärter Hinweis unter dem Diagramm (Text `globaler_minderaufwand`), nicht als Kachel.
- **D-08:** **Farben:** Jede PB hat eine feste Farbe aus `echartsTheme.ts`, die Kinder erben sie in Abstufungen. KL bekommt einen eigenen, abgesetzten Akzent mit Muster bzw. Decal, damit die Kachel auch ohne Farbe erkennbar ist. Dieselbe PB→Farbe-Zuordnung gilt in Treemap, Balken, Sankey und mobilen Balken. Die Zuordnung steht zentral in `echartsTheme.ts`, und die Kontraste genügen dem a11y-Ziel.

### Navigation, Jahr & Produktdetail (AUSG-05, FLUSS-01…04, UI-01)
- **D-09:** Das **Produktdetail ist eine eigene Route `/produkt/:code`**. Es ist verlinkbar aus Treemap, Balken, Glossar-Akkordeon und später aus Phase 6. Inhalt nach AUSG-05: Beschreibung, Leistungen, Bindungsgrad, Gremium, Teilergebnisplan 2024–2029 als Mini-Tabelle, Erläuterungen, Grundzahlen (berechnete Pro-Kopf-Werte gekennzeichnet), Investitionen des Produkts und Quellenlink (PDF-Seite). „Zurück“ führt zur Ausgabenseite auf der Ebene des Produkts (PB/PG im Query). Unbekannter Code → freundliche Fehlermeldung oder Redirect. — **Reversibility:** costly — Phase 6 und das Glossar verlinken auf dieses URL-Schema.
- **D-10:** Der **Jahr-Umschalter ist global und steht in der URL** (`?jahr=2027`, Hash-Router-Query). Er gilt auf `/einnahmen`, `/ausgaben` und `/geldfluss`. Ohne Parameter gilt das Haushaltsjahr aus den Daten (2026), ungültige Werte fallen darauf zurück. Links zwischen den Seiten (z. B. Sankey → Ausgaben) behalten das Jahr. Jeder angezeigte Wert trägt die Wertart aus `haushalt.wertarten` als Etikett (Ist/Ansatz/Planung). Die Jahresliste kommt aus `haushalt.jahre`, ist also nicht fest im Code. — **Reversibility:** costly — Das URL-Schema `?jahr=` wird von Links und Phase-6-Seiten mitbenutzt.
- **D-11:** **Sankey-Ausgleich je Jahr:** Bei einem Defizit steht links der Knoten „Defizit (Entnahme aus Rücklagen)“, bei einem Überschuss (z. B. 2024 Ist +191.990 €) rechts „Überschuss (Zuführung zur Rücklage)“. Der Minderaufwand erscheint nur bei einem Wert ≠ 0 als Gegenposten. Alles wird aus GEP `jahresergebnis`, `globaler_minderaufwand` und `ergebnis_nach_minderaufwand` abgeleitet, ohne Sonderfall für einzelne Jahre. Ein Test prüft für alle 6 Jahre, dass linke und rechte Summe gleich sind. Der Erklärtext (`defizit_ruecklagen`) muss zum Jahr passen; er wird nur bei Defizit gezeigt bzw. bekommt eine Überschuss-Variante. Hover hebt Pfade hervor, ein Klick auf einen Aufgabenbereich führt zu `/ausgaben?jahr=…` mit gewählter PB (FLUSS-03).
- **D-12:** **Mobile Alternative zum Sankey** (< Breakpoint aus `lib/bildschirm.ts`): zwei gleich lange gestapelte Balken, „Woher“ (Ertragsarten + ggf. Defizit) und „Wohin“ (KL, Aufgabenbereiche, Zinsen + ggf. Minderaufwand/Überschuss), in denselben Farben (D-08). Darunter steht die Tabelle.
- **D-19:** **Minderaufwand im Sankey links (ändert D-11/D-12, Entscheidung 2026-10-04 nach Research):** Der globale Minderaufwand ist ein **Quellknoten links** („Globaler Minderaufwand“) neben „Defizit (Entnahme aus Rücklagen)“, nicht ein Gegenposten rechts. Nur so bilanziert der Sankey, weil `ergebnis_nach_minderaufwand` = `jahresergebnis` − `globaler_minderaufwand` gilt. Für 2026 ergibt die rechte Platzierung 29.855.569 € gegenüber 31.055.569 €. Der Ausgleichstest prüft alle 6 Jahre mit ±2 € Toleranz, weil die PDF-Rundung ΣPB gegenüber dem GEP in 2024 und 2028 um ±1 € verschiebt. Der mobile Balken „Woher“ (D-12) enthält entsprechend Defizit und Minderaufwand, der Balken „Wohin“ ggf. den Überschuss. Die UI-SPEC wird beim Ausführen angepasst.
- **D-20:** **Einstiegskachel „größter Aufgabenbereich“** auf der Startseite: Das ist die größte PB **ohne** KL (2026: PB 01). Der Wert wird aus den Daten abgeleitet und nicht von Hand eingetragen.
- **D-13:** **Kopfmenü:** Start · Woher? · Wofür? · Geldfluss · Glossar. Phase 6 ergänzt eine Gruppe „Mehr wissen“ als Dropdown. Auf schmalen Bildschirmen öffnet sich das Menü als `wa-drawer`. Die Fokussteuerung beim Routenwechsel bleibt erhalten bzw. kommt dazu.

### Glossar & Fußzeile (GLOS-01…03, UI-03, UI-05)
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §3 (Fallstricke: 3.1 Ergebnis- vs. Finanzplan, 3.3 Minderaufwand, 3.4 Kreisumlage, 3.5 Einnahmen in PB 16, 3.6 Sonderposten, 3.8 Datenauffälligkeiten)
- `discussion/SPEZIFIKATION.md` §6.1–6.6, 6.14, 6.15 — Seiteninhalte Start, Einnahmen, Ausgaben, Geldfluss, Glossar, gemeinsame UI-Elemente
- `discussion/SPEZIFIKATION.md` Anhang B — Sollwerte (Kennzahlenband, Steuerarten, Transferaufwendungen)

### Projekt & Anforderungen
- `.planning/PROJECT.md` — Core Value, Constraints, Key Decisions
- `.planning/REQUIREMENTS.md` — START-01/02, EINN-01…06, AUSG-01…05, FLUSS-01…04, GLOS-01…03, UI-01, UI-03, UI-05
- `.planning/ROADMAP.md` Phase 5 — Erfolgskriterien 1–5

### Vorentscheidungen
- `.planning/phases/04-manuelle-daten-und-app-daten/04-CONTEXT.md` — D-01…D-04 (KL-Knoten, Zuschussbedarf), D-05…D-09 (manuelle Tabellen, Regel 5), D-15…D-17 (Platzhalter-Texte, Abnahme-Checkpoint), D-21…D-23 (App-JSON-Schnitt, Formeln)
- `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` — offene Punkte WR-06/IN-01 (`formatiere()`-Fallback) betreffen Phase 5
- `.planning/phases/01-setup/01-CONTEXT.md` — D-02/D-03 (Münster-Komponenten selbst geschrieben, neue Komponenten in Phase 5), D-04 (Palette, Kontraste)
- `.planning/phases/01-setup/01-UI-SPEC.md` — bestehender Design-Vertrag
- `daten/manuell/README.md` — Konventionen der Handdaten (Erweiterung für D-03/D-04)
- `daten/manuell/texte/erklaerungen.md` — vorhandene Erklärtexte (Änderung D-02)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/src/components/PageIntro.vue`, `ChartCard.vue` (mit `beispieldaten`-Flag), `BaseChart.vue`, `DatenTabelle.vue` (+ `datenTabelle.ts`, `chartKontext.ts`): Basis jeder Seite, Tabellenalternative je Diagramm
- `app/src/charts/format.ts`: einzige Formatierung (`euro`, `euroKurz`, `formatiere()` für Platzhaltertexte)
- `app/src/charts/echartsTheme.ts`: registrierte ECharts-Module. Treemap- und Sankey-Module müssen dort ergänzt werden; die PB-Farbzuordnung kommt hierher (D-08)
- `app/src/lib/bildschirm.ts`: `useSchmalerBildschirm()` für Mobil-Umschaltung (D-12)
- `app/src/data/daten.ts` + `typen.ts`: typisierter Zugriff auf `haushalt`, `produkte`, `investitionen`, `texte` ohne Typumwandlung
- `app/src/lib/webawesome.ts` / `main.ts`: Web-Awesome-Komponenten werden einzeln importiert (neu z. B. `wa-details`, `wa-tooltip`, `wa-drawer`, `wa-radio-group`)

### Established Patterns
- Hash-Router (`app/src/router/index.ts`) mit benannten Routen, heute nur `start` + Catch-all
- `haushalt.json`: Werte als Arrays entlang `jahre`/`wertarten`, Knoten über `eltern`, berechnete Werte unter `berechnet`, KL + `KL.<posten>` synthetisch mit `gerundet`
- Produkt-Grundzahlen enthalten Steuer-Ist 2022–2025 (160101 Pos. 1–9) und Konzessionsabgaben (Pos. 10–12, nur bis 2025)
- Pipeline: dünne typer-Skripte, Logik in `pipeline/ostbevern/`, Regel 5 für manuelle Tabellen, CI-Diff auf `daten` + `app/src/data`
- CSS-Präfix `om-`, nur `--wa-*`-Tokens, Du-Anrede, keine Drittanbieter-Requests

### Integration Points
- `App.vue`: Kopfmenü (D-13) und Fußzeile (D-17/D-18) ersetzen den heutigen Rahmen
- `StartPage.vue`: Demo-Inhalt (Beispieldaten) wird durch das echte Kennzahlenband ersetzt
- Neue Routen: `/einnahmen`, `/ausgaben`, `/geldfluss`, `/glossar`, `/produkt/:code`
- Pipeline Schritt 07 (`07_app_daten.py`) + Texte: neue manuelle Tabellen (D-03/D-04) und Glossar (D-14)

</code_context>

<specifics>
## Specific Ideas

- Grundsatz aus der Diskussion: Wenn zwei gedruckte Quellen sich widersprechen, gewinnt die Quelle, die zum Gesamtplan passt. Text und Diagramm dürfen nie verschiedene Werte für dasselbe Jahr zeigen.
- Lieber eine Tabelle sauber nachtragen und prüfen, als eine Ebene ohne Aufschlüsselung zu lassen (Pauschalen, 2.1.7).
- Den Zuschussbedarf ehrlich mit negativen Balken zeigen, statt Überschüsse in einer Treemap zu verstecken.
- PB-Farben sollen seitenübergreifend wiedererkennbar sein.

</specifics>

<deferred>
## Deferred Ideas

- Spiel-Teaser auf der Startseite (Spez. 6.3) — mit den Spielen in v2
- Kontakt-E-Mail festlegen — vor Phase 7 (Deployment-Gate, D-17)
- Repo-URL bzw. GitHub-Issues als zusätzlicher Kontaktweg — ggf. Phase 7, sobald ein Remote existiert

</deferred>

---

*Phase: 05-leitfragen-seiten*
*Context gathered: 2026-10-04*
