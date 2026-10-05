---
phase: 05-leitfragen-seiten
verified: 2026-10-05T20:10:00Z
status: human_needed
score: 5/5 roadmap success criteria verified in code and data; 6/6 must-haves of gap-closure plan 05-16 verified in code (browser behavior pending)
covered_files:
  - .planning/phases/05-leitfragen-seiten/05-01-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-01-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-02-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-02-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-03-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-03-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-04-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-04-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-05-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-05-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-06-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-06-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-07-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-07-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-08-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-08-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-09-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-09-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-10-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-10-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-11-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-11-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-12-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-12-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-13-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-13-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-14-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-14-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-15-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-15-SUMMARY.md
  - .planning/phases/05-leitfragen-seiten/05-16-PLAN.md
  - .planning/phases/05-leitfragen-seiten/05-16-SUMMARY.md
  - app/src/App.vue
  - app/src/components/AufwandTreemap.vue
  - app/src/components/AufwandsartBalken.vue
  - app/src/components/BaseChart.vue
  - app/src/components/BerechnetEtikett.vue
  - app/src/components/Brotkrumen.vue
  - app/src/components/ChartCard.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/EbenenTabelle.vue
  - app/src/components/EinstiegsKachel.vue
  - app/src/components/ErklaerText.vue
  - app/src/components/ErtragsBalken.vue
  - app/src/components/GeldflussBalken.vue
  - app/src/components/GlossarBegriff.vue
  - app/src/components/GlossarListe.vue
  - app/src/components/JahrUmschalter.vue
  - app/src/components/KennzahlKachel.vue
  - app/src/components/KreisumlageCallout.vue
  - app/src/components/PageIntro.vue
  - app/src/components/ProduktAkkordeon.vue
  - app/src/components/SankeyDiagramm.vue
  - app/src/components/SteuerZeitreihe.vue
  - app/src/components/WertartEtikett.vue
  - app/src/components/ZuschussBalken.vue
  - app/src/config.ts
  - app/src/data/haushalt.json
  - app/src/data/produkte.json
  - app/src/data/texte.json
  - app/src/lib/__tests__/sprungziel.test.ts
  - app/src/lib/__tests__/stiltokens.test.ts
  - app/src/lib/ansage.ts
  - app/src/lib/ansicht.ts
  - app/src/lib/aufwandsarten.ts
  - app/src/lib/berechnung.ts
  - app/src/lib/bewegung.ts
  - app/src/lib/bildschirm.ts
  - app/src/lib/drilldown.ts
  - app/src/lib/einnahmen.ts
  - app/src/lib/ertragsarten.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/glossar.ts
  - app/src/lib/jahr.ts
  - app/src/lib/kennzahlen.ts
  - app/src/lib/kreisumlage.ts
  - app/src/lib/menue.ts
  - app/src/lib/produkt.ts
  - app/src/lib/sprungziel.ts
  - app/src/lib/texte.ts
  - app/src/lib/webawesome.ts
  - app/src/lib/zeilen.ts
  - app/src/lib/zeitreihen.ts
  - app/src/pages/AusgabenPage.vue
  - app/src/pages/EinnahmenPage.vue
  - app/src/pages/GeldflussPage.vue
  - app/src/pages/GlossarPage.vue
  - app/src/pages/ProduktPage.vue
  - app/src/pages/StartPage.vue
  - app/src/router/index.ts
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/texte.py
covered_digest: "v2:sha256:fd1d7a1c6d3757ecfd0aff58fb5dc9923bcb81f2b451847da44c8b8edaa0154a"
behavior_unverified: 5
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/5 roadmap success criteria verified in code and data (browser behavior pending)
  gaps_closed:
    - "G-05-6 (UAT, major): GlossarBegriff-Sprung landete unter der festen Kopfzeile (Router-Offset fehlte, --wa-space-md undefiniert) - Code- und Testbeleg, Browserbeleg offen"
    - "G-05-4 (UAT, cosmetic): Unterstrich von „Bindungsgrad“ berührte das wa-tag (kein Abstand dt/dd) - CSS-Beleg, Browserbeleg offen"
  gaps_remaining: []
  regressions: []
behavior_unverified_items:
  - truth: "Nach jedem Seitenwechsel springt der Fokus auf die h1, der Titel wird gesetzt und die Ansage erfolgt (D-13, router/index.ts afterEach)"
    test: "Im Browser zwischen Start, Einnahmen, Ausgaben, Geldfluss und Glossar wechseln (Menü und Tastatur), danach document.title, document.activeElement und die Live-Region prüfen; zusätzlich /#/glossar#hebesatz direkt aufrufen"
    expected: "Fokus liegt auf der h1 der neuen Seite (bei Fragment auf dem Zielelement), Titel lautet „{Seite} – Ostbevern Money“, die Live-Region meldet „Seite … geladen“; ein reiner Query-Wechsel (Jahr, Modus) lässt den Fokus am Steuerelement"
    why_human: "Es gibt keinen Test für router.afterEach oder die Komponenten; Präsenz und Verdrahtung sind belegt, Fokus und Ansage sind Laufzeitverhalten"
  - truth: "Klick auf einen Aufgabenbereich im Sankey öffnet /ausgaben?pb=… mit gleichem Jahr (FLUSS-03); Hover hebt Pfade hervor (emphasis focus adjacency)"
    test: "Auf /#/geldfluss bei 1280 px einen Aufgabenbereichsknoten anklicken und mit der Maus über Knoten und Flüsse fahren; mit gewähltem Jahr 2025 wiederholen"
    expected: "Navigation zu Ausgaben mit pb und jahr in der URL; Ertragsknoten navigieren nicht; Hover dimmt nicht benachbarte Pfade"
    why_human: "zielCodeAusKlick ist getestet, der echte Canvas-Klick und der Router-Aufruf in SankeyDiagramm.vue laufen nur im Browser"
  - truth: "Ausgaben-Drilldown (Treemap-Klick, Brotkrumen, Zurück-Taste) und Umschalter Aufwand/Zuschussbedarf ändern den URL-Zustand und die Ebene"
    test: "Auf /#/ausgaben Kachel anklicken (Aufgabenbereich, Produktgruppe, Produkt), Brotkrumen und Browser-Zurück nutzen, Umschalter betätigen, ungültige URL-Werte (?pb=xyz) eintragen"
    expected: "Ebene wechselt, Brotkrumen und Fokus folgen, Zurück führt eine Ebene hoch, ungültige Werte werden auf die oberste Ebene bereinigt"
    why_human: "Die Zustandslogik (ansicht, drilldown) ist per Unit-Test belegt; das Zusammenspiel von wa-radio-group-Ereignis, ECharts-Klick, Router und Fokus ist nicht getestet"
  - truth: "Auf schmalen Bildschirmen (< 700 px) erscheint statt des Sankeys der gestapelte Balken (FLUSS-04); Kopfmenü wird zum Drawer"
    test: "Fenster auf 360 px verkleinern und /#/geldfluss sowie das Menü öffnen; über 700 px zurück"
    expected: "GeldflussBalken statt SankeyDiagramm, kein horizontales Scrollen, Drawer öffnet, schließt bei Navigation und gibt den Fokus an die Menütaste zurück"
    why_human: "useSchmalerBildschirm und die Drawer-Ereignisse hängen an matchMedia und Web-Awesome-Elementen, die vitest ohne DOM nicht ausführt"
  - truth: "Nach einem Klick auf einen GlossarBegriff oder eine Sprungmarke landet der Zielbegriff unter der festen wa-page-Kopfzeile und ist vollständig sichtbar (G-05-6, GLOS-03, D-16)"
    test: "Auf /#/produkt/030101 den Link „Bindungsgrad“ anklicken; auf /#/glossar die erste, eine mittlere und die letzte Sprungmarke anklicken; je bei 1280 px und 360 px (Drawer-Kopfzeile), einmal mit prefers-reduced-motion"
    expected: "Der Begriff samt 2-px-Fokusring liegt vollständig unter der Kopfzeile sichtbar; der Sprung ist ein Sofortsprung"
    why_human: "sprungPosition ist per Unit-Test auf { el, top } geprüft und vue-router zieht top ab (Quelltext gelesen), aber der berechnete scroll-margin-top (calc mit var(--scroll-margin-top), vererbt von wa-page) und die tatsächliche Landeposition entstehen nur im Browser"
human_verification:
  - test: "Glossar-Sprung unter der Kopfzeile (Plan 05-16, G-05-6): /#/produkt/030101 „Bindungsgrad“ anklicken; auf /#/glossar drei Sprungmarken (erste, mittlere, letzte) anklicken; bei 1280 px und bei 360 px (Drawer-Kopfzeile); einmal mit prefers-reduced-motion"
    expected: "Der Begriff und sein Fokusring liegen vollständig sichtbar direkt unter der festen Kopfzeile; der Sprung bleibt ein Sofortsprung"
    why_human: "Landeposition hängt am berechneten scroll-margin-top und an der Kopfzeilenhöhe von wa-page, nur im Browser sichtbar"
  - test: "Einnahmen-Balken-Scroll (Plan 05-16): auf /#/einnahmen den Balken „Steuern“ anklicken, bei 1280 px und 360 px"
    expected: "Die Zeile der geöffneten Aufschlüsselung liegt vollständig unter der festen Kopfzeile; mit prefers-reduced-motion ohne Animation"
    why_human: "scrollIntoView mit scroll-margin-top, Sichtbarkeit unter der Kopfzeile ist ein Layouturteil"
  - test: "Produktseite Etikett–Wert-Abstand (Plan 05-16, G-05-4): /#/produkt/030101 und /#/produkt/160101 bei 360 px und 1280 px"
    expected: "Der gepunktete Unterstrich von „Bindungsgrad“ berührt das wa-tag darunter nicht (4 px Abstand); Gremium und Fachbereich zeigen denselben Abstand"
    why_human: "Überlappung von Unterstreichung und Tag-Rand ist ein Rendering-Urteil; automatisch ist nur die CSS-Deklaration belegt"
  - test: "Kennzahlenband, Einstiege, Kreisumlage-Hinweis und Fußzeile auf der Startseite bei 360 px und 1280 px ansehen (Plan 05-08)"
    expected: "Sieben Kacheln ohne horizontales Scrollen und ohne umbrechende Zahlen; „-2,35 Mio. €“ steht neben „Defizit“; „berechnet“-Etikett zeigt Tooltip bei Fokus; beide Einstiege und der Kreisumlage-Link navigieren"
    why_human: "Layout, Umbruch und Tooltip-Fokus sind ohne Browser nicht prüfbar (Sandbox hat keinen Browser)"
  - test: "Einnahmen-Seite im Browser durchgehen (Plan 05-09): Aufklapper, Klick auf Ertragsbalken, Zeitreihe je Steuerart, Jahr-Umschalter 2024 bis 2029, investive Einnahmen"
    expected: "Ist und Plan in der Zeitreihe unterscheidbar (Linienart/Legende), Balkenklick öffnet und scrollt zur Aufschlüsselung, Tabellenalternativen erreichbar, Tooltips ohne Fehler"
    why_human: "ECharts-Darstellung, Hover und Tastaturbedienung brauchen einen Browser"
  - test: "Ausgaben-Treemap und Zuschuss-Balken optisch prüfen (Plan 05-10, 05-14)"
    expected: "„Weitergabe an Kreis und Land“ ist farblich und per Streifenmuster abgesetzt und lesbar (siehe WR-03: Streifen sind möglicherweise vollständig deckend), Überschuss-Punkte, Beschriftungen passen, Tooltips korrekt"
    why_human: "Visuelle Prüfung; WR-03 sagt voraus, dass die Deckkraft der Dekals im Browser nicht greift"
  - test: "Produktseite /#/produkt/030101, /#/produkt/160101 und ein Produkt ohne Investitionen öffnen (Plan 05-11)"
    expected: "Abschnittsreihenfolge laut UI-SPEC, Tabelle scrollt bei 360 px mit fester erster Spalte, Zurück-Link führt zur selben Ebene und demselben Jahr"
    why_human: "Layout und Scrollverhalten"
  - test: "Geldfluss-Seite je Jahr 2024 bis 2029 ansehen (Plan 05-12)"
    expected: "Sankey bilanziert (Defizit und Minderaufwand links, Überschuss rechts in 2024), Knotenbeschriftungen überlappen bei 700 bis 1280 px nicht, Lesehilfe passt zum Jahr"
    why_human: "Beschriftungsüberlappung und Optik der 16 rechten Knoten"
  - test: "Glossar öffnen, Sprungmarken und GlossarBegriff-Links aus Seiten testen (Plan 05-13, 05-15)"
    expected: "Link scrollt zum Begriff und setzt den Fokus, Tooltip zeigt den ersten Satz bei Hover und Fokus, Produktakkordeon klappt auf und „Produkt öffnen“ führt zur Produktseite"
    why_human: "Scroll- und Fokusverhalten, Tooltips"
  - test: "Tastatur- und Skip-Link-Prüfung (Plan 05-07)"
    expected: "Skip-Link „Zum Inhalt springen“ erscheint als erstes fokussierbares Element und springt zum Hauptinhalt; Fokusring überall sichtbar"
    why_human: "Tastaturbedienung"
  - test: "Fußzeile: Kontakt und Link zum Original-PDF festlegen oder bewusst als Platzhalter belassen (UI-03, ROADMAP SC 1)"
    expected: "Entscheidung des Entwicklers: Die Fußzeile verweist heute auf `kontakt-noch-nicht-festgelegt@example.invalid` und `https://haushaltsplan-noch-nicht-festgelegt.invalid/` (app/src/config.ts). Nutzerentscheidung D-17 verschiebt die echten Werte nach Phase 7; kein Test oder CI-Schritt erzwingt das (IN-09)"
    why_human: "Die Werte kann nur der Projektinhaber liefern; ob UI-03 für Phase 5 damit als erfüllt gilt, ist eine Entscheidung"
gaps: []
---

# Phase 5: Leitfragen-Seiten Verification Report

**Phase Goal:** Bürgerinnen und Bürger finden in der App laienverständliche Antworten auf „Wo kommt das Geld her?“ und „Wofür wird es ausgegeben?“. Jede gezeigte Zahl stammt aus den generierten Daten.
**Verified:** 2026-10-05T20:10:00Z
**Status:** human_needed
**Re-verification:** Ja, nach Gap-Closure-Plan 05-16 (G-05-4, G-05-6 aus 05-UAT.md); Erstverifikation vom 2026-10-04 (23 Dateien, 1005 Tests)

## Re-Verifikation nach Plan 05-16 (G-05-4, G-05-6)

Ausgangslage: 05-UAT.md meldet 6 bestanden und 2 Probleme. Plan 05-16 sollte beide schließen. Ich habe die Must-haves des Plans gegen den Code geprüft, nicht gegen 05-16-SUMMARY.md. Ergebnis: alle sechs Wahrheiten sind im Code belegt, keine Regression, keine neuen Gaps. Die Landeposition im Browser bleibt offen und steht unter Human Verification.

| # | Must-have aus 05-16 | Status | Evidenz |
|---|---------------------|--------|---------|
| 1 | Hash-Ziel landet unter der Kopfzeile: Router scrollt zum Element minus dessen berechnetes `scroll-margin-top` | ✓ VERIFIED im Code, ⚠️ PRESENT_BEHAVIOR_UNVERIFIED im Browser | `router/index.ts` `scrollBehavior` delegiert an `sprungPosition(to, from, gespeichert)`; `sprungziel.ts` gibt `{ el: ziel, top: versatz(ziel) }` zurück, `scrollVersatz` liest `getComputedStyle(ziel).scrollMarginTop`. vue-router (`devtools-CN5uWJaH.js`, `getElementPosition`) rechnet `top = elRect.top - docRect.top - (offset.top \|\| 0)`, `top` ist also ein Abzug, wie der Plan annimmt. `wa-page` definiert `--scroll-margin-top: calc(var(--header-height, 0px) + var(--subheader-height, 0px) + 0.5em)` (Web-Awesome-Stylesheet, gelesen). `GlossarListe.vue:58` nutzt `calc(var(--scroll-margin-top, 0px) + var(--wa-space-m))` |
| 2 | `sprungPosition` liefert genau `{ el, top }`; Offset 0 bei unlesbar oder negativ; unbekannter Hash bleibt oben; gespeicherte Position und reiner Query-Wechsel wie zuvor | ✓ VERIFIED | `sprungziel.ts` Zweigfolge: Ziel, gespeichert, gleicher Pfad `false`, sonst `{ top: 0 }`; `versatzAusScrollMargin` lässt nur endliche Werte > 0 zu. `sprungziel.test.ts` (11 Tests) enthält `toEqual({ el, top: 96 })` und `toEqual({ top: 0 })`. Lauf: 2 Dateien, 16 Tests grün |
| 3 | Sprung bleibt ein Sofortsprung, kein `behavior`-Schlüssel | ✓ VERIFIED | Rückgabe enthält kein `behavior`; `toEqual` im Test schließt einen zusätzlichen Schlüssel aus |
| 4 | Jedes `var(--wa-*)` in `app/src` ist definiert, ein Test schlägt bei undefiniertem Token fehl; `--wa-space-md` ist behoben | ✓ VERIFIED | `grep wa-space-md app/src` trifft nur noch die absichtlichen Beispiele in `stiltokens.test.ts`. Mutationsprobe in einer Scratch-Kopie: Rückgängig-Machen der Korrektur in `GlossarListe.vue` lässt `stiltokens.test.ts` mit `expected [ '--wa-space-md' ] to deeply equal []` fehlschlagen; mit der Korrektur 5/5 grün. Der Test hat Sanity-Zähler (> 20 Dateien, > 100 Tokens) |
| 5 | Einnahmen-Balkenklick scrollt unter die Kopfzeile nach derselben Regel; Reduced-Motion-Schalter unverändert | ✓ VERIFIED im Code, ⚠️ Browser offen | `EinnahmenPage.vue:447` `scroll-margin-top: calc(var(--scroll-margin-top, 0px) + var(--wa-space-m))`; `oeffneAufschluesselung` ist im Plan-Diff nicht angefasst (Plan 05-16 listet nur diese Regel als Änderung) |
| 6 | Blick-Block: dt/dd durch `--wa-space-2xs` getrennt, Unterstrich berührt das Tag nicht | ✓ VERIFIED im Code, ⚠️ Browser offen | `ProduktPage.vue:238-242` `.om-produkt__blick dd { margin: 0; margin-block-start: var(--wa-space-2xs); }`; gilt für alle drei Zeilen |

Verbote aus 05-16: `GlossarBegriff.vue:37` behält `text-underline-offset: 4px` (✓); die dt-Regel behält `line-height: var(--wa-line-height-condensed)` (✓).

Key Links: `router/index.ts` → `sprungziel.ts` (Import von `elementFuerHash`, `sprungPosition`; Aufruf `sprungPosition(`) ✓ WIRED; `sprungziel.ts` → `scrollMarginTop` ✓; `GlossarListe.vue` → `var(--scroll-margin-top` ✓. Die lokale `elementFuerHash` wurde aus dem Router entfernt; `afterEach` nutzt die importierte Funktion, der Fokus-Code (D-13) ist unverändert.

Selbst erhobene Evidenz: Scratch-Kopie von `app/` (git-Stand = Arbeitsbaum, keine Änderungen unter `app/`) mit der Linux-`node_modules` per Symlink; `vitest run` gesamt: **1031 Tests grün**; die beiden neuen Dateien einzeln: 16 Tests grün. Type-check, lint, format:check, build und die Pipeline-Kette (ruff, pytest 528) habe ich nicht erneut gefahren, sie wurden nach dem Merge als grün gemeldet. Anti-Pattern-Scan der neuen Dateien: keine TODO/FIXME/XXX/TBD.

Folgen für den Status: G-05-4 und G-05-6 sind im Code und in den Tests geschlossen. Ob die Begriffe im Browser tatsächlich sichtbar unter der Kopfzeile landen (1280 px und 360 px) und der Unterstrich das Tag nicht mehr berührt, kann nur ein Mensch prüfen. Das sind drei neue Human-Verification-Punkte, davon einer als `behavior_unverified`. Deshalb bleibt der Status `human_needed`. Eine Rückmeldung per `/gsd-verify-work` (UAT-Tests 4 und 6) schließt die Gaps formal.

## Zusammenfassung (Erstverifikation, weiterhin gültig)

Ich bin von der Annahme ausgegangen, dass das Ziel verfehlt ist, und habe sie gegen Code und Daten geprüft. Sie ließ sich nicht halten: Alle fünf ROADMAP-Erfolgskriterien sind im Code vorhanden, mit den echten Daten verdrahtet und durch Unit-Tests auf konkrete Sollwerte geprüft. Es gibt keine fehlgeschlagene Wahrheit und keinen Blocker.

Der Status ist trotzdem `human_needed`, aus drei Gründen:

1. Die Sandbox hat keinen Browser. Alle Plan-Hostchecks (Layout bei 360 und 1280 px, Tastatur und Fokus, Sankey-Hover und -Klick, Tooltips, Drawer, Skip-Link) stehen aus.
2. Es gibt keine Komponenten- oder Router-Tests. Vier verhaltensabhängige Wahrheiten (Fokus nach Routenwechsel, Sankey-Klick, Drilldown-Zusammenspiel, mobile Umschaltung) sind vorhanden und verdrahtet, aber nicht ausgeführt.
3. Kontakt und PDF-Link in der Fußzeile sind Platzhalter (`.invalid`). Das ist eine ausdrückliche Nutzerentscheidung (D-17), aber ROADMAP SC 1 verlangt „Link zum Original-PDF und einen Kontakt“. Das Urteil darüber liegt beim Projektinhaber.

## Evidenz, die ich selbst erhoben habe

- Erstverifikation: vitest in der Scratch-Kopie `.../scratchpad/s2/app` auf HEAD `ed0b034`: 23 Dateien, 1005 Tests bestanden. Nach Plan 05-16 (siehe oben): 25 Dateien, 1031 Tests bestanden.
- Der Orchestrator hat die vollständige CI-Spiegelung auf dem Endstand gefahren (type-check, lint, format:check, build, pytest 515, `alle.py` byte-identisch). Das habe ich nicht erneut ausgeführt und übernehme es als gemeldet.
- Anti-Pattern-Scan über `app/src` und `pipeline/ostbevern`: keine Treffer für TBD, FIXME, XXX, TODO, HACK, placeholder, „coming soon“, „not yet implemented“ (außerhalb der Tests).
- `texte.json`: Nach Entfernen der `{{…}}`-Platzhalter bleiben in den 41 Texten nur Jahreszahlen und §-Verweise als Ziffern übrig. Jeder Text mit Platzhalter hat nicht-leere `quelle_seiten`.
- `quelltext.test.ts` prüft über alle `.vue`-Templates: keine getippten Tausenderzahlen, keine Zahl mit Mio./€/%, kein `v-html`.

## Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidenz |
|---|-------|--------|---------|
| 1 | Startseite: Kennzahlenband 2026, zwei Einstiege, Kreisumlage-Hinweis, Fußzeile mit Datenstand, PDF-Link, „inoffizielles Projekt“, Kontakt | ✓ VERIFIED (mit Vorbehalt zu Kontakt und PDF-Link) | `StartPage.vue` rendert `baueKennzahlen()` (sieben Kacheln), `baueEinstiege()` und `KreisumlageCallout kurz`. `kennzahlen.test.ts:108-123` prüft 27,5 / 30,5 / -2,35 / 12,3 / 5,2 Mio. € und Pro-Kopf 2594 und 1571. Werte kommen aus `haushalt.json` (GESAMT Ertrag 27.502.063, Aufwand 30.455.569, Ergebnis nach Minderaufwand -2.353.506) und `investitionen.json`. Fußzeile in `App.vue:152-188` enthält Datenstand, Original-PDF-Link, „Inoffizielles Projekt“, Kontakt, aber PDF-URL und E-Mail sind `.invalid`-Platzhalter (siehe Human Verification Punkt 8) |
| 2 | `/einnahmen`: Ertragsarten mit Betrag und Anteil, aufklappbare Ebenen (Steuern mit Hebesätzen und Selbstfestlegung, Zuwendungen mit Sonderposten „kein Geldfluss“, sonstige Erträge mit Konzessionsabgaben), Zeitreihe je Steuerart 2022 bis 2029 mit Ist/Plan, investive Einnahmen getrennt | ✓ VERIFIED | `EinnahmenPage.vue`: `ErtragsBalken` plus Tabelle (`baueErtragsarten`), drei `wa-details` mit `DatenTabelle`, Hebesatz-Absatz, `ErklaerText steuern_selbst_festgelegt`, `kein Geldfluss`-Tag, `SteuerZeitreihe`, eigener Abschnitt „Investive Einnahmen“ mit eigenem Callout und `INVEST_FARBE`. Konzessionsabgaben 470.000 € in `vorbericht.sonstige_ertraege`; Summe der Posten 2026 = 1.943 T€ = Zeile 07. Zeitreihe: Ist 2022/2023 aus Grundzahlen 160101, Plan aus Vorbericht (`zeitreihen.ts`, `zeitreihen.test.ts`). Der Druckfehler 2.396 T€ (2028) ist in `befunde.md` dokumentiert |
| 3 | `/ausgaben`: Treemap mit Drilldown, KL als abgesetzte Kachel mit Callout, Minderaufwand-Hinweis, Umschalter Aufwand/Zuschussbedarf mit Überschuss-Erklärung, Aufwandsart-Sicht mit Transfer-Aufklappern und Abschreibungen „kein Geldfluss“, Produktdetail | ✓ VERIFIED | `AusgabenPage.vue`: `AufwandTreemap`/`ZuschussBalken`, `Brotkrumen`, `KL_DECAL` in `drilldown.ts`, `KreisumlageCallout` (oberste Ebene und innerhalb KL), `wa-callout` für `minderaufwandHinweis`, Überschuss-Callout, `AufwandsartBalken` mit „Transferaufwendungen im Einzelnen“ und „kein Geldfluss“-Tag. `ProduktPage.vue` hat Beschreibung, Leistungen, Auf einen Blick (Bindungsgrad, Gremium), Teilergebnisplan, Erläuterungen, Grundzahlen mit `BerechnetEtikett`, Investitionen, Quellzeile. Der „Quellenlink“ ist laut D-09 eine PDF-Seitenangabe als Text; die klickbare Seitenleiste ist Phase 7 (UI-02) |
| 4 | `/geldfluss`: Sankey bilanziert über Defizit und Minderaufwand, Hover-Hervorhebung, Klick zur Ausgabenseite, schmal Tabelle oder Balken, Jahr-Umschalter 2024 bis 2029 | ✓ VERIFIED (Klick, Hover und mobile Umschaltung als PRESENT_BEHAVIOR_UNVERIFIED) | `geldfluss.ts`: linke Seite Erträge + Defizit + Minderaufwand, rechte Seite KL + PB + Zinsen + Überschuss; `geldfluss.test.ts:261` prüft 2026 Defizit 2.353.506 € + Minderaufwand 600.000 € = 30.455.569 € und 2024 Überschuss rechts. `emphasis: { focus: 'adjacency' }` (Z. 415), `SankeyDiagramm.vue` ruft bei Klick `router.push` auf `ausgaben?pb=` mit `jahrLink`; `GeldflussPage.vue` zeigt unter `istSchmal` den `GeldflussBalken`, sonst Sankey plus Tabellen mit Detail-Links als Tastaturpfad. `JahrUmschalter` auf Einnahmen, Ausgaben, Geldfluss |
| 5 | `/glossar`: mindestens 22 Begriffe aus Spez. 6.14, alle 63 Produkte als Akkordeon, `GlossarBegriff`-Links führen zum Begriff, Zahlen in Erklärtexten aus Daten mit PDF-Seite | ✓ VERIFIED | `texte.json.glossar` hat 24 Einträge, alle 22 Begriffe der Spez. 6.14 sind vorhanden (Ertrag/Aufwand und Ein-/Auszahlung je als ein Eintrag). `produkte.json` hat 63 Produkte, alle mit Beschreibung; `glossar.test.ts` prüft „jedes Produkt genau einmal“. `GlossarBegriff` verlinkt `/glossar#schluessel` mit Tooltip, auf allen fünf Inhaltsseiten verwendet (3/3/2/6/2 Verwendungen); `quelltext.test.ts` prüft Pflichtschlüssel und dass jeder verwendete Schlüssel existiert (Union-Typ). Zahlen kommen über `{{schluessel\|kuerzel}}`-Platzhalter aus `werte` |

**Score:** 5/5 Erfolgskriterien in Code und Daten belegt; 4 Teilwahrheiten verhaltensabhängig ohne Test (`behavior_unverified: 4`).

## Required Artifacts

| Artifact | Erwartet | Status | Details |
|----------|----------|--------|---------|
| `app/src/pages/{Start,Einnahmen,Ausgaben,Produkt,Geldfluss,Glossar}Page.vue` | Sechs Seiten | ✓ VERIFIED | 154 / 501 / 466 / 274 / 154 / 76 Zeilen, voll gefüllte Templates, im Router eingetragen |
| `app/src/router/index.ts` | Routen `/`, `/einnahmen`, `/ausgaben`, `/produkt/:code`, `/geldfluss`, `/glossar`, Titel und Fokus | ✓ VERIFIED | Alle sechs Routen vorhanden, `afterEach` mit Titel, Fokus, Ansage; `scrollBehavior` delegiert seit 05-16 an `sprungPosition` |
| `app/src/lib/sprungziel.ts` (+ `sprungziel.test.ts`, `stiltokens.test.ts`) | Router-Scrollposition mit Kopfzeilen-Versatz, Token-Wächter (05-16) | ✓ VERIFIED | Substanziell (Logik, 11 + 5 Tests), vom Router importiert und genutzt |
| `app/src/lib/*.ts` (Builder) | Datenaufbereitung ohne getippte Werte | ✓ VERIFIED | 21 Module, 19 Testdateien in `lib/__tests__` |
| `app/src/data/{haushalt,texte,produkte}.json` | Generierte Daten | ✓ VERIFIED | Von `alle.py` byte-identisch reproduziert (Orchestrator) |
| `pipeline/ostbevern/texte.py`, `app_daten.py` | Textprüfung und Datenexport | ✓ VERIFIED | Teil der 515 grünen Pipeline-Tests |
| `app/src/config.ts` | Kontakt und PDF-URL | ⚠️ PLATZHALTER | Absichtlich `.invalid` (D-17), siehe Human Verification |

## Key Link Verification

| Von | Nach | Via | Status |
|-----|------|-----|--------|
| `StartPage` | `haushalt.json`, `investitionen.json` | `baueKennzahlen`, `baueEinstiege` | ✓ WIRED, Daten fließen (Test auf Sollwerte) |
| `EinnahmenPage` | Vorbericht-Tabellen | `baueSteuern`, `baueZuwendungen`, `baueSonstigeErtraege` | ✓ WIRED |
| `AusgabenPage` | `haushalt.knoten`/`ergebnisplan` | `baueEbene`, `useAnsicht` (URL-Zustand) | ✓ WIRED |
| `SankeyDiagramm` | `/ausgaben?pb=` | `beiKlick` → `router.push(jahrLink(…))` | ✓ WIRED (Laufzeit nicht geprüft) |
| `GlossarBegriff` | `/glossar#schluessel` | `RouterLink` mit Hash, `scrollBehavior` → `sprungPosition` mit `scroll-margin-top`-Versatz (05-16) | ✓ WIRED (Landeposition im Browser offen) |
| `GlossarPage` | 63 Produkte | `ProduktAkkordeon` → `produktGruppen()` | ✓ WIRED |
| Seiten | Erklärtexte | `ErklaerText` → `textFuerJahr` → `rendereAbsatz` | ✓ WIRED |
| `App.vue` Fußzeile | `config.ts` | `ORIGINAL_PDF_URL`, `KONTAKT_EMAIL` | ✓ WIRED, Werte Platzhalter |

## Data-Flow Trace (Level 4)

| Artefakt | Variable | Quelle | Echte Daten | Status |
|----------|----------|--------|-------------|--------|
| `StartPage` | `kennzahlen` | `haushalt.ergebnisplan.GESAMT`, `investitionen.finanzierung` | Ja | ✓ FLOWING |
| `EinnahmenPage` | `ertragsarten`, `aufklapper` | `haushalt.ergebnisplan`, `haushalt.vorbericht.*` | Ja | ✓ FLOWING |
| `AusgabenPage` | `eintraege` | `haushalt.knoten` + `ergebnisplan[*].berechnet.aufwand` | Ja | ✓ FLOWING |
| `GeldflussPage` | `geldfluss` | `baueGeldfluss(index)` aus Ergebnisplan + Vorbericht | Ja | ✓ FLOWING |
| `GlossarPage` | `begriffe`, `gruppen` | `texte.json`, `produkte.json` | Ja | ✓ FLOWING |
| Erklärtexte | `werte` | `texte.json.werte` (40 Schlüssel, aus Pipeline-Daten abgeleitet) | Ja | ✓ FLOWING |

## Behavioral Spot-Checks

| Verhalten | Befehl | Ergebnis | Status |
|-----------|--------|----------|--------|
| Gesamte App-Testsuite (einmal) | `npx vitest run` in der Scratch-Kopie | 23 Dateien, 1005 Tests bestanden | ✓ PASS |
| Scratch-Kopie = HEAD | `diff -rq app/src …/s2/app/src` | keine Unterschiede | ✓ PASS |
| Sollwerte Start | `kennzahlen.test.ts` (Teil des Laufs) | 27,5 / 30,5 / -2,35 / 12,3 / 5,2 Mio. €, 2594 €, 1571 € | ✓ PASS |
| Geldfluss bilanziert | `geldfluss.test.ts` (Teil des Laufs) | Linke Summe 2026 = 30.455.569 € | ✓ PASS |
| Datenzähler | `node` über `texte.json`, `produkte.json`, `haushalt.json` | 24 Glossarbegriffe, 63 Produkte mit Beschreibung, 63 Produktknoten | ✓ PASS |

Step 7c (Probes): Es gibt keine `probe-*.sh` und die Pläne deklarieren keine. Übersprungen.

## Requirements Coverage

Alle 23 IDs der Phase stehen in mindestens einem PLAN-Frontmatter (05-16 deklariert GLOS-03 und AUSG-05) und in der Traceability-Tabelle von REQUIREMENTS.md als „Phase 5“. Keine verwaisten IDs. Hinweis: Status und Checkboxen in REQUIREMENTS.md stehen noch auf „Pending“ bzw. `[ ]`; die Pflege gehört zum Phasenabschluss. UI-02 (Phase 7), UI-04 (Phase 6) und UI-06 (Phase 7) sind korrekt nicht Phase 5 zugeordnet.

| Requirement | Pläne | Status | Evidenz |
|-------------|-------|--------|---------|
| START-01 | 05-08 | ✓ SATISFIED | Sieben Kennzahlkacheln, Test auf Sollwerte |
| START-02 | 05-06, 05-08 | ✓ SATISFIED (WR-02) | Zwei `EinstiegsKachel`, `KreisumlageCallout kurz`; Formulierung der zweiten Kachel siehe WR-02 |
| EINN-01 | 05-06, 05-09 | ✓ SATISFIED | Ertragsbalken + Tabelle mit Betrag und Prozent |
| EINN-02 | 05-09 | ✓ SATISFIED | Steuern-Aufklapper, Hebesatz-Absatz, Spalte „Festlegung“, Text `steuern_selbst_festgelegt` |
| EINN-03 | 05-09 | ✓ SATISFIED | Zuwendungen-Aufklapper, `kein Geldfluss`-Tag für Sonderposten |
| EINN-04 | 05-02, 05-09 | ✓ SATISFIED | Sonstige Erträge mit Konzessionsabgaben (470.000 €), Regel 5 prüft gegen Zeile 07 |
| EINN-05 | 05-03, 05-09 | ✓ SATISFIED | `SteuerZeitreihe` mit Ist/Plan-Serien, Erklärtexte Gewerbesteuer und Schlüsselzuweisung |
| EINN-06 | 05-02, 05-09 | ✓ SATISFIED | Eigener Abschnitt „Investive Einnahmen“, eigene Farbe, eigenes Diagramm |
| AUSG-01 | 05-05, 05-10 | ✓ SATISFIED | `AufwandTreemap` mit Drilldown PB → PG → Produkt |
| AUSG-02 | 05-05, 05-06, 05-10, 05-14 | ✓ SATISFIED | KL-Dekal und Callout, Minderaufwand-Callout unter dem Diagramm |
| AUSG-03 | 05-10 | ✓ SATISFIED | `wa-radio-group` Aufwand/Zuschussbedarf, Überschuss-Callout |
| AUSG-04 | 05-14 | ✓ SATISFIED | `AufwandsartBalken`, Transfer-Aufklapper, Abschreibung „kein Geldfluss“ |
| AUSG-05 | 05-04, 05-11, 05-16 | ✓ SATISFIED (Optik im Browser offen) | `ProduktPage` mit allen geforderten Abschnitten; Quellenlink als Seitenangabe (D-09); Etikett–Wert-Abstand seit 05-16 (G-05-4) |
| FLUSS-01 | 05-05, 05-12 | ✓ SATISFIED | `geldflussOption` Sankey |
| FLUSS-02 | 05-12 | ✓ SATISFIED | Defizit- und Minderaufwand-Knoten, Bilanztest |
| FLUSS-03 | 05-12 | ✓ SATISFIED (Laufzeit offen) | `emphasis`, `beiKlick`, `zielCodeAusKlick` getestet |
| FLUSS-04 | 05-05, 05-12 | ✓ SATISFIED (Laufzeit offen) | `GeldflussBalken` bei `istSchmal`, Tabelle bei breit |
| GLOS-01 | 05-03, 05-13 | ✓ SATISFIED | 24 Begriffe |
| GLOS-02 | 05-13 | ✓ SATISFIED | `ProduktAkkordeon`, 63 Produkte |
| GLOS-03 | 05-13, 05-15, 05-16 | ✓ SATISFIED (Landeposition im Browser offen) | `GlossarBegriff` auf allen fünf Inhaltsseiten, Quelltext-Test; seit 05-16 scrollt der Router mit Kopfzeilen-Versatz (G-05-6) |
| UI-01 | 05-04 | ✓ SATISFIED | `JahrUmschalter` auf Einnahmen, Ausgaben, Geldfluss; `?jahr=` validiert, Standard 2026 |
| UI-03 | 05-07 | ⚠️ NEEDS HUMAN | Fußzeile vollständig verdrahtet; Kontakt und PDF-URL sind Platzhalter (D-17) |
| UI-05 | 05-01, 05-03, 05-06, 05-15 | ✓ SATISFIED | Platzhalter-Renderer, Pipeline-Ziffernregel, `quelltext.test.ts`, Seitenverweis in `ErklaerText` |

## Anti-Patterns

Keine Blocker. Keine Debt-Marker (TBD/FIXME/XXX) in den geänderten Dateien. Die offenen Befunde stammen aus dem Code-Review (`05-REVIEW.md`, 0 kritisch, 7 Warnungen, 11 Info, alle `open`), die ich nicht neu bewertet habe, mit Ausnahme der folgenden, die das Phasenziel berühren:

| Datei | Befund | Schwere | Auswirkung auf das Ziel |
|-------|--------|---------|-------------------------|
| `app/src/pages/StartPage.vue:95` / `lib/kennzahlen.ts:196` (WR-02) | Kachel sagt „Den größten Anteil bekommt Innere Verwaltung: 4,5 Mio. €“, während der Callout darunter „Der größte Einzelposten ist die Weitergabe an Kreis und Land“ (rund 11 Mio. €) sagt. Der Satz stammt wörtlich aus der UI-SPEC (D-20), liest sich aber auf demselben Bildschirm widersprüchlich | ⚠️ Warning | Laienverständlichkeit und „Bürgerinformation muss stimmen“. Vor Phase 7 (Textdurchgang) umformulieren, etwa „Unter den Aufgabenbereichen …“ |
| `lib/geldfluss.ts` (WR-01) | Sankey-Tooltips zeigen Vorbericht-Werte (T€ × 1000) ohne „rd.“, anders als alle anderen Seiten | ⚠️ Warning | Zahlen stammen aus den Daten, aber die Präzision wird überzeichnet. Nicht zielgefährdend |
| `charts/echartsTheme.ts` (WR-03) | `mitDeckkraft` verarbeitet nur `#rrggbb`; `--wa-color-surface-default` ist `white`, die Dekal-Deckkraft greift im Browser nicht | ⚠️ Warning | Betrifft die Lesbarkeit der KL-Kachel (AUSG-02, „farblich abgesetzt“ bleibt erfüllt); im Browser prüfen |
| `pipeline/ostbevern/pruefung.py`, `texte.py` (WR-04, WR-05, WR-06) | Stille Lücken in Prüfungen (Seitenspannen in `Quelle:`, fehlendes `meta`, Formeln für andere Jahrgänge) | ⚠️ Warning | Aktuell ohne Datenfehler; schwächt die Prüfgarantie bei künftigen Änderungen |
| `components/DatenTabelle.vue` (WR-07) | Jede beschriftete Tabelle ist ein Tab-Stopp und doppelt benannt | ⚠️ Warning | A11Y (Phase 7, Lighthouse ≥ 95) |

Die Info-Befunde IN-01 bis IN-11 sind latente Fehler oder Konsistenzthemen ohne Auswirkung auf die aktuellen Daten und kein Grund für gaps. IN-09 (Platzhalter ohne CI-Sperre) hängt mit Human-Verification-Punkt 8 zusammen und sollte vor dem Deployment in Phase 7 erzwungen werden.

## Deferred Items

| # | Punkt | Adressiert in | Evidenz |
|---|-------|---------------|---------|
| 1 | Klickbare Quellenseitenleiste mit PDF-Ausschnitt (über die PDF-Seitenangabe hinaus) | Phase 7 | ROADMAP Phase 7 SC 1 / UI-02 |
| 2 | Barrierefreiheit gesamt (Lighthouse ≥ 95), Tabellenalternativen für jedes Diagramm, 360-px-Prüfung | Phase 7 | ROADMAP Phase 7 SC 2 und 3 |
| 3 | Du-Anrede-Textdurchgang | Phase 7 | ROADMAP Phase 7 SC 4 / UI-06 |

Echte Kontakt-Adresse und PDF-URL sind **nicht** ausdrücklich in einem Phase-7-Erfolgskriterium genannt, nur in der Nutzerentscheidung D-17 und im Kommentar in `config.ts`. Deshalb führe ich sie als Human-Verification-Punkt und nicht als Deferred.

## Human Verification Required

Siehe das Frontmatter (`human_verification`, elf Punkte; die ersten drei stammen aus 05-16). Zusammengefasst:

0. Neu aus 05-16: Glossar-Sprung unter der Kopfzeile (1280 und 360 px, Reduced Motion), Einnahmen-Balken-Scroll, Etikett–Wert-Abstand auf Produktseiten

1. Startseite bei 360 und 1280 px (Plan 05-08)
2. Einnahmen-Seite (Plan 05-09)
3. Ausgaben-Treemap, KL-Optik (WR-03), Zuschuss-Balken (Pläne 05-10, 05-14)
4. Produktseiten (Plan 05-11)
5. Geldfluss je Jahr, Beschriftungen (Plan 05-12)
6. Glossar, Sprungmarken, Tooltips (Pläne 05-13, 05-15)
7. Skip-Link und Tastatur (Plan 05-07)
8. Entscheidung zu Kontakt und PDF-Link in der Fußzeile (UI-03)

Dazu die fünf `behavior_unverified_items` (vier aus der Erstverifikation, eines neu: Landeposition des Glossar-Sprungs) (Fokus nach Routenwechsel, Sankey-Klick, Drilldown-Zusammenspiel, mobile Umschaltung und Drawer).

## Gaps Summary

Keine Gaps. Das Phasenziel ist im Code und in den Daten erreicht: Beide Leitfragen haben eigene Seiten, jede Zahl läuft über `haushalt.json`, `texte.json` oder `produkte.json`, und Tests binden die Kernzahlen an die Sollwerte aus dem PDF. Seit Plan 05-16 sind auch die beiden UAT-Gaps G-05-4 und G-05-6 im Code geschlossen. Offen sind ausschließlich Browserprüfungen, die Entscheidung zu den Fußzeilen-Platzhaltern und ein redaktioneller Widerspruch auf der Startseite (WR-02), den ich als Warnung führe.

---

_Verified: 2026-10-05T20:10:00Z (Re-Verifikation)_
_Verifier: Claude (gsd-verifier)_
