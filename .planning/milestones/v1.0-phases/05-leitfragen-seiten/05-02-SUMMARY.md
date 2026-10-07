---
phase: 05-leitfragen-seiten
plan: 02
subsystem: pipeline-daten
tags: [vorbericht, regel-5, gesamtfinanzplan, konzessionsabgaben, zeilen-namen, haushalt-json, typescript-types]

requires:
  - phase: 04-manuelle-daten-und-app-daten
    provides: "VORBERICHT_SPALTEN-Format, Regel 5 (zweistufig), weitere_vorberichtstabellen.csv, baue_vorbericht_tabelle(sonstige=...), haushalt.json-Vertrag"
provides:
  - "Tabelle 2.1.7 sonstige_ertraege (S. 33) als sechste weitere Vorberichtstabelle, geprüft gegen GEP Z. 07, vier dokumentierte Befunde"
  - "investitionszuwendungen.csv (S. 52): zehn Posten + Gesamtzeile 3.742 T€, geprüft gegen GFP Z. 18 (neuer Regel-5-Finanzplan-Zweig)"
  - "meta.json vorbericht_werte.konzessionsabgabe_strom|gas|wasser mit Regel-5-Summenprüfung gegen Posten konzessionsabgaben"
  - "haushalt.json: vorbericht.sonstige_ertraege (mit berechnetem Posten Sonstige), vorbericht.investitionszuwendungen (planzeile/gesamt_plan null), zeilen_namen.{ergebnisplan,finanzplan}"
  - "typen.ts: ZeilenName, Haushalt.zeilen_namen"
affects: [05-leitfragen-seiten, einnahmen-seite, aufwandsart-ansicht, produktdetail]

actuals:
  tokens: 20150
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "REGEL5_GFP_ZEILEN: Vorberichtstabelle -> Gesamtfinanzplan-Zeile (Stufe b), getrennt von REGEL5_GEP_ZEILEN (Spez. 3.1)"
    - "TABELLEN_MIT_SONSTIGE: berechneter Posten Sonstige für zuwendungen und sonstige_ertraege"
    - "zeilen_namen wird ausschließlich aus ostbevern/zeilen.py ZEILEN erzeugt (keine zweite Namenstabelle in der App)"

key-files:
  created:
    - daten/manuell/investitionszuwendungen.csv
  modified:
    - daten/manuell/weitere_vorberichtstabellen.csv
    - daten/manuell/meta.json
    - daten/manuell/README.md
    - daten/pruefberichte/befunde.md
    - daten/pruefberichte/konsistenz.md
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/tests/test_pruefung.py
    - pipeline/tests/test_manuell.py
    - pipeline/tests/test_app_daten.py
    - app/src/data/haushalt.json
    - app/src/data/typen.ts

key-decisions:
  - "Der gedruckte Wert 2.396 T€ der Gesamtzeile 2028 (Tabelle 2.1.7) bleibt unverändert in der CSV; die Abweichung ist ein Befund, die App folgt GEP Z. 07 (Sonstige 2028 = 1.161 €)"
  - "Posten-Schlüssel der Förderungen folgen der README-Ableitungsregel inklusive Fördersatz (z. B. foerderung_wirtschaftswege_70), wie versicherung_ohne_gebaeude"
  - "investitionszuwendungen steht in vorbericht_quellen direkt nach kita_zuschuesse, sonstige_ertraege bleibt dadurch letzte Tabelle"
  - "zeilen_namen wird hinter eigenkapital angehängt, bestehende haushalt.json-Schlüssel behalten ihre Reihenfolge"

requirements-completed: [EINN-04, EINN-06]

coverage:
  - id: D1
    description: "Tabelle 2.1.7 (S. 33) wie gedruckt transkribiert, Regel 5 gegen GEP Z. 07 grün mit vier dokumentierten Befunden, in haushalt.json mit berechnetem Posten Sonstige 2028"
    requirement: EINN-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_sonstige_ertraege_ergibt_gep_zeile_07"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_sonstige_ertraege_gedruckter_druckfehler_bleibt_erhalten"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (Gesamtstatus: grün)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Konzessionsabgaben Strom/Gas/Wasser in meta.json, Summe per Regel 5 gegen den Posten konzessionsabgaben bewiesen"
    requirement: EINN-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel5_konzessionsabgaben_split_abweichung_rot"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel5_konzessionsabgaben_split_gruen_auf_eingecheckten_daten"
        status: pass
    human_judgment: false
  - id: D3
    description: "Investive Zuweisungen S. 52 (Pauschalen und Förderungen) mit Regel-5-Finanzplan-Zweig gegen GFP Z. 18 und im App-JSON ohne Ergebnisplan-Zeile"
    requirement: EINN-06
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel5_gfp_gesamtzeile_gegen_gfp_18_rot"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_investitionszuwendungen_gleich_gfp_18_im_haushaltsjahr"
        status: pass
    human_judgment: false
  - id: D4
    description: "zeilen_namen (gedruckte Zeilennamen, Nummer, Summenflag) aus zeilen.py in haushalt.json und typen.ts, Type-Check ohne Casts"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_zeilen_namen_decken_ergebnisplan_ab"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_zeilen_namen_decken_finanzplan_ab"
        status: pass
      - kind: other
        ref: "npm run type-check / lint / format:check / build im Scratch-Copy von app/"
        status: pass
    human_judgment: false
  - id: D5
    description: "Reproduzierbarkeit: alle.py --jahr 2026 lässt daten/ und app/src/data/ unverändert"
    verification:
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data (sauber, keine untracked Dateien)"
        status: pass
    human_judgment: false

duration: ca. 90 min (Startzeit nicht erfasst, geschätzt)
completed: 2026-10-04
status: complete
plan_head_before: b35812ee68903990dadca3e55bbb1501490164b0
plan_head_after: abf4f6c864cb9d15ca22c17969ed7cab81ca94f7
commits: 6
---

# Phase 5 Plan 02: Vorbericht 2.1.7 und S. 52, Regel-5-Finanzplan-Zweig, Zeilennamen Summary

**Zwei Vorbericht-Tabellen (2.1.7 Sonstige ordentliche Erträge, S. 52 investive Zuweisungen) abgeschrieben und über Regel 5 (GEP Z. 07, neuer GFP-Z.-18-Zweig, Konzessionsabgaben-Summe) belegt, plus `zeilen_namen` aus `zeilen.py` in `haushalt.json` und `typen.ts`.**

## Performance

- **Duration:** ca. 90 min (Startzeit nicht erfasst, geschätzt)
- **Completed:** 2026-10-04
- **Tasks:** 3 (Tracer, 2 TDD-Tasks)
- **Files modified:** 14 (1 neu)
- **Pytest gesamt:** 484 passed, 1 skipped (`test_port_wie_format_ts`, erwartet im Worktree ohne `app/node_modules`)

## Accomplishments

- **Tracer (Task 1):** Tabelle 2.1.7 (S. 33, Text und gerendertes Seitenbild verglichen) transkribiert, sechste Tabelle in `WEITERE_VORBERICHTSTABELLEN`, `REGEL5_GEP_ZEILEN["sonstige_ertraege"] = "07"`. Regel 5 meldete vier Abweichungen, alle gegen PDF und GEP-Seite (S. 62) verifiziert und in `befunde.md` dokumentiert: `summe_posten` 2024 (+2.000), 2025 (+1.000), 2028 (-51.000) sowie `gep_07` 2028 (+49.839). Der gedruckte 2028-Wert 2.396 T€ ist ein Druckfehler (Σ Posten 2.345 T€, GEP 2.346.161 €); die CSV hält ihn unverändert. `haushalt.json` enthält `sonstige_ertraege` als letzte Tabelle mit berechnetem Posten „Sonstige“ nur 2028 (1.161 €), sodass Σ Posten exakt GEP Z. 07 ergibt; in allen anderen Jahren liegt die Gesamtzeile innerhalb ±1.000 €.
- **Task 2:** `investitionszuwendungen.csv` (zehn Posten, Gesamtzeile 3.742 T€, nur Haushaltsjahr, S. 52), `meta.json` mit Strom 315 / Gas 40 / Wasser 115 T€ (S. 33). Neuer Regel-5-Zweig `REGEL5_GFP_ZEILEN` (`gfp_18`, Toleranz ±1.000 €, `_pruefe_regel5(planwerte_finanzplan=...)`) und `_pruefe_regel5_konzessionsabgaben` (exakt, Summe der Sparten = Posten × 1000). App-JSON: `vorbericht.investitionszuwendungen` ohne `planzeile`/`gesamt_plan`, Werte nur im Haushaltsjahr, Σ = GFP Z. 18.
- **Task 3:** `baue_zeilen_namen` liest nur `ZEILEN` und liefert je Ergebnisplan- und Finanzplan-Schlüssel `{schluessel, nummer, name, ist_summe}`; `haushalt.json` trägt `zeilen_namen` hinter `eigenkapital`; `typen.ts` ergänzt `ZeilenName` und `Haushalt.zeilen_namen` (Type-Check ohne Casts grün).
- Regel 5 geprüft jetzt 148 Werte (vorher 145 plus die Tracer-Tabelle), `konsistenz.md`: Gesamtstatus grün, 0 veraltete Befunde.

## Task Commits

1. **Task 1: Tracer 2.1.7 end-to-end** - `b81b922` (feat)
2. **Task 2: Daten S. 52 und Konzessionsabgaben** - `09e0ce0` (feat, reine Abschrift plus schema-Konstante)
   - RED: `7bc5929` (test)
   - GREEN: `38b631f` (feat)
3. **Task 3: zeilen_namen**
   - RED: `51bf30c` (test)
   - GREEN: `abf4f6c` (feat)

**Plan metadata:** wird mit diesem SUMMARY committet (docs).

## Tracer-Gate

Task 1 trug `type="tracer"`; `workflow.auto_advance=false`, `human_verify_mode=end-of-phase`, `<verify>` rein automatisiert. Der Tracer wurde Ende-zu-Ende erneut gefahren (pytest der drei Dateien, `alle.py --jahr 2026`, `Gesamtstatus: grün`, JSON-Akzeptanzprüfung): bestanden, danach Expansion.

## TDD Gate Compliance

- Task 2: `test(05-02)` `7bc5929` vor `feat(05-02)` `38b631f`. Die Abschrift der Handdaten (`09e0ce0`, kein Verhalten) wurde vor dem RED-Commit committet, damit die Mutationstests auf echten Dateien eine Assertion verfehlen statt an einer fehlenden Datei zu scheitern. RED: sieben Tests scheiterten an Assertions/Lookups des geplanten Verhaltens (Regel-5-Abweichung bleibt aus, `REGEL5_GFP_ZEILEN` fehlt, Tabelle fehlt im JSON); kein Collection-Fehler (Modulzugriff statt Import).
- Task 3: `test(05-02)` `51bf30c` vor `feat(05-02)` `abf4f6c`; RED: vier Tests rot (KeyError `zeilen_namen`, Schlüsselreihenfolge).
- Der formale `gsd_run check tdd-red-evidence`-Record wurde nicht erzeugt (Werkzeug im Worktree nicht verfügbar); die Fehlschläge wurden stattdessen an der pytest-Ausgabe geprüft.
- Kein REFACTOR-Commit nötig.

## Decisions Made

Siehe `key-decisions` im Frontmatter. Zusätzlich: Die Förderquoten stehen als Teil des gedruckten Namens im Posten-Schlüssel (Ableitungsregel der README), damit die Schlüsselableitung für alle manuellen Dateien einheitlich bleibt.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] README-Abschnitt vor dem Regel-5-Code**
- **Found during:** Task 2 (nach Abschrift der Daten)
- **Issue:** `test_manuell.py::test_readme_nennt_jede_manuelle_datei` verlangt, dass `daten/manuell/README.md` jede Datei nennt; `investitionszuwendungen.csv` fehlte dort, obwohl das README laut Plan erst im letzten Schritt ergänzt werden sollte.
- **Fix:** README-Abschnitte (investitionszuwendungen.csv, meta-Zeile, Konzessionsabgaben-Aufteilung) bereits im Daten-Commit.
- **Files modified:** daten/manuell/README.md
- **Committed in:** 09e0ce0

**2. [Rule 1 - Bug] Bestehende Schlüsselreihenfolge-Tests an das neue Top-Level-Feld angepasst**
- **Found during:** Task 3 (GREEN, Vollauf)
- **Issue:** `test_haushalt_json_eigenkapital` (`eigenkapital` letzter Schlüssel) und `test_haushalt_json_knoten_und_ergebnisplan` (exakte Schlüsselliste) kannten `zeilen_namen` nicht.
- **Fix:** Erwartung um `zeilen_namen` am Ende ergänzt (bewusst, laut Plan wird hinten angehängt).
- **Files modified:** pipeline/tests/test_app_daten.py
- **Committed in:** 51bf30c / abf4f6c

**3. [Plan-Annahme präzisiert] Vierter Befund bei Tabelle 2.1.7**
- **Issue:** Der Plan nannte Stufe-(a)-Abweichungen 2024/2025 und Stufe (b) 2028; Regel 5 meldete zusätzlich Stufe (a) 2028 (Σ Posten 2.345 T€ gegen gedruckte 2.396 T€ = -51.000 €).
- **Fix:** Als eigener Befund dokumentiert (gleiche Ursache, Druckfehler im Vorbericht).
- **Files modified:** daten/pruefberichte/befunde.md
- **Committed in:** b81b922

---

**Total deviations:** 3 (1 blocking, 1 bug in Tests, 1 Plan-Präzisierung). **Impact on plan:** Kein Scope-Creep; alle drei folgen direkt aus den Zielen des Plans.

## Issues Encountered

- App-Checks liefen in einem Scratch-Copy unter dem Scratchpad (`tar` ohne `node_modules`, `npm ci`), statt `mktemp -d`, weil die Sandbox-Regeln des Worktrees `mktemp`-Variablen in Pipelines ablehnten. Ergebnis unverändert: type-check, lint, format:check, build grün.
- `pkill -f "pytest -q"` beendete versehentlich die eigene Shell; der Vollauf wurde sauber wiederholt (484 passed).

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. Stub-Muster in den geänderten Dateien: keine.

## Threat Flags

None. Keine neuen Netzwerk-, Auth- oder Dateizugriffsflächen; Mitigationen T-05-03 bis T-05-05 umgesetzt (zweistufige Regel 5, Summenprüfung Konzessionsabgaben, Mutationstests auf tmp-Kopien, `investitionszuwendungen` ohne GEP-Zeile durch Test abgesichert).

## Next Phase Readiness

- Die Einnahmen-Seite kann `vorbericht.sonstige_ertraege` (inkl. Konzessionsabgaben und `meta.vorbericht_werte.konzessionsabgabe_*`), `vorbericht.investitionszuwendungen` (nur Haushaltsjahr, übrige Jahre „–“, Rest von GFP Z. 18 als „Sonstige (berechnet)“) und `zeilen_namen` direkt lesen; `npm run type-check` belegt die Form.
- Der Orchestrator-Gate (`test_port_wie_format_ts`) muss auf dem Haupt-Checkout laufen (im Worktree übersprungen).

## Self-Check: PASSED

- Gefunden: `daten/manuell/investitionszuwendungen.csv`, alle sechs Commits (`b81b922`, `09e0ce0`, `7bc5929`, `38b631f`, `51bf30c`, `abf4f6c`).
- Akzeptanzkriterien aller drei Tasks erneut ausgeführt, Reproduzierbarkeits-Gate sauber.

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
