---
phase: 01-setup
fixed_at: 2026-10-01T10:15:00Z
review_path: .planning/phases/01-setup/01-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 01: Code Review Fix Report

**Fixed at:** 2026-10-01T10:15:00Z
**Source review:** .planning/phases/01-setup/01-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (fix_scope: critical_warning — Critical: 0, Warning: 5; Info findings out of scope)
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: No `base` path configured for GitHub Pages project hosting

**Files modified:** `app/vite.config.ts`
**Commit:** 21a5f2d
**Applied fix:** Set `base: './'` in `vite.config.ts` (relative base, works with the hash router) instead of hardcoding a repo name, since the repo has no remote yet and the final GitHub repository name is undecided. Verified with a live `npm run build`: `dist/index.html` now references `./assets/index-*.js`, `./assets/index-*.css`, and `./favicon.ico` (all relative), which resolves correctly under any GitHub Pages project-page subpath.

### WR-02: `prefers-reduced-motion` is a stated a11y requirement but is implemented nowhere

**Files modified:** `app/src/styles/basis.css`
**Commit:** 1bf3ad4
**Applied fix:** Added a global `@media (prefers-reduced-motion: reduce) { wa-skeleton::part(indicator) { animation: none; } }` rule. Confirmed against the installed Web Awesome package source (`chunk.XQCWQFLH.js`) that `wa-skeleton`'s shadow DOM renders `<div part="indicator" class="indicator">`, so `::part(indicator)` is the correct, currently-exposed selector to disable the `sheen`/`pulse` animation.

### WR-03: Unsafe `as number` casts in `DatenTabelle.vue` with no runtime check against `spalte.art`

**Files modified:** `app/src/components/DatenTabelle.vue`
**Commit:** f7e9544
**Applied fix:** Replaced the three `as number` casts (euro/zahl/prozent columns) with a new `alsZahl()` guard that throws a `TypeError` if the cell value isn't actually a `number`, so a data/schema mismatch fails loudly instead of silently rendering `NaN`/garbage. Widened the guard's parameter type to `string | number | null | undefined` to match the actual indexed-access type TypeScript infers for `zeile[spalte.schluessel]` (the project's `tsconfig` has `noUncheckedIndexedAccess`-equivalent strictness) — `vue-tsc --build` caught this and the fix was adjusted before commit.

### WR-04: ECharts theme tokens are read once at module load and never update

**Files modified:** `app/src/charts/echartsTheme.ts`
**Commit:** 80989bd
**Applied fix:** Added the documentation-only `ACHTUNG` comment the review suggested, directly above the `token()` helper, flagging that `ersatz` fallback values are a manual copy of the installed Web Awesome CSS and are not automatically kept in sync if the CSS tokens change later (e.g. a future theme toggle). No behavioral change, per the review's own "at minimum" framing — this finding described a one-shot-by-design limitation, not a bug to code around yet.

### WR-05: `DatenTabelle`'s `spalten` prop is optional but required whenever `zeilen` is passed

**Files modified:** `app/src/components/DatenTabelle.vue`
**Commit:** 6860d21
**Applied fix:** Added a dev-only `watchEffect` that emits `console.warn('DatenTabelle: \`zeilen\` wurde ohne \`spalten\` übergeben.')` whenever the component is in data mode (`zeilen` provided) but `spalten` is empty/missing, gated by `import.meta.env.DEV` so it's stripped from production builds. Used `watchEffect` instead of a one-shot setup-time check so the warning also fires if `spalten`/`zeilen` change reactively after mount, not just on initial render.

## Skipped Issues

None — all in-scope findings were fixed.

---

## Verification

All gates re-run inside the isolated review-fix worktree (`workflow.use_worktrees` was not disabled, so this run created and used `.claude/worktrees/rf-01-*`; `app/node_modules` was restored via `npm ci` and the pipeline `.venv` via `uv run`, both not present in the worktree by default) after the final fix (WR-05), confirming no regressions across all five commits:

- `app/`: `npm run type-check` — pass (no errors)
- `app/`: `npm run lint` — pass (no errors)
- `app/`: `npm run format:check` — pass (`prettier --check src/`, plus explicit `npx prettier --check` on each modified non-`src` file: `vite.config.ts`)
- `app/`: `npm run build` — pass; `dist/index.html` inspected and confirmed relative asset paths (WR-01)
- `pipeline/`: `uv run pytest -q` — 17 passed
- `pipeline/`: `uv run ruff check .` — all checks passed
- `pipeline/`: `uv run ruff format --check .` — 6 files already formatted

These results were produced in the worktree environment (`.claude/worktrees/rf-01-*`, now removed by the cleanup tail) and are reproducible from the main checkout by re-running the same commands against the fast-forwarded `main` branch.

---

_Fixed: 2026-10-01T10:15:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
