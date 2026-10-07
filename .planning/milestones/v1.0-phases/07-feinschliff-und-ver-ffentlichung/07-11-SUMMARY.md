---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 11
subsystem: qualitaetssicherung-deployment
tags: [playwright, axe, smoke-test, github-pages, github-actions, vitest, ssr, a11y]

requires:
  - phase: 07-09
    provides: "e2e/routen.ts (routen()), Inventar und 360-px-Pruefung, vollstaendige Diagrammbeschreibungen"
  - phase: 07-10
    provides: "Impressum ohne .invalid-Platzhalter, Route ueber"
provides:
  - "BaseChart: exportierte reine Funktion datenpunkte(option) und Attribut data-om-datenpunkte am Diagrammcontainer"
  - "src/components/__tests__/zustaende.test.ts: SSR-Zustandstests (laden, Fehler, leer, teilweise leer) fuer BaseChart und DatenTabelle"
  - "e2e/smoke.spec.ts: Smoke-Test je Route mit Konsole, Netz, Platzhalter, Diagrammdaten, Tabellenzeilen und axe"
  - "ci.yml: Playwright-Schritt, Pages-Upload (nur main) und Deploy-Job mit minimalen Rechten"
  - "README: Abschnitt Veroeffentlichung auf GitHub Pages"
affects: [07-12]

actuals:
  tokens: 6500
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "SSR-Zustandstests mit createSSRApp und renderToString aus vue/server-renderer; vue-echarts laedt in Node, kein Mock noetig"
    - "axe-Pruefung je Route im Standardzustand und mit geoeffneten wa-details unter reduzierter Bewegung (sonst misst axe Text mitten im Einblenden)"
    - "Deploy-Job als einziger Job mit pages: write und id-token: write, Bedingung event != pull_request und ref == refs/heads/main"

key-files:
  created:
    - app/e2e/smoke.spec.ts
    - app/src/components/__tests__/zustaende.test.ts
  modified:
    - app/src/components/BaseChart.vue
    - .github/workflows/ci.yml
    - README.md

key-decisions:
  - "datenpunkte() steht in einem zweiten, normalen script-Block von BaseChart.vue, weil script setup keine Exporte erlaubt; istLeer ist jetzt datenpunkte(option) === 0 (gleiche Zaehlung wie vorher)"
  - "Zustandstests rendern mit dem echten vue-echarts (laedt in Node); der im Plan vorgesehene vi.mock war nicht noetig"
  - "Der Smoke-Test prueft axe zusaetzlich mit geoeffneten wa-details (reduzierte Bewegung), damit auch die Tabellen in geschlossenen Bereichen auf Kontrast und Struktur geprueft sind"
  - "Der Kopfkommentar von ci.yml nennt die Rechte nicht woertlich, weil die Plan-Pruefung genau ein Vorkommen von pages: write und id-token: write verlangt"

requirements-completed: [QUAL-02, A11Y-02, DEPL-01]

coverage:
  - id: D1
    description: "BaseChart setzt data-om-datenpunkte auf die Zahl der Eintraege in data, links und edges aller Serien; Zustaende, Props und Slot unveraendert"
    requirement: "QUAL-02"
    verification:
      - kind: unit
        ref: "app/src/components/__tests__/zustaende.test.ts#datenpunkte() und BaseChart Zustaende"
        status: pass
    human_judgment: false
  - id: D2
    description: "Zustaende laden, Fehler, leer und teilweise leer von BaseChart und DatenTabelle (wa-skeleton, Fehlertext, Leerzustand, Zelle ohne Wert als Strich mit verborgenem 'kein Wert', nie 0)"
    requirement: "QUAL-02"
    verification:
      - kind: unit
        ref: "app/src/components/__tests__/zustaende.test.ts (11 Tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Smoke-Test je Route (11 Routen): Ueberschrift, keine Konsolenmeldung error oder warning, kein pageerror, nur Anfragen an den Preview-Server, keine Antwort ab Status 400, kein .invalid im Dokument, Diagramme mit Daten, Produktseite mit Tabellenzeilen"
    requirement: "QUAL-02"
    verification:
      - kind: e2e
        ref: "app/e2e/smoke.spec.ts (Projekt ci, Docker-Image playwright:v1.63.0-noble)"
        status: pass
    human_judgment: false
  - id: D4
    description: "axe (wcag2a, wcag2aa, wcag21a, wcag21aa) auf jeder Route ohne Verstoss, im Standardzustand und mit geoeffneten Bereichen; keine Regel abgeschaltet"
    requirement: "A11Y-02"
    verification:
      - kind: e2e
        ref: "app/e2e/smoke.spec.ts (22 axe-Tests, alle gruen)"
        status: pass
    human_judgment: false
  - id: D5
    description: "ci.yml: Playwright-Schritt, test:e2e nach dem Build, Pages-Upload nur auf main, Deploy-Job mit needs [pipeline, app], Bedingung nicht pull_request und refs/heads/main, concurrency pages, Rechte nur im Deploy-Job, SHA-gepinnte Actions"
    requirement: "DEPL-01"
    verification:
      - kind: other
        ref: "statische grep- und awk-Pruefungen der Plan-Verifikation und Akzeptanzkriterien; actionlint ohne Befund"
        status: pass
    human_judgment: true
    rationale: "Der Workflow laeuft erst nach dem Push des Nutzers (07-12); npx playwright install --with-deps chromium und der Pages-Deploy sind in der Sandbox nicht ausfuehrbar (RESEARCH A5, D-10)"
  - id: D6
    description: "README erklaert in deutscher Du-Anrede die Veroeffentlichung: Repository ostbevern-money in bitwerkstatt anlegen, Remote origin, Push main, Pages-Quelle GitHub Actions, URL https://bitwerkstatt.github.io/ostbevern-money/"
    requirement: "DEPL-01"
    verification:
      - kind: other
        ref: "grep auf bitwerkstatt.github.io/ostbevern-money und GitHub Actions in README.md"
        status: pass
    human_judgment: true
    rationale: "Ob die Anleitung am echten GitHub-Konto der Organisation funktioniert (Pages in der Organisation erlaubt, RESEARCH A4), bestaetigt der Nutzer bei 07-12"

duration: 30min
completed: 2026-10-06
status: complete
plan_head_before: 2f9f110e836f476b0a9ac34723e3b6297ab04723
plan_head_after: 92fc4ccec614e0aeac1ebd56249269f0db0e3364
---

# Phase 7 Plan 11: Smoke-Test mit axe und Pages-Deploy Summary

**Ein Playwright-Smoke-Test mit axe prüft alle 11 Routen des Produktionsbuilds auf Konsole, Netz, Platzhalter, Diagrammdaten und WCAG-AA-Kontrast und blockiert in der CI den neuen, auf `main` beschränkten GitHub-Pages-Deploy-Job; BaseChart meldet seine Datenmenge über `data-om-datenpunkte`.**

## Performance

- **Duration:** ca. 30 min
- **Tasks:** 3
- **Files modified:** 5 (2 neu)

## Accomplishments

- **BaseChart:** `datenpunkte(option)` zählt `data`, `links` und `edges` aller Serien und ersetzt die frühere Inline-Zählung in `istLeer`; der Diagrammcontainer trägt `data-om-datenpunkte`. Vier Zustände, Props und Slot sind unverändert.
- **Zustandstests (TDD, RED `f213e7f`, GREEN `068b92e`):** 11 Tests rendern BaseChart und DatenTabelle mit `vue/server-renderer`: `laedt` zeigt `wa-skeleton` ohne Diagramm oder Tabelle, `fehler` den Fehlertext, leere Serien oder `zeilen: []` den Leerzustand, eine Zelle ohne Wert den Strich mit dem verborgenen „kein Wert“ und nie `value="0"`. Das echte vue-echarts lädt in Node, der Plan-Fallback (`vi.mock`) war nicht nötig.
- **Smoke-Test:** `e2e/smoke.spec.ts` läuft je Route (`routen()`) mit drei Tests (33 insgesamt). Alle grün im Playwright-Image, ohne gefilterte Meldung und ohne abgeschaltete axe-Regel. Gemessene Diagramme je Route (Plan-Kontrolle gegen RESEARCH): `/einnahmen` 3, `/ausgaben` 2, `/geldfluss` 1, `/entwicklung` 9, `/investitionen` 5, `/rat-entscheidet` 4, `/stellenplan` 6, Startseite, Glossar, Über 0; die Produktseite `/produkt/010601` hat drei Tabellen mit 14, 20 und 3 Zeilen.
- **CI/Deploy:** `workflow_dispatch`, Playwright-Chromium, `npm run test:e2e` nach dem Build, Pages-Upload nur auf `main`, Job `deploy` mit `needs: [pipeline, app]`, `concurrency: pages` ohne Abbruch, Environment `github-pages` mit `page_url`. Die globalen Rechte bleiben `contents: read`; `pages: write` und `id-token: write` stehen genau einmal, im Deploy-Job. `actionlint` meldet nichts.
- **README:** Abschnitt „Veröffentlichung auf GitHub Pages“ mit den Schritten Repository anlegen, Remote, Push, Pages-Quelle, URL und Hinweis auf `base: './'` und Hash-Router. Kein Repository angelegt, kein Remote gesetzt, nichts gepusht (D-10).

## Task Commits

1. **Task 1 RED:** `f213e7f` (test) SSR-Zustandstests
2. **Task 1 GREEN:** `068b92e` (feat) `datenpunkte()` und `data-om-datenpunkte`
3. **Task 2:** `f4fad93` (test) Smoke-Test mit axe
4. **Task 3:** `92fc4cc` (feat) CI-Smoke-Schritt, Deploy-Job, README

## Verifikation

- `npm run test` 1967 Tests grün, `type-check`, `lint`, `format:check` sauber (frischer `npm ci` im Worktree).
- Plan-Verifikation Aufgabe 2: `playwright test --project=ci` im Docker-Image `mcr.microsoft.com/playwright:v1.63.0-noble` gegen `vite preview` des Builds: 76 Tests grün (33 Smoke-Tests plus Quelle, Inventar, Interaktion).
- Aufgabe 3: alle statischen Prüfungen der Verifikation und Akzeptanzkriterien erfüllt (SHA-Pins 5 von 5, `needs: [pipeline, app]`, Rechte genau einmal und im Deploy-Job, globales `contents: read`).
- Nicht ausführbar in der Sandbox: `npx playwright install --with-deps chromium` auf ubuntu-latest und der Pages-Deploy selbst (Firewall, kein Remote); statisch geprüft, der erste echte Lauf folgt nach dem Push des Nutzers (07-12).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Scheinverstöße bei axe mit geöffneten Bereichen**
- **Found during:** Task 2
- **Issue:** Der ergänzende axe-Test mit geöffneten `wa-details` meldete Kontrastwerte von 1,2 bis 2,1 auf allen Routen mit Tabellen. Ursache war der Test, nicht die App: axe las den Text mitten im Einblenden mit halber Deckkraft (der Standardzustand war auf allen Routen grün).
- **Fix:** Der Test öffnet unter `emulateMedia({ reducedMotion: 'reduce' })` (Übergänge laut 07-09 auf 0) und wartet zwei Frames und alle endlichen Animationen ab. Danach ohne Verstoß, ohne Regel abzuschalten und ohne Eingriff in die App.
- **Files modified:** app/e2e/smoke.spec.ts
- **Commit:** f4fad93

### Erweiterung gegenüber dem Plan

- **Zusätzlicher axe-Lauf mit geöffneten Bereichen** (11 weitere Tests): Der Plan verlangt axe „nach dem Rendern der Diagramme“; geschlossene `wa-details` blenden Tabellen vor axe aus. Der zweite Lauf prüft sie mit, ohne neue Befunde an der App.
- **Zustandstests ohne `vi.mock`:** vue-echarts lädt in Node, daher der im Plan genannte Fallback nicht benötigt.

**Total deviations:** 1 auto-fixed (Testartefakt), 2 Anmerkungen. **Impact:** Keine Änderung an App-Komponenten außer dem Zählattribut an BaseChart; es fanden sich keine echten axe-, Konsolen-, Netz- oder Platzhalterbefunde an der App.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. Die Plan-Bedrohungen sind mitigiert: T-07-24 (Rechte nur im Deploy-Job, Bedingung main und nicht pull_request, per grep und awk geprüft), T-07-25 (volle Commit-SHAs mit Versionskommentar), T-07-26 (Smoke-Test scheitert bei Anfrage außerhalb des Preview-Ursprungs), T-07-27 (Smoke-Test scheitert bei `.invalid`), T-07-SC (`npx playwright install` nutzt das gepinnte `@playwright/test` 1.63.0, kein neues Paket).

## Next Phase Readiness

- 07-12: Nach dem Push läuft der Workflow zum ersten Mal auf ubuntu-latest (Playwright-Download dort, GitHub-Pages-Freigabe der Organisation bitwerkstatt laut RESEARCH A4 bestätigen, Pages-Quelle auf „GitHub Actions“ stellen). Die README-Schritte sind die Anleitung dafür.

## Self-Check: PASSED

- Dateien vorhanden: app/e2e/smoke.spec.ts, app/src/components/__tests__/zustaende.test.ts, app/src/components/BaseChart.vue, .github/workflows/ci.yml, README.md.
- Commits vorhanden: f213e7f, 068b92e, f4fad93, 92fc4cc.
- Akzeptanzkriterien aller drei Aufgaben erfüllt.

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
