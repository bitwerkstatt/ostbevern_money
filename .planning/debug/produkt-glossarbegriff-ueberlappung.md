---
status: diagnosed
trigger: "Auf den Produktseiten liegen Glossarbegriffshülle (\"Bindungsgrad\") und Glossarbegriff (\"teils pflichtig, teils freiwillig\") leicht übereinder (Überschneidung)"
created: 2026-10-05T00:00:00Z
updated: 2026-10-05T00:25:00Z
goal: find_root_cause_only
---

## Current Focus

bug_class: Bohrbug (deterministic CSS layout; reproduces on every render of /produkt/:code with bindungsgrad)
sbfl: skipped — no failing test exists for a visual/layout defect; no per-test coverage of CSS
known_pattern_candidate: none (.planning/debug/knowledge-base.md does not exist; MemPalace not configured)

hypothesis: The dotted underline of the GlossarBegriff link in the "Bindungsgrad" <dt> is drawn 4px below the alphabetic baseline (text-underline-offset: 4px) while the <dt> line box is only 1.2 x 14px = 16.8px tall; the <dd> follows with zero gap and its first line box starts with the wa-tag's 1px border/fill, so the underline (and the "g" descenders) paint into the top edge of the wa-tag.
test: (a) compute dt/dd line-box geometry from Web Awesome 3 tokens + scoped CSS; (b) git diff of 86ce67e (dt was plain text before); (c) differential vs. Gremium/Fachbereich rows; (d) optional headless render if a browser image can be pulled
expecting: underline bottom > dt bottom (16.8px) and tag top == dd top == dt bottom
next_action: return ROOT CAUSE FOUND (diagnose-only); headless render not possible in sandbox (playwright CDN 403), geometry derived analytically from token values

reasoning_checkpoint:
  hypothesis: "Underline of GlossarBegriff (offset 4px, ProduktPage dt line-height 1.2) protrudes ~0.6–1.6px below the dt box; the dd's wa-tag (30.4px inline-flex, taller than the dd strut) sits flush at dd top with no dt/dd gap, so underline and tag border overlap."
  confirming_evidence:
    - "GlossarBegriff.vue:36-37 text-decoration: underline dotted; text-underline-offset: 4px"
    - "ProduktPage.vue:232-236 dt font-size var(--wa-font-size-s)=14px, line-height var(--wa-line-height-condensed)=1.2 -> 16.8px line box"
    - "ProduktPage.vue:238-240 dd margin 0; Web Awesome native.css gives dt no margin; nothing separates dt and dd inside the row <div> (gap: var(--wa-space-s) on .om-produkt__blick applies only between row divs)"
    - "wa-tag size=small: font 14px, height calc(form-control-height*0.8)=0.8*38=30.4px, inline-flex; its top (≈19.5px above baseline) exceeds the dd strut top (≈18.5px above baseline) so the tag defines the dd line-box top -> tag border at dd top"
    - "git show 86ce67e: dt was plain 'Bindungsgrad' text before Plan 05-15 wrapped it in GlossarBegriff; Gremium/Fachbereich rows (plain dt, plain dd text) show no overlap"
  falsification_test: "Render /#/produkt/030101 and measure: if getBoundingClientRect of the wa-tag top >= dt.bottom + underline extent (≈ baseline+4px+thickness), or if adding a dt/dd gap does not change the visual, the hypothesis is wrong."
  fix_rationale: "Diagnose only. Direction: give the dt room for the underline (line-height normal or padding-block-end/margin) or add a gap between dt and dd (row div as flex column with gap / dd margin-block-start), rather than removing the glossary link."
  blind_spots: "Not pixel-verified in a real browser (no Chromium obtainable in sandbox). Exact underline thickness/position varies by font (SF Pro on macOS vs. others) and engine (Blink measures length offsets from the alphabetic baseline)."
  candidate_causes:
    - "code (CSS): condensed dt line-height + 4px underline offset + zero dt/dd spacing in ProduktPage.vue"
    - "code (CSS, component lib): wa-tag box (30.4px) taller than dd strut, pushes tag border flush to dd top"
    - "environment: font metrics (ui-sans-serif/SF Pro descent ≈0.24em) — affects magnitude, not existence"
    - "data: bindungsgrad text length — eliminated (overlap is vertical, independent of tag text)"
  and_gate: "yes — overlap requires all of: (1) underline offset/descenders below the dt line box (condensed line-height + 4px offset), (2) zero spacing between dt and dd, (3) a painted box (wa-tag border/fill) at the very top of the dd. Removing any one removes the visible overlap; GlossarBegriff in running text (line-height 1.6) never overlaps."

## Symptoms

expected: Label „Bindungsgrad“ (GlossarBegriff) und Wert „teils pflichtig, teils freiwillig“ (wa-tag) überlappen nicht.
actual: "Auf den Produktseiten liegen Glossarbegriffshülle ("Bindungsgrad") und Glossarbegriff ("teils pflichtig, teils freiwillig") leicht übereinder (Überschneidung)"
errors: none
reproduction: UAT Test 4 — /#/produkt/030101, /#/produkt/160101
started: discovered during Phase 05 UAT

## Eliminated

- hypothesis: wa-tooltip inside the GlossarBegriff wrapper takes layout space and pushes/overlaps the dd
  evidence: tooltip.styles (chunk.DJLBC7Q4.js) sets :host { position: absolute; display: inline-block } — out of flow, no layout contribution
  timestamp: 2026-10-05T00:12:00Z

- hypothesis: the overlap is horizontal (tag text runs into the label) due to long bindungsgrad text
  evidence: dt and dd are block siblings stacked vertically inside the row <div> (.om-produkt__blick is flex-direction: column); no horizontal juxtaposition exists; 160101 ("pflichtig", short) shows the same symptom per UAT
  timestamp: 2026-10-05T00:14:00Z

- hypothesis: focus ring (a:focus-visible outline + outline-offset) causes the overlap
  evidence: user describes a static overlap visible without interaction; focus ring only paints on keyboard focus
  timestamp: 2026-10-05T00:15:00Z

## Evidence

- timestamp: 2026-10-05T00:05:00Z
  checked: app/src/pages/ProduktPage.vue:88-109 (markup) and :225-240 (scoped CSS)
  found: Row = <div><dt><GlossarBegriff>Bindungsgrad</GlossarBegriff></dt><dd><wa-tag size="small">…</wa-tag><span hinweis/></dd></div>. dt: font-size var(--wa-font-size-s), line-height var(--wa-line-height-condensed). dd: margin 0. Gap var(--wa-space-s) only on .om-produkt__blick (between row divs), not between dt and dd.
  implication: dt bottom == dd top; the dt line box is tight (condensed).

- timestamp: 2026-10-05T00:06:00Z
  checked: app/src/components/GlossarBegriff.vue:34-42
  found: .om-glossar-begriff { text-decoration: underline dotted; text-underline-offset: 4px }
  implication: underline sits 4px below the alphabetic baseline (fixed px, not em) — larger than the font's descent at 14px.

- timestamp: 2026-10-05T00:08:00Z
  checked: node_modules/@awesome.me/webawesome/dist/styles/themes/default.css:195,218,337-340; native.css:44-69,176-178,281-287
  found: --wa-font-size-s = 14px; --wa-line-height-condensed = 1.2; --wa-form-control-height = round(2*0.75em + 1em*1.2, 1px); native.css gives dt only font-weight (no margin), dd margin 0; a has text-underline-offset 0.125em (overridden to 4px by the scoped class).
  implication: dt line box = 16.8px. With ui-sans-serif/SF Pro (ascent ≈0.95em, descent ≈0.24em) the baseline sits ≈13.4px from dt top, descent reaches ≈16.8px (the dt bottom); underline at baseline+4px ≈17.4px, i.e. ≈0.6px BELOW the dt box, plus ~1px thickness -> ends ≈18.4px.

- timestamp: 2026-10-05T00:10:00Z
  checked: wa-tag styles (chunk.4AHPL3WP.js) + size styles (size.styles.ts chunk) + tag.ts (chunk.JS5OA4M6.js)
  found: :host { display: inline-flex; height: calc(var(--wa-form-control-height) * 0.8); line-height: calc(form-control-height - 2*border); border-width: var(--wa-border-width-s) (1px); background fill-quiet }; size="small" -> font-size 14px -> form-control-height 38px -> tag height 30.4px, line-height 36px; slotted text 12px (font-size-smaller).
  implication: Inline-flex baseline ≈19.5px below the tag top; dd strut (16px, line-height 1.6) top is only ≈18.5px above baseline -> the tag box defines the top of the dd's first line box, so the tag's 1px top border lies exactly at dd top == dt bottom (16.8px). The underline (≈17.4–18.4px) and the "g" descenders of "Bindungsgrad" paint onto the tag's border/fill => visible slight overlap.

- timestamp: 2026-10-05T00:12:00Z
  checked: git show 86ce67e -- app/src/pages/ProduktPage.vue (Plan 05-15)
  found: Before 86ce67e the dt was plain text "Bindungsgrad"; 05-15 wrapped it in <GlossarBegriff schluessel="bindungsgrad">.
  implication: Regression introduced when the underlined glossary link was placed into a condensed-line-height dt that sits flush on a boxed wa-tag. Explains why Plan 05-11 layout looked fine.

- timestamp: 2026-10-05T00:13:00Z
  checked: differential — all other GlossarBegriff usages (StartPage, EinnahmenPage, AusgabenPage, GeldflussPage, ProduktPage:62) and the Gremium/Fachbereich rows
  found: All other usages are in running text with body line-height 1.6 (≈4.8px half-leading absorbs the 4px offset) and no boxed element directly underneath; Gremium/Fachbereich dt have no underline and dd has no box.
  implication: Only ProduktPage.vue:92 combines condensed line-height + underline + flush boxed successor — matches the symptom being reported only on Produktseiten.

- timestamp: 2026-10-05T00:16:00Z
  checked: availability of a headless browser for pixel measurement
  found: no chromium/playwright in sandbox; `playwright install chromium` -> download 403; docker playwright image pull did not complete in time
  implication: geometry is derived analytically from shipped CSS tokens, not pixel-measured (noted as blind spot).

## Resolution

root_cause: In ProduktPage.vue the "Auf einen Blick" row stacks <dt> and <dd> with zero spacing, and the <dt> uses font-size-s (14px) with line-height-condensed (1.2 -> 16.8px line box). Plan 05-15 (86ce67e) wrapped the dt label in GlossarBegriff, whose link draws a dotted underline at text-underline-offset: 4px below the baseline — further than the 14px font's descent — so the underline (and the "g" descenders) extend ≈1–2px below the dt box. The dd's first line box is defined by the wa-tag (size small: inline-flex, 30.4px tall, 1px border + quiet fill), whose top edge sits exactly at dd top == dt bottom. Result: the underline of "Bindungsgrad" paints onto the top border of the "teils pflichtig, teils freiwillig" tag. (AND-gate: condensed dt line-height + 4px underline offset; zero dt/dd gap; boxed wa-tag at dd top.)
fix:
verification:
files_changed: []
