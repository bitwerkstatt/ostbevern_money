---
phase: 07-feinschliff-und-ver-ffentlichung
verified: 2026-10-07T08:30:00Z
status: gaps_found
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
  - "app/e2e/mobil.spec.ts"
  - "app/src/components/KennzahlKachel.vue"
  - "app/src/components/QuelleKnopf.vue"
  - "app/src/data/quellen.json"
  - "app/src/lib/kennzahlen.ts"
  - "app/src/lib/quelle.ts"
  - "app/src/pages/StartPage.vue"
  - "app/src/styles/basis.css"
  - "pipeline/ostbevern/belegbilder.py"
  - "pipeline/ostbevern/quellen.py"
  - "scripts/lighthouse-a11y.sh"
covered_digest: "v3:sha256:fe38f2fae0edb7dfead5bbd097799cc8f67749359f75ccebe955c94a6d5db281"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "Alle Seiten sind ab 360 px Breite nutzbar (ROADMAP SC 2; A11Y-03; Phasenziel „mobil nutzbar“)"
    status: failed
    reason: >
      Die KennzahlKachel läuft bei allen Breiten über 360 px über. Im Browser gemessen (Chromium im
      Docker-Image v1.63.0-noble, Build aus dem aktuellen Quellstand, Startseite): Bei 400, 560 und 600 px
      ragt der Knopf „Quelle anzeigen“ um 7 bis 21 px aus der grauen Kachel. Ab 700 px (Schrift 2xl) ragen die
      Beträge („27,5 Mio. €“, „-2,35 Mio. €“) um 12 bis 37 px aus der Kachel, auch bei 900, 1280 und 1440 px.
      Bei 768 px scrollt die Seite waagerecht auf „/“ (scrollWidth 795) und „/rat-entscheidet“ (829).
      Betroffen sind alle Seiten mit KennzahlKachel: „/“, „/investitionen“, „/rat-entscheidet“, „/stellenplan“.
      Bei exakt 360 und 380 px ist alles in Ordnung. „ab 360 px“ heißt 360 px und breiter; der Mobil-Test
      misst nur 360 × 640, deshalb blieb der Mangel unentdeckt.
    artifacts:
      - path: "app/src/styles/basis.css"
        issue: ".om-zahl { white-space: nowrap } lässt den Betrag in der Kachel nie umbrechen"
      - path: "app/src/pages/StartPage.vue"
        issue: "Grid repeat(auto-fit, minmax(160px, 1fr)): Spaltenbreite wird durch nowrap-Inhalt aufgeweitet (min-width:auto); Kacheln verlassen den Raster-Container"
      - path: "app/src/components/KennzahlKachel.vue"
        issue: "Kein min-width:0 / overflow-wrap für den Betrag; .om-kennzahl__wert wechselt ab 700 px auf 2xl, ohne dass die Kachelbreite mitwächst"
      - path: "app/src/components/QuelleKnopf.vue"
        issue: "Knopf in Variante kachel läuft über den Kachelrand, sobald die Kachelinnenbreite unter ca. 150 px fällt"
      - path: "app/e2e/mobil.spec.ts"
        issue: "Prüft nur 360 × 640; keine Breiten zwischen 361 und 1280 px, keine Kachel-Überlaufprüfung"
    missing:
      - "Betrag in der Kachel darf umbrechen oder schrumpfen (z. B. .om-kennzahl .om-zahl { white-space: normal; overflow-wrap: anywhere } oder Kachelraster mit minmax(min(100%, 12rem), 1fr) bzw. weniger Spalten); Raster-Kinder mit min-width: 0"
      - "Knopf „Quelle anzeigen“ in der Kachel darf umbrechen, ohne den Rand zu verlassen"
      - "Playwright-Test (Projekt mobil oder ci) mit Breiten 400, 480, 560, 700, 768, 1024, 1440: tile.scrollWidth <= tile.clientWidth für jede .om-kennzahl und documentElement.scrollWidth <= innerWidth auf allen Routen mit KennzahlKachel"
      - "Nach der Korrektur Beträge aus den Daten auf Lesbarkeit prüfen (längster Betrag: „-2,35 Mio. €“ bzw. in Euro-Anzeige ohne Kürzung)"
deferred: []
advisory: []
behavior_unverified_items: []
human_verification:
  - test: "Öffentliche Seite https://bitwerkstatt.github.io/ostbevern_money/ im Browser öffnen: keine 404 im Netzwerk-Tab (Icons, ein Belegbild unter /ostbevern_money/quellen/), direkter Reload von /#/ausgaben und /#/ueber, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei"
    expected: "Alle genannten Punkte funktionieren auf der echten URL"
    why_human: "Die Sandbox-Firewall blockiert github.io (HTTP 403 vom Proxy). Belegt ist über die GitHub-API nur: Repo public, Pages build_type workflow, Deployment-Status success. Die Nutzerantwort „veröffentlicht“ ist ein indirekter Beleg."
  - test: "Nach der Korrektur der Kachel: Startseite auf einem echten Gerät und im Browser bei 360, 400, 600, 768 und 1280 px ansehen"
    expected: "Beträge und Knopf „Quelle anzeigen“ bleiben in allen Kacheln innerhalb der grauen Fläche; kein waagerechtes Scrollen"
    why_human: "Schriftmetriken auf dem Gerät des Nutzers weichen von denen im Docker-Image ab; der Nutzer hat den Mangel ursprünglich selbst bemerkt."
---

# Phase 7: Feinschliff und Veröffentlichung Verification Report

**Phase Goal:** Die App ist belegbar, barrierefrei, mobil nutzbar und unter einer öffentlichen URL erreichbar.
**Verified:** 2026-10-07T08:30:00Z
**Status:** gaps_found
**Re-verification:** No, initial verification

## Zusammenfassung

Belegbarkeit, Barrierefreiheit (Diagramm-Tabellen, Fokus, Kontrast, reduzierte Bewegung, Lighthouse), Smoke-Test, Du-Anrede und Veröffentlichung sind im Code und in den Läufen belegt. Ein Ziel-Bestandteil ist nicht erreicht: „mobil nutzbar“ gilt nur bei exakt 360 bis etwa 380 px. Ab 400 px laufen Knopf und Beträge der Kennzahl-Kacheln aus der Kachel, und bei 768 px scrollt die Startseite waagerecht. Ich habe das selbst im Browser reproduziert; die Behauptung der Orchestrierung, die Desktop-Ansicht sei in Ordnung, stimmt nicht (siehe Evidenz).

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | „Quelle anzeigen“ an Kennzahlen und Tabellenzeilen öffnet eine Seitenleiste mit gerenderter WebP-Seite und markiertem Zeilenrechteck | ✓ VERIFIED | `app/src/data/quellen.json`: 2.496 Belege (ep 1.508, seite 231, gz 220, vb 145, inv 137, sp 123, pr 63, fp 41, meta 19, ve 6, sd 3), 231 Seiten, genau 231 WebP unter `app/public/quellen/` (18 MB), kein Waisenbild, jede `seiten`-Zeile hat ihr Bild. `ep:GESAMT:ordentliche_ertraege` hat `pdf_seite 62`, `bbox [42.05, 280.8, 561.74, 292.77]`. 264 Belege ohne bbox, laut Bericht `quellenbelege.md` dokumentiert; die App zeigt dann „Zeile nicht automatisch markiert“ statt zu raten. `QuelleKnopf.vue` rendert nur bei vorhandenem Beleg, `oeffneQuelle` öffnet die globale Leiste. Playwright `quelle.spec.ts` (Enter, Stellenplan-Querformat, Seiten-Beleg, Pro-Kopf) im 90-Test-Lauf des Orchestrators grün, Spezifikationen per `playwright test --list` bestätigt. |
| 2 | Tabellenalternative je Diagramm, Fokus beim Routenwechsel, Kontraste, `prefers-reduced-motion`, alle Seiten ab 360 px nutzbar | ✗ FAILED (Teilaspekt „ab 360 px“) | Tabellen/Fokus/Kontrast/Bewegung: `inventar.spec.ts` (Ausnahmeliste hat genau einen, begründeten Eintrag), `interaktion.spec.ts` (10 Routen-Fokus-Tests plus Menü- und Reduced-Motion-Tests), `basis.css` setzt unter `prefers-reduced-motion` Übergänge und Drawer-Dauern auf 0, axe in `smoke.spec.ts` ohne Verstöße: VERIFIED. **Nutzbarkeit ab 360 px: FAILED.** Eigene Messung (siehe Spot-Checks): Überlauf der Kacheln ab 400 px, waagerechter Seitenscroll bei 768 px. `mobil.spec.ts` prüft nur 360 × 640. |
| 3 | Lighthouse-Barrierefreiheit ≥ 95 auf allen Routen | ✓ VERIFIED | `scripts/lighthouse-a11y.sh` vorhanden, Werte 100 auf 11 Routen laut 07-12-SUMMARY und Orchestrator-Lauf auf b46259f. Ich habe Lighthouse nicht erneut gestartet (einmaliges Skript, nicht in CI); axe-Läufe mit WCAG-2-A/AA-Tags in `smoke.spec.ts` sind unabhängig grün. Hinweis: Lighthouse a11y misst keinen Überlauf aus dem Kachelrahmen, daher widerspricht 100 Punkte dem Befund unter Truth 2 nicht. |
| 4 | Playwright-Smoke-Test: jede Route ohne Konsolenfehler, Diagramme mit Daten; Textdurchgang Deutsch/Du-Anrede | ✓ VERIFIED | `smoke.spec.ts` deckt 11 Routen × 3 Tests (Rendern/Konsole/Daten, axe, axe mit offenen Bereichen) ab. `data-om-datenpunkte` in `BaseChart`. `duanrede.test.ts` läuft im vitest (45 Dateien, 1.967 Tests, von mir in einer identischen Scratch-Kopie ausgeführt: alle bestanden). Nutzerfreigabe der Texte: 07-10-SUMMARY „Freigegeben“. |
| 5 | GitHub Actions baut und deployt auf GitHub Pages (eigener Account); App unter öffentlicher URL erreichbar | ✓ VERIFIED (mit Resthinweis) | `gh run view 37576891540`: Jobs `app`, `pipeline`, `deploy` alle grün. `gh api .../pages`: `build_type: workflow`, `html_url https://bitwerkstatt.github.io/ostbevern_money/`. `gh api .../deployments`: Umgebung `github-pages`, Status `success`, SHA b46259f. Repo `private: false`. `ci.yml`: `deploy` nur bei `event != pull_request` und `ref == refs/heads/main`, `pages: write`/`id-token: write` nur im Deploy-Job, Actions auf Commit-SHAs gepinnt. Ladevorgang der Seite selbst von hier nicht prüfbar (Firewall), siehe Human Verification. |

**Score:** 4/5 Truths verified

### Weitere Plan-Truths (stichprobenartig, nicht reduzierend)

| Plan-Truth | Status | Evidenz |
| ---------- | ------ | ------- |
| 07-01/03: `quellen.json`-Schema, alle Belegtypen, Bilder je Seite, keine Waisen | ✓ VERIFIED | Siehe Truth 1. `pytest` (Pipeline) in Scratch-Kopie: 629 bestanden, 1 übersprungen (`typescript` nicht installiert), 1 Fehler `test_formatkuerzel_wie_format_ts` nur weil meine Kopie `app/src/charts/format.ts` nicht enthielt (Kopierfehler, kein Befund; Orchestrator meldet 631 grün). |
| 07-03: Schwärzung der Personenfelder per Test auf den eingecheckten Bildern | ✓ VERIFIED | Test in `test_belegbilder.py` ist Teil der 629 bestandenen. Seite 9 und weitere Amtsrollen-Seiten ungeschwärzt: vom Nutzer freigegeben (07-10, 07-SECURITY AR-03). |
| 07-05: `/ueber`, Impressum mit echten Werten, kein Platzhalter | ✓ VERIFIED | `config.test.ts` (im vitest-Lauf) prüft Bereitschaft; Werte aus 07-10-SUMMARY. |
| 07-09: `mobil.spec.ts` prüft Überlauf und 44 px-Ziele bei 360 × 640 | ⚠️ Zu eng | Test existiert und besteht, deckt aber nur eine Breite ab (siehe Gap). |
| 07-12: CI-identisches Gate, Lighthouse, Repo, Push | ✓ VERIFIED | Grüner CI-Lauf und Deployment per API belegt. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/src/data/quellen.json` | Belege + Seiten | ✓ VERIFIED | 2.496/231, Bilder vollständig |
| `app/public/quellen/*.webp` | 231 Bilder | ✓ VERIFIED | 231 Dateien, 18 MB |
| `daten/pruefberichte/quellenbelege.md` | Bericht mit Prüfliste | ✓ VERIFIED | Datei vorhanden |
| `app/src/components/QuelleKnopf.vue` / `QuelleSeitenleiste.vue` | Auslöser und Leiste | ✓ VERIFIED | Substanziell, verdrahtet (`oeffneQuelle`) |
| `app/e2e/{smoke,interaktion,inventar,mobil,quelle,textliste}.spec.ts` | Browser-Tests | ✓ VERIFIED | Alle gelistet; `mobil` zu eng (Gap) |
| `app/src/lib/__tests__/duanrede.test.ts` | Du-Wächter | ✓ VERIFIED | Teil der 1.967 grünen Tests |
| `.github/workflows/ci.yml` | Smoke + Deploy-Job | ✓ VERIFIED | Siehe Truth 5 |
| `scripts/lighthouse-a11y.sh` | Einmaliger Lauf | ✓ VERIFIED (mit CR-02) | Löscht ein vom Nutzer übergebenes `LH_SCRATCH`-Verzeichnis (Review CR-02, offen) |
| `app/src/styles/basis.css` / `KennzahlKachel.vue` | Responsive Kachel | ✗ DEFECT | Überlauf ab 400 px (Gap) |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `QuelleKnopf.vue` | `quellen.json` | `findeBeleg` → `oeffneQuelle` | ✓ WIRED | Kein Knopf ohne Beleg |
| `kennzahlen.ts` | `quelle.ts` | `belegSchluessel.ep(...)` | ✓ WIRED | Schlüssel lösen auf (Vertragstest `quelle-abdeckung`, `quelle-kacheln` grün) |
| `e2e/routen.ts` | `lib/menue.ts` | `menueLinks`, `FUSSZEILEN_ROUTEN` | ✓ WIRED | Routenliste datenabgeleitet |
| `ci.yml` `deploy` | `app` Artefakt | `upload-pages-artifact` → `deploy-pages` | ✓ WIRED | Lauf grün, Deployment success |
| `playwright.config.ts` | `mobil.spec.ts` | Projekt `mobil` | ✓ WIRED | Aber nur 360 × 640 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Real Data | Status |
| -------- | ------------- | ------ | --------- | ------ |
| `KennzahlKachel` auf „/“ | `wert` | `baueKennzahlen` aus `haushalt.json` | Ja (27,5 Mio. €, 30,5 Mio. €, -2,35 Mio. € im Browser gerendert) | ✓ FLOWING |
| Quelle-Leiste | `bbox`, `bild` | `quellen.json` | Ja | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| App-Unit-Tests | `npx vitest run` in Scratch-Kopie (src/e2e/package.json per `diff -rq` identisch zum Repo) | 45 Dateien, 1.967 Tests bestanden | ✓ PASS |
| Pipeline-Tests | `uv run --directory pipeline pytest -q` in Scratch-Kopie | 629 bestanden, 1 übersprungen, 1 Kopierartefakt-Fehler | ✓ PASS (mit Hinweis) |
| Playwright-Spezifikationen vorhanden | `playwright test --list` im Docker-Image | smoke, interaktion, quelle, mobil, textliste gelistet | ✓ PASS |
| Kachel-Überlauf bei Breiten 360 bis 1440 px | Chromium im Docker-Image, `dist` des aktuellen Quellstands, Messung `getBoundingClientRect` gegen Kachelrand | 360, 380, 440, 480, 520, 640: ok. 400, 560, 600: Knopf ragt 7 bis 21 px heraus. 700 bis 1440: Betrag ragt 12 bis 37 px heraus | ✗ FAIL |
| Seitenscroll auf allen Routen bei 360, 400, 480, 560, 640, 768 px | Chromium im Docker-Image | Nur bei 768 px: „/“ scrollWidth 795, „/rat-entscheidet“ 829 (innerWidth 768). Kachel-Überlauf zusätzlich auf „/investitionen“, „/stellenplan“ ab 400 px | ✗ FAIL |
| Screenshots | `raster-400.png`, `raster-1280.png`, `full-1440.png` im Scratchpad | Betrag „27,5 Mio. €“ und „-2,35 Mio. €“ endet sichtbar außerhalb der grauen Kachel; rechte Spalte bei 400 px abgeschnitten | ✗ FAIL (bestätigt visuell) |

Zur Abgrenzung gegenüber der Orchestrator-Evidenz: Die Aussage „bei 360 px und Desktop ist es in Ordnung“ trifft für 360 px zu, für Desktop nicht. Bei 1280 und 1440 px (Docker-Fallback-Schrift, Schrift auf dem Mac des Nutzers kann anders breit sein) überlaufen die Beträge ebenfalls. Der Befund ist unabhängig von der Schriftart, weil `white-space: nowrap` plus Rasterspalte (`minmax(160px, 1fr)`, 8 Spalten möglich) die Breite nicht begrenzt. Die Abweichung der Schrift kann nur die genaue Pixelzahl verändern.

### Probe Execution

Step 7c: übersprungen. Die Phase deklariert keine `probe-*.sh`; `find scripts -path '*/tests/probe-*.sh'` und die PLAN-Texte nennen keine solche Datei.

### Requirements Coverage

Alle zehn Phasen-IDs stehen in mindestens einem PLAN-Frontmatter (DATA-04: 01, 02, 03, 06; UI-02: 01, 06, 07, 08, 09; UI-06: 05; A11Y-01: 09; A11Y-02: 01, 09; A11Y-03: 09; A11Y-04: 04; QUAL-02: 04; DEPL-01: 11 (Truth) und 12; DEPL-02: 05). Keine verwaisten IDs: REQUIREMENTS.md ordnet nur diese zehn der Phase 7 zu.

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| DATA-04 | 07-01, 02, 03, 06 | Quellenbelege (`quellen.json`, `public/quellen/`) | ✓ SATISFIED | Truth 1 |
| UI-02 | 07-01, 06 bis 09 | „Quelle anzeigen“ öffnet Seitenleiste mit PDF-Ausschnitt | ✓ SATISFIED | Truth 1 |
| UI-06 | 07-05, 07-10 | Deutsch, Du-Anrede | ✓ SATISFIED | `duanrede.test.ts` grün, Texte vom Nutzer freigegeben |
| A11Y-01 | 07-09 | Tabellenalternative je Diagramm | ✓ SATISFIED | `inventar.spec.ts`, eine begründete Ausnahme |
| A11Y-02 | 07-01, 07-09 | Fokus, Kontrast, Reduced Motion | ✓ SATISFIED | `interaktion.spec.ts`, `basis.css`, axe grün |
| A11Y-03 | 07-09 | Alle Seiten ab 360 px nutzbar | ✗ BLOCKED | Nur bei 360 bis ca. 380 px erfüllt; ab 400 px Überlauf, bei 768 px Seitenscroll (Gap). In REQUIREMENTS.md als Complete markiert, das ist zu korrigieren. |
| A11Y-04 | 07-04 | Lighthouse a11y ≥ 95 | ✓ SATISFIED | 100 auf 11 Routen (07-12-SUMMARY, Orchestrator) |
| QUAL-02 | 07-04, 07-11 | Smoke-Test jede Route, Diagramme mit Daten | ✓ SATISFIED | `smoke.spec.ts` |
| DEPL-01 | 07-11, 07-12 | GitHub Actions baut und deployt | ✓ SATISFIED | CI-Lauf und Deployment-Status. REQUIREMENTS.md führt DEPL-01 noch als Pending (Pflegefehler); nach Evidenz erfüllt. |
| DEPL-02 | 07-05, 07-12 | Öffentliche URL | ✓ SATISFIED (human check empfohlen) | Pages-API, Deployment success |

REQUIREMENTS.md-Pflege: DATA-04, UI-02, A11Y-01, A11Y-02, QUAL-02, DEPL-01 stehen noch auf Pending, obwohl erfüllt. A11Y-03 steht auf Complete, obwohl nicht erfüllt.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `app/src/styles/basis.css` | 14 | `.om-zahl { white-space: nowrap }` ohne Ausnahme im Kachelkontext | 🛑 Blocker | Ursache des Betragsüberlaufs |
| `app/src/pages/StartPage.vue` | ~129 | `minmax(160px, 1fr)` bei nowrap-Inhalt | 🛑 Blocker | Raster wächst über den Container, Seitenscroll bei 768 px |
| `app/e2e/mobil.spec.ts` | 135 | Nur Breite 360 | ⚠️ Warning | Testlücke, die den Mangel durchließ |
| `scripts/lighthouse-a11y.sh` | 35-52 | `rm -rf "$S"` auf nutzereigenes `LH_SCRATCH` | ⚠️ Warning | Datenverlust-Risiko (Review CR-02, offen); Einmalwerkzeug |
| `app/src/lib/kennzahlen.ts` | 117-138 | Kacheln „Erträge“/„Aufwendungen“ `berechnet: false`, aber `herleitung` gesetzt | ⚠️ Warning | Seitenleiste sagt „Berechneter Wert, nicht im PDF“, Kachel trägt kein „berechnet“-Etikett (Review WR-05, offen); berührt den Kernwert „jede Zahl belegt“ auf der Startseite |
| `pipeline/ostbevern/belegbilder.py` | 87-113 | Rendert nur fehlende Bilder, nicht atomar | ⚠️ Warning | Review WR-01/WR-02: veraltete, ungeschwärzte Bilder bleiben bei geänderter Schwärzung unbemerkt |
| `pipeline/ostbevern/quellen.py` | 371, 652, 1045 | Rohe `IndexError`s | ⚠️ Warning | Review WR-03 |
| `.github/workflows/ci.yml` | 11-13 | Kommentar „Es gibt noch kein GitHub-Remote“ | ℹ️ Info | Veraltet, das Repository ist veröffentlicht |

Kein `TBD`/`FIXME`/`XXX` in `app/src`, `app/e2e`, `pipeline/ostbevern`, `pipeline/*.py`, `scripts`, `.github`.

### Prohibitions

| Prohibition (Plan) | Tier | Befund |
| ------------------ | ---- | ------ |
| 07-09: Inventar-Ausnahmeliste nicht erweitern | test | Liste hat genau einen Eintrag, `inventar.spec.ts` Z. 18-20: eingehalten |
| 07-11: nicht aus PR/Fork/anderem Branch als `main` deployen, `pages: write`/`id-token: write` nur im Deploy-Job | test | `ci.yml` bestätigt: eingehalten |
| 07-10: keine Textkorrekturen/Impressum vor Nutzerantwort; keine erfundenen Impressumdaten; kein Personenname im Material | judgment | Nicht-autoritatives Urteil: Antwort im 07-10-SUMMARY wörtlich protokolliert, Werte stammen daraus. `unverified-prohibition: Menschliche Prüfung empfohlen` |
| 07-11: keine Konsolenfilter / axe-Regeln ohne Begründung abschalten; kein Repository-Anlegen/Push durch den Agenten | judgment | Nicht-autoritativ: im Smoke-Spec nicht im Detail geprüft; Push erfolgte laut 07-12 durch den Nutzer. `unverified-prohibition: Menschliche Prüfung empfohlen` |
| 07-12: Lighthouse nicht vor Freigabe, nicht in `package.json`/CI; kein Repo/Push durch den Agenten | judgment | `lighthouse` in `app/package.json` nicht vorhanden (per Plan geprüft), Freigabe AR-06 dokumentiert. `unverified-prohibition: Menschliche Prüfung empfohlen` |

### Human Verification Required

1. **Öffentliche URL im Browser** — Test: https://bitwerkstatt.github.io/ostbevern_money/ öffnen, Netzwerk-Tab auf 404 prüfen, `/#/ausgaben` und `/#/ueber` direkt neu laden, Quelle-Leiste öffnen, Fußzeile und PDF-Link prüfen. Erwartung: alles funktioniert. Warum Mensch: Firewall blockiert github.io in der Sandbox.
2. **Kacheln nach der Korrektur** — Test: Startseite bei 360, 400, 600, 768, 1280 px auf dem Gerät des Nutzers. Erwartung: Beträge und Knopf bleiben in der Kachel, kein Seitenscroll. Warum Mensch: Geräteschrift weicht vom Docker-Image ab.

### Gaps Summary

Ein Blocker, eine Ursache: Die Kennzahl-Kachel (`KennzahlKachel` mit `.om-zahl { white-space: nowrap }` im Raster `minmax(160px, 1fr)`) ist nur bei 360 bis etwa 380 px stimmig. Der Betrag und der Knopf „Quelle anzeigen“ ragen ab 400 px aus der Kachel; ab 700 px (Schrift 2xl) ragen auch die Beträge heraus, auf Desktop-Breiten ebenfalls; bei 768 px scrollt die Seite waagerecht. Damit ist ROADMAP Success Criterion 2 („alle Seiten ab 360 px Breite nutzbar“) und A11Y-03 nicht erfüllt, und das Phasenziel „mobil nutzbar“ ist nur teilweise erreicht. Der Mobil-Test deckt nur 360 px ab; Lighthouse und axe messen diesen Überlauf nicht. Eine Korrektur braucht eine Anpassung an `basis.css`/`KennzahlKachel.vue`/`StartPage.vue`/`QuelleKnopf.vue` und einen Test über mehrere Breiten (Details im `gaps`-Block). Die Nacharbeitspunkte WR-01 bis WR-05 und CR-02 aus dem Code-Review sind keine Zielblocker, sollten aber gemeinsam mit der Korrektur geplant werden; WR-05 betrifft die Wahrhaftigkeit der Startseite („Erträge“ als berechnet oder nicht).

Alle übrigen Success Criteria (Belege, Diagramm-Tabellen, Fokus, Lighthouse, Smoke-Test, Du-Anrede, CI-Deploy, öffentliche URL) sind belegt. Die Veröffentlichung selbst ist durch GitHub-API-Evidenz gedeckt; DEPL-01 ist nach Evidenz erfüllt, obwohl REQUIREMENTS.md es noch als Pending führt.

---

_Verified: 2026-10-07T08:30:00Z_
_Verifier: Claude (gsd-verifier)_
