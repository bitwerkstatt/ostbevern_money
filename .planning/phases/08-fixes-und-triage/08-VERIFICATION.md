---
phase: 08-fixes-und-triage
verified: 2026-10-09T06:03:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - .planning/milestones/v1.0-phases/01-setup/01-REVIEW-DISPOSITION.md
  - .planning/milestones/v1.0-phases/05-leitfragen-seiten/05-REVIEW-DISPOSITION.md
  - .planning/milestones/v1.0-phases/06-kontext-seiten/06-REVIEW-DISPOSITION.md
  - .planning/phases/08-fixes-und-triage/08-01-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-01-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-02-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-02-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-03-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-03-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-04-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-04-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-05-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-05-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-06-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-06-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-07-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-07-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-08-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-08-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-09-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-09-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-10-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-10-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-11-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-11-SUMMARY.md
  - .planning/phases/08-fixes-und-triage/08-12-PLAN.md
  - .planning/phases/08-fixes-und-triage/08-12-SUMMARY.md
  - app/e2e/menueDrawer.ts
  - app/e2e/mobil.spec.ts
  - app/e2e/tabellenrahmen.ts
  - app/src/App.vue
  - app/src/charts/format.ts
  - app/src/components/DatenTabelle.vue
  - app/src/components/EbenenTabelle.vue
  - app/src/components/ZuschussListe.vue
  - app/src/components/__tests__/zustaende.test.ts
  - app/src/components/datenTabelle.ts
  - app/src/data/texte.json
  - app/src/lib/__tests__/geldfluss.test.ts
  - app/src/lib/__tests__/quelltext.test.ts
  - app/src/lib/berechnung.ts
  - app/src/lib/einwohner.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/zuschuesse.ts
  - daten/manuell/texte/erklaerungen.md
  - daten/manuell/texte/glossar.md
  - pipeline/ostbevern/texte.py
covered_digest: "v3:sha256:eda89fecc881b201b8c8414b1af70f57707120b97609a020956d158c488dcb11"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5 must-haves verified
  gaps_closed:
    - "08/WR-01: Rendertests für leere Beschriftung konnten nicht fehlschlagen; die Regel steht jetzt als reine Funktion tabellenRahmen mit Unit-Tests, die vor dem Fix rot waren (Fix 78744d4, Test 8b4ae20)"
    - "08/WR-02: Rahmen einer überlaufenden Tabelle verlor bei leerer Beschriftung den Tabstopp; jetzt hat er für jede Beschriftung Fokus, Rolle und Namen, leer heißt die Caption „Tabelle“ (Fix 78744d4)"
  gaps_remaining: []
  regressions: []
coincidental_reliance_items:
  - truth: "Jahreszahlen, abgeleitete und fehlende Werte sind erkennbar (SC 2)"
    reason: undeclared-precondition
    harden: "Relative Jahres-Platzhalter in erklaerungen.md/glossar.md stehen neben Werten mit festem Jahr im Schlüssel. Seit WR-01 (e8e25d5) prüft _pruefe_jahrbezug, dass ein jahr.*-Platzhalter im Absatz auf dasselbe Jahr auflöst wie die Wertschlüssel. Die Prüfung arbeitet mengenweise je Absatz, nicht paarweise (08-REVIEW IN-03). Beim Bau von Jahrgang 2027 prüfen, ob das reicht."
human_verification:
  - test: "Screenreader-Ansage des Tabellennamens bei 360 px auf /ausgaben (VoiceOver oder NVDA): in eine Datentabelle navigieren, deren Rahmen scrollt"
    expected: "Der Name der Tabelle wird beim Betreten von Region und Tabelle nicht störend doppelt vorgelesen (A11Y-03). Wird er es, soll nur eines der beiden Elemente (Region oder Caption) den Namen tragen."
    why_human: "DOM und ARIA-Baum sind per Playwright belegt (genau ein aria-labelledby, kein aria-label, eindeutige Regionnamen). Ob ein Screenreader Region und Tabelle trotzdem nacheinander ansagt, ist RESEARCH-Annahme A1 und lässt sich ohne echten Screenreader nicht prüfen. Vom Nutzer in `08-UAT.md` Test 1 bestanden (result: pass, 2026-10-08, Commit dd77df1)."
    beleg: "UAT 08 Test 1 (pass, Nutzer, 2026-10-08)"
    verifier_geprueft: "nein"
    hinweis: "Der Verifier hat DOM und ARIA-Baum geprüft (Playwright, genau ein Name je Rahmen); das Vorleseverhalten mit einem echten Screenreader hat der Nutzer bestätigt"
---

# Phase 8: Fixes und Triage Verification Report

**Phase Goal:** Alles, was die App in Worten über Zahlen sagt, stimmt auch in Grenzfällen, und Datentabellen und das mobile Menü funktionieren für Screenreader und Touch ohne Lücken. Jeder der 28 offenen Review-Befunde aus den Phasen 1, 5 und 6 ist behoben, übersprungen oder begründet zurückgestellt, und das ist im jeweiligen Ledger belegt. Reihenfolge: zuerst Fixes an Zahlen und Texten, dann Barrierefreiheit und Hygiene, zum Schluss die Ledger auf `open: 0`.
**Verified:** 2026-10-09T06:03:00Z
**Status:** passed (die Screenreader-Ansage für A11Y-03 bleibt ein offener menschlicher Check in `08-UAT.md`, Test 1)
**Re-verification:** Ja. Die Verifikation vom 2026-10-08 war nach dem D-20-Fix aus Plan 09-02 veraltet (Änderung an `DatenTabelle.vue`, `datenTabelle.ts` und den Tests). Frühere Re-Verifikation: Stand nach den Review-Fixes WR-01..WR-03 (e8e25d5, 13eb786, 98803c4) und den Nyquist-Tests (7b9f0a6), geprüft gegen HEAD 90f8315. Diese Fassung ergänzt den Abschnitt „Re-Verifikation 09-02 (D-15)“ unten.

## Goal Achievement

Der Code erreicht das Phasenziel, auch nach den Review-Fixes. Es gibt keine fehlgeschlagene Wahrheit, keinen Stub und keinen Blocker. Offen bleibt ein menschlicher Check: die Screenreader-Ansage für A11Y-03.

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | Sätze über Zahlen stimmen in Grenzfällen: Lesehilfe sagt „genau“ nur bei echtem Ausgleich, Minderaufwand-Hinweis nie negativ, `rd.`-Regel an genau einer Stelle | ✓ VERIFIED | `lesehilfeSatz` (`app/src/lib/geldfluss.ts`) unterscheidet vier Fälle (A Defizit, B Überschuss, C nur Minderaufwand, D nichts). „genau“ steht nur in Fall D. Fall C sagt, dass erst der Minderaufwand beide Seiten ausgleicht. `minderaufwandBetrag` (`lib/berechnung.ts`) liefert `null` bei 0 oder fehlendem Wert, den positiven Betrag bei negativem Z. 27 und wirft bei Z. 27 > 0. `RD_PRAEFIX` und `RUND_PRAEFIX` stehen im App-Code nur in `charts/format.ts`. Ein Grep nach `'rd. '`-Literalen und Templates außerhalb von Tests findet keine Altkopie. vitest in Scratch-Kopie auf HEAD: 2158 Tests grün. |
| 2 | Jahreszahlen, abgeleitete und fehlende Werte sind erkennbar | ✓ VERIFIED (coincidental-reliance) | Eigener Aufruf von `pruefe_text` auf HEAD: „Im Jahr 2026“, „Seit 1900“ und „Bis 2099“ lehnt er mit der Meldung „Handgetippte Jahreszahl … nur als Platzhalter, zum Beispiel {{jahr.haushaltsjahr\|jahr}}“ ab. `{{jahr.haushaltsjahr\|jahr}}` besteht, `{{jahr.haushaltsjahr\|zahl}}` scheitert am Kürzel. 2100 fällt in die Regel „nackte Ziffer“. Der WR-01-Fix `_pruefe_jahrbezug` (`texte.py:585`) ist in `loese_auf` verdrahtet (`:631`). `ZuschussListe` zeigt die Zusammen-Zeile über `zusammen().berechnet` mit Etikett. `StellenplanPage` setzt `berechnet` auf allen drei Kacheln und nennt über `seitenText` nur deren Seiten. `EbenenTabelle.vue` ruft im Modus `zuschussbedarf` `einwohnerZahl()` auf, die bei fehlendem oder ungültigem Wert wirft. Wirkung gilt nur für Jahrgang 2026, siehe `coincidental_reliance_items`. |
| 3 | `DatenTabelle`-Rahmen hat Rolle und Namen, kein doppelter Name; Menü schließt beim Link der aktuellen Seite | ✓ VERIFIED | `tabellenRahmen` (seit 09-02, ruft `rahmenAttribute`) liefert bei Überlauf `tabindex`, `role=region` und `aria-labelledby` auf die Caption, nie `aria-label`, und zwar für jede `beschriftung`: leer oder nur Leerzeichen heißt die Caption „Tabelle“. `beschriftung` ist Pflicht-Prop. Alle 29 `<DatenTabelle>`-Aufrufe übergeben sie (Grep), keiner leer. `App.vue` `beiDrawerLinkKlick` schließt bei jedem Primärklick im offenen Drawer, ignoriert Strg/Meta/Shift/Alt und Nicht-Primärtasten (WR-02-Fix), `oeffneDrawer` setzt den Merker zurück. `beiAfterHide` setzt den Fokus auf die h1. Playwright (Orchestrator auf HEAD über `scripts/e2e-wie-ci.sh`): mobil 41, ci 89 grün, darunter „Link der aktuellen Seite“, Zusatztasten-Fall und alle Tabellenrahmen-Tests mit axe. Die Screenreader-Ansage bleibt menschlicher Check. |
| 4 | Ledger 01, 05, 06 stehen auf `open: 0`, jede Zeile nennt Commit oder Begründung | ✓ VERIFIED | Eigene Prüfung: `open: 0` in allen drei Dateien (total 10, 18, 15). Keine Zeile mehr mit `disposition: open` und keine Tabellenzeile `open`. Alle Zeilen `fixed`, bis auf 06/WR-01 `skipped` mit Verweis auf UAT 06 Test 1 und PROJECT.md. Jeder zitierte 7-stellige Hash wird von `git cat-file -e` als Commit erkannt, keiner fehlt. Die 28 Befunde (5 + 13 + 10) sind abgedeckt. Die Zusatzzeilen in 05 und 06 sind bereits im Fix-Stand behobene Altbefunde. |
| 5 | Querschnittsbedingung: `alle.py --jahr 2026` byte-identisch, Regeln 1–10 grün, CI-Kette grün | ✓ VERIFIED | Eigener Lauf auf HEAD nach WR-01: `uv run --directory pipeline python alle.py --jahr 2026` Exit 0, Regeln 1–10 „grün“ in Schritt 06, danach `git diff --stat --exit-code -- daten app/src/data` leer und `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` leer. pytest gesamt: 681 passed. ruff check und ruff format --check grün. vitest 2158 grün (eigener Lauf, Scratch). type-check, lint, format, build und Playwright: Messung des Orchestrators auf HEAD (grün). |

**Score:** 5/5 truths verified (0 behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/src/charts/format.ts` | einzige `rd.`/`rund`-Regel | ✓ VERIFIED | `betragMitHinweis`, `kurzMitHinweis`, `rundMitHinweis`, `rundKurz` |
| `app/src/lib/berechnung.ts` | `minderaufwandBetrag` | ✓ VERIFIED | nie negativ, wirft bei positivem Z. 27 |
| `app/src/lib/geldfluss.ts` | `lesehilfeSatz` mit vier Fällen | ✓ VERIFIED | Fälle A bis D |
| `app/src/lib/einwohner.ts` | `einwohnerZahl` wirft laut | ✓ VERIFIED | genutzt in `EbenenTabelle.vue` |
| `app/src/lib/zuschuesse.ts` | `zusammen()` mit `berechnet` | ✓ VERIFIED | genutzt in `ZuschussListe.vue` |
| `app/src/components/DatenTabelle.vue`, `datenTabelle.ts` | Rolle und ein Name, Ersatzname für leere Beschriftung | ✓ VERIFIED | `tabellenRahmen` und `ERSATZ_BESCHRIFTUNG` in `datenTabelle.ts`, `rahmenLage` in `DatenTabelle.vue`, DEV-Warnung bleibt (09-02) |
| `app/src/App.vue` | Drawer schließt bei jedem Link | ✓ VERIFIED | `beiDrawerLinkKlick` mit Zusatztasten-Guard |
| `pipeline/ostbevern/texte.py` | Jahreszahlen-Regel, Jahresbezug-Prüfung | ✓ VERIFIED | `_JAHRESZAHL_MUSTER`, `_pruefe_jahrbezug` verdrahtet |
| `app/e2e/menueDrawer.ts`, `tabellenrahmen.ts`, `mobil.spec.ts` | Browser-Prüfung A11Y-01/02/03 | ✓ VERIFIED | vorhanden, Orchestrator-Lauf grün |
| Ledger 01/05/06 | `open: 0` | ✓ VERIFIED | siehe Truth 4 |

### Key Link Verification

| From | To | Via | Status |
| ---- | -- | --- | ------ |
| `EuroBetrag.vue` und die übrigen Verbraucher | `charts/format.ts` | `betragMitHinweis`, `kurzMitHinweis`, `rundMitHinweis` | WIRED |
| `geldfluss.ts`, `aufwandsarten.ts` | `berechnung.minderaufwandBetrag` | Aufruf | WIRED |
| `DatenTabelle.vue` | `datenTabelle.tabellenRahmen` | `v-bind` am Rahmen und Caption-Text aus `rahmenLage` | WIRED |
| `App.vue` Drawer-Links | `beiDrawerLinkKlick` | `@click` | WIRED |
| `ZuschussListe.vue` | `zusammen().berechnet` | `EuroBetrag :berechnet` | WIRED |
| `StellenplanPage.vue` | `stellenSummen().seiten*` | `kachelZeile`, `seitenText` | WIRED |
| `texte.loese_auf` | `_pruefe_jahrbezug` | Aufruf je Absatz (`:631`) | WIRED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| `pruefe_text` lehnt Jahre ab | Python-Aufruf mit 2026, 1900, 2099, Platzhalter mit `zahl` | 2026/1900/2099 und `zahl`-Kürzel werfen, Platzhalter `jahr` besteht | ✓ PASS |
| Pipeline-Tests | `uv run --directory pipeline pytest -q` | 681 passed | ✓ PASS |
| Lint und Format Pipeline | `ruff check .` und `ruff format --check .` | grün | ✓ PASS |
| App-Unit-Tests | `npx vitest run` (Scratch, rsync von HEAD) | 2158 passed | ✓ PASS |
| Reproduzierbarkeit | `alle.py --jahr 2026`, dann `git diff` und `git status` auf `daten`, `app/src/data`, `app/public/quellen` | Exit 0, kein Diff, keine neuen Dateien | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED. Die Phase deklariert keine `probe-*.sh`-Skripte.

### Requirements Coverage

Alle 13 IDs aus den PLAN-Frontmatter (08-01 bis 08-12) stehen in `REQUIREMENTS.md` und im ROADMAP-Eintrag der Phase. Es gibt keine verwaisten IDs.

| Requirement | Source Plan | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| TXT-01 | 08-02 | ✓ SATISFIED | `lesehilfeSatz` vier Fälle |
| TXT-02 | 08-02 | ✓ SATISFIED | `minderaufwandBetrag`, nie negativ |
| TXT-03 | 08-01 | ✓ SATISFIED | `pruefe_text`, `_pruefe_jahrbezug`, eigener Aufruf |
| TXT-04 | 08-02, 08-04, 08-05, 08-07 | ✓ SATISFIED | Regel nur in `format.ts` |
| TXT-05 | 08-03, 08-05 | ✓ SATISFIED | Etikett und Seiten je Kachel (Umfang: Kontextseiten) |
| TXT-06 | 08-03 | ✓ SATISFIED | `einwohnerZahl()` wirft laut |
| A11Y-01 | 08-06 | ✓ SATISFIED | Rolle und Name bei Überlauf, Pflicht-`beschriftung`, Guard |
| A11Y-02 | 08-06 | ✓ SATISFIED | Drawer schließt bei jedem Link, e2e grün |
| A11Y-03 | 08-06 | ✓ SATISFIED | Ein Name im DOM belegt (Playwright, mobil.spec.ts „Rahmen mit Rolle und genau einem Namen“); Screenreader-Ansage vom Nutzer bestanden (08-UAT.md Test 1, pass, 2026-10-08), nicht vom Verifier geprüft |
| TRI-01 | 08-12 | ✓ SATISFIED | Ledger 01 `open: 0` |
| TRI-02 | 08-12 | ✓ SATISFIED | Ledger 05 `open: 0` |
| TRI-03 | 08-12 | ✓ SATISFIED | Ledger 06 `open: 0`, 06/WR-01 `skipped` mit UAT-Begründung |
| TRI-04 | 08-06 bis 08-12 | ✓ SATISFIED | Hygiene-Befunde behoben, Commits im Ledger |

Hinweis zur Nachführung: In `REQUIREMENTS.md` stehen alle 13 Einträge noch als `[ ]` und „Pending“, und `ROADMAP.md` führt Phase 8 als „In Progress“. Das ist Sache des Orchestrators beim Phasenabschluss, kein Codebefund.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (geänderte Dateien) | - | `TBD`, `FIXME`, `XXX` | none | keine Treffer |
| `app/src/components/DatenTabelle.vue` | 127-144 | (behoben in 09-02, 78744d4) Bei leerer `beschriftung` verlor ein überlaufender Rahmen `tabindex` (08-REVIEW WR-02) | ✓ geschlossen | Der Rahmen ist jetzt für jede Beschriftung erreichbar und benannt |
| `app/src/components/__tests__/zustaende.test.ts` | 165-189 | (behoben in 09-02, 8b4ae20 und 78744d4) Zwei SSR-Rendertests konnten nicht fehlschlagen (08-REVIEW WR-01) | ✓ geschlossen | Ersetzt durch Unit-Tests von `tabellenRahmen` und einen SSR-Test der Ersatz-Caption; vor dem Fix rot |
| `app/src/lib/__tests__/quelltext.test.ts`, `app/e2e/menueDrawer.ts`, `pipeline/ostbevern/texte.py` | siehe Review | IN-01 bis IN-03 aus 08-REVIEW | ℹ️ Info | Test-Nits und Docstring-Präzision, kein Zielverhalten betroffen |

`08-REVIEW-DISPOSITION.md` stand bei der früheren Fassung mit 9 Zeilen auf `open`. Seit Plan 09-02 (D-20) steht es auf `open: 0`: WR-01, WR-02 und IN-01 sind `fixed` mit Commit-Hash, IN-02 bis IN-07 `deferred` mit Begründung.

### Human Verification Required

#### 1. Screenreader-Ansage des Tabellennamens (A11Y-03)

**Test:** In VoiceOver oder NVDA bei 360 px Breite `/ausgaben` öffnen und mit dem Screenreader in eine Datentabelle navigieren, deren Rahmen horizontal scrollt.
**Expected:** Der Tabellenname wird nicht störend doppelt vorgelesen (Region plus Caption). Wird er doppelt vorgelesen, soll nur eines der beiden Elemente den Namen tragen (Fallback der UI-SPEC).
**Why human:** Playwright belegt genau einen Namen im ARIA-Baum. Das Vorleseverhalten realer Screenreader ist RESEARCH-Annahme A1 und nicht automatisiert prüfbar. Der Eintrag steht unverändert in `08-UAT.md` (Test 1, `result: [pending]`).

### Offene Punkte, keine Gaps

- **Steuergruppen auf Leitfragen-Seiten** („Grundsteuer (A+B)“ auf `/geldfluss`, `/einnahmen`) sind von der App gebildete Summen ohne „berechnet“-Etikett. TXT-05 und SC 2 beschränken sich auf die Kontextseiten, ein Test sichert den Zustand bewusst. Entscheidung des Nutzers, ob die Regel dort auch gelten soll.
- **Feste Jahre in Text-Schlüsseln:** `_pruefe_jahrbezug` fängt auseinanderlaufende Beschriftung und Wertschlüssel jetzt ab (mengenweise je Absatz). Vor dem Bau des nächsten Jahrgangs gegenprüfen.
- **Vier ältere Befunde aus Ledger 05** außerhalb der 28 stehen laut 08-12 SUMMARY noch im Code. Sie gehören nicht zum Umfang dieser Phase.
- **08-REVIEW WR-02** (leere `beschriftung` ohne Tastaturfokus): in Plan 09-02 behoben, der Rahmen fällt auf den Ersatznamen „Tabelle“ zurück (siehe unten).

### Gaps Summary

Keine Lücken. Alle fünf Success Criteria sind am Code auf HEAD belegt, auch durch eigene Läufe von pytest (681), ruff, vitest (2158), `pruefe_text`-Aufrufen und der Pipeline-Reproduzierbarkeit nach WR-01. Playwright (mobil 41, ci 89) und die übrigen App-Prüfungen (type-check, lint, format, build) stützen sich auf die Messung des Orchestrators auf HEAD. Der Status ist `human_needed`, weil die Screenreader-Ansage für A11Y-03 nur ein Mensch mit einem echten Screenreader prüfen kann.

## Re-Verifikation 09-02 (D-15)

Anlass: Plan 09-02 hat `DatenTabelle.vue`, `datenTabelle.ts`, `zustaende.test.ts` und `quelltext.test.ts` geändert (D-20), die Fassung vom 2026-10-08 war damit veraltet.

**Änderung:** Neue reine Funktion `tabellenRahmen` mit `ERSATZ_BESCHRIFTUNG` in `datenTabelle.ts`; `DatenTabelle.vue` nutzt sie für Caption-Text und Rahmenattribute. Test-Commit 8b4ae20 (rot), Fix-Commit 78744d4. `git diff --stat 90f8315..HEAD` über alle bisher abgedeckten Dateien (`app`, `daten`, `pipeline` und die drei Ledger 01/05/06) zeigt genau vier geänderte Dateien: `DatenTabelle.vue`, `datenTabelle.ts`, `__tests__/zustaende.test.ts`, `__tests__/quelltext.test.ts`. Kein Eingriff in `daten/`, `app/src/data/` oder `pipeline/`.

**Wirkung auf die Success Criteria:** SC 1, 2, 4 und 5 sind unberührt (kein Zahlen-, Text- oder Pipelinecode geändert, Ledger 01/05/06 unverändert). SC 3 gilt stärker als vorher: Der überlaufende Rahmen hat Rolle und Namen auch ohne `beschriftung`. Daher bleibt der Score bei 5/5.

**Belege (Scratch-Kopie von `app/`, Linux-`node_modules` über `npm ci`):**

- vitest gesamt: 2162 Tests grün (zuvor 2158; Saldo aus 8 neuen und 4 entfernten Tests). RED belegt: 8 Tests rot vor dem Fix (`TypeError: tabellenRahmen is not a function` und leere Caption), `check tdd-red-evidence` meldet `RED_EVIDENCE_OK` auf dem JUnit-Bericht.
- `vue-tsc --build`, `eslint .`, `prettier --check src/ e2e/`: ohne Befund.
- `vite build` (`build-only`): erfolgreich.
- Playwright über `scripts/e2e-wie-ci.sh`: Projekt `mobil` 41 grün (darunter alle „Rahmen mit Rolle und genau einem Namen“-Tests und axe auf allen Routen), `interaktion.spec.ts` plus `smoke.spec.ts` im Projekt `ci` 62 grün.
- Ledger: `08-REVIEW-DISPOSITION.md` `open: 0`, `total: 10`.

`covered_files` und `covered_digest` stammen unverändert aus `verification.fingerprint`. Die Screenreader-Ansage (A11Y-03) bleibt offen in `08-UAT.md` und ist keine Folge dieser Änderung.

## Nachtrag 09-15 (D-12)

Stand 2026-10-09. Nach dem Basislauf (head `1d0df35da1842daec515b40dd62f8d918e240105`) hat Plan 09-14 in `448e43d` (Lücke G-09-03, Test `b3b2658`) `app/src/lib/geldfluss.ts` geändert, eine vom Bericht abgedeckte Datei; `verification.status` meldete deshalb wieder `stale`. Änderung: `berechnet: gruppe.posten.length > 1` statt `berechnet: false` an den Steuergruppen in `baueGeldfluss`, dazu ein Kommentar und die Doku des Feldes. Die Gruppensumme „Grundsteuer (A+B)“ trägt jetzt das Etikett „berechnet“; Beträge, Bilanz und `lesehilfeSatz` sind unverändert.

| Commit | Geänderte abgedeckte Datei | Betroffene Wahrheit | Test |
|--------|----------------------------|---------------------|------|
| `448e43d` | `app/src/lib/geldfluss.ts` | SC 2 („abgeleitete und fehlende Werte sind erkennbar“) wird stärker: eine von der App gebildete Summe ist jetzt als „berechnet“ erkennbar. SC 1 (`lesehilfeSatz` mit vier Fällen) ist unberührt, die Funktion steht nicht im Diff. SC 3 bis 5 sind nicht betroffen | `geldfluss.test.ts` „G-09-03“ (sechs Jahre), vorher rot in `b3b2658`; `lesehilfeSatz`-Tests in `geldfluss.test.ts:437` und `:487` weiter grün |

Nachprüfung in einer Scratch-Kopie von `app/` mit Linux-`node_modules` (`npm ci`) auf dem Stand `7e2b775`: `geldfluss`, `berechnung`, `rdregel`, `quelltext`, `zustaende` und `einwohner` zusammen 419 Tests grün; die volle App-Suite 2207 Tests grün (zuvor 2162). Keine Wahrheit gebrochen, kein Gap, keine Regression; der Score bleibt 5/5 und der Status `passed`. Die Screenreader-Ansage (A11Y-03) bleibt offen in `08-UAT.md` und ist keine Folge dieser Änderung. Der volle Lauf der CI-Kette auf dem Endstand (SC 5) steht im Abschnitt „Abschlusslauf“ von `.planning/v1.0-MILESTONE-AUDIT.md`.

`covered_files` und `covered_digest` stammen unverändert aus `verification.fingerprint`, mit den bisherigen Implementierungsdateien plus `app/src/lib/__tests__/geldfluss.test.ts`.

---

_Verified: 2026-10-09T06:03:00Z_
_Verifier: Claude (gsd-verifier)_
