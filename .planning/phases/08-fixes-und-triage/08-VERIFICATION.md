---
phase: 08-fixes-und-triage
verified: 2026-10-07T22:10:00Z
status: human_needed
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
  - app/e2e/mobil.spec.ts
  - app/e2e/tabellenrahmen.ts
  - app/src/App.vue
  - app/src/charts/format.ts
  - app/src/components/DatenTabelle.vue
  - app/src/components/EbenenTabelle.vue
  - app/src/components/EuroBetrag.vue
  - app/src/components/ZuschussListe.vue
  - app/src/components/datenTabelle.ts
  - app/src/lib/__tests__/rdregel.test.ts
  - app/src/lib/berechnung.ts
  - app/src/lib/einwohner.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/stellen.ts
  - app/src/lib/zuschuesse.ts
  - app/src/pages/StellenplanPage.vue
  - daten/manuell/texte/erklaerungen.md
  - pipeline/ostbevern/texte.py
covered_digest: "v3:sha256:dbc09878b36f31462969eddb7809626eb0ce7ad5f545fe8625e29e6e4f6a5f0d"
behavior_unverified: 0
overrides_applied: 0
coincidental_reliance_items:
  - truth: "Jahreszahlen in Texten sind nur über Platzhalter möglich und stimmen im Bestand (Truth 2)"
    reason: undeclared-precondition
    harden: "Die Bestandstexte koppeln relative Jahres-Platzhalter ({{jahr.vorjahr|jahr}}) mit Wert-Schlüsseln mit festem Jahr (schulden.gesamt.2025, ve.faellig.2027, vorbericht.steuerarten.gewerbesteuer.2024). Die Aussage stimmt nur, solange der Jahrgang 2026 ist. Entweder relative Wert-Schlüssel einführen oder eine Pipeline-Prüfung, die Label-Jahr und Schlüssel-Suffix abgleicht (08-REVIEW WR-01)."
human_verification:
  - test: "Screenreader-Ansage des Tabellennamens bei 360 px auf /ausgaben (VoiceOver oder NVDA): in eine Datentabelle navigieren, deren Rahmen scrollt"
    expected: "Der Name der Tabelle wird beim Betreten von Region und Tabelle nicht störend doppelt vorgelesen (A11Y-03). Wird er es, soll nur eines der beiden Elemente (Region oder Caption) den Namen tragen."
    why_human: "DOM und ARIA-Baum sind per Playwright belegt (genau ein aria-labelledby, kein aria-label, eindeutige Regionnamen). Ob ein Screenreader Region und Tabelle trotzdem nacheinander ansagt, ist RESEARCH-Annahme A1 und lässt sich ohne echten Screenreader nicht prüfen."
---

# Phase 8: Fixes und Triage Verification Report

**Phase Goal:** Alles, was die App in Worten über Zahlen sagt, stimmt auch in Grenzfällen, und Datentabellen und das mobile Menü funktionieren für Screenreader und Touch ohne Lücken. Jeder der 28 offenen Review-Befunde aus den Phasen 1, 5 und 6 ist behoben, übersprungen oder begründet zurückgestellt, und das ist im jeweiligen Ledger belegt.
**Verified:** 2026-10-07T22:10:00Z
**Status:** human_needed
**Re-verification:** No, initial verification

## Goal Achievement

Der Code erreicht das Phasenziel. Es gibt keine fehlgeschlagene Wahrheit, keinen Stub und keinen offenen Blocker. Offen bleibt ein menschlicher Check: die Screenreader-Ansage für A11Y-03. Er war schon in der Planung als manuell vorgesehen.

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | Sätze über Zahlen stimmen in Grenzfällen: Lesehilfe sagt „genau“ nur bei echtem Ausgleich, Minderaufwand-Hinweis nie negativ, `rd.`-Regel an genau einer Stelle | ✓ VERIFIED | `lesehilfeSatz` (`app/src/lib/geldfluss.ts:652-695`) unterscheidet vier Fälle. „genau“ steht nur im Zweig ohne Defizit, Überschuss und Minderaufwand. Fall C (nur Minderaufwand) sagt, dass erst er die Seiten ausgleicht. `minderaufwandBetrag` (`lib/berechnung.ts:33`) liefert nie einen negativen Betrag, `null` bei 0 oder fehlend, wirft bei Z. 27 > 0. Beide Verbraucher (`geldfluss.ts:249`, `aufwandsarten.ts:177`) nutzen sie. `RD_PRAEFIX` und `RUND_PRAEFIX` stehen nur in `charts/format.ts` (per `od` geprüft: U+00A0). Außer `format.ts` baut keine App-Datei den Vorsatz, und der Wächter `rdregel.test.ts` erzwingt das über alle `src/**/*.{ts,vue}`. Vitest in Scratch-Kopie: 49 Dateien, 2153 Tests grün (Code identisch zu HEAD). |
| 2 | Jahreszahlen, abgeleitete und fehlende Werte sind erkennbar: `pruefe_text` lehnt 1900-2099 ab, „berechnet“-Etikett, Stellenplan-Quellzeile, EbenenTabelle meldet fehlende Einwohnerzahl | ✓ VERIFIED (coincidental-reliance) | `pipeline/ostbevern/texte.py:45` `\b(?:19\|20)\d{2}\b` in `pruefe_text`, mit Meldung, Abschnitt und Ausweg. Im Namensraum `jahr.` ist nur das Kürzel `jahr` erlaubt. pytest `test_texte.py` und `test_app_daten.py`: 146 grün, darunter 1900, 2099 und 1990er. In den Texten stehen keine getippten Jahre mehr. `ZuschussListe` zeigt „Zusammen“ über `EuroBetrag` mit Etikett nur bei `zusammen().berechnet`, die Filtersumme auf `/investitionen` trägt `BerechnetEtikett`, `StellenplanPage` setzt auf allen drei Kacheln `berechnet` und `lib/stellen.ts:143-145` liefert die Seiten je Kachel. `einwohnerZahl()` wirft bei fehlendem oder ungültigem Wert und `EbenenTabelle.vue:52` ruft sie auf. Die Wirkung gilt nur für Jahrgang 2026, siehe Hinweis unten. |
| 3 | `DatenTabelle`-Rahmen hat Rolle und Namen, kein doppelter Name; Menü schließt beim Link der aktuellen Seite | ✓ VERIFIED | `rahmenAttribute` (`components/datenTabelle.ts`) liefert bei Überlauf immer `tabindex=0`, `role=region` und `aria-labelledby` auf die Caption, nie `aria-label`. `beschriftung` ist Pflicht-Prop und alle 29 Aufrufe übergeben sie. `App.vue:69` `beiDrawerLinkKlick` schließt bei jedem Linkklick, `beiAfterHide` setzt den Fokus auf die h1. Ich habe in der Scratch-Kopie gelaufen: `mobil.spec.ts` „Link der aktuellen Seite“ (1 grün) und alle 22 „Tabellenrahmen bei 360 px“-Tests inkl. axe (22 grün). Die Screenreader-Ansage selbst bleibt menschlicher Check. |
| 4 | Ledger 01, 05, 06 stehen auf `open: 0`, jede Zeile nennt Commit oder Begründung | ✓ VERIFIED | `01-REVIEW-DISPOSITION.md` (10 Zeilen), `05-…` (18), `06-…` (15): `open: 0`, Frontmatter und Tabelle stimmen zeilenweise überein, nur `fixed` bzw. ein `skipped` (06/WR-01 mit UAT-06-Begründung). Alle zitierten Commit-Hashes existieren als Commits. Die 28 Befunde: 5 + 13 + 10 sind abgedeckt. Stichproben im Code: `beispieldaten.json` gelöscht, `triangle-exclamation` im `ChartCard`, negative `anzahlen` abgelehnt (`konfiguration.py:180`), Warn-Icon-Datei vorhanden. |
| 5 | Querschnittsbedingung: `alle.py --jahr 2026` byte-identisch, CI-Kette grün | ✓ VERIFIED | Eigener Lauf auf HEAD (2b50f3b): ruff check, ruff format --check, `alle.py --jahr 2026` und Reproduzierbarkeitsprüfung (`daten`, `app/src/data`, `app/public/quellen`) grün. Die App-Kette lief wegen vollem Datenträger (`npm ci` scheiterte mit ENOSPC) nicht neu; ich habe stattdessen in der Scratch-Kopie von Welle 4 (Code identisch zu HEAD, `git diff 3cc837e HEAD -- app pipeline daten scripts .github` leer) vitest (2153), die genannten pytest-Dateien (146) und gezielte Playwright-Tests laufen lassen. type-check, lint, build und die volle Playwright-Suite stützen sich auf die Messung des Orchestrators (ci 87, mobil 39). Der Diff gegenüber dem Phasenstart in `daten/` und `app/src/data/` besteht nur aus den begründeten Änderungen `texte.json`, `erklaerungen.md` und der gelöschten `beispieldaten.json`. |

**Score:** 5/5 truths verified (0 behavior-unverified; 1 menschlicher Check offen, siehe unten)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/src/charts/format.ts` | einzige `rd.`/`rund`-Regel | ✓ VERIFIED | `betragMitHinweis`, `kurzMitHinweis`, `rundMitHinweis`, `rundKurz`, U+00A0 |
| `app/src/lib/berechnung.ts` | `minderaufwandBetrag` | ✓ VERIFIED | genutzt in `geldfluss.ts` und `aufwandsarten.ts` |
| `app/src/lib/geldfluss.ts` | `lesehilfeSatz` mit vier Fällen | ✓ VERIFIED | Fälle A bis D, getestet |
| `app/src/lib/einwohner.ts` | `einwohnerZahl` wirft laut | ✓ VERIFIED | genutzt in `kennzahlen.ts`, `produkt.ts`, `EbenenTabelle.vue` |
| `app/src/lib/zuschuesse.ts` | `zusammen()` mit `berechnet` | ✓ VERIFIED | genutzt in `ZuschussListe.vue` |
| `app/src/components/DatenTabelle.vue`, `datenTabelle.ts` | Rolle und ein Name | ✓ VERIFIED | `rahmenAttribute`, Pflicht-`beschriftung` |
| `app/src/App.vue` | Drawer schließt bei jedem Link | ✓ VERIFIED | `beiDrawerLinkKlick` an beiden `RouterLink`-Typen |
| `pipeline/ostbevern/texte.py` | Jahreszahlen-Regel in `pruefe_text` | ✓ VERIFIED | `_JAHRESZAHL_MUSTER`, pytest-Fälle |
| `app/src/lib/__tests__/rdregel.test.ts` | Wächter gegen neue Kopien | ✓ VERIFIED | Fail-first-Fälle plus Lauf über alle App-Dateien |
| `app/e2e/tabellenrahmen.ts`, `mobil.spec.ts` | Browser-Prüfung A11Y-01/02/03 | ✓ VERIFIED | selbst gelaufen, grün |
| Ledger 01/05/06 | `open: 0` | ✓ VERIFIED | siehe Truth 4 |

### Key Link Verification

| From | To | Via | Status |
| ---- | -- | --- | ------ |
| `EuroBetrag.vue` | `charts/format.ts` | `betragMitHinweis`, `kurzMitHinweis` | WIRED |
| `geldfluss.ts`, `drilldown.ts`, `zeitreihen.ts`, `AufwandTreemap.vue`, `NichtBeeinflussbarBlock.vue`, `EbenenTabelle.vue`, `ZuschussListe.vue` | `charts/format.ts` | Import der Hilfsfunktionen | WIRED |
| `AusgabenPage.vue` | `aufwandsarten.minderaufwandHinweis` → `minderaufwandBetrag` | Aufruf (`:214`) | WIRED |
| `DatenTabelle.vue` | `datenTabelle.rahmenAttribute` | `v-bind` am Rahmen | WIRED |
| `App.vue` Drawer-Links | `beiDrawerLinkKlick` | `@click` (`:191`, `:197`) | WIRED |
| `ZuschussListe.vue` | `zusammen().berechnet` | `EuroBetrag :berechnet` | WIRED |
| `StellenplanPage.vue` | `stellenSummen().seiten*` | `kachelZeile` | WIRED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Alle vitest-Tests | `npx vitest run` (Scratch, Code = HEAD) | 49 Dateien, 2153 Tests | ✓ PASS |
| Texte-Regeln | `uv run --offline pytest tests/test_texte.py tests/test_app_daten.py` | 146 passed | ✓ PASS |
| Pipeline reproduzierbar | `alle.py --jahr 2026` auf HEAD plus `git diff --exit-code` | keine Änderung | ✓ PASS |
| Drawer-Link der aktuellen Seite | Playwright `mobil`, „Link der aktuellen Seite“ | 1 passed | ✓ PASS |
| Tabellenrahmen und axe bei 360 px | Playwright `mobil`, „Tabellenrahmen“ | 22 passed | ✓ PASS |

### Requirements Coverage

Alle 13 IDs aus den PLAN-Frontmatter stehen in REQUIREMENTS.md und im ROADMAP-Eintrag der Phase. Es gibt keine verwaisten IDs.

| Requirement | Source Plan | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| TXT-01 | 08-02 | ✓ SATISFIED | `lesehilfeSatz` vier Fälle |
| TXT-02 | 08-02 | ✓ SATISFIED | `minderaufwandBetrag`, nie negativ |
| TXT-03 | 08-01 | ✓ SATISFIED | `pruefe_text`, `pruefe_titel`, Platzhalter-Texte |
| TXT-04 | 08-02, 08-04, 08-05, 08-07 | ✓ SATISFIED | Regel nur in `format.ts`, Wächter |
| TXT-05 | 08-03, 08-05 | ✓ SATISFIED | Etikett und Seiten je Kachel (Umfang: Kontextseiten) |
| TXT-06 | 08-03 | ✓ SATISFIED | `einwohnerZahl()` wirft laut (Entscheidung D-09) |
| A11Y-01 | 08-06 | ✓ SATISFIED | Rolle und Name bei Überlauf, Pflicht-`beschriftung` |
| A11Y-02 | 08-06 | ✓ SATISFIED | Drawer schließt bei jedem Link, e2e grün |
| A11Y-03 | 08-06 | ? NEEDS HUMAN | Ein Name im DOM belegt, Screenreader-Ansage offen |
| TRI-01 | 08-12 | ✓ SATISFIED | Ledger 01 `open: 0` |
| TRI-02 | 08-12 | ✓ SATISFIED | Ledger 05 `open: 0` |
| TRI-03 | 08-12 | ✓ SATISFIED | Ledger 06 `open: 0`, 06/WR-01 mit UAT-Begründung |
| TRI-04 | 08-06 bis 08-12 | ✓ SATISFIED | Hygiene-Befunde behoben, Commits im Ledger |

Hinweis zur Nachführung: In `REQUIREMENTS.md` stehen alle 13 Einträge noch als `[ ]` und „Pending“, und `ROADMAP.md` führt Phase 8 als „In Progress“. Das ist Sache des Orchestrators beim Abschluss der Phase, kein Codebefund.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (geänderte Dateien) | - | `TBD`, `FIXME`, `XXX` | none | keine Treffer |
| `app/src/App.vue` | 69 | Link-Klick setzt Flag auch ohne Navigation (Strg-Klick), Flag wird nur in `beiAfterHide` zurückgesetzt | ⚠️ Warning | Randfall: Fokus springt nach Strg-Klick im Menü zur h1; kein Fehler im Zielverhalten (08-REVIEW WR-02) |
| `app/src/components/DatenTabelle.vue` | 20 | Leere `beschriftung` würde eine namenlose Region erzeugen, kein Guard | ⚠️ Warning | Heute nicht erreichbar (alle 29 Aufrufe haben Text, e2e prüft jede Route); latent (08-REVIEW WR-03) |
| `daten/manuell/texte/erklaerungen.md` | 7, 13, 19, 49, 55 | Relative Jahres-Platzhalter neben Werten mit festem Jahr im Schlüssel | ⚠️ Warning | Für Jahrgang 2026 korrekt; bei einem neuen Jahrgang würden Label und Wert auseinanderlaufen (08-REVIEW WR-01) |

Die Review-Befunde WR-01 bis WR-03 und IN-01 bis IN-07 stehen in `08-REVIEW-DISPOSITION.md` als `open` und sind als Hinweis erfasst, nicht als Blocker. Die drei Warnungen verletzen keinen der fünf Success Criteria für den heutigen Datenstand.

### Human Verification Required

#### 1. Screenreader-Ansage des Tabellennamens (A11Y-03)

**Test:** In VoiceOver oder NVDA bei 360 px Breite `/ausgaben` öffnen und mit dem Screenreader in eine Datentabelle navigieren, deren Rahmen horizontal scrollt.
**Expected:** Der Tabellenname wird nicht störend doppelt vorgelesen (Region plus Caption). Wird er doppelt vorgelesen, soll nur eines der beiden Elemente den Namen tragen (Fallback der UI-SPEC).
**Why human:** Playwright belegt genau einen Namen im ARIA-Baum. Das Vorleseverhalten realer Screenreader ist RESEARCH-Annahme A1 und nicht automatisiert prüfbar.

### Offene Punkte, keine Gaps

- **Steuergruppen auf Leitfragen-Seiten** („Grundsteuer (A+B)“ auf `/geldfluss`, `/einnahmen`) sind von der App gebildete Summen ohne „berechnet“-Etikett. TXT-05 und SC 2 beschränken sich auf die Kontextseiten, ein Test sichert den Zustand bewusst (`geldfluss.test.ts:169-178`). Entscheidung des Nutzers, ob die Regel dort auch gelten soll.
- **Feste Jahre in Text-Schlüsseln** (siehe Anti-Patterns und `coincidental_reliance_items`): vor dem Bau des nächsten Jahrgangs lösen.
- **Vier ältere Befunde aus Ledger 05**, die außerhalb der 28 liegen und laut 08-12 SUMMARY noch im Code stehen. Sie gehören nicht zum Umfang dieser Phase.

### Gaps Summary

Keine Lücken. Alle fünf Success Criteria sind am Code belegt, auch durch eigene Läufe von vitest (2153), pytest (146), der Pipeline-Reproduzierbarkeit auf HEAD und gezielter Playwright-Tests (23). Der Status ist `human_needed`, weil die Screenreader-Ansage für A11Y-03 nur ein Mensch mit einem echten Screenreader prüfen kann.

Einschränkung dieser Verifikation: Der Datenträger der Sandbox war voll (ENOSPC). Deshalb habe ich die komplette App-Kette (type-check, lint, build, volle Playwright-Suite) nicht neu laufen lassen. Dafür gelten die Messungen des Orchestrators auf Code, der zu HEAD identisch ist.

---

_Verified: 2026-10-07T22:10:00Z_
_Verifier: Claude (gsd-verifier)_
