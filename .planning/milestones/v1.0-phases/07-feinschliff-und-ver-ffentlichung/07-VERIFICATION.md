---
phase: 07-feinschliff-und-ver-ffentlichung
verified: 2026-10-09T06:36:00Z
status: passed
score: "4/5 must-haves vom Verifier geprüft (Kriterien 1 bis 4), 1/5 vom Nutzer bestätigt (Kriterium 5 samt Gerätecheck, 2026-10-08), keines davon als vom Verifier geprüft gezählt"
covered_files:
  - ".github/workflows/ci.yml"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-01-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-01-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-02-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-02-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-03-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-03-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-04-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-04-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-05-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-05-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-06-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-06-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-07-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-07-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-08-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-08-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-09-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-09-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-10-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-10-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-11-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-11-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-12-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-12-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-13-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-13-SUMMARY.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-14-PLAN.md"
  - ".planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-14-SUMMARY.md"
  - "README.md"
  - "app/e2e/interaktion.spec.ts"
  - "app/e2e/inventar.spec.ts"
  - "app/e2e/kacheln.spec.ts"
  - "app/e2e/mobil.spec.ts"
  - "app/e2e/quelle.spec.ts"
  - "app/e2e/smoke.spec.ts"
  - "app/e2e/textliste.spec.ts"
  - "app/playwright.config.ts"
  - "app/src/App.vue"
  - "app/src/components/DatenTabelle.vue"
  - "app/src/components/EbenenTabelle.vue"
  - "app/src/components/QuelleKnopf.vue"
  - "app/src/components/QuelleSeite.vue"
  - "app/src/components/QuelleSeitenleiste.vue"
  - "app/src/components/__tests__/zustaende.test.ts"
  - "app/src/components/datenTabelle.ts"
  - "app/src/config.ts"
  - "app/src/data/quellen.json"
  - "app/src/lib/__tests__/duanrede.test.ts"
  - "app/src/lib/__tests__/quelle-ui-abdeckung.test.ts"
  - "app/src/lib/produkt.ts"
  - "app/src/lib/quelle.ts"
  - "app/src/pages/UeberPage.vue"
  - "app/src/router/index.ts"
  - "app/src/styles/basis.css"
  - "pipeline/08_quellenbelege.py"
  - "pipeline/ostbevern/belegbilder.py"
  - "pipeline/ostbevern/quellen.py"
  - "scripts/e2e-wie-ci.sh"
  - "scripts/lighthouse-a11y.sh"
covered_digest: "v3:sha256:22d8272340df5b7214d06a647dccfc145e2941248fd52f1154c1c3ed3ab99fe7"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "4/5 must-haves verified"
  gaps_closed:
    - "Phase-8-Befund 08/WR-02 (D-20): Der Phase-8-Fix 98803c4 ließ bei leerer Beschriftung Rolle, Namen und Tabstopp des überlaufenden Tabellenrahmens der DatenTabelle entfallen (A11Y-01, WCAG 2.1.1). 78744d4 (Plan 09-02) schließt das: tabellenRahmen setzt den Ersatznamen „Tabelle“, der Rahmen bleibt per Tastatur erreichbar und benannt."
  gaps_remaining: []
  regressions: []
gaps: []
deferred:
  - truth: "CR-01 des Code-Reviews von Phase 7: Namen und Unterschriften zweier Personen stehen ungeschwärzt im ausgelieferten Belegbild app/public/quellen/s009.webp"
    addressed_in: "Nutzerentscheidung vom 2026-10-07 (kein Folgeplan)"
    evidence: "07-REVIEW-DISPOSITION.md, Zeile CR-01: disposition deferred, „bleibt so — öffentliche Satzung, Amtsträger unterzeichnen in amtlicher Funktion; Bild s009.webp unverändert“. Das Bild ist seit 82713f0 (2026-10-06) unverändert. Kein Befund dieses Berichts, keine Regression (D-22)."
advisory:
  - finding: "Kriterium 3 (Lighthouse-Barrierefreiheit ≥ 95) beruht auf der Lighthouse-Messung vom 2026-10-07 (100 auf 11 Routen, Plan 07-12) und heute nur auf axe (WCAG 2.0/2.1 A und AA, null Verstöße auf allen elf Routen, auch mit geöffneten Bereichen)."
    category: other
    reason: "scripts/lighthouse-a11y.sh braucht Docker und eine Paketprüfung durch den Nutzer (Plan 07-12) und läuft in diesem Plan nicht; seit der Messung hat Phase 8 DatenTabelle, App.vue und Tokens geändert. Lighthouse nutzt axe-core, bewertet aber auch Regeln außerhalb der WCAG-Tags; ein Lauf auf dem Endstand würde den Befund endgültig belegen."
    evidence_status: "indirekt: axe grün im Basislauf, Lighthouse nicht neu gemessen"
behavior_unverified_items: []
human_verification:
  - test: "Stand main pushen, im Reiter Actions den Lauf abwarten: Jobs app, pipeline und deploy müssen grün sein. Im Log des Jobs app zeigt der Schritt „Smoke-Test (Playwright + axe)“ vier Zeilen „Schrift der Beträge auf …: DejaVu Sans“, und kacheln.spec.ts besteht. Danach https://bitwerkstatt.github.io/ostbevern_money/ öffnen: keine 404 (Icons, Belegbild unter /ostbevern_money/quellen/), Reload von /#/ausgaben und /#/ueber, Quelle-Leiste zeigt ihr Bild, Fußzeile zeigt die Kontakt-Adresse, PDF-Link öffnet die Gemeinde-Datei, Kacheln sitzen in der grauen Fläche"
    expected: "Grüner Lauf samt Deploy, öffentliche Seite zeigt den Kachel-Fix"
    why_human: "Push ist Sache des Nutzers (D-10), die Sandbox-Firewall blockiert github.io und die Actions-API. Der letzte bekannte GitHub-Lauf (37589932223) war rot; ob der Runner ubuntu-24.04 tatsächlich dieselbe Schrift wie die lokale Nachstellung rendert, belegt erst ein grüner Lauf. Backstop-Must-have von 07-14."
    beleg: "vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft"
  - test: "Startseite, /investitionen, /rat-entscheidet und /stellenplan auf dem eigenen Gerät bei 360, 400, 600, 768 und 1280 px ansehen (die Spur ist mit 07-14 breiter geworden)"
    expected: "Jeder Betrag und jeder Knopf „Quelle“ liegt innerhalb der grauen Kachel, bündig mit der Überschrift; kein waagerechtes Scrollen der Seite"
    why_human: "Geräteschriften weichen von DejaVu Sans ab; die UAT-Bestätigung (Test 1: pass) galt dem Stand vor 07-14. Backstop-Must-have von 07-14, nie vom Verifier als erfüllt zu markieren."
    beleg: "vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft"
---

# Phase 7: Feinschliff und Veröffentlichung Verification Report

**Phase Goal:** Die App ist belegbar, barrierefrei, mobil nutzbar und unter einer öffentlichen URL erreichbar.
**Verified:** 2026-10-09T06:36:00Z
**Status:** passed (Kriterien 1 bis 4 vom Verifier geprüft; Kriterium 5 und Gerätecheck vom Nutzer bestätigt, siehe „Nutzerbestätigung (D-14)“)
**Re-verification:** Ja, Phase 9 (AUD-02), gegen den Endstand nach Phase 8 und dem D-20-Fix aus Plan 09-02

## Warum diese Re-Verifikation (Phase 9, AUD-02)

Der vorige Bericht (verifiziert auf Stand 137b05d vom 2026-10-07, `status: passed`, Score „4/5 must-haves verified“, Digest v2) galt für den Code vor Phase 8. Seitdem haben Phase 8 und die Wellen 1 und 2 von Phase 9 Phase-7-Code geändert; `gsd-tools` meldete den Bericht deshalb als `stale` (Basislauf, Abschnitt „Verifikationsstatus vor der Re-Verifikation“). Dieser Bericht ersetzt ihn. Er ist ein neuer Goal-Backward-Lauf nach dem Verfahren von `gsd-verifier` im Re-Verifikationsmodus (Schritt 0, Schritte 3 bis 9, Abschnitt „Create VERIFICATION.md“), ausgeführt in Plan 09-10, weil Executoren den Subagenten nicht starten können. Jede Wahrheit des alten Berichts und jedes ROADMAP-Kriterium von Phase 7 wurde gegen den heutigen Code geprüft, nicht aus dem alten Bericht übernommen.

Was sich an Phase-7-Code seit dem alten Berichtsstand 137b05d geändert hat (`git diff --stat 137b05d HEAD -- app/src app/e2e` : 96 Dateien; `pipeline`, `daten`, `scripts`, `.github`, `README.md` und `app/package*.json`: 22 Dateien):

- **Review-Fixes von Phase 7 nach dem alten Berichtsstand** (2026-10-07, 11:54 bis 12:52 +0200): ef612e9 (WR-06, Schrift der Kalibrierung im Workflow herstellen), 3db0795 (WR-07), f3efd0a, f024de9, 8523030, a3f05af, 2cb379e, bf956ff (IN-07 bis IN-12) an `ci.yml`, `kacheln.spec.ts`, `e2e-wie-ci.sh`, `basis.css`, `README.md`. Der alte Bericht beschrieb `ci.yml` noch als „nur `runs-on` plus Kommentar geändert“; heute enthält der Job `app` zusätzlich den Schritt „Schrift der Kalibrierung sicherstellen“ (Z. 98-113). Die Aussage ist unten neu geprüft.
- **Phase 8** (2026-10-07 bis 2026-10-08): 08-06 (fe416ab Tabellenrahmen der `DatenTabelle`, df0d2b0 Drawer-Linkklick in `App.vue`, e75a05b `ProduktAkkordeon`), 13eb786 und 98803c4 (WR-02, WR-03), 28462a7 (`ci.yml`, nur Kommentarzeilen; geprüft mit `git show 28462a7 -- .github/workflows/ci.yml`: keine Nicht-Kommentarzeile geändert), Refactors der Jahr-, Kennzahl- und Stellenlogik (08-02 bis 08-11).
- **Phase 9, Welle 1** (Plan 09-02, D-20): 78744d4 und 8b4ae20 an `DatenTabelle.vue`, `datenTabelle.ts` und `zustaende.test.ts`.

Seit dem Kopf des Basislaufs (`1d0df35`) hat sich kein Codepfad geändert: `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline app daten scripts .github` endet mit Exit 0. Die Läufe aus `09-BASISLAUF.md` gelten damit für den hier geprüften Code.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | „Quelle anzeigen“ öffnet Seitenleiste mit WebP-Seite und markiertem Zeilenrechteck | ✓ VERIFIED | Auslöser: `QuelleKnopf.vue` Z. 47-63 (Knopf nur, wenn `findeBeleg` den Schlüssel auflöst, `lib/quelle.ts` Z. 87-105), eingesetzt in `KennzahlKachel.vue`, `ProduktPage.vue` und in der Tabellenspalte `art: 'quelle'` von `DatenTabelle.vue` Z. 211-219 (genutzt u. a. von `EbenenTabelle`, `SteuerZeitreihe`, `ZuschussListe`, `StellenNachGruppe`, `EinnahmenPage`, `AusgabenPage`). Seitenleiste: `QuelleSeitenleiste.vue` Z. 80-130 (`wa-drawer`, Wertzeile, Hinweis, Original-Link), global eingebunden in `App.vue` Z. 228. Bild und Rechteck: `QuelleSeite.vue` (`img` mit `bildUrl`, Markierung aus `bboxProzent`, Scroll erst nach `wa-after-show`). Daten: `quellen.json` hat 2496 Belege und 231 Seiten, `app/public/quellen/` 231 WebP-Dateien. Basislauf: Schritt 08 „2496 Belege, 33 ohne Markierung, 231 Seiten, 0 Bilder neu gerendert“, `alle.py` byte-identisch; Playwright `ci`: `quelle.spec.ts:121` „Klick öffnet die Seitenleiste mit Bild und Markierung, Escape gibt den Fokus zurück“, `:139`, `:158`, `:186`, `:203`, `:262` „Tabellenzeilen-Knopf auf /ausgaben“, `:294` „Stellenplan-Zeile … Querformatseite mit der Markierung im Bild“, `:335`, `:364`. Eigener Lauf: `pytest tests/test_quellen.py tests/test_belegbilder.py` 74 bestanden. Phase 8 hat die Quell-Komponenten nicht geändert (nur Kommentare in `quelle*.test.ts`, 4b45a07). |
| 2 | Tabellenalternative je Diagramm, Fokus beim Routenwechsel, Kontraste, `prefers-reduced-motion`, alle Seiten ab 360 px nutzbar | ✓ VERIFIED | **Tabellenalternative:** Basislauf `inventar.spec.ts:39` „jedes Diagramm hat Tabelle und Beschreibung“ auf elf Routen (`/`, `/einnahmen`, `/ausgaben`, `/geldfluss`, `/entwicklung`, `/investitionen`, `/rat-entscheidet`, `/stellenplan`, `/glossar`, `/ueber`, `/produkt/010601`), Ausnahmeliste weiter genau ein Eintrag (`inventar.spec.ts` Z. 18-20). **Fokus:** `router/index.ts` Z. 128-148 (Titel, Fokus auf `h1` oder Hash-Ziel, Ansage), Basislauf `interaktion.spec.ts:278` „Fokus und Titel bei jedem Routenwechsel“ für zehn Routen; Menü-Drawer schließt bei jedem Linkklick (`App.vue` Z. 58-130; `interaktion.spec.ts:314-334`, `mobil.spec.ts:223-243`, D-21). **Kontraste:** `smoke.spec.ts:185` und `:191` (axe WCAG 2.0/2.1 A und AA, auch mit geöffneten `wa-details`) auf allen elf Routen grün. **Reduzierte Bewegung:** `basis.css` Z. 71-88 (Übergangs-Tokens und Drawer-Dauern 0), `BaseChart.vue` Z. 60 (`ohneAnimation`), Basislauf `quelle.spec.ts:218`, `interaktion.spec.ts:393`, `:407`, `:419`. **ab 360 px:** `mobil.spec.ts:151` „Überlauf und Zielgröße je Route“ auf elf Routen, `:181` und `:194` „Tabellenrahmen bei 360 px“ (Rahmen mit Rolle und genau einem Namen, axe mit geöffneten Bereichen) auf elf Routen, `:251`, `:281`, `:311` (Leiste, Drawer, Querformatseite); `kacheln.spec.ts:465` auf den vier Kachelrouten, alle Breiten inklusive Spaltensprünge. **Phase-8-Änderungen daran neu geprüft:** `DatenTabelle.vue` Z. 132-142 und `datenTabelle.ts` Z. 78-84 (`tabellenRahmen`: überlaufender, gerenderter Rahmen hat immer Tabstopp, Rolle und Namen, Ersatzname „Tabelle“); eigener Lauf `vitest run src/components/__tests__/zustaende.test.ts`: 24 bestanden, darunter „leere Beschriftung mit Überlauf: Rahmen bleibt erreichbar, Name ist ‚Tabelle‘“. Basislauf: `ci` 89, `mobil` 41 bestanden, vitest 2162 bestanden. |
| 3 | Lighthouse-Barrierefreiheit ≥ 95 auf allen Routen | ✓ VERIFIED (indirekt, Lighthouse nicht neu gemessen) | Letzte Messung 100 auf elf Routen laut `07-12-SUMMARY.md` (2026-10-07), vor Phase 8. Auf dem Endstand nicht wiederholt (Docker und Paketprüfung nötig, in diesem Plan nicht ausführbar). Heutige Evidenz: axe-core, die Grundlage der Lighthouse-Bewertung, meldet im Basislauf null Verstöße gegen WCAG 2.0/2.1 A und AA auf allen elf Routen, auch mit geöffneten Bereichen (`smoke.spec.ts:185`, `:191`) und bei 360 px (`mobil.spec.ts:194`, axe mit geöffneten Bereichen auf allen elf Routen). Das Skript `scripts/lighthouse-a11y.sh` ist weiter vorhanden; der Review-Fix CR-02 (Z. 36-48: frisches Unterverzeichnis, Löschschutz) ändert die Messung nicht. Vermerkt unter `advisory`. |
| 4 | Playwright-Smoke-Test: jede Route ohne Konsolenfehler, Diagramme mit Daten; Textdurchgang Deutsch/Du-Anrede | ✓ VERIFIED | `smoke.spec.ts:138` „rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten“ auf elf Routen grün (Basislauf, `ci`); Routenliste aus `routen.ts`, nichts getippt. Textdurchgang: `duanrede.test.ts` scannt `texte.json`, alle Vue-Templates und Skriptzeichenketten, geschlossene Ausnahmeliste; Teil des grünen vitest-Laufs (2162 Tests, 49 Dateien); Projekt `texte` (`textliste.spec.ts:118`) bestanden. Phase 8 hat Texte geändert (7d4be31, e8e25d5: Jahreszahlen als Platzhalter); `duanrede.test.ts` und `texte.test.ts` laufen auf diesem Stand grün. |
| 5 | GitHub Actions baut und deployt auf GitHub Pages; App unter öffentlicher URL erreichbar | ✓ VOM NUTZER BESTÄTIGT (2026-10-08, D-14), nicht vom Verifier geprüft | Quelltext vom Verifier geprüft: `ci.yml` Z. 64-121 (Job `app`: `runs-on: ubuntu-24.04`, Schrift der Kalibrierung, `npm run test:e2e`, Upload nur bei Push auf `main`), Z. 123-139 (Job `deploy`: `needs: [pipeline, app]`, nur `main`, `pages: write`, `id-token: write`, `actions/deploy-pages`), `vite.config.ts` `base: './'` mit Hash-Router, README Z. 39-55 (Einrichtung). Ob der Lauf auf GitHub grün ist, der Deploy erfolgte und die URL erreichbar ist, kann der Verifier nicht prüfen (Firewall, kein Zugriff auf github.io und die Actions-API). Der Nutzer hat am 2026-10-08 erklärt, den grünen Lauf samt Deploy und die öffentliche URL selbst geprüft zu haben; zusätzlich steht „pass“ in `07-UAT.md` Test 1 (2026-10-07). Der Verifier zählt das Kriterium nicht als selbst geprüft. Siehe Human-Item 1 und „Nutzerbestätigung (D-14)“. |

**Score:** 4/5 Truths vom Verifier geprüft (Kriterien 1 bis 4; 0 present, behavior-unverified), 1/5 vom Nutzer bestätigt (Kriterium 5, D-14). Der Gerätecheck (Human-Item 2) ergänzt Kriterium 2 und ist ebenfalls nur vom Nutzer bestätigt; Kriterium 2 steht auf VERIFIED allein wegen der automatischen Prüfungen. Kein vom Nutzer bestätigtes Item ist als vom Verifier geprüft gezählt.

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | CR-01 des Code-Reviews von Phase 7: Namen und Unterschriften zweier Personen auf `app/public/quellen/s009.webp` | Nutzerentscheidung vom 2026-10-07 (kein Folgeplan) | `07-REVIEW-DISPOSITION.md`, Zeile CR-01: `deferred`, „bleibt so — öffentliche Satzung, Amtsträger unterzeichnen in amtlicher Funktion; Bild s009.webp unverändert“. `git log` zeigt für `s009.webp` nur 82713f0 (2026-10-06), das Bild ist unverändert. Nicht erneut geöffnet, weder Lücke noch Regression (D-22). |

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | Lighthouse-Barrierefreiheit (Kriterium 3) auf dem Endstand nicht neu gemessen, nur axe grün | other | Docker und Paketprüfung nötig (Plan 07-12); indirekt belegt, kein deterministischer Lighthouse-Lauf |

### Regressionsprüfung der Plan-Must-haves

Geprüft wurden die `must_haves`-Artefakte der 14 Pläne, die sich seit dem alten Berichtsstand 137b05d geändert haben (Schnitt aus den Pfaden der Pläne und `git diff --name-only 137b05d HEAD`): `ci.yml`, `README.md`, `basis.css`, `UeberPage.vue` (liest `config.ts`), `EbenenTabelle.vue`, `produkt.ts`, `zustaende.test.ts`, `duanrede.test.ts`, `stiltokens.test.ts`, `quelle*.test.ts`, `kacheln`-, `mobil`-, `interaktion`-, `quelle`- und `smoke`-Spec, `e2e-wie-ci.sh`, `lighthouse-a11y.sh` sowie `08_quellenbelege.py`, `belegbilder.py`, `quellen.py` und `test_belegbilder.py`. Ergebnis:

- `EbenenTabelle.vue` und `produkt.ts` haben nur die Einwohnerzahl über `einwohnerZahl()` und die rd.-Regel über `betragMitHinweis` zentralisiert (08-02, 08-03); die Quelle-Spalte und die Belegschlüssel sind unverändert. `quelle-ui-abdeckung.test.ts` (eigener Lauf, 7 bestanden) und `quelle-kacheln`, `quelle-kontext`, `quelle-leitfragen` (Basislauf-vitest) bestätigen, dass jede Kachel und jede Quelle-Spalte weiter auf den Beleg verweisen.
- `quelle.spec.ts` prüft den Seitenbeleg ohne Markierung jetzt an der Zeile „Weitergabe an Kreis und Land“ auf `/ausgaben` statt an einer Stellenplan-Kachel, weil diese Kacheln seit 08-03 „berechnet“ sind (c3b1406). Das ist eine Anpassung des Tests an die Phase-8-Fachlogik, keine Abschwächung: die Aussage „Zeile nicht automatisch markiert, keine Markierung“ wird weiter geprüft (`quelle.spec.ts:335`, Basislauf bestanden).
- `UeberPage.vue`: Der Abschnitt „Dank“ heißt „Dank und Informationen“ und ist um den Hinweis auf KI, Nachprüfbarkeit über die Quelle und Rundung ergänzt. Impressumsfelder, Kontakt und Original-PDF-Link kommen weiter aus `config.ts`; `duanrede.test.ts` ist grün.
- Die übrigen geänderten Artefakte sind Review-Fixes von Phase 7 (siehe oben), Kommentarpflege und die Tests zu D-20. Eine Regression gegenüber einer Phase-7-Wahrheit ergab sich nicht (`re_verification.regressions: []`).

### Plan-07-14-Truths und Prohibitions (gegen den heutigen Code geprüft)

| Plan-Truth / Prohibition | Status | Evidenz |
| ------------------------ | ------ | ------- |
| li des Kachelrasters mit Außenabstand 0, Spec meldet Abweichungen | ✓ VERIFIED | `basis.css` Z. 42-45 `.om-kachelraster > li { min-width: 0; margin: 0; }`; `kacheln.spec.ts` prüft den li-Außenabstand (Basislauf: `:465` ×4 bestanden). |
| Mindestspur als eine Custom Property `--om-kachel-mindestbreite` (13,25rem) | ✓ VERIFIED | `basis.css` Z. 31 und 33; Spec löst die Property im Browser auf (`kacheln.spec.ts` Z. 365-367). Die gemessene Reserve von 16,0 px nennt der Kommentar `basis.css` Z. 17-29; sie hängt an den Daten und wird protokolliert, nicht erzwungen (IN-09). Der Wert aus dem Basislauf ist im Titel nicht sichtbar, der Test besteht. |
| Sweep über alle Breiten inklusive Spaltensprüngen, Selbsttest | ✓ VERIFIED | `kacheln.spec.ts` Z. 49 `SPALTENSPRUENGE = [488, 732, 968, 1204, 1440]`, Z. 55 `BREITEN`, Z. 495-500 Selbsttest („kein Spaltensprung der Mindestspur“), Z. 67 `TOLERANZ = 0.5`. |
| Schrift der Beträge wird je Route protokolliert und gegen die Kalibrierschrift geprüft | ✓ VERIFIED | `kacheln.spec.ts` Z. 36 `KALIBRIERSCHRIFT = 'DejaVu Sans'`, Z. 471-482: jeder gemeldete Eintrag muss mit `DejaVu Sans (` beginnen, sonst bricht der Test ab. Dass `ci` im Basislauf mit 89 Tests (davon vier Kachelrouten) besteht, belegt DejaVu Sans im Lauf über `e2e-wie-ci.sh`. |
| `ci.yml`: Job `app` auf `ubuntu-24.04`, Schrift der Kalibrierung hergestellt und geprüft | ✓ VERIFIED (Quelltext) | `ci.yml` Z. 71 `runs-on: ubuntu-24.04`, Z. 98-113 Installation von `fonts-dejavu-core`, Ausgabe der Version, `fc-match`-Prüfung. Seit 28462a7 nur Kommentarzeilen geändert. Ausführung auf GitHub: Human-Item 1. |
| `e2e-wie-ci.sh`: Standardprojekt `ci`, Download mit Zeitlimit, Prüfsumme | ✓ VERIFIED | `e2e-wie-ci.sh` Z. 70 (`curl -fsSL --max-time 60 --retry 2`), Z. 74-75 (SHA-256 geprüft), Z. 89-91 (ohne `--project` wird `--project=ci` ergänzt). Das Skript lief im Basislauf fehlerfrei. |
| README zu `e2e-wie-ci.sh` | ✓ VERIFIED | `README.md` Z. 28-37. |
| G-01 bis G-03 aus 07-13 gelten weiter (`.om-zahl` ohne Umbruch, Label „Quelle“) | ✓ VERIFIED | `basis.css` Z. 11-15 (`white-space: nowrap`), `QuelleKnopf.vue` Z. 61 (Text „Quelle“, Kachel und Produktseite). |
| Scope-Zaun von 07-14 (Beträge, Daten, Schrift) | ✓ eingehalten | Kein Schriftbezug in `app/package.json` (kein Treffer für „font“); `.om-zahl` unverändert; keine Datenänderung durch 07-14. Spätere Änderungen stammen aus Review-Fixes und Phase 8 (siehe oben) und sind in den Wahrheiten 1 bis 4 neu geprüft. |
| Prohibition: Betrag nicht verkleinern, umbrechen oder abschneiden; kein Ausschluss von Route oder Breite; Toleranz bleibt 0,5 | ✓ eingehalten (Urteil, nicht autoritativ) | `.om-zahl` unverändert, `TOLERANZ = 0.5` (`kacheln.spec.ts` Z. 67), Breitenliste nur erweitert. `unverified-prohibition: Menschliche Prüfung empfohlen` |
| Backstop: grüner GitHub-Lauf und öffentliche URL zeigen den Fix | ? offen | Human-Item 1; nicht als vom Verifier erfüllt markiert. |
| Backstop: Gerätecheck der Kacheln nach der breiteren Spur | ? offen | Human-Item 2; nicht als vom Verifier erfüllt markiert. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/src/components/QuelleKnopf.vue`, `QuelleSeite.vue`, `QuelleSeitenleiste.vue` | Auslöser, Bild mit Markierung, globale Seitenleiste | ✓ VERIFIED | Substanziell, verdrahtet (`App.vue` Z. 228, Tabellen und Kacheln); Daten fließen aus `quellen.json` |
| `app/src/lib/quelle.ts`, `app/src/data/quellen.json` | Schlüsselgrammatik, Lookup, 2496 Belege | ✓ VERIFIED | `findeBeleg` mit `Map`, kein Prototype-Zugriff; 231 Seiten, 231 WebP |
| `app/src/components/DatenTabelle.vue`, `datenTabelle.ts` | Tabellenalternative mit Quelle-Spalte, benanntem Rahmen | ✓ VERIFIED | Nach Phase 8 und D-20 neu geprüft (Z. 132-142; `tabellenRahmen` Z. 78-84) |
| `app/src/styles/basis.css` | li-Reset, `--om-kachel-mindestbreite`, reduzierte Bewegung | ✓ VERIFIED | Z. 11-15, 30-45, 71-88 |
| `app/e2e/*.spec.ts` (`smoke`, `inventar`, `interaktion`, `mobil`, `kacheln`, `quelle`, `textliste`) | Browser-Tests der Phase | ✓ VERIFIED | Im Basislauf grün: `ci` 89, `mobil` 41, `texte` 1 |
| `.github/workflows/ci.yml` | Jobs `pipeline`, `app`, `deploy` | ✓ VERIFIED (Quelltext) | siehe Wahrheit 5 |
| `scripts/e2e-wie-ci.sh`, `scripts/lighthouse-a11y.sh` | CI-Schrift-Nachstellung, Lighthouse-Einmalwerkzeug | ✓ VERIFIED | Vorhanden, Review-Fixes IN-10 und CR-02 enthalten |
| `README.md` | Hinweis zu `e2e-wie-ci.sh`, Einrichtung von Pages | ✓ VERIFIED | Z. 28-55; Z. 7 siehe Anti-Patterns |
| `pipeline/08_quellenbelege.py`, `ostbevern/quellen.py`, `belegbilder.py` | Schritt 08 | ✓ VERIFIED | `alle.py` byte-identisch (Basislauf); atomares Schreiben in `belegbilder.py` Z. 79 und 177 (WR-02) |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `DatenTabelle.vue` (Spalte `quelle`) | `QuelleKnopf.vue` | `findeBeleg`, Z. 211-219 | ✓ WIRED | `quelle.spec.ts:262` öffnet die Leiste aus einer Tabellenzeile |
| `QuelleKnopf.vue` | `QuelleSeitenleiste.vue` | `oeffneQuelle` / `useQuelle` in `lib/quelle.ts` | ✓ WIRED | `quelle.spec.ts:121` |
| `QuelleSeitenleiste.vue` | `public/quellen/*.webp` | `bildUrl(beleg.bild)` in `QuelleSeite.vue` | ✓ WIRED | 231 Dateien vorhanden, Ladefehler-Pfad getestet (`quelle.spec.ts:203`) |
| `basis.css` (`--om-kachel-mindestbreite`) | `kacheln.spec.ts` | Property im Browser aufgelöst | ✓ WIRED | Z. 365-367 der Spec |
| `ci.yml` (`npm run test:e2e`) | `kacheln.spec.ts` | Projekt `ci` auf `ubuntu-24.04` | ✓ WIRED (Quelltext) | Ausführung auf GitHub: Human-Item 1 |
| `ci.yml` (`deploy`) | `app/dist` | `upload-pages-artifact` aus Job `app` | ✓ WIRED (Quelltext) | Z. 116-121 und 123-139 |

### Data-Flow Trace (Level 4)

Die Wertzeile der Seitenleiste kommt aus der Anfrage des Knopfes (formatierter Wert und Herleitung aus den Seitendaten), Bild, Seitenmaß und Rechteck aus `quellen.json` (von Schritt 08 erzeugt, im Basislauf byte-identisch reproduziert). Kachelwerte kommen unverändert aus den App-Daten; Phase 8 hat nur Berechnung und Formatierung zentralisiert (vitest 2162 grün). ✓ FLOWING.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Kein Codepfad seit dem Basislauf geändert | `git diff --quiet 1d0df35da1842daec515b40dd62f8d918e240105 HEAD -- pipeline app daten scripts .github` | Exit 0 | ✓ PASS |
| Tabellenrahmen nach D-20 | `npx vitest run src/components/__tests__/zustaende.test.ts` (eigene Scratch-Kopie von `app/`, `npm ci`) | 1 Datei, 24 bestanden | ✓ PASS |
| Belege und Belegbilder (Pipeline) | `uv run --directory pipeline pytest -p no:cacheprovider -q tests/test_quellen.py tests/test_belegbilder.py` | 74 bestanden | ✓ PASS |
| Belegabdeckung der Kacheln und Quelle-Spalten nach Phase 8 | `npx vitest run src/lib/__tests__/quelle-ui-abdeckung.test.ts` (eigene Scratch-Kopie) | 1 Datei, 7 bestanden | ✓ PASS |
| Voller Pipeline-Lauf, pytest, vitest, Build, Playwright `ci`/`mobil`/`texte` | nicht erneut gelaufen, zitiert aus `09-BASISLAUF.md` | 681 pytest, `alle.py` byte-identisch, 2162 vitest, `ci` 89, `mobil` 41, `texte` 1 | ✓ PASS (Basislauf) |

### Probe Execution

Step 7c: übersprungen, die Phase deklariert keine `probe-*.sh` (`find scripts -path '*/tests/probe-*.sh'` ohne Treffer).

### Requirements Coverage

Alle zehn Phasen-IDs stehen in den PLAN-Frontmattern (14 Pläne), `v1.0-REQUIREMENTS.md` ordnet genau diese zehn IDs Phase 7 zu; keine verwaisten IDs.

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| DATA-04 | 07-01, 07-02, 07-03, 07-06 | Quellenbelege: PDF-Zeilenrechteck und gerenderte WebP-Seite (`quellen.json`, `public/quellen/`) | ✓ SATISFIED | Wahrheit 1: 2496 Belege, 231 Seiten, `alle.py` byte-identisch (Basislauf), 74 Pipeline-Tests (eigener Lauf) |
| UI-02 | 07-01, 07-06, 07-07, 07-08, 07-09, 07-13 | „Quelle anzeigen“ öffnet an Kennzahlen und Tabellenzeilen eine Seitenleiste mit PDF-Ausschnitt | ✓ SATISFIED | Wahrheit 1: `quelle.spec.ts:121`, `:262`, `:294`, `:364` (Basislauf) |
| UI-06 | 07-05, 07-10 | Alle Texte deutsch, durchgehend Du-Anrede | ✓ SATISFIED | `duanrede.test.ts` im vitest-Lauf (2162 bestanden), Projekt `texte` bestanden (Basislauf) |
| A11Y-01 | 07-09 | Tabellenalternative zu jedem Diagramm | ✓ SATISFIED | `inventar.spec.ts:39` auf elf Routen, Rahmen-Tests `mobil.spec.ts:181`; `zustaende.test.ts` 24 bestanden (eigener Lauf) |
| A11Y-02 | 07-01, 07-09, 07-11 | Fokussteuerung, Kontraste, `prefers-reduced-motion` | ✓ SATISFIED | `router/index.ts` Z. 128-148; `interaktion.spec.ts:278`, `:393-:419`; axe `smoke.spec.ts:185` (Basislauf) |
| A11Y-03 | 07-09, 07-12, 07-13, 07-14 | Alle Seiten ab 360 px nutzbar | ✓ SATISFIED (Quellstand und Tests) | `mobil.spec.ts:151`, `:181`; `kacheln.spec.ts:465` (Basislauf). Gerätecheck (Human-Item 2): vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft |
| A11Y-04 | 07-04, 07-12 | Lighthouse-Barrierefreiheit ≥ 95 auf allen Routen | ✓ SATISFIED (indirekt) | Wahrheit 3: Messung 100 vom 2026-10-07, heute axe grün auf elf Routen; Lighthouse nicht neu gemessen (`advisory`) |
| QUAL-02 | 07-04, 07-11, 07-14 | Playwright-Smoke-Test: jede Route ohne Konsolenfehler, Diagramme mit Daten | ✓ SATISFIED | `smoke.spec.ts:138` auf elf Routen, `ci` 89 bestanden (Basislauf) |
| DEPL-01 | 07-11, 07-14 | GitHub Actions baut und deployt auf GitHub Pages | ✓ SATISFIED (Quelltext vom Verifier; Lauf vom Nutzer bestätigt, 2026-10-08) | Workflow im Quelltext korrekt (`ci.yml` Z. 64-139, vom Verifier geprüft); grüner Lauf samt Deploy: vom Nutzer bestätigt, nicht vom Verifier geprüft (Human-Item 1, D-14) |
| DEPL-02 | 07-05, 07-12, 07-14 | App unter öffentlicher URL erreichbar | ✓ SATISFIED (Quelltext vom Verifier; Erreichbarkeit vom Nutzer bestätigt, 2026-10-08) | `base: './'`, Hash-Router, README Z. 39-55 (vom Verifier geprüft); öffentliche URL erreichbar: vom Nutzer bestätigt, nicht vom Verifier geprüft (Human-Item 1, D-14) |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `README.md` | 7 | „Online geht die App, sobald das Repository auf GitHub angelegt und `main` gepusht ist“ | ℹ️ Info | Veraltet, der Nutzer hat Repository, Push und Deploy erledigt; kein Zielverstoß |
| `app/e2e/kacheln.spec.ts` | 465-535 | Reserve von 16,0 px hängt an den Daten und wird nur protokolliert | ℹ️ Info | Bewusst (IN-09), Prüfpunkt beim Jahrgangswechsel steht im Kommentar `basis.css` Z. 22-29 |

Behoben seit dem alten Bericht: CR-02 (`lighthouse-a11y.sh` löscht nur noch ein frisches Unterverzeichnis, Z. 36-48), WR-05 `berechnet: false` bei gesetzter `herleitung` (laut `07-REVIEW-DISPOSITION.md` fixed), WR-01 bis WR-03 der Pipeline (fixed), veralteter Kopfkommentar „noch kein GitHub-Remote“ in `ci.yml` (28462a7), Prettier-Abdeckung von `e2e/` (`package.json` `format:check` prüft `src/ e2e/`). Kein `TBD`, `FIXME` oder `XXX` in den geprüften Dateien (der einzige Treffer ist die `mktemp`-Vorlage `lighthouse-a11y.XXXXXX`).

### Human Verification Required

1. **Push, grüner GitHub-Lauf und öffentliche URL**
   **Test:** `main` pushen; im Reiter Actions müssen `app`, `pipeline` und `deploy` grün sein. Im Log des Jobs `app` stehen vier Zeilen „Schrift der Beträge auf …: DejaVu Sans“. Dann die öffentliche URL prüfen: keine 404, Reload von `/#/ausgaben` und `/#/ueber`, Quelle-Leiste mit Bild, Kontakt-Adresse in der Fußzeile, PDF-Link, Kacheln in der grauen Fläche.
   **Expected:** Grüner Lauf samt Deploy; die Seite zeigt den Fix.
   **Why human:** Push gehört dem Nutzer (D-10), Firewall blockiert github.io; ob der Runner dieselbe Schrift wie die Nachstellung rendert, belegt erst ein grüner Lauf.
   **Beleg:** vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft

2. **Gerätecheck der Kacheln**
   **Test:** Startseite, `/investitionen`, `/rat-entscheidet`, `/stellenplan` bei 360, 400, 600, 768 und 1280 px auf dem eigenen Gerät.
   **Expected:** Beträge und Knopf „Quelle“ innerhalb der Kachel, bündig mit der Überschrift, kein waagerechtes Scrollen.
   **Why human:** Geräteschriften weichen von DejaVu Sans ab; die frühere UAT-Bestätigung galt dem Stand vor 07-14.
   **Beleg:** vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft

### Nutzerbestätigung (D-14)

Der Nutzer hat am 2026-10-08 erklärt, dass er beide Prüfungen selbst erledigt hat: den grünen GitHub-Actions-Lauf samt Deploy auf GitHub Pages mit der öffentlichen URL (Human-Item 1, ROADMAP-Kriterium 5) und den Gerätecheck der Kacheln bei 360 bis 1280 px (Human-Item 2). Beide Items bleiben in diesem Bericht stehen, jedes trägt den `beleg` „vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft“. Der Verifier hat sie nicht geprüft und kann es auch nicht: Die Sandbox erreicht weder github.io noch die Actions-API, und ein Gerätecheck braucht ein echtes Gerät. Sie zählen deshalb nicht zu den vier vom Verifier geprüften Kriterien (siehe Score). Mit der Bestätigung ist der frühere Widerspruch aufgelöst (Frontmatter `passed`, Text `human_needed`): Frontmatter und Text sagen jetzt beide `passed`. ROADMAP Phase 9, Kriterium 3, bleibt gewahrt: Die Items stehen als Aufgabe des Nutzers im Bericht und gelten nicht als vom Verifier bestanden. Ergänzend steht in `07-UAT.md` für beide Tests „pass“ (2026-10-07, vor den Review-Fixes und Phase 8); das ersetzt die Bestätigung vom 2026-10-08 für den Endstand nicht.

### Live-Evidenz

Alle vollständigen Läufe stammen aus `09-BASISLAUF.md` (Kopf `1d0df35da1842daec515b40dd62f8d918e240105`, erstellt 2026-10-09T06:24:00Z): `pytest` 681 bestanden ohne Skip, `alle.py --jahr 2026` byte-identisch mit den zehn Prüfregeln grün, vitest 2162 Tests in 49 Dateien, `type-check`, `lint`, `format:check` und `build` grün, Playwright `ci` 89, `mobil` 41, `texte` 1 bestanden (Image `mcr.microsoft.com/playwright:v1.63.0-noble` mit DejaVu Sans über `scripts/e2e-wie-ci.sh`). Dieser Plan hat weder `alle.py` noch die volle pytest-Suite noch Playwright gestartet; seit dem Basislauf-Kopf hat sich kein Codepfad geändert (`git diff --quiet`, Exit 0). Eigene Prüfungen: die beiden Läufe im Abschnitt „Behavioral Spot-Checks“, Quelltextlesungen mit Zeilenangaben, `git log` und `git show` über die Phase-7-Dateien.

### Gaps Summary

Keine offenen Lücken im Quellstand. Die Wahrheiten 1 bis 4 gelten auf dem Endstand nach Phase 8 und dem D-20-Fix; die Phase-8-Änderungen an `DatenTabelle`, Drawer und Kennzahllogik haben keine Phase-7-Wahrheit gebrochen (`regressions: []`); die zeitweise Lücke im Tabellenrahmen (98803c4) ist durch 78744d4 geschlossen. Kriterium 5 (Deploy, öffentliche URL) und der Gerätecheck konnte nur der Nutzer prüfen; er hat beides am 2026-10-08 bestätigt (D-14), der Verifier hat es nicht geprüft. Der Status ist deshalb `passed` und sagt im Frontmatter wie im Text dasselbe. Kriterium 3 ist indirekt belegt (Lighthouse nicht neu gemessen, `advisory`). CR-01 (Unterschriften auf `s009.webp`) bleibt als `deferred` mit Verweis auf die Nutzerentscheidung vom 2026-10-07 stehen und ist weder Lücke noch Regression (D-22).

---

_Verified: 2026-10-09T06:36:00Z_
_Verifier: Claude (gsd-verifier-Verfahren, ausgeführt in Plan 09-10)_
