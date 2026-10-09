---
phase: 06-kontext-seiten
verified: 2026-10-09T06:29:51Z
status: passed
score: 6/6 must-haves verified
covered_files:
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-01-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-01-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-02-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-02-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-03-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-03-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-04-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-04-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-05-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-05-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-06-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-06-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-07-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-07-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-08-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-08-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-09-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-09-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-10-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-10-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-11-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-11-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-12-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-12-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-13-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-13-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-14-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-14-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-15-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-15-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-16-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-16-SUMMARY.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-17-PLAN.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-17-SUMMARY.md
  - app/e2e/interaktion.spec.ts
  - app/e2e/kacheln.spec.ts
  - app/src/charts/format.ts
  - app/src/components/EntwicklungsDiagramm.vue
  - app/src/components/HinweisNichtImHaushalt.vue
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MassnahmenListe.vue
  - app/src/components/MenueGruppe.vue
  - app/src/components/NichtBeeinflussbarBlock.vue
  - app/src/components/StellenNachBereich.vue
  - app/src/components/UeberschussListe.vue
  - app/src/components/ZuschussListe.vue
  - app/src/data/texte.json
  - app/src/lib/__tests__/hilfsfunktionen.test.ts
  - app/src/lib/__tests__/stiltokens.test.ts
  - app/src/lib/bindungsgrad.ts
  - app/src/lib/entwicklung.ts
  - app/src/lib/hilfsfunktionen.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/menue.ts
  - app/src/lib/menueVersatz.ts
  - app/src/lib/ruecklagen.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/lib/zuschuesse.ts
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/RatEntscheidetPage.vue
  - app/src/pages/StellenplanPage.vue
  - app/src/router/index.ts
covered_digest: "v3:sha256:89a7b89f6a2ea2cddb7d22ecdb2038cf1dd17b5338d09338baf97c4e5a1733c1"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "5/5 must-haves verified"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
  human_items_resolved:
    - "Rücklagen-Fußnote (WR-01 Vorzeichenwortlaut): UAT Test 1 pass, Beträge-Lesart akzeptiert (06-UAT.md; durch die UAT gelöst, nicht durch den Verifier)"
    - "End-of-Phase-Walkthrough 1280/360 px: UAT Test 2 pass (06-UAT.md; durch die UAT gelöst, nicht durch den Verifier)"
    - "Menü 'Mehr wissen' (erneutes Öffnen, Resize, Escape, Fokus): UAT Test 3 pass (06-UAT.md; durch die UAT gelöst, nicht durch den Verifier)"
deferred: []
advisory: []
behavior_unverified_items: []
---

# Phase 6: Kontext-Seiten Verification Report

**Phase Goal:** Die App ordnet den Haushalt ein: Entwicklung bis 2029, Investitionen und Schulden, Gestaltungsspielraum des Rats, Personal und was außerhalb des Kernhaushalts liegt.
**Verified:** 2026-10-09
**Status:** passed
**Re-verification:** Ja. Der Vorbericht vom 2026-10-06 (passed, „5/5 must-haves verified“) stammt aus der Zeit vor Phase 7 und Phase 8, die Phase-6-Code geändert haben. Dieser Bericht prüft alle Wahrheiten erneut gegen den heutigen Code.

## Warum diese Re-Verifikation (Phase 9, AUD-02)

Der Vorbericht trug den Digest der Fassung v2 und führte Pfade unter `.planning/phases/06-kontext-seiten/`. Die Phase liegt seit dem Meilenstein-Abschluss unter `.planning/milestones/v1.0-phases/06-kontext-seiten/`, und die Quelldateien haben sich nach dem Vorbericht geändert; `verification.status` meldete deshalb `stale` (09-BASISLAUF.md, Abschnitt „Verifikationsstatus vor der Re-Verifikation“). Der Prüfpunkt AUD-02 verlangt einen Bericht, der den Endstand beschreibt (D-13).

Verfahren: Die Re-Verifikation folgt dem Ablauf des gsd-verifier (Step 0 Re-Verifikationsmodus, Steps 3 bis 9, „Create VERIFICATION.md“). Der Ausführer kann das Subagent-Werkzeug nicht starten und wendet das Verfahren selbst an. Jede Wahrheit des Vorberichts und jedes ROADMAP-Erfolgskriterium wurde gegen den heutigen Code geprüft, nicht aus dem Vorbericht übernommen.

Code-Änderungen an den Phase-6-Dateien seit dem Vorbericht (`git log --since=2026-10-06T11:05:00Z` über die Implementierungsdateien des alten `covered_files`):

- Phase 7 (Veröffentlichung): `348040f`/`bc89a33` (07-04, Typografie- und Abstandstokens), `f2081c4` (07-06, „Quelle anzeigen“ an den Kacheln von Investitionen und Stellenplan), `face109`/`e2eebdb` (07-08, Quelle für Einzelzuschüsse, Maßnahmen und Stellen), `c899020` (07-13, gemeinsames Kachelraster `om-kachelraster`), `da9da3b` (Schulden-Tooltip zeigt fehlende Werte als `KEIN_WERT`).
- Phase 8 (Fixes und Triage), laut Ledger `06-REVIEW-DISPOSITION.md`: `dde7341` (08-02, rd.-Regel nur in `format.ts`), `1d4e359` (08-03, Kacheln „berechnet“ und Seiten je Kachel), `af0a3eb`/`470a149` (08-05, Zusammen-Zeile der Zuschüsse und Filtersumme mit Etikett), `4b45a07` (08-07, Begründungskommentare), `7f85070` (08-09, Key-Trenner, strikte Vergleiche), `656c73e`/`fad1da9`/`507d787` (08-10, gemeinsame Jahr-Helfer, `postenEintrag`, `anzahlText`), `487df23`/`31d0334`/`af2f80b` (08-11, `klickIndex`, `jahreListe`, `quellenZeile` in `hilfsfunktionen.ts`, Maßnahmenfilter einmal je Seite).
- Befund: Keine dieser Änderungen hat eine Wahrheit gebrochen. Die Abschnitte unten belegen das je Wahrheit mit dem heutigen Code.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | `/entwicklung` zeigt Erträge, Aufwendungen und Jahresergebnis 2024–2029 mit unterscheidbarem Ist, Ansatz und Planung (Defizit 2029 −3,56 Mio. €), Zeitreihen für Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal und Zinsen sowie Rücklagen mit der Angabe, wie lange das Polster reicht | VERIFIED | `EntwicklungPage.vue` Z. 93–117 (Erträge/Aufwendungen und Jahresergebnis), Z. 119–131 (fünf Posten aus `ENTWICKLUNG_POSTEN`, `lib/entwicklung.ts` Z. 185–215: kreisumlage, gewerbesteuer, schluesselzuweisung, personal, zinsen), Z. 133–165 (Rücklagen, Rückgang, Polster-Text). Ist/Ansatz/Planung getrennt über `haushalt.wertarten` in `EntwicklungsDiagramm.vue` Z. 21/64/119. Defizit 2029: `entwicklung.test.ts` Z. 120 (−3.557.700) und Z. 133 („Defizit 3,56 Mio. €“), grün. Rückgang 1,77 / 4,23 / 4,73 / 10,04 %: `ruecklagen.test.ts` Z. 169–176, grün; die Fußnote nennt alle Terme (`rueckgangFormelText()`, `ruecklagen.ts` Z. 139–146, CR-01 weiter geschlossen). Playwright: `smoke.spec.ts:138 Smoke /entwicklung › rendert ohne Konsolenmeldung…`, `inventar.spec.ts:39 Inventar /entwicklung`, `mobil.spec.ts:151 … Route /entwicklung` (09-BASISLAUF.md). |
| 2 | `/investitionen`: Maßnahmen 2026–2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art; Verpflichtungsermächtigungen 11,6 Mio. € mit Fälligkeiten; Finanzierung mit Kreditaufnahme und Tilgung; Schuldenstand gesamt und je Einwohner (≈ 7,7 Mio. € / ≈ 656 €) | VERIFIED | `InvestitionenPage.vue` Z. 95–111 (Filter und `MassnahmenListe`), Z. 112–125 (VE mit `VeFaelligkeiten`), Z. 126–139 (zwei `FinanzierungsDiagramm`-Karten), Z. 140–146 (Schuldenstand), Kacheln Z. 41–55. Der Filter hat Aufgabenbereich und die vier Arten Bau, Grundstücke, Fahrzeuge und Ausstattung, Sonstige (`investitionen.ts` Z. 27–32; `MassnahmenFilter.vue` Z. 70–108). Der Filterzustand entsteht einmal je Seite (`InvestitionenPage.vue` Z. 70, 08-11 `af2f80b`). VE 11.600.000: `finanzierung.test.ts` Z. 502; 7.710.000 € und 656 € ohne „berechnet“: `schulden.test.ts` Z. 317–328; Singular „1 Maßnahme“ aus `ergebnisText()` (`investitionen.ts` Z. 204–207). Playwright: `interaktion.spec.ts:453 Maßnahmenfilter auf /investitionen …`, `interaktion.spec.ts:345 Tabellenrahmen bei 360 px … /investitionen`, `smoke.spec.ts:138 Smoke /investitionen`, `kacheln.spec.ts:465 … Kacheln und Seitenbreite: /investitionen`. |
| 3 | `/rat-entscheidet`: Zuschussbedarf 2026 nach Bindungsgrad als gestapelter Balken mit den Produkten je Kategorie; Block „Was der Rat nicht beeinflussen kann“; Einzelzuschüsse aus dem Vorbericht; Hinweis, dass der Bindungsgrad eine Selbstauskunft ist | VERIFIED | `RatEntscheidetPage.vue` Z. 42–43 (`BindungsgradBalken`), Z. 53–57 (Callout mit `ErklaerText bindungsgrad_selbstauskunft`), Z. 59–76 (Produkte je Segment), Z. 77–79 (`UeberschussListe`, `NichtBeeinflussbarBlock`, `ZuschussListe`), Z. 80 (`HinweisNichtImHaushalt variante="kurz"`). Segmente 29 / 15 / 15 Produkte: `bindungsgrad.test.ts` Z. 242–243, grün. Die Zusammen-Zeile der Zuschüsse trägt „berechnet“ nur bei eigener Summe (`ZuschussListe.vue` Z. 108–113, 190–197; `zuschuesse.test.ts` Z. 87–126). Playwright: `smoke.spec.ts:138 Smoke /rat-entscheidet`, `inventar.spec.ts:39 Inventar /rat-entscheidet`, `kacheln.spec.ts:465 … /rat-entscheidet`, `mobil.spec.ts:151 … Route /rat-entscheidet`. |
| 4 | `/stellenplan`: Stellen 2026 im Vergleich zu 2025 und zu den besetzten Stellen am 30.06.2025, Verteilung nach Aufgabenbereich und Entgelt- bzw. Besoldungsgruppe, daneben der Personalaufwand je Aufgabenbereich | VERIFIED | `StellenplanPage.vue` Z. 90–140 (drei Kacheln: Haushaltsjahr, Vorjahr, besetzt mit Stichtag; jede „berechnet“ samt Herleitung und eigenen Seiten, 08-03 `1d4e359`), Z. 206–215 (`StellenNachBereich`: Stellen und Personalaufwand je Aufgabenbereich, `stellen.ts` Z. 239–296), Z. 217–237 (`StellenNachGruppe` je Teil). Werte 62,91 / 62,13 / 56,63 VZÄ: `stellen.test.ts` Z. 223–227, Σ Personalaufwand 5.204.054 € Z. 475–476, grün. Playwright: `quelle.spec.ts:294 … eine Stellenplan-Zeile öffnet eine Querformatseite …`, `smoke.spec.ts:138 Smoke /stellenplan`, `kacheln.spec.ts:465 … /stellenplan`, `mobil.spec.ts:311 … eine Querformatseite scrollt nur im eigenen Rahmen`. |
| 5 | Ein Hinweis „Was nicht im Haushalt steht“ erklärt BBO (Hallenbad) und TEO AöR (Abwasser) | VERIFIED | `HinweisNichtImHaushalt.vue` Z. 19–27 (Leitsätze mit Hallenbad/BBO und Abwasser/TEO AöR) und Z. 50 („Was sind BBO und TEO?“); eingebunden in `EinnahmenPage.vue` Z. 423, `AusgabenPage.vue` Z. 379 und `RatEntscheidetPage.vue` Z. 80. Langtext `texte.json` Z. 104–112 und Z. 540 mit Beträgen als Platzhalter aus den Daten. `hinweis.test.ts` grün. |
| 6 | Das Menü „Mehr wissen“ (Wahrheit des Vorberichts, verhaltensabhängig): Die Liste bleibt beim erneuten Öffnen und nach einem Resize im Viewport; Escape, Klick außen, Tab und Routenwechsel schließen sie; die vier Seiten sind darüber erreichbar | VERIFIED | `menue.ts` Z. 38–41 (Einträge Entwicklung, Investitionen, Rat entscheidet, Stellenplan), `router/index.ts` Z. 81–100, `menueVersatz.ts` (`listenVersatz`) mit `menueVersatz.test.ts` grün. Verhalten im Browser durch Playwright belegt, das heute läuft und nicht mehr nur durch UAT: `interaktion.spec.ts:179 … die geöffnete Liste bleibt nach dem Öffnen und nach einem Resize im Fenster, style.left passt zur Lage`, `:87 Escape schließt die offene Liste …`, `:135 ein Klick außerhalb schließt die Liste`, `:145 ein Routenwechsel schließt die Liste`, `:102 Tab läuft ohne Fokusfalle …` (09-BASISLAUF.md, Projekt `ci`). Zusätzlich UAT Test 3 pass. |

**Score:** 6/6 Wahrheiten verifiziert, 0 present-but-behavior-unverified. Die Zahl 6 enthält die verhaltensabhängige Wahrheit des Vorberichts (Menü) als eigene Zeile; die fünf ROADMAP-Kriterien sind die Wahrheiten 1 bis 5.

### Required Artifacts

| Artifact | Status | Details |
| -------- | ------ | ------- |
| `app/src/pages/{Entwicklung,Investitionen,RatEntscheidet,Stellenplan}Page.vue` | VERIFIED | geroutet (`router/index.ts` Z. 81–100), mit echten Daten aus `@/data/daten`; keine Platzhalter |
| `app/src/components/{ZuschussListe,UeberschussListe,NichtBeeinflussbarBlock,MassnahmenFilter,MassnahmenListe,MenueGruppe,HinweisNichtImHaushalt,StellenNachBereich}.vue` | VERIFIED | substanziell und von den Seiten eingebunden; h2/h3 nutzen `--wa-font-size-l` |
| `app/src/lib/{ruecklagen,schulden,stellen,bindungsgrad,investitionen,menueVersatz,entwicklung,zuschuesse}.ts`, `charts/format.ts`, `lib/hilfsfunktionen.ts` | VERIFIED | substanziell, genutzt; Phase 8 hat Helfer verschoben (`klickIndex`, `jahreListe`, `quellenZeile` in `hilfsfunktionen.ts`), die Aufrufer wurden mitgeführt |
| `app/src/lib/__tests__/stiltokens.test.ts` | VERIFIED | Typografie-Guard grün |

`gsd-tools query verify.artifacts` über alle 17 PLANs: 16 von 17 bestehen vollständig. 06-17 nennt als Artefakt `.planning/phases/06-kontext-seiten/06-REVIEW-DISPOSITION.md`; die Datei liegt seit dem Archivieren unter `.planning/milestones/v1.0-phases/06-kontext-seiten/06-REVIEW-DISPOSITION.md` (vorhanden). Das ist eine reine Pfadänderung, keine Regression.

### Key Link Verification

`gsd-tools query verify.key-links` über alle PLANs: Die Links mit Dateipfaden sind alle WIRED. Vier Links sind in den PLANs mit Funktionsnamen statt Pfad beschrieben (06-13, 06-15, 06-16) und für das Werkzeug nicht auswertbar; sie wurden von Hand geprüft:

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `rueckgangFormelText()` | `abbau()` | Fußnote beschreibt die Rechnung | WIRED | `ruecklagen.ts` Z. 96 (`abbau`), Z. 120 (`rueckgang` ruft `abbau`), Z. 133–146 (Text) |
| `investitionen.ts`, `bindungsgrad.ts` | `charts/format.ts` | `anzahlText` (Singular/Plural) | WIRED | `investitionen.ts` Z. 14/206, `bindungsgrad.ts` Z. 7/130, `format.ts` Z. 87 |
| `schuldenKacheln()` | `investitionen.schuldenstand.berechnet` | Etikett folgt dem Datenfeld | WIRED | `schulden.ts` Z. 9–13, 62, 79, 192–225 |
| `StellenplanPage.vue` `nachwuchsSatz` | `stellen.ts` `nachwuchs()` | Personenzahlen | WIRED | `StellenplanPage.vue` Z. 33/144–157, `stellen.ts` Z. 201 |

### Behavioral Spot-Checks

Eigene Prüfungen dieses Plans (nur lesend; Scratch-Kopie von `app/` mit eigenem `npm ci`, Linux):

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Phase-6-Testdateien | `npx vitest run src/lib/__tests__/{ruecklagen,schulden,stellen,bindungsgrad,investitionen,menueVersatz,entwicklung,zuschuesse,stiltokens,quelle-kontext,hinweis,finanzierung}.test.ts` | 12 Dateien, 600 Tests bestanden | PASS |
| Debt-Marker in Phase-6-Dateien | `grep -n -E "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` über die 16 Implementierungsdateien | keine Treffer | PASS |
| Schriftgrößen-Tokens | `grep -n -E "font-size-xl\|font-weight-semibold"` über Seiten und Komponenten | keine Treffer; h2 in `EntwicklungPage.vue` Z. 230, `InvestitionenPage.vue` Z. 177, `RatEntscheidetPage.vue` Z. 103 nutzen `--wa-font-size-l` | PASS |
| Hartkodierte Farben | `grep -n -E "#[0-9a-fA-F]{3,6}\b"` über Phase-6-Seiten und -Komponenten | keine Treffer (06/IN-01 bleibt behoben) | PASS |

Step 7c (Probes): keine `probe-*.sh` in dieser Phase deklariert; übersprungen.

### Requirements Coverage

Alle 15 Phasen-IDs kommen in den PLAN-Frontmattern vor, sind in `.planning/milestones/v1.0-REQUIREMENTS.md` (Z. 102–137) definiert und der Phase 6 zugeordnet (Traceability: 15 Zeilen „Phase 6“, alle `Complete`). Keine verwaisten Anforderungen: die 15 Zeilen der Traceability decken sich mit den 15 IDs der PLANs.

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| ENTW-01 | 06-02, 06-05, 06-12, 06-14, 06-17 | Erträge, Aufwendungen und Jahresergebnis 2024–2029, Ist, Ansatz und Planung unterscheidbar | SATISFIED | `EntwicklungPage.vue` Z. 93–117, `EntwicklungsDiagramm.vue` Z. 64/119 (Wertart je Jahr); Defizit 2029 −3.557.700 in `entwicklung.test.ts` Z. 120 (heute grün); `smoke.spec.ts:138 Smoke /entwicklung` (09-BASISLAUF.md) |
| ENTW-02 | 06-05, 06-12 | Zeitreihen für Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen | SATISFIED | `entwicklung.ts` Z. 185–215 (`ENTWICKLUNG_POSTEN`, fünf Einträge), `EntwicklungPage.vue` Z. 119–131; `entwicklung.test.ts` grün; `inventar.spec.ts:39 Inventar /entwicklung` |
| ENTW-03 | 06-01, 06-04, 06-08, 06-12, 06-13, 06-17 | Ausgleichsrücklage und allgemeine Rücklage, wie lange das Polster reicht | SATISFIED | `EntwicklungPage.vue` Z. 133–165, `ruecklagen.ts` Z. 139–146 (Fußnote mit allen Termen); Rückgang 1,77 / 4,23 / 4,73 / 10,04 % in `ruecklagen.test.ts` Z. 169–176 und Regressionsschutz Z. 242–245, heute grün; UAT Test 1 pass |
| INV-01 | 06-02, 06-06, 06-12, 06-14, 06-15, 06-17 | Maßnahmen 2026–2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art | SATISFIED | `InvestitionenPage.vue` Z. 95–111, `MassnahmenFilter.vue` Z. 70–108, `investitionen.ts` Z. 27–32 und Z. 204–207 („1 Maßnahme“ im Singular); `interaktion.spec.ts:453 Maßnahmenfilter auf /investitionen …` (09-BASISLAUF.md) |
| INV-02 | 06-09, 06-12 | Verpflichtungsermächtigungen (11,6 Mio. €) mit Fälligkeiten | SATISFIED | `InvestitionenPage.vue` Z. 112–125 (`VeFaelligkeiten`), `finanzierung.test.ts` Z. 502 (`veGesamt()` = 11.600.000), heute grün |
| INV-03 | 06-09, 06-12 | Finanzierung (Investitionseinzahlungen, Kredite) und Zeitreihe Kreditaufnahme/Tilgung | SATISFIED | `InvestitionenPage.vue` Z. 126–139 (zwei `FinanzierungsDiagramm`-Karten), `finanzierung.ts` Z. 229–278 (`kreditaufnahme`, `tilgung`); `finanzierung.test.ts` grün; `smoke.spec.ts:185 axe … /investitionen` |
| INV-04 | 06-04, 06-09, 06-12, 06-16, 06-17 | Schuldenstand gesamt und je Einwohner | SATISFIED | `schulden.ts` Z. 192–225 (`schuldenKacheln()`), `schulden.test.ts` Z. 317–328 (7.710.000 €, 656 €, ohne „berechnet“), heute grün; `kacheln.spec.ts:465 … /investitionen` |
| RAT-01 | 06-02, 06-04, 06-10, 06-12, 06-14, 06-15, 06-17 | Zuschussbedarf 2026 nach Bindungsgrad als gestapelter Balken mit den Produkten je Kategorie | SATISFIED | `RatEntscheidetPage.vue` Z. 42–76, `bindungsgrad.test.ts` Z. 242–243 (29 / 15 / 15 Produkte), heute grün; `smoke.spec.ts:138 Smoke /rat-entscheidet` |
| RAT-02 | 06-07, 06-10, 06-12 | Block „Was der Rat nicht beeinflussen kann“ (Kreisumlage, Gewerbesteuerumlage, gesetzliche Sozialleistungen) | SATISFIED | `NichtBeeinflussbarBlock.vue` Z. 11/34/69 (Titel „Was der Rat nicht beeinflussen kann“, Kacheln aus `nichtBeeinflussbar()`), `zuschuesse.ts` Z. 5–6, 44–48 (Kreis/Land über `kreisumlage.ts`, Sozialleistungen); `zuschuesse.test.ts` grün |
| RAT-03 | 06-01, 06-07, 06-12 | Einzelzuschüsse aus dem Vorbericht (Kita-Träger einzeln, Kinder- und Jugendwerk, OGS, Vereine, VHS, Sport, Musikschule) | SATISFIED | `ZuschussListe.vue` Z. 108–113, 190–197 (Zusammen-Zeile „berechnet“ nur bei eigener Summe, 08-05 `af0a3eb`), `zuschuesse.ts` Z. 41, 107; `zuschuesse.test.ts` Z. 87–126 grün |
| RAT-04 | 06-04, 06-10, 06-12 | Hinweis, dass der Bindungsgrad eine Selbstauskunft der Verwaltung ist | SATISFIED | `RatEntscheidetPage.vue` Z. 53–57 (`ErklaerText bindungsgrad_selbstauskunft`), `texte.json` Z. 201 |
| STEL-01 | 06-02, 06-11, 06-12, 06-14, 06-16, 06-17 | Stellen 2026 im Vergleich zu 2025 und zu den besetzten Stellen am 30.06.2025 | SATISFIED | `StellenplanPage.vue` Z. 90–140 (drei Kacheln mit „berechnet“ und Herleitung, 08-03 `1d4e359`), `stellen.test.ts` Z. 223–227 (6291 / 6213 / 5663 Hundertstel = 62,91 / 62,13 / 56,63 VZÄ), heute grün; `kacheln.spec.ts:465 … /stellenplan` |
| STEL-02 | 06-04, 06-11, 06-12, 06-16, 06-17 | Verteilung nach Aufgabenbereich und nach Entgelt- bzw. Besoldungsgruppe | SATISFIED | `StellenplanPage.vue` Z. 206–237 (`StellenNachBereich`, `StellenNachGruppe` je Teil), `stellen.ts` Z. 248–349; `quelle.spec.ts:294 … eine Stellenplan-Zeile öffnet eine Querformatseite …` |
| STEL-03 | 06-11, 06-12 | Personalaufwand je Aufgabenbereich (TP Z. 11) | SATISFIED | `StellenNachBereich.vue` Z. 162–175 (zweites Diagramm und Tabellenspalte), `stellen.ts` Z. 229/273 (`personalaufwand` aus dem Teilergebnisplan), `stellen.test.ts` Z. 475–476 (Σ 5.204.054 €), heute grün |
| UI-04 | 06-03, 06-04, 06-07, 06-12 | Hinweis „Was nicht im Haushalt steht“ erklärt BBO (Hallenbad) und TEO AöR (Abwasser) | SATISFIED | `HinweisNichtImHaushalt.vue` Z. 19–27, 50; eingebunden in `EinnahmenPage.vue` Z. 423, `AusgabenPage.vue` Z. 379, `RatEntscheidetPage.vue` Z. 80; `texte.json` Z. 104–112, 540 |

Zeilen der Spalte „Evidence“ mit „heute grün“ beziehen sich auf den eigenen Lauf dieses Plans (12 Testdateien, 600 Tests, Scratch-Kopie); Zeilen mit Playwright-Titeln auf 09-BASISLAUF.md.

### Regressionsprüfung der Plan-must_haves

Geprüft wurden die must_haves-Artefakte und -Links aller 17 PLANs (`verify.artifacts`, `verify.key-links`, dazu Handprüfung der vier Links, die das Werkzeug nicht auswerten kann; siehe „Required Artifacts“ und „Key Link Verification“). Artefakte, die seit dem Vorbericht geändert wurden (`ruecklagen.ts`, `schulden.ts`, `stellen.ts`, `investitionen.ts`, `bindungsgrad.ts`, `menueVersatz.ts`, `format.ts`, die vier Seiten, `MassnahmenFilter.vue`, `ZuschussListe.vue`, `NichtBeeinflussbarBlock.vue`, `UeberschussListe.vue`), erfüllen weiterhin ihre `contains`-Muster und Verdrahtungen. Ergebnis: `re_verification.regressions` ist `[]`. Die zwei Abweichungen des Werkzeugs sind Pfadnotation in den PLANs (archivierter Pfad in 06-17, Funktionsnamen statt Dateipfaden in 06-13/06-15/06-16), keine Codebefunde.

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| Phase-6-Dateien | TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER | keine | Schuldenmarker-Gate bestanden |
| `app/src/lib/ruecklagen.ts` | „zuzüglich der Verrechnung“ ohne Vorzeichenhinweis (Review 06/WR-01) | INFO | Im Ledger `skipped` mit Begründung UAT Test 1 pass; die Kommentare zum Vorzeichen wurden in 08-07 (`81fcd86`) und 08-10 (`507d787`) präzisiert. Keine Regression. |

### Human Verification Required

Keine. Die drei Human-Items des Vorberichts sind in `06-UAT.md` abgeschlossen (3 passed, 0 issues, 0 pending) und oben unter `re_verification.human_items_resolved` mit UAT-Verweis geführt. `06-SECURITY.md`: `threats_open: 0`, `status: verified`.

### Gaps Summary

Keine Gaps. Das Phasenziel ist auf dem heutigen Code erreicht. Die Änderungen aus Phase 7 und Phase 8 an Phase-6-Dateien haben keine Wahrheit gebrochen.

### Live-Evidenz

Die vollen Läufe stammen aus `09-BASISLAUF.md` (head `1d0df35da1842daec515b40dd62f8d918e240105`): 681 pytest-Tests ohne Skip, `alle.py` byte-identisch, 2162 Vitest-Tests in 49 Dateien, Playwright `ci` 89, `mobil` 41, `texte` 1 bestanden. Dieser Plan hat weder `alle.py` noch die volle pytest-Suite noch Playwright gestartet. Beweis, dass sich seit dem Basislauf kein Codepfad geändert hat: `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline app daten scripts .github` endet mit Exit 0.

## Nachtrag 09-15 (D-12)

Stand 2026-10-09. Nach dem Basislauf (head `1d0df35da1842daec515b40dd62f8d918e240105`) hat Plan 09-14 in `ce5880e` (Lücke G-09-02, „PDF-Seite“ im Singular nur bei genau einer Seite; Test `74fed1c`) die Datei `app/src/lib/hilfsfunktionen.ts` um die Funktion `seitenText` ergänzt. Diese Datei deckt der Bericht ab; `verification.status` meldete deshalb wieder `stale`. Die Aussage „seit dem Basislauf hat sich kein Codepfad geändert“ im Abschnitt „Live-Evidenz“ oben beschrieb den Stand vor 09-14 und bleibt als solcher stehen.

| Commit | Geänderte abgedeckte Datei | Betroffene Wahrheit | Test |
|--------|----------------------------|---------------------|------|
| `ce5880e` | `app/src/lib/hilfsfunktionen.ts` (neue Funktion `seitenText`, 11 Zeilen; `quellenZeile`, `klickIndex`, `jahreListe` und alle anderen Funktionen unverändert) | Wahrheiten zu den Hilfsfunktionen der Kontext-Seiten (`quellenZeile`, `klickIndex`, `jahreListe` in `hilfsfunktionen.ts`, Aufrufer in den Seiten 06): bleiben wahr; `ZuschussListe.vue` und `StellenplanPage.vue` behalten ihre eigenen lokalen `seitenText`-Helfer, `StellenNachTeil.vue` ist unverändert. Mittelbar: `ErklaerText.vue` (Phase 5) nutzt `seitenText` und steht auf `/entwicklung`, `/investitionen` und `/rat-entscheidet` (z. B. RAT-04 `bindungsgrad_selbstauskunft`); dort lautet die Quellenzeile jetzt bei mehreren Seiten „PDF-Seiten“. Das ist eine reine Wortlaut-Korrektur, keine Zahl ändert sich, und keine Wahrheit dieses Berichts hängt am Singular | `hilfsfunktionen.test.ts` „G-09-02“ und `erklaertext.test.ts` „G-09-02“ (21 Texte), dazu die bestehenden Phase-6-Tests |

Nachprüfung in einer Scratch-Kopie von `app/` mit Linux-`node_modules` (`npm ci`) auf dem Stand `7e2b775`: die zehn Testdateien `hilfsfunktionen`, `zuschuesse`, `entwicklung`, `investitionen`, `schulden`, `stellen`, `ruecklagen`, `bindungsgrad`, `menue` und `stiltokens` zusammen 410 Tests grün; die volle App-Suite 2207 Tests grün. Keine Wahrheit gebrochen, kein Gap, keine Regression; Status bleibt `passed`, `re_verification.gaps_closed` bleibt leer, weil 09-14 keine Lücke dieser Phase geschlossen hat.

`covered_files` und `covered_digest` stammen unverändert aus `verification.fingerprint`, mit den bisherigen Implementierungsdateien plus `app/src/lib/__tests__/hilfsfunktionen.test.ts`.

---

_Verified: 2026-10-09_
_Verifier: Claude (gsd-verifier-Verfahren, ausgeführt in Plan 09-09)_
