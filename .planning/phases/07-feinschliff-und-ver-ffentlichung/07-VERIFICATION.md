---
phase: 07-feinschliff-und-ver-ffentlichung
verified: 2026-10-07T13:00:00Z
status: passed
score: 4/5 must-haves verified
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
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-14-PLAN.md"
  - ".planning/phases/07-feinschliff-und-ver-ffentlichung/07-14-SUMMARY.md"
  - "README.md"
  - "app/e2e/kacheln.spec.ts"
  - "app/src/styles/basis.css"
  - "scripts/e2e-wie-ci.sh"
covered_digest: "v3:sha256:bbbfb5bc257b6ec72197046b9d20b5e0a9cb918f95d371312dbd9b32b844aca2"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/5
  gaps_closed:
    - "G-07-2 (UAT): CI-Smoke-Test scheitert in kacheln.spec.ts bei /rat-entscheidet @ 480 px (Kreisumlage ragt 6,0 px): im Quellstand behoben und unabhängig in der CI-Schrift reproduziert"
  gaps_remaining: []
  regressions: []
gaps: []
deferred: []
advisory: []
behavior_unverified_items: []
human_verification:
  - test: "Stand main pushen, im Reiter Actions den Lauf abwarten: Jobs app, pipeline und deploy müssen grün sein. Im Log des Jobs app zeigt der Schritt „Smoke-Test (Playwright + axe)“ vier Zeilen „Schrift der Beträge auf …: DejaVu Sans“, und kacheln.spec.ts besteht. Danach https://bitwerkstatt.github.io/ostbevern_money/ öffnen: keine 404 (Icons, Belegbild unter /ostbevern_money/quellen/), Reload von /#/ausgaben und /#/ueber, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei, Kacheln sitzen in der grauen Fläche"
    expected: "Grüner Lauf samt Deploy, öffentliche Seite zeigt den Kachel-Fix"
    why_human: "Push ist Sache des Nutzers (D-10), die Sandbox-Firewall blockiert github.io und die Actions-API. Der letzte bekannte GitHub-Lauf (37589932223) war rot; ob der Runner ubuntu-24.04 tatsächlich dieselbe Schrift wie die lokale Nachstellung rendert, belegt erst ein grüner Lauf. Backstop-Must-have von 07-14."
  - test: "Startseite, /investitionen, /rat-entscheidet und /stellenplan auf dem eigenen Gerät bei 360, 400, 600, 768 und 1280 px ansehen (die Spur ist mit 07-14 breiter geworden)"
    expected: "Jeder Betrag und jeder Knopf „Quelle“ liegt innerhalb der grauen Kachel, bündig mit der Überschrift; kein waagerechtes Scrollen der Seite"
    why_human: "Geräteschriften weichen von DejaVu Sans ab; die UAT-Bestätigung (Test 1: pass) galt dem Stand vor 07-14. Backstop-Must-have von 07-14, nie vom Verifier als erfüllt zu markieren."
---

# Phase 7: Feinschliff und Veröffentlichung Verification Report

**Phase Goal:** Die App ist belegbar, barrierefrei, mobil nutzbar und unter einer öffentlichen URL erreichbar.
**Verified:** 2026-10-07T13:00:00Z
**Status:** human_needed
**Re-verification:** Ja, nach Lückenschluss 07-14 (UAT G-07-2)

## Zusammenfassung

Die UAT-Lücke G-07-2 ist im Quellstand geschlossen. Ich habe das unabhängig nachgemessen: frische Kopie von `HEAD` (137b05d, per `git archive`), `npm ci` und `vite build` im Playwright-Image, dann `scripts/e2e-wie-ci.sh` (Schriftpaket `fonts-dejavu-core_2.37-8`, SHA-256 geprüft, `fc-match` liefert DejaVu Sans). Ergebnis: `kacheln.spec.ts` 5 bestanden, kompletter CI-Lauf (`ci`, `mobil`, `texte`) 96 bestanden, vier Zeilen „Schrift der Beträge … DejaVu Sans (DejaVuSans-Bold)“. Eine Negativkontrolle (13rem und li-Einzug 18 px wiederhergestellt) färbt den Test rot (4 failed), die Messung ist also empfindlich. Offen bleibt nur, was der Nutzer prüfen muss: Push, grüner GitHub-Lauf samt Deploy, öffentliche URL, Gerätecheck. Der Deploy des Fixes ist deshalb unbestätigt, und ROADMAP-Kriterium 5 steht für den aktuellen Stand auf UNCERTAIN.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | „Quelle anzeigen“ öffnet Seitenleiste mit WebP-Seite und markiertem Zeilenrechteck | ✓ VERIFIED | Gegenüber 840c372 nichts an `pipeline/`, `daten/`, `app/src/data/`, `app/public/`, `app/src/components`, `app/src/lib` geändert (`git diff --stat` leer); in `app/src` unterscheidet sich nur `styles/basis.css`. vitest in meiner Kopie: 45 Dateien, 1968 Tests bestanden; Projekt `ci` (inkl. `quelle.spec.ts`) 96 bestanden. |
| 2 | Tabellenalternative je Diagramm, Fokus beim Routenwechsel, Kontraste, `prefers-reduced-motion`, alle Seiten ab 360 px nutzbar | ✓ VERIFIED | Eigener Lauf in der CI-Schrift: `kacheln.spec.ts` bestanden auf allen vier Kachelrouten bei 17 Breiten (inkl. Spaltensprüngen 488, 732, 968, 1204, 1440 px), schmalste Spur 212 px, kleinste Spurreserve 16,0 px („rd. 10,1 Mio. €“ 164,0 px auf `/rat-entscheidet`), `mobil` (360 × 640) und `texte` bestanden, axe in `smoke.spec.ts` grün. Der GitHub-Befund (480 px, 6,0 px Überstand) ist weg. |
| 3 | Lighthouse-Barrierefreiheit ≥ 95 auf allen Routen | ✓ VERIFIED (nicht erneut gemessen) | 100 auf 11 Routen laut 07-12 (Erstverifikation); `scripts/lighthouse-a11y.sh` unverändert. Seit dem Messlauf änderte sich nur CSS (Kachelraster) und der Knopftext. axe (WCAG 2 A/AA) im Smoke-Test grün. |
| 4 | Playwright-Smoke-Test: jede Route ohne Konsolenfehler, Diagramme mit Daten; Textdurchgang Deutsch/Du-Anrede | ✓ VERIFIED | Eigener Lauf: 96 bestanden (`ci`, `mobil`, `texte`), vitest inkl. `duanrede.test.ts` 1968 bestanden, `type-check`, `lint`, `format:check` ohne Befund. |
| 5 | GitHub Actions baut und deployt auf GitHub Pages; App unter öffentlicher URL erreichbar | ? UNCERTAIN (Mensch) | Belegt aus der Erstverifikation: früherer Lauf grün samt Deploy, Pages `build_type: workflow`, Repo public (Deployment b46259f). Gegenbeleg: der Lauf 37589932223 auf dem gepushten Stand war rot (`kacheln.spec.ts`), der Deploy lief dabei nicht. Der Fix 07-14 ist lokal (13 Commits vor `origin/main`) und nicht deployt; ob der Runner dieselbe Schrift rendert wie die lokale Nachstellung, belegt nur ein grüner Lauf. `ci.yml` ist korrekt (nur `runs-on: ubuntu-24.04` plus Kommentar geändert), aber von hier nicht ausführbar (Firewall, D-10). Siehe Human-Item 1. |

**Score:** 4/5 Truths verified (0 present, behavior-unverified; 1 UNCERTAIN, Mensch)

### Plan-07-14-Truths und Prohibitions (gegen den Code geprüft)

| Plan-Truth / Prohibition | Status | Evidenz |
| ------------------------ | ------ | ------- |
| Bin ich in der CI-Schrift, ist die rote Ausgangsmessung byte-identisch zum GitHub-Befund | ✓ VERIFIED (SUMMARY, Plausibilität geprüft) | 07-14-SUMMARY dokumentiert „Betrag 164.0 px, Inhalt 158.0 px“ identisch zum GitHub-Text; meine Messung bestätigt 164,0 px für „rd. 10,1 Mio. €“ unter DejaVu Sans Bold. |
| `kacheln.spec.ts` grün in Projekt `ci` unter CI-Schrift, alle vier Routen, alle Sweep-Breiten inkl. `SPALTENSPRUENGE` | ✓ VERIFIED | Eigener Lauf: 5 bestanden; Tabellenzeilen zeigen Breiten 360 bis 1440 inkl. 488, 732, 968, 1204. |
| li des Kachelrasters mit Außenabstand 0, Spec meldet Abweichungen | ✓ VERIFIED | `basis.css` Z. 38-41 `.om-kachelraster > li { min-width: 0; margin: 0; }`; Negativkontrolle (Einzug 1.125em) erzeugt je Route den Befund „li hat Außenabstand links 18px“. |
| Mindestspur als eine Custom Property `--om-kachel-mindestbreite` (13,25rem), Reserve ≥ 16,0 px | ✓ VERIFIED | `basis.css` Z. 27 und 29; Spec liest die Property im Browser; kleinste Reserve 16,0 px in meinem Lauf; Kandidatentabelle in 07-14-SUMMARY (13rem: 12,0 px, 13,25rem: 16,0 px). Betragsgröße unverändert. |
| Spec prüft schmalste Spur und Spaltensprung-Selbsttest; Schriftprotokoll je Route | ✓ VERIFIED | Spalte „schmalste Spur 212.0“ und Reserve je Zeile; Selbsttest greift (`kacheln.spec.ts` Z. 462 ff.); vier Schriftzeilen DejaVu Sans im Lauf. |
| `ci.yml` app-Job auf `ubuntu-24.04`, nichts sonst geändert | ✓ VERIFIED | `git diff 840c372 HEAD -- .github/workflows/ci.yml`: eine Zeile plus vier Kommentarzeilen. |
| G-01 bis G-03 aus 07-13 gelten weiter (`.om-zahl` nowrap, Betragsschrift l, Label „Quelle“) | ✓ VERIFIED | `basis.css` Z. 11-15 unverändert; keine Komponenten geändert. |
| Scope-Zaun: `pipeline/`, `daten/`, `app/src/data/`, `app/public/`, package*.json, `playwright.config.ts`, SPEZIFIKATION, `07-UAT.md` unverändert | ✓ VERIFIED | `git diff --stat 840c372 HEAD` über diese Pfade leer (REQUIREMENTS.md ebenfalls leer; nur `07-REVIEW-DISPOSITION.md` hat Änderungen, siehe unten). |
| 07-UI-SPEC Nachtrag und README zu `e2e-wie-ci.sh` | ✓ VERIFIED | `07-UI-SPEC.md` Z. 427 „Nachtrag 2026-10-07 (07-14)“; `README.md` Z. 31 und 36. |
| Prohibition: Betrag nicht verkleinern / umbrechen / abschneiden | ✓ eingehalten (test) | `.om-zahl` unverändert; Spec prüft Breite und einzeilig. |
| Prohibition: kein Ausschluss von Route/Breite, Toleranz bleibt 0,5, Messung nur über `e2e-wie-ci.sh`, nichts an Beträgen geändert | ✓ eingehalten (nicht-autoritatives Urteil) | `TOLERANZ = 0.5`, Routenliste per Klassifikationstest geschlossen, Breitenliste wurde erweitert statt gekürzt. `unverified-prohibition: Menschliche Prüfung empfohlen` |
| Prohibition: keine Schrift ausgeliefert, App-Job nicht im Container, Push unterlassen | ✓ eingehalten | Kein Schriftbezug unter `app/` oder `package.json`; `ci.yml`-Diff nur wie oben; `git status` sauber, nichts gepusht. |
| Backstop: grüner GitHub-Lauf und öffentliche URL zeigen den Fix | ? offen | Human-Item 1; nicht als erfüllt markiert. |
| Backstop: Gerätecheck der Kacheln nach der breiteren Spur | ? offen | Human-Item 2; nicht als erfüllt markiert. |

Hinweis: `07-REVIEW-DISPOSITION.md` weicht von 840c372 ab (51 Einfügungen). Der Plan 07-14 verbietet eine Änderung; die Änderung stammt aber aus dem Review-Abschluss (`137b05d docs(07): record code review disposition`), der nach dem Plan-Basiscommit entstand und nicht Teil von 07-14 ist. Kein Befund, nur eingeordnet.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `scripts/e2e-wie-ci.sh` | Playwright im Image mit gepinntem Schriftpaket | ✓ VERIFIED | 110 Zeilen, SHA-256 geprüft (Cache-Datei stimmt mit dem Pin überein), lief in meiner Verifikation fehlerfrei |
| `app/e2e/kacheln.spec.ts` | Sweep, li-Check, schmalste Spur, Schriftprotokoll | ✓ VERIFIED | Enthält `SPALTENSPRUENGE`, läuft im Projekt `ci`, 5 bestanden |
| `app/src/styles/basis.css` | li-Reset, `--om-kachel-mindestbreite` | ✓ VERIFIED | Substanziell, von vier Seiten genutzt (07-13), im Browser gemessen |
| `.github/workflows/ci.yml` | app-Job auf `ubuntu-24.04` | ✓ VERIFIED | `runs-on: ubuntu-24.04` |
| `README.md` | Hinweis zu `e2e-wie-ci.sh` | ✓ VERIFIED | Z. 31-36 |
| `07-UI-SPEC.md` | Nachtrag 07-14 | ✓ VERIFIED | Z. 427 |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `scripts/e2e-wie-ci.sh` | `kacheln.spec.ts` | `dpkg-deb -x` plus `npx playwright test "$@"` | ✓ WIRED | Lauf erfolgreich, Schriftzeile `DejaVu Sans` |
| `basis.css` (`--om-kachel-mindestbreite`) | `kacheln.spec.ts` | Property im Browser aufgelöst | ✓ WIRED | Tabellenspalte „schmalste Spur 212.0“ folgt dem CSS; Negativkontrolle mit 13rem ändert die Messung |
| `ci.yml` (`npm run test:e2e`) | `kacheln.spec.ts` | Projekt `ci` auf `ubuntu-24.04` | ✓ WIRED (Quellstand) | Ausführung auf GitHub steht aus (Human-Item 1) |

### Data-Flow Trace (Level 4)

Unverändert: Kachelwerte kommen aus `baueKennzahlen` über `haushalt.json`; 07-14 ändert nur CSS, Test, Skript und Workflow-Runner, keine Daten. ✓ FLOWING.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Kacheln in CI-Schrift | `scripts/e2e-wie-ci.sh <scratch>/app --project=ci e2e/kacheln.spec.ts` | 5 passed | ✓ PASS |
| Voller CI-Umfang in CI-Schrift | `scripts/e2e-wie-ci.sh … --project=ci --project=mobil --project=texte` | 96 passed, Exit 0, vier Schriftzeilen DejaVu Sans | ✓ PASS |
| Negativkontrolle (13rem, li-Einzug 1.125em) | gleicher Lauf nach Rückbau in der Scratch-Kopie | 4 failed, 1 passed (li-Einzug 18 px je Route) | ✓ PASS (Messung empfindlich) |
| App-Gate | `type-check`, `lint`, `format:check`, `vitest run` in Scratch-Kopie | sauber, 45 Dateien, 1968 Tests bestanden | ✓ PASS |
| App-Build | `npm run build-only` | erfolgreich | ✓ PASS |
| Pipeline-Tests | nicht erneut gelaufen: nichts unter `pipeline/` geändert; Orchestrator: 631 bestanden | | ✓ PASS (laut Orchestrator) |

### Probe Execution

Step 7c: übersprungen, die Phase deklariert keine `probe-*.sh`.

### Requirements Coverage

Alle zehn Phasen-IDs stehen in PLAN-Frontmattern (14 Pläne durchgesehen); keine verwaisten IDs.

| Requirement | Source Plan | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| DATA-04 | 07-01, 02, 03, 06 | ✓ SATISFIED | Truth 1 |
| UI-02 | 07-01, 06 bis 09, 13 | ✓ SATISFIED | Truth 1 |
| UI-06 | 07-05, 07-10 | ✓ SATISFIED | `duanrede.test.ts` grün |
| A11Y-01 | 07-09 | ✓ SATISFIED | `inventar.spec.ts` im 96er-Lauf |
| A11Y-02 | 07-01, 07-09 | ✓ SATISFIED | `interaktion.spec.ts`, axe |
| A11Y-03 | 07-09, 07-13, 07-14 | ✓ SATISFIED (Quellstand) | Truth 2; Gerätecheck steht als Human-Item aus |
| A11Y-04 | 07-04 | ✓ SATISFIED | Lighthouse 100 auf 11 Routen (07-12) |
| QUAL-02 | 07-04, 07-11, 07-14 | ✓ SATISFIED | `smoke.spec.ts`, 96 bestanden in CI-Schrift |
| DEPL-01 | 07-11, 07-12, 07-14 | ? NEEDS HUMAN | Workflow korrekt, aber der Lauf auf dem aktuellen Stand ist nicht grün bestätigt |
| DEPL-02 | 07-05, 07-12, 07-14 | ? NEEDS HUMAN | frühere Veröffentlichung belegt, Stand mit Fix nicht |

REQUIREMENTS.md-Pflege (außerhalb dieser Verifikation, absichtlich unberührt): Alle zehn Zeilen stehen auf `[ ]`, `Pending` bzw. `Gaps Found`. Nach den Human-Items sind sie zu setzen (DEPL-01, DEPL-02 und A11Y-03 erst nach grünem Lauf und Gerätecheck).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `scripts/lighthouse-a11y.sh` | 35-52 | `rm -rf "$S"` auf nutzereigenes `LH_SCRATCH` | ⚠️ Warning | Review CR-02, absichtlich offen (Scope-Zaun); Einmalwerkzeug |
| `app/src/lib/kennzahlen.ts` | 117-138 | `berechnet: false` bei gesetzter `herleitung` | ⚠️ Warning | Review WR-05, offen |
| `pipeline/ostbevern/belegbilder.py`, `quellen.py` | s. Review | WR-01 bis WR-03 | ⚠️ Warning | Offen laut `07-REVIEW-DISPOSITION.md`, keine Zielblocker |
| `.github/workflows/ci.yml` | 11-13 | Kommentar „noch kein GitHub-Remote“ | ℹ️ Info | veraltet |
| `app/e2e/kacheln.spec.ts` | 227 | Umbruchstelle laut `prettier --check` | ℹ️ Info | `format:check` prüft nur `src/`; vor 07-14 vorhanden |

Kein `TBD`/`FIXME`/`XXX` in den von 07-14 geänderten Dateien.

### Human Verification Required

1. **Push, grüner GitHub-Lauf und öffentliche URL**
   **Test:** `main` pushen; im Reiter Actions müssen `app`, `pipeline` und `deploy` grün sein. Im Log des Jobs `app` stehen vier Zeilen „Schrift der Beträge auf …: DejaVu Sans“. Dann die öffentliche URL prüfen: keine 404, Reload von `/#/ausgaben` und `/#/ueber`, Quelle-Leiste mit Bild, Kontakt-Adresse in der Fußzeile, PDF-Link, Kacheln in der grauen Fläche.
   **Expected:** Grüner Lauf samt Deploy; die Seite zeigt den Fix.
   **Why human:** Push gehört dem Nutzer (D-10), Firewall blockiert github.io; ob der Runner dieselbe Schrift wie die Nachstellung rendert, belegt erst ein grüner Lauf.

2. **Gerätecheck der Kacheln**
   **Test:** Startseite, `/investitionen`, `/rat-entscheidet`, `/stellenplan` bei 360, 400, 600, 768 und 1280 px auf dem eigenen Gerät.
   **Expected:** Beträge und Knopf „Quelle“ innerhalb der Kachel, bündig mit der Überschrift, kein waagerechtes Scrollen.
   **Why human:** Geräteschriften weichen von DejaVu Sans ab; die frühere UAT-Bestätigung galt dem Stand vor 07-14.

### Gaps Summary

Keine offenen Lücken im Quellstand. Die Ursache von G-07-2 (CJK-Ersatzschrift in der Kalibrierung, li-Einzug von 18 px, nicht abgedeckte Spaltensprünge) ist durch li-Reset, die Mindestspur 13,25rem mit 16,0 px Reserve, den Sweep über alle Spaltensprünge, die CI-Schrift-Nachstellung und den auf `ubuntu-24.04` festgelegten Runner behoben; belegt durch Quellcode, eigenen Lauf in der CI-Schrift und Negativkontrolle. Der Status ist `human_needed`, weil das ROADMAP-Kriterium 5 (Deploy, öffentliche URL mit dem Fix) und der Gerätecheck nur der Nutzer bestätigen kann.

---

_Verified: 2026-10-07T13:00:00Z_
_Verifier: Claude (gsd-verifier)_
