---
phase: 08-fixes-und-triage
reviewed: 2026-10-07T00:00:00Z
depth: standard
files_reviewed: 98
files_reviewed_list:
  - .claude/CLAUDE.md
  - .github/workflows/ci.yml
  - app/e2e/interaktion.spec.ts
  - app/e2e/menueDrawer.ts
  - app/e2e/mobil.spec.ts
  - app/e2e/quelle.spec.ts
  - app/e2e/tabellenrahmen.ts
  - app/src/App.vue
  - app/src/charts/__tests__/format.test.ts
  - app/src/charts/echartsTheme.ts
  - app/src/charts/format.ts
  - app/src/charts/wertartStil.ts
  - app/src/components/AufwandTreemap.vue
  - app/src/components/ChartCard.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/EbenenTabelle.vue
  - app/src/components/EntwicklungsDiagramm.vue
  - app/src/components/ErgebnisBalken.vue
  - app/src/components/EuroBetrag.vue
  - app/src/components/FinanzierungsDiagramm.vue
  - app/src/components/KreisumlageCallout.vue
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MassnahmenListe.vue
  - app/src/components/NichtBeeinflussbarBlock.vue
  - app/src/components/PostenZeitreihe.vue
  - app/src/components/ProduktAkkordeon.vue
  - app/src/components/ProduktBalkenListe.vue
  - app/src/components/RuecklagenBalken.vue
  - app/src/components/SchuldenstandDiagramm.vue
  - app/src/components/SteuerZeitreihe.vue
  - app/src/components/VeFaelligkeiten.vue
  - app/src/components/ZuschussListe.vue
  - app/src/components/__tests__/chartcard.test.ts
  - app/src/components/__tests__/eurobetrag.test.ts
  - app/src/components/__tests__/zustaende.test.ts
  - app/src/components/datenTabelle.ts
  - app/src/data/texte.json
  - app/src/lib/__tests__/aufwandsarten.test.ts
  - app/src/lib/__tests__/berechnung.test.ts
  - app/src/lib/__tests__/bindungsgrad.test.ts
  - app/src/lib/__tests__/drilldown.test.ts
  - app/src/lib/__tests__/duanrede.test.ts
  - app/src/lib/__tests__/einwohner.test.ts
  - app/src/lib/__tests__/entwicklung.test.ts
  - app/src/lib/__tests__/geldfluss.test.ts
  - app/src/lib/__tests__/glossar.test.ts
  - app/src/lib/__tests__/hinweis.test.ts
  - app/src/lib/__tests__/investitionen.test.ts
  - app/src/lib/__tests__/jahr.test.ts
  - app/src/lib/__tests__/kennzahlen.test.ts
  - app/src/lib/__tests__/menue.test.ts
  - app/src/lib/__tests__/menueVersatz.test.ts
  - app/src/lib/__tests__/quelle-kacheln.test.ts
  - app/src/lib/__tests__/quelle-kontext.test.ts
  - app/src/lib/__tests__/quelle-leitfragen.test.ts
  - app/src/lib/__tests__/quelle-ui-abdeckung.test.ts
  - app/src/lib/__tests__/quelle.test.ts
  - app/src/lib/__tests__/quelltext.test.ts
  - app/src/lib/__tests__/rdregel.test.ts
  - app/src/lib/__tests__/ruecklagen.test.ts
  - app/src/lib/__tests__/schulden.test.ts
  - app/src/lib/__tests__/stellen.test.ts
  - app/src/lib/__tests__/stiltokens.test.ts
  - app/src/lib/__tests__/texte.test.ts
  - app/src/lib/__tests__/zeitreihen.test.ts
  - app/src/lib/__tests__/zuschuesse.test.ts
  - app/src/lib/aufwandsarten.ts
  - app/src/lib/berechnung.ts
  - app/src/lib/bindungsgrad.ts
  - app/src/lib/drilldown.ts
  - app/src/lib/einwohner.ts
  - app/src/lib/entwicklung.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/hilfsfunktionen.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/jahr.ts
  - app/src/lib/kennzahlen.ts
  - app/src/lib/produkt.ts
  - app/src/lib/ruecklagen.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/lib/texte.ts
  - app/src/lib/zeitreihen.ts
  - app/src/lib/zuschuesse.ts
  - app/src/pages/AusgabenPage.vue
  - app/src/pages/EinnahmenPage.vue
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/StartPage.vue
  - app/src/pages/StellenplanPage.vue
  - daten/manuell/texte/erklaerungen.md
  - pipeline/alle.py
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_formatiere.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_texte.py
findings:
  critical: 0
  warning: 3
  info: 7
  total: 10
status: issues_found
---

# Phase 08: Code Review Report

**Reviewed:** 2026-10-07
**Depth:** standard
**Files Reviewed:** 98
**Status:** issues_found

## Summary

Reviewed the full non-planning diff of phase 08 (`93b0a61..HEAD`) with the focus on changed code: the single "rd."/"rund" rule in `charts/format.ts`, the Minderaufwand rule in `berechnung.ts`, the four-case Lesehilfe in `geldfluss.ts`, `DatenTabelle` frame attributes, the mobile drawer focus handling, the pipeline year-placeholder rules (`pruefe_text`, `pruefe_titel`, `loese_auf`, `festes_jahr`) and the new tests and e2e helpers. I traced the shared helpers (`haushaltsjahrIndex`, `wertartAn`, `einwohnerZahl`, `minderaufwandBetrag`, `zusammen`, `seiten*` in `stellen.ts`) through their callers.

The refactoring is consistent. Both `rd.` and `rund` prefixes contain U+00A0 (verified byte-wise), no stale `RD_PRAEFIX` importer remains, and the four Lesehilfe cases are mutually exclusive: `defizit` needs `nachMinderaufwand < 0`, `ueberschuss` needs `> 0`, and Fall C can only occur at exactly 0. There are no security findings and no data-loss or crash defects in the normal data path. The remaining concerns are one latent correctness hole introduced by the new year placeholders, one focus edge case in the drawer, and a few robustness and maintainability points.

## Warnings

### WR-01: Year label and value key are now decoupled; a new Jahrgang silently produces wrong statements

**File:** `daten/manuell/texte/erklaerungen.md:7, 13, 19, 49, 55` (mirrored in `app/src/data/texte.json`, Absätze der Schlüssel `schluesselzuweisung`, `gewerbesteuer`, `kreisumlage`, Schulden, Verpflichtungsermächtigungen)
**Issue:** Phase 08 replaced typed years by relative placeholders (`{{jahr.vorjahr|jahr}}`, `{{jahr.vorvorjahr|jahr}}`, `{{jahr.haushaltsjahr_plus_1|jahr}}`). The amounts next to them still use keys with a hard-coded year suffix, for example `{{schulden.gesamt.2025|mio}}`, `{{vorbericht.steuerarten.gewerbesteuer.2024|mio}}`, `{{ve.faellig.2027|mio}}`. Before this change label and value were both literals and agreed by construction. Now the label moves with `haushaltsjahr` while the value is pinned. For a 2027 Jahrgang the text would read "Ende 2026 waren das zusammen {{schulden.gesamt.2025}}" and pass every check (`pruefe_text`, `loese_auf`, `pruefe_grundzahl_jahre` only validates `grundzahlen.*`). That is a wrong number-to-year claim published to citizens, which the project's core value ("jede Zahl korrekt") rules out. It stays hidden until the next Jahrgang is built.
**Fix:** Either make the value keys relative as well (`schulden.gesamt.vorjahr`, `ve.faellig.haushaltsjahr_plus_1`, resolved in `textwerte`), or add a pipeline check in `loese_auf`/`pruefe_text` that fails when a paragraph pairs a relative `jahr.*` placeholder with a value key whose `.YYYY` suffix does not equal the resolved year of the same Jahrgang (for example `jahr.vorjahr` together with `*.{haushaltsjahr-1}`). A cheap interim guard is a pipeline test that asserts, for the current Jahrgang, the year suffix of each paired key equals the resolved relative year.

### WR-02: Drawer link click sets the "closes by navigation" flag even when no navigation happens

**File:** `app/src/App.vue:27-30` (used at `:191` and `:195`)
**Issue:** `beiDrawerLinkKlick` runs on every `click` of the `RouterLink`, including Ctrl/Cmd/Shift-click and any click where `RouterLink` does not navigate (new tab/window). In those cases the drawer is closed, `schliesstDurchSeitenwechsel` is set, and `beiAfterHide` then moves focus to the `h1` of the current page (`fokussiereUeberschrift` scrolls to it without `preventScroll`). The user opened a link in a new tab and is thrown to the top of the page. The flag is also only ever reset in `beiAfterHide`; if the drawer is already closing (second click during the close animation) or `wa-after-hide` is not delivered, the stale `true` makes the next Escape/overlay close skip returning focus to the menu button (a keyboard focus regression, A11Y-02).
**Fix:**
```ts
function beiDrawerLinkKlick(ereignis: MouseEvent) {
  if (ereignis.ctrlKey || ereignis.metaKey || ereignis.shiftKey || ereignis.altKey || ereignis.button !== 0) {
    return
  }
  if (!drawerOffen.value) {
    return
  }
  schliesstDurchSeitenwechsel.value = true
  drawerOffen.value = false
}
```
and reset the flag in `oeffneDrawer()` so it cannot leak into the next session of the drawer.

### WR-03: `DatenTabelle` accepts an empty `beschriftung`, producing an unnamed scroll region with no guard left

**File:** `app/src/components/DatenTabelle.vue:20`, `app/src/components/datenTabelle.ts:881-889`
**Issue:** D-16/D-20 made `beschriftung` a required prop and the only source of the region name (`aria-labelledby` pointing to the caption). The type only enforces presence, not content. `beschriftung=""` (or a computed that yields an empty string) renders `role="region"` with `aria-labelledby` pointing to an empty caption: a landmark without a name, exactly the A11Y-01 defect this phase fixes. The old dev-mode `console.warn` guard for missing props was deleted without replacement, and the e2e check only runs on the routes and data present today.
**Fix:** Add a dev guard next to `rahmenAttribute` use, or make `rahmenAttribute` omit the attributes when the name is blank:
```ts
const rahmenAttributeGebunden = computed(() =>
  rahmenAttribute(
    ueberlaeuft.value && !props.laedt && !istLeer.value && props.beschriftung.trim() !== '',
    captionId,
  ),
)
if (import.meta.env.DEV) {
  watchEffect(() => {
    if (props.beschriftung.trim() === '') console.warn('DatenTabelle: `beschriftung` ist leer.')
  })
}
```

## Info

### IN-01: `kurzMitHinweis(..., false)` drops the rounding disclosure of `euroKurz`

**File:** `app/src/components/NichtBeeinflussbarBlock.vue:52` (also `app/src/charts/format.ts:111-114`)
**Issue:** `euroKurz` rounds to three significant digits, which is why `rundKurz` exists for prose ("immer mit 'rund' davor, weil euroKurz auf drei signifikante Stellen rundet"). `kurzMitHinweis` adds "rd." only when the source value is T€-rounded. An exact euro value (`gerundet === false`) shown through `euroKurz` therefore appears as "12,3 Mio. €" with no hint that it was shortened. `NichtBeeinflussbarBlock` previously always printed "rd." and now depends on `p.gerundet`; the SUMMARY states the output is identical for 2026, but the behaviour differs for any future exact Posten. Pre-existing for the chart labels (treemap, Drilldown bars).
**Fix:** Decide the policy once in `format.ts`: either document that "rd." only means "T€-genau" and short forms are intentionally unmarked, or let `kurzMitHinweis` always prefix when the shortened text loses digits.

### IN-02: `flaechenFarbe()` docstring contradicts how the decals use it

**File:** `app/src/charts/echartsTheme.ts:15-17, 225, 234, 281`
**Issue:** The docstring says the colour is a function "weil der Token erst zur Aufrufzeit gelesen werden darf". `KL_DECAL`, `PUNKT_DECAL` and `BERECHNET_DECAL` still call it at module load, so the token is read once at import time. If Web Awesome's stylesheet has not been applied then, the `#ffffff` fallback is baked in permanently (pre-existing behaviour, now documented incorrectly).
**Fix:** Correct the comment, or build the decals lazily (functions or getters evaluated per chart option).

### IN-03: Redundant condition in `lies_glossar`

**File:** `pipeline/ostbevern/texte.py:187`
**Issue:** `PLATZHALTER_MUSTER.search(text.absaetze[0]) or "{{" in text.absaetze[0]`: every match of the pattern contains `{{`, so the first operand is dead. The same redundant pair repeats a few lines below for the Quelle check.
**Fix:** Use `"{{" in text.absaetze[0]` only, or extract a helper `enthaelt_platzhalter(absatz)` for both places.

### IN-04: Unusual rest-tuple signature for `einwohnerZahl`

**File:** `app/src/lib/einwohner.ts:12`
**Issue:** `einwohnerZahl(...pruefwert: [wert?: unknown])` distinguishes "no argument" from an explicit `undefined` only to make the throw testable. It is an API shaped by a test and easy to misread at call sites (`einwohnerZahl(undefined)` throws, `einwohnerZahl()` does not).
**Fix:** Split into a pure `pruefeEinwohnerZahl(wert: unknown): number` (tested directly) and `einwohnerZahl()` that calls it with `haushalt.meta.einwohner.wert`.

### IN-05: `quellenZeile` renders a dangling separator for an empty page list

**File:** `app/src/lib/hilfsfunktionen.ts:19-23`
**Issue:** With `pdfSeiten = []` the result is `"Ist 2026 · PDF-Seiten "` (plural word, trailing space, no number). The function moved here unchanged, but phase 08 now has Kacheln without pages (`seitenVorjahr` etc. may be empty), and `StellenplanPage` handles that case separately in `kachelZeile`, so other callers remain exposed.
**Fix:** Return `${wertart} ${formatiereJahr(jahr)}` when `pdfSeiten.length === 0`.

### IN-06: Fixed 500 ms sleep in the table-frame e2e helper

**File:** `app/e2e/tabellenrahmen.ts:30`
**Issue:** `page.waitForTimeout(500)` after opening all `wa-details` is a time-based wait; it is slow on every route (about 11 routes times 2 tests) and can still be too short on a loaded CI runner. The callers already wrap the check in `expect.poll`, which makes the sleep redundant for correctness.
**Fix:** Drop the sleep and rely on `expect.poll(() => befundeTabellenrahmen(page))`, or poll on a stable layout signal (`scrollWidth` of the frames unchanged over two frames).

### IN-07: `rdregel` guard covers only "rd.", not the "rund" prefix; comment stripping can hide copies

**File:** `app/src/lib/__tests__/rdregel.test.ts:44, 31-37`
**Issue:** D-22 centralises both `RD_PRAEFIX` and `RUND_PRAEFIX` in `format.ts`, but `RD_KOPIE` only detects hand-built "rd." prefixes; a new `` `rund ${euro(x)}` `` copy passes. In addition `ohneKommentare` strips everything after whitespace plus `//` including inside template literals, so a copy on such a line is invisible (the limitation is documented in the test, but not mitigated). The regex also embeds a literal U+00A0 that is invisible in the source and easy to lose in an editor.
**Fix:** Add a second pattern for `rund` followed by space, U+00A0 or `&nbsp;` and then `${`/`{{`/`euro`, and write the U+00A0 alternatives with escapes (` `) in the regex source.

---

_Reviewed: 2026-10-07_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
