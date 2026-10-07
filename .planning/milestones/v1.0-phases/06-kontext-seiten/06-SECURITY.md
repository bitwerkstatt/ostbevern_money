---
phase: "6"
slug: "kontext-seiten"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-06"
---

# Phase 6 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PDF transcript → daten/manuell | Hand-typed amounts enter the checked data | öffentliche Haushaltsdaten |
| meta.json → texts/app | Threshold values become citable numbers | öffentliche Haushaltsdaten |
| URL (hash route) → router | Untrusted path segments select a page | öffentliche Haushaltsdaten |
| theme tokens → canvas | CSS values feed the chart renderer | öffentliche Haushaltsdaten |
| texte.json → DOM | Pipeline text is rendered in the browser | öffentliche Haushaltsdaten |
| erklaerungen.md / glossar.md → Schritt 07 | Hand-written texts are parsed and their Platzhalter resolved | öffentliche Haushaltsdaten |
| texte.json → app | Texts are rendered for citizens | öffentliche Haushaltsdaten |
| JSON data → chart options | Names and values feed ECharts, whose tooltip formatter output is HTML | öffentliche Haushaltsdaten |
| URL query (pb, art) → app state | Untrusted values from shared links | öffentliche Haushaltsdaten |
| JSON names → tooltips | Maßnahme names reach ECharts HTML tooltips | öffentliche Haushaltsdaten |
| JSON names → chart tooltips | Einrichtungs- and Vereinsnamen reach ECharts HTML tooltips | öffentliche Haushaltsdaten |
| meta/eigenkapital JSON → chart and text | Threshold and reserve numbers shown to citizens | öffentliche Haushaltsdaten |
| investitionen.json → charts and tiles | Debt and commitment figures shown to citizens | öffentliche Haushaltsdaten |
| produkte.json names → tooltips | Product names reach ECharts HTML tooltips | öffentliche Haushaltsdaten |
| stellenplan.json → UI | Staff figures shown to citizens | öffentliche Haushaltsdaten |
| component templates → citizens | Any hand-typed number would bypass the checked data | öffentliche Haushaltsdaten |
| generated data → citizen-facing explanation | The footnote is the only place where a reader learns how the shown Rückgang is computed; a wrong or incomplete explanation misleads without any visible error | öffentliche Haushaltsdaten |
| viewport size → navigation | The window width is user-controlled (device, resize); a mis-positioned list can hide the only navigation path to the four Phase-6 pages | öffentliche Haushaltsdaten |
| filter state (URL) → live-region announcement | The count announced to screen-reader users depends on the user-chosen filter; a wrong text is announced without visual cross-check | öffentliche Haushaltsdaten |
| generated data → Kennzahl tiles and sentences | A derived value shown without its label, or a missing value shown as a smaller number, misinforms citizens without any visible error | öffentliche Haushaltsdaten |
| review ledger → phase completion | The ledger is what later gates read to decide that CR-01 no longer stands; a premature "fixed" would let the phase seal with a live defect | öffentliche Haushaltsdaten |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-06-01 | Tampering (wrong number) | zuschuesse_lfd_zwecke.csv | high | mitigate | Regel 5 Stufe a (Σ posten = Gesamtzeile) plus cross-check against Transferposten zuschuesse_laufende_zwecke, mutation tests red — Nachweis: Regel 5 in `pipeline/ostbevern/manuell.py`/`app_daten.py`; `test_manuell.py` (Mutation → `PruefungsFehler`) | closed |
| T-06-02 | Tampering (wrong number) | meta.json HSK-Schwellen | medium | mitigate | `lies_meta_json` leaf rules and `test_meta_hsk_schwellen` pin value, unit and page — Nachweis: `test_manuell.py::test_meta_hsk_schwellen` | closed |
| T-06-03 | Information Disclosure | new manual table | low | accept | Table holds only purposes printed in the public Vorbericht, no personal names — Nachweis: Akzeptiert, siehe Accepted Risks | closed |
| T-06-SC | Tampering | npm/pip installs | high | mitigate | No new dependency; scratch-copy `npm ci` uses the committed lockfile — Nachweis: Kein Diff an `app/package.json`, `app/package-lock.json`, `pipeline/pyproject.toml`, `pipeline/uv.lock` seit 3643cf0 | closed |
| T-06-04 | Spoofing/Tampering | router | low | accept | Static route table with catch-all redirect; no parameters on the new routes — Nachweis: Akzeptiert, siehe Accepted Risks | closed |
| T-06-05 | Denial of Service (usability) | MenueGruppe | low | mitigate | Escape/outside/route/focus-out close paths, focus return, no focus trap (keyboard users cannot get stuck) — Nachweis: `MenueGruppe.vue` Escape (Z. 68), `pointerdown` außen, `@focusout`; `menue.test.ts` | closed |
| T-06-06 | Information Disclosure | icon loading | low | mitigate | Chevron drawn inline, no new icon file, no third-party request — Nachweis: Kein Chevron in `app/public/icons`, Pfeil inline | closed |
| T-06-07 | Tampering (XSS) | HinweisNichtImHaushalt | medium | mitigate | Text only through ErklaerText (text interpolation, no raw HTML; quelltext.test.ts scans every .vue) — Nachweis: 0 × `v-html` in `app/src/**/*.vue`; `quelltext.test.ts` | closed |
| T-06-08 | Tampering (misleading info) | Leitsätze | low | mitigate | Leitsätze are digit-free; numbers only from the checked pipeline text with page reference — Nachweis: Leitsätze ziffernfrei, `pruefe_text` in `pipeline/ostbevern/texte.py` | closed |
| T-06-09 | Tampering (wrong number) | ABGELEITET formulas | high | mitigate | Real-data tests incl. printed cross-checks (gesamt_vorbericht, Kredit/Tilgung identity), human review with raw-value preview — Nachweis: `test_texte.py` Realdaten-Tests; D-20-Checkpoint (06-04 T2) | closed |
| T-06-10 | Tampering (XSS precursor) | new texts | medium | mitigate | pruefe_text rejects HTML characters and bare digits; app renders text only — Nachweis: `texte.py` `pruefe_text` lehnt `<`/`>` ab (Z. 198) | closed |
| T-06-11 | Repudiation | unapproved texts | medium | mitigate | Blocking-human checkpoint before commit; drafts verified uncommitted via git status — Nachweis: Blocking-human Checkpoint 06-04 T2 laut 06-04-SUMMARY | closed |
| T-06-12 | Tampering (XSS) | chart tooltips | medium | mitigate | Tooltips only via tooltipZeilen/htmlSicher; no raw HTML directive (quelltext.test.ts) — Nachweis: `charts/tooltip.ts` `htmlSicher`/`tooltipZeilen`; `quelltext.test.ts` | closed |
| T-06-13 | Tampering (wrong number) | entwicklung.ts | high | mitigate | Identity tests against GEP rows and cross-source tests against /einnahmen and /ausgaben sources; printed 2029 value pinned — Nachweis: `entwicklung.test.ts` (Identitäten, Querquellen, 2029-Pin) | closed |
| T-06-14 | Tampering (input validation) | leseMassnahmenFilter | medium | mitigate | Allowlist via Map/Set, first array element only, prototype keys rejected, invalid values removed with router.replace (ASVS V5) — Nachweis: `lib/investitionen.ts` `PB_CODES`/`ART_CODES` Set-Allowlist, Prototyp-Schlüssel (Z. 278); `investitionen.test.ts` | closed |
| T-06-15 | Tampering (XSS) | MassnahmenListe tooltips | medium | mitigate | horizontaleBalkenOption tooltips through tooltipZeilen/htmlSicher; no raw HTML directive — Nachweis: `horizontaleBalkenOption` → `tooltipZeilen`/`htmlSicher` | closed |
| T-06-16 | Tampering (wrong number) | baueVorhaben | high | mitigate | Σ and per-Art identities against GFP rows; group count pinned for 2026 — Nachweis: `investitionen.test.ts` (Σ gegen GFP, Gruppenzahl) | closed |
| T-06-17 | Tampering (XSS) | ZuschussListe tooltips | medium | mitigate | horizontaleBalkenOption tooltips through tooltipZeilen/htmlSicher; no raw HTML directive — Nachweis: `horizontaleBalkenOption` → `tooltipZeilen`/`htmlSicher` | closed |
| T-06-18 | Tampering (wrong number) | zuschuesse.ts | high | mitigate | Σ tests against the Transferposten and Kita Gesamtzeile; KL values compared with lib/kreisumlage.ts — Nachweis: `zuschuesse.test.ts` (Σ = 120.000, KL gegen `lib/kreisumlage.ts`) | closed |
| T-06-21 | Tampering (wrong number) | ruecklagen.ts | high | mitigate | S. 23 values pinned to two decimals, S. 311 column identity, Python/TS rule equality test — Nachweis: `ruecklagen.test.ts` (S. 23 auf zwei Nachkommastellen, 1,77 %) | closed |
| T-06-22 | Repudiation (misleading statement) | Polster section | medium | mitigate | Only the approved pipeline text, thresholds attributed to the Vorbericht, no forecast beyond the last plan year — Nachweis: Freigegebener Pipeline-Text; UAT 06 Test 1 pass | closed |
| T-06-23 | Tampering (wrong number) | schulden.ts / finanzierung.ts | high | mitigate | Identity tests: gesamt = Investitionskredite + NRW.Bank, Σ VE = GFP VE, Σ rows 18–22 = Z. 23, series = GFP rows — Nachweis: `schulden.test.ts`, `finanzierung.test.ts` (Σ VE = 11.600.000) | closed |
| T-06-24 | Repudiation (misleading) | berechnet years | medium | mitigate | Decal and axis line driven only by schuldenstand.berechnet, tested against the array — Nachweis: `schulden.test.ts` (`berechnet`-Array) | closed |
| T-06-25 | Tampering (XSS) | chart tooltips with Maßnahme names | medium | mitigate | tooltipZeilen/htmlSicher only; no raw HTML directive — Nachweis: `tooltipZeilen`/`htmlSicher`; `quelltext.test.ts` | closed |
| T-06-26 | Tampering (wrong number / misleading) | bindungsgrad.ts | high | mitigate | Values read from berechnet only, sums and exclusions tested, explaining caption that the bar is not the whole Zuschussbedarf — Nachweis: `bindungsgrad.test.ts` (6.358.143 / Ausschlüsse) | closed |
| T-06-27 | Tampering (XSS) | product bar tooltips | medium | mitigate | horizontaleBalkenOption with tooltipZeilen/htmlSicher; no raw HTML directive — Nachweis: `horizontaleBalkenOption` → `tooltipZeilen`/`htmlSicher` | closed |
| T-06-28 | Tampering (wrong number) | stellen.ts | high | mitigate | Hundredths arithmetic, three-way sum identity, Personalaufwand Σ = GESAMT, pinned 2026 values — Nachweis: `stellen.test.ts` (6291, 5.204.054) | closed |
| T-06-29 | Information Disclosure | Stellenplan view | medium | mitigate | Only Gruppen, Teile and Aufgabenbereiche are shown; amtsbezeichnung is not rendered; no salary-like ratio — Nachweis: `amtsbezeichnung` außerhalb von Tests/Daten nirgends in `app/src` | closed |
| T-06-30 | Tampering (integrity) | all Phase-6 .vue templates | high | mitigate | Template scan for hand-typed amounts/percentages/grouped numbers across every .vue file — Nachweis: `quelltext.test.ts` Template-Scan aller `.vue` | closed |
| T-06-31 | Tampering (XSS) | all Phase-6 components | medium | mitigate | Template scan for the raw-HTML directive across every .vue file — Nachweis: `quelltext.test.ts`; 0 × `v-html` | closed |
| T-06-32 | Tampering (integrity of citizen information) | rueckgangFormelText() / EntwicklungPage tabellenFussnote | high | mitigate | Clause built next to abbau() from the same posten constants; vitest recomputes every plan year from the named terms and must equal rueckgang(); a 2026 runIf test proves the pre-fix wording would yield 0,56 % instead of 1,77 %; source test pins that the page uses the lib function — Nachweis: `rueckgangFormelText` in `lib/ruecklagen.ts`, genutzt von `EntwicklungPage.vue`; `ruecklagen.test.ts` | closed |
| T-06-33 | Tampering (integrity) | baueRuecklagen() summe | medium | mitigate | summe is null unless both halves exist; tests for a missing allgemeine Rücklage, a missing Ausgleichsrücklage and a real 0 — Nachweis: `ruecklagen.test.ts` (fehlende Hälften → `null`) | closed |
| T-06-34 | Denial of Service (UI) | MenueGruppe.positioniere / listenVersatz | low | mitigate | Offset computed absolutely from the base position via a pure function; node tests for reopen, resize, left/right overflow, over-wide list and a fixed-point grid; source test pins the wiring — Nachweis: `lib/menueVersatz.ts` `listenVersatz`, verdrahtet in `MenueGruppe.vue`; Node-Tests; UAT 06 Test 3 pass | closed |
| T-06-35 | Tampering (integrity of citizen-facing text) | MassnahmenFilter aria-live line, ProduktBalkenListe summary, BindungsgradBalken tooltip | low | mitigate | Strings built by tested lib functions over anzahlText; test over every real pb × art combination; source test bans fixed-plural count literals in the three components — Nachweis: `anzahlText` in `lib/investitionen.ts`/`lib/bindungsgrad.ts`; Tests grün | closed |
| T-06-36 | Tampering (integrity of citizen information) | schuldenKacheln() / InvestitionenPage tiles | medium | mitigate | Both tiles take the flag from schuldenstand.berechnet of the Vorjahr; tests with berechnet true and false, Jahrgang pin, source test that the page no longer builds the tiles — Nachweis: `schuldenKacheln` in `lib/schulden.ts`, genutzt von `InvestitionenPage.vue`; `schulden.test.ts` | closed |
| T-06-37 | Tampering (integrity) | nachwuchs() in lib/stellen.ts | medium | mitigate | A row without personen makes the year null (never 0); tests for both years; pinned 2026 values unchanged — Nachweis: `nachwuchs` in `lib/stellen.ts`; `stellen.test.ts` | closed |
| T-06-38 | Repudiation (integrity of the review record) | 06-REVIEW-DISPOSITION.md | medium | mitigate | Ledger edited only after the CI-identical gate and the wiring greps are green in the same run; a parser check pins exactly six fixed and eight open entries and the unchanged YAML header; the SUMMARY records the evidence per finding — Nachweis: `06-REVIEW-DISPOSITION.md` mit Dispositionen fixed/open laut 06-17-SUMMARY | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-06-01 | T-06-03 | Die Tabelle `zuschuesse_lfd_zwecke` enthält nur im öffentlichen Vorbericht gedruckte Zwecke, keine Personennamen | Plan 06-01 | 2026-10-06 |
| AR-06-02 | T-06-04 | Statische Routentabelle mit Catch-all-Redirect; die neuen Routen haben keine Parameter | Plan 06-02 | 2026-10-06 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-06 | 37 | 37 | 0 | /gsd-secure-phase (L1 grep, Orchestrator) |

## Security Audit 2026-10-06
| Metric | Count |
|--------|-------|
| Threats found | 37 |
| Closed | 37 |
| Open | 0 |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-06
