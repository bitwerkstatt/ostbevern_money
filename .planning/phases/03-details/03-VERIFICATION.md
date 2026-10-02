---
phase: 03-details
verified: 2026-10-02T10:10:00Z
status: passed
score: 11/11 must-haves verified
covered_files: [".planning/phases/03-details/03-01-PLAN.md", ".planning/phases/03-details/03-01-SUMMARY.md", ".planning/phases/03-details/03-02-PLAN.md", ".planning/phases/03-details/03-02-SUMMARY.md", ".planning/phases/03-details/03-03-PLAN.md", ".planning/phases/03-details/03-03-SUMMARY.md", ".planning/phases/03-details/03-04-PLAN.md", ".planning/phases/03-details/03-04-SUMMARY.md", ".planning/phases/03-details/03-05-PLAN.md", ".planning/phases/03-details/03-05-SUMMARY.md", "daten/aufbereitet/erlaeuterungen.csv", "daten/aufbereitet/grundzahlen.csv", "daten/aufbereitet/investitionen.csv", "daten/aufbereitet/produkte.json", "daten/aufbereitet/ve_faelligkeiten.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/investitionen_pb.csv", "daten/zwischen/querschnitte.csv", "pipeline/03_produktinfos.py", "pipeline/04_investitionen.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/freitext.py", "pipeline/ostbevern/investitionen.py", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/produkte.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/querschnitte.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/spalten.py", "pipeline/ostbevern/zahlen.py", "pipeline/tests/conftest.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_freitext.py", "pipeline/tests/test_investitionen.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_produkte.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_querschnitte.py", "pipeline/tests/test_spalten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v2:sha256:38e68b79fc2e3f21e37db48feb2c8fee21253233f9530fbb79161a52c3a32a1d"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 3: Details — Verification Report

**Phase Goal:** Alle 63 Produkte sind inhaltlich vollständig beschrieben (Produktinformationen, Bindungsgrad, Grundzahlen, Erläuterungen), und die Investitionsmaßnahmen stimmen mit den Finanzplänen überein.
**Verified:** 2026-10-02T10:10:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth (ROADMAP.md Success Criterion) | Status | Evidence |
|---|---------------------------------------|--------|----------|
| 1 | `produkte.json` enthält alle 63 Produkte mit Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Klassifizierung, Zielgruppe, Zielen, PDF-Seiten und Bindungsgrad (normalisiert + original); Regel 8 grün | ✓ VERIFIED | `daten/aufbereitet/produkte.json` has 63 records, keys exactly `{code,name,pb,pg,fachbereich,gremium,beschreibung,leistungen,auftragsgrundlage,bindungsgrad,bindungsgrad_original,klassifizierung,zielgruppe,ziele,erlaeuterungen,pdf_seiten}`, sorted by code, `bindungsgrad` ⊆ {pflichtig,freiwillig,teils}; sample 030101: `bindungsgrad_original="teils pflichtig teils freiwillig"`, `gremium="Bildungs-, Generationen- und Sozialausschuss"`, `leistungen[0]="Betrieb der Ambrosius-Grundschule"`, `pdf_seiten=[151,152,153,154]` (matches Spez. 4.2). `konsistenz.md`: `Regel 8 – Vollständigkeit der Produkte | grün | 820 | 0 | 0 | 0`. |
| 2 | `grundzahlen.csv` führt Kennzahlen je Produkt mit Einheit, Jahr, Stichtagshinweis, inkl. Steuer-Istwerte 2022–2025 aus 160101 (Gewerbesteuer 2023 = 4.771.497 €); Erläuterungsposten je Produkt mit Betrag, Text, Zeilenbezug | ✓ VERIFIED | `grundzahlen.csv` header `produkt,position,gruppe,bezeichnung,einheit,jahr,wert,nachkommastellen,hinweis,pdf_seite`; row `160101,1,,Gewerbesteuer (Im Teilplan Zeile 01),EUR,2023,4771497.0,0,,280` present exactly. 48 distinct products, 0 null `einheit`. `erlaeuterungen.csv` header `produkt,block,position,zu_zeilen,betrag,text,pdf_seite`; Spez. 4.2 example row `030101,1,...,13|16,66500,"Strom, Nahwärme, Wasser, Abwasser",152` present. |
| 3 | `investitionen.csv` stammt nur aus Produktseiten; Summe je Produkt = TFP Z. 23/30; Summe aller Maßnahmen 2026 = 7.224.830 € / 12.280.484 € (Regel 6); „(Kassenwirksamkeit)“ nur in `ve_faelligkeiten.csv`, nicht in Summen | ✓ VERIFIED | `investitionen.csv` (959 data rows): Ansatz-Haushaltsjahr `einzahlung` sum = 7224830, `auszahlung` sum = 12280484 (computed directly via polars, matches roadmap figures exactly); no Konto with prefix 692/792 present. `ve_faelligkeiten.csv` holds exactly 8 rows, separate file, not referenced in any investitionen.csv sum. `konsistenz.md`: `Regel 6 – Investitionsmaßnahmen → Teil-/Gesamtfinanzplan \| grün \| 1964 \| 0 \| 0 \| 8`. |
| 4 | Querschnitte ab S. 291 stimmen mit eigenen PG-Aggregaten überein (Regel 7); `konsistenz.md` meldet Regeln 1–4 und 6–8 als grün | ✓ VERIFIED | `querschnitte.csv` (control source) has exactly 1152 data rows. `konsistenz.md`: `Gesamtstatus: grün`; overview table lists Regeln 1,2,3,4,6,7,8 — all `grün`, 0 open Abweichungen, 0 Lücken; `## Lücken` section reads `Keine.`; `## Veraltete Befunde` reads `Keine.`. Fresh `alle.py --jahr 2026` run (this verification pass) reproduced identical line: `Schritt 06: Regel 7: grün (1152 Werte)`. |

**Score:** 4/4 roadmap success criteria verified; 7/7 plan-level must-have clusters (truths below) verified. No items routed to human verification, no behavior-unverified truths, no overrides.

### Plan-Level Must-Have Highlights (cross-checked against ROADMAP SCs above)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 5 | 03-01: `06_pruefen.py`/`alle.py` extract Querschnitte before CSV-only `pruefung.py`; Regel 7 never reads the PDF | ✓ VERIFIED | `test_pruefung_liest_kein_pdf` (AST import check) passes; `alle.py` output order confirmed (`Schritt 06: Querschnitte: 1152 Werte geschrieben.` precedes `Regel 7: grün`). |
| 6 | 03-02: `art`/`richtung`/Kontengruppen vocabulary fixed (D-07); Finanzierungs-Konten (692/792) excluded and verified against TFP Z.33/35 | ✓ VERIFIED | `art` set in investitionen.csv = exactly `{ausstattung,bau,beitraege,finanzanlagen,grundstuecke,immaterielles,investitionszuschuesse,zuwendungen}`; no 692/792 Konto present (checked directly on CSV). |
| 7 | 03-03: PB-Investitionslisten cross-checked against product pages (D-06); one-sided measures become non-excusable Lücken | ✓ VERIFIED | `investitionen_pb.csv` sums to the same 7.224.830 € / 12.280.484 €; `konsistenz.md` Regel 6 shows 0 Lücken on checked-in data; `test_pruefung.py -k "luecke or pb_liste"` subset passes within the full 294-test run. |
| 8 | 03-04: No personal name (`Verantwortliche/r`, `Sachbearbeiter/innen`) reaches any file under `daten/` (D-09) | ✓ VERIFIED | `uv run pytest tests/test_produkte.py -q -k keine_personennamen` → `1 passed`; manual `grep -rn "verantwortlich\|sachbearbeiter" daten/` returns no hits. |
| 9 | 03-04: Erläuterungen D-04 plausibility (zu_zeilen printed, Posten ≤ referenced Ansatz sum) holds on real data | ✓ VERIFIED | Full test suite includes `test_pruefe_plausibilitaet_gruen_auf_echten_daten` and the two violation-detection tests; all passed in the 294-test run. |
| 10 | 03-05: `lies_kennzahl` parses German decimals correctly; Grundzahlen units/hints/groups normalised (D-12/D-13) | ✓ VERIFIED | Stichproben tests (`test_stichprobe_grundzahl_*`, 5 cases) passed; `grundzahlen.csv` has rows with `nachkommastellen>0` and `einheit` starting `EUR/`; no `einheit` equals `C`/`C/...`. |
| 11 | Phase gate: `alle.py --jahr 2026` leaves `git status --porcelain daten/` empty; full pytest suite and ruff/CI-replay green | ✓ VERIFIED | Re-ran in this verification session: `alle.py --jahr 2026` exit 0, `git status --porcelain daten/` empty afterwards; `pytest -q` → `294 passed`; `ruff check .` / `ruff format --check .` → all pass. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `daten/aufbereitet/produkte.json` | 63 products, no person names | ✓ VERIFIED | 63 records, exact key set, sample values match Spez. 4.2 |
| `daten/aufbereitet/grundzahlen.csv` | Grundzahlen incl. Steuer-Istwerte | ✓ VERIFIED | 827 rows, 48 products, 160101 Gewerbesteuer 2023 row exact |
| `daten/aufbereitet/erlaeuterungen.csv` | Erläuterungsposten | ✓ VERIFIED | 229 rows, 030101 Spez.-example row exact |
| `daten/aufbereitet/investitionen.csv` | Product-page investment measures | ✓ VERIFIED | 959 rows, sums = 7.224.830 € / 12.280.484 €, no 692/792 |
| `daten/aufbereitet/ve_faelligkeiten.csv` | Kassenwirksamkeit maturities | ✓ VERIFIED | 8 rows, separate from sums |
| `daten/zwischen/querschnitte.csv` | Control source for Regel 7 | ✓ VERIFIED | 1152 rows |
| `daten/zwischen/investitionen_pb.csv` | Control source for Regel 6 PB check | ✓ VERIFIED | 959 rows, same totals as product pages |
| `daten/pruefberichte/konsistenz.md` | Regeln 1-4, 6-8 grün | ✓ VERIFIED | Gesamtstatus grün; all 7 rules grün; 0 open Abweichungen/Lücken |
| `pipeline/ostbevern/pruefung.py` (Regel 6/7/8) | `_pruefe_regel6/7/8` | ✓ VERIFIED | Present, wired into `pruefe_alles`, exercised by passing tests |
| `pipeline/ostbevern/produkte.py` | `extrahiere_produkte` incl. Grundzahlen/Erläuterungen | ✓ VERIFIED | Present; writes 3 outputs; D-09 drop confirmed |
| `pipeline/ostbevern/investitionen.py` | Investitionen parser | ✓ VERIFIED | Present; writes 3 outputs (product, VE, PB) |
| `pipeline/ostbevern/querschnitte.py` | Querschnitte parser | ✓ VERIFIED | Present; writes control CSV |

### Key Link Verification

| From | To | Via | Status |
|------|----|----|--------|
| `pipeline/alle.py` | `produkte.extrahiere_produkte` | module-attribute call, Schritt 03 | ✓ WIRED (confirmed via live run output `Schritt 03: ...`) |
| `pipeline/alle.py` | `investitionen.extrahiere_investitionen` | Schritt 04 | ✓ WIRED (`Schritt 04: ...` lines observed) |
| `pipeline/alle.py` | `querschnitte.extrahiere_querschnitte` | Schritt 06 pre-Prüfung | ✓ WIRED (`Schritt 06: Querschnitte: ...` observed) |
| `pipeline/ostbevern/pruefung.py` | `daten/aufbereitet/produkte.json` | `lies_produkte_json` feeds `_pruefe_regel8` | ✓ WIRED (Regel 8 grün with 820 geprüfte Werte) |
| `pipeline/ostbevern/pruefung.py` | `daten/aufbereitet/investitionen.csv` + `investitionen_pb.csv` | Regel 6 product/PB cross-check | ✓ WIRED (Regel 6 grün, 0 Lücken) |

### Data-Flow Trace (Level 4)

All five generated artifacts (`produkte.json`, `grundzahlen.csv`, `erlaeuterungen.csv`, `investitionen.csv`, `querschnitte.csv`) were regenerated live in this verification session via `uv run --directory pipeline python alle.py --jahr 2026` and produced byte-identical output to the checked-in files (`git status --porcelain daten/` empty afterward) — confirming the full PDF → pipeline → CSV/JSON chain is live, not static/mocked data.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full pipeline regenerates deterministically | `uv run --directory pipeline python alle.py --jahr 2026` | exit 0, all 7 rules grün, `git status --porcelain daten/` empty | ✓ PASS |
| Full test suite | `uv run --directory pipeline pytest -q` | `294 passed in 190.05s` | ✓ PASS |
| Privacy test (D-09) over full `daten/` tree | `pytest tests/test_produkte.py -q -k keine_personennamen` | `1 passed` | ✓ PASS |
| Regel 8 test subset | `pytest tests/test_pruefung.py -q -k regel8` | `11 passed` | ✓ PASS |
| Regel 6/7 test subset | `pytest tests/test_pruefung.py -q -k "regel6 or regel7"` | `13 passed` | ✓ PASS |
| Lint/format | `ruff check .` / `ruff format --check .` | both clean | ✓ PASS |
| No dependency drift | `git diff --exit-code pipeline/pyproject.toml pipeline/uv.lock` | exit 0 | ✓ PASS |
| No debt markers in phase files | `grep -nE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` over all pipeline files touched in this phase | no matches | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention exists in this project; the phase's own acceptance mechanism is the `konsistenz.md` rule report plus pytest, both exercised above. N/A.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| EXTR-06 | 03-04 | Produktinformationen aller 63 Produkte in `produkte.json` | ✓ SATISFIED | 63 records, exact field set, Stichprobe 030101 matches |
| EXTR-07 | 03-05 | Grundzahlen je Produkt mit Einheit/Jahr/Stichtagshinweis, Steuer-Istwerte 160101 | ✓ SATISFIED | 827 rows, Gewerbesteuer 2023 = 4.771.497 confirmed |
| EXTR-08 | 03-04 | Erläuterungsposten je Produkt mit Betrag/Text/Zeilenbezug | ✓ SATISFIED | 229 rows, Spez. 4.2 example row confirmed |
| EXTR-09 | 03-02, 03-03 | Investitionsmaßnahmen nur aus Produktseiten; Kassenwirksamkeit separat | ✓ SATISFIED | 959 rows, no 692/792, ve_faelligkeiten.csv separate (8 rows) |
| PRUEF-06 | 03-02, 03-03 | Investitionssummen je Produkt/Gesamt stimmen (7.224.830 €/12.280.484 €) | ✓ SATISFIED | Sums computed directly match exactly; Regel 6 grün |
| PRUEF-07 | 03-01 | Querschnitte S.291ff stimmen mit PG-Aggregaten | ✓ SATISFIED | 1152 rows; Regel 7 grün |
| PRUEF-08 | 03-05 | Vollständigkeit: 63 Produkte mit allen Pflichtfeldern | ✓ SATISFIED | Regel 8 grün, 820 geprüfte Werte, 0 Lücken |

All 7 phase requirements declared in PLAN frontmatter are marked `Complete` in `.planning/REQUIREMENTS.md` and mapped to `Phase 3`. No orphaned requirements found (grep for "Phase 3" in REQUIREMENTS.md returns exactly these 7 IDs).

### Decision Coverage

CONTEXT.md decisions (D-01 through D-15) are reflected across the five plan SUMMARY.md files' `key-decisions` sections and in the implementation details verified above (D-06 PB cross-check, D-07 Kontengruppen vocabulary, D-08 fail-fast guards, D-09 privacy triple-enforcement, D-12/D-13 Grundzahlen hints/groups, D-14 control-source separation). No decision appears abandoned without documentation.

### Anti-Patterns Found

None. Scanned all pipeline files modified across the five plans for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and common stub patterns — zero matches. No hardcoded empty-data patterns found in the generated-data writers (all write from parsed PDF content, confirmed via live regeneration).

### Code Review Findings (advisory, pre-existing disposition)

`03-REVIEW.md` / `03-REVIEW-DISPOSITION.md` record 5 open findings, 0 critical, 0 blocking:
- WR-01 (warning): `ordne_spalten` tolerance computed globally, not per-anchor-pair.
- WR-02 (warning): `test_alle.py` mocks `extrahiere_produkte` with a 2-tuple while the real function returns a 3-tuple. **Verified as a test-fixture inaccuracy, not a production defect**: `alle.py` iterates the result generically (`for ergebnis in ergebnisse_produkte`), so the mismatch only means the mocked test echoes 2 lines instead of 3 — it does not affect correctness of the real pipeline (confirmed live: real `alle.py` run emits 3 "Schritt 03:" lines as designed, and the full 294-test suite still passes).
- IN-01, IN-02, IN-03 (info): labeling/documentation nits, no functional impact.

These were already triaged as `open` (not `fixed`/`skipped`) by the developer and are advisory per the task's framing ("0 critical"); none block the phase goal.

### Human Verification Required

None. This is a data-pipeline/backend phase (CLI tools, CSV/JSON outputs, automated Prüfregeln) with no user-facing UI — infrastructure/foundation carve-out applies. All acceptance criteria are verifiable programmatically and were verified directly against the real PDF-derived data in this session (not merely re-reading SUMMARY.md claims).

### Gaps Summary

No gaps. All four ROADMAP.md Success Criteria for Phase 3 are independently verified against the live codebase and regenerated data: `produkte.json` (63 products, Regel 8 grün), `grundzahlen.csv`/`erlaeuterungen.csv` (with exact Spez. 4.2 sample values), `investitionen.csv`/`ve_faelligkeiten.csv` (sums exactly matching the roadmap's stated totals), and `querschnitte.csv` (Regel 7 grün). `konsistenz.md` reports Gesamtstatus grün with Regeln 1-4 and 6-8 all grün, 0 open Abweichungen, 0 Lücken. The full pytest suite (294 tests), ruff lint/format, and a fresh `alle.py --jahr 2026` regeneration all pass with an empty `git status --porcelain daten/` afterward — confirming determinism, not just a one-time checked-in snapshot.

---

_Verified: 2026-10-02T10:10:00Z_
_Verifier: Claude (gsd-verifier)_
