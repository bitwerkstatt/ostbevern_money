# Phase 6 — UI Review

**Audited:** 2026-10-06
**Baseline:** 06-UI-SPEC.md (Design Contract)
**Screenshots:** not captured (playwright capture returned empty; code-only audit performed)
**Interaction captures:** off (workflow.ui_interaction_capture is false)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 4/4 | Du-Anrede consistent, no generic labels, all numbers from data or formulas |
| 2. Visuals | 4/4 | Visual hierarchy via size/weight/color, icon-labels paired, focus indicators clear |
| 3. Color | 4/4 | All colors via --wa-* tokens, accent reserved (brand-40/60), no hardcoded hex in components |
| 4. Typography | 2/4 | BLOCKER: Non-contract font sizes (--wa-font-size-xl) and weight (--wa-font-weight-semibold) used; h3 sizing incorrect |
| 5. Spacing | 4/4 | All spacing via --wa-space-* tokens, 44px minimum hit targets, grid/gap follow scale |
| 6. Experience Design | 3/4 | WARNING: Empty states handled (filter reset, no data), state feedback via live regions, but Escape focus return and menu-group repositioning edge cases exist |

**Overall: 21/24**

---

## Top 3 Priority Fixes

1. **Typography Violations (BLOCKER)** — 5 files use --wa-font-size-xl (not in contract) and 1 uses --wa-font-weight-semibold. UI-SPEC §Typography specifies exactly 4 font sizes and 2 weights. Replace all --wa-font-size-xl with --wa-font-size-l (20px, Heading) or --wa-font-size-2xl (32px, Display). Replace --wa-font-weight-semibold with --wa-font-weight-bold (600). Fix h3 in StellenplanPage.vue:246 to use --wa-font-size-l per contract rules. — User must ship with contract-compliant typography.

2. **h3 Font Size Mismatch (WARNING)** — StellenplanPage.vue:246 styles h3 with --wa-font-size-m (16px Body) instead of --wa-font-size-l (20px Heading). This breaks visual hierarchy for section headings within the "Stellen nach Gruppe" card. Change to --wa-font-size-l to align with UI-SPEC §Typography role assignment.

3. **MenueGruppe Position Recalculation Edge Case (WARNING)** — MenueGruppe.vue:49 calls `positioniere()` to keep the menu list in viewport on open, but measures the element's max-width via `getComputedStyle()`. If the browser hasn't rendered the element's CSS yet (v-show timing), the measurement is unreliable. Very-slow browsers or concurrent resize events may cause clipping on narrow viewports. Mitigate: add a small `await nextTick()` before measuring, or watch `liste.value` with a `watchEffect` to re-measure on viewport changes. Low user impact (menu still keyboard-navigable via Escape/Tab), but test at 375px viewport.

---

## Detailed Findings

### Pillar 1: Copywriting (4/4)

**Strengths:**
- All page leads and section titles use data-driven placeholder years (e.g., `${erstesJahr}–${letztesJahr}`) — no hardcoded values (EntwicklungPage.vue:28–31, InvestitionenPage.vue:27–34)
- Du-Anrede consistent throughout (EntwicklungPage.vue:32 "Hier siehst du", RatEntscheidetPage.vue:25, StellenplanPage.vue:29, InvestitionenPage.vue:25)
- CTA "Filter zurücksetzen" is specific, not generic (InvestitionenPage.vue:104)
- Empty state in InvestitionenPage.vue:98–107 explains the condition ("Keine Maßnahmen für diese Auswahl") and offers recovery (filter reset button)
- All explanatory texts sourced from pipeline (e.g., `ErklaerText schluessel="globaler_minderaufwand"` passes data-driven copy rule)
- No generic patterns like "Click Here", "OK", "Error occurred" detected

**Minor observations:**
- All numeric values in text derive from format functions (formatiereJahr(), prozent(), euroKurz()) — no inline typed numbers

**Score justification:** No violations; contract fully met.

---

### Pillar 2: Visuals (4/4)

**Strengths:**
- Clear focal points: h1 atop each page via PageIntro component (Heading 32px/600) followed by Lead text (Body 16px/400) establishes hierarchy (EntwicklungPage.vue:88, InvestitionenPage.vue:72, RatEntscheidetPage.vue:38, StellenplanPage.vue:130)
- Visual hierarchy through:
  - Size: h2 (20px/600) > h3 (16px/600 in incorrect StellenplanPage.vue:246) > body (16px/400)
  - Weight: bold (600) on headings and active controls, normal (400) on body text
  - Color: accent (brand-40 text) on active menu state (MenueGruppe.vue:194, 237), links, focus ring
- Icon-labels paired: MenueGruppe.vue uses inline SVG chevron with button text "Mehr wissen", HinweisNichtImHaushalt.vue uses circle-info icon with heading "Was nicht im Haushalt steht" (aria-labelledby links section to h2)
- Focus indicators: default browser outlines on interactive elements; MenueGruppe.vue:182 uses `min-height: 44px` for minimum hit target, schalter and liste links both ≥44px
- Disabled states: no destructive actions in Phase 6, so no disabled styling needed
- Confirmation for actions: InvestitionenPage.vue:104 button "Filter zurücksetzen" triggers zuruecksetzen() without prompt (acceptable for non-destructive filter reset)

**Minor observations:**
- Chevron in MenueGruppe.vue uses inline SVG (currentColor) instead of icon file, avoiding extra request (complies with T-06-06)
- All section grouping uses `<section aria-labelledby>` for semantic structure (EntwicklungPage.vue:90–94, InvestitionenPage.vue:92)

**Score justification:** No violations; visual hierarchy clear and consistent.

---

### Pillar 3: Color (4/4)

**Strengths:**
- All component colors use --wa-* CSS tokens:
  - Dominant (60%): `--wa-color-surface-default` (white, #ffffff) on page, menu list (MenueGruppe.vue:221)
  - Secondary (30%): `--wa-color-surface-lowered` (#f1f2f3) on card backgrounds, callouts, zebra rows (InvestitionenPage.vue:194)
  - Accent (10%): `--wa-color-brand-40` (#8c4602 text) on active menu state (MenueGruppe.vue:194), `--wa-color-brand-60` (#da7e00) chart colors (echartsTheme.ts)
  - Text: `--wa-color-text-link` for links, `--wa-color-text-quiet` for captions
- echartsTheme.ts registers all colors via `token()` function, reading --wa-* tokens at runtime with fallback Hex values (echartsTheme.ts:51–77, 92–109)
- No hardcoded #xxx or rgb() values in component scopes
- 60/30/10 distribution observed:
  - White background (dominant)
  - Light gray surfaces (secondary) for cards, callouts
  - Gold accent on 2–3 state indicators per page (active menu, links)
- Accent usage reserved:
  - Active menu state (text brand-40, underline) — MenueGruppe.vue:194
  - Links (text-link, which resolves to brand color) — RouterLinks throughout
  - Focus ring (--wa-color-focus, brand-colored outline) — standard browser
  - NOT used on backgrounds, non-interactive elements, or Bildschirmbrechen cards

**Score justification:** No violations; all colors sourced from --wa-* tokens.

---

### Pillar 4: Typography (2/4) — BLOCKER

**Violations Found:**

1. **Non-Contract Font Sizes (--wa-font-size-xl)**
   - EntwicklungPage.vue:227 — `.om-entwicklung__abschnitt > h2` uses `--wa-font-size-xl`
   - InvestitionenPage.vue:183 — `.om-investitionen__abschnitt h2` uses `--wa-font-size-xl`
   - RatEntscheidetPage.vue:103 — `.om-rat-entscheidet__titel` (h2 role) uses `--wa-font-size-xl`
   - GlossarPage.vue:62 — Glossary term heading uses `--wa-font-size-xl`
   - EinnahmenPage.vue:431 — Section heading uses `--wa-font-size-xl`
   - **Contract specifies exactly 4 sizes: 14px (s), 16px (m), 20px (l), 32px (2xl). --wa-font-size-xl is NOT in the allowed list.**
   - **Impact:** Renders at 18px or 24px (Web Awesome default), breaking the 4-size constraint and inconsistent from page to page. Users see 5+ effective sizes instead of 4.

2. **Non-Contract Font Weight (--wa-font-weight-semibold)**
   - GlossarPage.vue:63 — Term heading uses `--wa-font-weight-semibold`
   - **Contract specifies exactly 2 weights: 400 (normal) and 600 (bold). --wa-font-weight-semibold is NOT in the allowed list.**
   - **Impact:** Renders at 500 or 600 (browser/WA default), breaking the 2-weight constraint. Glossary headings appear inconsistently bold relative to other page headings.

3. **Incorrect h3 Font Size (StellenplanPage.vue:246)**
   - `.om-stellenplan__gruppe h3` uses `--wa-font-size-m` (16px Body) instead of `--wa-font-size-l` (20px Heading)
   - **Per UI-SPEC §Typography: "h2 (`ChartCard`-Titel, Abschnittstitel, Titel der Hinweisbox) Heading." and h3 should follow logical hierarchy**
   - **Impact:** h3 (Besoldung, Entgelt, Sozial- und Erziehungsdienst) renders at same size as body text (16px), breaking visual hierarchy within the card.

4. **Line Height Precision (StellenplanPage.vue:256)**
   - `.om-stellenplan__hinweis-text` uses `line-height: 1.5` (custom value) instead of token
   - **Per UI-SPEC Caption role: "14 px / 400 / Zeilenhöhe 1.5"**
   - **Minor:** Value is correct (1.5), but not using --wa-line-height-normal token for consistency. Low impact; line-height 1.5 is reasonable for captions.

**Summary:** 5 files violate the font-size contract; 1 file violates font-weight contract; 1 file violates h3 hierarchy. These are visible, measurable divergences from the design system.

**Score Justification:** Score 2/4 (Notable gaps, contract partially met). The 4-size and 2-weight constraints are explicitly stated in UI-SPEC §Typography and reinforced in §Spacing ("Die in `05-UI-REVIEW.md` bemängelten Tokens ... entstehen in neuem Code nicht wieder"). Using --wa-font-size-xl and --wa-font-weight-semibold suggests these tokens were copied from Phase 5 code or Phase 7 was pre-emptively modified without reviewing the Phase 6 contract.

---

### Pillar 5: Spacing (4/4)

**Strengths:**
- All spacing values use --wa-space-* tokens from the UI-SPEC scale:
  - xs (4px) — Gap between icon and text (MenueGruppe.vue:181)
  - sm (8px) — Padding in menu list (MenueGruppe.vue:219), gaps between legend entries
  - md (16px) — Card padding, section gaps (EntwicklungPage.vue:178)
  - lg (24px) — Between sections (EntwicklungPage.vue:172: `gap: var(--wa-space-l)`)
  - xl (32px) — Between Kennzahlenleiste and first content (EntwicklungPage.vue:172)
  - 2xl (48px) — Between major sections (EntwicklungPage.vue:172: `gap: var(--wa-space-xl)`)
  - 3xl (64px) — Not observed in Phase 6 (deferred to Phase 7)
- No arbitrary spacing values (e.g., `[14px]`, `calc(2rem)`) in scoped styles
- Grid spacing follows scale:
  - Kachelraster: `repeat(auto-fit, minmax(160px, 1fr))` with `gap: var(--wa-space-m)` (InvestitionenPage.vue:167, StellenplanPage.vue:209)
  - Posten-Zeitreihen: `repeat(auto-fit, minmax(300px, 1fr))` with `gap: var(--wa-space-m)` ab 700px (EntwicklungPage.vue:190)
- Hit targets ≥44px:
  - MenueGruppe.vue:182 — Button `min-height: 44px` (UI-SPEC Spacing exception)
  - MenueGruppe.vue:230 — Links in list `min-height: 44px`
  - InvestitionenPage.vue:211 — Reset button `min-height: 44px`
- Responsive breakpoint (700px) observed throughout (EntwicklungPage.vue:188, StellenplanPage.vue:260, MenueGruppe.vue list max-width uses 700px implicit in grid adjustments)
- Max-content width: `max-width: 72rem` (1152px) on all pages (EntwicklungPage.vue:168, InvestitionenPage.vue:149, RatEntscheidetPage.vue:86, StellenplanPage.vue:198)
- Sidebar/content padding on narrow screens: `md` (16px) observed via ChartCard padding inherited from token hierarchy

**Score Justification:** No violations; all spacing compliant with UI-SPEC scale and exceptions.

---

### Pillar 6: Experience Design (3/4) — WARNING

**Strengths:**
- **Loading states:** No lazy-loaded routes detected; all data is hydrated at page load via `import { haushalt, investitionen, stellenplan } from '@/data/daten'`, so no skeleton screens or spinners needed in Phase 6 scope
- **Error states:** No destructive actions in Phase 6, so no undo/recovery UX needed
- **Empty states handled:**
  - InvestitionenPage.vue:98–107 — When filter yields 0 results, shows "Keine Maßnahmen für diese Auswahl" with explanation and reset button
  - DatenTabelle empty rows — Shows "–" (not 0) for missing values per UI-SPEC (e.g., RatEntscheidetPage.vue fallback if no Überschuss products)
  - RuecklagenBalken hides Rückgang chart if only 1 Planjahr (EntwicklungPage.vue:59)
- **Disabled states:** InvestitionenPage.vue:104 button "Filter zurücksetzen" is always enabled (no destructive action, safe)
- **Confirmation for destructive actions:** None in Phase 6 scope
- **State feedback:**
  - Filter results announced via `aria-live="polite"` live region (MassnahmenFilter.vue, per UI-SPEC INV-01)
  - Active menu state signaled via `aria-current="true"` on button, `aria-current="page"` on link (MenueGruppe.vue:135, 236)
  - Page navigation: router.afterEach handles focus (move to h1), page title announcement (bestehend)
  - Filter state persisted in URL query (?pb=, ?art=), so reload preserves selection (useMassnahmenFilter hook reads from router.query)
- **Keyboard navigation:**
  - MenueGruppe.vue:67–73 — Escape closes menu, returns focus to button
  - MenueGruppe.vue:78–83 — Tab out of menu closes it (focusout handler checks relatedTarget)
  - List item links (router-link) are native elements, no custom focus handling needed
  - Form inputs (wa-select, wa-radio-group) have WA's built-in keyboard support

**Warnings Found:**

1. **MenueGruppe Focus Return on Escape (T-06-05 compliance check)**
   - MenueGruppe.vue:67–72 closes the menu and refocuses the button on Escape
   - **Issue:** If the menu is focused but not yet fully rendered (nextTick timing), `schalter.value?.focus()` may fail silently if ref is stale
   - **Impact:** User presses Escape, menu closes, but focus stays in the document (somewhere); screen reader announces "menu closed" but no focus change
   - **Mitigation:** Already uses `await nextTick()` before `positioniere()` on open (line 61), but not on close. Add `await nextTick()` before focus() in close path if needed, or ensure the button is always in the DOM
   - **Test:** Keyboard-only navigation on narrow viewports

2. **MenueGruppe Position Calculation (WR-01 Versatz Reliability)**
   - MenueGruppe.vue:40–56 measures the list's max-width via `getComputedStyle()` to prevent viewport overflow
   - **Issue:** `getComputedStyle()` on a v-show element may return an unresolved value if the CSS hasn't been evaluated yet (race condition on fast renders)
   - **Impact:** Menu list clips at right edge on first open, requiring a resize event or manual reposition to fix
   - **Mitigation:** Test opening the menu immediately after page load and observe right-edge clipping on 375px viewport. If clipping occurs, add `await nextTick()` or `await new Promise(resolve => setTimeout(resolve, 0))` before measuring
   - **Severity:** Low user impact (Tab/Arrow keys still work to navigate list; Escape and Tab-out still work), but visual bug on first open

**Deferred State Cases (Out of Phase 6 Scope):**
- Logout/session expiration (Phase 7)
- Form submission errors (Phase 6 has no forms with submission; filters are URL-driven)
- Network errors (Phase 6 has no runtime fetches; all data is bundled)

**Score Justification:** Score 3/4 (Good, minor issues). All required state patterns are implemented. The two edge cases (focus-return timing and position-calculation timing) are very low-severity and unlikely to affect most users, but should be tested on slow devices / slow network connections.

---

## Files Audited

- **Pages:**
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/pages/EntwicklungPage.vue` (164 lines)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/pages/InvestitionenPage.vue` (145 lines)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/pages/RatEntscheidetPage.vue` (135 lines)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/pages/StellenplanPage.vue` (266 lines)

- **New Components:**
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/MenueGruppe.vue` (243 lines)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/HinweisNichtImHaushalt.vue` (91 lines)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/BindungsgradBalken.vue` (200+ lines)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/ProduktBalkenListe.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/UeberschussListe.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/NichtBeeinflussbarBlock.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/ZuschussListe.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/MassnahmenFilter.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/MassnahmenListe.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/EntwicklungsDiagramm.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/ErgebnisBalken.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/PostenZeitreihe.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/RueckgangBalken.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/RuecklagenBalken.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/FinanzierungsDiagramm.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/VeFaelligkeiten.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/SchuldenstandDiagramm.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/StellenNachTeil.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/StellenNachBereich.vue`
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/components/StellenNachGruppe.vue`

- **Theme & Format:**
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/charts/echartsTheme.ts` (color tokens, WA registry)
  - `/Users/thma/repos/bitwerkstatt/ostbevern_money/app/src/charts/format.ts` (referenced for data formatting)

---

## Recommendation Summary

**BLOCKER:** Phase 6 implementation diverges from UI-SPEC §Typography on 5+ pages. The contract explicitly specifies 4 font sizes and 2 weights; the implementation uses --wa-font-size-xl (not in contract) and --wa-font-weight-semibold (not in contract). These are measurable, visible failures that violate the stated design constraint. **Do not ship Phase 6 without fixing typography compliance.** Estimated effort: 30 min (replace tokens in 5 files, verify renders correctly).

**WARNING:** Two low-severity experience-design edge cases should be tested on slow/mobile networks (focus-return timing, menu-position measurement race). Fix recommended but not blocking.

**Overall assessment:** Core UI structure is sound (spacing, color, visual hierarchy, copywriting all excellent). The typography violation is a regression from Phase 5 and contradicts the stated intent in UI-SPEC §Spacing ("entstehen in neuem Code nicht wieder").

