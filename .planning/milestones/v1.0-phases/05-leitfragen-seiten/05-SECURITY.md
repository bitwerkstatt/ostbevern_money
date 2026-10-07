---
phase: "5"
slug: "leitfragen-seiten"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-05"
---

# Phase 5 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| PDF → pipeline | Pipeline reads the official budget PDF and manual transcriptions | public budget figures (integrity-critical) |
| pipeline → app data | Generated JSON under app/src/data is the only data source of the app | public figures, approved texts (integrity-critical) |
| URL (hash route, query, fragment) → app | Year, view, product code and glossary anchors come from the URL | untrusted user input (low sensitivity) |
| app → browser DOM / ECharts tooltips | Dynamic strings rendered as text or escaped HTML | public data (XSS surface) |
| npm registry → build | Dev dependency vitest 5.0.3 added | supply chain |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-05-01 | Tampering (integrity of displayed numbers) | `formatiere()` | medium | mitigate | formatiere() returns "–" for nullish/non-finite; test_formatiere.py + format.test.ts | closed |
| T-05-02 | Repudiation | CI test step | low | accept | Accepted (see log) | closed |
| T-05-SC | Tampering | npm/pip installs (all plans) | high | mitigate | vitest pinned exactly at 5.0.3 (devDependency); no other new dependency in phase; npm ci from lockfile | closed |
| T-05-03 | Tampering (data integrity) | transcription of S. 33/S. 52 | high | mitigate | Regel 5 in pipeline/ostbevern/app_daten.py; test_pruefung.py / test_manuell.py | closed |
| T-05-04 | Repudiation | befunde.md | medium | mitigate | daten/pruefberichte/befunde.md; stale-Befund mechanism | closed |
| T-05-05 | Tampering (plan mixing) | haushalt.json vorbericht | medium | mitigate | test_app_daten.py asserts planzeile/gesamt_plan null for investitionszuwendungen | closed |
| T-05-06 | Tampering (XSS precursor) | glossary texts | medium | mitigate | pipeline/ostbevern/texte.py pruefe_text rejects < and > | closed |
| T-05-07 | Tampering (wrong number) | placeholders in glossary/texts | high | mitigate | texte.py pruefe_grundzahl_jahre + digit rule; human review done (05-03 checkpoint) | closed |
| T-05-08 | Repudiation | unapproved texts | medium | mitigate | 05-03 blocking-human checkpoint approved before commit | closed |
| T-05-09 | Tampering | `leseJahr`, `leseAnsicht`, `findeProdukt` | medium | mitigate | allowlists; __proto__ cases in ansicht.test.ts / jahr.test.ts | closed |
| T-05-10 | Tampering (reflected XSS) | not-found message with `:code` | medium | mitigate | no v-html/innerHTML in app/src (0 files); quelltext.test.ts scan | closed |
| T-05-11 | Spoofing (open redirect) | router, hash handling | low | mitigate | named routes only; hash used solely via getElementById (lib/sprungziel.ts) | closed |
| T-05-12 | Tampering (XSS) | ECharts tooltip formatters | medium | mitigate | htmlSicher/tooltipZeilen in charts/tooltip.ts; tooltip.test.ts | closed |
| T-05-13 | Information disclosure (misleading display) | colour-only encoding | low | mitigate | decals + text for KL/Überschuss; farben.test.ts contrast | closed |
| T-05-14 | Tampering (XSS) | ErklaerText, KreisumlageCallout | medium | mitigate | text interpolation only; v-html scan empty | closed |
| T-05-15 | Tampering (integrity: wrong year) | textFuerJahr | high | mitigate | textFuerJahr; texte.test.ts per text and year | closed |
| T-05-16 | Tampering | placeholder lookup | low | mitigate | Object.hasOwn/Map lookups in lib | closed |
| T-05-17 | Tampering (reverse tabnabbing) | external footer links | low | mitigate | rel="noopener noreferrer" on external links in App.vue; config.test.ts | closed |
| T-05-18 | Repudiation | placeholder contact in production | medium | mitigate | .invalid placeholders in config.ts, istPlatzhalter; D-17 hand-off to Phase 7 | closed |
| T-05-19 | Spoofing (navigation hijack) | wa-page skip link in hash router | low | mitigate | skip-link click preventDefault in App.vue; menue.test.ts; UAT test 7 pass | closed |
| T-05-20 | Information disclosure | third-party requests | low | mitigate | icons self-hosted under app/public/icons; no runtime fetch/CDN in app/src | closed |
| T-05-21 | Tampering (integrity of displayed numbers) | Kennzahlenband | high | mitigate | kennzahlen.test.ts per field; quelltext.test.ts template gate | closed |
| T-05-22 | Information disclosure (misleading label) | Einstiegskachel 2 | low | mitigate | synthetic KL node excluded; kennzahlen.test.ts | closed |
| T-05-23 | Tampering (integrity: plan mixing) | investive section | medium | mitigate | separate builder in lib/einnahmen.ts; einnahmen.test.ts investive sums | closed |
| T-05-24 | Tampering (integrity: source mix) | tax time series | high | mitigate | D-01 tests in zeitreihen.test.ts | closed |
| T-05-25 | Tampering (XSS) | ECharts tooltips | medium | mitigate | tooltipZeilen in balken/einnahmen tooltips; balken.test.ts | closed |
| T-05-26 | Tampering | pb/pg handling | medium | mitigate | useAnsicht allowlists; baueEbene throws for unknown codes; drilldown.test.ts | closed |
| T-05-27 | Tampering (XSS) | treemap/bar tooltips | medium | mitigate | tooltipZeilen/htmlSicher for every dynamic string | closed |
| T-05-28 | Tampering (integrity) | Zuschussbedarf display | high | mitigate | values from berechnet only; no ertraege arithmetic in drilldown.ts; drilldown.test.ts | closed |
| T-05-29 | Tampering | product code lookup | medium | mitigate | findeProdukt via Map; produkt.test.ts prototype codes | closed |
| T-05-30 | Tampering (reflected XSS) | not-found text and back link | medium | mitigate | text interpolation; back query re-validated with leseAnsicht | closed |
| T-05-31 | Information disclosure (misleading per-unit value) | Bezugsgrößen | medium | mitigate | approved Bezugsgrößen only; produkt.test.ts | closed |
| T-05-32 | Tampering (integrity: misleading balance) | baueGeldfluss | high | mitigate | geldfluss.test.ts balance ±2 € all years | closed |
| T-05-33 | Tampering (XSS) | Sankey/bar tooltips | medium | mitigate | tooltipZeilen/htmlSicher in Sankey/bar tooltips | closed |
| T-05-34 | Tampering (wrong-year text) | reading aid | medium | mitigate | welcheLesetexte + textFuerJahr; geldfluss.test.ts per year | closed |
| T-05-35 | Tampering | hash handling | low | mitigate | getElementById only (lib/sprungziel.ts); unknown id no-op | closed |
| T-05-36 | Tampering (XSS) | GlossarListe, tooltips | medium | mitigate | text interpolation only; no v-html | closed |
| T-05-37 | Tampering (integrity) | Aufwandsart sums | medium | mitigate | aufwandsarten.test.ts exact sums per year | closed |
| T-05-38 | Tampering (wrong-year text) | Minderaufwand hint | medium | mitigate | curated text only for Haushaltsjahr; aufwandsarten.test.ts | closed |
| T-05-39 | Information disclosure (false precision) | Transfer/KL Unterposten | low | mitigate | "rd." marking in lib/kreisumlage.ts; kreisumlage.test.ts | closed |
| T-05-40 | Tampering (integrity) | .vue templates | high | mitigate | quelltext.test.ts source scan with fail-first sample | closed |
| T-05-41 | Tampering (XSS) | all components | medium | mitigate | quelltext.test.ts raw-HTML directive scan | closed |
| T-05-42 | Tampering | glossary keys | low | mitigate | glossary union type + usage scan (glossar.test.ts) | closed |
| T-05-43 | Tampering (injection) | app/src/lib/sprungziel.ts elementFuerHash | medium | mitigate | elementFuerHash getElementById on decoded fragment; sprungziel.test.ts | closed |
| T-05-44 | Denial of Service (UI) | sprungPosition / versatzAusScrollMargin | low | mitigate | Number.isFinite && >0 clamp in sprungziel.ts; sprungziel.test.ts | closed |
| T-05-45 | Tampering (integrity of presentation) | all .vue/.css/.ts using var(--wa-*) | low | mitigate | stiltokens.test.ts with fail-first samples | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-05-01 | T-05-02 | CI test step runs only local unit tests; no secrets, no network beyond `npm ci` from the committed lockfile | plan 05-01 (threat model) | 2026-10-04 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-05 | 46 | 46 | 0 | /gsd-secure-phase (L1 grep-level verification, orchestrator) |

Evidence base: PLAN `<threat_model>` blocks 05-01 to 05-16, SUMMARY `## Threat Flags` (none raised), grep checks over `app/src` and `pipeline/ostbevern`, full test suites green on 2026-10-05 (pytest 528, vitest 1031).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-05
