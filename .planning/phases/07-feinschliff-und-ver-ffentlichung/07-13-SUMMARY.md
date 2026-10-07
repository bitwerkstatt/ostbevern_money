---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 13
subsystem: ui
tags: [vue, css-grid, playwright, a11y, kennzahl-kachel, quelle-knopf]
gap_closure: true
gap_ids: [A11Y-03-kachel-ueberlauf, UI-REVIEW-BLOCKER-1, UI-REVIEW-WARNING-2]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: "QuelleKnopf, KennzahlKachel, Playwright-Projekte ci/mobil/texte (07-01 bis 07-12)"
provides:
  - "Breitentest app/e2e/kacheln.spec.ts im Projekt ci (4 Kachelrouten x 10 Breiten, geschlossene Routenliste)"
  - "gemeinsames Kachelraster .om-kachelraster (13rem Mindestspur) auf Start, Investitionen, Stellenplan, Rat entscheidet"
  - "Kachelbetrag in Größe l bei jeder Breite, Knopf „Quelle“ mit unverändertem zugänglichem Namen"
  - "07-UI-SPEC.md Nachtrag 2026-10-07 mit fünf datierten Änderungsmarken"
affects: [07-verification, phase-07-abnahme, a11y-03]

actuals:
  tokens: 9900
  tasks: 3
  commits: 3
plan_head_before: dbc67fee048835755000b2b9e67fb7ae3aa256d8
plan_head_after: 94fe70fbd082286a4d82858838a446244c099f6a

tech-stack:
  added: []
  patterns:
    - "Eine gemeinsame Rasterklasse om-kachelraster statt vier seitenlokaler Raster"
    - "Breitentest misst Inhaltsbereich der Kachel (Innenabstand) statt Rahmen, mit 0,5 px Toleranz und gesammelten Befunden"
    - "Klassifikationstest hält die Liste der Kachelrouten geschlossen"

key-files:
  created:
    - app/e2e/kacheln.spec.ts
  modified:
    - app/src/styles/basis.css
    - app/src/pages/StartPage.vue
    - app/src/pages/InvestitionenPage.vue
    - app/src/pages/StellenplanPage.vue
    - app/src/components/NichtBeeinflussbarBlock.vue
    - app/src/components/KennzahlKachel.vue
    - app/src/components/QuelleKnopf.vue
    - app/src/lib/__tests__/quelle.test.ts
    - .planning/phases/07-feinschliff-und-ver-ffentlichung/07-UI-SPEC.md

key-decisions:
  - "G-01: Betrag bricht nie um und wird nie abgeschnitten, .om-zahl behält white-space: nowrap"
  - "G-02: Kachelbetrag bleibt bei jeder Breite --wa-font-size-l, keine Display-Regel, keine fließende Größe"
  - "G-03: sichtbarer Text „Quelle“ (Kachel, Produkt), zugänglicher Name „Quelle anzeigen: {Bezeichnung}, PDF-Seite {n}“ unverändert"
  - "G-04: Mindestspur 13rem (kleinster getesteter Wert mit mindestens 16 px gemessener Reserve)"
  - "G-05: Breitentest im Projekt ci, damit GitHub Actions die Regression fängt"

patterns-established:
  - "Kachellisten tragen ausschließlich die Klasse om-kachelraster, kein .vue hat ein eigenes Kachelraster"
  - "Jede neue Route mit .om-kennzahl muss in KACHEL_ROUTEN stehen, sonst scheitert der Klassifikationstest"

requirements-completed: [A11Y-03, UI-02]

duration: 13min
completed: 2026-10-07
status: complete

coverage:
  - id: D1
    description: "Auf allen vier Kachelrouten liegen Betrag und Knopf bei 360 bis 1440 px im Inhaltsbereich der Kachel, kein seitliches Scrollen der Seite"
    requirement: "A11Y-03"
    verification:
      - kind: e2e
        ref: "app/e2e/kacheln.spec.ts#Kacheln und Seitenbreite: / (und /investitionen, /rat-entscheidet, /stellenplan)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Betrag steht in einer Zeile, ist nicht abgeschnitten und hat bei jeder Breite die Größe --wa-font-size-l"
    requirement: "A11Y-03"
    verification:
      - kind: e2e
        ref: "app/e2e/kacheln.spec.ts#Kacheln und Seitenbreite (getClientRects, overflow-x, computed font-size)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Knopf zeigt „Quelle“ (kachel, produkt), zugänglicher Name unverändert, Knopf mindestens 44 x 44 px"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle.test.ts#QuelleKnopf zeigt in der Variante kachel/produkt den Text „Quelle“"
        status: pass
      - kind: e2e
        ref: "app/e2e/kacheln.spec.ts#Kacheln und Seitenbreite (innerText, aria-label, Mindestmaß)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Alle vier Kachellisten nutzen die gemeinsame Klasse om-kachelraster; die Routenliste ist durch einen Klassifikationstest geschlossen"
    requirement: "A11Y-03"
    verification:
      - kind: e2e
        ref: "app/e2e/kacheln.spec.ts#Kachelrouten: genau diese Routen zeigen Kennzahl-Kacheln"
        status: pass
    human_judgment: false
  - id: D5
    description: "07-UI-SPEC.md dokumentiert Label, Betragsgröße und Kachelraster mit datierten Änderungsmarken und Nachtrag"
    verification: []
    human_judgment: true
    rationale: "Vertragstext: ob die Formulierung die Nutzerentscheidungen G-01 bis G-05 trifft, beurteilt ein Mensch"
  - id: D6
    description: "Auf dem eigenen Gerät und Browser bleiben Beträge und Knöpfe bei 360, 400, 600, 768 und 1280 px in der Kachel (07-VERIFICATION human_verification Punkt 2)"
    verification: []
    human_judgment: true
    rationale: "Schriften auf dem Gerät weichen vom Docker-Testbild ab; die Geräteprüfung bleibt Sache des Nutzers und ist hier nicht verifiziert"
---

# Phase 7 Plan 13: Kennzahl-Kacheln über alle Breiten Summary

**Gemeinsames Kachelraster `om-kachelraster` (13rem Mindestspur, gemessen), Kachelbetrag in Größe l bei jeder Breite und Knopf „Quelle“ schließen die Lücke A11Y-03; ein Playwright-Breitentest im Projekt `ci` hält das Ergebnis in GitHub Actions fest.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-10-07T07:07:35Z
- **Completed:** 2026-10-07T07:20:00Z
- **Tasks:** 3
- **Files modified:** 10 (1 neu, 9 geändert)

## Accomplishments

- Die Kachel-Überläufe aus `07-VERIFICATION.md` sind behoben: Beträge und Knopf liegen auf `/`, `/investitionen`, `/rat-entscheidet` und `/stellenplan` bei 360, 400, 480, 560, 600, 700, 768, 1024, 1280 und 1440 px im Inhaltsbereich der Kachel, ohne seitliches Scrollen der Seite.
- Der Betrag bleibt vollständig, einzeilig und in Heading-Größe (`--wa-font-size-l`), die Display-Regel ab 700 px ist entfernt. Der Platz kommt allein aus dem Raster.
- Der Knopf heißt sichtbar „Quelle“ (Kachel, Produktseite), der zugängliche Name bleibt „Quelle anzeigen: {Bezeichnung}, PDF-Seite {n}“; alle bestehenden `getByRole`-Locatoren laufen unverändert.
- `kacheln.spec.ts` läuft im Projekt `ci` (96 Tests in `ci`, `mobil` und `texte` grün) und hält die Liste der Kachelrouten durch einen Klassifikationstest geschlossen.
- `07-UI-SPEC.md` trägt den Nachtrag 2026-10-07 mit fünf datierten Änderungsmarken.

## Task Commits

1. **Task 1: Tracer, Startseite** - `771b795` (fix): Breitentest rot, dann Raster, Größe l, Knopf „Quelle“ grün
2. **Task 2: alle Kachelseiten, Kalibrierung** - `c899020` (fix): drei weitere Listen auf `om-kachelraster`, Mindestspur gemessen
3. **Task 3: UI-SPEC-Nachtrag und Abschluss-Gate** - `94fe70f` (docs)

**Plan metadata:** folgt als `docs(07-13): complete ...`-Commit (nur diese SUMMARY, kein STATE/ROADMAP/REQUIREMENTS).

## Rote Ausgangsmessung (vor dem Fix)

Lauf von `e2e/kacheln.spec.ts` (nur Startseite, Spec nur mit KACHEL_ROUTEN `start`) gegen den unveränderten Produktionsbuild im Playwright-Image (`--project=ci`): **1 failed**, Test „Kacheln und Seitenbreite: /“. Der Lauf nennt 834 Befundzeilen (Befund je Kachel, Breite und Regel). Tabelle der Messung (Spalten: Route, Breite, Kacheln, Spalten, breitester Betrag, Betragbreite, engste Innenbreite, Reserve, scrollWidth):

| Route | Breite | Kacheln | Spalten | breitester Betrag | Betragbreite | engste Innenbreite | Reserve | scrollWidth |
|-------|-------:|--------:|--------:|-------------------|-------------:|-------------------:|--------:|------------:|
| / | 360 | 7 | 1 | -2,35 Mio. € | 117.9 | 262.0 | 144.1 | 360 |
| / | 400 | 7 | 2 | -2,35 Mio. € | 117.9 | 118.0 | 0.1 | 400 |
| / | 480 | 7 | 2 | -2,35 Mio. € | 117.9 | 158.0 | 40.1 | 480 |
| / | 560 | 7 | 3 | -2,35 Mio. € | 117.9 | 110.0 | -7.9 | 560 |
| / | 600 | 7 | 3 | -2,35 Mio. € | 117.9 | 123.3 | 5.4 | 600 |
| / | 700 | 7 | 3 | -2,35 Mio. € | 188.7 | 151.3 | -37.3 | 700 |
| / | 768 | 7 | 4 | -2,35 Mio. € | 188.7 | 112.0 | -76.7 | **795** |
| / | 1024 | 7 | 5 | -2,35 Mio. € | 188.7 | 126.0 | -62.7 | 1024 |
| / | 1280 | 7 | 6 | -2,35 Mio. € | 188.7 | 135.3 | -53.3 | 1280 |
| / | 1440 | 7 | 7 | -2,35 Mio. € | 188.7 | 128.3 | -60.4 | 1440 |

Befunde der roten Messung, die zu `07-VERIFICATION` passen:

- **Knopf außerhalb des Inhaltsbereichs** der Kachel bei 400 px (28,5 px), 560 px (36,5 px), 600 px (23,2 px) und weiteren Breiten (gemessen gegen den Inhaltsbereich; `07-VERIFICATION` maß 7 bis 21 px gegen den Kachelrand). Beispiel: `/ @ 400 px: „Erträge“: Quelle-Knopf liegt bei 58.0 bis 204.5 px, Inhaltsbereich 58.0 bis 176.0 px`.
- **Betrag außerhalb** ab 560 px (7,9 px) und ab 700 px bis 76,7 px bei 768 px. Beispiel: `/ @ 700 px: „Erträge“: Betrag „27,5 Mio. €“ ragt 27.7 px über den Inhaltsbereich (Betrag 179.1 px, Inhalt 151.3 px)`.
- **Betragsgröße 32 px statt 20 px** ab 700 px (Display-Regel): `/ @ 700 px: „Erträge“: Betragsgröße 32px, erwartet 20px (--wa-font-size-l)`.
- **Seitenscroll bei 768 px:** `/ @ 768 px: Seite scrollt waagerecht (scrollWidth 795 > innerWidth 768): span.om-zahl reicht bis 795.1 px`.
- **Kein gemeinsames Raster:** `Kachel steht in keinem .om-kachelraster` und `Quelle-Knopf zeigt „Quelle anzeigen“, erwartet „Quelle“` bei jeder Breite.

## Zwischenmessung der drei übrigen Kachelrouten (vor dem Wechsel auf das gemeinsame Raster)

Lauf der erweiterten Spec mit den lokalen 160-px-Rastern, aber den globalen Änderungen aus Task 1 (Größe l, Knopf „Quelle“):

| Route | Ergebnis | Befunde (Auszug) |
|-------|----------|------------------|
| `/investitionen` | rot | 29 x „Kachel steht in keinem .om-kachelraster“; bei 560 px zwei Beträge 1,9 px über dem Inhaltsbereich („7,71 Mio. €“, „11,6 Mio. €“) |
| `/rat-entscheidet` | rot | 39 x „keinem .om-kachelraster“; Beträge bis 31,1 px über dem Inhaltsbereich (400 px: 23,1; 560 px: 31,1; 600 px: 17,8; 768 px: 29,1), `Kachel scrollWidth 149 > clientWidth 144` |
| `/stellenplan` | rot | 29 x „keinem .om-kachelraster“; Seitenscroll bei 700 px (878) und 768 px (912), Ursache siehe Abweichung 1 |
| Klassifikationstest | grün | genau die vier Routen: `/` 7, `/investitionen` 3, `/rat-entscheidet` 4, `/stellenplan` 3 Kacheln, alle anderen Routen 0 |

## Kalibrierung der Mindestspur X (G-04)

Je Kandidat in einer Scratch-Kopie in `basis.css` gesetzt, `build-only`, dann `kacheln.spec.ts` im Playwright-Image (nach der Korrektur der Wartelogik, Abweichung 1). Reserve = kleinster Abstand zwischen rechter Betragskante und rechter Inhaltskante über alle Routen und Breiten.

| X | Ergebnis | kleinste Reserve | wo |
|---|----------|-----------------:|----|
| 10rem (160 px, bisher) | fail (`/`, `/investitionen`, `/rat-entscheidet`) | -31,1 px | `/rat-entscheidet` @ 560 px |
| 11rem | pass | 8,1 px | `/` @ 1024 px |
| 12rem | pass | 10,3 px | `/rat-entscheidet` @ 700 px |
| **13rem** | **pass** | **16,9 px** | `/rat-entscheidet` @ 480 px |

Gewählt: **13rem**, der kleinste Wert mit mindestens 16 px Reserve (eine `--wa-space-m`). Die Reserve bleibt bei 13rem auf allen vier Routen und allen zehn Breiten mindestens 16,9 px.

## Lesbarkeit je Kachelroute am engsten mehrspaltigen Raster (G-06)

Engste Breite mit mindestens zwei Spalten ist auf allen vier Routen **480 px** (2 Spalten, Inhaltsbreite der Kachel 158,0 px). Der Betrag passt jeweils:

| Route | Kacheln | Spalten | breitester Betrag | Betragbreite | Inhaltsbreite Kachel | Reserve | passt |
|-------|--------:|--------:|-------------------|-------------:|---------------------:|--------:|:-----:|
| `/` | 7 | 2 | -2,35 Mio. € | 117,9 px | 158,0 px | 40,1 px | ja |
| `/investitionen` | 3 | 2 | 7,71 Mio. € | 111,9 px | 158,0 px | 46,1 px | ja |
| `/rat-entscheidet` | 4 | 2 | rd. 10,1 Mio. € | 141,1 px | 158,0 px | 16,9 px | ja |
| `/stellenplan` | 3 | 2 | 62,91 VZÄ | 93,1 px | 158,0 px | 64,9 px | ja |

Der schmalste Fall insgesamt ist „rd. 10,1 Mio. €“ auf `/rat-entscheidet` mit 16,9 px Reserve. Bei 360 px haben alle vier Raster genau eine Spalte (Inhaltsbreite 262 px, Reserve mindestens 120,9 px). Die Messung stammt aus dem Playwright-Image (System-Sans-Schrift); auf dem Gerät des Nutzers weicht die Schrift ab, deshalb gilt die 16-px-Reserve als Auswahlregel und die Geräteprüfung bleibt offen.

## Files Created/Modified

- `app/e2e/kacheln.spec.ts` - Breitentest (10 Breiten, 4 Kachelrouten), Klassifikationstest, Tabellenausgabe je Route und Breite
- `app/src/styles/basis.css` - `.om-kachelraster` (Raster, `li { min-width: 0 }`, Abstand l ab 700 px); `.om-zahl` unverändert
- `app/src/pages/StartPage.vue`, `InvestitionenPage.vue`, `StellenplanPage.vue`, `app/src/components/NichtBeeinflussbarBlock.vue` - Liste auf `om-kachelraster`, lokale Raster und Medienblöcke entfernt
- `app/src/components/KennzahlKachel.vue` - Display-Regel ab 700 px entfernt, Prop-Kommentar angepasst
- `app/src/components/QuelleKnopf.vue` - sichtbarer Text „Quelle“ (kachel, produkt), Kommentare angepasst; `zugaenglicherName` unverändert
- `app/src/lib/__tests__/quelle.test.ts` - Kachel-Test auf „Quelle“, neuer Test für `produkt`, Negativ-Assertion im Unbekannt-Test
- `.planning/phases/07-feinschliff-und-ver-ffentlichung/07-UI-SPEC.md` - fünf datierte Änderungsmarken und Nachtrag 2026-10-07

## Decisions Made

Die Entscheidungen G-01 bis G-06 stammen vom Nutzer und sind im Plan festgeschrieben. Eigene Entscheidung dieses Laufs: `X = 13rem`, weil nur dieser Kandidat die Auswahlregel (Reserve mindestens 16 px) erfüllt (Tabelle oben).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Breitentest meldete nachziehende Diagramme als Seitenüberlauf**
- **Found during:** Task 2 (Zwischenmessung und erste Kalibrierung)
- **Issue:** Auf `/stellenplan` meldete die Spec bei 700 px (scrollWidth 878) und 768 px (912) einen Seitenüberlauf. Ursache war kein Kachelfehler: Beim Wechsel auf das zweispaltige Layout ab 700 px stand die Leinwand eines Diagramms kurz noch in der alten Breite (520 px in einer Spalte von 302 px; ECharts zieht verzögert nach). Die Annahme des Plans, Diagramme zögen „nie breiter“ nach, trifft an diesem Umbruch nicht zu. Nach dem Nachziehen scrollt die Seite nicht (mit Wartezeit gemessen, kein Überlauf bei 700 und 768 px).
- **Fix:** `warteAufLayout` wartet nach den zwei Animationsframes, bis `documentElement.scrollWidth <= window.innerWidth`, höchstens 2 s. Ein dauerhafter Überlauf bleibt nach Ablauf bestehen und wird gemeldet; Toleranz, Routen und Breiten sind unverändert. Der Plan-Hinweis zu den aufsteigenden Breiten bleibt, reicht aber allein nicht.
- **Files modified:** `app/e2e/kacheln.spec.ts`
- **Verification:** `/stellenplan` bestanden, die roten Läufe (Kandidat 10rem) bleiben rot
- **Committed in:** `c899020`

**2. [Rule 1 - Bug] Abnahmekriterium mit regulärem Ausdruck passt nicht auf `${`**
- **Found during:** Task 1 (acceptance_criteria)
- **Issue:** `grep -q 'Quelle anzeigen: ${props.bezeichnung}, PDF-Seite' QuelleKnopf.vue` (einfaches grep, Basis-Regex) liefert Exit 1, obwohl die Zeile vorhanden ist (`${` ist im Regex kein Literal).
- **Fix:** Kein Codefehler. Dasselbe Muster mit `grep -F` liefert Exit 0; `zugaenglicherName` ist byte-identisch zur Vorversion.
- **Files modified:** keine

---

**Total deviations:** 2 (beide Rule 1, keine Auswirkung auf Produktionscode)
**Impact on plan:** Die Spec ist robuster gegen verzögerte Diagramme; Umfang, Routen, Breiten, Toleranz und Entscheidungen G-01 bis G-06 blieben unverändert.

Hinweis (kein Fehler): `/investitionen` hat durch die gemeinsame Klasse jetzt ab 700 px den Abstand l (vorher überall m), wie im Plan vorgesehen und in `07-UI-SPEC.md` (G-04) dokumentiert.

## Issues Encountered

- Docker legt `test-results` als root an; frische Scratch-Kopien wurden über einen `rm -rf` im Container aufgeräumt. Der npm-Registry-Zugriff funktionierte (`npm ci` aus dem Lockfile, 283 Pakete, jedes Mal in der Scratch-Kopie, nie in `app/`).
- Einmal fehlte im Befehlsblock der Sandbox ein Wrapper-Skript mit Variablen im Befehlsnamen; die Läufe liefen danach über Skripte mit festen Pfaden.

## Abschluss-Gate (CI-identisch, app-Job)

Frische Scratch-Kopie (`tar --exclude=app/node_modules --exclude=app/dist`), `npm ci` aus dem Lockfile:

| Schritt | Ergebnis |
|---------|----------|
| `type-check` (vue-tsc) | grün |
| `lint` (eslint) | grün |
| `format:check` | grün |
| `test` (vitest) | 45 Testdateien, **1968 Tests** bestanden |
| `build` | grün |
| Playwright `--project=ci --project=mobil --project=texte` | **96 passed** (ci 81, mobil 14, texte 1), `textliste.md` vorhanden (83.943 Bytes) |
| `--list`: Projekt `ci` | 4 Tests „Kacheln und Seitenbreite: /“, `kacheln.spec.ts` in `mobil` und `texte` nicht gelistet |

**Pipeline-Job übersprungen.** Grund: Außerhalb von `app/` und `.planning/` hat sich nichts geändert; `git diff --quiet a02a28c -- pipeline daten app/src/data app/src/charts/format.ts discussion/SPEZIFIKATION.md .planning/phases/07-feinschliff-und-ver-ffentlichung/07-REVIEW-DISPOSITION.md` liefert Exit 0, und `git status --porcelain --untracked-files=all -- pipeline daten app/src/data` ist leer. `REQUIREMENTS.md` ist ebenfalls unverändert gegenüber `a02a28c`.

**Reste der Beschriftung „Quelle anzeigen“** (`git grep -n "Quelle anzeigen" -- app`): nur der `aria-label`-Ausdruck und sein Kommentar in `QuelleKnopf.vue`, die `getByRole`-Locatoren und Kommentare in `app/e2e` (`interaktion`, `mobil`, `quelle`, `textliste`), die Muster-Prüfung und der Kommentar in `kacheln.spec.ts`, die synthetische Vorlage in `duanrede.test.ts`, `aria-label`-Assertions und Testnamen in `quelle.test.ts` sowie Funktionskommentare in `schulden.ts`, `StellenplanPage.vue` und `quelle-abdeckung.test.ts`. Kein sichtbarer Text „Quelle anzeigen“ in einer Vorlage.

## Offener Mensch-Check

`07-VERIFICATION.md` `human_verification` Punkt 2 bleibt **offen und ist hier nicht verifiziert**: Auf dem eigenen Gerät und Browser Startseite bei 360, 400, 600, 768 und 1280 px (einmal auch `/investitionen`, `/rat-entscheidet`, `/stellenplan`) öffnen. Jeder Betrag und jeder Knopf „Quelle“ muss in seiner grauen Kachel bleiben, Beträge bleiben einzeilig, die Seite scrollt nie seitwärts.

## Außerhalb des Umfangs (Scope-Zaun)

CR-02, WR-01 bis WR-05 und IN-01 bis IN-08 aus `07-REVIEW-DISPOSITION.md` bleiben offen und unberührt; die Datei ist gegenüber `a02a28c` unverändert. `REQUIREMENTS.md` und `discussion/SPEZIFIKATION.md` wurden nicht bearbeitet. Kein Eingriff in `pipeline/`, `daten/`, `app/src/data/` oder `app/src/charts/format.ts`. Keine neue Abhängigkeit.

## Known Stubs

Keine.

## Threat Flags

Keine neue Angriffsfläche (nur CSS, ein sichtbares Label und ein Testartefakt). T-07-30 und T-07-31 sind wie im Plan mitigiert: Test im Projekt `ci`, geschlossene Routenliste, rote Ausgangsmessung dokumentiert, keine Änderung an Daten und Formatierung.

## Next Phase Readiness

- Die Lücke aus `07-VERIFICATION.md` („Alle Seiten sind ab 360 px Breite nutzbar“) ist per Code und CI-Test geschlossen; `07-UI-REVIEW` BLOCKER 1 und WARNING 2 lösen sich mit derselben Änderung.
- Offen: die Geräteprüfung durch den Nutzer (siehe oben); Anpassung der Requirement-Status (A11Y-03, UI-02) liegt beim Verifikations-Workflow, nicht bei diesem Plan.

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-07*

## Self-Check: PASSED

- Dateien vorhanden: `app/e2e/kacheln.spec.ts`, `app/src/styles/basis.css`, `.planning/phases/07-feinschliff-und-ver-ffentlichung/07-UI-SPEC.md`
- Commits vorhanden: `771b795`, `c899020`, `94fe70f`
