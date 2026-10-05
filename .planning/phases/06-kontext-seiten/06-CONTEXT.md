# Phase 6: Kontext-Seiten - Context

**Gathered:** 2026-10-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Vier neue Seiten ordnen den Haushalt ein: `/entwicklung` (ENTW-01…03), `/investitionen` (INV-01…04), `/rat-entscheidet` (RAT-01…04) und `/stellenplan` (STEL-01…03). Dazu kommt der Hinweis „Was nicht im Haushalt steht“ zu BBO und TEO (UI-04). Die Seiten sind über die Menügruppe „Mehr wissen“ erreichbar (P5 D-13). Nicht Teil dieser Phase: „Quelle anzeigen“ mit WebP-Seiten, Lighthouse-Abnahme, Deployment (alles Phase 7) sowie Spiele (v2).

</domain>

<decisions>
## Implementation Decisions

### Worüber entscheidet der Rat? (RAT-01…04)
- **D-01:** **Bindungsgrad-Balken ohne 160101, nur positiver Zuschussbedarf.** Produkt 160101 „Allgemeine Finanzwirtschaft“ (2026: −20.225.500 € Zuschussbedarf, dort liegen Steuern und Schlüsselzuweisung) ist die Finanzierungsquelle und erscheint nicht im gestapelten Balken. Ein Satz erklärt das. Produkte mit Überschuss (2026: 011202, 011204, 110101) stehen als eigene kleine Liste „bringen mehr ein, als sie kosten“ unter dem Balken. Der Balken summiert nur Produkte mit Zuschussbedarf > 0. Werte kommen ausschließlich aus `ergebnisplan[code].berechnet.zuschussbedarf` bzw. `ueberschuss` und werden nicht neu gerechnet (P5 D-05). Hintergrund: Ohne diese Regel ergäbe „pflichtig“ 2026 −13,9 Mio. €. Welche Produkte ausgeschlossen bzw. als Überschuss gelistet werden, wird aus den Daten abgeleitet (Vorzeichen bzw. ein benannter Ausschluss für 160101 an genau einer Stelle), nicht als Liste von Codes in der Komponente.
- **D-02:** **Die Weitergabe an Kreis und Land (KL) erscheint nur im Block „Was der Rat nicht beeinflussen kann“** (RAT-02), nicht als Segment im Bindungsgrad-Balken. KL ist kein Produkt und hat keinen Bindungsgrad. Der Block nennt Kreisumlage, Gewerbesteuerumlage (aus `KL.*`) und die gesetzlichen Sozialleistungen (`vorbericht.transferaufwendungen.sozialleistungen`) und stellt die Größenordnung dem Balken gegenüber.
- **D-03:** **Die fehlenden Einzelzuschüsse werden aus dem Vorbericht abgeschrieben.** Kulturtragende Vereine (23 T€), VHS (5 T€), Sportförderung (28 T€), Musikschule/JeKits (8 T€) u. a. kommen in eine neue manuelle Tabelle unter `daten/manuell/`. Es gelten die Regeln aus P4/P5: `betrag_teur`, Langformat, Seitenbeleg `quelle`, README-Begründung und Regel 5 gegen eine Planzeile, wo eine passende Zeile existiert. Der Researcher bestimmt Vorberichtsseite und Zuordnung (vermutlich Aufschlüsselung von „Zuschüsse für lfd. Zwecke“, 120 T€). Vorhandene Daten werden wiederverwendet: `kita_zuschuesse` (einzeln), Kinder- und Jugendwerk und OGS aus `transferaufwendungen`. Der Weg führt über Schritt 07 → `haushalt.json` → `vorbericht` → `typen.ts`.
- **D-04:** **Produkte je Bindungsgrad als drei Aufklapper** (`wa-details`), jeweils mit horizontalen Balken der Produkte, absteigend nach Zuschussbedarf, in PB-Farben (P5 D-08). Jedes Produkt verlinkt auf `/produkt/:code` (P5 D-09). Die `DatenTabelle` ist die Alternative.
- **D-05:** Der Hinweis zu RAT-04 („Der Bindungsgrad ist eine Selbstauskunft der Verwaltung; auch in pflichtigen Produkten gibt es Spielraum bei der Höhe“) ist ein Pipeline-Erklärtext mit Seitenverweis.

### Investitionen und Schulden (INV-01…04)
- **D-06:** **Arten-Filter: Bau · Grundstücke · Fahrzeuge/Ausstattung · Sonstige.** „Sonstige“ fasst `finanzanlagen`, `investitionszuschuesse` und `immaterielles` zusammen. So fehlt keine Auszahlung, und die Summe aller Auszahlungen trifft die GFP-Zeile `auszahlungen_investitionen`; ein Test prüft das. Der zweite Filter ist der Aufgabenbereich (PB). Beide Filter sind per Tastatur bedienbar.
- **D-07:** **Liste und Balken zeigen die Summe 2026–2029 je Maßnahme.** Zeilen mit derselben `massnahme_id` werden über die Konten gebündelt und nach der Summe 2026–2029 sortiert. Die Jahreswerte stehen in der Tabelle bzw. im Detail. Der globale `?jahr=`-Umschalter gilt auf dieser Seite nicht. Die Maßnahmen verlinken auf `/produkt/:code`.
- **D-08:** **Einzahlungen je Maßnahme erscheinen nur im Finanzierungsblock**, nicht in Liste und Balken (keine Netto-Rechnung). Der Finanzierungsblock zeigt die Investitionseinzahlungen (GFP-Zeilen, ggf. mit der Aufteilung aus P5 D-03) sowie die Zeitreihe von Kreditaufnahme und Tilgung 2024–2029 aus `investitionen.finanzierung`. Finanzplan und Ergebnisplan stehen nie im selben Diagramm.
- **D-09:** **Der Schuldenstand 2026–2029 wird gezeigt und als berechnet gekennzeichnet.** 2024/2025 sind gedruckt (S. 310). Die Jahre 2026–2029 tragen `BerechnetEtikett` mit der Formel aus `schuldenstand.formel`. Die Kennzahl oben ist der Stand Ende 2025: 7,71 Mio. € gesamt bzw. 656 € je Einwohner. Ein datengetriebener Satz erklärt den Anstieg durch die geplanten Kredite. Dass Liquiditätskredite ab 2027 fehlen (`null`), wird kenntlich gemacht und nicht als 0 dargestellt.
- **D-10:** Die Verpflichtungsermächtigungen (11,6 Mio. €, Summe `ve_faelligkeiten`) werden mit ihren Fälligkeiten je Jahr gezeigt, dazu der vorhandene Text `verpflichtungsermaechtigungen`.

### Entwicklung 2024–2029 (ENTW-01…03)
- **D-11:** **Erträge und Aufwendungen als Linien, das Jahresergebnis als Balken um die Null-Linie** (2024: +191.990 €, 2029: −3.557.700 €). Ist, Ansatz und Planung sind wie in P5 D-01/D-10 unterscheidbar und stehen als Etikett bzw. im Tooltip. Der globale Minderaufwand wird wie auf `/geldfluss` erklärt (Text `globaler_minderaufwand`), und es ist klar, ob das Ergebnis vor oder nach Minderaufwand gezeigt wird.
- **D-12:** **Die Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal und Zinsen laufen einheitlich 2024–2029.** Es gibt keinen Quellmix mit den Grundzahlen 2022–2023; diese bleiben `/einnahmen` vorbehalten. Für dasselbe Jahr gilt dieselbe Quelle wie in P5 D-01 (z. B. Gewerbesteuer aus `vorbericht.steuerarten`).
- **D-13:** **Die fünf Posten stehen als kleine Einzeldiagramme** (Liniendiagramme mit eigener y-Achse) mit Veränderung 2024 → 2029 in %. Auf schmalen Bildschirmen stehen sie untereinander. Jede Reihe hat eine Tabellenalternative.
- **D-14:** **„Wie lange reicht das Polster?“ wird mit Fakten bis 2029 und den HSK-Schwellen beantwortet.** Gestapelte Balken zeigen die Ausgleichsrücklage und die allgemeine Rücklage 2024–2029 aus `haushalt.eigenkapital`. Ein datengetriebener Satz lautet etwa: „Die Ausgleichsrücklage ist 2026 aufgebraucht, danach sinkt die allgemeine Rücklage bis 2029 um X %.“ Die Verringerung der allgemeinen Rücklage je Jahr wird in % gezeigt, mit den Schwellen der Haushaltssicherung als Bezug (§ 76 GO NRW: mehr als 25 % in einem Jahr bzw. mehr als 5 % in zwei aufeinanderfolgenden Jahren). Ein Glossar-Link führt zu „Haushaltssicherung“. **Es gibt keine eigene Prognose über 2029 hinaus.** Der Researcher prüft den genauen Wortlaut und die Bezugsgröße der Schwellen. Die Schwellenwerte stehen mit Quelle in den Daten bzw. der Konfiguration, nicht als Literal in der Komponente. Die Formulierung darf keine rechtliche Bewertung vorwegnehmen („Schwelle“, nicht „muss ein HSK aufstellen“).

### Stellenplan (STEL-01…03)
- **D-15:** **Drei Kennzahlkacheln plus gruppierte Balken nach Teil.** Die Kacheln zeigen Stellen 2026 (62,91), 2025 (62,13) und besetzt am 30.06.2025 (56,63), dazu die Differenzen als berechnet. Die gruppierten Balken je Teil (Beamte, Tarif, Sozial- und Erziehungsdienst) zeigen jeweils die drei Werte. Nachwuchskräfte stehen als Hinweis daneben. Alle Summen werden aus `stellenplan.json` abgeleitet; die Zeilen mit `produktbereich` (Stellenübersicht nach PB) dürfen nicht doppelt gezählt werden.
- **D-16:** **Stellen und Personalaufwand je Aufgabenbereich als zwei Balken je PB nebeneinander:** Stellen 2026 in VZÄ und Personalaufwand aus TP Z. 11 (`personalaufwendungen` je PB, 2026), mit getrennten Achsen und in PB-Farbe (P5 D-08). **Es gibt keinen berechneten Aufwand je Stelle**, weil das einer Gehaltsschätzung nahekäme (Out of Scope). Die Aufteilung nach PB gibt es nur für 2026; die Seite sagt das.
- **D-17:** **Die Verteilung nach Gruppe hat einen Abschnitt je Teil:** Besoldung (A/B), Entgelt (E 1–14) und S-Gruppen, jeweils aufsteigend sortiert. Ein kurzer Glossar-Eintrag erklärt die Gruppen.

### Was nicht im Haushalt steht (UI-04)
- **D-18:** **Eine wiederverwendbare Hinweisbox** mit dem vorhandenen Text `nicht_im_haushalt` (S. 14/33/46/48) steht auf `/ausgaben` (Hallenbad, Verlustübernahme), `/einnahmen` (Abwassergebühren fehlen) und in Kurzform auf `/rat-entscheidet`. Dazu kommt ein Anker im Glossar. Es gibt keine eigene Route.

### Übergreifend
- **D-19:** Neue Routen `/entwicklung`, `/investitionen`, `/rat-entscheidet` und `/stellenplan` stehen im Dropdown „Mehr wissen“. Dafür wird `MenueEintrag` zu einer Vereinigung erweitert, wie in `app/src/lib/menue.ts` vorgesehen. `MENUE` bleibt die einzige Quelle für die horizontale Liste und den Drawer. Seitentitel stehen in `meta.titel`, und die Fokussteuerung beim Routenwechsel bleibt erhalten.
- **D-20:** Neue Erklärtexte (u. a. RAT-04, Überschuss-Liste, Polster-Satz, Schuldenanstieg, Glossar „Haushaltssicherung“ und Gruppen) sind Pipeline-Texte mit Platzhaltern `{{schluessel|kuerzel}}` und Seitenverweis. Der Executor entwirft sie, ein **Checkpoint** legt sie dir zur fachlichen Abnahme vor (wie P4 D-17 / P5 D-15). Berechnete Werte in Sätzen (Prozente, Differenzen) stammen aus den Daten, nicht von Hand.

### Claude's Discretion
- Komponentenschnitt und Namen (z. B. `BindungsgradBalken`, `MassnahmenListe`, `RuecklagenBalken`, `HinweisNichtImHaushalt`) sowie Composables
- Genaue Diagrammformen innerhalb der Entscheidungen (Farben aus `echartsTheme.ts`, Decals, Achsen), Reihenfolge der Abschnitte je Seite
- Reihenfolge der Einträge im Dropdown „Mehr wissen“
- Ob die Markierung „Ortsteil Brock“ (Spez. 6.10, optional) als einfacher Textfilter mitkommt
- Ob neue Daten (Bündelung je Maßnahme, Summen je Bindungsgrad) in der Pipeline (Schritt 07) oder in `app/src/lib/` entstehen, solange die Werte aus `berechnet` gelesen und Summen gegen die Planzeilen getestet werden

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §3.1 (Ergebnis- vs. Finanzplan), §3.3 (Minderaufwand), §3.4 (Kreisumlage), §3.7 (Außerhalb des Kernhaushalts: BBO/TEO)
- `discussion/SPEZIFIKATION.md` §6.10–6.13 — Seiteninhalte Investitionen, Rat, Entwicklung, Stellenplan; §6.15 gemeinsame UI-Elemente
- `discussion/SPEZIFIKATION.md` Anhang B.6 — Eckwerte (Rücklagenverringerung, Schulden 7,7 Mio. € / 656 €, Beamte 8)

### Projekt & Anforderungen
- `.planning/PROJECT.md` — Core Value, Constraints, Out of Scope (keine Gehaltsschätzung, BBO/TEO nur als Hinweis)
- `.planning/REQUIREMENTS.md` — ENTW-01…03, INV-01…04, RAT-01…04, STEL-01…03, UI-04
- `.planning/ROADMAP.md` Phase 6 — Erfolgskriterien 1–5

### Vorentscheidungen
- `.planning/phases/05-leitfragen-seiten/05-CONTEXT.md` — D-01 (Steuerquellen je Jahr, Ist/Ansatz/Planung), D-03 (manuelle Tabellen), D-05 (Zuschussbedarf aus `berechnet`), D-08 (PB-Farben), D-09 (`/produkt/:code`), D-10 (`?jahr=`), D-13 (Menü „Mehr wissen“), D-14/D-15 (Texte und Abnahme-Checkpoint)
- `.planning/phases/05-leitfragen-seiten/05-UI-SPEC.md` — Design-Vertrag der Leitfragen-Seiten (Fortschreibung für Phase 6)
- `.planning/phases/05-leitfragen-seiten/05-UI-REVIEW.md` — offene Token-Hygiene, nicht wiederholen
- `.planning/phases/04-manuelle-daten-und-app-daten/04-CONTEXT.md` — D-05…D-09 (manuelle Tabellen, Regel 5), D-15…D-17 (Platzhalter-Texte), D-21…D-23 (App-JSON-Schnitt)
- `daten/manuell/README.md` — Konventionen der Handdaten (Erweiterung für D-03)
- `daten/manuell/texte/erklaerungen.md` — vorhandene Erklärtexte (`nicht_im_haushalt`, `schulden`, `verpflichtungsermaechtigungen`, `defizit_ruecklagen`)

### Extern (vom Researcher zu prüfen)
- § 76 GO NRW (Haushaltssicherungskonzept) — Schwellen für D-14

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `KennzahlKachel`, `BerechnetEtikett`, `WertartEtikett`, `ErklaerText`, `GlossarBegriff`, `EuroBetrag`: Grundbausteine jeder neuen Seite
- `SteuerZeitreihe.vue` + `lib/zeitreihen.ts`: Muster für Zeitreihen mit Ist/Ansatz/Planung (D-11…D-13)
- `ZuschussBalken.vue`, `charts/balken.ts`: horizontale Balken mit PB-Farben (D-04, D-07, D-16)
- `KreisumlageCallout.vue`, `lib/kreisumlage.ts`: KL-Werte für den Block „nicht beeinflussbar“ (D-02)
- `lib/berechnung.ts`, `lib/produkt.ts`, `lib/ansicht.ts` (`findeProdukt`): Produkt- und Zuschussbedarfszugriff
- `lib/menue.ts`: Menüliste, für „Mehr wissen“ vorbereitet (D-19)
- `lib/bildschirm.ts`: Umschaltung für schmale Bildschirme

### Established Patterns
- `haushalt.json`: Werte als Arrays entlang `jahre` mit `wertarten`; `ergebnisplan[code].berechnet.{aufwand,ertraege,zuschussbedarf,ueberschuss}`; `eigenkapital.posten` (Ausgleichsrücklage, allgemeine Rücklage, Jahresergebnis); `vorbericht.{transferaufwendungen,kita_zuschuesse,personal,…}`
- `investitionen.json`: `massnahmen` (137 Zeilen, 83 IDs, `art`, `richtung`, `werte`, `pb`, `pdf_seite`), `ve_faelligkeiten` (Summe 11,6 Mio. €), `finanzierung.zeilen`, `schuldenstand` (mit `berechnet[]` und `formel`), `buergschaften`
- `stellenplan.json`: Zeilen mit `teil` (beamte/tarif/sozial_erziehungsdienst/nachwuchs), `merkmal` (stellen/besetzt/…), `jahr`, `gruppe`, `produktbereich` (nur Stellen 2026; Summe je PB = Summe je Gruppe = 62,91)
- `produkte.json`: `bindungsgrad` (31 pflichtig, 15 teils, 17 freiwillig)
- Zahlen in Texten nur über Platzhalter; Quelltext-Scan verbietet handgetippte Zahlen; kein `v-html`; CSS-Präfix `om-`, nur `--wa-*`-Tokens (`stiltokens.test.ts`)
- App-Checks laufen im Linux-Sandbox in einer Scratch-Kopie (macOS-Binaries in `app/node_modules`)

### Integration Points
- `app/src/router/index.ts`: vier neue benannte Routen mit `meta.titel`
- `app/src/lib/menue.ts` + `App.vue`: Dropdown „Mehr wissen“ (Desktop) und Drawer (mobil)
- `AusgabenPage.vue`, `EinnahmenPage.vue`: Einbau der Hinweisbox (D-18)
- Pipeline Schritt 07 + `daten/manuell/`: neue Zuschusstabelle (D-03), neue Texte (D-20); CI-Diff auf `daten/` und `app/src/data/`

</code_context>

<specifics>
## Specific Ideas

- Grundsatz aus Phase 5 gilt weiter: Text und Diagramm zeigen für dasselbe Jahr denselben Wert aus derselben Quelle.
- Ehrlich, aber lesbar: Überschüsse nicht verstecken, sondern getrennt erklären (D-01).
- Keine eigenen Prognosen über das PDF hinaus. Hochgerechnete Werte (Schuldenstand) sind sichtbar als berechnet gekennzeichnet.
- Keine gehaltsähnlichen Kennzahlen im Stellenplan.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-kontext-seiten*
*Context gathered: 2026-10-05*
