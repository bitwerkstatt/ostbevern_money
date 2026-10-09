---
phase: 08-fixes-und-triage
plan: 05
subsystem: ui
tags: [vue, vitest, zuschuesse, berechnet-etikett, rd-regel, massnahmenfilter]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-02: charts/format.ts als einzige rd.-Autorität (betragMitHinweis, kurzMitHinweis), EuroBetrag mit Props gerundet/berechnet/kurz"
provides:
  - "zusammen() liefert { wert, berechnet } | null (interface ZuschussSumme)"
  - "Zeile Zusammen in ZuschussListe über EuroBetrag, Etikett nur bei selbst gebildeter Summe"
  - "Etikett berechnet an der Filtersumme auf /investitionen"
  - "Prüfauftrag D-12 mit dokumentierter Liste (siehe unten)"
affects: [08-07]

plan_head_before: b3aec27fde1414fd0d766fec9e7682c3813a2de2
plan_head_after: 470a149fb7117a12959aceba3692183c4b55170c

actuals:
  tokens: 4000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Eine Summe trägt das Etikett berechnet genau dann, wenn die App sie gebildet hat; die Modellfunktion liefert das Kennzeichen mit"

key-files:
  created: []
  modified:
    - app/src/lib/zuschuesse.ts
    - app/src/lib/__tests__/zuschuesse.test.ts
    - app/src/components/ZuschussListe.vue
    - app/src/components/MassnahmenFilter.vue

key-decisions:
  - "Die Kita-Beschreibung zeigt die gedruckte Summe ohne Etikett; wäre sie berechnet, fällt sie auf Zuschuss je Einrichtung. zurück und die Zeile Zusammen mit Etikett steht im Kartenkörper (RESEARCH Open Question 2)"
  - "Das Etikett an der Filtersumme steht außerhalb der aria-live-Region, damit der Live-Text byte-identisch bleibt"

requirements-completed: [TXT-05, TXT-04]

coverage:
  - id: D1
    description: "zusammen() unterscheidet die gedruckte Gesamtzeile (berechnet false) von der selbst gebildeten Summe (berechnet true), ohne Wert null; transfer ist immer berechnet"
    requirement: TXT-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/zuschuesse.test.ts#zusammen"
        status: pass
    human_judgment: false
  - id: D2
    description: "Die Zeile Zusammen in ZuschussListe entsteht über EuroBetrag; die drei rd.-Altkopien sind entfernt"
    requirement: TXT-04
    verification:
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh app e2e/smoke.spec.ts (33 Tests, inkl. /rat-entscheidet, axe)"
        status: pass
    human_judgment: true
    rationale: "Ob das Etikett an der Zeile Zusammen optisch neben dem Betrag passt (360 px, Umbruch von berechnet), prüft kein Test"
  - id: D3
    description: "Die Filtersumme auf /investitionen trägt das Etikett berechnet, der Live-Text bleibt unverändert"
    requirement: TXT-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#ergebnisText"
        status: pass
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh app e2e/smoke.spec.ts e2e/interaktion.spec.ts (54 Tests)"
        status: pass
    human_judgment: true
    rationale: "Optik und Lesereihenfolge des Etiketts neben der Live-Region sind ein Urteil über Wirkung"
  - id: D4
    description: "Prüfauftrag D-12: alle Summenstellen der Kontextseiten sind einzeln als Etikett nötig oder nicht nötig eingeordnet"
    requirement: TXT-05
    verification: []
    human_judgment: true
    rationale: "Die Einordnung ist eine fachliche Bewertung gegen das PDF; der Nutzer soll den offenen Punkt Steuergruppen entscheiden"

duration: 6min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 05: Etikett berechnet nur bei selbst gebildeter Summe Summary

**`zusammen()` sagt jetzt, ob die Summe gedruckt oder von der App gebildet ist, die Zeile „Zusammen“ der Zuschüsse entsteht über `EuroBetrag` mit Etikett nur bei berechneter Summe, die drei rd.-Altkopien in `ZuschussListe` sind weg, und die Filtersumme auf /investitionen trägt das Etikett „berechnet“.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-07T18:37:44Z
- **Completed:** 2026-10-07T18:43:00Z
- **Tasks:** 2 (Tracer, Auto)
- **Files modified:** 4

## Accomplishments

- `zusammen(gruppe)` liefert `{ wert, berechnet } | null` (`ZuschussSumme`): gedruckte Gesamtzeile mit `berechnet: false`, sonst die Summe der vorhandenen Werte mit `berechnet: true`, ohne einen Wert `null`. Die Gruppe `transfer` hat keine gedruckte Summe und ist immer berechnet. Kita (S. 46) und laufende Zwecke sind gedruckt, also ohne Etikett.
- `ZuschussListe.vue`: `zusammenText` entfällt, die Zeile „Zusammen“ steht im Template über `<EuroBetrag gerundet :berechnet>`; Tabellenzellen über `betragMitHinweis(wert, true)`, Diagrammlabels über `kurzMitHinweis(wert, true)`. Die Kita-Beschreibung nennt die gedruckte Summe ohne Etikett; eine berechnete Kita-Summe würde mit Etikett in den Kartenkörper wandern.
- `MassnahmenFilter.vue`: `<p><span aria-live="polite">{{ ergebnis }}</span><BerechnetEtikett /></p>`. Der Live-Text ist unverändert.
- Prüfauftrag D-12 ausgeführt (Tabelle unten).

## Task Commits

1. **Task 1 (Tracer): zusammen() mit Kennzeichen, Zusammen-Zeile über EuroBetrag, rd.-Kopien entfernt** — `af0a3eb` (fix, 06/IN-07, 05/WR-01)
2. **Task 2: Filtersumme auf /investitionen mit Etikett, Prüfauftrag D-12** — `470a149` (fix, 06/IN-07)

**Plan metadata:** docs-Commit mit dieser SUMMARY (STATE.md und ROADMAP.md gehören dem Orchestrator).

## Prüfauftrag D-12: geprüft, Etikett nötig / nicht nötig

Jede Zeile gegen den Code am angegebenen Ort neu geprüft; die VE-Summen zusätzlich gegen das PDF (PDF-Seiten 25 und 309 mit pdfplumber gelesen).

| Stelle | Gezeigt auf | Ergebnis | Begründung |
|---|---|---|---|
| `lib/investitionen.ts` `ergebnisText` (:213-216) über `MassnahmenFilter.vue` | /investitionen | **Etikett nötig** (gesetzt, Commit `470a149`) | Die Summe der gefilterten Vorhaben steht nirgends im PDF, sie hängt vom Filter ab. |
| `lib/finanzierung.ts` VE-Jahressummen (`baueVeFaelligkeiten`, :99) | /investitionen | nicht nötig | S. 25 druckt „Summe: 9.400 T€ 2.200 T€“, S. 309 dieselben Beträge je Fälligkeitsjahr; die App summiert die Maßnahmen zu denselben Werten. |
| `lib/finanzierung.ts` `veGesamt` (:109-111) | /investitionen, VE-Kachel | nicht nötig | Entspricht der gedruckten Gesamtsumme (S. 25 „insgesamt 11,6 Mio. €“, S. 309 „Summe: 11.600 T€“). |
| `lib/finanzierung.ts` `einzahlungsAbweichungen` (:320-331) | /investitionen, Fußnote des Finanzierungsdiagramms | nicht nötig | Zeigt keine Summe, sondern nennt nur die höchste Abweichung der Einzelzeilen von der gedruckten Summenzeile (Z. 23). |
| `lib/bindungsgrad.ts` Summen (:115 ff.) | /rat-entscheidet | nicht nötig | Bereits gekennzeichnet: `BindungsgradBalken.vue:120` „Summen und Anteile“ mit `BerechnetEtikett`. |
| `lib/einnahmen.ts` Rest „Sonstige (berechnet)“ (:315) | /einnahmen | nicht nötig | Bereits `berechnet: true` und im Namen als berechnet benannt. |
| `lib/geldfluss.ts` Steuergruppen (:161/165, „Grundsteuer (A+B)“) | /geldfluss, /einnahmen (Leitfragen-Seiten) | nicht in diesem Auftrag, siehe Offene Punkte | Keine Kontextseite, also außerhalb D-12. Die Gruppen sind Summen einzelner Steuerarten und tragen `berechnet: false`; `geldfluss.test.ts:169-178` sichert das ab (05/WR-01). Der Rest „Übrige Steuern“ ist dagegen `berechnet: true`. |

Alle sieben Vorannahmen des Plans haben sich bestätigt, kein Widerspruch. In den von 08-04 gehaltenen Dateien (SteuerZeitreihe, PostenZeitreihe, AusgabenPage, EinnahmenPage, KreisumlageCallout, AufwandTreemap, EbenenTabelle, NichtBeeinflussbarBlock, drilldown.ts, zeitreihen.ts, quelltext.test.ts) habe ich nichts geändert und nichts Zusätzliches gefunden.

## Offene Punkte für den Nutzer

- **Steuergruppen auf den Leitfragen-Seiten:** „Grundsteuer (A+B)“ und die anderen Steuergruppen in `lib/geldfluss.ts` (:161/165) sind vom Code gebildete Summen mehrerer gedruckter Zeilen, stehen aber ohne Etikett auf /geldfluss und /einnahmen. Das ist seit 05/WR-01 ein bewusster Zustand (Test `geldfluss.test.ts:169-178` verlangt `berechnet: false`). D-12 gilt nur für Kontextseiten, deshalb habe ich es nicht angefasst. Entscheide, ob die Regel „Etikett bei jeder von der App gebildeten Summe“ auch dort gelten soll; dann müsste der Test geändert werden.

## Files Created/Modified

- `app/src/lib/zuschuesse.ts` - `ZuschussSumme`, neuer Rückgabetyp von `zusammen()`
- `app/src/lib/__tests__/zuschuesse.test.ts` - fünf Tests für `zusammen()` (gedruckt, berechnet, leer, transfer, Kita/lfd)
- `app/src/components/ZuschussListe.vue` - Zeile Zusammen über `EuroBetrag`, Kita-Beschreibung, rd.-Kopien ersetzt
- `app/src/components/MassnahmenFilter.vue` - Etikett neben der Live-Region

## Decisions Made

- Kita-Beschreibung und Kartenkörper wie in RESEARCH Open Question 2 empfohlen (weicht bewusst vom Wortlaut der UI-SPEC ab, weil ein berechneter Betrag im Fließtext sonst ohne Etikett stünde).
- Etikett außerhalb des `aria-live`-Spans: der angesagte Text bleibt wie bisher, der Tooltip des Etiketts wird nicht bei jedem Filterwechsel vorgelesen.

## Deviations from Plan

None - plan executed exactly as written.

Hinweis ohne Abweichung: Task 1 ist ein Tracer, die Tests wurden vor der Implementierung geschrieben, aber nicht als eigener RED-Commit festgehalten (kein `tdd="true"`-Task). Prettier verlangte einen Zeilenumbruch in `ZuschussListe.vue`; der Umbruch ist im Task-Commit enthalten.

## Issues Encountered

None

## Verification

- Scratch-Kopie (`npm ci`, Linux): `type-check`, `lint`, `format:check`, voller `vitest`-Lauf (47 Dateien, 2019 Tests), `build-only` grün.
- `scripts/e2e-wie-ci.sh`: nach Task 1 `smoke.spec.ts` 33 Tests grün; nach Task 2 `smoke.spec.ts` und `interaktion.spec.ts` 54 Tests grün (inkl. axe auf /rat-entscheidet und /investitionen).
- Akzeptanzkriterien: `rd. ${` 0 Treffer, `zusammenText` 0 Treffer, `<EuroBetrag` 1 Treffer, `export interface ZuschussSumme` 1 Zeile, `BerechnetEtikett` 2 Zeilen, `aria-live="polite"` 1 Zeile in `MassnahmenFilter.vue`.
- `uv run --directory pipeline python alle.py --jahr 2026`: danach `git status` ohne Änderung, `daten/`, `app/src/data/` und `app/public/quellen` unverändert.

## User Setup Required

None - no external service configuration required.

## Threat Flags

Keine neue Angriffsfläche. T-08-09 ist mitigiert: `zusammen().berechnet` steuert das Etikett (Test für die drei Zustände), die Filtersumme ist gekennzeichnet.

## Next Phase Readiness

- 08-07 kann den Wächtertest für die rd.-Regel um `ZuschussListe.vue` ergänzen (keine Kopie mehr vorhanden).
- Offen für den Nutzer: Steuergruppen (siehe oben).

## Self-Check: PASSED

- app/src/lib/zuschuesse.ts, app/src/components/ZuschussListe.vue, app/src/components/MassnahmenFilter.vue, app/src/lib/__tests__/zuschuesse.test.ts: vorhanden
- Commits af0a3eb, 470a149: Vorfahren von HEAD

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
