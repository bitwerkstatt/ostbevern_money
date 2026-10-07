---
phase: 07-feinschliff-und-ver-ffentlichung
verified: 2026-10-07T10:10:00Z
status: human_needed
score: 5/5 must-haves verified
covered_files:
  - ".github/workflows/ci.yml"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-01-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-01-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-02-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-02-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-03-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-03-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-04-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-04-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-05-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-05-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-06-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-06-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-07-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-07-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-08-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-08-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-09-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-09-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-10-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-10-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-11-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-11-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-12-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-12-SUMMARY.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-13-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-13-SUMMARY.md"
  - "app/e2e/kacheln.spec.ts"
  - "app/src/components/KennzahlKachel.vue"
  - "app/src/components/NichtBeeinflussbarBlock.vue"
  - "app/src/components/QuelleKnopf.vue"
  - "app/src/lib/__tests__/quelle.test.ts"
  - "app/src/pages/InvestitionenPage.vue"
  - "app/src/pages/StartPage.vue"
  - "app/src/pages/StellenplanPage.vue"
  - "app/src/styles/basis.css"
covered_digest: "v3:sha256:23b6bc176a27e7a0e9cbc635054684bf7c70c05b9dddd1e4ebcd7a7cd0c62366"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "Alle Seiten sind ab 360 px Breite nutzbar (ROADMAP SC 2; A11Y-03): Kachel-Überlauf durch Plan 07-13 geschlossen"
  gaps_remaining: []
  regressions: []
gaps: []
deferred: []
advisory: []
behavior_unverified_items: []
human_verification:
  - test: "Startseite (und /investitionen, /rat-entscheidet, /stellenplan) auf dem eigenen Gerät und im eigenen Browser bei 360, 400, 600, 768 und 1280 px ansehen"
    expected: "Jeder Betrag und jeder Knopf „Quelle“ liegt innerhalb der grauen Kachel; kein waagerechtes Scrollen der Seite"
    why_human: "Die Schriftmetriken auf dem Gerät des Nutzers weichen vom Docker-Image (System-Sans-Fallback) ab; der Nutzer hat den Mangel selbst bemerkt. Der Plan 07-13 hat dafür 16 px Reserve vorgesehen, die Geräteprüfung bleibt offen."
  - test: "Die Korrektur veröffentlichen: lokale Commits (20 vor origin/main, darunter 07-13) nach main pushen, auf den grünen CI-Lauf mit Deploy warten, dann https://bitwerkstatt.github.io/ostbevern_money/ im Browser öffnen: keine 404 im Netzwerk-Tab (Icons, ein Belegbild unter /ostbevern_money/quellen/), direkter Reload von /#/ausgaben und /#/ueber, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei"
    expected: "Die öffentliche Seite zeigt den Stand mit dem Kachel-Fix; alle genannten Punkte funktionieren auf der echten URL"
    why_human: "Das veröffentlichte Deployment (SHA b46259f) enthält den Kachel-Fix noch nicht: origin/main steht auf b46259f, HEAD auf 3ca5fa9. Die Sandbox-Firewall blockiert github.io und Push ist Sache des Nutzers; der Ladevorgang der echten URL ist von hier nicht prüfbar."
---

# Phase 7: Feinschliff und Veröffentlichung Verification Report

**Phase Goal:** Die App ist belegbar, barrierefrei, mobil nutzbar und unter einer öffentlichen URL erreichbar.
**Verified:** 2026-10-07T10:10:00Z
**Status:** human_needed
**Re-verification:** Ja, nach Lückenschluss (Plan 07-13)

## Zusammenfassung

Die einzige Lücke der Erstverifikation (Kachel-Überlauf ab 400 px, Seitenscroll bei 768 px) ist im Quellstand geschlossen. Ich habe das unabhängig im Browser gemessen, mit einer eigenen Messung, die auch Breiten außerhalb der Testliste von 07-13 prüft, und mit einer Negativkontrolle, die den Fehler wieder findet. Alle fünf ROADMAP-Kriterien sind im Code belegt. Offen bleiben nur menschliche Prüfungen: Gerätecheck der Kacheln, und die Veröffentlichung des Fixes (die öffentliche URL zeigt noch den Stand vor 07-13).

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | „Quelle anzeigen“ öffnet Seitenleiste mit WebP-Seite und markiertem Zeilenrechteck | ✓ VERIFIED (Regression geprüft) | 231 WebP unter `app/public/quellen/` unverändert; `quelle.test.ts` und `quelle.spec.ts` grün; accessible name unverändert „Quelle anzeigen: {Bezeichnung}, PDF-Seite {n}“ (`QuelleKnopf.vue`, `aria-label`), sichtbarer Text jetzt „Quelle“ (WCAG 2.5.3 gewahrt, da der Name mit dem sichtbaren Text beginnt). Beleg-Details aus der Erstverifikation unverändert (keine Änderung an `pipeline/`, `daten/`, `app/src/data/`: `git diff a02a28c c906d0c` leer). |
| 2 | Tabellenalternative je Diagramm, Fokus beim Routenwechsel, Kontraste, `prefers-reduced-motion`, alle Seiten ab 360 px nutzbar | ✓ VERIFIED | Früher bereits verifiziert (inventar/interaktion/smoke-axe) und im Lauf erneut grün. **Lücke geschlossen:** Eigene Messung in Chromium (Docker v1.63.0-noble, Build des aktuellen Quellstands, `diff -rq` src/e2e/public/package-lock gegen das Repo leer): 10 Routen × 20 Breiten (360, 375, 390, 400, 412, 420, 480, 520, 560, 600, 640, 700, 768, 820, 900, 1024, 1100, 1280, 1440, 1920): 0 Verstöße (kein Kindelement aus der `.om-kennzahl` heraus, `tile.scrollWidth <= clientWidth`, `documentElement.scrollWidth <= innerWidth`). Negativkontrolle (Betragsschrift per Injektion auf 3rem): Messung meldet 7 Verstöße, u. a. `/ @768 sw=837 > iw=768`; die Messung ist also empfindlich. `kacheln.spec.ts` (Projekt `ci`) plus Klassifikationstest: 5 Tests bestanden. Projekt `mobil` und `texte`: 15 bestanden (360 × 640, auch mit Quell-Leiste und Menü). |
| 3 | Lighthouse-Barrierefreiheit ≥ 95 auf allen Routen | ✓ VERIFIED (nicht erneut gemessen) | `scripts/lighthouse-a11y.sh` vorhanden, 100 auf 11 Routen laut 07-12 (Erstverifikation). Seit dem Lauf änderten sich Knopftext („Quelle“) und Kachelraster; axe (WCAG-2-A/AA) in `smoke.spec.ts` ist im Lauf unverändert grün (96 bestanden laut Orchestrator-Protokoll). Lighthouse selbst wurde nicht neu gestartet (Einmalskript, nicht in CI). |
| 4 | Playwright-Smoke-Test: jede Route ohne Konsolenfehler, Diagramme mit Daten; Textdurchgang Deutsch/Du-Anrede | ✓ VERIFIED | `smoke.spec.ts` 11 Routen × 3 Tests grün (Protokoll `e2e.log`, 96 bestanden). `npx vitest run` in meiner Scratch-Kopie: 45 Dateien, 1.968 Tests bestanden (inkl. `duanrede.test.ts`). |
| 5 | GitHub Actions baut und deployt auf GitHub Pages; App unter öffentlicher URL erreichbar | ✓ VERIFIED (mit Hinweis) | Wie in der Erstverifikation: CI-Lauf 37576891540 grün (`app`, `pipeline`, `deploy`), Pages `build_type: workflow`, Deployment `success`, Repo public. `ci.yml` seit der Erstverifikation unverändert (`git diff a02a28c HEAD -- .github scripts` leer). **Hinweis:** Das veröffentlichte Deployment ist b46259f; der Fix aus 07-13 ist lokal (20 Commits vor `origin/main`) und noch nicht deployt. Das ist kein Mangel des Quellstands, aber die öffentliche Seite zeigt den Kachelfehler, bis gepusht wird (Human-Item 2). |

**Score:** 5/5 Truths verified (0 present, behavior-unverified)

### Plan-07-13-Truths und Prohibitions (gegen den Code geprüft)

| Plan-Truth / Prohibition | Status | Evidenz |
| ------------------------ | ------ | ------- |
| Alle vier Kachellisten nutzen `om-kachelraster`, kein `.vue` hat ein eigenes Kachelraster | ✓ VERIFIED | `grep`: `class="om-kachelraster"` in `StartPage`, `InvestitionenPage`, `StellenplanPage`, `NichtBeeinflussbarBlock`; Regel in `basis.css` (`repeat(auto-fit, minmax(min(100%, 13rem), 1fr))`, `li { min-width: 0 }`, Gap l ab 700 px) |
| Betrag bricht nie um, wird nie abgeschnitten (`.om-zahl` nowrap bleibt) | ✓ VERIFIED (test) | `basis.css` Z. 14 `white-space: nowrap`; in `KennzahlKachel.vue` kein `clamp`, `@media`, `text-overflow`, `overflow: hidden`, `word-break`; `kacheln.spec.ts` prüft `getClientRects().length === 1` und `overflow-x: visible` |
| Betragsgröße = `--wa-font-size-l` bei jeder Breite | ✓ VERIFIED (test) | `KennzahlKachel.vue` `.om-kennzahl__wert { font-size: var(--wa-font-size-l) }`, keine Medienregel; Spec prüft computed font-size |
| Knopf „Quelle“ ≥ 44 × 44 px, Name unverändert | ✓ VERIFIED | `QuelleKnopf.vue` `min-width/min-height: 44px`, `aria-label` unverändert; vitest und Spec grün |
| `kacheln.spec.ts` läuft im Projekt `ci`, mit Klassifikationstest | ✓ VERIFIED | Läuft im `ci`-Lauf (4 Routen-Tests + Klassifikationstest); `playwright.config.ts` unverändert |
| Scope-Zaun: nichts in `pipeline/`, `daten/`, `app/src/data/`, `format.ts`, `SPEZIFIKATION.md`, `07-REVIEW-DISPOSITION.md`, `REQUIREMENTS.md` geändert | ✓ VERIFIED | `git diff --stat a02a28c c906d0c` über diese Pfade leer; `git diff a02a28c HEAD --stat` zeigt nur `app/` und `.planning/`-Dateien der Phase, ROADMAP, STATE |
| Prohibition „Gerätecheck nicht als verifiziert markieren“ | ✓ eingehalten | Bleibt als Human-Item offen (siehe oben); 07-13-SUMMARY D6 `human_judgment: true` |
| Prohibition „Test nicht durch Ausschluss von Route/Breite oder Toleranzerhöhung bestehen lassen“ (judgment) | ✓ eingehalten (nicht-autoritatives Urteil) | Nicht-autoritatives Urteil: eingehalten. Toleranz 0,5 px, 10 Breiten, vier Routen, Klassifikationstest hält die Routenliste geschlossen; meine unabhängige Messung deckt zusätzlich 20 Breiten × 10 Routen ab. `unverified-prohibition: Menschliche Prüfung empfohlen` |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/e2e/kacheln.spec.ts` | Breitentest, `KACHEL_ROUTEN` | ✓ VERIFIED | 371 Zeilen, läuft, besteht |
| `app/src/styles/basis.css` | `.om-kachelraster` | ✓ VERIFIED | Gemeinsame Regel, in vier Seiten verdrahtet |
| `app/src/components/KennzahlKachel.vue` | Größe l überall | ✓ VERIFIED | Substanziell und verwendet |
| `app/src/components/QuelleKnopf.vue` | Label „Quelle“ | ✓ VERIFIED | Text „Quelle“, `aria-label` unverändert |
| `app/src/lib/__tests__/quelle.test.ts` | vitest Label | ✓ VERIFIED | Teil der 1.968 grünen Tests |
| `07-UI-SPEC.md` | Nachtrag 2026-10-07 | ✓ VERIFIED | Von 07-13 geändert (28 Zeilen), Inhalt Vertragstext (human_judgment) |

Artefakte der Erstverifikation (Belege, Bilder, Specs, CI-Workflow, Lighthouse-Skript): Stichprobe auf Existenz und Zahl (231 WebP), unverändert.

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| vier Kachelseiten | `basis.css` | Klasse `om-kachelraster` | ✓ WIRED | im Browser trägt jede `.om-kennzahl` den Vorfahren (Spec prüft) |
| `test:e2e` (Projekt `ci`) | `kacheln.spec.ts` | Projekt ignoriert nur `mobil` und `textliste` | ✓ WIRED | Spec im `ci`-Lauf gelistet |
| `kacheln.spec.ts` | `routen.ts` | `routen()` | ✓ WIRED | Klassifikationstest bestanden |

### Data-Flow Trace (Level 4)

Unverändert: Kachelwerte kommen aus `baueKennzahlen` über `haushalt.json`; die Änderung betrifft nur Layout und Beschriftung, keine Daten (`format.ts` und `app/src/data/` unverändert). ✓ FLOWING.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Kachel- und Seitenüberlauf, 10 Routen × 20 Breiten | eigene Playwright-Messung im Docker-Image gegen `vite build` des aktuellen Quellstands | 0 Verstöße | ✓ PASS |
| Negativkontrolle der Messung (3rem-Betrag injiziert) | gleiche Messung, 3 Breiten | 7 Verstöße gefunden | ✓ PASS (Messung empfindlich) |
| `kacheln.spec.ts` | `playwright test --project=ci e2e/kacheln.spec.ts` | 5 bestanden | ✓ PASS |
| `mobil` und `texte` | `playwright test --project=mobil --project=texte` | 15 bestanden | ✓ PASS |
| App-Unit-Tests | `npx vitest run` | 1.968 bestanden | ✓ PASS |
| Typprüfung, Lint, Format | `npm run type-check`, `npm run lint`, `npm run format:check` (Scratch-Kopie) | ohne Befund | ✓ PASS |
| Pipeline-Tests | nicht erneut gelaufen: nichts unter `pipeline/` geändert; Orchestrator-Protokoll `pytest.log`: 631 bestanden | | ✓ PASS (laut Protokoll) |

### Probe Execution

Step 7c: übersprungen, die Phase deklariert keine `probe-*.sh`.

### Requirements Coverage

Alle zehn Phasen-IDs stehen in PLAN-Frontmattern (A11Y-03 und UI-02 zusätzlich in 07-13); keine verwaisten IDs.

| Requirement | Source Plan | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| DATA-04 | 07-01, 02, 03, 06 | ✓ SATISFIED | Truth 1 |
| UI-02 | 07-01, 06 bis 09, 13 | ✓ SATISFIED | Truth 1; Knopf „Quelle“ |
| UI-06 | 07-05, 07-10 | ✓ SATISFIED | `duanrede.test.ts` grün, Texte freigegeben |
| A11Y-01 | 07-09 | ✓ SATISFIED | `inventar.spec.ts` |
| A11Y-02 | 07-01, 07-09 | ✓ SATISFIED | `interaktion.spec.ts`, axe |
| A11Y-03 | 07-09, 07-13 | ✓ SATISFIED | Lücke geschlossen; Gerätecheck steht als Human-Item aus |
| A11Y-04 | 07-04 | ✓ SATISFIED | Lighthouse 100 auf 11 Routen (07-12) |
| QUAL-02 | 07-04, 07-11 | ✓ SATISFIED | `smoke.spec.ts` |
| DEPL-01 | 07-11, 07-12 | ✓ SATISFIED | CI-Lauf, Deployment success |
| DEPL-02 | 07-05, 07-12 | ✓ SATISFIED (Human-Item 2) | Pages-API, Deployment success; Fix noch nicht veröffentlicht |

REQUIREMENTS.md-Pflege (außerhalb dieser Verifikation, vom Executor absichtlich nicht angefasst): Alle zehn Zeilen stehen in der Checkbox-Liste und in der Tabelle noch auf `Pending` bzw. `Gaps Found`. Nach dieser Verifikation sind sie, vorbehaltlich der Human-Items, auf `Complete` zu setzen (A11Y-03 erst nach dem Gerätecheck).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `scripts/lighthouse-a11y.sh` | 35-52 | `rm -rf "$S"` auf nutzereigenes `LH_SCRATCH` | ⚠️ Warning | Review CR-02, absichtlich offen (Scope-Zaun, Nacharbeit nach Phase 7); Einmalwerkzeug |
| `app/src/lib/kennzahlen.ts` | 117-138 | `berechnet: false` bei gesetzter `herleitung` | ⚠️ Warning | Review WR-05, offen; berührt die Wahrhaftigkeit der Kachel „Erträge“/„Aufwendungen“ |
| `pipeline/ostbevern/belegbilder.py`, `quellen.py` | s. Review | WR-01 bis WR-03 | ⚠️ Warning | Offen laut `07-REVIEW-DISPOSITION.md`; keine Zielblocker |
| `.github/workflows/ci.yml` | 11-13 | Kommentar „noch kein GitHub-Remote“ | ℹ️ Info | veraltet |

Kein `TBD`/`FIXME`/`XXX` in den von 07-13 geänderten Dateien. Der Code-Review-Schritt wurde für den Lückenlauf per Nutzerentscheidung übersprungen; die offenen Befunde stammen aus dem früheren Review und sind unverändert dokumentiert.

### Human Verification Required

1. **Gerätecheck der Kacheln**: Startseite, `/investitionen`, `/rat-entscheidet`, `/stellenplan` auf dem eigenen Gerät und Browser bei 360, 400, 600, 768 und 1280 px. Erwartung: Beträge und Knopf „Quelle“ innerhalb der grauen Kachel, kein waagerechtes Scrollen. Warum Mensch: Geräteschrift weicht vom Docker-Image ab.
2. **Fix veröffentlichen und echte URL prüfen**: 20 lokale Commits pushen (darunter 07-13), grünen CI-Lauf samt Deploy abwarten, dann die öffentliche URL prüfen (keine 404 bei Icons und Belegbild, Reload von `/#/ausgaben` und `/#/ueber`, Quell-Leiste, Fußzeile, PDF-Link). Warum Mensch: Firewall blockiert github.io, Push ist Sache des Nutzers; die veröffentlichte Version (b46259f) hat den Fix noch nicht.

### Gaps Summary

Keine offenen Lücken. Die Lücke „Kachel-Überlauf ab 400 px / Seitenscroll bei 768 px“ ist durch das gemeinsame Raster `om-kachelraster` (13rem Mindestspur), die feste Betragsgröße l und den kürzeren Knopf „Quelle“ geschlossen, ohne Betrag zu kürzen, umzubrechen oder zu verkleinern. Belegt durch Quellcode, den neuen CI-Test (`kacheln.spec.ts`) und meine unabhängige, breitere Messung mit Negativkontrolle. Der Status ist `human_needed`, weil zwei Punkte nur der Nutzer prüfen kann: der Gerätecheck und die Veröffentlichung des Fixes samt Test der echten URL.

---

_Verified: 2026-10-07T10:10:00Z_
_Verifier: Claude (gsd-verifier)_
