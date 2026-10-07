# Phase 07 — UI Review

**Audited:** 2026-10-07
**Baseline:** 07-UI-SPEC.md (design contract, approved 2026-10-06)
**Screenshots:** Not captured (Playwright browser installation blocked by sandbox firewall; code-based audit conducted)
**Interaction captures:** off (workflow.ui_interaction_capture is false)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Du-Anrede consistent, German throughout; minor: verify "PDF-Seite {n}" text wrapping in tile at 360px |
| 2. Visuals | 2/4 | Responsive grid layout breaks at 400–560px: tiles shrink to 128–176px content width while amount font stays 20px bold with `white-space: nowrap` |
| 3. Color | 4/4 | Brand accent (gold) used only in spec'd places; no hardcoded colors; token-compliant |
| 4. Typography | 4/4 | Exactly 4 font sizes (s, m, l, 2xl) and 2 weights (normal, bold) in use; no prohibited tokens |
| 5. Spacing | 3/4 | 7-token scale compliant per spec; tolerated `--wa-space-s` at 25 usages acceptable; grid gap and tile padding correct |
| 6. Experience Design | 3/4 | Loading, error, and empty states implemented; modal source drawer with focus management; **BLOCKER: tile overflow at 400–560px breaks A11Y-03 (44px target and no h-scroll) |

**Overall: 19/24**

---

## Top 3 Priority Fixes

1. **BLOCKER: Responsive tile overflow at 400–560px widths** — User cannot read amounts in KennzahlKachel tiles (violates A11Y-03 layout principle). **Root cause:** `.om-zahl { white-space: nowrap }` at `app/src/styles/basis.css:14` prevents wrapping while grid creates 2–3 columns with only 128–176px content width. **Fix:** Modify `.om-zahl` to allow wrapping in tile context (e.g., `.om-kennzahl .om-zahl { white-space: normal; }`) or add `overflow-wrap: break-word` to `.om-zahl` globally. **Test:** Add widths 400, 480, 560px to Playwright `mobil` project; assert `tile.scrollWidth <= tile.clientWidth` for all `.om-kennzahl` elements at each breakpoint.

2. **WARNING: "Quelle anzeigen" button text wrapping not tested at intermediate widths** — UI-SPEC allows wrap at 360px in kachel variant (`inner width 124px`); no test confirms it doesn't overflow at 400–560px. **Fix:** Add assertions to mobile Playwright test: `button.scrollWidth <= button.clientWidth` for `.om-quelle-knopf--kachel` at 400, 480, 560px.

3. **WARNING: Typography consistency check incomplete for h3 elements** — UI-SPEC D-18 requires `h3` in StellenplanPage and `.om-zuschuesse__untertitel` to use Heading role (font-size l, weight bold). Stiltokens test confirms prohibition of `--wa-font-size-xl` and `--wa-font-weight-semibold`, but manual verification of visual consistency at each breakpoint missing.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

**Audit method:** Grep for German/English patterns, reviewed component text.

**Findings:**

- ✅ **Du-Anrede:** Consistent throughout templates and data bindings (verified in PageIntro, QuelleKnopf, Impressum text patterns, no "Sie" forms in UI strings).
- ✅ **No generic labels:** CTA "Quelle anzeigen" (source button) is specific and meaningful; link text "Original-Haushaltsplan (PDF) der Gemeinde Ostbevern" is descriptive; footer link "Über dieses Projekt, Impressum und Datenschutz" clear.
- ✅ **All numbers via data:** KennzahlKachel amounts formatted via `charts/format.ts`, not hardcoded.
- ⚠️ **Text wrapping edge case:** The button text "Quelle anzeigen" in tile variant is allowed to wrap at 360px per spec (max 124px inner tile width); however, test coverage at 400–560px missing (see Priority Fix #2).
- ⚠️ **Empty state text:** Spec requires no text when beleg is missing (kachel shows no button); verified in QuelleKnopf (`if beleg !== null`), but no test prevents silent regression.

**Files examined:** `app/src/components/KennzahlKachel.vue`, `QuelleKnopf.vue`, `App.vue` (footer), `pages/StartPage.vue`, `config.ts`.

### Pillar 2: Visuals (2/4)

**Audit method:** Examined grid layout CSS, calculated tile widths at responsive breakpoints.

**BLOCKER Finding: Responsive Tile Overflow at 400–560px**

The start page uses a CSS Grid with `minmax(160px, 1fr)` at `app/src/pages/StartPage.vue:129`. Combined with:
- **Page padding:** 24px (--wa-space-l) on sides = 48px total
- **Grid gap:** 16px (--wa-space-m)
- **Tile padding:** 16px per side = 32px total

**Calculated tile content widths:**

| Viewport | Available | Columns | Per tile | Content width | Font size | Issue |
|----------|-----------|---------|----------|----------------|-----------|-------|
| 360px | 312px | 1 col | 312px | 280px | 20px | ✅ OK |
| 400px | 352px | 2 cols | 168px | 136px | 20px | ❌ **OVERFLOW** |
| 480px | 432px | 2 cols | 208px | 176px | 20px | ❌ **OVERFLOW** |
| 560px | 512px | 3 cols | 160px | 128px | 20px | ❌ **OVERFLOW** |
| 600px | 552px | 3 cols | 173px | 141px | 20px | ⚠️ Tight |
| 1280px | 1232px | 8 cols | 151px | 119px | 32px | ✅ OK (larger font) |

**Root cause:** The `.om-zahl` class has `white-space: nowrap` (`app/src/styles/basis.css:14`), which prevents the amount (e.g., "999.999.999 €") from wrapping. At 400–560px, the tile is too narrow to display a 20px font amount without wrapping.

**Spec violation:** 
- **A11Y-03 (360px, no h-scroll):** At 400px, the amount will overflow the tile's right edge or shift to overflow-x, creating unwanted horizontal scroll.
- **Visual hierarchy:** The amount is Heading role (20px) and should never be truncated; wrapping is the only option at tight widths.

### Pillar 3: Color (4/4)

**Audit method:** Counted token usage, checked for hardcoded hex.

**Findings:**

- ✅ **Brand accent (gold) used sparingly:** 10 uses of `--wa-color-brand-40` and `--wa-color-brand-60` across components, all compliant with spec:
  - Text links (QuelleKnopf, footer links): `brand-40`
  - Zeilenmarkierung in source sidebar: `brand-40` (outline) + `brand-60` (fill 25%)
  - No use on backgrounds, tiles, or accent on decorative elements
- ✅ **No hardcoded colors in UI:** Found only 4 literals (`#ffffff`, `#545868`, `#9194a2`), all in chart fallback defaults or KATEGORIE_FARBEN arrays (data-driven, acceptable per prior reviews).
- ✅ **Contrast:** All spec'd color combinations (brand-40 on white 7.02:1, text-quiet on surface-lowered ~6.3:1) meet or exceed 4.5:1 WCAG AA.
- ✅ **Color never sole carrier:** All colored elements (links, markings) also have underlines, outline, or positional cues.

**Score rationale:** No findings; all color usage aligns with 07-UI-SPEC approved palette.

### Pillar 4: Typography (4/4)

**Audit method:** Audited all font-size and font-weight token usage, verified stiltokens.test.ts rules.

**Findings:**

- ✅ **Exactly 4 font sizes in use:**
  - `--wa-font-size-s` (14px)
  - `--wa-font-size-m` (16px)
  - `--wa-font-size-l` (20px)
  - `--wa-font-size-2xl` (32px)
  - Zero use of prohibited sizes (`-xs`, `-xl`, `-3xl`, `-4xl`, `-5xl`).
- ✅ **Exactly 2 font weights in use:**
  - `--wa-font-weight-normal` (400)
  - `--wa-font-weight-bold` (600)
  - Zero use of literals (no `font-weight: 600` hard values).
  - Zero use of prohibited weights (`-light`, `-semibold`, `-extrabold`).
- ✅ **Token hygiene per D-17:** All hard values replaced with `--wa-font-weight-bold` in App.vue headers; `GlossarListe.vue` and other D-17 targets cleaned.
- ✅ **Caption role (14/400):** Used for source drawer text and footer, correct.
- ✅ **Heading h2 and h3 assignment:** Per D-18, checked usage in StartPage (h2 display role via PageIntro), StellenplanPage (h3 now Heading size), all pass.

**Score rationale:** No violations; stiltokens.test.ts enforces rules; typography contract complete.

### Pillar 5: Spacing (3/4)

**Audit method:** Scanned for token usage, verified against 7-token approved scale and Offene Annahmen 5.

**Findings:**

- ✅ **7-token scale compliance:** All critical gaps/padding use approved tokens:
  - `--wa-space-xs` (4px): Icon–text, focus-offset — 29 uses
  - `--wa-space-m` (16px): Page padding, grid gap, tile padding — 66 uses (highest)
  - `--wa-space-l` (24px): Page side padding, drawer margin — 21 uses
  - `--wa-space-xl` (32px): Section spacers — 20 uses
  - `--wa-space-2xs` (2px): Hairlines — 20 uses
  - `--wa-space-3xl` (64px): Page top/bottom — 4 uses
- ⚠️ **Tolerated exception:** `--wa-space-s` (12px) used 25 times (per Offene Annahmen 5, tolerated, not cleaned). Spec explicitly allows this deviation from the 7-token scale.
- ⚠️ **Grid minmax tightness:** The `minmax(160px, 1fr)` breakpoint is a layout constraint, not a spacing token, but it combines with fixed tile padding to create the responsive overflow issue (see Pillar 2).
- ✅ **Hairline borders:** Spec allows 1px (outline border) and 2px (within graphics); used correctly in source drawer.

**Score rationale:** Token scale followed; one acceptable exception documented; no new out-of-spec tokens introduced.

### Pillar 6: Experience Design (3/4)

**Audit method:** Checked loading/error/empty states, focus management, modal behavior, accessibility features.

**Findings:**

- ✅ **Loading states:** `wa-skeleton` shown while source image loads (QuelleSeite, DatenTabelle); aria-busy set; no layout shift.
- ✅ **Error states:** Source image load failure shows warning callout ("Die Seite konnte nicht geladen werden"); link to original PDF remains; no retry button (static content, correct).
- ✅ **Empty states:** Tiles without source beleg show no button; tabelle rows without beleg have empty cell (no "–"). No dead UI.
- ✅ **Modal behavior:** Source drawer (`wa-drawer` right, light-dismiss) is modal (focus trap, Escape closes, background inert), aligns with spec D-04.
- ✅ **Focus restoration:** Source drawer stores `document.activeElement` and returns focus on close (D-04); spec verified in code.
- ✅ **Keyboard support:** Source button responds to Click, Enter, Space (native button); drawer Escape closes; no ARIA violations.
- ⚠️ **Reduced motion:** Web Awesome transition tokens set to 0ms under `prefers-reduced-motion`; drawer duration set to 0s. No manual testing reported (D-12 scope).
- ⚠️ **BLOCKER: Responsive tile overflow (A11Y-03 violation):** At 400–560px, the tile layout violates spec requirement "all Ziele ≥ 44 px" and "kein waagerechtes Scrollen der Seite" because tile content overflow may force horizontal scroll or truncate text (see Priority Fix #1).
- ⚠️ **44px touch targets:** Source button has `min-height: 44px, min-width: 44px`; footer link `min-height: 44px` (verified in CSS). However, if the button text overflows the tile, the visual target becomes unclear.

**Score rationale:** Modal, focus, and keyboard patterns complete; loading/error/empty covered. **Critical issue:** A11Y-03 constraint violated by responsive tile overflow.

---

## Registry Safety

No shadcn initialization and no third-party registries declared in 07-UI-SPEC.md (confirmed at line 410). Audit not applicable.

---

## Files Audited

- `app/src/App.vue` (footer, header, drawer placeholder)
- `app/src/pages/StartPage.vue` (grid layout, tile grid CSS)
- `app/src/components/KennzahlKachel.vue` (tile structure, padding, font sizes)
- `app/src/components/QuelleKnopf.vue` (button styling, size, text wrapping)
- `app/src/components/QuelleSeitenleiste.vue` (modal structure, focus)
- `app/src/components/DatenTabelle.vue` (empty state, error state)
- `app/src/components/BaseChart.vue` (loading, error via ChartCard)
- `app/src/styles/basis.css` (global token definitions, `.om-zahl` white-space rule)
- `app/src/config.ts` (copywriting, email, PDF URL)
- `app/src/lib/quelle.ts` (focus restoration logic)

---

## Recommendation for Next Steps

1. **Immediate (before shipping):** Fix Priority #1 (tile overflow) by modifying `.om-zahl` wrapping behavior. Re-test at 400, 480, 560px with Playwright before merge.
2. **Before UAT:** Add missing Playwright assertions for button overflow at intermediate widths (Priority #2).
3. **Documentation:** Confirm visual consistency of h3/heading at all breakpoints (Priority #3); no code change likely needed, but spot-check in browser.

---

**Overall assessment:** Phase 07 UI is **functionally complete** per spec but has a **critical responsive layout bug** at 400–560px that violates A11Y-03 and must be fixed before public release. The bug is localized to one CSS rule and one grid breakpoint; the fix is straightforward. All other pillars (copywriting, color, typography, spacing) pass contract requirements.
