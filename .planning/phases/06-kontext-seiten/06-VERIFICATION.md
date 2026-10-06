---
phase: 06-kontext-seiten
verified: 2026-10-06T11:05:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - .planning/phases/06-kontext-seiten/06-01-PLAN.md
  - .planning/phases/06-kontext-seiten/06-01-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-02-PLAN.md
  - .planning/phases/06-kontext-seiten/06-02-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-03-PLAN.md
  - .planning/phases/06-kontext-seiten/06-03-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-04-PLAN.md
  - .planning/phases/06-kontext-seiten/06-04-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-05-PLAN.md
  - .planning/phases/06-kontext-seiten/06-05-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-06-PLAN.md
  - .planning/phases/06-kontext-seiten/06-06-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-07-PLAN.md
  - .planning/phases/06-kontext-seiten/06-07-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-08-PLAN.md
  - .planning/phases/06-kontext-seiten/06-08-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-09-PLAN.md
  - .planning/phases/06-kontext-seiten/06-09-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-10-PLAN.md
  - .planning/phases/06-kontext-seiten/06-10-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-11-PLAN.md
  - .planning/phases/06-kontext-seiten/06-11-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-12-PLAN.md
  - .planning/phases/06-kontext-seiten/06-12-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-13-PLAN.md
  - .planning/phases/06-kontext-seiten/06-13-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-14-PLAN.md
  - .planning/phases/06-kontext-seiten/06-14-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-15-PLAN.md
  - .planning/phases/06-kontext-seiten/06-15-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-16-PLAN.md
  - .planning/phases/06-kontext-seiten/06-16-SUMMARY.md
  - .planning/phases/06-kontext-seiten/06-17-PLAN.md
  - .planning/phases/06-kontext-seiten/06-17-SUMMARY.md
  - app/src/charts/format.ts
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MenueGruppe.vue
  - app/src/components/NichtBeeinflussbarBlock.vue
  - app/src/components/UeberschussListe.vue
  - app/src/components/ZuschussListe.vue
  - app/src/lib/__tests__/stiltokens.test.ts
  - app/src/lib/bindungsgrad.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/menueVersatz.ts
  - app/src/lib/ruecklagen.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/RatEntscheidetPage.vue
  - app/src/pages/StellenplanPage.vue
covered_digest: "v2:sha256:708e667872cf574d1cd530f6248867adc5f2769b37d5f4b906d1decd1e395b40"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/5
  gaps_closed: []
  gaps_remaining: []
  regressions: []
  human_items_resolved:
    - "Rücklagen-Fußnote (WR-01 Vorzeichenwortlaut): UAT Test 1 pass, Beträge-Lesart akzeptiert"
    - "End-of-Phase-Walkthrough 1280/360 px: UAT Test 2 pass"
    - "Menü 'Mehr wissen' (erneutes Öffnen, Resize, Escape, Fokus): UAT Test 3 pass; schließt das frühere behavior_unverified-Item"
---

# Phase 6: Kontext-Seiten Verification Report

**Phase Goal:** Die App ordnet den Haushalt ein: Entwicklung bis 2029, Investitionen und Schulden, Gestaltungsspielraum des Rats, Personal und was außerhalb des Kernhaushalts liegt.
**Verified:** 2026-10-06
**Status:** passed
**Re-verification:** Ja. Der Vorbericht (human_needed, 5/5) wurde durch die Quick-Task 261006-f1w (Commits 3ad3244, 0098673, ff7cff6) veraltet. Die offenen Human-Items sind inzwischen in `06-UAT.md` abgeschlossen (3/3 pass, Commit 3fb71f0).

## Was sich seit dem letzten Bericht geändert hat

Geprüft gegen den Code, nicht gegen die SUMMARY:

- `git show 0098673`: genau sechs Zeilen geändert, `--wa-font-size-xl` auf `--wa-font-size-l` in den h2-Regeln von `EntwicklungPage.vue`, `InvestitionenPage.vue`, `RatEntscheidetPage.vue`, `ZuschussListe.vue`, `UeberschussListe.vue`, `NichtBeeinflussbarBlock.vue`. Es ist eine reine Stiländerung, die keine Logik, Daten oder Texte berührt.
- `grep` auf `font-size-xl` und `font-weight-semibold` in allen sieben Phase-6-Seiten und -Komponenten: keine Treffer. `--wa-font-size-l` steht in den h2-Regeln (Rat Z. 103, Investitionen Z. 183/200, Entwicklung Z. 227).
- `app/src/lib/__tests__/stiltokens.test.ts` enthält den Guard (Fail-first-Fälle, Glob-Abdeckung, `it.each` über die sechs Dateien). Er läuft grün.
- `git diff d1b8e64..HEAD -- pipeline daten app/src/data` ist leer: Pipeline und Daten sind seit der Erstverifikation unverändert.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | `/entwicklung`: Erträge, Aufwendungen, Jahresergebnis 2024-2029 mit unterscheidbarem Ist/Ansatz/Planung (Defizit 2029 -3,56 Mio.), Zeitreihen Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal, Zinsen, Rücklagen mit Angabe, wie lange das Polster reicht | VERIFIED | Unverändert gegenüber dem Vorbericht (Regression: Testsuite grün, Daten unverändert; Rückgang 1,77 / 4,23 / 4,73 / 10,04 % = PDF S. 23, Abbau 2029 = 3.557.700). Fußnote nennt jeden Term der Rechnung (CR-01 geschlossen, `rueckgangFormelText()`). Der Vorzeichen-Wortlaut (WR-01) wurde in UAT Test 1 von Hand geprüft und akzeptiert. |
| 2 | `/investitionen`: Maßnahmen 2026-2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art; VE 11,6 Mio. mit Fälligkeiten; Finanzierung mit Kreditaufnahme/Tilgung; Schuldenstand gesamt und je Einwohner (7,7 Mio. / 656 EUR) | VERIFIED | Unverändert; `schuldenKacheln()` und Filter-/VE-/Finanzierungstests grün; UAT Test 2 (`?pb=04` meldet "1 Maßnahme") pass. |
| 3 | `/rat-entscheidet`: Zuschussbedarf 2026 nach Bindungsgrad gestapelt mit Produkten je Kategorie; Block "Was der Rat nicht beeinflussen kann"; Einzelzuschüsse; Hinweis Selbstauskunft | VERIFIED | Bindungsgrad-, Block-, Zuschuss-Tests grün; Seite und Komponenten bis auf die h2-Schriftgröße unverändert. |
| 4 | `/stellenplan`: Stellen 2026 vs. 2025 vs. besetzt 30.06.2025, Verteilung nach Aufgabenbereich und Gruppe, daneben Personalaufwand je Aufgabenbereich | VERIFIED | Stellen-Tests grün (62,91 / 62,13 / 56,63 VZÄ); `StellenplanPage.vue` von der Quick-Task nicht berührt. |
| 5 | Hinweis "Was nicht im Haushalt steht" erklärt BBO (Hallenbad) und TEO AöR (Abwasser) | VERIFIED | `HinweisNichtImHaushalt` und `texte.json` unverändert; Pipeline und `app/src/data` unverändert. |

**Score:** 5/5 Wahrheiten verifiziert, 0 present-but-behavior-unverified. Die frühere verhaltensabhängige Wahrheit (Menüliste bleibt beim erneuten Öffnen und nach Resize im Viewport) ist durch die manuelle Beobachtung in UAT Test 3 belegt; der Kern (`listenVersatz`) ist zusätzlich per Test abgedeckt.

### Required Artifacts

| Artifact | Status | Details |
| -------- | ------ | ------- |
| `app/src/pages/{Entwicklung,Investitionen,RatEntscheidet,Stellenplan}Page.vue` | VERIFIED | geroutet, mit echten Daten |
| `app/src/components/{ZuschussListe,UeberschussListe,NichtBeeinflussbarBlock}.vue` | VERIFIED | h2 nutzt `--wa-font-size-l` (UI-SPEC Heading) |
| `app/src/lib/{ruecklagen,schulden,stellen,bindungsgrad,investitionen,menueVersatz}.ts`, `charts/format.ts` | VERIFIED | substanziell, genutzt, unverändert seit dem letzten Bericht |
| `app/src/lib/__tests__/stiltokens.test.ts` | VERIFIED | Typografie-Guard grün |

### Key Link Verification

Unverändert gegenüber dem Vorbericht (Fußnote zu `rueckgangFormelText()`, `MenueGruppe.vue` zu `menueVersatz.ts`, `MassnahmenFilter.vue` zu `ergebnisText()`, `InvestitionenPage.vue` zu `schuldenKacheln()`, Bindungsgrad-Komponenten zu den Anzahltexten): WIRED. Die Quick-Task hat nur CSS-Zeilen und eine Testdatei geändert, keine Verdrahtung.

### Behavioral Spot-Checks

Ausgeführt in einer Scratch-Kopie (frisch synchronisiertes `app/src`, `app/node_modules` unberührt):

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Volle App-Testsuite | `npx vitest run` | 37 Dateien, 1585 Tests bestanden (zuvor 1576, +9 durch den Typografie-Guard) | PASS |
| Typprüfung | `vue-tsc --build` | Exit 0 | PASS |
| Lint | `eslint .` | keine Ausgabe, keine Fehler | PASS |
| Format | `prettier --check src` | "All matched files use Prettier code style" | PASS |
| Build | `vite build` | Build erzeugt (nur Chunk-Größen-Hinweis) | PASS |
| Pipeline/Daten unverändert | `git diff d1b8e64..HEAD -- pipeline daten app/src/data` | leer (Pipeline-Suite 546 passed im Vorbericht, Eingaben identisch) | PASS |

Step 7c (Probes): keine `probe-*.sh` in dieser Phase deklariert; übersprungen.

### Requirements Coverage

Alle 15 Phasen-IDs kommen in den PLAN-Frontmattern vor, sind in REQUIREMENTS.md (Zeilen 93-128) definiert und der Phase 6 zugeordnet (Traceability Zeilen 235-255). Keine verwaisten Anforderungen.

| Requirement | Status | Evidence |
| ----------- | ------ | -------- |
| ENTW-01 | SATISFIED | Erträge/Aufwendungen/Jahresergebnis 2024-2029, Wertart unterscheidbar, Defizit 2029 = -3.557.700 |
| ENTW-02 | SATISFIED | fünf Posten-Zeitreihen |
| ENTW-03 | SATISFIED | Rücklagen, Rückgang = PDF S. 23, Fußnote mit allen Termen; UAT Test 1 pass |
| INV-01 | SATISFIED | Liste, Balken, Filter mit URL-Zustand |
| INV-02 | SATISFIED | VE 11.600.000 mit Fälligkeiten |
| INV-03 | SATISFIED | Finanzierung, Kreditaufnahme/Tilgung |
| INV-04 | SATISFIED | 7,71 Mio. / 656 EUR |
| RAT-01 | SATISFIED | Segmente 29/15/15 Produkte |
| RAT-02 | SATISFIED | `NichtBeeinflussbarBlock` |
| RAT-03 | SATISFIED | `ZuschussListe` |
| RAT-04 | SATISFIED | `bindungsgrad_selbstauskunft` |
| STEL-01 | SATISFIED | 62,91 / 62,13 / 56,63 VZÄ |
| STEL-02 | SATISFIED | Verteilung nach Bereich und Gruppe |
| STEL-03 | SATISFIED | Personalaufwand je Aufgabenbereich |
| UI-04 | SATISFIED | `HinweisNichtImHaushalt` auf drei Seiten |

Hinweis: In REQUIREMENTS.md stehen Checkboxen und Traceability-Status weiterhin auf `Pending`. Das Abhaken ist Aufgabe des Orchestrators nach der Freigabe.

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| Phase-6-Dateien | TBD/FIXME/XXX/TODO/HACK | keine | Schuldenmarker-Gate bestanden |
| `app/src/lib/ruecklagen.ts` | "zuzüglich der Verrechnung" ohne Vorzeichenhinweis (Review WR-01) | INFO | Von der Fachseite in UAT Test 1 als ausreichend akzeptiert, kein Blocker |
| `app/src/components/MenueGruppe.vue` | DOM-Integration ohne Mount-Test | INFO | Durch UAT Test 3 manuell beobachtet |
| diverse | IN-01 bis IN-09 | INFO | laut 06-REVIEW.md bewusst offen, nicht zielrelevant |

### Human Verification Required

Keine. Alle drei früheren Human-Items sind in `06-UAT.md` abgeschlossen (3 passed, 0 issues, 0 pending). `06-SECURITY.md`: threats_open 0.

### Anmerkungen (nicht blockierend)

- `06-VALIDATION.md` hat im Frontmatter noch `nyquist_compliant: false`, obwohl die Sign-off-Checkliste im Dokument `nyquist_compliant: true` als gesetzt abhakt ("approved 2026-10-06"). Das ist eine Inkonsistenz im Tracking-Dokument, kein Codebefund; das Frontmatter sollte beim Abschluss auf `true` gesetzt werden.
- REQUIREMENTS.md-Checkboxen stehen auf `Pending` (siehe oben).

### Gaps Summary

Keine Gaps. Das Phasenziel ist im Code erreicht: Vier Kontext-Seiten und die Hinweisbox sind geroutet, nutzen echte Daten und reproduzieren die Sollwerte. Die Typografie-Korrektur der Quick-Task ist nachweislich auf die sechs h2-Regeln beschränkt und durch einen Guard abgesichert. Die frischen Läufe (1585 Tests, Typprüfung, Lint, Format, Build) sind grün, und alle menschlichen Prüfpunkte sind abgeschlossen.

---

_Verified: 2026-10-06_
_Verifier: Claude (gsd-verifier)_
