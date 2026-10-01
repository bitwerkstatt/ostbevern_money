---
phase: 02-kernzahlen
verified: 2026-10-01T15:31:01Z
status: passed
score: 5/5 must-haves verified (roadmap Success Criteria); 28/28 plan-level must_have truths verified
covered_files: [".planning/phases/02-kernzahlen/02-01-PLAN.md", ".planning/phases/02-kernzahlen/02-01-SUMMARY.md", ".planning/phases/02-kernzahlen/02-02-PLAN.md", ".planning/phases/02-kernzahlen/02-02-SUMMARY.md", ".planning/phases/02-kernzahlen/02-03-PLAN.md", ".planning/phases/02-kernzahlen/02-03-SUMMARY.md", ".planning/phases/02-kernzahlen/02-04-PLAN.md", ".planning/phases/02-kernzahlen/02-04-SUMMARY.md", ".planning/phases/02-kernzahlen/02-05-PLAN.md", ".planning/phases/02-kernzahlen/02-05-SUMMARY.md", "daten/aufbereitet/ergebnisplan.csv", "daten/aufbereitet/finanzplan.csv", "daten/aufbereitet/hierarchie.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/seiten.csv", "pipeline/01_seiten_klassifizieren.py", "pipeline/02_plaene_extrahieren.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/plaene.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/seiten.py", "pipeline/ostbevern/zahlen.py", "pipeline/ostbevern/zeilen.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_hierarchie.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_plaene.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_seiten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v2:sha256:e1d9cc14a245a053fe4580628e7297082ef0881737bfe360bff9c0184902f991"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 2: Kernzahlen Verification Report

**Phase Goal:** Alle Ergebnis- und Finanzpläne (Gesamt, PB, Produkt) liegen korrekt im Langformat vor. Die Pipeline weist das durch automatische Prüfungen und Anhang-B-Sollwerte nach.
**Verified:** 2026-10-01T15:31:01Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `seiten.csv` maps every PDF page to typ/PB/PG/Produkt with continuation-page inheritance; Anhang-A start-page test for all 63 products; `hierarchie.csv` has 15 PB, all PG (synthetic flagged) and 63 named products | ✓ VERIFIED | `daten/zwischen/seiten.csv` has exactly 400 rows, one per PDF page (1..400), 0 pages typed `unbekannt` (confirmed via live `alle.py` run). `daten/aufbereitet/hierarchie.csv` (parsed with `csv.DictReader`, not naive comma-split, to handle quoted names with commas) has 15 PB, 48 PG (40 `synthetisch=true` + 8 printed), 63 P. `pipeline/tests/test_hierarchie.py` (7 tests, all pass) asserts PB/PG/P codes exactly match Anhang A, names match ignoring whitespace/case, start pages match, and synthetic-PG derivation rule holds. |
| 2 | Zahlenparser unit tests green: German thousands format, minus (ASCII + U+2212), „–" as no-value, glued amounts, `C`/`€` as Euro sign | ✓ VERIFIED | `pipeline/tests/test_zahlen.py` (21 tests) covers all listed forms plus invalid-format rejection; `pipeline/ostbevern/zahlen.py` is a 80-line, non-stub implementation. Full pytest run: 129/129 passed. |
| 3 | `ergebnisplan.csv`/`finanzplan.csv` (incl. VE) hold Gesamt/PB/Produkt plans with `zeile`, `zeile_kanonisch`, `ist_summe`, `pdf_seite`; Regel 1 (Zeilenformeln) green for every plan; Regel 2 (Produkt→PG→PB) green; Regel 3 (15 PB → Gesamt, excl. TP 27/28) green | ✓ VERIFIED | Both CSVs have all required columns and all four `ebene` levels with non-trivial row counts (ergebnisplan: GESAMT 198, PB 1236, PG 3702, P 4992; finanzplan: GESAMT 287, PB 672, PG 1575, P 2163; `wertart=ve` present, 671 rows). Live `alle.py --jahr 2026` run: Regel 1 grün (6550 Werte), Regel 2 grün (7920 Werte), Regel 3 grün (114 Werte), all 0 Abweichungen. Manipulation tests (`test_regel2_erkennt_manipulierte_produktzeile`, `test_regel3_erkennt_manipulierte_pb_zeile`, etc.) prove these rules actually detect injected errors, not trivially-green checks. |
| 4 | Anhang-B Sollwerte matched to the Euro: B.1 Z.28 2026 = −2.353.506 €; B.2 Z.23/30/33/41; B.3 PB sums 27.042.063 €/30.255.569 €; Satzung § 1 27.502.063 €/30.455.569 € | ✓ VERIFIED | Independently queried CSVs confirm exact figures: B.1 Z.28 2026 = -2353506; B.2 Z.23=7224830, Z.30=12280484, Z.33=5200000, Z.41=4199420; B.3 PB-level sum of Z.10=27042063 and Z.17=30255569 (computed independently from the 15 PB rows, matching `GESAMT` Z.10/17 exactly). Satzung values (27502063/30455569) present in `2026_sollwerte.toml` `[satzung]` and covered by Regel 4 (194 checked values, 0 deviations, live run). The two corrected Anhang-B.3 Sollwerte for PB 09/15 (`ergebnis_mit_internen_verrechnungen`: -115550→-133250, -118138→-190692) were independently re-verified against `raw_data/haushalt-2026.pdf` pages 296 and 299 (`GESAMTSUMME -133.250` for PB 09, `GESAMTSUMME -190.692` for PB 15 = PG 1501 -118.138 + PG 1502 -72.554) — the correction is legitimate; `discussion/SPEZIFIKATION.md` had transcribed the first Produktgruppe's row instead of the PB total. See "Code Review Findings" below for a narrower, already-flagged limitation in 2 of the 194 Regel-4 checks. |
| 5 | `uv run pytest` produces `daten/pruefberichte/konsistenz.md`; an undocumented >1€ deviation fails the run | ✓ VERIFIED | `uv run --directory pipeline pytest -q`: 129 passed. Live `alle.py` run regenerates `konsistenz.md` byte-identically (`git status --porcelain daten/` empty afterward). `test_konsistenzbericht_meldet_abweichung_ueber_einem_euro` (2€ injected deviation → Regel red, 1 finding) and `test_konsistenzbericht_toleriert_einen_euro` (1€ → stays grün) both pass, proving the >1€ gate is live, not just documented. `konsistenz.md` shows Veraltete Befunde: 0. |

**Score:** 5/5 roadmap Success Criteria verified.

### Plan-Level Must-Have Truths (02-01 through 02-05)

All 28 `must_haves.truths` entries across the five plan frontmatters were checked against the live codebase and the regenerated `daten/` output (not just read from SUMMARY.md). All verified. Representative spot-checks performed directly (not inferred from SUMMARY claims):

- `02_plaene_extrahieren.py` output format (33 Gesamtergebnisplan rows × 6 cols = 198 lines, `ebene=GESAMT`) — confirmed by direct CSV count.
- Operator/sign preservation (Z.17 positive, Z.27 negative with `-` operator, Z.09 `+/-`) — confirmed by direct row inspection (`pipeline/ostbevern/zeilen.py`, `pipeline/tests/test_plaene.py`).
- PlaeneFehler aborts on unknown row number / mismatched label / wrong value count — confirmed via `pytest.raises(PlaeneFehler, match=...)` tests in `test_plaene.py` (page+line cited in the exception message).
- `06_pruefen.py` and `pytest` call the same `pruefung.pruefe_alles` and write `konsistenz.md` byte-identically — confirmed by diffing a live regeneration against the committed file (`git status --porcelain daten/` empty).
- Teilergebnis/Teilfinanzplan page-splitting by section title (not `seiten.csv` typ), continuation-page joining — exercised by `pipeline/tests/test_plaene.py`'s teilplan tests (all green).
- Synthetic PG row derivation (sum of products, single-product PG = copy, lowest product's `pdf_seite`) — confirmed by `test_synthetische_pg_markierung_und_namen` in `test_hierarchie.py`.
- `alle.py` chains Schritt 01→02→06 in order and exits 1 on step failure or red report — confirmed by `test_alle.py`'s 4 monkeypatched order/failure tests, all passing, plus a live successful run.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| EXTR-01 | 02-01 | Zahlenparser (deutsches Format, Minus, „–", angeklebt, `C`) mit Unit-Tests | ✓ SATISFIED | `zahlen.py` + 21 passing unit tests in `test_zahlen.py`. **Note:** `.planning/REQUIREMENTS.md` line 20 still shows this requirement unchecked (`- [ ]`) while all nine sibling Phase-2 requirements are checked — this is a stale tracking checkbox, not a real gap (implementation and tests are substantive and green). Flagged as an info-level documentation discrepancy below. |
| EXTR-02 | 02-02 | `seiten.csv` mit Seite/Typ/PB/PG/Produkt, Fortsetzungsseiten, Anhang-A-Startseiten | ✓ SATISFIED | `seiten.csv` 400 rows; Anhang-A test in `test_hierarchie.py` green. |
| EXTR-03 | 02-02 | `hierarchie.csv`: 15 PB, alle PG (synthetisch markiert), 63 Produkte | ✓ SATISFIED | Confirmed via direct CSV parse: 15/48(40 synth)/63. |
| EXTR-04 | 02-01, 02-04 | Gesamtergebnisplan + alle Teilergebnispläne im Langformat | ✓ SATISFIED | `ergebnisplan.csv` has GESAMT/PB/PG/P rows with required columns. |
| EXTR-05 | 02-03, 02-04 | Gesamtfinanzplan + alle Teilfinanzpläne inkl. VE | ✓ SATISFIED | `finanzplan.csv` has `wertart=ve` rows (671) across all ebenen. |
| PRUEF-01 | 02-03, 02-04 | Zeilenformeln aller Pläne stimmen (Regel 1) | ✓ SATISFIED | Regel 1 grün, 6550 Werte, live run. |
| PRUEF-02 | 02-05 | Produkt-Teilpläne = PG = PB-Teilplan (Regel 2) | ✓ SATISFIED | Regel 2 grün, 7920 Werte, live run; manipulation test proves detection. |
| PRUEF-03 | 02-05 | 15 PB = Gesamtergebnisplan (Regel 3) | ✓ SATISFIED | Regel 3 grün, 114 Werte, live run; manipulation test proves detection. |
| PRUEF-04 | 02-01, 02-03, 02-05 | Anhang-B-Sollwerte getroffen (Regel 4) | ✓ SATISFIED | Regel 4 grün, 194 Werte, 0 Abweichungen, live run; B.1/B.2/B.3/Satzung figures independently spot-checked. |
| PRUEF-09 | 02-01, 02-03, 02-05 | Alle Prüfungen in pytest, `konsistenz.md`, >1€-Gate | ✓ SATISFIED | 129/129 pytest green; >1€ gate proven live with injected-deviation tests. |

No orphaned requirements: all 10 IDs declared in ROADMAP.md for Phase 2 appear in at least one plan's `requirements` field and are addressed above.

### Determinism / Reproducibility

```
$ uv run --directory pipeline python alle.py --jahr 2026
Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.
Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 48 PG (40 synthetisch), 63 Produkte.
Schritt 02: 14825 Planzeilen geschrieben.
Schritt 06: Regel 1: grün (6550 Werte)
Schritt 06: Regel 2: grün (7920 Werte)
Schritt 06: Regel 3: grün (114 Werte)
Schritt 06: Regel 4: grün (194 Werte)
Schritt 06: Veraltete Befunde: 0

$ git status --porcelain daten/
(empty)
```

### Befunde.md Spot-Checks (independent PDF verification)

Two of the ten documented rounding differences were independently re-extracted from `raw_data/haushalt-2026.pdf` with a fresh `pdfplumber` read (not trusting the befunde.md prose):

- PB 08 Z.17 2024: PDF page 203 and 206 both print `186.499`; sum of printed Zeilen 11,13-16 = 11.654+92.684+60.162+20.136+1.865 = **186.501** → 2€ rounding difference, confirmed exactly as documented.
- PB 01 Z.29/Z.09 2024: PDF page 66 prints Z.29 `-2.556.326` and Z.09 (Teilfinanzplan) `859.878`, matching the befunde.md table's cited printed values exactly.

Both spot-checks confirm the documented differences are genuinely printed in the PDF (not extraction bugs masked as "known findings").

### Anhang-B.3 Sollwerte Correction (orchestrator-flagged item)

Independently confirmed via direct `pdfplumber` read of PDF pages 296 and 299:
- PB 09 Haushaltsquerschnitt GESAMTSUMME = **-133.250** (matches corrected sollwert, not the old -115.550 which was PG 0901's row only)
- PB 15 Haushaltsquerschnitt GESAMTSUMME = **-190.692** = PG 1501 (-118.138) + PG 1502 (-72.554) (matches corrected sollwert, not the old -118.138 which was PG 1501's row only)

The correction is legitimate: `discussion/SPEZIFIKATION.md` Anhang B.3 had transcribed the first Produktgruppe's figure instead of the Produktbereich total for these two PBs. The roadmap SC4 headline figures (B.3 PB-sum totals 27.042.063 €/30.255.569 €) are unaffected by and independent of this correction — they match the `GESAMT` Z.10/Z.17 figures exactly, both before and after.

### PG 1501/1502 Open Question (orchestrator-flagged item)

**Assessment: does not conflict with Success Criterion 1.** SC1 requires "alle PG (synthetische mit `synthetisch=true`)" matching Anhang A — Anhang A (`2026_sollwerte.toml`) lists only product-level entries `150101`/`150102` under PB 15, with no separate 4-digit PG code for "1502". The pipeline's rule (PG code = first 4 digits of product code) therefore correctly derives a single synthetic PG `1501` covering both products, consistent with Anhang A as the authoritative source (per project convention) and with all 62 other products' derivation passing the same test. The Haushaltsquerschnitt pages (S. 299/300) separately labelling "1502 Tourismus" is a cross-reference question for Regel 7 (Querschnitte vs. PG-Aggregate), which is explicitly in Phase 3's scope (`ROADMAP.md` Phase 3 SC4: "Die Querschnitte ab S. 291 stimmen mit den eigenen PG-Aggregaten überein (Regel 7)"). The ambiguity is transparently documented in `daten/pruefberichte/befunde.md`'s "Beobachtungen ohne Prüfregel" section with an explicit call-out that it must be resolved before Phase 3's Regel 7. **Deferred, not a Phase 2 gap.**

### Code Review Findings (02-REVIEW.md, disposition: all open)

0 critical, 3 warning, 2 info — none block Phase 2 goal achievement; all are documentation-accuracy or defensive-coding gaps in otherwise-correct, green code:

| ID | Severity | Summary | Why non-blocking |
|---|---|---|---|
| WR-01 | warning | `befunde.md` header states the Regel-1 `abweichung` sign formula backwards (prose only; the code and the actual tabulated values are correct) | Documentation-only; no incorrect number is produced or displayed |
| WR-02 | warning | 2 of 194 Regel-4-B.3 checks (PB 09/15 Zeile 29) compare a hand-derived sollwert against the pipeline's own formula chain, rather than an independently PDF-sourced figure, because Anhang B itself has the documented typo for these two PBs | Narrow (2/194 values), explicitly reasoned and documented in the sollwerte TOML comment and the review; the roadmap SC4 headline B.3 figures (PB-sum totals) are unaffected and were independently re-verified against the PDF in this report |
| WR-03 | warning | `_pruefe_regel4_b1` could raise a bare `IndexError` instead of `PruefungsFehler` if `jahre`/`spalten` ever go out of sync (not triggered by any current data) | Defensive-coding gap for a hypothetical future jahrgang mismatch; does not affect 2026 data correctness |
| IN-01 | info | Comment on `REGEL3_ZEILEN` only names a subset of excluded lines | Cosmetic |
| IN-02 | info | `lies_befunde`'s table parser has no guard against `|` inside free text | Fails loudly if ever triggered; no current data triggers it |

These are legitimate, already-surfaced findings that should be addressed as follow-up work (tracked in `02-REVIEW-DISPOSITION.md`, all `open`), not reasons to re-open Phase 2.

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`), no empty/stub implementations, no hardcoded-empty data flowing to output were found in any `pipeline/ostbevern/*.py` or `pipeline/*.py` file. `ruff check .` and `ruff format --check .` both pass clean.

### Documentation Discrepancy (info, non-blocking)

`.planning/REQUIREMENTS.md` line 20 shows EXTR-01 as `- [ ]` (Pending) while the other nine Phase-2 requirement rows show `- [x]` (Complete). This is inconsistent with the actual state (EXTR-01 is fully implemented and tested — see Requirements Coverage above) and should be corrected to `- [x]` as a documentation housekeeping item; it does not reflect a real implementation gap.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full pipeline run succeeds and is deterministic | `uv run --directory pipeline python alle.py --jahr 2026` then `git status --porcelain daten/` | exit 0, empty diff | ✓ PASS |
| Full test suite green | `uv run --directory pipeline pytest -q` | 129 passed | ✓ PASS |
| Lint/format clean (CI parity) | `uv run --directory pipeline ruff check .` / `ruff format --check .` | clean | ✓ PASS |
| 2€ injected deviation turns Regel 4 red | `pytest -k abweichung_ueber_einem_euro` | 1 deviation reported, regel4.status == "rot" | ✓ PASS |
| 1€ injected deviation stays green | `pytest -k toleriert_einen_euro` | regel4.status == "grün" | ✓ PASS |
| Manipulated product-level row caught at the correct hierarchy level | `pytest -k manipul` | 2/2 passed | ✓ PASS |

### Human Verification Required

None. This is a deterministic, headless Python pipeline with comprehensive automated test coverage; all observable truths were verified programmatically.

### Gaps Summary

No gaps found. All five roadmap Success Criteria, all 28 plan-level must-have truths, and all 10 declared requirement IDs are verified against the live codebase and a fresh pipeline run, not just SUMMARY.md claims. The orchestrator's three flagged items (Sollwerte correction, befunde.md spot-checks, PG 1501/1502 question) were each independently investigated and confirmed non-blocking.

---

_Verified: 2026-10-01T15:31:01Z_
_Verifier: Claude (gsd-verifier)_
