---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 08
subsystem: ui
tags: [vue, quellenbelege, vitest, tdd, datentabelle, stellenplan, investitionen]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: "07-01: belegSchluessel, findeBeleg, DatenTabelle-Spaltenart quelle, KennzahlKachel-Props quelle/wertart; 07-03: vollstaendige quellen.json (vb, inv, sp, seite)"
provides:
  - "Zuschuss.beleg (vb-Schluessel der Tabelle) und Belegschluessel der nichtBeeinflussbar-Kacheln in lib/zuschuesse.ts"
  - "Quelle-Spalte (art quelle) in ZuschussListe, Maßnahmentabelle und StellenNachGruppe; :quelle/:wertart an den Kacheln von NichtBeeinflussbarBlock"
  - "Vorhaben.beleg/anzahlKonten und quelleHerleitung bei gebuendelten Konten (lib/investitionen.ts); GruppenZeile mit teil, position, produktbereich, beleg (lib/stellen.ts)"
  - "quelle-kontext.test.ts: Abdeckungstest der Kontextseiten-Tabellen und -Kacheln"
affects: [07-09, 07-10, 07-11, 07-12]

actuals:
  tokens: 7000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Schluessel nur ueber belegSchluessel; Zeilen tragen das Feld quelle (und optional quelleHerleitung) fuer die DatenTabelle-Spalte art quelle"
    - "Quelltext-Pruefung per import.meta.glob ?raw ueber .vue- und lib/*.ts-Dateien: keine Spalte Quelle/PDF-Seite mit art text"

key-files:
  created:
    - app/src/lib/__tests__/quelle-kontext.test.ts
  modified:
    - app/src/lib/zuschuesse.ts
    - app/src/components/ZuschussListe.vue
    - app/src/components/NichtBeeinflussbarBlock.vue
    - app/src/lib/investitionen.ts
    - app/src/lib/stellen.ts
    - app/src/components/StellenNachGruppe.vue
    - app/src/lib/__tests__/zuschuesse.test.ts
    - app/src/lib/__tests__/investitionen.test.ts
    - app/src/lib/__tests__/stellen.test.ts

key-decisions:
  - "KL-Unterposten (Code KL.kreisumlage usw.) nehmen den Vorberichtsschluessel vb:transferaufwendungen:{posten}, wenn er aufloest, sonst seite:{pdfSeite}"
  - "Eine gebuendelte Massnahme traegt den inv-Schluessel der Kontozeile mit der groessten Auszahlung im Haushaltsjahr (bei Gleichstand oder ohne Wert die erste Zeile) und quelleHerleitung 'Summe aller Konten dieser Maßnahme'"
  - "Die VE-Faelligkeiten-Tabelle (lib/finanzierung.ts) bleibt unveraendert: sie hat keine Seitenspalte, ihre Zeilen sind ueber Massnahmen aggregierte Faelligkeitsjahre"

patterns-established:
  - "Zeilenfeld quelleHerleitung: wird nur gesetzt, wenn der Beleg nicht den ganzen angezeigten Wert abdeckt (Prohibition 'nicht eine Kontozeile als ganze Massnahme ausgeben')"

requirements-completed: [UI-02]

coverage:
  - id: D1
    description: "Einzelzuschuesse auf /rat-entscheidet zeigen eine Quelle-Spalte mit vb-Schluesseln; die Kacheln 'Was der Rat nicht beeinflussen kann' tragen :quelle (KL-Unterposten und Sozialleistungen auf vb:transferaufwendungen)"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle-kontext.test.ts#/rat-entscheidet: Einzelzuschüsse und #/rat-entscheidet: Was der Rat nicht beeinflussen kann; zuschuesse.test.ts#Zuschuss.beleg"
        status: pass
    human_judgment: false
  - id: D2
    description: "Maßnahmentabelle auf /investitionen ersetzt PDF-Seite durch die Quelle-Spalte; gebuendelte Vorhaben tragen den inv-Schluessel der groessten Kontozeile samt Herleitung"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#baueMassnahmenTabelle (Quelle-Spalte, aufloesende Schluessel, Herleitung, groesste Auszahlung, ein Konto); quelle-kontext.test.ts#/investitionen: Maßnahmen"
        status: pass
    human_judgment: false
  - id: D3
    description: "StellenNachGruppe auf /stellenplan traegt sp-Schluessel; die Stellenplanseiten sind Querformat und die Markierung liegt innerhalb der Seite"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stellen.test.ts#stellenNachGruppe (sp-Schluessel, Querformat-Umrechnung); quelle-kontext.test.ts#/stellenplan: Stellen nach Gruppe"
        status: pass
    human_judgment: false
  - id: D4
    description: "Das Aussehen der Quelle-Spalte und der Knoepfe in den Kontexttabellen und Kacheln (Abstaende, Umbruch bei 360 px, Lesbarkeit der Markierung auf den Querformat-Seiten) ist nur im Browser beurteilbar"
    requirement: "UI-02"
    verification: []
    human_judgment: true
    rationale: "Kein e2e-Test fuer die neuen Spalten: e2e/quelle.spec.ts deckt nur die Start-Kachel ab; die optische Abnahme faellt in 07-09 (Mobil) und den Checkpoint 07-10"

duration: 38min
completed: 2026-10-06
status: complete
plan_head_before: a799ce0b63e5b0c7c9c4495564c479089661e7ae
plan_head_after: e2eebdb3cd69678cc677499708f3e48a8cd10503
---

# Phase 7 Plan 08: Quelle anzeigen auf den Kontextseiten Summary

**Einzelzuschuesse, die nicht beeinflussbaren Posten, die Maßnahmentabelle und die Stellen-nach-Gruppe-Tabelle nutzen jetzt die Spalte Quelle (art quelle) mit Schluesseln ueber belegSchluessel; gebuendelte Maßnahmen nennen die groesste Kontozeile mit der Herleitung "Summe aller Konten dieser Maßnahme", und ein Vertragstest haelt die Schluessel aufloesbar.**

## Performance

- **Duration:** 38 min
- **Tasks:** 2 (beide TDD, je RED- und GREEN-Commit)
- **Files modified:** 10 (1 neu)

## Accomplishments

- **/rat-entscheidet:** `Zuschuss.beleg` (vb-Schluessel aus Tabelle und Posten, `null` ohne Seite); die Spalte "Quelle" von `ZuschussListe` ist `art: 'quelle'`, der Text "PDF-Seite n" entfaellt (die Quellzeile ueber der Tabelle bleibt Text). `NichtBeeinflussbarBlock` reicht `:quelle` und `:wertart` an `KennzahlKachel` weiter, ohne Herleitung (die Werte stehen gedruckt da, nur auf T€ gerundet; der Hinweis zur Rundung kommt vom Beleg selbst).
- **KL-Unterposten:** Code `KL.kreisumlage` wird auf `vb:transferaufwendungen:kreisumlage` abgebildet, ohne passenden Posten auf `seite:{pdfSeite}`.
- **/investitionen:** `baueMassnahmenTabelle` endet mit der Quelle-Spalte; `buendeln` merkt je Vorhaben den Beleg der Kontozeile mit der groessten Auszahlung im Haushaltsjahr und die Zahl der Konten. Bei mehr als einem Konto traegt die Zeile `quelleHerleitung`. Im echten Bestand betrifft das 10 von 89 Maßnahmen.
- **/stellenplan:** `GruppenZeile` traegt `teil`, `position`, `produktbereich` und den `sp`-Schluessel; `StellenNachGruppe` zeigt die Spalte als `art: 'quelle'`. Alle Zeilen loesen auf, die Seiten 284 bis 290 sind Querformat (841,89 x 595,28), die Markierungen liegen innerhalb der Seite (Test mit `bboxProzent`).
- **VE-Faelligkeiten:** unveraendert; die Tabelle hat keine Seitenspalte, ihre Zeilen sind Faelligkeitsjahre.
- **Test:** `quelle-kontext.test.ts` prueft alle ausgesendeten Schluessel auf Aufloesbarkeit und scannt `ZuschussListe.vue`, `NichtBeeinflussbarBlock.vue`, `StellenNachGruppe.vue`, `lib/investitionen.ts` und `lib/stellen.ts` auf Seitenspalten mit Art text beziehungsweise fehlende `belegSchluessel`-Aufrufe; das Pruefmuster hat eigene Positiv- und Negativproben.

## Task Commits

1. **Task 1: /rat-entscheidet** - RED `9a4c72e` (test), GREEN `face109` (feat)
2. **Task 2: /investitionen und /stellenplan** - RED `a8e080b` (test), GREEN `e2eebdb` (feat)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md)

## TDD Gate Compliance

Fuer beide Aufgaben gibt es einen `test(07-08)`-Commit vor dem `feat(07-08)`-Commit; kein REFACTOR noetig.

- **RED Aufgabe 1** (`9a4c72e`): 9 Tests rot, u. a. `ZuschussListe hat eine Quelle-Spalte der Art quelle` (Quelltext enthaelt `art: 'quelle'` nicht), `jeder Zuschuss mit Seite traegt einen auflösbaren Vorberichtsschluessel` (`beleg` ist `undefined`), `KL.kreisumlage: expected null not to be null`. Semantische Bewertung: alle Ziel-Tests liefen und scheiterten an der geplanten Zusicherung (fehlendes Feld, fehlende Spaltenart), nicht an Syntax, Import oder Fixture; die uebrigen 22 Tests blieben gruen.
- **RED Aufgabe 2** (`a8e080b`): 12 Tests rot (Quelle-Spalte fehlt, `seite` statt `quelle`, `beleg`/`teil` `undefined`, Herleitung fehlt). Erste Fassung des Herleitungs-Tests schluesselte ueber ein noch nicht existierendes Zeilenfeld und scheiterte deshalb an der falschen Stelle (0 Konten); vor dem Commit auf das vorhandene Feld `schluessel` umgestellt, danach scheiterte er an `quelleHerleitung` wie geplant.
- `gsd_run check tdd-red-evidence` nicht ausgefuehrt: `workflow.tdd_mode` ist in diesem Projekt aus; die semantische Pruefung erfolgte von Hand.

## Deviations from Plan

None - plan executed exactly as written. (`MassnahmenListe.vue` brauchte keine Aenderung: sie reicht `tabelle.spalten` unveraendert an `DatenTabelle`, das die Spaltenart `quelle` selbst zeichnet.)

**Total deviations:** 0.

## Issues Encountered

- **Vorbestehender, unsteter e2e-Test:** In `e2e/quelle.spec.ts` schlaegt der erste Test ("Klick oeffnet die Seitenleiste mit Bild und Markierung") bei kalten Laeufen zeitweise fehl (Markierung ragt um etwa 50 px ueber den Bildrand: `boundingBox` von Markierung und Bild werden zu verschiedenen Zeitpunkten waehrend der Drawer-Animation gemessen). Der Test beruehrt keine Datei dieses Plans. Gegenprobe: ein Build von `a799ce0` (Basis) schlug im selben Lauf in 2 von 4 kalten Laeufen ebenfalls fehl; mit meinem Stand liefen 18 von 18 Wiederholungen (`--repeat-each=3`) gruen, eine Wiederholung von 30 rot. Nicht behoben (ausserhalb dieses Plans); Vorschlag fuer 07-09 bis 07-11: vor dem Messen auf das Ende der Drawer-Animation warten (`wa-after-show`) oder beide Boxen in einem `page.evaluate` lesen.
- **Defekte Installation im Worktree:** `npm ci` hinterliess eine leere Datei `app/node_modules/echarts/lib/component/brush/selector.js` (7 Testdateien schlugen beim Import von `echartsTheme.ts` fehl). Behoben, indem genau diese Datei aus dem Tarball `echarts@6.1.0` (die in `package-lock.json` gepinnte Version) neu geschrieben wurde; `node_modules` ist gitignoriert, keine Abhaengigkeit hat sich geaendert.
- Das Wurzeldateisystem der Sandbox war voll (`/tmp`); die Basisgegenprobe lief daher in einem kurzlebigen Verzeichnis unter dem Worktree, das danach geloescht wurde.
- Die Verify-Befehle des Plans tarren `app` in ein Scratch-Verzeichnis; stattdessen liefen alle Pruefungen direkt im Worktree (Linux-`node_modules`, wie in 07-04): `type-check`, `lint`, `format:check`, die volle Suite (40 Dateien, 1786 Tests), `build-only` und der Playwright-Lauf im Docker-Image `playwright:v1.63.0-noble` (Container mit eindeutigem Namen, Port 4173 nur im Container).

## Known Stubs

None. Zuschuesse ohne Seite haben `beleg: null` und damit keinen Knopf (modellierter Zustand), `bbox: null` zeigt den Hinweis aus 07-01.

## Threat Flags

None - keine neue Netz-, Auth- oder Dateizugriffsflaeche; Schluessel entstehen nur ueber `belegSchluessel` und werden vom Abdeckungstest geprueft (T-07-19 mitigiert).

## Next Phase Readiness

- Die optische Abnahme der neuen Quelle-Spalten (360 px, Querformat-Markierung der Stellenplanseiten) steht fuer 07-09 und den Checkpoint 07-10 aus (`human_judgment: true` in D4).
- Nuance zur Herleitung: bei aktivem Artfilter auf `/investitionen` buendelt `buendeln` nur die gefilterten Konten; der Text "Summe aller Konten dieser Maßnahme" bezeichnet dann die Konten im Filter (der Plan schreibt den Wortlaut vor).

## Self-Check: PASSED

- Dateien vorhanden: quelle-kontext.test.ts, zuschuesse.ts, ZuschussListe.vue, NichtBeeinflussbarBlock.vue, investitionen.ts, stellen.ts, StellenNachGruppe.vue und die drei erweiterten Testdateien.
- Commits vorhanden: 9a4c72e, face109, a8e080b, e2eebdb (alle im Zweig).
- Akzeptanzkriterien beider Aufgaben geprueft (erfuellt).

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
