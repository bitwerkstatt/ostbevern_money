---
phase: 06-kontext-seiten
verified: 2026-10-06T14:00:00Z
status: human_needed
score: 5/5 must-haves verified
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
  - .planning/phases/06-kontext-seiten/06-13-PLAN.md
  - .planning/phases/06-kontext-seiten/06-13-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-14-PLAN.md
  - .planning/phases/06-kontext-seiten/06-14-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-15-PLAN.md
  - .planning/phases/06-kontext-seiten/06-15-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-16-PLAN.md
  - .planning/phases/06-kontext-seiten/06-16-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-17-PLAN.md
  - .planning/phases/06-kontext-seiten/06-17-SUMMARY.md
  - app/src/charts/format.ts
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MenueGruppe.vue
  - app/src/lib/bindungsgrad.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/menueVersatz.ts
  - app/src/lib/ruecklagen.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/RatEntscheidetPage.vue
  - app/src/pages/StellenplanPage.vue
covered_digest: "v2:sha256:8fc3e1af6c8141527d530a6b8ed368e15f2ff1904fc3843df2bf451c49d861e9"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "CR-01: Fußnote unter der Rücklagen-Tabelle nennt jetzt die Verrechnung der Bilanzierungshilfe (Formeltext aus ruecklagen.ts abgeleitet, Nachrechentest)"
  gaps_remaining: []
  regressions: []
behavior_unverified_items:
  - truth: "Kopfmenü-Gruppe 'Mehr wissen' hält die geöffnete Liste bei jedem Öffnen und nach Resize im Fenster (MenueGruppe.positioniere, Plan 06-14)"
    test: "Bei 360-1024 px Breite 'Mehr wissen' öffnen, schließen, erneut öffnen; Fenster verkleinern und vergrößern, während die Liste offen ist"
    expected: "Die Liste bleibt jedes Mal vollständig im Viewport (Abstand zum Rand = Rand aus max-width)"
    why_human: "Die reine Funktion listenVersatz() ist per Test abgedeckt (Zweitöffnen, Resize, Fixpunkt). Die Integration in MenueGruppe.vue (liest element.style.left, schreibt versatz.value, Vue-Update vor der nächsten Messung) ist nur per Quelltext-Test festgenagelt; es gibt keinen DOM-/Mount-Test und keinen Browser in der Sandbox."
human_verification:
  - test: "Rücklagen-Fußnote auf /entwicklung lesen und mit PDF S. 311 nachrechnen (Entscheidung zum Restpunkt WR-01 des Reviews)"
    expected: "Mit Fehlbetrag 2.353.506 minus Ausgleichsrücklage 2.132.213 = 221.293, plus Betrag der Verrechnung 476.327 = 697.620, geteilt durch 39.522.991 = 1,77 %. Die Fußnote sagt 'zuzüglich der Verrechnung' ohne Vorzeichenhinweis; der gedruckte Wert auf S. 311 ist -476.327. Bitte entscheiden: ausreichend (Beträge-Lesart, wie bei 'Fehlbetrag') oder Vorzeichen-Zusatz gewünscht (Einzeiler in rueckgangFormelText())."
    why_human: "Ob eine Bürgerin oder ein Bürger den Text ohne Raten richtig anwendet, ist ein Verständlichkeitsurteil, kein programmatisch prüfbarer Befund."
  - test: "End-of-Phase-Walkthrough aller vier Seiten bei 1280 px und 360 px, nur Maus und Tastatur (vollständige Liste in 06-12-SUMMARY.md 'Offene Human-Checks', ergänzt um die Punkte aus 06-17-PLAN)"
    expected: "Kein horizontales Seiten-Scrollen bei 360 px; zweizeilige Achsen (Ist/Ansatz/Planung) lesbar; Direktbeschriftung und 'Defizit 3,56 Mio. EUR' haben Platz; Filter nur per Tastatur bedienbar; '/investitionen?pb=04' meldet '1 Maßnahme · zusammen …'; Aufklapper 'Produkte hinter dem Balken' zeigen korrekt dimensionierte Diagramme; Stellen-Diagramme fluchten bei 1280 px und stapeln bei 360 px"
    why_human: "Sandbox ohne Browser; Layout, Kontrast, Fokusfluss und ECharts-Rendering sind nicht programmatisch prüfbar. Es existiert kein Komponenten-Mount-Test (nur lib-Tests)."
  - test: "Menü 'Mehr wissen': öffnen, Escape (Fokus zurück an den Schalter), Klick außen, Enter/Leertaste, aktiver Zustand bei aktiver Unterseite; bei 360 px Drawer-Gruppe; erneutes Öffnen und Resize (siehe behavior_unverified_items)"
    expected: "Wie in 06-02-SUMMARY beschrieben; Liste immer im Viewport"
    why_human: "Interaktion, Fokusverhalten und Layout"
---

# Phase 6: Kontext-Seiten Verification Report

**Phase Goal:** Die App ordnet den Haushalt ein: Entwicklung bis 2029, Investitionen und Schulden, Gestaltungsspielraum des Rats, Personal und was außerhalb des Kernhaushalts liegt.
**Verified:** 2026-10-06
**Status:** human_needed
**Re-verification:** Ja, nach Gap Closure (Pläne 06-13 bis 06-17)

Ausgangsannahme war, dass das Phasenziel nicht erreicht ist. Geprüft wurde gegen den Quellcode, die eingecheckten Daten, das Quell-PDF (S. 23, 311) und frisch ausgeführte Läufe, nicht gegen die SUMMARYs. Items, die im ersten Durchgang bestanden, wurden per Regressionsprüfung (Volltest, Schlüsselwerte) bestätigt; CR-01 wurde vollständig neu geprüft.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | `/entwicklung`: Erträge, Aufwendungen, Jahresergebnis 2024-2029 mit unterscheidbarem Ist/Ansatz/Planung (Defizit 2029 -3,56 Mio.), Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen, Rücklagen mit Angabe, wie lange das Polster reicht | VERIFIED (mit offenem WARNING WR-01, siehe unten) | Regression: `abbau(2029)` = 3.557.700 = Jahresergebnis 2029 (-3.557.700, PDF S. 23 und S. 311). Rückgang aus `rueckgang()` 2026-2029: 1,765 / 4,231 / 4,730 / 10,043 % = S. 23 des PDFs (-1,77 / -4,23 / -10,04 v. H., per pdfplumber bestätigt). `ausgleichsruecklageAufgebrauchtJahr()` = 2026 (Ausgleichsrücklage ab 2027 = 0). **CR-01 geschlossen:** Die gerenderte Fußnote lautet jetzt: "Quelle: Eigenkapitalübersicht, PDF-Seite 311. Der Rückgang im Jahr ist berechnet wie im Vorbericht (PDF-Seite 23): der Fehlbetrag des Jahres, soweit die Ausgleichsrücklage ihn nicht deckt, zuzüglich der Verrechnung aus der Zeile „Einmalige Verrechnung Bilanzierungshilfe“, geteilt durch die allgemeine Rücklage zu Jahresbeginn." (Ausgabe von `rueckgangFormelText()` auf den echten Daten). Jeder Term der Rechnung ist genannt; die Zeile heißt in den Daten und in der PDF-Tabelle S. 311 genau so. |
| 2 | `/investitionen`: Maßnahmen 2026-2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art; VE 11,6 Mio. mit Fälligkeiten; Finanzierung mit Kreditaufnahme/Tilgung; Schuldenstand gesamt und je Einwohner (7,7 Mio. / 656 EUR) | VERIFIED | Regression: `schuldenKennzahlen()` = 7.710.000 / 656 EUR (Ansatz 2025, S. 310 und 25), `berechnet: false`. Neu: `schuldenKacheln()` liefert beide Kacheln ("7,71 Mio. €", "656 €") mit datengetriebenem `berechnet`-Flag; `InvestitionenPage.vue` nutzt `schuldenKacheln()`. `ergebnisText()` liefert "1 Maßnahme" im Singular. Volltest deckt Filter, VE (11.600.000) und Finanzierung. |
| 3 | `/rat-entscheidet`: Zuschussbedarf 2026 nach Bindungsgrad gestapelt mit Produkten je Kategorie; Block "Was der Rat nicht beeinflussen kann"; Einzelzuschüsse; Hinweis Selbstauskunft | VERIFIED | Regression: `baueBindungsgrad()` liefert die Segmente pflichtig (29 Produkte, 6.358.143 EUR), teils, freiwillig; Seiten, `NichtBeeinflussbarBlock`, `ZuschussListe` und `bindungsgrad_selbstauskunft`-Callout unverändert vorhanden; `produkteText()`/`segmentZusammenfassung()` neu (Singular), von `ProduktBalkenListe.vue` und `BindungsgradBalken.vue` genutzt. |
| 4 | `/stellenplan`: Stellen 2026 vs. 2025 vs. besetzt 30.06.2025, Verteilung nach Aufgabenbereich und Gruppe, daneben Personalaufwand je Aufgabenbereich (TP Z. 11) | VERIFIED | Regression: `stellenSummen()` = 6291 / 6213 / 5663 (Hundertstel-VZÄ = 62,91 / 62,13 / 56,63), Stichtag 2025-06-30, Seiten 284-286. `nachwuchs()` = 5 / 6 (S. 290) unverändert; fehlende Personenzahl ergibt jetzt `null` statt 0. |
| 5 | Hinweis "Was nicht im Haushalt steht" erklärt BBO (Hallenbad) und TEO AöR (Abwasser) | VERIFIED | Unverändert seit der ersten Verifikation; die Gap-Pläne haben `HinweisNichtImHaushalt`, `texte.json` und die Seiten /ausgaben, /einnahmen, /rat-entscheidet nicht berührt (siehe Diff unten). |

**Score:** 5/5 Wahrheiten verifiziert, 1 davon verhaltensabhängig und noch nicht im Browser beobachtet (Menüposition, `behavior_unverified: 1`).

### Urteil zu CR-01 und zum neuen Review-Warning WR-01 (Vorzeichen)

**CR-01 ist geschlossen.** Der ursprüngliche Mangel war, dass die Fußnote den Summanden "Verrechnung der Bilanzierungshilfe" gar nicht nannte; ein Leser kam mit der Fußnote zwingend auf 0,56 % (221.293 / 39.522.991) statt der gezeigten und auf PDF S. 23 gedruckten 1,77 %. Das ist behoben:

- Der Term steht in der gerenderten Fußnote, mit dem gedruckten Zeilennamen, abgeleitet aus denselben Konstanten wie `abbau()` (`rueckgangFormelText()` neben `abbau()` in `app/src/lib/ruecklagen.ts`; `EntwicklungPage.vue` baut `tabellenFussnote` aus diesem Text, keine handgetippte Zahl).
- Ein Nachrechentest gleicht die Fußnotenterme mit `rueckgang()` auf 12 Stellen ab und hält fest, dass ohne den Verrechnungsterm 0,56 % herauskäme.
- Die Zahl selbst blieb unverändert und stimmt mit dem PDF überein (1,77 / 4,23 / 4,73 / 10,04 %).

**WR-01 des neuen Reviews (Vorzeichen) lässt die Wahrheit nicht scheitern, bleibt aber als offenes WARNING bestehen.** Begründung:

- Die Fußnote argumentiert durchgängig in Beträgen: "der Fehlbetrag des Jahres" ist ein positiver Betrag, obwohl S. 311 das Jahresergebnis als -2.353.505,75 druckt. Wer diese Betragslesart auf "Fehlbetrag" anwendet, wendet sie natürlicherweise auch auf "die Verrechnung" an (476.327 erhöht den Abbau) und erhält 221.293 + 476.327 = 697.620, also 1,77 %. S. 23 des PDFs verwendet dieselbe Wendung ("inkl. der Verrechnung der durch die COVID 19-Pandemie ... entstandenen Belastungen").
- Wörtlich mit dem gedruckten negativen Wert (-476.327) addiert, ergäbe sich -255.034, also ein negativer "Abbau". Das ist offensichtlich unsinnig und weist den Leser auf die Vorzeichenumkehr hin, ist aber kein sauberes, ratefreies Nachrechnen.
- Die Tabelle zeigt weder Jahresergebnis noch Verrechnung; der Leser muss beide aus PDF S. 311 holen. Der Review-Befund ist also sachlich zutreffend: die Fußnote ist an dieser Stelle uneindeutig, nicht falsch.
- Damit ist die Kernforderung "Die Zahl ist ableitbar und der Erklärtext nennt jeden Term" erfüllt; die Restforderung "ohne Interpretationsspielraum" nicht vollständig. Das ist ein Textpolitur-Punkt (Einzeiler: z. B. "vermehrt um den Betrag der Verrechnung ... (dort negativ gebucht)"), kein Blocker, weil weder Zahl noch Datenlage falsch sind und der erste Fehlerfall (Term fehlt) nicht mehr besteht. Die Entscheidung, ob das ausreicht, ist als Human-Item 1 aufgeführt. Ich werte ihn nicht als gaps_found, weil die Wahrheit nach Betragslesart und PDF-Gegenprobe reproduzierbar ist.

### Gap-Closure-Pläne 06-13 bis 06-17 (Wiring gegen Code geprüft)

| Plan | Befund | Status | Nachweis im Code |
| ---- | ------ | ------ | ---------------- |
| 06-13 | CR-01, WR-04 | VERIFIED (CR-01 mit Warning, s. o.) | `rueckgangFormelText()` in `ruecklagen.ts`, von `EntwicklungPage.vue` genutzt; `baueRuecklagen()` liefert `summe: null` bei fehlender Rücklage |
| 06-14 | WR-01 (Menü) | Reine Funktion VERIFIED; Integration PRESENT_BEHAVIOR_UNVERIFIED | `menueVersatz.ts` (`listenVersatz`, `randAusMaximalbreite`), `MenueGruppe.positioniere()` liest `element.style.left`, ruft `listenVersatz` auf, setzt `versatz.value`; Template bindet `:style="{ left: versatz + 'px' }"` (Zeile 164); Öffnen (nach `nextTick`) und Resize gehen durch `positioniere()`. Statische Analyse: Ergebnis ist unabhängig vom bereits angewandten Versatz, der Fehler "Messung mit veraltetem Versatz" ist beseitigt. |
| 06-15 | WR-02 (Singular) | VERIFIED | `anzahlText()` in `charts/format.ts`; `ergebnisText()`, `produkteText()`, `segmentZusammenfassung()` wiederum genutzt in `MassnahmenFilter.vue`, `ProduktBalkenListe.vue`, `BindungsgradBalken.vue`; `FormatKuerzel`/`formatiere()` unverändert |
| 06-16 | WR-03, WR-05 | VERIFIED | `schuldenKacheln()` (liefert für 2026: beide Kacheln `berechnet: false`), von `InvestitionenPage.vue` genutzt; `personen()` in `stellen.ts` gibt `null` statt 0 |
| 06-17 | Gate und Ledger | VERIFIED | `git diff d1b8e64..HEAD -- pipeline daten app/src/data` ist leer (nur App-Änderungen); Ledger `06-REVIEW-DISPOSITION.md` stimmt mit Code überein |

### Required Artifacts

| Artifact | Status | Details |
| -------- | ------ | ------- |
| `app/src/pages/{Entwicklung,Investitionen,RatEntscheidet,Stellenplan}Page.vue` | VERIFIED | Unverändert geroutet, im Menü, mit echten Daten |
| `app/src/lib/ruecklagen.ts` (`rueckgangFormelText`) | VERIFIED | substanziell, genutzt, Daten fließen (Ausgabe oben) |
| `app/src/lib/menueVersatz.ts`, `MenueGruppe.vue` | VERIFIED (Integration: Human) | s. o. |
| `app/src/charts/format.ts` (`anzahlText`) | VERIFIED | in drei Modulen genutzt |
| `app/src/lib/schulden.ts` (`schuldenKacheln`), `stellen.ts` | VERIFIED | s. o. |
| `app/src/data/*.json`, `daten/`, `pipeline/` | VERIFIED | seit Verifikationscommit d1b8e64 unverändert; Pipeline-Tests grün |

### Key Link Verification

| From | To | Status | Details |
| ---- | -- | ------ | ------- |
| `EntwicklungPage.vue` `tabellenFussnote` | `rueckgangFormelText()` | WIRED | Fußnote enthält den Satzteil (Laufzeitausgabe) |
| `rueckgangFormelText()` | `abbau()` | WIRED | gleiche Konstanten `VERRECHNUNG`, `AUSGLEICH`, `ERGEBNIS`, `ALLGEMEINE` |
| `MenueGruppe.vue` | `menueVersatz.ts` | WIRED | `listenVersatz(...)` in `positioniere()` |
| `MassnahmenFilter.vue` | `ergebnisText()` | WIRED | |
| `InvestitionenPage.vue` | `schuldenKacheln()` | WIRED | |
| `ProduktBalkenListe.vue`, `BindungsgradBalken.vue` | `bindungsgrad.ts` Anzahltexte | WIRED | |
| Menü, Seiten, Hinweisbox, Pipeline-Texte | wie in der Erstverifikation | WIRED (Regression) | keine Änderung durch Gap-Pläne |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Rücklagen-Fußnote | Verrechnungsname, Formelterme | `haushalt.eigenkapital.posten` (S. 311) | Ja: "Einmalige Verrechnung Bilanzierungshilfe", Wert -476.327 in 2026 | FLOWING |
| Rückgang-Tabelle und -Diagramm | `rueckgang(i)` | `eigenkapital` aus `haushalt.json` | Ja (697.620 / 1.642.528 / 1.758.827 / 3.557.700) | FLOWING |
| Schuldenkacheln | `kennzahlen.berechnet`, `gesamt`, `proKopf` | `investitionen.json`, Einwohner S. 25 | Ja (7,71 Mio. / 656) | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Volle App-Testsuite | `npx vitest run` in Scratch-Kopie von `app/` (node_modules per Symlink, nichts im Repo) | 37 Dateien, 1576 Tests bestanden | PASS |
| App-Typprüfung | `vue-tsc --build` (Scratch) | Exit 0 | PASS |
| Lint / Format / Build | `eslint .`, `prettier --check`, `vite build` (Scratch) | keine Fehler, Build erzeugt (nur Chunk-Größen-Hinweis) | PASS |
| Pipeline-Testsuite | `.venv/bin/python -m pytest -q -p no:cacheprovider` | 546 passed | PASS |
| Fußnotentext und Rückgangswerte auf echten Daten | Scratch-Test über `rueckgangFormelText()`, `abbau()`, `rueckgang()` | Fußnote nennt die Verrechnung; 697.620 / 0,01765 für 2026 | PASS |
| PDF-Gegenprobe | pdfplumber S. 23 und S. 311 | S. 23: 2026 -1,77; 2027 -4,23; 2029 -10,04 v. H. (Fußnote 2: "inkl. der Verrechnung"); S. 311: Verrechnung, Ausgleichsrücklage, Jahresergebnis wie in den Daten | PASS |
| Schlüsselwerte SC2/SC4 | Scratch-Lauf `schuldenKennzahlen`, `schuldenKacheln`, `stellenSummen`, `nachwuchs`, `baueBindungsgrad` | 7.710.000 / 656; 6291 / 6213 / 5663; 5 / 6; Segment pflichtig 29 Produkte | PASS |
| Gap-Pläne änderten nur die App | `git diff d1b8e64..HEAD -- pipeline daten app/src/data` | leer | PASS |

Step 7c (Probes): keine `probe-*.sh` in dieser Phase deklariert; übersprungen.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
| ----------- | -------------- | ----------- | ------ | -------- |
| ENTW-01 | 06-02, 06-05, 06-12, 06-14 | Erträge, Aufwendungen, Jahresergebnis 2024-2029; Ist/Ansatz/Planung unterscheidbar | SATISFIED | Linien, Jahresergebnis-Säulen, Wertart-Etikett; Defizit 2029 = -3.557.700 |
| ENTW-02 | 06-05, 06-12 | Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen | SATISFIED | fünf Posten-Reihen (Regression, Volltest) |
| ENTW-03 | 06-01, 06-04, 06-08, 06-12, 06-13, 06-17 | Ausgleichsrücklage, allgemeine Rücklage, wie lange das Polster reicht | SATISFIED (Warning WR-01 Vorzeichenwortlaut) | Rücklagen, Rückgang = PDF S. 23, Fußnote nennt jetzt alle Terme; Polster-Aussage aus Daten |
| INV-01 | 06-02, 06-06, 06-12, 06-14, 06-15, 06-17 | Maßnahmen als Liste und Balken, filterbar | SATISFIED | Filter mit URL-Zustand, Ergebniszeile mit Singular |
| INV-02 | 06-09, 06-12 | VE 11,6 Mio. mit Fälligkeiten | SATISFIED | Regression, Volltest |
| INV-03 | 06-09, 06-12 | Finanzierung, Kreditaufnahme/Tilgung 2024-2029 | SATISFIED | Regression, Volltest |
| INV-04 | 06-04, 06-09, 06-12, 06-16, 06-17 | Schuldenstand gesamt und je Einwohner | SATISFIED | 7,71 Mio. / 656 EUR, beide Kacheln über `schuldenKacheln()` |
| RAT-01 | 06-02, 06-04, 06-10, 06-12, 06-15, 06-17 | Zuschussbedarf nach Bindungsgrad, gestapelt, Produkte je Kategorie | SATISFIED | Segmente 29/15/15 Produkte, Summe 13.286.440 |
| RAT-02 | 06-07, 06-10, 06-12 | Block "Was der Rat nicht beeinflussen kann" | SATISFIED | `NichtBeeinflussbarBlock` (Regression) |
| RAT-03 | 06-01, 06-07, 06-12 | Einzelzuschüsse aus dem Vorbericht | SATISFIED | `ZuschussListe`, Pipeline-Regel 5 grün (pytest 546) |
| RAT-04 | 06-04, 06-10, 06-12 | Hinweis Selbstauskunft | SATISFIED | `bindungsgrad_selbstauskunft` |
| STEL-01 | 06-02, 06-11, 06-12, 06-14, 06-16, 06-17 | Stellen 2026 vs. 2025 vs. besetzt 30.06.2025 | SATISFIED | 62,91 / 62,13 / 56,63 VZÄ |
| STEL-02 | 06-04, 06-11, 06-12, 06-16, 06-17 | Verteilung nach Aufgabenbereich und Gruppe | SATISFIED | `stellenNachBereich`, `stellenNachGruppe` |
| STEL-03 | 06-11, 06-12 | Personalaufwand je Aufgabenbereich (TP Z. 11) | SATISFIED | `StellenNachBereich` |
| UI-04 | 06-03, 06-04, 06-07, 06-12 | Hinweis "Was nicht im Haushalt steht" (BBO, TEO AöR) | SATISFIED | `HinweisNichtImHaushalt` auf drei Seiten |

Alle 15 Phasen-IDs kommen in den PLAN-Frontmattern vor, sind in REQUIREMENTS.md definiert und dort Phase 6 zugeordnet (Zeilen 93-128, Traceability 235-255). Keine verwaisten Anforderungen. Hinweis: Checkboxen und Traceability-Status in REQUIREMENTS.md stehen weiterhin auf `Pending`; Abhaken ist Orchestrator-Aufgabe nach der Freigabe.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `app/src/lib/ruecklagen.ts` | 146-153 (Review) | "zuzüglich der Verrechnung" ohne Vorzeichenhinweis; Doc-Kommentare und Testkommentar sagen "plus" für `- verrechnung` | WARNING (WR-01 Review, offen) | Wortlaut uneindeutig, Zahl und Daten korrekt; siehe Urteil oben |
| `app/src/components/MenueGruppe.vue` | 34-56 | Integration (DOM) ohne Mount-Test | WARNING (behavior-unverified) | Verhalten im Browser unbeobachtet |
| diverse | | IN-01 bis IN-09 | INFO | laut 06-REVIEW.md bewusst offen, nicht zielrelevant |

Schuldenmarker (TBD/FIXME/XXX/TODO/HACK) in den geänderten Dateien: keine. `v-html`: nicht verwendet.

### Deferred Items

Keine. Phase 7 (Quellenbelege, Barrierefreiheit, Mobilansicht, Smoke-Test, Deployment) deckt die offenen Human-Items nicht explizit ab; sie bleiben Teil dieser Phase (Walkthrough).

### Human Verification Required

Siehe Frontmatter `human_verification` (3 Items) und `behavior_unverified_items` (1 Item).

1. **Rücklagen-Fußnote, Vorzeichenwortlaut:** Entscheidung, ob "zuzüglich der Verrechnung" (Betragslesart) genügt oder ein Vorzeichenhinweis ergänzt wird. Test: Fußnote auf /entwicklung lesen, mit PDF S. 311 nachrechnen. Erwartung: 221.293 + 476.327 = 697.620 / 39.522.991 = 1,77 %.
2. **End-of-Phase-Walkthrough** bei 1280 px und 360 px (Layout, Kontrast, Fokus, Diagramme, `?pb=04` meldet "1 Maßnahme").
3. **Menü "Mehr wissen"**: erneutes Öffnen und Resize bleiben im Viewport.

### Gaps Summary

Das Phasenziel ist erreicht: Alle vier Seiten und die Hinweisbox existieren, sind geroutet, nutzen echte Daten und reproduzieren die Sollwerte (-3,56 Mio., 11,6 Mio., 7,7 Mio./656 EUR, 62,91/62,13/56,63 VZÄ) und die PDF-Gegenproben (S. 23, 311). Das einzige Gap der Erstverifikation (CR-01, Fußnote ohne Verrechnungsterm) ist geschlossen. Die Gap-Pläne 06-13 bis 06-17 sind im Code verdrahtet; Volltest (1576 App-Tests, 546 Pipeline-Tests), Typprüfung, Lint, Format und Build sind frisch grün. Es bleiben nur Items, die ein Mensch im Browser bzw. per Leseurteil entscheiden muss (Menüposition, Walkthrough, Vorzeichenwortlaut der Fußnote), daher `human_needed` statt `passed`. Kein Blocker, keine Gap-Closure-Pläne nötig.

---

_Verified: 2026-10-06_
_Verifier: Claude (gsd-verifier)_
