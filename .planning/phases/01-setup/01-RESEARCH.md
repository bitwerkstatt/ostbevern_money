# Phase 1: Setup - Research

**Researched:** 2026-10-01
**Domain:** Repo scaffolding — uv Python pipeline, Vue 3 app skeleton, GitHub Actions CI, year-config convention
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Münster-Übernahme**
- **D-01:** Den Münster-Code (`codeformuenster/haushalt-muenster-2026`) nutzen wir **nur als Vorlage** und schreiben ihn selbst neu. Es werden keine Dateien 1:1 kopiert und das Repo wird nicht geklont.
- **D-02:** Die neuen Komponenten behalten die **Namen und Props/Schnittstellen der Münster-Komponenten** (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts`). Die Umsetzung schreiben wir selbst.
- **D-03:** In Phase 1 entstehen **nur die Basiskomponenten**: `PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts` und `bildschirm.ts`. `GlossarBegriff`, `BegriffeListe`, `ProduktAkkordeon` und Sankey folgen in Phase 5, `QuelleSeitenleiste` in Phase 7.
- **D-04:** Die App bekommt eine **eigene Ostbevern-Farbpalette**, als Web-Awesome-Theme und als ECharts-Theme (`echartsTheme.ts`). Kontraste müssen dem a11y-Ziel genügen (Lighthouse ≥ 95).
- **D-05:** Lizenz: **MIT** (`LICENSE` im Root). README und App nennen „Inspiriert von Münster Money (Code for Münster)" mit Link. — **Reversibility: one-way.**

**Jahrgangskonfiguration**
- **D-06:** Format TOML, Ort `pipeline/jahrgaenge/2026.toml`. Gelesen mit `tomllib` aus der Standardbibliothek, keine weitere Abhängigkeit.
- **D-07:** Die Jahrgangsdatei enthält alles PDF-Spezifische: Haushaltsjahr, PDF-Pfad, Spaltenköpfe je Plantyp, Seitenbereiche der Kapitel, Kopfzeilen-Muster, erwartete Anzahlen (15 PB, 63 Produkte). **Fachliche Regeln bleiben im Code.**
- **D-08:** Sollwerte (Anhang B) liegen in `pipeline/jahrgaenge/2026_sollwerte.toml`. Phase 1 legt die Datei mit Struktur an (mind. Satzung § 1 bzw. B.1-Kopfwerte). Phase 2 füllt sie vollständig.
- **D-09:** Jahrgang wird über **`--jahr`** an jedem Pipeline-Skript gewählt. Standardwert 2026 steht **an genau einer Stelle**. Pipeline und Tests nutzen denselben Lader (`ostbevern.konfiguration.lade_jahrgang(jahr)`).

**Pipeline-Aufbau**
- **D-10:** Nummerierte Skripte nach Spez. 5.2 (`pipeline/01_seiten_klassifizieren.py` … `08_quellenbelege.py`, `alle.py`). Dünne typer-Einstiegspunkte, Logik im Paket `pipeline/ostbevern/`. Phase 1: nur die Skripte, die das Gerüst braucht.
- **D-11:** PDF wird nach **`raw_data/haushalt-2026.pdf`** umbenannt, Kopie in `discussion/` wird gelöscht. Normales Git, ohne LFS. Pfad kommt nur aus der Jahrgangsdatei.
- **D-12:** `uv run pytest` prüft in Phase 1 mit einem **Rauchtest**: Jahrgangsdatei lädt und ist vollständig; Sollwertdatei lädt; PDF existiert und hat 400 Seiten (Wert aus Jahrgangsdatei).
- **D-13:** Python **3.12**: `.python-version` = 3.12, `requires-python = ">=3.12"`.

**CI & Tooling**
- **D-14:** **ruff** prüft Lint und Format (`ruff check`, `ruff format --check`), Dev-Abhängigkeit im uv-Projekt. Kein mypy/pyright.
- **D-15:** Eine Workflow-Datei `.github/workflows/ci.yml` mit **zwei parallelen Jobs**, bei jedem Push und PR, ohne Pfadfilter:
  - `pipeline`: uv einrichten, `uv sync`, `ruff check`, `ruff format --check`, `pytest`
  - `app`: Node 22, `npm ci`, `vue-tsc`, ESLint, Prettier-Check, `npm run build`
  Deploy-Workflow kommt erst in Phase 7.
- **D-16:** **Node 22 LTS** (`.nvmrc` und `engines`) mit npm und Prettier über `eslint-config-prettier`. `npm run format:check` läuft in der CI.
- **D-17:** Befehle und Konventionen stehen in **`.claude/CLAUDE.md`** ("Technology Stack", "Conventions"). **Keine Root-`CLAUDE.md`** (bewusste Abweichung von Spez. 7). GSD-verwaltete Abschnitte bleiben unangetastet. Konventionen (Erfolgskriterium 5): deutsche Bezeichner ohne Umlaute, Beträge als int-Euro, nur 1-basierte PDF-Seiten, keine Jahrgangswerte im Code, Du-Anrede, Zahlen in Texten aus Daten.
- **D-18:** **Noch kein GitHub-Remote.** Phase 1 schreibt `ci.yml` und prüft alle CI-Befehle **lokal** mit denselben Befehlen. Executor legt kein Repo an und pusht nicht.

### Claude's Discretion
- `.gitignore`-Inhalt: `node_modules`, `.venv`, `dist`, `__pycache__`, `.DS_Store` usw. Generierte Daten unter `daten/` bleiben eingecheckt. Ob `daten/zwischen/` eingecheckt wird, entscheidet der Planner (Empfehlung: ja, wegen Diff-Prüfung in Phase 4).
- Leere Verzeichnisse (`daten/*`) per `.gitkeep` oder README.
- Umfang des App-Gerüsts: Layout-Shell und welche Routen schon als leere Seiten existieren. Nötig: mindestens eine Startseite und eine Demo-Nutzung der Basiskomponenten.
- Konkrete Farbwerte der Ostbevern-Palette (kontrastgeprüft).
- ESLint-Konfiguration (Flat Config, `@vue/eslint-config-typescript`) und ruff-Regelsatz.
- Interne Modulaufteilung von `ostbevern/` über `konfiguration.py` hinaus.

### Deferred Ideas (OUT OF SCOPE)
None. Die Diskussion blieb im Rahmen der Phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SETUP-01 | Repo-Struktur nach Spez. 7 existiert (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`), Quell-PDF unter `raw_data/` | See Architecture Patterns → Recommended Project Structure; Runtime State Inventory for the PDF rename/delete pair |
| SETUP-02 | Pipeline ist uv-Projekt (Python ≥ 3.12, pdfplumber, polars, typer, pytest), `uv run pytest` läuft | See Standard Stack → Core (Pipeline); Code Examples → pyproject.toml, konfiguration.py, smoke test; verified live in this sandbox |
| SETUP-03 | App-Grundgerüst (Vue 3, TS, Vite, Web Awesome, vue-echarts, Hash-Router) mit Münster-Basiskomponenten, `npm run build` läuft | See Standard Stack → Core (App); Code Examples → vite.config.ts, main.ts, router/index.ts; verified live end-to-end in this sandbox incl. `wa-*` elements + vue-echarts |
| SETUP-04 | Projekt-`CLAUDE.md` dokumentiert Befehle und Konventionen | See Project Constraints section below; D-17 fixes target file to `.claude/CLAUDE.md` |
| SETUP-05 | Jahrgangsspezifisches steht in Konfigurationsdatei, nicht im Code | See Code Examples → `2026.toml` skeleton, `konfiguration.py` loader pattern; Don't Hand-Roll → TOML parsing |
| QUAL-01 | `vue-tsc` und ESLint laufen fehlerfrei in der CI | See Validation Architecture; Code Examples → `ci.yml`; verified live (`npm run build`, `npm run lint`) in this sandbox |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

`.claude/CLAUDE.md` (project-level, this is the GSD-managed file D-17 designates as the one and only CLAUDE.md for this project) currently documents only the project description and constraints already covered by `CONTEXT.md`/`PROJECT.md` (tech stack, hosting, Genauigkeit, Datenschutz, Sprache, Pro-Kopf-Werte, Barrierefreiheit — all reproduced above or in PROJECT.md). Its "Technology Stack", "Conventions", and "Architecture" sections are explicitly placeholder ("not yet documented") — **populating them is SETUP-04's deliverable**, not a pre-existing constraint to honor. The GSD-managed sections ("GSD Workflow Enforcement", "Developer Profile", "Project Skills") must be left untouched per D-17.

The top-level sandbox `/Users/thma/repos/bitwerkstatt/CLAUDE.md` contains only sandbox/environment operating instructions (network policy, git auth, shell persistence) — not project conventions. It imposes no constraint on this phase's deliverables beyond "use the Bash tool correctly," which this research already complied with.

## Summary

Phase 1 is pure scaffolding: an empty-but-green uv Python project, an empty-but-buildable Vue 3 app, a two-job GitHub Actions workflow, and a year-config convention that keeps every PDF-layout fact for 2026 out of the code. None of this requires novel engineering — it requires picking current, mutually-compatible tool versions and following each tool's own current defaults, because several of the libraries this project depends on shipped major-version changes recently that most training-era tutorials (and even some fresh web search results) still describe using the *previous* major's patterns. This research runs the real scaffolding commands in this sandbox end-to-end (`uv init`, `uv add --dev`, `npm create vue@latest -- --ts --router --eslint --prettier`, then wiring in Web Awesome + vue-echarts, then `npm run build` and `npm run lint`) rather than trusting search-result snippets, specifically because of that version churn.

Three findings materially change what the planner should write into tasks: (1) `vue-router`'s current major is **5.x**, not 4.x — `npm create vue@latest` installs `^5.3.1` by default, and the project's hash-router requirement (D-09/§6.1) is satisfied by swapping one line (`createWebHistory` → `createWebHashHistory`) in the generated `router/index.ts`, no different from v4. (2) `uv add --dev` now writes a PEP 735 `[dependency-groups]` table, not the `[tool.uv] dev-dependencies` key that circulates in older blog posts — this is what D-14/D-15's `uv sync`+`ruff`+`pytest` CI job will actually operate on. (3) Web Awesome's custom elements (`wa-*`) need exactly one Vite-side config line (`template.compilerOptions.isCustomElement`) to make `vue-tsc --build` and `vite build` both pass cleanly with zero other wiring — confirmed by a live build in this sandbox, including a `vue-echarts` chart and a `wa-callout`/`wa-icon` pair together.

**Primary recommendation:** Scaffold the app with the official `create-vue` CLI (`npm create vue@latest -- --ts --router --eslint --prettier --bare`) rather than hand-assembling `package.json`, then layer Web Awesome + vue-echarts + the hash-router swap on top — this guarantees a tested-compatible version set instead of independently "latest"-pinned packages that may not have been tested together. For the pipeline, use `uv init --python 3.12` + `uv add --dev pytest ruff` + `uv add pdfplumber polars typer`, which produces exactly the `pyproject.toml` shape D-13/D-14 require.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PDF parsing / data extraction | Build-time Python pipeline (offline, not a runtime tier) | — | Runs once per PDF via `uv run`, output is checked-in generated data; no server exists (project has no backend) |
| Year/layout configuration (TOML) | Build-time Python pipeline | — | Read only by pipeline scripts via `tomllib`; the app never reads TOML, only the JSON the pipeline emits later (Phase 4+) |
| Consistency checks (Prüfregeln) | Build-time Python pipeline (pytest) | CI (GitHub Actions `pipeline` job) | Business-rule verification belongs where the data is produced, re-run on every push |
| App UI shell / routing | Browser (client-side SPA) | — | Static site, no SSR, no backend — Vue Router runs entirely client-side with hash history for GitHub Pages compatibility |
| Chart rendering (`BaseChart`/`vue-echarts`) | Browser (client-side) | — | ECharts renders to canvas/SVG in the browser; no server-side chart generation |
| Design tokens / theming (Web Awesome + `echartsTheme.ts`) | Browser (CSS custom properties read at runtime) | Build-time (Vite bundles the CSS) | Tokens are CSS custom properties resolved via `getComputedStyle` in the browser, but the CSS itself is bundled at build time |
| Type checking / linting (`vue-tsc`, ESLint, ruff) | CI (GitHub Actions `app`/`pipeline` jobs) | Local dev (pre-push) | Gate correctness before merge; D-18 means CI only runs locally in Phase 1 (no remote yet) |
| CLI entry points (`01_…py` … `alle.py`) | Build-time Python pipeline | — | `typer` CLIs are developer/CI-invoked, never served |

## Standard Stack

### Core (Pipeline)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12 (managed by uv; system default is 3.14.4) | Runtime | D-13 locks `.python-version`/`requires-python` to 3.12; `uv python install 3.12` works transparently even though the sandbox's system `python3` is 3.14.4 — **[VERIFIED: ran `uv python install 3.12` this session, succeeded in 4.86s]** |
| uv | 0.9.26 (already on PATH in this sandbox) | Project/dependency manager | `[VERIFIED: ran "uv --version" this session → 0.9.26]`. `uv init --python 3.12 .` produces `requires-python = ">=3.12"` in `pyproject.toml` and a `.python-version` file containing `3.12` — `[VERIFIED: ran "uv init" this session, inspected generated files]` |
| pdfplumber | 0.11.10 | PDF text/coordinate extraction | `[VERIFIED: pip index versions pdfplumber this session → 0.11.10 current]`. Already used in this session to read the real PDF and confirm page count (400) |
| polars | 1.44.2 | DataFrame / CSV I/O | `[VERIFIED: pip index versions polars this session → 1.44.2 current]` |
| typer | 0.27.2 | CLI entry points for `01_…py`…`alle.py` | `[VERIFIED: pip index versions typer this session → 0.27.2 current]` |
| pytest | 9.1.1 | Smoke test + Prüfregeln (later phases) | `[VERIFIED: pip index versions pytest this session → 9.1.1 current]`; `[VERIFIED: ran "uv run pytest" against a scratch project this session, passed]` |
| ruff | 0.16.9 | Lint (`ruff check`) + format (`ruff format --check`), D-14 | `[VERIFIED: pip index versions ruff this session → 0.16.9 current]`; `[VERIFIED: ran "uv run ruff check ." and "uv run ruff format --check ." this session against a scratch project, both passed]` |

**Installation (pipeline):**
```bash
cd pipeline
uv init --no-readme --python 3.12 .
uv add pdfplumber polars typer
uv add --dev pytest ruff
```
`[VERIFIED: ran this exact sequence (minus --no-readme) this session]` — `uv add --dev` writes a `[dependency-groups]` table (see Code Examples), not the older `[tool.uv] dev-dependencies` key some tutorials still show (see State of the Art).

### Core (App)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| vue | ^3.5.42 | UI framework | `[VERIFIED: resolved by "npm create vue@latest -- --ts --router --eslint --prettier --bare" this session, confirmed by inspecting the generated package.json]` |
| vue-router | **^5.3.1** | Hash-based client routing | `[VERIFIED: same scaffold run this session]`. **This is a major-version jump from the v4 that most training-era examples assume** — see State of the Art. The project's Hash-Router requirement is satisfied by changing one import/call in the generated `src/router/index.ts` |
| vite | ^8.2.2 (registry "latest" is 8.3.1) | Build tool / dev server | `[VERIFIED: scaffold-resolved version this session]`; `engines: { node: "^20.19.0 \|\| >=22.12.0" }` `[VERIFIED: npm view vite engines this session]` — the sandbox's Node 22.22.1 satisfies this |
| @vitejs/plugin-vue | ^6.0.9 | Vue SFC compilation for Vite | `[VERIFIED: npm view @vitejs/plugin-vue version/peerDependencies this session]` |
| vue-tsc | ^3.3.11 | Type-checking `.vue` + `.ts` files in CI (QUAL-01) | `[VERIFIED: scaffold-resolved version this session]`; peer requires `typescript >= 5.0.0` `[VERIFIED: npm view vue-tsc peerDependencies this session]` |
| typescript | ~6.0.0 (scaffold pin; registry "latest" is 7.0.2) | Type system | `[VERIFIED: scaffold-resolved version this session]`. Registry "latest" (7.0.2) is newer than what the official scaffold currently pins — follow the scaffold's pin for a tested-compatible set rather than the bare "latest" tag |
| eslint | ^10.10.0 (registry "latest" is 10.11.0) | Linting (QUAL-01) | `[VERIFIED: scaffold-resolved version this session]` |
| eslint-plugin-vue | ~10.11.0 | Vue-specific lint rules, flat config | `[VERIFIED: scaffold-resolved version this session]` |
| @vue/eslint-config-typescript | ^14.9.0 | `withVueTs`/`defineConfigWithVueTs` flat-config helper | `[VERIFIED: scaffold-resolved version this session]`; peers `eslint ^9.10.0 \|\| ^10.0.0`, `eslint-plugin-vue ^9.28.0 \|\| ^10.0.0` `[VERIFIED: npm view this session]` |
| eslint-config-prettier | ^10.1.8 | Disables ESLint rules that conflict with Prettier (D-16) | `[VERIFIED: scaffold-resolved version this session]`; imported as `eslint-config-prettier/flat` in the generated flat config `[VERIFIED: read generated eslint.config.ts this session]` |
| prettier | 3.9.6 (registry "latest" is 3.9.9) | Formatting, `npm run format:check` (D-16) | `[VERIFIED: scaffold-resolved version this session]` |
| @vue/tsconfig | ^0.9.1 | Shared `tsconfig` base (`tsconfig.dom.json`) | `[VERIFIED: scaffold-resolved version this session]` |
| echarts | ^6.1.0 | Charting engine | `[VERIFIED: npm view echarts version this session → 6.1.0; npm install succeeded this session]` |
| vue-echarts | ^8.3.1 | Vue wrapper around ECharts (`BaseChart`) | `[VERIFIED: npm view vue-echarts peerDependencies this session → { vue: "^3.3.0", echarts: "^6.0.0" }]`, both satisfied |
| @awesome.me/webawesome | ^3.14.0 | UI component library (per UI-SPEC) | `[VERIFIED: npm view @awesome.me/webawesome version this session → 3.14.0, matches UI-SPEC's stated provenance command/version]` |

**Installation (app):**
```bash
npm create vue@latest app -- --ts --router --eslint --prettier --bare
cd app
npm install
npm install echarts vue-echarts @awesome.me/webawesome
```
`[VERIFIED: ran this exact sequence this session; "npm run build" and "npm run lint" both passed cleanly afterward, including with wa-* custom elements and a vue-echarts chart wired into App.vue]`

Node/npm actually available in this sandbox: Node v22.22.1, npm 9.2.0 `[VERIFIED: "node --version"/"npm --version" this session]`. Note: `npm install` surfaced `EBADENGINE` warnings for 3 transitive dev-tool packages wanting `^22.22.2 || ^24.15.0 || >=26.0.0` (one patch version above what's installed) — these are warnings only, install and build both still succeeded `[VERIFIED: ran "npm install"/"npm run build" this session despite the warnings]`. Document in CI as a known-harmless warning, not a failure signal.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| oxlint (`eslint-plugin-oxlint`, `oxlint`) | ~1.82.0 | Fast Rust-based pre-lint, bundled by `create-vue`'s default `--eslint` flag | `[VERIFIED: scaffold-resolved this session]`. **Not mentioned in D-15/D-16** (which specify only ESLint). Claude's Discretion covers "ESLint-Konfiguration" — the planner should explicitly decide whether to keep oxlint (fast, zero extra conceptual cost, already wired by the scaffold) or strip it for a leaner, spec-literal `lint` script. Recommendation: keep it — it runs as a `run-s` pre-step before ESLint and does not change what D-15's CI step (`ESLint`) needs to invoke |
| @types/node, @tsconfig/node24 | scaffold-pinned | Node typings for `vite.config.ts` etc. | Installed automatically by the scaffold |
| vite-plugin-vue-devtools | ^8.2.1 | Dev-only Vue DevTools integration | Scaffold default; harmless in production builds (dev-only), fine to keep or remove per Claude's Discretion |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `tomllib` (stdlib) for Jahrgangsdatei | `tomli`/`tomlkit` (third-party) | D-06 explicitly rejects this — stdlib `tomllib` (Python ≥3.11) is read-only but sufficient since the pipeline never writes TOML; zero extra dependency |
| Hand-assembling `app/package.json` | `npm create vue@latest` scaffold (recommended) | Hand-assembly risks picking mutually-incompatible "latest" versions across vue/vue-router/vite/vue-tsc/eslint; the scaffold is Vue core team's tested baseline |
| `vue-router` v5 (current) | Pin to `vue-router@^4` | v4 is the long-familiar major from most tutorials and is still maintained (`npm view vue-router@^4 version` → latest `4.6.4`), but `create-vue@latest` (the project's own recommended scaffolding path) installs v5 by default; v5's extra peers (`vite`, `pinia`, `@pinia/colada`) are all `optional: true` `[VERIFIED: npm view vue-router peerDependenciesMeta this session]` so plain hash-router usage needs nothing beyond what's already installed. No CONTEXT.md decision pins a specific major — flagged as an open question below for explicit confirmation rather than treated as silently settled |
| oxlint + ESLint hybrid (scaffold default) | ESLint only | D-15/D-16 only name ESLint; oxlint is free extra speed with no added CI step (it's chained via `npm run lint`), but the planner should note it explicitly rather than let it pass unremarked |

## Package Legitimacy Audit

Ran `gsd_run query package-legitimacy check` for every package named above, across both ecosystems.

| Package | Registry | Age (publishedAt of current version) | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| vue | npm | 2026-09-17 | unavailable in sandbox | github.com/vuejs/core | SUS (`too-new`, `unknown-downloads`) | Flagged — see note below |
| vue-router | npm | 2026-09-02 | unavailable | github.com/vuejs/router | SUS (`too-new`, `unknown-downloads`) | Flagged |
| vue-echarts | npm | 2026-09-28 | unavailable | github.com/ecomfe/vue-echarts | SUS (`too-new`, `unknown-downloads`) | Flagged |
| echarts | npm | 2026-05-19 | unavailable | github.com/apache/echarts | SUS (`unknown-downloads`) | Flagged |
| vite | npm | 2026-09-24 | unavailable | github.com/vitejs/vite | SUS (`too-new`, `unknown-downloads`) | Flagged |
| vue-tsc | npm | 2026-08-21 | unavailable | github.com/vuejs/language-tools | SUS (`unknown-downloads`) | Flagged |
| typescript | npm | 2026-07-08 | unavailable | github.com/microsoft/TypeScript | SUS (`unknown-downloads`) | Flagged |
| eslint | npm | 2026-09-18 | unavailable | github.com/eslint/eslint | SUS (`too-new`, `unknown-downloads`) | Flagged |
| eslint-plugin-vue | npm | 2026-09-24 | unavailable | github.com/vuejs/eslint-plugin-vue | SUS (`too-new`, `unknown-downloads`) | Flagged |
| @vue/eslint-config-typescript | npm | 2026-06-21 | unavailable | github.com/vuejs/eslint-config-typescript | SUS (`unknown-downloads`) | Flagged |
| eslint-config-prettier | npm | 2025-07-18 | unavailable | github.com/prettier/eslint-config-prettier | SUS (`unknown-downloads`) | Flagged |
| prettier | npm | 2026-09-23 | unavailable | github.com/prettier/prettier | SUS (`too-new`, `unknown-downloads`) | Flagged |
| @awesome.me/webawesome | npm | 2026-09-24 | unavailable | github.com/shoelace-style/webawesome | SUS (`too-new`, `unknown-downloads`) | Flagged |
| @vue/tsconfig | npm | 2026-03-24 | unavailable | github.com/vuejs/tsconfig | SUS (`unknown-downloads`) | Flagged |
| pdfplumber | pypi | 2026-06-15 | unavailable | github.com/jsvine/pdfplumber | SUS (`unknown-downloads`) | Flagged |
| polars | pypi | 2026-09-09 | unavailable | pola.rs (→ github.com/pola-rs/polars) | SUS (`too-new`, `unknown-downloads`) | Flagged |
| typer | pypi | 2026-08-28 | unavailable | github.com/fastapi/typer | SUS (`unknown-downloads`) | Flagged |
| pytest | pypi | 2026-06-19 | unavailable | github.com/pytest-dev/pytest | SUS (`unknown-downloads`) | Flagged |
| ruff | pypi | 2026-09-24 | unavailable | docs.astral.sh/ruff (→ github.com/astral-sh/ruff) | SUS (`too-new`, `unknown-downloads`) | Flagged |

**Interpretation note (important for the planner):** every single package checked came back `SUS`, which at first glance looks alarming but is a sandbox-environment artifact, not a per-package risk signal: the `package-legitimacy check` tool could not reach a download-count API from this sandbox (`unknown-downloads` on 100% of packages, including `pytest` and `vue` — unambiguously legitimate, decade-old projects), and its `too-new` heuristic compares against the *latest published version's* timestamp, not the package's *first-ever* publish date — every one of these is an actively-maintained project that ships new versions every few weeks, so "latest version is < 30 days old" is expected and not a red flag. Every package above resolves to the canonical, well-known GitHub organization/repo for that project (`vuejs/core`, `apache/echarts`, `pytest-dev/pytest`, `astral-sh` ruff, etc.) — there is no slopsquatting signal (no off-brand repo, no missing repo, no suspicious `postinstall` script — `[VERIFIED: npm view <pkg> scripts.postinstall this session for all npm packages → all empty/null]`). Per the Package Legitimacy Gate protocol this file still files every package as `SUS`/"Flagged" so the planner inserts a `checkpoint:human-verify` before the install tasks — treat that checkpoint as a quick "does this still look like the real repo" glance rather than a deep investigation, given the explanation above.

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** all 19 packages above (see interpretation note — sandbox tooling limitation, not a per-package finding). Planner: add one `checkpoint:human-verify` task before the dependency-install tasks in both the pipeline and app plans.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  raw_data/haushalt-2026.pdf  (400 pages, checked into git)       │
└───────────────────────────────┬───────────────────────────────────┘
                                 │ read by (Phase 2+; Phase 1 only
                                 │ smoke-tests existence + page count)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  pipeline/  (uv project, Python 3.12)                            │
│                                                                   │
│  pipeline/jahrgaenge/2026.toml  ──┐                               │
│  pipeline/jahrgaenge/2026_sollwerte.toml ─┤                       │
│                                    │ loaded via                  │
│                                    ▼                              │
│  pipeline/ostbevern/konfiguration.py::lade_jahrgang(jahr)         │
│                                    │                              │
│                                    ▼                              │
│  pipeline/01_seiten_klassifizieren.py … 08_quellenbelege.py       │
│  (thin typer CLIs; Phase 1 = skeletons only)      │ alle.py       │
│                                    │               (orchestrates) │
│                                    ▼                              │
│  pipeline/tests/  ── uv run pytest ── Rauchtest (D-12):          │
│     - Jahrgangsdatei lädt & vollständig                          │
│     - Sollwertdatei lädt                                         │
│     - PDF existiert, 400 Seiten                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ (Phase 4+: app/src/data/*.json —
                                 │  out of scope for Phase 1)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  app/  (Vite + Vue 3 + TypeScript, static SPA)                    │
│                                                                   │
│  src/main.ts                                                      │
│   ├─ setIconPath('/icons')  (self-hosted WA icons, no CDN)        │
│   ├─ Web Awesome CSS + JS side-effect imports                    │
│   └─ app.use(router).mount('#app')                                │
│                                                                   │
│  src/router/index.ts — createWebHashHistory() (GitHub Pages)     │
│                                                                   │
│  src/components/ (Phase 1 base components, D-02/D-03):            │
│   PageIntro · ChartCard · BaseChart(vue-echarts) · DatenTabelle   │
│  src/charts/format.ts · echartsTheme.ts · src/lib/bildschirm.ts   │
│                                                                   │
│  Build: vite.config.ts (isCustomElement: tag.startsWith('wa-'))  │
│   npm run build → vue-tsc --build  +  vite build  → dist/        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  .github/workflows/ci.yml  — on every push/PR, two parallel jobs │
│   job "pipeline": setup-uv → uv sync → ruff check → ruff format  │
│                    --check → pytest                               │
│   job "app": setup-node(22) → npm ci → vue-tsc → eslint →         │
│              prettier --check → npm run build                    │
│   (D-18: no GitHub remote yet — Phase 1 verifies these commands  │
│    locally; CI itself only runs once the user pushes)            │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure
```
ostbevern_money/
├── README.md
├── LICENSE                        # MIT (D-05)
├── .claude/CLAUDE.md               # commands + conventions (D-17, no root CLAUDE.md)
├── discussion/                     # spec; PDF copy DELETED by this phase (D-11)
├── raw_data/
│   └── haushalt-2026.pdf           # renamed from "Haushalt 2026 komplett.pdf" (D-11)
├── pipeline/                        # uv project
│   ├── pyproject.toml
│   ├── .python-version              # "3.12" (D-13)
│   ├── uv.lock
│   ├── ostbevern/                  # library package
│   │   └── konfiguration.py        # lade_jahrgang(jahr) — D-09
│   ├── jahrgaenge/
│   │   ├── 2026.toml               # D-06/D-07
│   │   └── 2026_sollwerte.toml     # D-08 (structure only in Phase 1)
│   ├── 01_seiten_klassifizieren.py … 08_quellenbelege.py   # D-10
│   ├── alle.py
│   └── tests/
│       └── test_rauchtest.py       # D-12
├── daten/
│   ├── zwischen/                   # .gitkeep (generated, Phase 2+)
│   ├── aufbereitet/                # .gitkeep
│   ├── manuell/                    # .gitkeep
│   └── pruefberichte/              # .gitkeep
└── app/                             # Vite project (via create-vue)
    ├── package.json
    ├── .nvmrc                      # "22" (D-16)
    ├── vite.config.ts              # isCustomElement for wa-*
    ├── eslint.config.ts            # flat config, D-15/D-16
    ├── .prettierrc.json
    ├── index.html
    └── src/
        ├── main.ts
        ├── App.vue
        ├── router/index.ts         # createWebHashHistory
        ├── components/
        │   ├── PageIntro.vue
        │   ├── ChartCard.vue
        │   ├── BaseChart.vue
        │   └── DatenTabelle.vue
        ├── charts/
        │   ├── format.ts
        │   └── echartsTheme.ts
        └── lib/
            └── bildschirm.ts
```

### Pattern 1: Single-source Jahrgang loader
**What:** One Python function (`ostbevern.konfiguration.lade_jahrgang(jahr: int)`) reads `pipeline/jahrgaenge/{jahr}.toml` via `tomllib`, validates required keys are present, and returns a typed structure. Every pipeline script and every test imports this function instead of reading TOML directly or hardcoding values.
**When to use:** Any time a script needs the PDF path, column headers, page ranges, header patterns, or expected counts (D-07).
**Example:**
```python
# Source: verified this session — tomllib.load() behavior confirmed against
# Python 3.12 (via `uv run --python 3.12 python3 -c "..."`) and against the
# project's own TOML shape implied by D-07/D-12.
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

JAHRGAENGE_DIR = Path(__file__).parent.parent / "jahrgaenge"

REQUIRED_KEYS = {"haushaltsjahr", "pdf_pfad", "erwartete_pdf_seiten"}


@dataclass(frozen=True)
class Jahrgang:
    haushaltsjahr: int
    pdf_pfad: Path
    erwartete_pdf_seiten: int
    # ... weitere Felder je nach finaler 2026.toml-Struktur (Spaltenköpfe,
    # Seitenbereiche, Kopfzeilen-Muster) — ergänzt in Phase 2.


def lade_jahrgang(jahr: int) -> Jahrgang:
    pfad = JAHRGAENGE_DIR / f"{jahr}.toml"
    with pfad.open("rb") as f:
        rohdaten = tomllib.load(f)
    fehlend = REQUIRED_KEYS - rohdaten.keys()
    if fehlend:
        raise ValueError(f"Jahrgangsdatei {pfad} fehlen Schlüssel: {fehlend}")
    return Jahrgang(
        haushaltsjahr=rohdaten["haushaltsjahr"],
        pdf_pfad=Path(rohdaten["pdf_pfad"]),
        erwartete_pdf_seiten=rohdaten["erwartete_pdf_seiten"],
    )
```
Default-year placement (D-09, "an genau einer Stelle"): define `STANDARD_JAHR = 2026` once in `ostbevern/konfiguration.py` (or a small `ostbevern/__init__.py` constant), and have every typer CLI's `--jahr` option default to that constant — never repeat the literal `2026` in each script.

### Pattern 2: Thin typer CLI wrapping library logic
**What:** Each `pipeline/0N_*.py` file is a few lines: import from `pipeline/ostbevern/`, define a typer `app`, accept `--jahr` (default `STANDARD_JAHR`), call into the library.
**When to use:** All D-10 pipeline scripts.
**Example:**
```python
# Source: typer official pattern (typer.tiangolo.com/tutorial/first-steps,
# typer.tiangolo.com/tutorial/options), verified this session via WebSearch
# against the current docs structure.
import typer
from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang

app = typer.Typer()


@app.command()
def main(jahr: int = typer.Option(STANDARD_JAHR, "--jahr", help="Haushaltsjahr")) -> None:
    konfiguration = lade_jahrgang(jahr)
    # Phase 1: no extraction logic yet — this is a placeholder entry point.
    typer.echo(f"Seitenklassifikation für Jahrgang {konfiguration.haushaltsjahr} (Platzhalter)")


if __name__ == "__main__":
    app()
```

### Pattern 3: Web Awesome custom elements in Vue + Vite
**What:** Two-line wiring makes `vue-tsc --build` and `vite build` both treat `wa-*` tags as opaque custom elements instead of unresolved Vue components.
**When to use:** Any `.vue` file using a `<wa-*>` tag (every page from Phase 1 onward).
**Example:**
```typescript
// Source: verified this session — built end-to-end in a scratch Vite project
// with <wa-callout> + <wa-icon> + a vue-echarts chart in the same App.vue;
// `npm run build` (vue-tsc --build + vite build) and `npm run lint` both
// passed with zero errors.
// vite.config.ts
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('wa-'),
        },
      },
    }),
  ],
})
```
```typescript
// src/main.ts — self-hosted icons per UI-SPEC (no Font Awesome CDN dependency)
import '@awesome.me/webawesome/dist/styles/webawesome.css'
import '@awesome.me/webawesome/dist/styles/color/variants/brand.css'
import { setIconPath } from '@awesome.me/webawesome'
import '@awesome.me/webawesome/dist/webawesome.js'

// [VERIFIED: node_modules/@awesome.me/webawesome/dist/utilities/base-path.d.ts
// this session] — doc comment on setIconPath reads (verbatim):
// "Sets the path where the default icon library resolves SVG icons from...
//  The expected directory structure mirrors the Font Awesome SVG download,
//  e.g. `{path}/solid/house.svg` or `{path}/brands/github.svg`.
//  This should be called before Web Awesome components are loaded."
setIconPath('/icons')
```
The `.wa-brand-yellow` class (UI-SPEC's accent mechanism) is real and does exactly what the UI-SPEC assumes — `[VERIFIED: node_modules/@awesome.me/webawesome/dist/styles/color/variants/brand.css:1-2,46-58 this session]`, verbatim excerpt:
```css
@layer wa-color-variant {
  :where(:root), /* default */
  .wa-brand-blue { --wa-color-brand-95: var(--wa-color-blue-95); /* … */ }
  /* … */
  .wa-brand-yellow {
    --wa-color-brand-95: var(--wa-color-yellow-95);
    /* …--wa-color-brand-* chain remapped to --wa-color-yellow-* … */
  }
}
```
Import path: `@awesome.me/webawesome/dist/styles/color/variants/brand.css`, then apply class `wa-brand-yellow` to `<html>` (or another ancestor) to activate the gold accent tokens the UI-SPEC's Color section specifies.

### Pattern 4: Hash-router swap
**What:** `create-vue --router` generates `createWebHistory`; the project needs `createWebHashHistory` for GitHub Pages (no server-side rewrite rules).
**Example:**
```typescript
// src/router/index.ts — [VERIFIED: generated by `npm create vue@latest --
// --ts --router` this session, then this one-line diff applied and rebuilt
// successfully]
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'start', component: () => import('../views/StartView.vue') },
  ],
})

export default router
```

### Pattern 5: vue-echarts on-demand imports (tree-shaking)
**What:** Import only the chart types/components actually used, not the whole `echarts` bundle.
**Example:**
```typescript
// Source: [CITED: raw.githubusercontent.com/ecomfe/vue-echarts/main/README.md
// — fetched this session] + [VERIFIED: ran this exact pattern in a scratch
// project this session with BarChart/GridComponent/TooltipComponent; build
// succeeded]
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])
```
`BaseChart.vue` should wrap `VChart`, register only the renderer/series/component set the app actually needs across all later phases (Phase 1's demo chart can use a minimal set like the above; later phases add `PieChart`, `graphic`, `TreemapChart` series types, etc. as needed — don't register the whole library "just in case").

### Anti-Patterns to Avoid
- **Re-parsing TOML ad hoc in each script:** every pipeline script must go through `lade_jahrgang()` (D-09) — a script that does `tomllib.load()` itself duplicates the "Pflichtschlüssel vorhanden" validation and risks silently accepting an incomplete file.
- **Hardcoding `2026` anywhere outside the one `STANDARD_JAHR` constant:** defeats D-09's entire purpose (processing 2027 later with minimal changes).
- **Writing a custom German-number formatter in both `format.ts` and inline in components:** `charts/format.ts` is the single source of truth (D-02, UI-05) — `<wa-format-number>` and ECharts tooltip/axis formatters must both call into it, never format independently.
- **Importing the entire `echarts` package (`import "echarts"`)** instead of on-demand imports — works, but defeats tree-shaking; only acceptable as an explicit, documented tradeoff, not a default.
- **Forgetting `isCustomElement`:** omitting the Vite template-compiler option makes Vue try to resolve `<wa-*>` as a component and triggers "Failed to resolve component" warnings at runtime (and, depending on strictness, lint noise) even though the element still renders via the browser's native custom-element registry.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TOML parsing | A custom `.toml`/`.ini` reader or regex-based parser | `tomllib` (stdlib, Python ≥3.11) | D-06 explicitly mandates this; zero extra dependency, battle-tested, `[VERIFIED: ran tomllib.load() against a real nested TOML file this session on Python 3.12]` |
| CSV/DataFrame handling | Manual `csv.reader` + list-of-dicts bookkeeping | `polars` | Already the mandated stack (D-constraints); native CSV read/write, typed columns, used throughout later phases for `ergebnisplan.csv` etc. |
| CLI argument parsing | `argparse` boilerplate per script | `typer` | Already mandated; type-hint-driven, auto-generates `--help`, consistent `--jahr` handling across all 9 scripts |
| Number formatting (int-euro → "1.234 €") | Per-component `.toLocaleString()` calls scattered across the app | `charts/format.ts` (single module) | UI-05 requires every displayed number to route through generated data + one formatting source; duplicated formatting logic drifts over time |
| Icon hosting / resolution | Manual `<img>` tag SVG sprite management | Web Awesome's built-in `setIconPath()` + default icon library | `[VERIFIED: setIconPath exported from the package this session]` — exists precisely for this self-hosting use case, no custom asset-pipeline needed |
| ESLint+Prettier conflict resolution | Manually disabling individual ESLint stylistic rules | `eslint-config-prettier` (already in D-16) | Purpose-built for exactly this; `[VERIFIED: generated flat config imports "eslint-config-prettier/flat" as the final config in the array this session]` |
| Custom-element type checking workaround | Suppressing TS errors with `// @ts-ignore` on every `<wa-*>` usage | `isCustomElement` in `vite.config.ts`'s Vue plugin template compiler options | One config line handles every tag at once; verified end-to-end this session |

**Key insight:** every "hard problem" in this phase already has an official, verified-working answer baked into the mandated stack — the risk in Phase 1 is not under-building, it's *hand-rolling something the tooling (or the TOML/typer/polars stack itself) already solves*, or pinning package versions independently in a way that breaks a tested combination the official `create-vue` scaffold already gets right.

## Runtime State Inventory

> Phase 1 includes a file rename + delete (D-11: `raw_data/Haushalt 2026 komplett.pdf` → `raw_data/haushalt-2026.pdf`, and deletion of the `discussion/` copy), which triggers this checklist even though the phase is otherwise greenfield.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, no datastore exists in this project (static site, no backend) | None |
| Live service config | None — `[VERIFIED: "git remote -v" this session → empty output]`, confirming D-18 ("noch kein GitHub-Remote"); no CI has ever run against this repo, no external service holds config referencing the old filename | None |
| OS-registered state | None — no scheduled tasks, services, or process managers reference this repo | None |
| Secrets/env vars | None — no `.env`, no CI secrets configured yet (no remote to hold them) | None |
| Build artifacts / installed packages | **PDF file itself**: both copies are git-tracked, no LFS — `[VERIFIED: "git ls-files raw_data discussion" this session → "discussion/Haushalt 2026 komplett.pdf" and "raw_data/Haushalt 2026 komplett.pdf" both listed]`. This is a tracked-file rename + delete, not a data migration — use `git mv "raw_data/Haushalt 2026 komplett.pdf" "raw_data/haushalt-2026.pdf"` then `git rm "discussion/Haushalt 2026 komplett.pdf"` so git preserves rename history instead of showing a delete+add | Code edit only (the pipeline reads the path from the Jahrgangsdatei per D-11, so once `2026.toml`'s `pdf_pfad` points at the new path, nothing else references the old name) |

**Canonical question answered:** after this phase's rename, nothing outside the git tree and the one `pdf_pfad` TOML value refers to the old filename — confirmed by the empty `git remote -v` (D-18) and the absence of any database, scheduler, or secret store in this greenfield project.

## Common Pitfalls

### Pitfall 1: `uv add --dev` doesn't write `[tool.uv] dev-dependencies`
**What goes wrong:** Several still-circulating tutorials and blog posts (surfaced in this session's own web search) describe adding `[tool.uv]\ndev-dependencies = [...]` to `pyproject.toml` by hand. Following that pattern produces a `pyproject.toml` that doesn't match what the current `uv` CLI actually writes.
**Why it happens:** `uv` migrated to PEP 735 `[dependency-groups]` some time ago; older docs/posts predate the migration.
**How to avoid:** Always run `uv add --dev <pkg>` and let `uv` write the file — `[VERIFIED: ran "uv add --dev pytest" and "uv add --dev ruff" this session, resulting pyproject.toml has a `[dependency-groups]\ndev = ["pytest>=9.1.1", "ruff>=0.16.9"]` section]`.
**Warning signs:** A `pyproject.toml` with `[tool.uv] dev-dependencies = [...]` instead of `[dependency-groups]` was likely hand-written against stale docs — `uv sync` still probably works either way, but CI diff-checks against this file should reconcile with what `uv add` actually produces so the file stays reproducible by rerunning the same commands.

### Pitfall 2: `vue-router`'s current default major is 5, not 4
**What goes wrong:** Writing `router/index.ts` from memory/tutorials (which overwhelmingly show `vue-router@4` patterns) is fine API-wise (createRouter/createWebHashHistory are unchanged), but pinning `"vue-router": "^4.x.x"` by hand in `package.json` diverges from what `npm create vue@latest` actually installs today, and from the versions this research verified end-to-end.
**Why it happens:** v5 is a comparatively recent major; most training-era and even some current web content assumes v4 is "the" Vue 3 router.
**How to avoid:** Let the `create-vue` scaffold choose the version (`^5.3.1` as of this research), or make an explicit, documented choice to pin v4 if the planner has a specific reason to avoid v5's (all-optional) new peers.
**Warning signs:** `npm ls vue-router` showing a `5.x` version when a task/PLAN.md assumed `4.x` — not actually a functional problem (the API used by this project, `createRouter`/`createWebHashHistory`/`routes`, is unchanged across the major), but worth flagging for an executor who didn't expect it. See Open Questions.

### Pitfall 3: `wa-*` elements need `isCustomElement`, or Vue attempts component resolution
**What goes wrong:** Without the `isCustomElement` template-compiler option, Vue's runtime compiler treats unknown `wa-*` tags as unresolved Vue components (console warnings), even though the browser still renders them correctly as native custom elements once Web Awesome's JS has registered them.
**Why it happens:** Vue can't distinguish "a web component I haven't loaded yet" from "a typo'd component name" without this hint.
**How to avoid:** Set `template.compilerOptions.isCustomElement` in the `@vitejs/plugin-vue` options (see Pattern 3) — confirmed this one line is sufficient; no additional `tsconfig.json`/`vueCompilerOptions` entry was needed for `vue-tsc --build` to pass cleanly in this session's test (a `<wa-callout>` + `<wa-icon>` + `vue-echarts` combination built with zero type errors).
**Warning signs:** Console warnings like `[Vue warn]: Failed to resolve component: wa-callout` during dev/build, or ESLint's `vue/no-undef-components` (if enabled) flagging `wa-*` tags as unknown.

### Pitfall 4: Node 22.22.1 is one patch version behind some transitive dev-tool floors
**What goes wrong:** `npm install` in the scaffolded app prints `EBADENGINE` warnings for a handful of npm-internal transitive packages (`which@7.0.0`, `json-parse-even-better-errors@6.0.0`, `npm-normalize-package-bin@6.0.0`, `npm-run-all2@9.0.3`, `read-package-json-fast@6.0.0`) wanting `^22.22.2 || ^24.15.0 || >=26.0.0`.
**Why it happens:** These are npm's own bundled tooling dependencies bumping their floor slightly ahead of this sandbox's installed Node 22.22.1.
**How to avoid:** Nothing needs fixing — `[VERIFIED: ran "npm install" and "npm run build" this session despite the warnings, both succeeded]`. Document this as expected noise in the CI job so a reviewer doesn't mistake it for a real failure; it does not affect `npm ci`/`npm run build`/`vue-tsc`/ESLint functionality.
**Warning signs:** None needed — purely cosmetic in this case. If GitHub Actions' `actions/setup-node@v7` with `node-version: 22` resolves to a build ≥22.22.2 (likely, given these are moving-target CI runners), the warnings won't even appear there.

### Pitfall 5: `discussion/Haushalt 2026 komplett.pdf` and `raw_data/Haushalt 2026 komplett.pdf` are two separately tracked git blobs
**What goes wrong:** Deleting only one copy (e.g. forgetting the `discussion/` copy) leaves a stale, misleadingly-named duplicate PDF in the repo, doubling the repo's binary weight for no reason.
**Why it happens:** Both paths were committed independently before this phase; git does not automatically deduplicate identical file content across paths at the working-tree level (it does at the object-storage level, so the extra disk cost is small, but the duplicate *path* remains confusing).
**How to avoid:** `git mv "raw_data/Haushalt 2026 komplett.pdf" "raw_data/haushalt-2026.pdf"` (one path, preserves rename history) and `git rm "discussion/Haushalt 2026 komplett.pdf"` (the other path, per D-11) as two separate, explicit git operations — both `[VERIFIED: "git ls-files" this session confirms both paths currently exist and are tracked]`.
**Warning signs:** `git status` showing the PDF under `discussion/` still present after the phase claims to be complete.

## Code Examples

### `pipeline/pyproject.toml` (resulting shape after the Installation commands above)
```toml
# [VERIFIED: this exact shape produced by "uv init --python 3.12 ." +
# "uv add pdfplumber polars typer" + "uv add --dev pytest ruff" this session]
[project]
name = "ostbevern-money-pipeline"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pdfplumber>=0.11.10",
    "polars>=1.44.2",
    "typer>=0.27.2",
]

[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "ruff>=0.16.9",
]

[tool.ruff]
# line-length, target-version etc. — Claude's Discretion for exact rule set.
# [CITED: pyproject.toml vs ruff.toml discussion + Ruff docs structure,
# WebSearch this session] — sections are [tool.ruff], [tool.ruff.lint],
# [tool.ruff.format]; ruff auto-discovers the nearest pyproject.toml with a
# [tool.ruff] table.
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.ruff.format]
quote-style = "double"
```

### `pipeline/tests/test_rauchtest.py` (D-12)
```python
# Shape only — exact assertions depend on the final 2026.toml/
# 2026_sollwerte.toml structure the planner designs; page-count value
# [VERIFIED: ran pdfplumber against the real file this session —
# "raw_data/Haushalt 2026 komplett.pdf" has exactly 400 pages, matching
# both D-12's claim and the spec's "400-seitige" description]
import pdfplumber

from ostbevern.konfiguration import lade_jahrgang, lade_sollwerte  # name TBD by planner


def test_jahrgangsdatei_laedt_und_ist_vollstaendig():
    konfiguration = lade_jahrgang(2026)
    assert konfiguration.haushaltsjahr == 2026


def test_sollwertdatei_laedt():
    sollwerte = lade_sollwerte(2026)
    assert sollwerte is not None


def test_pdf_existiert_mit_erwarteter_seitenzahl():
    konfiguration = lade_jahrgang(2026)
    assert konfiguration.pdf_pfad.exists()
    with pdfplumber.open(konfiguration.pdf_pfad) as pdf:
        assert len(pdf.pages) == konfiguration.erwartete_pdf_seiten
```

### `.github/workflows/ci.yml` (D-15)
```yaml
# Action versions [VERIFIED: queried GitHub Releases API this session —
# actions/checkout latest = v7.0.1, actions/setup-node latest = v7.0.0,
# astral-sh/setup-uv latest = v10.2.0]
name: CI

on:
  push:
  pull_request:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: pipeline
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: astral-sh/setup-uv@v10.2.0
        with:
          version-file: pipeline/pyproject.toml
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run pytest

  app:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: app
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-node@v7.0.0
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: app/package-lock.json
      - run: npm ci
      - run: npm run type-check   # vue-tsc --build, per create-vue's default script name
      - run: npm run lint:eslint  # or a dedicated "lint:ci" script without --fix
      - run: npm run format:check # planner adds this script: "prettier --check src/"
      - run: npm run build
```
Note: `astral-sh/setup-uv`'s `version-file` input reads the uv version to install from the project's own lockfile/config — `[CITED: WebSearch summary of astral-sh/setup-uv action.yml inputs this session]`; an alternative is pinning `version: "0.9.26"` directly to exactly match what's verified working in this research. `npm ci` requires a committed `package-lock.json` — generate one locally (`npm install`) before the CI job can use `npm ci`.

### `app/eslint.config.ts` (flat config, D-15/D-16)
```typescript
// [VERIFIED: generated by "npm create vue@latest -- --ts --router --eslint
// --prettier --bare" this session, then successfully ran "npm run lint"
// against real wa-*/vue-echarts code with this exact config]
import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import pluginOxlint from 'eslint-plugin-oxlint'
import skipFormatting from 'eslint-config-prettier/flat'

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,ts,mts,tsx}'],
  },
  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),
  ...pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  ...pluginOxlint.buildFromOxlintConfigFile('.oxlintrc.json'),
  skipFormatting,
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `uv`: `[tool.uv]\ndev-dependencies = [...]` in `pyproject.toml` | `[dependency-groups]\ndev = [...]` (PEP 735) via `uv add --dev` | Before this research session (confirmed by running current `uv` 0.9.26) | Planner/executor should let `uv add --dev` write the file rather than copying the old key from older tutorials |
| `vue-router@4` as "the" Vue 3 router | `vue-router@5` is the current default (`create-vue@latest` installs `^5.3.1`) | Confirmed this session via live scaffold | API surface used by this project (createRouter/createWebHashHistory/routes) is unchanged; only the extra (all-optional) peerDependencies are new |
| ESLint `.eslintrc.*` (legacy config) | ESLint 9+/10 flat config (`eslint.config.ts`) via `defineConfigWithVueTs`/`vueTsConfigs` | Vue tooling migrated ahead of this research | D-15's "ESLint läuft fehlerfrei" should target the flat-config script names (`lint:eslint`), not a legacy `.eslintrc` |
| ESLint alone for Vue+TS linting | ESLint + oxlint hybrid, chained via `run-s "lint:*"` | `create-vue`'s current default scaffold (verified this session) | Not mandated by D-15/D-16 — planner decision point (keep for speed, or strip for spec-literal simplicity) |
| `vue-tsc --noEmit` | `vue-tsc --build` (scaffold's current `type-check` script) | `create-vue`'s current default scaffold (verified this session) | Functionally equivalent for CI purposes (type errors fail the command either way); `--build` also writes a `.tsbuildinfo` cache file (already `.gitignore`d by the scaffold's default ignore list) |
| Font Awesome icons via CDN (Web Awesome's zero-config default) | Self-hosted via `setIconPath('/icons')` | Project-specific decision (UI-SPEC), not an upstream change | Confirmed the API needed for this exists and behaves as the UI-SPEC assumed |

**Deprecated/outdated:** None of the mandated libraries are deprecated; the table above reflects version-currency drift (major-version bumps), not deprecation.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `oxlint`/`eslint-plugin-oxlint` should be kept (not stripped) from the `create-vue` default scaffold | Standard Stack → Supporting; State of the Art | Low — if the planner decides to strip it instead, `npm run lint` script needs a one-line edit (`run-s "lint:*"` → just `eslint . --fix`); does not affect `vue-tsc`/`npm run build`/CI pass/fail either way |
| A2 | `vue-router@^5.3.1` (the scaffold default) is the right choice rather than pinning `@^4` | Standard Stack → Core (App); Alternatives Considered; Pitfall 2 | Low-medium — both majors expose the same `createWebHashHistory` API this project needs; the only practical difference is 3 new (optional) peerDependencies in `package.json` that resolve to nothing extra being installed. No CONTEXT.md decision addresses the major version explicitly — flagged as an Open Question for a quick confirm rather than silently decided |
| A3 | `astral-sh/setup-uv@v10.2.0` and `actions/setup-node@v7.0.0`/`actions/checkout@v7.0.1` remain the correct action versions between now and when the user actually pushes to GitHub and the workflow first runs (D-18 defers the real CI run) | Code Examples → ci.yml | Low — these are fetched live from GitHub's Releases API this session; a newer patch/minor may exist by the time the user pushes, but the workflow YAML would still function with an older pin (GitHub Actions does not auto-break on stale-but-valid version pins) |
| A4 | `uv.lock` committed alongside `pyproject.toml` is the intended reproducibility mechanism (not explicitly stated in CONTEXT.md, but implied by "uv-Projekt" + the project's broader "generierte Dateien werden eingecheckt" convention from PROJECT.md) | Architecture Patterns → Recommended Project Structure | Low — `uv sync` in CI regenerates environment state from `uv.lock` either way; omitting the lock file from git just means CI resolves fresh each run instead of reproducing an exact pin |

**If this table is empty:** N/A — see entries above. All other claims in this research were verified live in this sandbox session or cited from official docs/sources fetched this session.

## Open Questions

1. **Should `vue-router` be pinned to v4 or allowed to float to the scaffold's current v5 default?**
   - What we know: v5 is what `npm create vue@latest` installs today, builds and lints cleanly with this project's hash-router usage, and its extra peerDependencies (`vite`, `pinia`, `@pinia/colada`) are all optional and unused.
   - What's unclear: Whether the Münster template (the external reference for component *names/props*, not package versions — D-01/D-02 explicitly say "nur als Vorlage") itself uses v4, and whether the planner wants to match that for easier side-by-side comparison during development, or just take the current scaffold default.
   - Recommendation: Default to whatever `npm create vue@latest` installs (v5) unless the planner has a specific reason to pin v4 — document the choice explicitly in the PLAN.md either way so it's not an accidental drift.

2. **Exact `pipeline/jahrgaenge/2026.toml` schema (field names/nesting for Spaltenköpfe, Seitenbereiche, Kopfzeilen-Muster)**
   - What we know: D-07 lists the five categories of content required (Haushaltsjahr+PDF-Pfad, Spaltenköpfe je Plantyp, Seitenbereiche der Kapitel, Kopfzeilen-Muster, erwartete Anzahlen).
   - What's unclear: The exact TOML table/key names — this is a data-modeling decision for the planner, not something this research can verify since no prior art/file exists yet in this repo.
   - Recommendation: Planner designs the schema directly from D-07's five bullet points and SPEZIFIKATION.md §2/§2.2 (which lists the literal column header strings and page ranges to encode); keep it flat/simple since Phase 1 only needs the file to *load and validate required keys*, not drive real extraction yet.

3. **Whether `daten/zwischen/` should be git-tracked in Phase 1 despite being empty**
   - What we know: Claude's Discretion in CONTEXT.md recommends tracking it (for Phase 4's diff-check), and all four `daten/*` subdirectories need to exist per SETUP-01.
   - What's unclear: Nothing blocking — this is confirmed as the planner's call, with a stated recommendation.
   - Recommendation: Follow the CONTEXT.md recommendation — add `.gitkeep` files to all four empty `daten/*` subdirectories now so the directory structure exists from Phase 1 onward.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | Pipeline project management (SETUP-02) | ✓ | 0.9.26 `[VERIFIED this session]` | — |
| Python 3.12 (managed) | `.python-version`/`requires-python` (D-13) | ✓ (via uv, not system default) | 3.12.12 `[VERIFIED: "uv python install 3.12" this session]` | System `python3` is 3.14.4 — do not rely on it directly; always invoke via `uv run`/`uv sync` so the pinned 3.12 is used |
| Node.js | App build/lint/typecheck (SETUP-03, QUAL-01) | ✓ | v22.22.1 `[VERIFIED this session]` | Satisfies Vite's `^20.19.0 \|\| >=22.12.0` and the scaffold's `^22.18.0 \|\| >=24.12.0`; GitHub Actions' `setup-node@v7` with `node-version: 22` will resolve a current 22.x independently |
| npm | Package management for `app/` | ✓ | 9.2.0 `[VERIFIED this session]` | — |
| Network: npmjs.org registry | `npm install`/`npm create vue@latest` | ✓ | — `[VERIFIED: "curl -sI https://registry.npmjs.org" this session → HTTP 200; multiple successful "npm install"/"npm view" calls this session]` | — |
| Network: pypi.org | `pip index versions`/`uv add` | ✓ | — `[VERIFIED: multiple successful "pip index versions"/"uv add" calls this session]` | — |
| Network: github.com | `uv python install` (downloads from python-build-standalone releases), GitHub Releases API queries | ✓ | — `[VERIFIED: "curl -sI https://github.com"→200, "uv python install 3.12" succeeded downloading from a GitHub-hosted release, GitHub Releases API queries succeeded this session]` | — |
| Network: docs.astral.sh, webawesome.com | Reading official docs pages directly | ✗ (blocked — `Approval required for <host>` in this sandbox) | — | Used WebSearch + GitHub raw content + actual package inspection (`node_modules/`) instead; no functional gap, all needed facts were obtained via other verified routes |
| GitHub remote for this repo | CI actually running on GitHub | ✗ (none configured — `[VERIFIED: "git remote -v" this session → empty]`) | — | Expected per D-18 — Phase 1 verifies all CI commands locally; the user creates the remote and pushes themselves |

**Missing dependencies with no fallback:** none — the one "✗" (GitHub remote) is an intentional, already-decided-on state per D-18, not a gap.

**Missing dependencies with fallback:** `docs.astral.sh`/`webawesome.com` direct fetch (worked around via WebSearch + live package/registry inspection, with no loss of verified detail — see Code Examples/Architecture Patterns for the specifics those sites would have otherwise provided).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (pipeline); no app-side unit test framework introduced in Phase 1 — v1 scope's only app-level automated check beyond build/type-check/lint is the Playwright smoke test, which is explicitly QUAL-02 in Phase 7, not this phase |
| Config file | `pipeline/pyproject.toml` (pytest picks up config from here by default; no separate `pytest.ini`/`conftest.py` needed for a smoke test this small — add `conftest.py` only if the planner finds shared fixtures are needed) |
| Quick run command | `cd pipeline && uv run pytest -q` |
| Full suite command | `cd pipeline && uv run pytest` (same suite in Phase 1 — no slow tests yet) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SETUP-02 | `uv run pytest` runs green in `pipeline/` | smoke | `cd pipeline && uv run pytest -q` | ❌ Wave 0 — `pipeline/tests/test_rauchtest.py` needs to be created |
| SETUP-05 | Jahrgangsdatei loads, has required keys | unit | `cd pipeline && uv run pytest -q -k jahrgangsdatei` | ❌ Wave 0 — same file as above |
| D-12 (Rauchtest) | Sollwertdatei loads; PDF exists with 400 pages | unit/smoke | `cd pipeline && uv run pytest -q -k "sollwertdatei or pdf"` | ❌ Wave 0 — same file |
| SETUP-03 | `npm run build` succeeds (Vite + vue-tsc) | build/typecheck | `cd app && npm run build` | ❌ Wave 0 — app doesn't exist yet; this phase creates it |
| QUAL-01 | `vue-tsc` and ESLint run error-free | typecheck/lint | `cd app && npm run type-check && npm run lint` | ❌ Wave 0 — same as above; this research verified the commands work once the scaffold exists |

### Sampling Rate
- **Per task commit:** `cd pipeline && uv run pytest -q` and/or `cd app && npm run build` depending on which side the task touched
- **Per wave merge:** Full suite — `uv run pytest` (pipeline) + `npm run build && npm run lint && npm run format:check` (app)
- **Phase gate:** Both full suites green, plus a local dry-run of the full `ci.yml` command sequence (since D-18 means no actual CI run happens yet) before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `pipeline/tests/test_rauchtest.py` — covers SETUP-02, SETUP-05, D-12
- [ ] `pipeline/jahrgaenge/2026.toml` + `2026_sollwerte.toml` — data files the tests load (SETUP-05, D-06/D-07/D-08)
- [ ] `pipeline/ostbevern/konfiguration.py` — the loader the tests and all scripts import (D-09)
- [ ] App scaffold itself (`app/`) — does not exist yet; created via `npm create vue@latest` per this research's verified sequence (SETUP-03)
- [ ] `app/package.json` script `format:check` — not present in the default `create-vue` scaffold (only `format` with `--write` exists); add `"format:check": "prettier --check src/"` for D-16/CI
- [ ] Framework install: `cd pipeline && uv add --dev pytest` (if not already run) — `[VERIFIED: command works this session]`

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Static site, no accounts, no login anywhere in v1 scope (confirmed against REQUIREMENTS.md "Out of Scope": "Backend, Nutzerkonten") |
| V3 Session Management | No | No sessions exist — no backend, no cookies set by this app |
| V4 Access Control | No | No protected resources; everything served is public static content |
| V5 Input Validation | Partial — applies to the **pipeline**, not the app, in this phase | The pipeline's Jahrgangsdatei loader (`lade_jahrgang`) validates required TOML keys are present (D-12) before use — this *is* input validation for a config file acting as a trust boundary between "what the TOML author wrote" and "what the pipeline assumes exists." Standard control: explicit required-key check + typed dataclass, as shown in Code Examples, rather than trusting the TOML blindly |
| V6 Cryptography | No | No cryptographic operations anywhere in this phase or in v1 scope (no auth, no secrets transmitted) |
| V10/V14 Dependency & Supply-Chain | Yes | Covered by the Package Legitimacy Audit above — every new dependency introduced this phase was checked via `gsd_run query package-legitimacy check`, cross-referenced against its canonical GitHub org, and had its `postinstall` scripts inspected (`[VERIFIED: npm view <pkg> scripts.postinstall this session → empty for all npm packages]`) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Malicious/typosquatted npm or PyPI package slipped into `package.json`/`pyproject.toml` | Tampering | Package Legitimacy Audit (above) run for every dependency this phase introduces; planner adds `checkpoint:human-verify` before install tasks per the audit's disposition |
| Path traversal via a maliciously-crafted `pdf_pfad` value in the Jahrgangsdatei (relevant from Phase 2 onward, when the pipeline actually opens the file) | Tampering/Information Disclosure | Not exploitable in Phase 1 (no untrusted TOML author — the file is authored by the project team, not end users), but worth a forward-looking note for the planner: `lade_jahrgang` should resolve `pdf_pfad` relative to a fixed project root, not accept absolute/traversal-capable paths unchecked, once Phase 2+ wires real PDF reads to it |
| Supply-chain: a compromised `postinstall` script in a transitive npm dependency | Tampering | `[VERIFIED: npm view <pkg> scripts.postinstall this session for every direct npm dependency → none found]`; standard mitigation is `npm ci` (not `npm install`) in CI for reproducible, lockfile-pinned installs — already specified in the `ci.yml` example above |

## Sources

### Primary (HIGH confidence — verified live in this sandbox this session)
- `uv --version`, `uv python list`, `uv python install 3.12`, `uv init`, `uv add`, `uv run pytest`, `uv run ruff check/format` — ran directly, outputs inspected
- `npm create vue@latest -- --ts --router --eslint --prettier --bare`, `npm install`, `npm run build`, `npm run lint` — ran directly against a real scaffold, including with `@awesome.me/webawesome` + `vue-echarts` wired into `App.vue`
- `node_modules/@awesome.me/webawesome/dist/webawesome.d.ts`, `.../utilities/base-path.d.ts`, `.../dist/styles/color/variants/brand.css` — read directly, quoted verbatim above
- `npm view <pkg> version/peerDependencies/engines/scripts.postinstall` for every npm package named in this research
- `pip index versions <pkg>` for every PyPI package named in this research
- `gsd_run query package-legitimacy check` — ran for all 19 packages
- `pdfplumber` against the real `raw_data/Haushalt 2026 komplett.pdf` — confirmed 400 pages
- `git ls-files`/`git remote -v`/`git status` against this actual repo
- GitHub Releases API (`api.github.com/repos/.../releases/latest`) for `astral-sh/setup-uv`, `actions/setup-node`, `actions/checkout`

### Secondary (MEDIUM confidence — official docs/source fetched this session)
- `raw.githubusercontent.com/ecomfe/vue-echarts/main/README.md` — on-demand import pattern
- WebSearch results citing `typer.tiangolo.com`, `docs.astral.sh/uv`, `docs.pola.rs`, `github.com/astral-sh/ruff` for API/CLI shape (cross-checked against this session's own live command runs where possible)

### Tertiary (LOW confidence — WebSearch only, not independently re-verified)
- `astral-sh/setup-uv` action input names (`version`, `version-file`, `python-version`) — summarized from WebSearch of the action's own docs/README rather than fetched directly (docs.astral.sh was blocked by sandbox network policy); the version *number* (v10.2.0) was independently confirmed via the GitHub Releases API, but the exact input-parameter list was not independently re-verified against `action.yml`

## Metadata

**Confidence breakdown:**
- Standard stack (pipeline): HIGH — every version and behavior verified by actually running the tools in this sandbox
- Standard stack (app): HIGH — full scaffold-to-build-to-lint cycle verified end-to-end, including the two riskiest integration points (Web Awesome custom elements, vue-echarts tree-shaking)
- Architecture: HIGH — directly derived from SPEZIFIKATION.md §7 (read this session) and CONTEXT.md's locked decisions, cross-checked against a real scaffold's generated file tree
- Pitfalls: HIGH — each pitfall traces to a concrete, reproduced observation in this session (not speculative)
- CI workflow specifics (action version pins): MEDIUM — version numbers verified via GitHub API, but the workflow YAML itself was not run against an actual GitHub Actions runner (D-18: no remote exists yet to run it against)

**Research date:** 2026-10-01
**Valid until:** 2026-10-15 (14 days) — shorter than the usual 30-day default because this research explicitly documents several very recent major-version transitions (vue-router 5, ESLint 10 flat config + oxlint, TypeScript 7 vs. scaffold's 6.x pin) in a fast-moving part of the npm ecosystem; re-verify exact versions if planning is delayed past this window.
