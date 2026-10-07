---
status: resolved
trigger: "Nach dem Klick auf einen Begriff scrollt die Seite zu weit nach oben, das fokussierte Element ist dadurch nicht sichtbar. (UAT 05 Test 6, Gap G-05-6)"
created: 2026-10-05T00:00:00Z
updated: 2026-10-07T12:00:00Z
goal: find_root_cause_only
---

## Current Focus

bug_class: Bohrbug (deterministic: every hash jump lands the target at viewport y=0 under the sticky header)
hypothesis: CONFIRMED — router scrollBehavior returns `{ el }` without a top offset; vue-router scrolls via window.scrollTo(elementRect.top) which ignores CSS scroll-margin-top, so the target section (and its focused h3) lands at viewport y=0, underneath wa-page's opaque sticky header. The intended compensation (GlossarListe scroll-margin-top) is additionally invalid because of the non-existent token `--wa-space-md`.
test: Source reading of vue-router 5.3.1 scrollToPosition/getElementPosition, WA 3.14 wa-page styles, token inventory diff (used vs. defined --wa-* tokens).
expecting: n/a (diagnosis complete; goal find_root_cause_only)
next_action: Return ROOT CAUSE FOUND to caller; fix is out of scope for this session.

reasoning_checkpoint:
  hypothesis: "The focused glossary heading is hidden because router/index.ts:101-102 returns `{ el: ziel }` without `top`, vue-router 5.3.1 (vue-router.esm-browser.js:676-735) converts that into window.scrollTo(top = elRect.top - docRect.top - 0), ignoring scroll-margin-top, and wa-page's header is `position: sticky; top: 0; z-index: 5` with an opaque background, so the top ~76px of the viewport (where the h3 now sits) is covered."
  confirming_evidence:
    - "vue-router getElementPosition uses only getBoundingClientRect and offset.top; no scrollIntoView anywhere in the {el} path"
    - "wa-page styles: [part~='header'] position: sticky; z-index: 5; background-color: surface-default; App.vue sets no disable-sticky"
    - "GlossarListe.vue:56 references var(--wa-space-md), the only --wa-* token used in app/src that WA 3.14 does not define -> declaration invalid at computed-value time -> scroll-margin-top: 0"
    - "Focus calls use preventScroll: true (router:131, GlossarListe:22), so no second scroll repositions the element"
  falsification_test: "In a browser, after clicking a Sprungmarke, `document.getElementById(key).getBoundingClientRect().top` would be >= header height (wa-page --header-height). If it is ~0 the hypothesis holds; if it is >= header height the hypothesis is wrong."
  fix_rationale: "Supplying the header offset to the scroll (either `{ el, top: offset }` in scrollBehavior, or a native scrollIntoView that honours a *valid* scroll-margin-top) places the target below the sticky header — addressing the position computation itself, not the focus."
  blind_spots: "No live browser reproduction: Playwright browser download (cdn.playwright.dev) requires sandbox approval, so the rect value was not measured. Header height at the user's viewport not measured (estimated ~76px from padding 2x--wa-space-m + 44px min-height links; more if nav wraps)."
  candidate_causes:
    - "code: scrollBehavior `{ el }` without offset (router/index.ts:101-102) + vue-router ignores scroll-margin"
    - "config/styling: invalid CSS token --wa-space-md voids scroll-margin-top (GlossarListe.vue:56)"
    - "environment/library: wa-page sticky header is opaque and on by default (WA 3.14), covering y=0..header-height"
    - "data/layout: late layout shift above target after scroll (eliminated — would push target DOWN, not hide it under header; nothing async above the list)"
  and_gate: "yes — symptom needs (a) opaque sticky header AND (b) scroll landing at y=0. (b) itself has two stacked defects: vue-router ignores scroll-margin-top, and the scroll-margin-top declaration is invalid. Fixing only the typo does NOT fix the bug (router still uses window.scrollTo); fixing only the router path via scrollIntoView without the typo fix also does NOT fix it (scroll-margin still 0)."

## Symptoms

expected: Klick auf einen GlossarBegriff-Link (aus einer Seite) oder Sprungmarke im Glossar scrollt zum Begriff und setzt den Fokus; der fokussierte Begriff ist danach im Viewport sichtbar.
actual: "Nach dem Klick auf einen Begriff scrollt die Seite zu weit nach oben, das fokussierte Element ist dadurch nicht sichtbar."
errors: None reported
reproduction: UAT 05 Test 6 (.planning/phases/05-leitfragen-seiten/05-UAT.md) — Glossar oeffnen, Sprungmarken und GlossarBegriff-Links aus Seiten testen
started: Discovered during UAT (2026-10-05)

## Eliminated

- hypothesis: Double scrolling — focus() scrolls the element after the router scroll and moves it out of view
  evidence: Both focus calls use preventScroll: true (router/index.ts:58 via :131 fokussiere(hashZiel, true); GlossarListe.vue:22 h3.focus({ preventScroll: true })). No other scroll calls exist on the Glossar path.
  timestamp: 2026-10-05T00:12:00Z

- hypothesis: Layout shift after the scroll (web component upgrade, wa-details/akkordeon expansion, fonts) moves the target
  evidence: Everything above the glossary list is static (PageIntro h1/p, nav of RouterLinks); custom elements are defined in main.ts before mount; ProduktAkkordeon/wa-divider are BELOW the list and cannot shift the target. A shift above would push the target DOWN (still visible), contradicting "zu weit nach oben ... nicht sichtbar".
  timestamp: 2026-10-05T00:13:00Z

- hypothesis: Window is not the scroll container (wa-page scrolls internally), so scrollTo goes to the wrong place
  evidence: wa-page body/main parts have no overflow; :host is min-height 100% and the document scrolls. UAT confirms the page does scroll (just too far).
  timestamp: 2026-10-05T00:14:00Z

## Evidence

- timestamp: 2026-10-05T00:05:00Z
  checked: Knowledge base (.planning/debug/knowledge-base.md), MemPalace
  found: No knowledge base file and no prior debug sessions exist.
  implication: No known-pattern candidate; open investigation.

- timestamp: 2026-10-05T00:06:00Z
  checked: app/src/router/index.ts:99-111 (scrollBehavior) and :116-137 (afterEach)
  found: scrollBehavior returns `{ el: ziel }` with NO `top` offset when the hash matches an element. afterEach then focuses the target with `fokussiere(hashZiel, true)` -> `focus({ preventScroll: true })` (line 58/131). Comment at 130 states "Gescrollt hat bereits scrollBehavior".
  implication: The only scroll on hash navigation is the one vue-router performs for `{ el }`. Focus does not scroll (preventScroll), so no double scroll from focus.

- timestamp: 2026-10-05T00:07:00Z
  checked: app/node_modules/vue-router/dist/vue-router.esm-browser.js:676-735 (vue-router 5.3.1 getElementPosition/scrollToPosition)
  found: For `{ el }`, vue-router computes `top = el.getBoundingClientRect().top - documentElement.getBoundingClientRect().top - (offset.top || 0)` and calls `window.scrollTo(...)`. It does NOT call scrollIntoView, so CSS `scroll-margin-top` on the target is never consulted.
  implication: The target section's top edge is placed exactly at viewport y=0 (offset.top is undefined -> 0).

- timestamp: 2026-10-05T00:08:00Z
  checked: @awesome.me/webawesome 3.14.0 wa-page styles (dist/chunks/chunk.FFR4H3XU.js) and JS (chunk.POQQIIHO.js:122-149)
  found: `[part~='header'] { position: sticky; top: var(--banner-top); z-index: 5; background-color: surface-default }`. Sticky is on by default; App.vue:114 `<wa-page ref="seite">` sets no `disable-sticky`. wa-page measures the header via ResizeObserver and sets `--header-height`; it exposes `--scroll-margin-top: calc(header + subheader + 0.5em)` on :host for consumers.
  implication: An opaque sticky header (logo + nav, >= 44px links + 2x --wa-space-m padding) covers the top of the viewport. Anything scrolled to y=0 lies underneath it.

- timestamp: 2026-10-05T00:09:00Z
  checked: app/src/components/GlossarListe.vue:56 and WA 3.14 token list (dist/styles/**/*.css)
  found: `scroll-margin-top: calc(var(--scroll-margin-top, 0px) + var(--wa-space-md));` — the token `--wa-space-md` does not exist (WA defines --wa-space-3xs..5xl, s, m, l, xl; no `md`). `var()` of an undefined custom property without fallback makes the whole declaration invalid at computed-value time -> scroll-margin-top falls back to its initial value 0.
  implication: Even a native scroll (scrollIntoView / browser fragment scroll) would not offset for the header. The intended header compensation is dead twice over.

- timestamp: 2026-10-05T00:09:30Z
  checked: grep for scroll-padding/scrollTo/scrollIntoView in app/src
  found: No `scroll-padding-top` on html/body anywhere (basis.css has none). Only other scroll code: EinnahmenPage.vue:205 scrollIntoView (different feature, UAT test 2 passed).
  implication: Nothing else compensates for the sticky header on the glossary jump.

- timestamp: 2026-10-05T00:15:00Z
  checked: Diff of all `var(--wa-*)` tokens used in app/src vs. tokens defined in @awesome.me/webawesome/dist/styles
  found: Exactly one undefined token: `--wa-space-md` (GlossarListe.vue:56). `--wa-space-m` = 1rem is defined in themes/default.css:232.
  implication: Confirms the typo; no other undefined WA tokens in the app.

- timestamp: 2026-10-05T00:16:00Z
  checked: Attempted live reproduction with Playwright
  found: Chromium download from cdn.playwright.dev returns "Approval required" (sandbox network policy). No local browser available.
  implication: Diagnosis rests on library/app source, not a measured rect. Falsification test documented in reasoning_checkpoint for manual confirmation.

- timestamp: 2026-10-05T00:17:00Z
  checked: git history
  found: Router scrollBehavior/afterEach hash handling from f3d6630 (05-04); GlossarListe scroll-margin-top with --wa-space-md from a93c8b3 (05-13).
  implication: Bug present since the glossary jump feature was introduced; no regression from a later change.

## Resolution

root_cause: "router/index.ts:101-102 returns `{ el: ziel }` without a `top` offset; vue-router 5.3.1 turns that into window.scrollTo(elementTop) (vue-router.esm-browser.js:676-683, 731-733) and never consults CSS scroll-margin-top, so the target section and its focused h3 land at viewport y=0, underneath wa-page's opaque sticky header (WA 3.14 page styles: [part~=header] position: sticky; z-index: 5). The intended compensation is also dead on its own: GlossarListe.vue:56 `scroll-margin-top: calc(var(--scroll-margin-top, 0px) + var(--wa-space-md))` uses the non-existent token --wa-space-md, making the declaration invalid at computed-value time (scroll-margin-top = 0)."
fix: (not applied — goal find_root_cause_only)
verification: (not applicable)
files_changed: []

## Resolution

resolved: 2026-10-07 — fixed; marked resolved by the user at v1.0 milestone close.
