---
phase: 01-setup
verified: 2026-10-09T06:29:13Z
status: passed
score: 10/10 must-haves verified
covered_files:
  - ".claude/CLAUDE.md"
  - ".github/workflows/ci.yml"
  - ".planning/milestones/v1.0-phases/01-setup/01-01-PLAN.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-01-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-02-PLAN.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-02-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-03-PLAN.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-03-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-04-PLAN.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-04-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-05-PLAN.md"
  - ".planning/milestones/v1.0-phases/01-setup/01-05-SUMMARY.md"
  - "LICENSE"
  - "README.md"
  - "app/.nvmrc"
  - "app/index.html"
  - "app/package.json"
  - "app/src/App.vue"
  - "app/src/charts/__tests__/format.test.ts"
  - "app/src/charts/echartsTheme.ts"
  - "app/src/charts/format.ts"
  - "app/src/components/BaseChart.vue"
  - "app/src/components/ChartCard.vue"
  - "app/src/components/DatenTabelle.vue"
  - "app/src/components/PageIntro.vue"
  - "app/src/components/__tests__/chartcard.test.ts"
  - "app/src/components/__tests__/zustaende.test.ts"
  - "app/src/components/chartKontext.ts"
  - "app/src/components/datenTabelle.ts"
  - "app/src/data/haushalt.json"
  - "app/src/lib/bildschirm.ts"
  - "app/src/lib/webawesome.ts"
  - "app/src/main.ts"
  - "app/src/pages/StartPage.vue"
  - "app/src/router/index.ts"
  - "app/src/styles/basis.css"
  - "app/vite.config.ts"
  - "pipeline/.python-version"
  - "pipeline/alle.py"
  - "pipeline/jahrgaenge/2026.toml"
  - "pipeline/jahrgaenge/2026_sollwerte.toml"
  - "pipeline/ostbevern/__init__.py"
  - "pipeline/ostbevern/konfiguration.py"
  - "pipeline/pyproject.toml"
  - "pipeline/tests/test_alle.py"
  - "pipeline/tests/test_konfiguration.py"
  - "pipeline/tests/test_rauchtest.py"
  - "pipeline/uv.lock"
covered_digest: "v3:sha256:cfeb96fcca5a30ff729e78c7dc549e604859b5c820407ae33af8acf1bb69afd8"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "10/10 must-haves verified"
  trigger: "Der Vorgängerbericht (verified 2026-10-02T09:35:14Z, covered_digest v2) beschreibt den Code vor Phase 4 bis 8. Phase 8 hat Phase-1-Code geändert (u. a. 4c105ff, 35b3d51, c18a032, 96a23de, fe416ab); verification.status meldete den Bericht als stale (09-BASISLAUF.md, Abschnitt Verifikationsstatus)."
  gaps_closed: []
  gaps_remaining: []
  regressions: []
  changes_since_previous:
    - path: "pipeline/ostbevern/konfiguration.py"
      change: "4c105ff und 35b3d51 (Phase 8, IN-04): lade_jahrgang lehnt negative anzahlen.* ab; 93a4720 (Phase 7): leere Layout-Listen nur für eine Allowlist; Ergänzungen der Phasen 2 bis 7. STANDARD_JAHR, JAHRGAENGE_VERZEICHNIS, lade_jahrgang, lade_sollwerte, KonfigurationsFehler bestehen unverändert."
      regression: false
    - path: "pipeline/alle.py"
      change: "c18a032 (Phase 8, IN-02): pdf_relativ wird einmal berechnet; die Schritte 01 bis 08 hängen an. --jahr mit Vorgabe STANDARD_JAHR und die Behandlung von KonfigurationsFehler stehen unverändert."
      regression: false
    - path: ".github/workflows/ci.yml"
      change: "Phase 7: dritter Job deploy (92fc4cc), Smoke- und Browser-Schritte, Push-Trigger nur auf main (2cb379e). Die Jobs pipeline und app bestehen weiter ohne needs und ohne Pfadfilter. Siehe deferred."
      regression: false
    - path: "app/src/components/DatenTabelle.vue"
      change: "Phase 5, 7 und 8 (u. a. e1e1901, fe416ab, 98803c4): Slot-Modus entfernt, beschriftung, spalten und zeilen sind Pflicht (D-16, D-19), Tabellenrahmen mit Rolle und genau einem Namen. Leer-, Lade- und Teilzustände durch zustaende.test.ts belegt."
      regression: false
    - path: "app/src/data/jahrgang.json, app/src/data/beispieldaten.json"
      change: "370497f (Phase 5) und 96a23de (Phase 8, IN-03) haben beide Demo-Dateien gelöscht. Das Haushaltsjahr der Startseite kommt aus app/src/data/haushalt.json, einer Pipeline-Ausgabe."
      regression: false
gaps: []
deferred:
  - truth: "Plan 01-05: ci.yml hat genau zwei parallele Jobs (pipeline, app)"
    addressed_in: "Phase 7"
    evidence: "Phase 7 (ROADMAP: „Deployment auf GitHub Pages“) ergänzte den Job deploy (92fc4cc, D-09). pipeline und app laufen weiter parallel und unabhängig; deploy braucht beide (needs) und läuft nur auf main."
  - truth: "Plan 01-05 und Roadmap-Ziel: die CI läuft bei jedem Push"
    addressed_in: "Phase 7"
    evidence: "07-REVIEW.md IN-07, behoben in 2cb379e: push nur auf main, Branches mit offenem Pull Request prüft pull_request (kein Doppellauf). Ein Push auf einen Branch ohne Pull Request löst keinen Lauf mehr aus. Kein Text im ROADMAP-Abschnitt von Phase 7 nennt das ausdrücklich; die Entscheidung steht im Review und in der Kopfzeile von ci.yml."
advisory:
  - finding: ".claude/CLAUDE.md nennt unter „CI“ weiter nur die Jobs pipeline und app; ci.yml hat seit Phase 7 den dritten Job deploy"
    category: other
    reason: "Dokumentationsabweichung, kein Codefehler. Der Block wurde zuletzt in 28462a7 (Phase 8) angefasst. Auflösung: den Satz um deploy ergänzen oder ausdrücklich auf die Prüf-Jobs beschränken."
    evidence_status: "direkt beobachtet: .claude/CLAUDE.md Abschnitt Technology Stack, Zeile „CI“, gegen .github/workflows/ci.yml jobs: pipeline, app, deploy"
  - finding: ".claude/CLAUDE.md sagt, die Basiskomponenten behielten die Münster-Namen und -Props; DatenTabelle weicht seit Phase 5 bewusst ab (Pflicht-Props, kein Slot-Modus)"
    category: other
    reason: "Die Abweichung ist im Kopfkommentar von DatenTabelle.vue als D-16 und D-19 begründet. Die Konvention in CLAUDE.md nennt sie nicht. Namen und Pfade aller sieben Basismodule bestehen unverändert."
    evidence_status: "direkt beobachtet: app/src/components/DatenTabelle.vue Zeilen 13 bis 16"
behavior_unverified_items: []
---

# Phase 1: Setup Verification Report

**Phase Goal:** Pipeline und App lassen sich leer bauen und testen. Die Konventionen und die Jahrgangskonfiguration sind festgelegt, und die CI prüft jeden Push.
**Verified:** 2026-10-09T06:29:13Z
**Status:** passed
**Re-verification:** Yes — neue Prüfung gegen den Endstand nach Phase 8 und dem Wellenstand von Phase 9. Der Vorgängerbericht stand auf `passed`, 10/10, und wurde nicht fortgeschrieben, sondern Punkt für Punkt gegen den heutigen Code geprüft.

## Warum diese Re-Verifikation (Phase 9, AUD-02)

Der Bericht vom 2026-10-02 beschreibt Phase 1 vor den Phasen 4 bis 8. Seitdem wurden Dateien geändert, die dieser Bericht abdeckte; `verification.status` meldete ihn deshalb als `stale` (09-BASISLAUF.md, Abschnitt „Verifikationsstatus vor der Re-Verifikation“). Phase 9 verlangt für jede Phase einen Bericht, der den Endstand beschreibt (AUD-02, D-13).

Vorgehen: Das gsd-verifier-Verfahren (Step 0 im Re-Verifikationsmodus, Steps 3 bis 9) wurde im Plan 09-04 selbst ausgeführt, weil Executor-Agenten den Verifier nicht starten können. Geprüft wurden alle zehn Wahrheiten des Vorgängerberichts und die fünf Erfolgskriterien aus `v1.0-ROADMAP.md` (Abschnitt Phase 1). Keine Wahrheit gilt wegen des alten Laufs als erfüllt.

Änderungen an Phase-1-Code seit dem Vorgängerbericht (`git log --oneline --since=2026-10-02T09:35:14Z -- <Implementierungsdateien der früheren covered_files>`): 85 Commits, davon mit Phase-1-Bezug aus Phase 8: `4c105ff` und `35b3d51` (negative `anzahlen.*` werden abgelehnt, IN-04), `c18a032` (`pdf_relativ` einmal berechnet, IN-02), `96a23de` (Warn-Icon, verwaiste `beispieldaten.json` entfernt, IN-03), `fe416ab` (Tabellenrahmen mit Rolle und einem Namen, IN-05), `98803c4` (Phase 8) und `78744d4` (Phase 9, Plan 09-01 oder 09-02; DatenTabelle ohne Beschriftung). Aus den Phasen 5 bis 7 kommen unter anderem `370497f` (`jahrgang.json` entfernt), `1c14077` (Kopfmenü), `2cb379e` (Push nur auf `main`) und `92fc4cc` (Deploy-Job).

Code-Stand: `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline app daten scripts .github` endet mit Exit 0. Seit dem Kopf von 09-BASISLAUF.md hat sich kein Codepfad geändert, die Läufe dort gelten für den heutigen Code (D-23).

## Goal Achievement

### Observable Truths

| # | Truth (Roadmap Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | Die Repo-Struktur nach Spez. 7 existiert (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`), das Quell-PDF liegt unter `raw_data/` | ✓ VERIFIED | `git ls-files` zeigt eingecheckte Dateien in `daten/zwischen` (5), `daten/aufbereitet` (10), `daten/manuell` (15) und `daten/pruefberichte` (4); `raw_data/haushalt-2026.pdf` ist getrackt (9.116.953 Bytes, Kopf `%PDF-1.5`); `discussion/` enthält nur `SPEZIFIKATION.md`, keine PDF-Kopie. Der Rauchtest `test_pdf_existiert_mit_erwarteter_seitenzahl` lief grün (eigener Lauf, siehe unten, und Basislauf). |
| 2 | `uv run pytest` läuft im uv-Projekt `pipeline/` (Python ≥ 3.12, pdfplumber, polars, typer, pytest) grün durch | ✓ VERIFIED | `pipeline/pyproject.toml`: `requires-python = ">=3.12"`, Abhängigkeiten `pdfplumber`, `polars`, `typer` (zusätzlich `pillow`, `pypdfium2` aus späteren Phasen), Dev-Gruppe `pytest`, `ruff`; `pipeline/.python-version` = `3.12`. 09-BASISLAUF.md, Abschnitt Pipeline: `uv sync --locked` Exit 0, `ruff check` „All checks passed!“, `ruff format --check` „51 files already formatted“, `681 passed in 350.31s`, `pytest_skipped: 0`. Eigener Lauf (benannte Auswahl, Linux, Python 3.12.12): `tests/test_rauchtest.py` und `tests/test_konfiguration.py` → `73 passed`, `tests/test_alle.py` → `15 passed`. |
| 3 | `npm run build` baut das Vue-3-Grundgerüst (TS, Vite, Web Awesome, vue-echarts, Hash-Router) mit den Münster-Basiskomponenten (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `echartsTheme.ts` u. a.); `vue-tsc` und ESLint laufen in GitHub Actions fehlerfrei | ✓ VERIFIED | 09-BASISLAUF.md, Tabelle „App (Scratch-Kopie)“: `npm ci`, `type-check` (`vue-tsc --build`), `lint`, `format:check` Exit 0, `npm run test` 2162 Tests grün, `npm run build` „✓ 1069 modules transformed“. Stack aus `app/package.json` (`vue`, `vue-router`, `echarts`, `vue-echarts`, `@awesome.me/webawesome`, `vite`, `vue-tsc`, `eslint`); Hash-Router `createWebHashHistory` in `app/src/router/index.ts:53`. Alle sieben Basismodule bestehen am alten Ort (`PageIntro.vue`, `ChartCard.vue`, `BaseChart.vue`, `DatenTabelle.vue`, `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts`). Auf GitHub: Lauf 37616724781 (`CI`, Kopf `291d86b`, 2026-10-07, ein Vorfahr von HEAD) hat im Job `app` die Schritte „Typprüfung (vue-tsc)“ und „ESLint“ mit `success` abgeschlossen. Nach Phase 8 gab es keinen GitHub-Lauf; die Kette lief dafür im Basislauf auf dem heutigen Code. |
| 4 | Haushaltsjahr, Spaltenköpfe, Seitenbereiche und PDF-Pfad stehen in einer Jahrgangs-Konfigurationsdatei; die Pipeline lädt sie von dort statt aus dem Code | ✓ VERIFIED | `pipeline/jahrgaenge/2026.toml` trägt `haushaltsjahr = 2026` (Z. 5), `pdf_pfad` (Z. 6), `[anzahlen]`, `[spalten]`, `[seitenbereiche]`, `[kopfzeilen]`; `lade_jahrgang` liest über `tomllib.load` (`konfiguration.py:126-131`), `lade_sollwerte` ebenso (`:487-492`). `grep -rlw 2026 pipeline --include="*.py"` ohne Tests liefert `konfiguration.py` (`STANDARD_JAHR = 2026`, Z. 20) und `texte.py` (nur ein Docstring-Satz, Z. 591); kein Jahrgangswert steht in einer Zuweisung außerhalb. Tests `test_konfiguration.py` (inklusive `test_negative_anzahl_wird_abgelehnt`, `test_absoluter_pdf_pfad_wird_abgelehnt`, `test_relativer_pdf_pfad_ausserhalb_projekt_wird_abgelehnt`) grün. |
| 5 | Die Projekt-`CLAUDE.md` nennt die Befehle für Pipeline und App sowie die sechs Konventionen | ✓ VERIFIED | `.claude/CLAUDE.md`, Abschnitt Conventions: „Deutsche Bezeichner ohne Umlaute“, „Beträge als int-Euro“, „Nur 1-basierte PDF-Seiten“, „Keine Jahrgangswerte im Code“, „Du-Anrede“, „Zahlen in Texten aus Daten“ stehen alle; Abschnitt Befehle nennt `uv run --directory pipeline pytest`, `ruff check`, `ruff format`, `python alle.py --jahr 2026`, `npm --prefix app run build`, `type-check`, `lint`, `format:check`, `test` und das lokale Nachstellen der CI. Es gibt keine `CLAUDE.md` im Repo-Root (`git ls-files` ohne Treffer). Seit dem Vorgängerbericht wurde die Datei in `65cd6d8` (Testbefehl) und `28462a7` (CI-Block) ergänzt, beides additiv. |
| 6 | (Plan 01-05, auf den Endstand gebracht) `ci.yml` löst auf Push und Pull Request aus, ohne Pfadfilter. Die Jobs `pipeline` (uv sync --locked, ruff check, ruff format --check, pytest) und `app` (npm ci, vue-tsc, ESLint, Prettier, Build) laufen parallel und unabhängig. Das Token ist auf `contents: read` begrenzt, alle Aktionen sind auf 40-stellige SHAs festgelegt | ✓ VERIFIED | `.github/workflows/ci.yml`: `on:` hat `push` (`branches: [main]`), `pull_request`, `workflow_dispatch`; weder `paths:` noch `paths-ignore:`. `pipeline` und `app` tragen kein `needs:`; die Schrittfolgen stehen wie beschrieben (`uv sync --locked`, `ruff check .`, `ruff format --check .`, `pytest`; `npm ci`, `type-check`, `lint`, `format:check`, `test`, `build`). Workflow-Ebene `permissions: contents: read`; alle sechs `uses:` tragen eine 40-stellige SHA mit Versionskommentar. Der Wortlaut „genau zwei Jobs“ und „jeder Push“ ist seit Phase 7 nicht mehr wörtlich wahr (dritter Job `deploy`, Push nur auf `main`) — siehe `deferred` und den Abschnitt „Deferred Items“. |
| 7 | (Plan 01-05) Jeder `run:`-Befehl der CI-Jobs läuft lokal in demselben Arbeitsverzeichnis mit derselben Kommandozeile grün | ✓ VERIFIED | 09-BASISLAUF.md hat die Kette des heutigen `ci.yml` auf dem Code `1d0df35` ausgeführt: Pipeline (`uv sync --locked`, `ruff check`, `ruff format --check`, volle pytest-Suite mit 681 Tests), Reproduzierbarkeit (`alle.py`, danach `git diff --stat --exit-code -- daten app/src/data` und `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` leer), App (`npm ci`, `type-check`, `lint`, `format:check`, `test`, `build`) und die Playwright-Projekte `ci` (89), `mobil` (41), `texte` (1) über `scripts/e2e-wie-ci.sh`. Nur GitHub-eigene Schritte (`playwright install --with-deps`, Schriftpaket, Pages-Upload, `deploy`) laufen lokal nicht; im GitHub-Lauf 37616724781 waren alle Schritte der Jobs `pipeline` und `app` sowie der Job `deploy` `success`. |
| 8 | (Plan 01-05) `README.md` nennt „Inspiriert von Münster Money (Code for Münster)“ mit Link; `LICENSE` ist MIT | ✓ VERIFIED | `README.md:71`: „Inspiriert von [Münster Money (Code for Münster)](https://github.com/codeformuenster/haushalt-muenster-2026)“. `LICENSE` beginnt mit „MIT License / Copyright (c) 2026 Thomas Manthey“. Der Fußbereich der App trägt denselben Dank mit Link (`app/src/App.vue:252-262`), die Seite „Über“ ebenso (`UeberPage.vue:39-58`). |
| 9 | (Plan 01-03) Die laufende App fragt bei keinem Drittanbieter etwas an | ✓ VERIFIED | Statisch: `app/index.html` lädt nur `/src/main.ts`; Web-Awesome-Komponenten sind einzeln gebündelt importiert (`app/src/main.ts`), Icons kommen von `${BASE_URL}icons` (`app/src/lib/webawesome.ts`, `setIconPath`); die drei Fundstellen von `https://` in `app/src` (`config.ts`, `App.vue`, `UeberPage.vue`) sind `href`-Ziele, keine Laufzeitanfragen; kein `@import url(http` in CSS, kein `v-html`/`innerHTML`. Dynamisch (Basislauf, Playwright `ci`): `e2e/quelle.spec.ts:238:3 › … alle Anfragen gehen an den Preview-Server (keine Drittanbieter)` und `e2e/smoke.spec.ts:138:5 › Smoke / › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten` (sowie dieselbe Spec für alle zehn weiteren Routen). |
| 10 | (Plan 01-04) Die Formatierungsfunktionen in `format.ts` liefern die festgelegte Ausgabe | ✓ VERIFIED | Eigener Lauf in der Scratch-Kopie (`npx vitest run`, Vitest 5.0.3): `euro(2353506)` = „2.353.506 €“, `euroKurz(27502063)` = „27,5 Mio. €“, `euroKurz(-2353506)` = „-2,35 Mio. €“, `zahl(11741)` = „11.741“, `prozent(0.341)` = „34,1 %“ (geschützte Leerzeichen normalisiert). `format.test.ts`, `chartcard.test.ts`, `zustaende.test.ts` und `eurobetrag.test.ts` → 61 Tests grün. `format.ts` wuchs seit dem Vorgängerbericht (u. a. `formatiere`, `rd.`-Regel, `anzahlText`); die fünf Phase-1-Funktionen sind unverändert exportiert. |

**Score:** 10/10 Wahrheiten verifiziert, 0 present-but-behavior-unverified, 0 Lücken.

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | „genau zwei parallele Jobs“ in `ci.yml` (Plan 01-05) | Phase 7 | Dritter Job `deploy` für GitHub Pages (`92fc4cc`, D-09). Phase-7-Ziel im ROADMAP: „Deployment auf GitHub Pages“. `pipeline` und `app` bleiben parallel, `deploy` braucht beide. |
| 2 | „CI läuft bei jedem Push“ (Roadmap-Ziel Phase 1, Plan 01-05) | Phase 7 | `07-REVIEW.md` IN-07, Fix `2cb379e`: `push` nur auf `main`, Pull Requests decken die übrigen Branches ab. Der ROADMAP-Text von Phase 7 nennt das nicht; der Beleg ist Review und `ci.yml`-Kopf. |

Beide Punkte ändern Status und Score nicht: Die Kerninhalte der Wahrheit (zwei unabhängige Prüf-Jobs, Prüfung bei Push auf `main` und bei jedem Pull Request) sind in Zeile 6 geprüft.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | `.claude/CLAUDE.md` nennt unter „CI“ nur `pipeline` und `app`, `ci.yml` hat auch `deploy` | other | Dokumentationsabweichung, kein Gate |
| 2 | CLAUDE.md-Konvention „Basiskomponenten behalten Münster-Namen und -Props“ gegen die begründete Abweichung von `DatenTabelle` (D-16, D-19) | other | Dokumentationsabweichung, im Code begründet |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `pipeline/ostbevern/konfiguration.py` | `STANDARD_JAHR`, `lade_jahrgang`, `lade_sollwerte`, `KonfigurationsFehler`, `Jahrgang` | ✓ VERIFIED | `grep -n "^def \|^class \|^STANDARD_JAHR"` findet alle fünf (Z. 20, 62, 108, 124, 485) |
| `pipeline/jahrgaenge/2026.toml` | alle PDF-spezifischen Werte | ✓ VERIFIED | Tabellen `[anzahlen]`, `[spalten]`, `[seitenbereiche]`, `[kopfzeilen]` vorhanden, dazu die Layout-Abschnitte späterer Phasen |
| `pipeline/jahrgaenge/2026_sollwerte.toml` | Sollwerte Satzung, Gesamtergebnisplan | ✓ VERIFIED | `[satzung]` mit `pdf_seite = 8` (Z. 11-12), `[gesamtergebnisplan]` (Z. 27) |
| `pipeline/tests/test_rauchtest.py` | Rauchtest (D-12) | ✓ VERIFIED | 3 Tests, im eigenen Lauf grün |
| `pipeline/alle.py` | dünner typer-Einstieg mit `--jahr` | ✓ VERIFIED | `jahr` mit Vorgabe `STANDARD_JAHR`, ruft `lade_jahrgang` und `lade_sollwerte`, behandelt `KonfigurationsFehler` mit Exit 1; `test_alle.py` (15 Tests mit Stubs der Schritte) grün |
| `pipeline/uv.lock` | gepinnte Abhängigkeiten | ✓ VERIFIED | getrackt; `uv sync --locked` Exit 0 im Basislauf |
| `app/src/components/PageIntro.vue` | Props `titel`, `beschreibung`, Default-Slot | ✓ VERIFIED | unverändert in Gestalt und Props |
| `app/src/router/index.ts` | Hash-Router, Catch-all auf Start | ✓ VERIFIED | `createWebHashHistory`, Route `start` bei `/`, `/:pathMatch(.*)*` leitet auf `start` (Z. 116) |
| `app/src/lib/webawesome.ts` | Styles, deutsche Übersetzung, selbst gehostete Icons | ✓ VERIFIED | `translations/de.js`, `setIconPath(`${BASE_URL}icons`)` |
| `app/src/main.ts` | einzeln importierte Web-Awesome-Komponenten | ✓ VERIFIED | `./lib/webawesome` ist der erste Import; 16 Komponenten einzeln importiert |
| `app/src/App.vue` | Rahmen mit Kopf, Navigation, RouterView, Fußbereich mit Dank | ✓ VERIFIED | `nav aria-label="Hauptnavigation"`, `RouterView`, Fußbereich mit Münster-Link |
| `app/package.json` | Skripte, `engines.node` | ✓ VERIFIED | `type-check`, `lint`, `format:check`, `test`, `build`, `test:e2e*`; `engines.node` `^22.18.0`; `.nvmrc` = 22 |
| `app/src/charts/format.ts` | einzige Quelle der Zahlenformatierung | ✓ VERIFIED | siehe Wahrheit 10 |
| `app/src/charts/echartsTheme.ts` | Registrierung und Theme aus WA-Tokens | ✓ VERIFIED | `use([...])` mit Renderer, Bar/Line/Sankey/Treemap, Grid/Tooltip/Legend/Aria/MarkLine; `token()` liest `--wa-*`; `KATEGORIE_FARBEN[0]` = `--wa-color-brand-60` (Gold); `POL_FARBEN` aus `success`/`danger`/`neutral` |
| `app/src/components/BaseChart.vue` | Zustände laedt, fehler, leer | ✓ VERIFIED | `zustaende.test.ts` prüft alle drei Zustände |
| `app/src/components/ChartCard.vue` | Kartenrahmen, `CHART_KONTEXT`, Beispieldaten-Hinweis | ✓ VERIFIED | `provide(CHART_KONTEXT, …)`, `beispieldaten` zeigt den warning-Callout; `chartcard.test.ts` grün |
| `app/src/components/DatenTabelle.vue` | semantische Tabelle, Leer-/Ladezustand | ✓ VERIFIED | Pflicht-Props `beschriftung`, `spalten`, `zeilen`; Zustände durch `zustaende.test.ts` belegt |
| `app/src/lib/bildschirm.ts` | reaktives Schmal-Flag | ✓ VERIFIED | `useSchmalerBildschirm`, `SCHMAL_BIS = 699` |
| `app/src/data/jahrgang.json`, `beispieldaten.json` | Phase-1-Demodaten | ✓ REPLACED | gelöscht in `370497f` und `96a23de`; ersetzt durch Pipeline-Ausgabe `app/src/data/haushalt.json` (Wahrheit 3, Datenfluss) |
| `.github/workflows/ci.yml` | Prüf-Jobs, SHA-Pins | ✓ VERIFIED | siehe Wahrheit 6 |
| `.claude/CLAUDE.md`, `README.md`, `LICENSE` | Dokumentation, Dank, MIT | ✓ VERIFIED | siehe Wahrheiten 5 und 8 |
| `app/vite.config.ts` | Pages-taugliche Basis (WR-01) | ✓ VERIFIED | `base: './'` mit Begründung; `isCustomElement` für `wa-*` |
| `app/src/styles/basis.css` | `prefers-reduced-motion` (WR-02) | ✓ VERIFIED | Block ab Z. 71: `wa-skeleton`-Animation aus, WA-Übergangs-Tokens und Drawer-Dauern auf 0 |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `test_rauchtest.py` | `konfiguration.py` | `lade_jahrgang`, `lade_sollwerte`, `STANDARD_JAHR` | ✓ WIRED | 3 Tests grün |
| `konfiguration.py` | `jahrgaenge/2026.toml` | `tomllib.load` auf `verzeichnis / f"{jahr}.toml"` | ✓ WIRED | `konfiguration.py:126-131` |
| `jahrgaenge/2026.toml` | `raw_data/haushalt-2026.pdf` | `pdf_pfad` | ✓ WIRED | Datei vorhanden; `alle.py` bricht bei fehlender PDF ab |
| `alle.py` | `konfiguration.py` | `--jahr` mit Vorgabe `STANDARD_JAHR` | ✓ WIRED | `test_ohne_jahr_nutzt_standardjahr` grün |
| `app/src/main.ts` | `app/src/lib/webawesome.ts` | erster Import | ✓ WIRED | `setIconPath` läuft vor den Komponenten |
| `app/src/router/index.ts` | `StartPage.vue` | Route `start` bei `/` | ✓ WIRED | Z. 55 |
| `StartPage.vue` | Haushaltsjahr | `haushalt.haushaltsjahr` aus `@/data/daten` | ✓ WIRED | ersetzt den Phase-1-Link auf `jahrgang.json`; `haushalt.json` enthält `"haushaltsjahr": 2026` |
| `vite.config.ts` | `wa-*`-Elemente | `isCustomElement` | ✓ WIRED | |
| `BaseChart.vue` | `echartsTheme.ts` | `CHART_THEME` | ✓ WIRED | Import und Übergabe an `VChart` |
| `BaseChart.vue` | `ChartCard.vue` | `inject(CHART_KONTEXT)` | ✓ WIRED | `chartKontext.ts` |
| `DatenTabelle.vue` | `charts/format.ts` | `EURO_OPTIONEN`, `KEIN_WERT` | ✓ WIRED | Import Z. 3 |
| `ci.yml` | `pipeline/uv.lock` | `uv sync --locked` | ✓ WIRED | Basislauf grün |
| `ci.yml` | `app/package.json` | npm-Skripte | ✓ WIRED | alle sechs Skripte vorhanden |
| `ci.yml` | `app/.nvmrc` | `node-version-file: app/.nvmrc` | ✓ WIRED | |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `StartPage.vue` Titel | `haushalt.haushaltsjahr` | `app/src/data/haushalt.json` ← `pipeline/ostbevern/app_daten.py` (Schritt 07) ← `2026.toml` | Ja, von der Pipeline erzeugt und im Basislauf byte-identisch neu geschrieben | ✓ FLOWING |
| `konfiguration.py` `Jahrgang` | TOML-Inhalt | `tomllib.load` auf `2026.toml` | Ja | ✓ FLOWING |
| `alle.py` Ausgabe | `lade_jahrgang(jahr)` | `konfiguration.py` | Ja (Basislauf: „Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.“) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Jahrgangs- und Rauchtest | `uv run --directory pipeline pytest -p no:cacheprovider -q tests/test_rauchtest.py tests/test_konfiguration.py` | `73 passed in 0.20s` | ✓ PASS |
| CLI-Vertrag von `alle.py` (Schritte gestubbt) | `uv run --directory pipeline pytest -p no:cacheprovider -q tests/test_alle.py` | `15 passed in 0.07s` | ✓ PASS |
| Basiskomponenten und `format.ts` | `npx vitest run src/charts/__tests__/format.test.ts src/components/__tests__/chartcard.test.ts src/components/__tests__/zustaende.test.ts src/components/__tests__/eurobetrag.test.ts` (Scratch-Kopie von `app/`, eigenes `npm ci`) | `Test Files 4 passed (4)`, `Tests 61 passed (61)` | ✓ PASS |
| Sollwerte aus Plan 01-04 | eine einmalige Vitest-Datei nur in der Scratch-Kopie (`euro`, `euroKurz`, `zahl`, `prozent`) | `1 passed` | ✓ PASS |
| Code seit Basislauf unverändert | `git diff --quiet 1d0df35… HEAD -- pipeline app daten scripts .github` | Exit 0 | ✓ PASS |
| Vollläufe (pytest, `alle.py`, Vitest, Build, Playwright) | nicht in diesem Plan gelaufen (D-23) | siehe Live-Evidenz | zitiert |

### Probe Execution

Weder PLAN- noch SUMMARY-Dateien dieser Phase deklarieren Probes; unter `scripts/` liegen `e2e-wie-ci.sh` und `lighthouse-a11y.sh`, keine `probe-*.sh`. Schritt 7c: SKIPPED.

### Live-Evidenz

Alle Vollläufe stammen aus `09-BASISLAUF.md` (Kopf `1d0df35da1842daec515b40dd62f8d918e240105`, erstellt 2026-10-09T06:24:00Z). Dieser Plan hat weder `alle.py` noch die volle pytest-Suite noch Playwright gestartet.

| Lauf | Ergebnis laut 09-BASISLAUF.md |
|---|---|
| `uv sync --locked`, `ruff check`, `ruff format --check` | Exit 0, „All checks passed!“, „51 files already formatted“ |
| volle pytest-Suite | `681 passed in 350.31s (0:05:50)`, 0 Skips |
| `alle.py --jahr 2026` | Exit 0, Regeln 1 bis 10 grün, „Veraltete Befunde: 0“, `daten/`, `app/src/data/`, `app/public/quellen` byte-identisch |
| App-Kette (Scratch-Kopie) | `type-check`, `lint`, `format:check` Exit 0; Vitest 2162 Tests in 49 Dateien; Build 1069 Module |
| Playwright `ci` / `mobil` / `texte` | 89 / 41 / 1 bestanden |
| GitHub Actions (Lauf 37616724781, Kopf `291d86b`, vor Phase 8) | Jobs `app`, `pipeline`, `deploy` mit `success` |

Zitierte Playwright-Titel zu dieser Phase: `e2e/smoke.spec.ts:138:5 › Smoke / › rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten`, `e2e/quelle.spec.ts:238:3 › … alle Anfragen gehen an den Preview-Server (keine Drittanbieter)`, `e2e/mobil.spec.ts:151:5 › 360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /`.

### Regressionsprüfung der Plan-Wahrheiten

Geprüft wurden die `must_haves` der Pläne 01-01 bis 01-05, soweit ihre Artefakte seit dem Vorgängerbericht geändert wurden (`git log --since=2026-10-02T09:35:14Z`). Ergebnis: keine Regression. Wo der heutige Code den Wortlaut des Plans verlässt, ist die Absicht der Wahrheit erhalten und die Änderung begründet.

| Plan | Wahrheit (gekürzt) | Heutiger Stand | Urteil |
|---|---|---|---|
| 01-02 | Jahrgangswert nur in `konfiguration.py`; unvollständige oder fehlerhafte Datei → `KonfigurationsFehler`; `pdf_pfad` außerhalb der Projektwurzel abgelehnt | `STANDARD_JAHR` nur in `konfiguration.py:20`; `test_konfiguration.py` grün (73 Tests mit Rauchtest), jetzt zusätzlich `test_negative_anzahl_wird_abgelehnt` (4c105ff, 35b3d51) | keine Regression, Verschärfung |
| 01-02 | `alle.py` nutzt ohne `--jahr` `STANDARD_JAHR` | `test_ohne_jahr_nutzt_standardjahr` grün; `pdf_relativ` einmal berechnet (c18a032) | keine Regression |
| 01-03 | Startseite zeigt „Der Haushalt 2026 der Gemeinde Ostbevern“, Jahr aus `app/src/data/jahrgang.json` | Titel `Der Haushalt ${jahrText} der Gemeinde Ostbevern`, Jahr aus `haushalt.json` (Pipeline-Ausgabe); `jahrgang.json` seit 370497f gelöscht. Absicht (Jahr aus Daten, nicht getippt) erhalten | keine Regression, Quelle gewechselt |
| 01-03 | Unbekannte Hash-Route leitet auf Start; Navigation und `PageIntro` laufen bei 360 px nicht über | `/:pathMatch(.*)*` → `start` (`router/index.ts:116`); `PageIntro` mit `hyphens: auto`, `overflow-wrap`; Playwright `mobil`: „360 × 640: Überlauf und Zielgröße je Route (A11Y-03) › Route /“ bis `/produkt/010601` (11 Routen) grün im Basislauf | keine Regression |
| 01-04 | Basismodule mit Münster-Namen; „und keine anderen Phase-5/7-Komponenten (D-03)“ | alle sieben Namen bestehen; der Zusatz galt nur für den Stand von Phase 1 und ist durch die Phasen 5 bis 7 planmäßig überholt (heute 47 Vue-Komponenten in app/src/components) | keine Regression |
| 01-04 | Demo-Diagramm mit Fixture und Beispieldaten-Hinweis | Fixture gelöscht (96a23de, D-15); Flag `beispieldaten` und Text „Beispieldaten — noch keine echten Haushaltszahlen.“ bleiben (`ChartCard.vue:38-41`, `chartcard.test.ts` grün); kein Aufrufer setzt das Flag | keine Regression, bewusst entfernt |
| 01-04 | Leerzustand „Noch keine Daten“ bei leerem Datensatz | Text seit Phase 5 „Keine Einzelwerte“ mit Erklärtext (UI-SPEC Copywriting); Zustand selbst durch `zustaende.test.ts` („leer: …“) belegt | keine Regression, Text geändert |
| 01-04 | `DatenTabelle`: semantische Tabelle, Zahlen rechtsbündig mit `tabular-nums`, scrollender Rahmen, klebende Labelspalte, Umbruch statt Abschneiden | `.om-zahl` in `basis.css:10-14`, `overflow-x: auto` (`DatenTabelle.vue:279`), `.om-tabelle__label` mit `position: sticky`, `max-width`, `hyphens: auto` (`:343-348`); Props jetzt Pflicht, Slot-Modus entfernt (D-16, D-19) | keine Regression, Props bewusst geändert (Advisory 2) |
| 01-04 | `ChartCard`: Slot-Container `min-width: 0`, Titel mit `hyphens: auto` | `ChartCard.vue:83` und `:69` | keine Regression |
| 01-04 | `format.ts` liefert die Sollstrings; Farben aus `echartsTheme.ts`, Gold zuerst, negativ/positiv über danger/success | Wahrheit 10; `KATEGORIE_FARBEN[0]` = `--wa-color-brand-60`, `POL_FARBEN` aus `success-50`/`danger-50` | keine Regression |
| 01-05 | `ci.yml`: Push und PR, zwei parallele Jobs, `contents: read`, SHA-Pins | siehe Wahrheit 6 und Deferred Items | keine Regression, Wortlaut durch Phase 7 überholt |
| 01-05 | Befehle und sechs Konventionen in `.claude/CLAUDE.md`; keine Root-`CLAUDE.md` | beides vorhanden (Wahrheit 5); die GSD-Blöcke wurden durch die Phasen 2 bis 8 planmäßig gefüllt | keine Regression |
| 01-05 | `LICENSE` MIT, README nennt Münster Money mit Link | `LICENSE` unverändert, `README.md:71` | keine Regression |
| 01-01 | Mensch bestätigt die Paketliste vor jeder Installation | Prozesswahrheit der Phase 1; `01-UAT.md` Tests 2 und 6 „pass“; die Lockfiles (`pipeline/uv.lock`, `app/package-lock.json`) sind getrackt | nicht code-prüfbar, unverändert |

Phase-8-Befunde zu Phase 1 (`01-REVIEW-DISPOSITION.md`): WR-01 bis WR-05 und IN-01 bis IN-05 stehen auf `fixed`, `open: 0`. Die Beleg-Commits sind im Repository vorhanden: `1c14077`, `c18a032`, `96a23de`, `4c105ff`, `35b3d51`, `fe416ab`. WR-01 (`base: './'`), WR-02 (`prefers-reduced-motion`) und WR-05 (Pflicht-Props) stehen heute im Code (Required Artifacts).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| SETUP-01 | 01-02, 01-05 | Repo-Struktur nach Spez. 7 existiert (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`), das Quell-PDF liegt unter `raw_data/` | ✓ SATISFIED | `git ls-files` zeigt Dateien in allen vier `daten/`-Unterordnern, `raw_data/haushalt-2026.pdf` ist getrackt, `discussion/` ohne PDF-Kopie; `test_pdf_existiert_mit_erwarteter_seitenzahl` grün (eigener Lauf, Basislauf); README „Aufbau“ nennt dieselbe Struktur |
| SETUP-02 | 01-01, 01-02 | Pipeline ist ein uv-Projekt (Python ≥ 3.12, pdfplumber, polars, typer, pytest), `uv run pytest` läuft | ✓ SATISFIED | `pyproject.toml` und `.python-version` 3.12; Basislauf: `uv sync --locked` Exit 0, `681 passed`, 0 Skips; eigener Lauf `73 passed` und `15 passed` |
| SETUP-03 | 01-01, 01-03, 01-04 | App-Grundgerüst (Vue 3, TS, Vite, Web Awesome, vue-echarts, Hash-Router) mit übernommenen Münster-Basiskomponenten, `npm run build` läuft | ✓ SATISFIED | Basislauf: Build Exit 0 (1069 Module), Vitest 2162 Tests; alle sieben Basismodule vorhanden; eigener Lauf der Komponententests: 61 grün |
| SETUP-04 | 01-05 | Projekt-CLAUDE.md dokumentiert Befehle und Konventionen (deutsche Bezeichner ohne Umlaute, Beträge als int-Euro, nur PDF-Seiten 1-basiert) | ✓ SATISFIED | `.claude/CLAUDE.md` heute gelesen: sechs Konventionen und alle Befehle, dazu Konventionen der späteren Phasen; zwei Abweichungen zum Code stehen unter Advisory |
| SETUP-05 | 01-02 | Jahrgangsspezifisches (Haushaltsjahr, Spaltenköpfe, Seitenbereiche, PDF-Pfad) steht in einer Konfigurationsdatei, nicht im Code | ✓ SATISFIED | `2026.toml` mit `haushaltsjahr`, `pdf_pfad`, `[spalten]`, `[seitenbereiche]`; `lade_jahrgang` liest die Datei; `grep -rlw 2026` auf Pipeline-Code ohne Tests: nur `STANDARD_JAHR` und ein Docstring; Basislauf: `alle.py` lädt „Jahrgang 2026 … 15 Seitenbereiche, Sollwerte geladen.“ |
| QUAL-01 | 01-03, 01-04, 01-05 | `vue-tsc` und ESLint laufen fehlerfrei in der CI | ✓ SATISFIED | Basislauf: `type-check` und `lint` Exit 0 auf dem Code von `head`; `ci.yml` ruft `npm run type-check` und `npm run lint` auf; GitHub-Lauf 37616724781: Schritte „Typprüfung (vue-tsc)“ und „ESLint“ `success` (Stand vor Phase 8) |

Keine verwaisten Anforderungen: `v1.0-REQUIREMENTS.md` ordnet SETUP-01 bis SETUP-05 und QUAL-01 der Phase 1 zu (Zeilen 190 bis 194 und 271, alle „Complete“); die Pläne 01-01 bis 01-05 deklarieren in `requirements` genau diese sechs IDs (01-01: SETUP-02, SETUP-03; 01-02: SETUP-01, SETUP-02, SETUP-05; 01-03: SETUP-03, QUAL-01; 01-04: SETUP-03, QUAL-01; 01-05: QUAL-01, SETUP-04, SETUP-01).

### Anti-Patterns Found

Gescannt wurden alle Implementierungsdateien der Fingerprint-Liste auf `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` (Groß-/Kleinschreibung beachtet) sowie, ohne Beachtung der Schreibweise, auf „coming soon“ und „not yet implemented“.

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| — | — | keine Debt-Marker, keine Platzhaltertexte | — | — |

Die Suche ohne Beachtung der Groß-/Kleinschreibung trifft nur `.claude/CLAUDE.md:7` („Münsterhack“, der Name des Hackathons) — Prosa, kein Marker, wie schon im Vorgängerbericht.

### Human Verification Required

Keine. Die Phase-1-UAT (`01-UAT.md`, 18 von 18 bestanden) bezog sich auf das damalige Gerüst mit Demo-Diagramm; die Startseite und die Basiskomponenten wurden in den Phasen 5 und 7 gebaut und dort per UAT sowie per Playwright (`mobil`, axe, Fokus, Kacheln) abgenommen. Keine Wahrheit dieser Phase verlangt heute eine menschliche Prüfung.

## Gaps Summary

Keine Lücken. Das Ziel von Phase 1 gilt auf dem heutigen Code: Pipeline und App bauen und testen grün (Basislauf auf `1d0df35`, unverändert bis HEAD), Konventionen und Jahrgangskonfiguration sind festgelegt und durch Tests gesichert, und die CI prüft Pushes auf `main` und jeden Pull Request (GitHub-Lauf 37616724781 grün). Die zwei Abweichungen vom Wortlaut des Plans 01-05 stammen aus Phase 7 und stehen unter Deferred Items; zwei Dokumentationsabweichungen stehen unter Advisory.

---

_Verified: 2026-10-09T06:29:13Z_
_Verifier: Claude (gsd-verifier-Verfahren, ausgeführt in Plan 09-04)_
