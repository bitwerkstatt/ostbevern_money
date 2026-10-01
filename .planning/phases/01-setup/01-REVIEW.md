---
phase: 01-setup
reviewed: 2026-10-01T09:49:58Z
depth: standard
files_reviewed: 48
files_reviewed_list:
  - .claude/CLAUDE.md
  - .github/workflows/ci.yml
  - .gitignore
  - LICENSE
  - README.md
  - app/.editorconfig
  - app/.gitattributes
  - app/.gitignore
  - app/.nvmrc
  - app/.prettierrc.json
  - app/.vscode/extensions.json
  - app/.vscode/settings.json
  - app/env.d.ts
  - app/eslint.config.ts
  - app/index.html
  - app/package.json
  - app/public/icons/solid/bars.svg
  - app/public/icons/solid/circle-info.svg
  - app/public/icons/solid/triangle-exclamation.svg
  - app/src/App.vue
  - app/src/charts/echartsTheme.ts
  - app/src/charts/format.ts
  - app/src/components/BaseChart.vue
  - app/src/components/ChartCard.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/PageIntro.vue
  - app/src/components/chartKontext.ts
  - app/src/components/datenTabelle.ts
  - app/src/data/beispieldaten.json
  - app/src/data/jahrgang.json
  - app/src/lib/bildschirm.ts
  - app/src/lib/webawesome.ts
  - app/src/main.ts
  - app/src/pages/StartPage.vue
  - app/src/router/index.ts
  - app/src/styles/basis.css
  - app/tsconfig.app.json
  - app/tsconfig.json
  - app/tsconfig.node.json
  - app/vite.config.ts
  - pipeline/.python-version
  - pipeline/alle.py
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/__init__.py
  - pipeline/ostbevern/konfiguration.py
  - pipeline/pyproject.toml
  - pipeline/tests/test_alle.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_rauchtest.py
findings:
  critical: 0
  warning: 5
  info: 5
  total: 10
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-10-01T09:49:58Z
**Depth:** standard
**Files Reviewed:** 48
**Status:** issues_found

## Summary

This phase delivers scaffolding only (Vue 3 app shell + Python pipeline config loader + CI), and it is in noticeably good shape: `uv run pytest`, `ruff check`, `ruff format --check`, `vue-tsc --build`, `eslint`, `prettier --check`, and `vite build` were all re-run live during this review and pass cleanly with no errors. `konfiguration.py` in particular has solid, well-tested path-traversal and type-validation guards around untrusted TOML input (absolute-path rejection, `is_relative_to` containment check, strict int/bool type checks for sollwerte).

No Critical/Blocker-level defects were found — there is no injection, no crash path, no data-loss risk, and no hardcoded secret in the reviewed scope. The issues below are real but forward-looking: a GitHub Pages hosting gap that will break the app the moment a deploy workflow is added, a stated accessibility requirement (`prefers-reduced-motion`) that isn't implemented anywhere, and a handful of type-safety/robustness gaps in the new chart/table components that are currently masked by the all-numeric example data but will bite as soon as real pipeline data of varied shape lands in Phase 2.

## Warnings

### WR-01: No `base` path configured for GitHub Pages project hosting

**File:** `app/vite.config.ts:7-22`
**Issue:** `.claude/CLAUDE.md` commits this project to "Hosting: GitHub Pages unter eigenem GitHub-Account" with deployment via GitHub Actions. `vite.config.ts` has no `base` option, so it defaults to `/`. A live `npm run build` (re-run during this review) confirms the emitted `dist/index.html` references `/assets/index-*.js` and `/assets/index-*.css` with absolute root paths, and `app/src/lib/webawesome.ts` resolves icons via `import.meta.env.BASE_URL` which will likewise resolve to `/`. Unless the target repository is itself named `<account>.github.io` (root user/org page), GitHub Pages serves project pages from `https://<account>.github.io/<repo>/`, and every asset reference will 404. There is no deploy workflow yet (`.github/workflows/` only contains `ci.yml`), so this is currently latent, but it is squarely in the scope of files reviewed and will silently break the first Pages deploy if not addressed before that phase.
**Fix:** Either set `base` explicitly once the repo/Pages target is known (e.g. via an env-driven value so local dev still works at `/`):
```ts
export default defineConfig({
  base: process.env.GITHUB_PAGES_BASE ?? '/',
  // ...
})
```
or, if the plan is to host at `<account>.github.io` directly, document that decision so this isn't silently revisited later.

### WR-02: `prefers-reduced-motion` is a stated a11y requirement but is implemented nowhere

**File:** `app/src/styles/basis.css`, `app/src/components/BaseChart.vue:57`, `app/src/components/DatenTabelle.vue:25-27`
**Issue:** `.claude/CLAUDE.md` explicitly lists `prefers-reduced-motion` as a required accessibility behavior ("Barrierefreiheit: Lighthouse a11y ≥ 95, Fokussteuerung, Kontraste, `prefers-reduced-motion`, responsiv ab 360 px."). The app's only animated element so far is `<wa-skeleton effect="sheen">`, used in both loading states. Inspecting the installed Web Awesome package confirms the skeleton's own styles (`node_modules/@awesome.me/webawesome/dist/chunks/chunk.JLCUD5BZ.js`) apply `animation: sheen 8s ease-in-out infinite` (and a `pulse` variant) with no `prefers-reduced-motion` guard inside the component, and a repo-wide grep for `prefers-reduced-motion` across `app/src` returns zero matches. So nothing in this codebase currently honors that stated requirement.
**Fix:** Add a global override, e.g. in `basis.css`:
```css
@media (prefers-reduced-motion: reduce) {
  wa-skeleton::part(indicator) {
    animation: none;
  }
}
```
(adjust the shadow-part selector to whatever Web Awesome exposes) or disable the `sheen`/`pulse` effect conditionally in script when `window.matchMedia('(prefers-reduced-motion: reduce)').matches`.

### WR-03: Unsafe `as number` casts in `DatenTabelle.vue` with no runtime check against `spalte.art`

**File:** `app/src/components/DatenTabelle.vue:66,73,80`
**Issue:** `DatenZeile` is typed as `Readonly<Record<string, string | number | null>>` with no link between a given `DatenSpalte.art` and the actual runtime type of `zeile[spalte.schluessel]`. The template blindly casts the cell value `as number` for `'euro'`, `'zahl'`, and `'prozent'` columns and feeds it straight into `<wa-format-number :value="...">`. Nothing prevents a caller from passing a string into an `'euro'`-typed column (e.g. a formatted amount already computed by the pipeline), which would compile fine (the cast suppresses the type error) and then either render `NaN`/garbage or throw inside the custom element at runtime. This is currently invisible because `StartPage.vue`'s only caller passes all-numeric data.
**Fix:** Narrow at the type level instead of casting past the compiler, e.g. make `DatenZeile` a discriminated shape per column, or add a runtime guard:
```ts
function alsZahl(wert: string | number | null): number {
  if (typeof wert !== 'number') {
    throw new TypeError(`Erwartete Zahl für numerische Spalte, erhalten: ${typeof wert}`)
  }
  return wert
}
```
and call `alsZahl(zeile[spalte.schluessel])` instead of the bare `as number` cast, so a data/schema mismatch fails loudly instead of silently.

### WR-04: ECharts theme tokens are read once at module load and never update

**File:** `app/src/charts/echartsTheme.ts:19-70`
**Issue:** `token()` reads Web-Awesome CSS custom properties via `getComputedStyle` synchronously when `echartsTheme.ts` is first evaluated, and `registerTheme()` is called once at that same moment with the resolved (or fallback) values baked in. If the page's stylesheet hasn't finished applying yet at that point (plausible: the production `dist/index.html` built during this review emits the `<script type="module">` tag *before* the extracted `<link rel="stylesheet">` tag, so the module graph — including this file — can execute before the CSS is guaranteed parsed), the chart silently falls back to the hardcoded `ersatz` literals. Today those literals happen to match the shipped CSS values, so there's no visible defect yet, but the theme has no mechanism to pick up token changes later (a future dark-mode toggle, a brand-class change, or simply a divergence between the hardcoded fallback and updated CSS) — `registerTheme` is a one-shot call, not reactive.
**Fix:** At minimum, add a code comment flagging that `ersatz` values must be kept in sync by hand, and consider re-registering the theme (or reading tokens lazily per-chart-render) if/when the app gains any runtime theme switching:
```ts
// ACHTUNG: ersatz-Werte sind eine manuelle Kopie der installierten
// Web-Awesome-CSS. Sie werden nur beim Modul-Laden einmal gelesen und
// NICHT automatisch aktualisiert, falls sich die CSS-Variablen später
// ändern (z. B. durch Theme-Umschaltung).
```

### WR-05: `DatenTabelle`'s `spalten` prop is optional but required whenever `zeilen` is passed

**File:** `app/src/components/DatenTabelle.vue:6-14,36-86`
**Issue:** `spalten` and `zeilen` are both independently optional props, but the "data mode" branch (`v-else-if="istDatenModus"`) unconditionally does `v-for="spalte in spalten"` for both the header row and each body row. If a caller supplies `zeilen` without `spalten` (an easy mistake — nothing in the type signature prevents it, and `istLeer` only checks `zeilen.length`, not `spalten`), the table renders with a header row and body rows that have zero `<th>`/`<td>` cells — a silently broken, empty-looking table rather than a visible error.
**Fix:** Either make `spalten` required whenever `zeilen` is used by giving the component two distinct prop sets via `withDefaults`/a discriminated prop contract, or add an explicit guard:
```ts
if (import.meta.env.DEV && istDatenModus.value && !props.spalten?.length) {
  console.warn('DatenTabelle: `zeilen` wurde ohne `spalten` übergeben.')
}
```

## Info

### IN-01: Unused icon asset `bars.svg`

**File:** `app/public/icons/solid/bars.svg`
**Issue:** The self-hosted icon set includes `bars.svg` (hamburger-menu icon), but a repo-wide search finds no `<wa-icon name="bars">` usage anywhere in `app/src`. Only `circle-info` and `triangle-exclamation` are referenced.
**Fix:** Either wire it up (e.g. for the mobile nav toggle implied by `useSchmalerBildschirm`) or remove it until it's needed, to avoid shipping dead assets.

### IN-02: Duplicate `pdf_relativ` computation in `alle.py`

**File:** `pipeline/alle.py:43-52`
**Issue:** `jahrgang.pdf_pfad.relative_to(PROJEKT_WURZEL)` is computed twice — once inside the `if not jahrgang.pdf_pfad.is_file():` branch for the error message, and again immediately after for the success message. Harmless today, but it's needless duplication that will drift if one call site is edited and the other isn't.
**Fix:**
```python
pdf_relativ = jahrgang.pdf_pfad.relative_to(PROJEKT_WURZEL)
if not jahrgang.pdf_pfad.is_file():
    typer.echo(f"Fehler: PDF nicht gefunden: {pdf_relativ}", err=True)
    raise typer.Exit(code=1)

typer.echo(
    f"Jahrgang {jahrgang.haushaltsjahr}: {pdf_relativ} "
    f"({jahrgang.anzahlen.pdf_seiten} Seiten erwartet), "
    f"{len(jahrgang.seitenbereiche)} Seitenbereiche, Sollwerte geladen."
)
```

### IN-03: `circle-info` icon used inside a `warning`-variant callout

**File:** `app/src/components/ChartCard.vue:28-31`
**Issue:** The "Beispieldaten" callout is styled `variant="warning"` but uses the `circle-info` icon rather than `triangle-exclamation` (which is already in the self-hosted icon set and used elsewhere for actual error states in `BaseChart.vue`). Minor semantic mismatch between the visual warning styling and the informational icon.
**Fix:** Use `triangle-exclamation` (or switch the callout to `variant="neutral"`/`"brand"` if "informational, not alarming" is the intent) for consistency.

### IN-04: No overlap/positivity validation for Jahrgang config values

**File:** `pipeline/ostbevern/konfiguration.py:125-176`
**Issue:** `lade_jahrgang` validates that each `Seitenbereich` is internally consistent (`1 <= von <= bis <= pdf_seiten`) and that `anzahlen.*` fields are integers, but it never checks that `anzahlen.*` values are non-negative, nor that different `seitenbereiche` entries don't overlap each other (e.g. `gesamtergebnisplan` and `gesamtfinanzplan` could be misconfigured to the same or overlapping page range and the loader would accept it). Given the project's stated accuracy bar ("Abweichungen über 1 € ... gelten als Fehler"), a silently-accepted misconfigured page range is the kind of thing that would produce wrong numbers downstream in Phase 2 without any loader-level signal.
**Fix:** Add an overlap check across `seitenbereiche.values()` and a `>= 0` check for `Anzahlen` fields, raising `KonfigurationsFehler` on violation, consistent with the existing validation style in this module.

### IN-05: Redundant double-labeling of data tables for screen readers

**File:** `app/src/components/DatenTabelle.vue:18-23,37-41`
**Issue:** The outer wrapper gets `role="region"` + `aria-label="{{ beschriftung }}"` whenever `beschriftung` is set, and the `<table>` inside it also gets a visually-hidden `<caption>` with the exact same text. Depending on the assistive-technology/browser combination, this can result in the same label text being announced twice (once entering the labeled region, once entering the table).
**Fix:** Pick one mechanism — either drop the `aria-label`/`role="region"` wrapper when a `<caption>` is already present, or drop the `<caption>` and rely solely on the region label, rather than applying both to the same text.

---

_Reviewed: 2026-10-01T09:49:58Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
