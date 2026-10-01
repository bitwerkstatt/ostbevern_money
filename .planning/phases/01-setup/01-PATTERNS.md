# Phase 1: Setup - Pattern Map

**Mapped:** 2026-10-01
**Files analyzed:** 27 (new)
**Analogs found:** 0 in-repo / 7 external (Münster reference, read-only) / 20 no-analog (use RESEARCH.md Code Examples)

## Ground Truth: Greenfield Repo

`git ls-files` / `find` confirm the repository contains **no application code** of any kind.
Tracked, non-planning content is limited to:

```
discussion/Haushalt 2026 komplett.pdf
discussion/SPEZIFIKATION.md
raw_data/Haushalt 2026 komplett.pdf
```

`.claude/**` is GSD tooling (gitignored install/runtime mirror in part, and in any case not
project code) and **must never be used as an analog** per the tracked-source gate. There is
**no `pipeline/`, no `app/`, no `.github/`** directory yet. Consequently this phase has **zero
in-repo analogs** for any file it creates — every "Pattern Assignment" below either points to
(a) the external Münster reference repo as a **naming/props template only** (per D-01/D-02 —
read, do not copy, do not clone), or (b) the verified, sandbox-tested Code Examples already
captured in `01-RESEARCH.md`, which the planner should treat as the de facto analog since no
closer one exists.

No PATTERNS.md section below cites an in-repo path as an analog. Where "Closest Analog" says
"external reference (names/props only)" or "RESEARCH.md Code Examples (verified)", that is a
deliberate statement of absence, not an omission.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pipeline/pyproject.toml` | config | batch | RESEARCH.md Code Examples (`pyproject.toml` shape, line ~536-569) | no in-repo analog — use verified example |
| `pipeline/.python-version` | config | batch | RESEARCH.md Standard Stack (D-13) | no in-repo analog |
| `pipeline/ostbevern/konfiguration.py` | service/utility | CRUD (config load) | RESEARCH.md Pattern 1 (`lade_jahrgang`, line ~309-350) | no in-repo analog — use verified example |
| `pipeline/jahrgaenge/2026.toml` | config | batch | RESEARCH.md Architecture (Recommended Project Structure) + SPEZIFIKATION.md §2 | no in-repo analog — content sourced from spec |
| `pipeline/jahrgaenge/2026_sollwerte.toml` | config | batch | SPEZIFIKATION.md Anhang B | no in-repo analog — structure only (D-08) |
| `pipeline/01_seiten_klassifizieren.py` … `08_quellenbelege.py` | controller (CLI) | request-response (CLI invocation) | RESEARCH.md Pattern 2 (thin typer CLI, line ~352-375) | no in-repo analog — use verified example |
| `pipeline/alle.py` | controller (CLI orchestrator) | batch | RESEARCH.md Pattern 2 (same shape, orchestrates sub-commands) | no in-repo analog |
| `pipeline/tests/test_rauchtest.py` | test | batch | RESEARCH.md Code Examples (`test_rauchtest.py` shape, line ~571+) | no in-repo analog — use verified example |
| `app/package.json` + scaffold (`vite.config.ts`, `tsconfig*.json`, `eslint.config.ts`) | config | request-response (build) | `npm create vue@latest -- --ts --router --eslint --prettier --bare` scaffold output (external, officially generated — not hand-written) | generated, not hand-authored — no analog needed |
| `app/src/main.ts` | provider/bootstrap | request-response | RESEARCH.md Pattern 3 (Web Awesome wiring, line ~401-414) | no in-repo analog — use verified example |
| `app/src/router/index.ts` | route | request-response | RESEARCH.md Pattern 4 (hash-router swap, line ~433-447) | no in-repo analog — use verified example |
| `app/src/components/PageIntro.vue` | component | request-response (presentational) | External: `codeformuenster/haushalt-muenster-2026` `PageIntro.vue` — **names/props only (D-02), read not copied** | no in-repo analog; external naming template |
| `app/src/components/ChartCard.vue` | component | request-response (presentational, slot-based) | External: Münster `ChartCard.vue` — names/props only | no in-repo analog; external naming template |
| `app/src/components/BaseChart.vue` | component | streaming/transform (renders chart data via vue-echarts) | External: Münster `BaseChart.vue` — names/props only; implementation per RESEARCH.md Pattern 5 (line ~449-465) | no in-repo analog; external naming template + verified echarts pattern |
| `app/src/components/DatenTabelle.vue` | component | transform (tabular render) | External: Münster `DatenTabelle.vue` — names/props only; no WA `<wa-table>` exists, build on semantic `<table>` (UI-SPEC note) | no in-repo analog; external naming template |
| `app/src/charts/format.ts` | utility | transform | External: Münster `charts/format.ts` — names/signature only (D-02) | no in-repo analog; external naming template |
| `app/src/charts/echartsTheme.ts` | utility/config | transform | External: Münster `charts/echartsTheme.ts` — names/signature only; token source per UI-SPEC Color section | no in-repo analog; external naming template |
| `app/src/lib/bildschirm.ts` | utility/hook | event-driven (viewport breakpoint) | External: Münster `lib/bildschirm.ts` — names/signature only | no in-repo analog; external naming template |
| `app/src/views/StartView.vue` (or `App.vue` demo) | component | request-response (presentational, demo data) | RESEARCH.md Pattern 4 route wiring + UI-SPEC Copywriting Contract (demo copy) | no in-repo analog |
| `.github/workflows/ci.yml` | config | event-driven (CI trigger) | RESEARCH.md System Architecture Diagram (two-job shape) + Standard Stack install commands | no in-repo analog — compose from verified commands |
| `.claude/CLAUDE.md` (edit: populate Technology Stack / Conventions / Architecture) | config/doc | batch | Existing file itself (sections currently placeholder, per D-17) | self — fill placeholders, leave GSD-managed sections untouched |
| `LICENSE` | config | batch | Standard MIT license text (D-05) | no analog needed — boilerplate |
| `README.md` | doc | batch | none — new content, must credit Münster Money (D-05) | no analog |
| `.gitignore` | config | batch | Claude's Discretion list in CONTEXT.md (`node_modules`, `.venv`, `dist`, `__pycache__`, `.DS_Store`) | no analog — explicit list given |
| `raw_data/haushalt-2026.pdf` (git mv target) | data file | file-I/O | Source: `raw_data/Haushalt 2026 komplett.pdf` (tracked, to be renamed via `git mv`) | in-repo — this IS the analog, it's a rename |
| `daten/{zwischen,aufbereitet,manuell,pruefberichte}/.gitkeep` | config | batch | none — empty dir placeholders | no analog needed |

## Pattern Assignments

### `pipeline/ostbevern/konfiguration.py` (service, CRUD/config-load)

**Analog:** none in-repo. Use RESEARCH.md Pattern 1 verbatim as the base shape (already
sandbox-verified against Python 3.12 `tomllib` behavior).

**Core pattern** (RESEARCH.md lines ~317-349):
```python
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

**Error handling pattern:** raise `ValueError` listing missing keys — this is the one
validation chokepoint every script/test must go through (anti-pattern: re-parsing TOML ad hoc
elsewhere, called out explicitly in RESEARCH.md Anti-Patterns).

**Default-year convention (D-09):** define `STANDARD_JAHR = 2026` once in this module (or
`ostbevern/__init__.py`); every CLI's `--jahr` option defaults to this constant, never to a
repeated literal.

---

### `pipeline/0N_*.py` / `alle.py` (controller/CLI, request-response)

**Analog:** none in-repo. Use RESEARCH.md Pattern 2.

**Core pattern** (RESEARCH.md lines ~360-375):
```python
import typer
from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang

app = typer.Typer()

@app.command()
def main(jahr: int = typer.Option(STANDARD_JAHR, "--jahr", help="Haushaltsjahr")) -> None:
    konfiguration = lade_jahrgang(jahr)
    typer.echo(f"Seitenklassifikation für Jahrgang {konfiguration.haushaltsjahr} (Platzhalter)")

if __name__ == "__main__":
    app()
```
Every one of the 8 numbered scripts + `alle.py` repeats this shape; `alle.py` additionally
imports and calls the others' `main()` functions (or their underlying library calls) in
sequence rather than shelling out.

---

### `pipeline/tests/test_rauchtest.py` (test, batch)

**Analog:** none in-repo. RESEARCH.md gives the shape only (exact assertions depend on final
TOML structure); D-12 fixes the three required assertions:
1. Jahrgangsdatei lädt und ist vollständig (calls `lade_jahrgang(2026)`, expects no exception).
2. Sollwertdatei lädt (separate loader/parse, no required-keys check beyond "loads").
3. PDF existiert und hat `erwartete_pdf_seiten` Seiten (open `raw_data/haushalt-2026.pdf` with
   `pdfplumber`, assert `len(pdf.pages) == konfiguration.erwartete_pdf_seiten` — value comes
   from the TOML, never hardcoded `400` in the test body, per D-12/Anti-Patterns).

---

### `app/src/main.ts`, `app/src/router/index.ts` (provider/route, request-response)

**Analog:** none in-repo. Use RESEARCH.md Pattern 3 + Pattern 4 verbatim (both sandbox-built
end-to-end this session).

**Web Awesome bootstrap** (RESEARCH.md lines ~401-414):
```typescript
import '@awesome.me/webawesome/dist/styles/webawesome.css'
import '@awesome.me/webawesome/dist/styles/color/variants/brand.css'
import { setIconPath } from '@awesome.me/webawesome'
import '@awesome.me/webawesome/dist/webawesome.js'
setIconPath('/icons')
```
Apply `class="wa-brand-yellow"` to `<html>` to activate the gold accent (UI-SPEC Color
section) — confirmed real in `@awesome.me/webawesome@3.14.0`.

**Hash router** (RESEARCH.md lines ~433-447):
```typescript
import { createRouter, createWebHashHistory } from 'vue-router'
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'start', component: () => import('../views/StartView.vue') },
  ],
})
export default router
```

**Vite custom-element wiring** (RESEARCH.md Pattern 3, lines ~386-399) — required so
`vue-tsc --build` and `vite build` both accept `<wa-*>` tags:
```typescript
import vue from '@vitejs/plugin-vue'
export default defineConfig({
  plugins: [
    vue({ template: { compilerOptions: { isCustomElement: (tag) => tag.startsWith('wa-') } } }),
  ],
})
```

---

### `app/src/components/{PageIntro,ChartCard,BaseChart,DatenTabelle}.vue`, `app/src/charts/{format,echartsTheme}.ts`, `app/src/lib/bildschirm.ts`

**Analog:** external reference only — `github.com/codeformuenster/haushalt-muenster-2026`
(read via browser/WebFetch, **never cloned, never copied** — D-01). Per D-02, adopt only:
- Component/module **names** exactly as listed (`PageIntro`, `ChartCard`, `BaseChart`,
  `DatenTabelle`, `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts`).
- Their **props/interface shape** (e.g. `BaseChart`'s `loading` prop + `error` slot, per
  01-UI-SPEC.md's Project Base Components table).

Implementation is written fresh against:
- UI-SPEC's per-component "Visual contract" column (01-UI-SPEC.md lines 59-67) for styling.
- RESEARCH.md Pattern 5 (on-demand `vue-echarts` imports, lines ~452-464) for `BaseChart`'s
  internals:
  ```typescript
  import { use } from 'echarts/core'
  import { CanvasRenderer } from 'echarts/renderers'
  import { BarChart } from 'echarts/charts'
  import { GridComponent, TooltipComponent } from 'echarts/components'
  import VChart from 'vue-echarts'
  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])
  ```
- `echartsTheme.ts` must read WA CSS custom properties via `getComputedStyle` (`--wa-color-
  brand-*`, `--wa-color-neutral-*`, `--wa-color-danger`, `--wa-color-success`,
  `--wa-font-family-body`, `--wa-space-*`) rather than hardcoding hex — see UI-SPEC Color
  section for the exact token values (`#da7e00` / `#8c4602` accent, WA default danger/success).
- `DatenTabelle` has **no WA analog** (`<wa-table>` does not exist) — build on a semantic
  `<table>`, one `<wa-format-number>` per numeric cell (UI-SPEC note under Component Inventory).

---

### `.github/workflows/ci.yml` (config, event-driven)

**Analog:** none in-repo (no `.github/` directory exists). Compose from RESEARCH.md's
verified command sequences — this file is the only place the two command lists need to be
assembled into job steps:

Pipeline job commands (RESEARCH.md Standard Stack → Installation (pipeline) + D-15):
```
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

App job commands (D-15/D-16):
```
npm ci
npx vue-tsc --build   # or the project's "type-check" script
npm run lint          # ESLint (oxlint pre-step is fine per RESEARCH.md Supporting table)
npm run format:check  # Prettier via eslint-config-prettier, D-16
npm run build
```
Both jobs run on every push/PR, no path filters (D-15). No deploy job — that is Phase 7.

---

### `.claude/CLAUDE.md` (edit, config/doc)

**Analog:** the file itself. Its "Technology Stack", "Conventions", and "Architecture"
sections are explicit placeholders today (confirmed by reading the file) — this phase fills
them per SETUP-04/D-17. Do **not** touch "GSD Workflow Enforcement", "Developer Profile", or
"Project Skills" sections. Conventions to record verbatim (D-17): deutsche Bezeichner ohne
Umlaute, Beträge als int-Euro, nur 1-basierte PDF-Seiten, keine Jahrgangswerte im Code,
Du-Anrede, Zahlen in Texten aus Daten.

---

### `raw_data/haushalt-2026.pdf` (data file, file-I/O)

**Analog:** itself, via rename. Preserve git history with explicit two-step operation
(RESEARCH.md Runtime State Inventory / Pitfall 5):
```bash
git mv "raw_data/Haushalt 2026 komplett.pdf" "raw_data/haushalt-2026.pdf"
git rm "discussion/Haushalt 2026 komplett.pdf"
```

## Shared Patterns

### Single-source year config (all pipeline files)
**Source:** `pipeline/ostbevern/konfiguration.py::lade_jahrgang()` + `STANDARD_JAHR` constant
(RESEARCH.md Pattern 1).
**Apply to:** every `pipeline/0N_*.py`, `alle.py`, `pipeline/tests/test_rauchtest.py`. No
script may call `tomllib.load()` directly or hardcode `2026`/`400`/column headers — those
values live only in `pipeline/jahrgaenge/2026.toml` / `2026_sollwerte.toml`.

### Thin-CLI-over-library (all pipeline scripts)
**Source:** RESEARCH.md Pattern 2.
**Apply to:** `01_seiten_klassifizieren.py` … `08_quellenbelege.py`, `alle.py`. Each file stays
a few lines; real logic (once it exists, Phase 2+) goes in `pipeline/ostbevern/`.

### Web Awesome custom-element wiring (all `.vue` files using `<wa-*>`)
**Source:** RESEARCH.md Pattern 3 (`vite.config.ts` `isCustomElement`, `main.ts` icon
bootstrap).
**Apply to:** every component file from Phase 1 onward that uses a `<wa-*>` tag — `PageIntro`,
`ChartCard`, `BaseChart`, `DatenTabelle`, `StartView.vue`/`App.vue` demo page.

### Number formatting single source of truth
**Source:** `app/src/charts/format.ts` (per D-02/UI-05).
**Apply to:** `DatenTabelle` numeric cells (via `<wa-format-number>`), `BaseChart` tooltip/axis
formatters. No component may call `.toLocaleString()` or hand-roll Euro formatting itself —
flagged explicitly as an anti-pattern in RESEARCH.md.

### Münster naming/props carryover (external reference, read-only)
**Source:** `github.com/codeformuenster/haushalt-muenster-2026` (D-01/D-02) — read via
WebFetch/browser only; never `git clone`d into this repo, never copied file-for-file.
**Apply to:** `PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`,
`charts/echartsTheme.ts`, `lib/bildschirm.ts` — adopt the **name and public
props/interface shape only**; implementation is original, driven by `01-UI-SPEC.md`.

## No Analog Found

All files in this phase lack an in-repo analog (greenfield repo). Files with **no reference
of any kind** (not even external) — planner should design purely from CONTEXT.md/RESEARCH.md:

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `README.md` | doc | batch | New content; only constraint is the Münster credit line (D-05) |
| `LICENSE` | config | batch | Standard MIT boilerplate, no project-specific pattern needed |
| `.gitignore` | config | batch | Content explicitly enumerated in CONTEXT.md discretion section |
| `daten/*/.gitkeep` | config | batch | Trivial placeholder files |
| `app/src/views/StartView.vue` | component | request-response | Phase 1 demo page; copy fixed by UI-SPEC's Copywriting Contract, no structural analog beyond the shared WA-wiring pattern above |
| `pipeline/jahrgaenge/2026.toml` content | config | batch | Field values sourced from `discussion/SPEZIFIKATION.md` §2, not from any code analog |
| `pipeline/jahrgaenge/2026_sollwerte.toml` content | config | batch | Field values sourced from `discussion/SPEZIFIKATION.md` Anhang B, structure-only in Phase 1 (D-08) |

## Metadata

**Analog search scope:** entire working tree (`find . -not -path './.git*'` and `git ls-files`), confirming zero tracked application code outside `.planning/`, `discussion/`, `raw_data/`. `.claude/**` excluded per tracked-source gate (GSD tooling, not project code).
**Files scanned:** full repo listing (4 tracked non-planning files total).
**Pattern extraction date:** 2026-10-01
