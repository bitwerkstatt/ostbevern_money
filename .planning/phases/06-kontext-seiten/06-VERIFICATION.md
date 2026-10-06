---
phase: 06-kontext-seiten
verified: 2026-10-06T12:00:00Z
status: gaps_found
score: 4/5 must-haves verified
covered_files:
  - .planning/phases/06-kontext-seiten/06-01-PLAN.md
  - .planning/phases/06-kontext-seiten/06-01-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-02-PLAN.md
  - .planning/phases/06-kontext-seiten/06-02-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-03-PLAN.md
  - .planning/phases/06-kontext-seiten/06-03-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-04-PLAN.md
  - .planning/phases/06-kontext-seiten/06-04-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-05-PLAN.md
  - .planning/phases/06-kontext-seiten/06-05-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-06-PLAN.md
  - .planning/phases/06-kontext-seiten/06-06-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-07-PLAN.md
  - .planning/phases/06-kontext-seiten/06-07-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-08-PLAN.md
  - .planning/phases/06-kontext-seiten/06-08-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-09-PLAN.md
  - .planning/phases/06-kontext-seiten/06-09-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-10-PLAN.md
  - .planning/phases/06-kontext-seiten/06-10-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-11-PLAN.md
  - .planning/phases/06-kontext-seiten/06-11-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-12-PLAN.md
  - .planning/phases/06-kontext-seiten/06-12-SUMMARY.md
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MenueGruppe.vue
  - app/src/lib/ruecklagen.ts
  - app/src/lib/stellen.ts
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/RatEntscheidetPage.vue
  - app/src/pages/StellenplanPage.vue
covered_digest: "v2:sha256:189947babfe3ec688f7d1202156ffc5218bb071d9c3ea8403c7e87b72f8ed7a7"
behavior_unverified: 1
overrides_applied: 0
gaps:
  - truth: "SC1 / ENTW-03 / Core Value: Die Rücklagen-Seite erklärt nachvollziehbar, wie lange das Polster reicht; jede Zahl ist aus dem PDF ableitbar (Fußnote unter der Rücklagen-Tabelle erklärt den gezeigten Rückgang im Jahr korrekt)"
    status: partial
    reason: "CR-01 (06-REVIEW.md) bestätigt. Die Fußnote in EntwicklungPage.vue beschreibt den Rückgang als 'Fehlbetrag, soweit die Ausgleichsrücklage ihn nicht deckt, geteilt durch die allgemeine Rücklage zu Jahresbeginn'. Die implementierte (und mit S. 23 übereinstimmende) Formel in lib/ruecklagen.ts ist max(0, -Ergebnis - Ausgleich) - Verrechnung_Bilanzierungshilfe. Für 2026: (2.353.506 - 2.132.213) = 221.293 / 39.522.991 = 0,56 % laut Fußnote, aber 697.620 / 39.522.991 = 1,77 % in Tabelle und Diagramm (und auf PDF S. 23 gedruckt). Der Zahlenwert ist korrekt, die bürgerseitige Herleitung nicht nachrechenbar."
    artifacts:
      - path: "app/src/pages/EntwicklungPage.vue"
        issue: "tabellenFussnote (Zeilen ca. 77-82) nennt den Summanden 'Verrechnung der Bilanzierungshilfe' nicht"
    missing:
      - "Fußnote um den Term 'zuzüglich der Verrechnung der Bilanzierungshilfe' ergänzen (besser: aus den Formelkonstanten ableiten)"
      - "Test, dass die Fußnote die Verrechnung nennt, sobald ein Jahr verrechnung_bilanzierungshilfe != 0 hat"
behavior_unverified_items:
  - truth: "Kopfmenü-Gruppe 'Mehr wissen' hält die geöffnete Liste bei jedem Öffnen und nach Resize im Fenster (MenueGruppe.positioniere, WR-01)"
    test: "Bei 360-1024 px Breite 'Mehr wissen' öffnen, schließen, erneut öffnen; Fenster verkleinern, während die Liste offen ist"
    expected: "Die Liste bleibt jedes Mal vollständig im Viewport"
    why_human: "Das Verhalten hängt von einem Render-Zyklus (versatz wird auf 0 gesetzt und sofort vor dem DOM-Update gemessen) und Layout ab; es gibt keinen Komponententest, grep sieht nur, dass positioniere() existiert und aufgerufen wird. Die Code-Review-Analyse (WR-01) deutet auf Messung mit veraltetem Offset beim zweiten Öffnen."
human_verification:
  - test: "End-of-Phase-Walkthrough aller vier Seiten bei 1280 px und 360 px, nur Maus und Tastatur (vollständige Liste in 06-12-SUMMARY.md 'Offene Human-Checks')"
    expected: "Kein horizontales Seiten-Scrollen bei 360 px; zweizeilige Achsen (Ist/Ansatz/Planung) lesbar; Direktbeschriftung und 'Defizit 3,56 Mio. EUR' haben Platz; Filter nur per Tastatur bedienbar; Aufklapper 'Produkte hinter dem Balken' zeigen korrekt dimensionierte Diagramme; Stellen-Diagramme fluchten bei 1280 px und stapeln bei 360 px"
    why_human: "Sandbox ohne Browser; Layout, Kontrast, Fokusfluss, Echarts-Rendering sind nicht programmatisch prüfbar. Es existiert kein Komponenten-Mount-Test (nur lib-Tests)."
  - test: "Menü 'Mehr wissen': öffnen, Escape (Fokus zurück an den Schalter), Klick außen, Enter/Leertaste, aktiver Zustand bei aktiver Unterseite; bei 360 px Drawer-Gruppe"
    expected: "Wie in 06-02-SUMMARY beschrieben; Liste immer im Viewport (siehe behavior_unverified_items)"
    why_human: "Interaktion und Fokusverhalten"
  - test: "/investitionen?art=xyz und ?pb=xyz aufrufen; Filter-Kombinationen mit genau einer Maßnahme (z. B. pb=04, pb=15)"
    expected: "Ungültige Werte werden bereinigt; Ergebniszeile liest sich korrekt (siehe WR-02, aktuell 'N Maßnahmen' auch bei N=1)"
    why_human: "Router-/Filterverhalten im Browser; WR-02 ist ein bekannter Textfehler im Singular"
---

# Phase 6: Kontext-Seiten Verification Report

**Phase Goal:** Die App ordnet den Haushalt ein: Entwicklung bis 2029, Investitionen und Schulden, Gestaltungsspielraum des Rats, Personal und was außerhalb des Kernhaushalts liegt.
**Verified:** 2026-10-06
**Status:** gaps_found
**Re-verification:** No, initial verification

Ausgangsannahme war, dass das Phasenziel nicht erreicht ist. Geprüft wurde gegen den Quellcode, die eingecheckten Daten (`app/src/data/*.json`) und das Quell-PDF (S. 23, 47, 310), nicht gegen die SUMMARYs.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | `/entwicklung` zeigt Erträge, Aufwendungen, Jahresergebnis 2024-2029 mit unterscheidbarem Ist/Ansatz/Planung (Defizit 2029 -3,56 Mio.), Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen, Ausgleichs- und allgemeine Rücklage mit Angabe, wie lange das Polster reicht | PARTIAL (Gap CR-01) | Route + `EntwicklungPage.vue` verdrahtet. Lib-Lauf (vitest-Scratch): `ergebnis_nach_minderaufwand` 2029 = -3.557.700 (= -3,56 Mio.); fünf Posten-Reihen (Kreisumlage 11,2/10,2/10,1/11,9/12,3/12,8 Mio.; Gewerbesteuer; Schlüsselzuweisung 2026 890.000; Personal; Zinsen) mit 6 Jahren; Rücklagen-Tabelle + Rückgang 1,77/4,23/4,73/10,04 % = exakt S. 23 des PDFs (-1,77 / -4,23 / -4,73 / -10,04 v. H.); Polster-Text mit `ausgleichsruecklage_aufgebraucht_jahr` aus Daten (Ausgleichsrücklage ab 2027 = 0). Mangel: die Fußnote unter der Rücklagen-Tabelle erklärt die Formel unvollständig (Verrechnung fehlt, siehe Gap). |
| 2 | `/investitionen` listet Maßnahmen 2026-2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art; VE (11,6 Mio.) mit Fälligkeiten; Finanzierung mit Zeitreihe Kreditaufnahme/Tilgung; Schuldenstand gesamt und je Einwohner (7,7 Mio. / 656 EUR) | VERIFIED | `MassnahmenFilter`, `MassnahmenListe`, `ARTEN` (Bau, Grundstücke, Fahrzeuge und Ausstattung, Sonstige), URL-Filter pb/art mit Allowlist; `veGesamt()` = 11.600.000 (Fälligkeiten 2027: 9,4 Mio., 2028: 2,2 Mio., Summe der CSV bestätigt); `finanzierung` Kreditaufnahme [0, 7,4, 5,2, 9,5, 0, 0] Mio. und Tilgung je Jahr; `schuldenKennzahlen()` = 7.710.000 / 656 EUR (2025), Rohdaten stimmen mit PDF S. 310 (6.879 + 831 TEUR); 137 Maßnahmen in `investitionen.json`. |
| 3 | `/rat-entscheidet`: Zuschussbedarf 2026 nach Bindungsgrad als gestapelter Balken mit Produkten je Kategorie; Block "Was der Rat nicht beeinflussen kann"; Einzelzuschüsse aus dem Vorbericht; Hinweis, dass der Bindungsgrad eine Selbstauskunft ist | VERIFIED | `baueBindungsgrad()` liefert Summe 13.286.440 in drei Segmenten (pflichtig 29, teils 15, freiwillig 15 Produkte); `ProduktBalkenListe` je Segment; `NichtBeeinflussbarBlock` (Kreisumlage 10.147.000, Gewerbesteuerumlage, Krankenhausumlage, Sozialleistungen 491 T EUR; KL-Gesamt 11.001.181); `ZuschussListe` mit Kitas (7 Träger, zusammen 559 T EUR), KJW, OGS 871 T EUR, 8 lfd. Zuschüsse + Summe 120 T EUR (Werte decken sich mit PDF S. 47); `bindungsgrad_selbstauskunft` in `texte.json` und als `ErklaerText` eingebunden. |
| 4 | `/stellenplan`: Stellen 2026 vs. 2025 vs. besetzt 30.06.2025, Verteilung nach Aufgabenbereich und Entgelt-/Besoldungsgruppe, daneben Personalaufwand je Aufgabenbereich (TP Z. 11) | VERIFIED | `stellenSummen()`: 62,91 / 62,13 / 56,63 VZÄ, Stichtag 2025-06-30, PDF-Seiten 284-286; `stellenNachTeil`, `stellenNachBereich` (Stellen und Personalaufwand je PB, z. B. PB 01: 21,87 VZÄ / 2.052.600 EUR), `StellenNachGruppe` je Teil; Personalaufwand-Diagramm neben dem Stellen-Diagramm (`StellenNachBereich.vue`). |
| 5 | Hinweis "Was nicht im Haushalt steht" erklärt BBO (Hallenbad) und TEO AöR (Abwasser) | VERIFIED | `HinweisNichtImHaushalt` auf `/ausgaben` (ausgaben), `/einnahmen` (einnahmen), `/rat-entscheidet` (kurz), jeweils mit Glossaranker `#nicht_im_haushalt`; Pipeline-Text `nicht_im_haushalt` (PDF-S. 14, 33, 46, 48) und Glossarbegriff existieren in `texte.json`. |

**Score:** 4/5 Wahrheiten verifiziert (1 teilweise erfüllt wegen CR-01; 1 Verhaltensprüfung offen: Menüpositionierung).

### Required Artifacts (Stichprobe aller Ebenen)

| Artifact | Status | Details |
| -------- | ------ | ------- |
| `app/src/pages/{Entwicklung,Investitionen,RatEntscheidet,Stellenplan}Page.vue` | VERIFIED | Substanziell (232/228/134/265 Zeilen), im Router (`router/index.ts`) registriert, im Menü (`lib/menue.ts`, Gruppe "Mehr wissen") verlinkt |
| `app/src/lib/{entwicklung,ruecklagen,schulden,finanzierung,investitionen,bindungsgrad,zuschuesse,stellen}.ts` | VERIFIED | Alle exportierten Funktionen laufen auf den realen JSON-Daten und liefern die oben genannten Werte (Scratch-Lauf in Kopie von app/, keine Repo-Änderung) |
| `app/src/components/HinweisNichtImHaushalt.vue` | VERIFIED | In drei Seiten eingebunden |
| `daten/manuell/zuschuesse_lfd_zwecke.csv` + Regel 5 | VERIFIED | 8 Posten + Summe 120 T EUR, Quelle S. 47; `konsistenz.md`: Gesamtstatus grün, Regel 5 grün (150 Prüfungen) |
| `app/src/data/{haushalt,investitionen,stellenplan,texte}.json` | VERIFIED | eingecheckt, Werte stimmen mit PDF-Stichproben (S. 23, 47, 310) |

### Key Link Verification

| From | To | Status | Details |
| ---- | -- | ------ | ------- |
| Menü (`MENUE`) | Routen entwicklung/investitionen/rat-entscheidet/stellenplan | WIRED | `App.vue` rendert `MenueGruppe` aus `MENUE`; Routen in `router/index.ts` |
| Seiten | lib-Module | WIRED | Importe und Nutzung in allen vier Seiten |
| lib | JSON-Daten | WIRED/FLOWING | Reale Werte (kein Static-Return); fehlende Werte bleiben `null` (Strich) |
| Hinweisbox | Glossar `#nicht_im_haushalt` | WIRED | `RouterLink` mit Hash; Anker in `GLOSSAR_SCHLUESSEL` und `texte.glossar` |
| Pipeline | `texte.json`/`haushalt.json` | WIRED | `alle.py --jahr 2026` reproduzierbar (laut 06-12, Orchestrator-Gate) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | -------- | ------ | ------ |
| Volle App-Testsuite | `npx vitest run` in Scratch-Kopie (36 Dateien) | 1393 passed | PASS |
| Schlüsselzahlen der fünf Erfolgskriterien | Scratch-Test über lib-Funktionen (Ergebnis in Scratchpad) | alle Soll-Werte reproduziert (-3.557.700; 11.600.000; 7.710.000/656; 62,91/62,13/56,63 VZÄ; 13.286.440) | PASS |
| PDF-Gegenprobe S. 23 / 47 / 310 | pdfplumber im Pipeline-venv | Rückgang 1,77/4,23/4,73/10,04 %, Zuschüsse S. 47, Verbindlichkeiten S. 310 stimmen mit Daten | PASS |
| CI-Gate (Pipeline pytest 546, ruff, App type-check/lint/format/build) | Orchestrator-Evidenz, nicht erneut ausgeführt | grün | übernommen |

### Requirements Coverage

| Requirement | Source Plan(s) | Status | Evidence |
| ----------- | -------------- | ------ | -------- |
| ENTW-01 | 06-02, 06-05, 06-12 | SATISFIED | Linien + Jahresergebnis-Säulen, Wertart-Etikett Ist/Ansatz/Planung |
| ENTW-02 | 06-05, 06-12 | SATISFIED | fünf Posten-Zeitreihen |
| ENTW-03 | 06-01, 06-04, 06-08, 06-12 | PARTIAL | Rücklagen, Rückgang und Polster-Text vorhanden; Formel-Fußnote unvollständig (CR-01) |
| INV-01 | 06-02, 06-06, 06-12 | SATISFIED | Liste + Balken + Filter (pb, art) |
| INV-02 | 06-09, 06-12 | SATISFIED | VE 11,6 Mio. mit Fälligkeiten 2027/2028 |
| INV-03 | 06-09, 06-12 | SATISFIED | Finanzierung, Kreditaufnahme/Tilgung 2024-2029 |
| INV-04 | 06-04, 06-09, 06-12 | SATISFIED | Schuldenstand 7,71 Mio. / 656 EUR (Vorjahr) und Reihe 2024-2029 |
| RAT-01 | 06-02, 06-04, 06-10, 06-12 | SATISFIED | Bindungsgrad-Balken + Produkte je Kategorie |
| RAT-02 | 06-07, 06-10, 06-12 | SATISFIED | `NichtBeeinflussbarBlock` |
| RAT-03 | 06-01, 06-07, 06-12 | SATISFIED | Einzelzuschüsse (Kita-Träger, KJW, OGS, Vereine, VHS, Sport, Musikschule) |
| RAT-04 | 06-04, 06-10, 06-12 | SATISFIED | `bindungsgrad_selbstauskunft`-Callout |
| STEL-01 | 06-02, 06-11, 06-12 | SATISFIED | drei Kacheln 2026/2025/besetzt |
| STEL-02 | 06-04, 06-11, 06-12 | SATISFIED | je Bereich und je Gruppe |
| STEL-03 | 06-11, 06-12 | SATISFIED | Personalaufwand je Bereich neben den Stellen |
| UI-04 | 06-03, 06-04, 06-07, 06-12 | SATISFIED | Hinweisbox auf drei Seiten |

Alle 15 vom Phasenauftrag genannten IDs kommen in den PLAN-Frontmattern vor und sind in REQUIREMENTS.md definiert. Keine verwaisten Phase-6-Anforderungen (REQUIREMENTS.md ordnet genau diese 15 IDs Phase 6 zu). Hinweis: Die Checkboxen und die Traceability-Tabelle in REQUIREMENTS.md stehen noch auf `Pending`; das Abhaken ist Orchestrator-Aufgabe nach bestandener Verifikation.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `app/src/pages/EntwicklungPage.vue` | ca. 77-82 | Erklärtext reproduziert die angezeigte Zahl nicht (CR-01) | BLOCKER (Gap) | Verstößt gegen Core Value (jede Zahl ableitbar) für das Kernjahr 2026 |
| `app/src/components/MenueGruppe.vue` | 34-50 | `positioniere()` misst mit veraltetem Versatz (WR-01) | WARNING | Liste kann beim erneuten Öffnen am Fensterrand abgeschnitten sein |
| `app/src/components/MassnahmenFilter.vue` | 23-25 | "1 Maßnahmen" erreichbar, in `aria-live` (WR-02) | WARNING | grammatikalisch falsch, Screenreader-Ansage |
| `app/src/pages/InvestitionenPage.vue` | 40-54 | `berechnet: false` hart codiert neben datengetriebenem Geschwister (WR-03) | WARNING | greift für andere Jahrgänge nicht |
| `app/src/lib/ruecklagen.ts` | 83-84 | Teilsumme als "Summe", fehlende Hälfte = 0 (WR-04) | WARNING | verletzt "nie 0 erfinden"; Daten lösen es heute nicht aus |
| `app/src/lib/stellen.ts` | 166 | `zeile.personen ?? 0` (WR-05) | WARNING | gleiche Regel, heute nicht ausgelöst |
| diverse | | IN-01 bis IN-08 | INFO | siehe 06-REVIEW.md; alle offen, nicht zielrelevant |

Schuldenmarker (TBD/FIXME/XXX/TODO/HACK): keine gefunden. `v-html`: nicht verwendet.

### Human Verification Required

Siehe Frontmatter `human_verification`. Der Walkthrough (06-12-SUMMARY, "Offene Human-Checks") bleibt komplett offen; die Sandbox hat keinen Browser, und es gibt keine Komponenten-Mount-Tests. Alle visuellen Aussagen (Layout 360/1280 px, Kontrast, Fokusreihenfolge, ECharts-Rendering, Aufklapper-Dimensionierung) sind daher nur über Typecheck, Build und lib-Tests gedeckt.

### Gaps Summary

Das Phasenziel ist in Daten, Logik und Verdrahtung erreicht: Alle vier Seiten und die Hinweisbox existieren, sind geroutet und im Menü, nutzen echte Daten, und die Sollwerte aus den Erfolgskriterien (-3,56 Mio., 11,6 Mio., 7,7 Mio./656 EUR, 62,91/62,13/56,63 VZÄ) sowie PDF-Stichproben (S. 23, 47, 310) stimmen. Ein Gap bleibt: Die Fußnote unter der Rücklagen-Tabelle (CR-01) beschreibt die Berechnung des "Rückgangs im Jahr" unvollständig, sodass ein Leser 0,56 % statt der gezeigten (und im PDF gedruckten) 1,77 % erhält. Das ist eine kleine, klar umrissene Korrektur (ein Satzbestandteil plus Test), aber sie betrifft den Core Value der App und die Zahl für das Haushaltsjahr, um das es auf der Seite geht. Die fünf Warnungen (WR-01 bis WR-05) und die acht Infos sind offen und nicht blockierend; WR-01 und WR-02 sind für Nutzer sichtbar und sollten mit CR-01 zusammen behoben werden.

Empfehlung: Gap-Closure-Plan (`/gsd-plan-phase 6 --gaps`) für CR-01, optional gebündelt mit WR-01 bis WR-05, danach Re-Verifikation und Browser-Walkthrough.

---

_Verified: 2026-10-06_
_Verifier: Claude (gsd-verifier)_
