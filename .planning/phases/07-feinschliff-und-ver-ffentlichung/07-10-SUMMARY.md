---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 10
subsystem: texte-abnahme-impressum
tags: [du-anrede, vitest, playwright, impressum, datenschutz, abnahme, checkpoint]

requires:
  - phase: 07-03
    provides: "Schwaerzung und Quellenbelege (Bilder, Pruefbericht)"
  - phase: 07-09
    provides: "routen(), Browserbeweis der Barrierefreiheit, Quelle-Leiste"
provides:
  - "duanrede.test.ts: dauerhafte Du-Anrede-Pruefung ueber texte.json, .vue-Templates samt Attributwerten und Stringliterale mit geschlossener Ausnahmeliste AUSNAHMEN"
  - "e2e/textliste.spec.ts (Projekt texte): Textliste je Route nach test-results/textliste.md als Abnahmegrundlage"
  - "Impressum (IMPRESSUM_NAME, IMPRESSUM_ANSCHRIFT) mit den Werten des Nutzers, Test 'veroeffentlichungsbereit' ueber alle vier Konfigurationswerte"
  - "Datenschutz-Satz zur IP-Verarbeitung durch GitHub Pages auf /ueber"
affects: [07-11, 07-12]

actuals:
  tokens: 7100
  tasks: 3
  commits: 2
plan_head_before: d9c29ddd6e920c1deff7475a61752358bb048ced
plan_head_after: b29be89a0797b5846995ecef080fa72d24f13c86

tech-stack:
  added: []
  patterns:
    - "Du-Anrede-Waechter mit geschlossener Ausnahmeliste (Quelle, erste 40 Zeichen des Satzes, Grund '3. Person' oder 'Possessiv'); jede neue Stelle faellt durch"
    - "Veroeffentlichungsbereitschaft als Test ueber die vier Konfigurationswerte (E-Mail, PDF-URL, Impressum-Name, Anschrift)"

key-files:
  created:
    - app/src/lib/__tests__/duanrede.test.ts
    - app/e2e/textliste.spec.ts
  modified:
    - app/src/config.ts
    - app/src/lib/__tests__/config.test.ts
    - app/src/pages/UeberPage.vue

key-decisions:
  - "Commits direkt auf main (git.allow_default_branch_commits: true, vom Nutzer entschieden)"
  - "Texte je Route freigegeben ohne Korrektur; kein Quelltext musste auf Du-Anrede umgestellt werden"
  - "Datenschutz auf /ueber um einen Satz zur IP-Verarbeitung durch GitHub Pages erweitert, ohne Link (reiner Text)"
  - "Schwaerzung der Beispielseiten und der Pruefliste unveraendert bestaetigt; layout.quellenbelege.schwaerzen_nach und die Bilder bleiben unangetastet"
  - "Veroeffentlichung gerenderter Gemeinde-PDF-Seiten ist freigegeben"
  - "Fokus der Quelle-Leiste: WA-Standard beibehalten"

requirements-completed: [UI-06]

coverage:
  - id: D1
    description: "Dauerhafte automatische Du-Anrede-Pruefung ueber alle App-Texte mit geschlossener Ausnahmeliste"
    requirement: "UI-06"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/duanrede.test.ts (32 Tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Textliste je Route als Abnahmematerial (test-results/textliste.md) und Abnahme durch den Nutzer"
    requirement: "UI-06"
    verification:
      - kind: e2e
        ref: "playwright test --project=texte (Docker, Task 1)"
        status: pass
    human_judgment: true
    rationale: "Die Du-Anrede-Heuristik hat Fehlalarme und englische UI-Texte werden nicht automatisch geprueft; die Freigabe der Texte je Route liegt beim Nutzer (D-15) und ist unten festgehalten."
  - id: D3
    description: "Impressum mit Name und Anschrift gesetzt, Veroeffentlichungsbereitschaft per Test gesichert"
    requirement: "UI-06"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#veroeffentlichungsbereit"
        status: pass
    human_judgment: false
  - id: D4
    description: "IP-Satz im Datenschutzabschnitt der Seite /ueber"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#nennt die IP-Verarbeitung durch GitHub Pages (Abnahme 07-10)"
        status: pass
    human_judgment: false

duration: mehrere Sitzungen (Checkpoint-Wartezeit des Nutzers eingeschlossen)
completed: 2026-10-06
status: complete
---

# Phase 7 Plan 10: Du-Anrede-Test, Textliste und Abnahme Summary

**Permanenter Du-Anrede-Waechter (vitest, geschlossene Ausnahmeliste), Textliste je Route per Playwright, vom Nutzer freigegebene Texte, Impressum mit echten Werten und ein Veroeffentlichungsbereitschafts-Test ueber E-Mail, PDF-URL, Name und Anschrift**

## Performance

- **Tasks:** 3 (Task 2 ist der Entscheidungs-Checkpoint, vom Nutzer beantwortet)
- **Files modified:** 5 (2 neu, 3 geaendert)
- **Abschluss dieser Fortsetzung:** 2026-10-06T20:13Z

## Accomplishments

- `duanrede.test.ts` (32 Tests) prueft texte.json, die Template-Teile aller .vue-Dateien samt Attributwerten (aria-label, title, alt, summary, label), versteckte Texte und Stringliterale in Skriptbloecken und `src/**/*.ts` ausserhalb von `__tests__` mit entfernten Kommentaren. RED-Beleg: Der erste Lauf mit leerer Ausnahmeliste scheiterte an genau 8 satzinitialen Treffern (7 in texte.json, 1 in EinnahmenPage.vue). `AUSNAHMEN` enthaelt jetzt 10 Eintraege (9 mal "3. Person", 1 mal "Possessiv"); kein Quellsatz musste auf Du-Anrede korrigiert werden.
- `textliste.spec.ts` (Projekt `texte`, nicht in der CI) schreibt `test-results/textliste.md` mit h1, Lead, Kartentiteln, Callouts, Knopf- und Linktexten, aria-label, alt und versteckten Texten je Route sowie den Texten einer offenen Quelle-Leiste.
- Impressum gesetzt: `IMPRESSUM_NAME = 'Thomas Manthey'`, `IMPRESSUM_ANSCHRIFT = ['Lehmbrock 1', '48346 Ostbevern']`; `KONTAKT_EMAIL` unveraendert. Der Test "veroeffentlichungsbereit" in `config.test.ts` stellt sicher, dass keiner der vier Werte ein Platzhalter ist, auch keine Anschriftzeile.
- Datenschutzabschnitt in `UeberPage.vue` um den freigegebenen Satz ergaenzt: "Beim Aufruf verarbeitet GitHub Pages technisch bedingt deine IP-Adresse; mehr dazu in der Datenschutzerklärung von GitHub." (ohne Link, damit keine handgetippte URL in einer .vue-Datei steht).

## Entscheidungen aus der Abnahme

Die Antworten des Nutzers wurden frageweise erhoben und vom Orchestrator weitergegeben.

- **Commits:** direkt auf main (`git.allow_default_branch_commits: true` in `.planning/config.json`; die Config-Aenderung selbst committet der Orchestrator).
- **(1) Texte je Route:** "Freigegeben" (keine Korrekturen).
- **(2) /ueber:** "Freigeben, mit IP-Satz". Eingefuegt wurde exakt: „Beim Aufruf verarbeitet GitHub Pages technisch bedingt deine IP-Adresse; mehr dazu in der Datenschutzerklärung von GitHub.“ (Vorschlag des Orchestrators, der Nutzer hat nicht widersprochen).
- **(3) Impressum**, Antwort des Nutzers im Wortlaut:

  ```
  Thomas Manthey
  Lehmbrock 1
  48346 Ostbevern
  mail(at)thomas-manthey.de
  ```

  Umsetzung: `IMPRESSUM_NAME = 'Thomas Manthey'`, `IMPRESSUM_ANSCHRIFT = ['Lehmbrock 1', '48346 Ostbevern']`. Die E-Mail-Zeile entspricht der bestehenden Konstante `KONTAKT_EMAIL` (mail@thomas-manthey.de) und bleibt unveraendert.
- **(4) Seitenbilder:** Schwaerzung der Beispielseiten (s072, s127) "bestätigt"; Seite 9 "Freigeben"; Seiten 17, 18, 32, 48, 284 "Alle freigeben". Freigegeben sind damit pro Seite: s072 (Schwaerzung bestaetigt), s127 (Schwaerzung bestaetigt), 9, 17, 18, 32, 48, 284. Keine zusaetzliche Schwaerzung: `layout.quellenbelege.schwaerzen_nach` und die gerenderten Bilder blieben unangetastet. `daten/pruefberichte/quellenbelege.md` wird von der Pipeline erzeugt und hat keine Entscheidungsspalte; sie blieb unveraendert (alle.py reproduziert sie, `git diff` leer).
- **(5) Veroeffentlichung gerenderter Gemeinde-PDF-Seiten:** "Ja, veröffentlichen".
- **(6) Fokus der Quelle-Leiste:** "WA-Standard beibehalten". `QuelleSeitenleiste.vue` und `quelle.spec.ts` blieben unveraendert.

Die Antwort enthaelt die Freigabe ("freigegeben") und die Impressum-Daten; die Vorbedingung von Task 3 war damit erfuellt.

## Task Commits

1. **Task 1: Du-Anrede-Test und Textliste je Route** - `560befa` (test)
2. **Task 2: Abnahme-Checkpoint (blocking-human)** - kein Commit; vom Nutzer beantwortet (siehe oben)
3. **Task 3: Abnahme einarbeiten, Impressum setzen, Bereitschaft pruefen** - `b29be89` (feat)

**Plan metadata:** wird mit diesem SUMMARY committet (docs: complete plan)

## Files Created/Modified

- `app/src/lib/__tests__/duanrede.test.ts` - Scanner, Regeln, `AUSNAHMEN`, fail-first-Beispiele
- `app/e2e/textliste.spec.ts` - Textliste je Route nach `test-results/textliste.md`
- `app/src/config.ts` - Impressum-Name und -Anschrift gesetzt, Kommentare angepasst
- `app/src/lib/__tests__/config.test.ts` - Test "veroeffentlichungsbereit" (ersetzt den Platzhalter-bis-zum-Checkpoint-Test), Test auf den IP-Satz
- `app/src/pages/UeberPage.vue` - IP-Satz im Datenschutzabschnitt; es wurde kein anderer UI-Text einer .vue- oder .ts-Datei korrigiert

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Alter Test haette nach dem Setzen des Impressums fehlgeschlagen**
- **Found during:** Task 3
- **Issue:** `config.test.ts` behauptete bis zum Checkpoint, dass Name und Anschrift Platzhalter sind (`toBe(true)`); mit den echten Werten waere der Test rot.
- **Fix:** Durch den geforderten Test "veroeffentlichungsbereit" ersetzt (gleiche Funktionen, umgekehrte Aussage, zusaetzlich jede Anschriftzeile einzeln).
- **Files modified:** app/src/lib/__tests__/config.test.ts
- **Verification:** `config.test.ts` gruen, vitest gesamt 1956 Tests gruen.
- **Committed in:** b29be89

**2. [Rule 2 - Missing Critical] Test fuer den neuen IP-Satz**
- **Found during:** Task 3
- **Issue:** Die Datenschutzaussage von D-08 ist durch einen Test abgesichert; der neue Satz sollte nicht ungeschuetzt bleiben.
- **Fix:** Test "nennt die IP-Verarbeitung durch GitHub Pages (Abnahme 07-10)" in `config.test.ts`; der bestehende Test auf die D-08-Aussage bleibt unveraendert gruen.
- **Committed in:** b29be89

### Verfahrensnotiz (keine Abweichung im Code)

main ist ein geschuetzter Branch; der erste Commit-Versuch wurde deshalb vom Guard abgelehnt. Der Nutzer hat direkte Commits auf main erlaubt (`git.allow_default_branch_commits: true`).

---

**Total deviations:** 2 auto-fixed (1 Rule 1, 1 Rule 2)
**Impact on plan:** Beide notwendig fuer Korrektheit, kein Scope Creep.

## Issues Encountered

- `npm ci` im Hauptcheckout ist wegen des Host-Ordners (macOS-Binaries) tabu; alle App-Pruefungen liefen in einer Kopie ohne node_modules im Scratchpad, Playwright nur ueber das Docker-Image. Die Kopie wird nicht eingecheckt.
- Prettier setzte den Zeilenumbruch des neuen Datenschutzsatzes in `UeberPage.vue` anders um; die formatierte Fassung wurde uebernommen (`format:check` gruen).

## Gates (nach der Abnahme)

- `uv run --directory pipeline pytest -q`: 631 passed
- `uv run --directory pipeline python alle.py --jahr 2026`: erfolgreich (Schritt 08: 2496 Belege, 0 Bilder neu gerendert); `git diff --stat --exit-code -- daten app/src/data` leer, `git status` fuer `daten`, `app/src/data`, `app/public/quellen` leer
- App-Kette in der Kopie: `type-check`, `lint`, `format:check` gruen; `test` 44 Dateien, 1956 Tests gruen; `build` gruen
- `playwright test --project=ci` (Docker, v1.63.0-noble): 43 passed
- Akzeptanzkriterien: `grep veröffentlichungsbereit` in config.test.ts und "Entscheidungen aus der Abnahme" in dieser Datei: erfuellt

## Known Stubs

Keine.

## Threat Flags

Keine neue Angriffsflaeche. T-07-21 (Freigabe vor Commit, Antwort protokolliert), T-07-22 (Pruefliste vom Nutzer freigegeben, Seiten nur per Nummer genannt, kein Personenname im Material) und T-07-23 (Bereitschaftstest) sind umgesetzt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Impressum und Texte sind freigegeben; 07-11 (Smoke-Test, CI-Schritt, Deploy auf GitHub Pages) kann den Platzhalter-Check scharf schalten.
- Offen fuer den Orchestrator: die Config-Aenderung `git.allow_default_branch_commits` in `.planning/config.json` ist nicht committet.

## Self-Check: PASSED

- FOUND: app/src/lib/__tests__/duanrede.test.ts, app/e2e/textliste.spec.ts
- FOUND: commits 560befa, b29be89 (Vorfahren von HEAD)

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
