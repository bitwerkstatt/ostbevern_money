---
phase: quick-261001-oim
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/seiten.py
  - pipeline/ostbevern/plaene.py
  - pipeline/tests/test_hierarchie.py
  - pipeline/tests/test_seiten.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_konfiguration.py
  - daten/zwischen/seiten.csv
  - daten/aufbereitet/hierarchie.csv
  - daten/aufbereitet/ergebnisplan.csv
  - daten/aufbereitet/finanzplan.csv
  - daten/pruefberichte/konsistenz.md
  - daten/pruefberichte/befunde.md
autonomous: true
requirements: [EXTR-03, EXTR-04, EXTR-05, PRUEF-02]

estimate:
  tokens: 65000
  raw_tokens: 65000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "Per D-14 every synthetic PG in daten/aufbereitet/hierarchie.csv has exactly one P child (via eltern_code). Its code is the product's first four digits unless pipeline/jahrgaenge/2026.toml declares the assignment under [synthetische_produktgruppen]"
    - "PG 1501 (synthetic, Wirtschaftsförderung, pdf_seite_start 273) has exactly one child, 150101. PG 1502 (synthetic, name Tourismus, pdf_seite_start 276) has exactly one child, 150102, and 150102's eltern_code is 1502"
    - "ergebnisplan.csv: PG 1501 Z. 29 Ansatz 2026 = -118138 and PG 1502 Z. 29 Ansatz 2026 = -72554, matching Haushaltsquerschnitt S. 299. The expected values in the test come from 2026_sollwerte.toml"
    - "Synthetic PG rows in ergebnisplan.csv and finanzplan.csv are exact copies of their single product's rows with ebene=PG and synthetisch=true (D-14). They are not sums"
    - "In seiten.csv, the pages of product 150102 carry pg=1502"
    - "Fail-loud handling (D-08): a malformed [synthetische_produktgruppen] or [haushaltsquerschnitt_pg] entry raises KonfigurationsFehler. An override for an unknown product, for a product inside a printed PG, or onto a printed PG code raises SeitenFehler. So do two products that resolve to the same synthetic PG code"
    - "uv run --directory pipeline python alle.py --jahr 2026 exits 0 (Prüfregeln 1-4 grün, no veraltete Befunde), and a second run leaves daten/ byte-identical"
    - "befunde.md no longer contains the open PG question about product 150102. All 10 Schlüsseltabelle rows are unchanged"
  artifacts:
    - path: "pipeline/jahrgaenge/2026.toml"
      provides: "[synthetische_produktgruppen.\"1502\"] with produkt, name and pdf_seite (source: Haushaltsquerschnitt S. 299/300)"
      contains: "synthetische_produktgruppen"
    - path: "pipeline/jahrgaenge/2026_sollwerte.toml"
      provides: "[haushaltsquerschnitt_pg] with the S. 299 Ergebnis values for PG 1501 and 1502"
      contains: "haushaltsquerschnitt_pg"
    - path: "pipeline/ostbevern/konfiguration.py"
      provides: "SynthetischeProduktgruppe dataclass and the Jahrgang.synthetische_produktgruppen field, parsed and validated in lade_jahrgang. Also validation of the optional sollwerte section in lade_sollwerte"
      contains: "SynthetischeProduktgruppe"
    - path: "pipeline/ostbevern/seiten.py"
      provides: "produktgruppe_fuer_produkt helper, used by klassifiziere_dokument and baue_hierarchie. Rule: one product per synthetic PG"
      contains: "produktgruppe_fuer_produkt"
    - path: "pipeline/ostbevern/plaene.py"
      provides: "_synthetische_pg_datensaetze copies the single child product found via hierarchie eltern_code"
    - path: "daten/aufbereitet/hierarchie.csv"
      provides: "49 PG rows, 41 of them synthetic, including PG,1502,Tourismus,15,276,true"
  key_links:
    - from: "pipeline/jahrgaenge/2026.toml [synthetische_produktgruppen]"
      to: "ostbevern.seiten.produktgruppe_fuer_produkt"
      via: "lade_jahrgang -> Jahrgang.synthetische_produktgruppen"
      pattern: "synthetische_produktgruppen"
    - from: "hierarchie.csv eltern_code"
      to: "plaene._synthetische_pg_datensaetze and pruefung Regel 2"
      via: "single source of truth for P->PG membership. No consumer re-derives membership from a code prefix"
      pattern: "eltern_code"
    - from: "2026_sollwerte.toml [haushaltsquerschnitt_pg]"
      to: "pipeline/tests/test_hierarchie.py"
      via: "lade_sollwerte (no Sollwert literals in tests)"
      pattern: "haushaltsquerschnitt_pg"
---

<objective>
Fix how synthetic Produktgruppen are assigned so that every synthetic PG holds exactly one product (D-14). Product 150102 (Touristische Öffentlichkeitsarbeit, S. 276) moves out of PG 1501 into its own synthetic PG 1502 "Tourismus", matching Haushaltsquerschnitt S. 299 (Ergebnisplan) and S. 300 (Finanzplan).

Purpose: today PG 1501 is the sum of 150101 and 150102 (Z. 29 2026 = -190692), but the PDF prints PG 1501 = -118.138 and PG 1502 = -72.554. Every number has to be correct for Bürgerinformation, and Phase 3 Regel 7 (Querschnitte, PRUEF-07) needs the PG split the PDF prints.

Output: the general rule in seiten.py and plaene.py, a Jahrgang config section with loader validation, a Querschnitt Sollwert section, new and updated tests (RED then GREEN), regenerated daten/, and a cleaned-up befunde.md.
</objective>

<decision_reconciliation>
READ BEFORE TASK 1. The locked user decisions contain one internal contradiction, resolved as follows.

- The first four digits of the product code "150102" are "1501". A purely digit-based rule can never place 150102 in PG 1502, and "child code starts with the PG code" can never hold for PG 1502. The PDF's Teilplanbereich (S. 66-282) prints no PG 1502 header. Only the Haushaltsquerschnitt (S. 299/300) shows the 1502 grouping.
- Resolution, which keeps the user's required result (1501 has only 150101, 1502 "Tourismus" has only 150102) and the no-year-values-in-code rule:
  1. The D-14 default stays the general rule: synthetic PG code = the product's first four digits, name = product name, pdf_seite_start = product start page.
  2. Also general: a synthetic PG has EXACTLY ONE product. Two products that resolve to the same synthetic code are an error (SeitenFehler). They are never summed silently. This replaces the current merging behaviour.
  3. Assignments the digits cannot express are declared in pipeline/jahrgaenge/2026.toml under [synthetische_produktgruppen], keyed by PG code. Each entry has `produkt` (the one product), `name` (the PG name) and `pdf_seite` (the page that is the source of the assignment and name, here S. 299). This extends the user's suggested "code -> name + pdf_seite" section by `produkt`, because the code cannot be derived otherwise. An entry also works as a plain name override when its key equals the product's four-digit prefix.
  4. The "child code starts with PG code" test applies to every synthetic PG NOT declared in the config. For declared PGs the test asserts child == declared produkt, and that child and PG share the PB prefix.
- pdf_seite_start of PG 1502 in hierarchie.csv = 276 (product start page, per D-14). The name source page 299 is stored only in the config entry. D-15 (names come from page headers) gets a declared exception: the name "Tourismus" comes from the Querschnitt, as decided by the user.
- The executor must NOT edit .planning/STATE.md or .planning/PROJECT.md. The orchestrator updates the STATE blocker and the PROJECT.md Key Decision row afterwards.
</decision_reconciliation>

<execution_context>
@/Users/thma/repos/bitwerkstatt/ostbevern_money/.claude/gsd-core/workflows/execute-plan.md
@/Users/thma/repos/bitwerkstatt/ostbevern_money/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.claude/CLAUDE.md
@.planning/phases/02-kernzahlen/02-CONTEXT.md
@.planning/phases/02-kernzahlen/02-04-SUMMARY.md

Facts verified at planning time (live observation, 2026-10-01):
- hierarchie.csv currently has 48 PG rows (8 printed, 40 synthetic). Only PG 1501 has two children (150101 at S. 273, 150102 at S. 276). All 63 products currently have eltern_code = their four-digit prefix.
- Current ergebnisplan.csv Z. 29 2026 ansatz values: P 150101 = -118138 (pdf_seite 274), P 150102 = -72554 (pdf_seite 277), PG 1501 = -190692.
- S. 299 columns: Ordentliche Erträge, Ordentliche Aufwendungen, Ordentliches Ergebnis, Finanzergebnis, Ergebnis der lfd. Verwaltungstätigkeit, Außerordentliches Ergebnis, Ergebnis des Teilhaushaltes. Rows: "1501 Wirtschaftsförderung ... -118.138", "1502 Tourismus ... -72.554", "GESAMTSUMME ... -190.692". S. 300 prints 1501 and 1502 separately as well.
- lade_jahrgang and lade_sollwerte ignore unknown top-level TOML sections today. Adding the new sections to the TOML files before the loader change is therefore harmless.
- pruefung.py Regel 2 already finds children through hierarchie eltern_code, and pruefung.py has no prefix-based PG logic. The only prefix-based membership code is in seiten.py (klassifiziere_dokument, baue_hierarchie) and plaene.py (_synthetische_pg_datensaetze).
- Code that encodes the old rule and must change: tests/test_hierarchie.py (ebenenzahlen, markierung_und_namen, eltern_code_je_ebene, the summation test), tests/test_seiten.py::test_produktseiten_tragen_pg_aus_produktcode, and tests/test_pruefung.py::test_regel1_sollwerte_gesamtplaene_gruen (hardcoded count 6550).
- alle.py exits 1 on KonfigurationsFehler, SeitenFehler, PlaeneFehler, a red Prüfbericht or veraltete Befunde.
- befunde.md Schlüsseltabelle has 10 rows (none of them touches PB 15).
- The working tree has unrelated untracked .claude/ files and a modified .planning/config.json. Stage ONLY the paths named in each task (project convention). Never use `git add -A` or `git add .`.

Conventions (from .claude/CLAUDE.md and the test module docstrings): German identifiers without umlauts. German docstrings and comments. No year-specific values in code, read only via lade_jahrgang and lade_sollwerte. Tests contain no Jahrgang, page or Sollwert literals; expected values come from the loaders. Fabricated codes such as PB "99" are acceptable in constructed fixtures (precedent: test_pruefung.py). Tests on checked-in data read daten/ only, never the PDF (D-06). ruff line length 100.
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: Tracer, from the config declaration to hierarchie.csv and both plan CSVs: one product per synthetic PG, PG 1502 "Tourismus"</name>
  <files>pipeline/jahrgaenge/2026.toml, pipeline/jahrgaenge/2026_sollwerte.toml, pipeline/tests/test_hierarchie.py, pipeline/ostbevern/konfiguration.py, pipeline/ostbevern/seiten.py, pipeline/ostbevern/plaene.py (generated by alle.py: daten/zwischen/seiten.csv, daten/aufbereitet/hierarchie.csv, daten/aufbereitet/ergebnisplan.csv, daten/aufbereitet/finanzplan.csv, daten/pruefberichte/konsistenz.md)</files>
  <read_first>pipeline/ostbevern/seiten.py (klassifiziere_dokument, baue_hierarchie, _aktualisiere_knoten), pipeline/ostbevern/plaene.py (_synthetische_pg_datensaetze, extrahiere_plaene), pipeline/ostbevern/konfiguration.py (Jahrgang, lade_jahrgang), pipeline/tests/test_hierarchie.py, pipeline/jahrgaenge/2026.toml, pipeline/jahrgaenge/2026_sollwerte.toml (comment above [teilergebnisplaene_pb], field name ergebnis_mit_internen_verrechnungen)</read_first>
  <behavior>
    - Every synthetic PG in the checked-in hierarchie.csv has exactly one P child (rows with ebene=P and eltern_code = PG code). If the PG is not declared in jahrgang.synthetische_produktgruppen, the child's code starts with the PG code. If it is declared, the child equals the declared produkt. In both cases child and PG share the two-digit PB prefix, and the PG's eltern_code is that PB.
    - For each declared entry (code, eintrag) in lade_jahrgang(STANDARD_JAHR).synthetische_produktgruppen (the test also asserts this mapping is non-empty for STANDARD_JAHR): hierarchie has a PG row with that code, synthetisch=true and name == eintrag.name.
    - Name and pdf_seite_start of every synthetic PG: name = declared name if declared, otherwise the child product's name (D-14). pdf_seite_start = the child product's pdf_seite_start (D-14), which equals anhang_a[child]["pdf_seite"].
    - eltern_code of every P row = the declared PG code if the product is declared in some entry, otherwise the product's first four digits.
    - The PG code set equals the printed PG codes (four-digit keys in anhang_a) plus, for every product, its resolved PG code (declared or four-digit prefix). The test computes this on its own and does not call the production helper.
    - In ergebnisplan.csv and finanzplan.csv, the rows of every synthetic PG are an exact copy of its single child's rows: the same set of (zeile, zeile_kanonisch, zeile_name, operator, ist_summe, jahr, wertart, betrag, pdf_seite), with ebene=PG, code=PG code and synthetisch=true. This replaces the old test that asserted a synthetic PG equals the SUM of all products sharing its prefix. Delete that old test.
    - For each code in lade_sollwerte(STANDARD_JAHR)["haushaltsquerschnitt_pg"]: the ergebnisplan.csv row with ebene=PG, that code, zeile_kanonisch "ergebnis_mit_internen_verrechnungen" (the sollwerte field name equals the kanonisch key) and the Ansatz column of jahrgang.haushaltsjahr has betrag == the Sollwert. Derive the (wertart, jahr) pair the same way the existing B.3 / Regel 4 tests do (zerlege_spaltenkopf on jahrgang.spalten["ergebnisplan"]). Also assert that every declared synthetic PG code appears in haushaltsquerschnitt_pg, so each declared assignment is backed by a Querschnitt Sollwert.
  </behavior>
  <action>
RED (commit 1). In pipeline/jahrgaenge/2026.toml, add a new section `[synthetische_produktgruppen."1502"]` with keys produkt = "150102", name = "Tourismus", pdf_seite = 299. Above it, write a German comment covering these points: the D-14 default is code = first four digits of the product code and name = product name. The section declares only the synthetic PG assignments and names that deviate from that default. Each synthetic PG holds exactly one product. The source is the Haushaltsquerschnitt (S. 299 Ergebnisplan, S. 300 Finanzplan), which lists product 150102 as its own PG 1502 "Tourismus", while the Teilplanbereich prints no PG 1502 header. pdf_seite is the source page of assignment and name. In hierarchie.csv the PG keeps its product's start page as pdf_seite_start (D-14).

In pipeline/jahrgaenge/2026_sollwerte.toml, add a section `[haushaltsquerschnitt_pg]` with "1501" = { ergebnis_mit_internen_verrechnungen = -118138, pdf_seite = 299 } and "1502" = { ergebnis_mit_internen_verrechnungen = -72554, pdf_seite = 299 }. Add a German comment: Haushaltsquerschnitt Ergebnisplan S. 299, column "Ergebnis des Teilhaushaltes", Ansatz of the Haushaltsjahr, equals TP Z. 29 of the PG (no internal allocations or Minderaufwand in PB 15). It documents the D-14 split 1501/1502.

Rewrite pipeline/tests/test_hierarchie.py per <behavior>. Update the module docstring: no literal PG counts, and describe the copy semantics. Keep test_anhang_a_eintraege_stimmen_mit_hierarchie_ueberein, test_produktseiten_in_seiten_csv_stimmen_mit_anhang_a and test_jeder_knoten_hat_ergebnis_und_finanzplanzeilen unchanged. Run `uv run --directory pipeline pytest tests/test_hierarchie.py -q`. It MUST fail: PG 1501 has two children, PG 1501 Z. 29 = -190692, PG 1502 is missing, and the Jahrgang attribute does not exist yet. Commit only these three files: `test(261001-oim): failing tests for one product per synthetic PG (D-14) and PG 1502`.

GREEN (commit 2). konfiguration.py: add a frozen dataclass SynthetischeProduktgruppe(code: str, produkt: str, name: str, pdf_seite: int) and a required Jahrgang field synthetische_produktgruppen: Mapping[str, SynthetischeProduktgruppe]. lade_jahrgang is the only construction site. It parses the optional top-level table and uses an empty dict when the table is absent. Task 1 needs only the happy-path parse. Full validation follows in Task 3.

seiten.py: add a public helper produktgruppe_fuer_produkt(produkt_code, jahrgang) -> str. It returns the code of the entry whose produkt equals produkt_code, otherwise the D-14 default (the product code's first four digits). klassifiziere_dokument uses the helper for the `pg` of product pages instead of the inline prefix. baue_hierarchie uses it for the P node's eltern_code instead of the inline prefix. Then replace the synthetic-PG block in baue_hierarchie (the comment and code that collect several products per prefix, take the name from the lowest-coded product and the minimum start page) with the general rule. Iterate products in ascending code order. Skip a product whose resolved PG code is a printed PG. Otherwise register the product as the single child of its resolved synthetic code. If that code already has a child, raise SeitenFehler naming the PG code and both product codes, and hint that the deviating assignment must be declared in [synthetische_produktgruppen] of the Jahrgangsdatei (D-14 "genau ein Produkt", D-08). Synthetic PG node: name = declared name if the code is declared, otherwise the product name. pdf_seite_start = the product's pdf_seite_start. eltern_code = the product's PB. Rewrite the explanatory German comment accordingly.

plaene.py: rewrite _synthetische_pg_datensaetze so it determines each synthetic PG's child from hierarchie (P rows whose eltern_code equals the PG code). Do NOT re-derive membership from a code prefix. Raise PlaeneFehler if a synthetic PG has a child count other than 1, or if the child has no rows in teil_df (D-08). Emit an exact copy of each child row (all PLAN_SPALTEN values) with ebene="PG", code=PG code and synthetisch=True, without any summation. The return shape stays a list of dicts consumed by extrahiere_plaene. Update the docstring (copy semantics per D-14, membership via eltern_code).

Regenerate with `uv run --directory pipeline python alle.py --jahr 2026` (must exit 0, Prüfregeln grün). Then run `uv run --directory pipeline pytest tests/test_hierarchie.py -q` (must pass). Two OTHER tests are expected to fail after this task and are fixed in Task 2: tests/test_seiten.py::test_produktseiten_tragen_pg_aus_produktcode and tests/test_pruefung.py::test_regel1_sollwerte_gesamtplaene_gruen (count). Any other failing test is a Task 1 defect and must be fixed here. Run `uv run --directory pipeline ruff check .` and `uv run --directory pipeline ruff format .`. Commit only konfiguration.py, seiten.py, plaene.py and the five regenerated daten/ files: `fix(261001-oim): one product per synthetic PG, PG 1502 Tourismus from Jahrgangsdatei (D-14)`.
  </action>
  <verify>
    <automated>uv run --directory pipeline python alle.py --jahr 2026 && uv run --directory pipeline pytest tests/test_hierarchie.py -q && grep -qx 'PG,1502,Tourismus,15,276,true' daten/aufbereitet/hierarchie.csv && grep -qx 'P,150102,Touristische Öffentlichkeitsarbeit,1502,276,false' daten/aufbereitet/hierarchie.csv && grep -qx 'PG,1501,Wirtschaftsförderung,15,273,true' daten/aufbereitet/hierarchie.csv && grep -q '^PG,1501,true,29,.*,2026,ansatz,-118138,' daten/aufbereitet/ergebnisplan.csv && grep -q '^PG,1502,true,29,.*,2026,ansatz,-72554,' daten/aufbereitet/ergebnisplan.csv</automated>
  </verify>
  <acceptance_criteria>
    - The git log shows a test(261001-oim) commit before the fix(261001-oim) commit. The RED run of tests/test_hierarchie.py failed before the implementation.
    - The alle.py Schritt 01 line reports the new PG totals: `uv run --directory pipeline python alle.py --jahr 2026 | grep -q '49 PG (41 synthetisch)'` succeeds.
    - `grep -q ',15,1502,150102$' daten/zwischen/seiten.csv` succeeds and `! grep -q ',15,1501,150102$' daten/zwischen/seiten.csv` succeeds.
    - `grep -q '^PG,1502,true,' daten/aufbereitet/finanzplan.csv` succeeds.
    - Non-comment code in pipeline/ostbevern/plaene.py has no prefix slicing on product codes: `! (grep -v '^\s*#' pipeline/ostbevern/plaene.py | grep -q '\[:4\]')` succeeds.
    - `grep -n 'produktgruppe_fuer_produkt' pipeline/ostbevern/seiten.py` shows the definition plus one use inside klassifiziere_dokument and one inside baue_hierarchie.
    - `! grep -q 'summieren_ihre_produkte' pipeline/tests/test_hierarchie.py` succeeds.
    - daten/pruefberichte/konsistenz.md shows `Gesamtstatus: grün`.
  </acceptance_criteria>
  <done>alle.py regenerates hierarchie.csv with PG 1501 holding only 150101 and PG 1502 "Tourismus" holding only 150102. The synthetic PG rows are exact product copies, PG 1501/1502 Z. 29 2026 = -118138 / -72554, Prüfregeln grün, and the RED/GREEN commit pair is in place.</done>
</task>

<task type="auto">
  <name>Task 2: Update the existing tests that encode the old rule, and remove the resolved open question from befunde.md</name>
  <files>pipeline/tests/test_seiten.py, pipeline/tests/test_pruefung.py, daten/pruefberichte/befunde.md</files>
  <read_first>pipeline/tests/test_seiten.py (test_produktseiten_tragen_pg_aus_produktcode, fixtures), pipeline/tests/test_pruefung.py (test_regel1_sollwerte_gesamtplaene_gruen and its comment), daten/pruefberichte/befunde.md (section "Beobachtungen ohne Prüfregel")</read_first>
  <action>
test_seiten.py: change test_produktseiten_tragen_pg_aus_produktcode so the expected pg of a product page is the declared PG code when jahrgang.synthetische_produktgruppen has an entry whose produkt equals the page's product, and the product's four-digit prefix otherwise. Compute this inline from the jahrgang fixture, not via the production helper, so the test stays independent. Update the test name and docstring if helpful (for example "pg aus Produktcode oder Jahrgangsdeklaration"). Do not weaken the assertion for undeclared products.

test_pruefung.py: in test_regel1_sollwerte_gesamtplaene_gruen, replace the hardcoded Regel-1 count with the new value from `uv run --directory pipeline python alle.py --jahr 2026` (Schritt 06 line for Regel 1, also in konsistenz.md). The delta against the old value must equal the number of Teilplan formula cells (zeile x column, printed rows only) that products 150101 and 150102 BOTH print. Before, the union was counted once for the merged PG; now PG 1501 and PG 1502 are each counted. Verify that equality against the regenerated ergebnisplan.csv and finanzplan.csv, and extend the German comment with this derivation. If the delta does not match, stop and investigate rather than adjusting the number.

befunde.md: delete only the last bullet of the section "Beobachtungen ohne Prüfregel", the open question about product 150102, synthetic PG 1501 and the separate Querschnitt listing before Regel 7. Leave the other two bullets, the header text and all 10 Schlüsseltabelle rows unchanged (D-02, D-04, D-05).

Run the full suite, then regenerate and confirm determinism against Task 1's committed data. Commit only these three files: `test(261001-oim): adapt seiten/pruefung tests to D-14 one-product rule, drop resolved PG observation`.
  </action>
  <verify>
    <automated>uv run --directory pipeline pytest -q && uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten/zwischen daten/aufbereitet daten/pruefberichte/konsistenz.md && basis=$(git show 93848a8d5c577f7643b031d3ade06e2b55e3b163:daten/pruefberichte/befunde.md) && diff <(printf '%s\n' "$basis" | grep '^| [123] |') <(grep '^| [123] |' daten/pruefberichte/befunde.md) && ! grep -q 'Haushaltsquerschnitt-Seiten 299/300' daten/pruefberichte/befunde.md</automated>
  </verify>
  <acceptance_criteria>
    - The full pipeline pytest suite passes.
    - Regenerating after the Task 1 commit leaves daten/zwischen, daten/aufbereitet and konsistenz.md byte-identical.
    - The Schlüsseltabelle rows of befunde.md are identical to those at the plan base commit 93848a8d5c577f7643b031d3ade06e2b55e3b163 (the diff in verify is empty), and the resolved PG observation is gone.
    - The new Regel-1 count in test_pruefung.py equals the number alle.py reports, and its comment explains the delta as the 150101/150102 formula-cell overlap.
  </acceptance_criteria>
  <done>The full suite is green with the new rule, Regel-1 count updated with a derivation, and befunde.md cleaned up with every Schlüsseltabelle row kept.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Fail-loud validation for config declarations and hierarchy assignment (D-08), then the final CI and determinism gate</name>
  <files>pipeline/tests/test_konfiguration.py, pipeline/tests/test_seiten.py, pipeline/ostbevern/konfiguration.py, pipeline/ostbevern/seiten.py</files>
  <read_first>pipeline/tests/test_konfiguration.py (helpers _jahrgangsdatei_text, _schreibe_jahrgangsdatei, _sollwertdatei_text, _schreibe_sollwertdatei and the regex-mutation style of existing negative tests), pipeline/ostbevern/konfiguration.py (anhang_a validation pattern in lade_sollwerte), pipeline/ostbevern/seiten.py (Seite, Seitenkopf, baue_hierarchie as changed in Task 1)</read_first>
  <behavior>
    - Positive: lade_jahrgang(STANDARD_JAHR).synthetische_produktgruppen is non-empty. Every entry is a SynthetischeProduktgruppe with a four-digit code equal to its key, a six-digit produkt sharing the code's PB prefix, a non-empty name and 1 <= pdf_seite <= anzahlen.pdf_seiten. A Jahrgangsdatei text with the whole [synthetische_produktgruppen] table removed loads with an empty mapping.
    - Each of these mutations of the real 2026.toml text (written to tmp_path) raises KonfigurationsFehler with a message naming synthetische_produktgruppen: a key that is not four digits; an entry missing produkt; an entry with an unknown extra key; a produkt that is not six digits; a produkt whose PB prefix differs from the code's; an empty name; pdf_seite 0 or beyond anzahlen.pdf_seiten, or a bool; the same produkt declared under two codes; a non-table value for the section.
    - Each of these mutations of the real 2026_sollwerte.toml text raises KonfigurationsFehler naming haushaltsquerschnitt_pg: a key that is not four digits; an entry missing ergebnis_mit_internen_verrechnungen; an invalid pdf_seite. The section stays optional. Non-int values are already rejected by the existing integer check.
    - baue_hierarchie with constructed inputs (fabricated PB "99", Seite and Seitenkopf objects, no PDF, page numbers derived from jahrgang.seitenbereiche["teilplaene"].von plus offsets, jahrgang via dataclasses.replace with matching anzahlen and a custom synthetische_produktgruppen mapping) raises SeitenFehler in each of these cases. (a) Two products resolve to the same synthetic code without a declaration; the message names both products. This characterizes the Task 1 rule and may pass on first run. (b) A declaration whose produkt does not exist. (c) A declaration whose produkt belongs to a printed PG. (d) A declaration whose code equals a printed PG code. With a valid declaration it returns the declared PG with the declared name and the product's start page.
  </behavior>
  <action>
RED (commit 1). Add the tests from <behavior>: the loader tests to pipeline/tests/test_konfiguration.py, following the existing pattern (read the real file text, mutate it by regex or str.replace, write to tmp_path, pytest.raises(KonfigurationsFehler, match=...)). Add the constructed baue_hierarchie tests to pipeline/tests/test_seiten.py. These must not use the module-scoped PDF fixtures, so they run without reading the PDF. Run `uv run --directory pipeline pytest tests/test_konfiguration.py tests/test_seiten.py -q`. The negative loader tests and cases (b)-(d) MUST fail. Commit only the two test files: `test(261001-oim): failing validation tests for synthetic PG declarations`.

GREEN (commit 2). konfiguration.py, lade_jahrgang: validate the optional [synthetische_produktgruppen] table fully per <behavior>. Use the exact allowed key set {produkt, name, pdf_seite} with missing and unknown keys reported, module-level compiled regex constants next to the existing _ANHANG_A_CODE_MUSTER style, a duplicate-produkt check across entries, and the pdf_seite range from anzahlen.pdf_seiten. Raise KonfigurationsFehler with the file path and the offending key, in German, matching the existing message style.

konfiguration.py, lade_sollwerte: validate the optional [haushaltsquerschnitt_pg] table (four-digit keys, required ergebnis_mit_internen_verrechnungen, pdf_seite an int >= 1 and not a bool, matching the anhang_a pdf_seite check). Do NOT add it to the required top-level keys and do NOT wire it into Regel 4. Querschnitt checks belong to Phase 3 Regel 7 (PRUEF-07).

seiten.py, baue_hierarchie: after the existing PB and product count checks, validate every declaration against the extracted nodes. The produkt must exist among the P nodes. Its four-digit prefix must not be a printed PG. The declared code must not be a printed PG code. Each failure raises SeitenFehler naming the PG code, the produkt and the Jahrgangsdatei section [synthetische_produktgruppen], so an override that would not end up as a synthetic PG fails loudly (D-08). alle.py already turns KonfigurationsFehler and SeitenFehler into exit 1. Keep the Task 1 collision check.

Run ruff check, ruff format and the full CI line. Regenerate and confirm daten/ is unchanged: validation must not alter any output, and regeneration must be deterministic (D-21). Commit only konfiguration.py and seiten.py: `fix(261001-oim): validate synthetic PG declarations and fail loudly (D-08)`. Do NOT edit .planning/STATE.md or .planning/PROJECT.md.
  </action>
  <verify>
    <automated>(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest) && uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten/</automated>
  </verify>
  <acceptance_criteria>
    - The git log shows a test(261001-oim) commit for the validation tests before the fix(261001-oim) validation commit. The RED run failed for the negative loader tests and baue_hierarchie cases (b)-(d).
    - `grep -q 'synthetische_produktgruppen' pipeline/ostbevern/konfiguration.py` and `grep -q 'haushaltsquerschnitt_pg' pipeline/ostbevern/konfiguration.py` both succeed.
    - The full CI line from the repo root passes (ruff check, ruff format --check, pytest).
    - After a fresh `alle.py --jahr 2026`, `git diff --exit-code -- daten/` is clean (deterministic, outputs unchanged by validation).
    - No executor commit of this plan touches the planning state files: `beruehrt=$(git log --name-only --format= --grep='(261001-oim)' 93848a8d5c577f7643b031d3ade06e2b55e3b163..HEAD -- .planning/STATE.md .planning/PROJECT.md) && test -z "$beruehrt"` succeeds.
  </acceptance_criteria>
  <done>Malformed or orphaned declarations fail loudly with KonfigurationsFehler or SeitenFehler, pipeline CI is green, and regeneration is byte-identical.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| raw_data PDF -> pipeline | The authoritative but externally produced document. Its structure (no PG 1502 header in the Teilplanbereich) differs from its Querschnitt pages |
| Jahrgang/Sollwert TOML -> loaders | Maintainer-edited configuration that now controls P->PG assignment. A wrong entry would silently misassign published amounts unless validated |
| daten/ CSVs -> App (Phase 4) -> public GitHub Pages | Generated numbers become Bürgerinformation. Integrity of each number is the core value |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-261001-oim-01 | Tampering (data integrity) | [synthetische_produktgruppen] in pipeline/jahrgaenge/2026.toml | high | mitigate | Task 3: strict lade_jahrgang validation (key and field set, formats, PB prefix, page range, duplicate produkt) plus semantic SeitenFehler checks in baue_hierarchie (unknown product, printed-PG product, printed-PG code). Task 1: every declared code must be backed by a [haushaltsquerschnitt_pg] Sollwert that the tests compare against ergebnisplan.csv |
| T-261001-oim-02 | Tampering (data integrity) | baue_hierarchie and _synthetische_pg_datensaetze merging several products into one synthetic PG (the original defect) | high | mitigate | Task 1: collision raises SeitenFehler. The plaene copy raises PlaeneFehler unless exactly one child exists. Regel 2 (Σ P = PG, Σ PG = PB) still runs via eltern_code in alle.py |
| T-261001-oim-03 | Repudiation (hidden errors) | daten/pruefberichte/befunde.md | medium | mitigate | Task 2 removes only the observation bullet. All 10 Schlüsseltabelle rows stay (count-checked). D-04 stale-befund detection keeps alle.py at exit 1 if a Befund vanishes |
| T-261001-oim-04 | Information disclosure | generated CSVs | low | accept | Only PG codes, names and amounts change. No Mitarbeitendennamen or other personal data is touched |
| T-261001-oim-05 | Denial of service | TOML and regex parsing of config | low | accept | Maintainer-controlled input parsed by tomllib with fixed precompiled patterns. Failures exit with a clear KonfigurationsFehler |
| T-261001-oim-SC | Tampering | uv/pip package installs | low | accept | No new packages. `uv sync --locked` only reproduces the existing pipeline/uv.lock |
</threat_model>

<verification>
- Repo root: `(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)` passes.
- `uv run --directory pipeline python alle.py --jahr 2026` exits 0: Prüfregeln 1-4 grün, 0 veraltete Befunde, and Schritt 01 reports 49 PG (41 synthetisch).
- A second `alle.py --jahr 2026` run leaves `git diff --exit-code -- daten/` clean.
- hierarchie.csv contains `PG,1501,Wirtschaftsförderung,15,273,true`, `P,150101,Wirtschaftsförderung,1501,273,false`, `PG,1502,Tourismus,15,276,true` and `P,150102,Touristische Öffentlichkeitsarbeit,1502,276,false`.
- ergebnisplan.csv PG 1501 / PG 1502 Z. 29 Ansatz 2026 = -118138 / -72554 (Haushaltsquerschnitt S. 299).
- .planning/STATE.md and .planning/PROJECT.md are untouched by the executor.
</verification>

<success_criteria>
- Per D-14, every synthetic PG has exactly one product, enforced in code (SeitenFehler, PlaeneFehler) and tested on checked-in data.
- Product 150102 sits in synthetic PG 1502 "Tourismus", declared in the Jahrgangsdatei with source page S. 299. PG 1501 holds only 150101. Values match the Haushaltsquerschnitt.
- No year-specific value in Python code. The config is read only via lade_jahrgang and lade_sollwerte with full validation.
- TDD history: RED then GREEN commit pairs for the rule (Task 1) and for validation (Task 3).
- Pipeline CI green and regeneration deterministic. befunde.md keeps all Schlüsseltabelle rows.
</success_criteria>

<output>
Create `.planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-SUMMARY.md` when done. It must state the decision reconciliation (D-14 default plus declared assignment, because the product code's first four digits for 150102 are 1501), the new Regel-1 count and its derivation, and the new Regel-2 count from konsistenz.md.
</output>
