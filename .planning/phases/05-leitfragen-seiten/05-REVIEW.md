---
phase: 05-leitfragen-seiten
reviewed: 2026-10-04T16:40:00Z
depth: standard
files_reviewed: 96
files_reviewed_list:
  - .claude/CLAUDE.md
  - .github/workflows/ci.yml
  - app/eslint.config.ts
  - app/package.json
  - app/src/App.vue
  - app/src/charts/__tests__/balken.test.ts
  - app/src/charts/__tests__/farben.test.ts
  - app/src/charts/__tests__/format.test.ts
  - app/src/charts/__tests__/tooltip.test.ts
  - app/src/charts/balken.ts
  - app/src/charts/echartsTheme.ts
  - app/src/charts/format.ts
  - app/src/charts/tooltip.ts
  - app/src/components/AufwandTreemap.vue
  - app/src/components/AufwandsartBalken.vue
  - app/src/components/BaseChart.vue
  - app/src/components/BerechnetEtikett.vue
  - app/src/components/Brotkrumen.vue
  - app/src/components/ChartCard.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/EbenenTabelle.vue
  - app/src/components/EinstiegsKachel.vue
  - app/src/components/ErklaerText.vue
  - app/src/components/ErtragsBalken.vue
  - app/src/components/GeldflussBalken.vue
  - app/src/components/GlossarBegriff.vue
  - app/src/components/GlossarListe.vue
  - app/src/components/JahrUmschalter.vue
  - app/src/components/KennzahlKachel.vue
  - app/src/components/KreisumlageCallout.vue
  - app/src/components/PageIntro.vue
  - app/src/components/ProduktAkkordeon.vue
  - app/src/components/SankeyDiagramm.vue
  - app/src/components/SteuerZeitreihe.vue
  - app/src/components/WertartEtikett.vue
  - app/src/components/ZuschussBalken.vue
  - app/src/components/datenTabelle.ts
  - app/src/config.ts
  - app/src/data/typen.ts
  - app/src/lib/__tests__/ansicht.test.ts
  - app/src/lib/__tests__/aufwandsarten.test.ts
  - app/src/lib/__tests__/berechnung.test.ts
  - app/src/lib/__tests__/bewegung.test.ts
  - app/src/lib/__tests__/config.test.ts
  - app/src/lib/__tests__/drilldown.test.ts
  - app/src/lib/__tests__/einnahmen.test.ts
  - app/src/lib/__tests__/ertragsarten.test.ts
  - app/src/lib/__tests__/geldfluss.test.ts
  - app/src/lib/__tests__/glossar.test.ts
  - app/src/lib/__tests__/jahr.test.ts
  - app/src/lib/__tests__/kennzahlen.test.ts
  - app/src/lib/__tests__/kreisumlage.test.ts
  - app/src/lib/__tests__/menue.test.ts
  - app/src/lib/__tests__/produkt.test.ts
  - app/src/lib/__tests__/quelltext.test.ts
  - app/src/lib/__tests__/texte.test.ts
  - app/src/lib/__tests__/zeilen.test.ts
  - app/src/lib/__tests__/zeitreihen.test.ts
  - app/src/lib/ansage.ts
  - app/src/lib/ansicht.ts
  - app/src/lib/aufwandsarten.ts
  - app/src/lib/berechnung.ts
  - app/src/lib/bewegung.ts
  - app/src/lib/drilldown.ts
  - app/src/lib/einnahmen.ts
  - app/src/lib/ertragsarten.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/glossar.ts
  - app/src/lib/jahr.ts
  - app/src/lib/kennzahlen.ts
  - app/src/lib/kreisumlage.ts
  - app/src/lib/menue.ts
  - app/src/lib/produkt.ts
  - app/src/lib/texte.ts
  - app/src/lib/zeilen.ts
  - app/src/lib/zeitreihen.ts
  - app/src/main.ts
  - app/src/pages/AusgabenPage.vue
  - app/src/pages/EinnahmenPage.vue
  - app/src/pages/GeldflussPage.vue
  - app/src/pages/GlossarPage.vue
  - app/src/pages/ProduktPage.vue
  - app/src/pages/StartPage.vue
  - app/src/router/index.ts
  - app/tsconfig.json
  - app/tsconfig.vitest.json
  - app/vitest.config.ts
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_app_daten.py
  - pipeline/tests/test_formatiere.py
  - pipeline/tests/test_manuell.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_texte.py
findings:
  critical: 0
  warning: 7
  info: 11
  total: 18
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-10-04T16:40:00Z
**Depth:** standard
**Files Reviewed:** 96
**Status:** issues_found

## Summary

Reviewed the Phase-5 app code (lib builders, charts, components, pages, router) and the changed pipeline modules (`texte.py`, the Phase-5 hunks of `pruefung.py`, `app_daten.py`, `schema.py`). Where the code made a claim about the data, I checked it against the generated `haushalt.json`, `texte.json` and `produkte.json`. I also copied `app/src` into the scratch directory and ran vitest there. All 1005 tests pass, so the findings below are things the tests do not cover.

Verified as sound:
- The Geldfluss balance holds in every year: left side = Erträge + Defizit + Minderaufwand, right side = KL + PB Z. 17 + Zinsen + Überschuss. The ±1 to 2 € gap in 2024 and 2028 comes from the PDF itself: its printed Finanzergebnis is off by 1 € against Z. 19 − Z. 20, and the PB Z. 17 sums differ from GESAMT by 1 €.
- Ertragsarten and Aufwandsarten sum exactly to `berechnet.ertraege` and `berechnet.aufwand`.
- Every knoten code has an `ergebnisplan` entry.
- URL values (`jahr`, `modus`, `pb`, `pg`, `code`) are only looked up through `Map` or `Set`, so prototype keys are safe.
- There is no `v-html`, and all ECharts tooltip HTML goes through `tooltipZeilen` and `encodeHTML`.
- `formatiere` handles `null`, `undefined`, `NaN` and `Infinity` as "–".
- The `textFuerJahr` guard against year-specific texts is applied on every page that shows a text with placeholders.
- The stale `watch` in `AusgabenPage` (ebene key) does not fire after unmount in Vue 3.5, because the RouterView update job runs first and disposes the child watcher.

No data-corrupting or injection defects found. The warnings concern numbers shown without the "rd." or "berechnet" qualifier the project requires, one misleading headline, one silently ineffective design parameter, and two latent pipeline problems.

## Warnings

### WR-01: Geldfluss shows Vorbericht-derived amounts as exact euros, without "rd." or "berechnet"

**File:** `app/src/lib/geldfluss.ts:130-155` (nodes), `:364`, `:376`, `:531` (tooltips); `app/src/lib/geldfluss.ts:46-58` (interface)
**Issue:** The Steuer nodes (Gewerbesteuer, Anteil Einkommensteuer, Grundsteuer) and "Schlüsselzuweisung" come from Vorbericht tables kept in T€ and multiplied by 1000. Every Vorbericht posten has `gerundet: true`. "Übrige Steuern" (`steuern − Σ gerundete Gruppen`) and "Sonstige Zuwendungen" (`zuwendungen − gerundete Schlüsselzuweisung`) are exact-minus-rounded differences. The result is a number that is neither exact nor a printed value.

`GeldflussKnoten` has no `gerundet` or `berechnet` flag. The tooltips (`euro(knoten.wert)`), the edge tooltips and the mobile bar tooltips (`euro(segment.wert)`) show them as precise values such as "7.800.000 €" or "1.621.808 €".

Everywhere else the app marks these amounts with "rd." (`drilldown.eintragTooltip`, `EbenenTabelle`, `KreisumlageCallout`, the Einnahmen tables). The Sankey is the one place where the convention is broken. A reader can compare the Sankey figure with the Einnahmen page, which shows "rd. 7.800.000 €", and see two different claims of precision.

**Fix:** Add `gerundet: boolean` and `berechnet: boolean` to `GeldflussKnoten` and `BalkenSegment`.
- Set `gerundet` on the four Vorbericht-based nodes.
- Set `berechnet` and `gerundet` on `uebrige_steuern` and `sonstige_zuwendungen`.
- Add a prefix helper used by `tooltipInhalt`, `balkenOption`, `geldflussZeilen` and the table slot:
```ts
const betragMitHinweis = (wert: number, gerundet: boolean) => gerundet ? `rd. ${euro(wert)}` : euro(wert)
```
- Add a test that every non-Ergebnisplan node carries the flag.

### WR-02: Start page says "Den größten Anteil bekommt Innere Verwaltung", but Weitergabe an Kreis und Land is more than twice as large

**File:** `app/src/pages/StartPage.vue:95`; `app/src/lib/kennzahlen.ts:196-205`
**Issue:** The tile under "Wofür wird das Geld ausgegeben?" claims the largest share goes to the biggest real Aufgabenbereich (Innere Verwaltung, about 4,52 Mio. €). `baueEinstiege` deliberately skips the synthetic KL node (D-20). In the data, KL is 11,0 Mio. € in 2026, so the sentence is false for the budget as a whole. The Kreisumlage callout further down says the opposite ("Der größte Einzelposten ist die Weitergabe an Kreis und Land"). Both statements appear on the same screen.

**Fix:** Qualify the copy so it stays true, for example "Unter den Aufgabenbereichen der Gemeinde ist {name} am größten: …" or "Ohne die Weitergabe an Kreis und Land …". Alternatively show KL as the largest block and name the biggest own Aufgabenbereich in a second sentence.

### WR-03: `mitDeckkraft` silently ignores every non-hex colour, so the decal opacity from the design never applies

**File:** `app/src/charts/echartsTheme.ts:444-450`, `:459`, `:468`
**Issue:** `KL_DECAL.color` and `PUNKT_DECAL.color` are built as `mitDeckkraft(token('--wa-color-surface-default', '#ffffff'), 0.45 / 0.55)`. `mitDeckkraft` only handles `#rrggbb`. In the Web Awesome CSS, `--wa-color-surface-default` is the keyword `white` (I confirmed it in the built CSS: `--wa-color-surface-default:white`). In a real browser the token is therefore `"white"`, the regex fails, and the function returns `"white"` unchanged. The KL stripes and the Überschuss/Minderaufwand dots are drawn as fully opaque white, not as 45% / 55% white. The unit test (`farben.test.ts`) runs without a DOM, so it only ever sees the `#ffffff` fallback and passes.

This affects the "never colour alone" pattern in the KL tile and the surplus bars. The tile's label background uses the KL colour as a pill precisely because the stripes harm legibility, and fully opaque stripes make that worse.

**Fix:** Resolve any CSS colour to RGB instead of regex-matching hex. For example, draw the token into a 1×1 canvas context, or parse with `new Option().style.color`. At minimum, wrap non-hex tokens with `color-mix(in srgb, <token> 45%, transparent)` or log a warning. Add a test that stubs `getComputedStyle` to return `white`.

### WR-04: `lies_erklaerungen` / `lies_glossar` silently drop page ranges in `Quelle:` lines

**File:** `pipeline/ostbevern/texte.py:54`, `:122`
**Issue:** `pruefe_text` explicitly allows ranges in running text (`_SEITE_MUSTER`: `S. 309-311`, `S. 24/25`). The `Quelle:` parser uses `_SEITENZAHL_MUSTER = r"S\.\s*(\d+)"` with `findall`. For `Quelle: S. 309-311` it returns `(309,)` and discards 310 and 311 without error. `Quelle: S. 24/25` gives `(24,)`. The app then shows "Quelle: PDF-Seite 309" for a text that cites three pages. The current `.md` files only use comma-separated single pages, so the data is unaffected today, but the next edit will lose pages silently. This is the same class of silent loss that the Core Value ("every figure traceable to PDF pages") is meant to prevent.

**Fix:** Either expand ranges (`S. 309-311` → 309, 310, 311) or reject them in the `Quelle:` line with a `TexteFehler`:
```python
if re.search(r"S\.\s*\d+\s*[-/]\s*\d+", quelle_treffer.group(1)):
    raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r}: Seitenspannen in Quelle nicht erlaubt, einzeln auflisten")
```

### WR-05: Konzessionsabgaben check is silently skipped when `meta` is absent; Regel 5 then reports a clean pass

**File:** `pipeline/ostbevern/pruefung.py:1443-1450` (the `if "sonstige_ertraege" in vorbericht and meta is not None` branch)
**Issue:** `pruefe_alles` always passes `meta`. But `_pruefe_regel5` accepts `meta=None` and, in that case, silently omits the split check. `geprueft` is lower by one and nothing signals the gap. The new Phase-5 table `sonstige_ertraege` is supposed to be covered by this check (the Konzessionsabgaben split is shown in the app per Sparte). The same pattern already exists for the Kreisumlage meta check, so a test calling `_pruefe_regel5` without `meta` would never notice. For the GFP branch you correctly raise `PruefungsFehler` when `planwerte_finanzplan` is missing; this branch should do the same.

**Fix:**
```python
if "sonstige_ertraege" in vorbericht:
    if meta is None:
        raise PruefungsFehler("Regel 5: sonstige_ertraege braucht meta.json für die Konzessionsabgaben-Aufteilung")
    ...
```

### WR-06: Fixed-year shape in `texte.py` formulas: KeyError instead of `TexteFehler`, and every formula runs even when unused

**File:** `pipeline/ostbevern/texte.py:246-269`, `:390-392`
**Issue:** `_ausgleichsruecklage_minderung_haushaltsjahr` reads `eigenkapital.ausgleichsruecklage.{hh + 1}` and `_schluesselzuweisung_rueckgang_haushaltsjahr` reads `vorbericht.zuwendungen.schluesselzuweisung.{vj}`. Every formula in `ABGELEITET` is evaluated unconditionally in `textwerte`, whether or not a text uses it. For another Jahrgang (Haushaltsjahr = last year in `jahre`, or a missing series) the pipeline aborts with a bare `KeyError: 'eigenkapital.ausgleichsruecklage.2030'`. That contradicts the stated fail-fast contract ("unbekannter Datenschlüssel bricht Schritt 07 mit `TexteFehler` ab") and the project rule that Jahrgang changes happen only in the TOML/config.

**Fix:** Evaluate only the formulas referenced by some text (derive the set from `PLATZHALTER_MUSTER` over the texts), and convert `KeyError` into `TexteFehler` with the formula name:
```python
try:
    werte[f"abgeleitet.{name}"] = formel(werte)
except KeyError as fehler:
    raise TexteFehler(f"Formel {name!r}: Eingabewert {fehler} fehlt") from fehler
```

### WR-07: `DatenTabelle` makes every captioned table a tab stop and duplicates its name for screen readers

**File:** `app/src/components/DatenTabelle.vue:71-91`
**Issue:** If `beschriftung` is set, the wrapper gets `role="region"`, `aria-label` and `tabindex="0"` unconditionally, and the `<table>` additionally renders a visually hidden `<caption>` with the same text. A screen-reader user hears the name twice (region plus table caption). Keyboard users get an extra tab stop on every table, including the many that never scroll (the Einnahmen page alone renders six). The focusable-region pattern is only recommended when the content actually overflows horizontally.

**Fix:** Drop the `role="region"` / `aria-label` (the caption already names the table). Make the wrapper focusable only when it overflows, via a `ResizeObserver` check of `scrollWidth > clientWidth`.

## Info

### IN-01: Latent "-0 €" and "-0 %" output from `proKopf` and `Intl`

**File:** `app/src/lib/berechnung.ts:13`; `app/src/charts/format.ts:28-30`; `app/src/lib/produkt.ts:565`; `app/src/components/EbenenTabelle.vue:53`
**Issue:** `Math.round(-0.3)` is `-0`, and `Intl.NumberFormat('de-DE', {style:'currency', …}).format(-0)` yields `"-0 €"` (I checked in Node; `wa-format-number` uses the same API). Any Zuschussbedarf with an absolute value below about 5 870 € and a negative sign would render "-0 € je Einwohner". The current data has no such case (I checked all 132 nodes), so this is latent and will appear with the next Jahrgang.
**Fix:** Normalise in `proKopf`: `return Math.round(betrag / einwohner) + 0` (adding 0 turns `-0` into `0`), or `|| 0`.

### IN-02: Hard-coded superlative in the Kreisumlage callout

**File:** `app/src/components/KreisumlageCallout.vue:49`
**Issue:** "Der größte Einzelposten ist die Weitergabe an Kreis und Land" is a data claim written as copy. It is true for every year today (KL ≥ 10,9 Mio. € against at most 4,5 Mio. € for any Aufgabenbereich), but nothing in the code derives or tests it. This conflicts with the convention that statements about data come from data.
**Fix:** Add a test asserting that KL is the maximum of all `aufwand` values for the Haushaltsjahr, or compute the sentence variant from the data.

### IN-03: "Quelle: PDF-Seite 51, 8" – singular for several pages, unsorted order

**File:** `app/src/components/ErklaerText.vue:22,29`; `app/src/pages/AusgabenPage.vue:129,311`; `app/src/components/KreisumlageCallout.vue:80`
**Issue:** `ErklaerText` renders `PDF-Seite {{ seiten }}` with `quelle_seiten.join(', ')`. Texts with several pages show "PDF-Seite 24, 9, 311" (singular, order as typed). `GlossarListe` and `quellenText` pluralise and sort correctly; these places do not. The AusgabenPage Überschuss callout has the same pattern.
**Fix:** Reuse `quellenText` from `lib/einnahmen.ts` (it deduplicates, sorts and pluralises) in `ErklaerText`, the Überschuss callout and the Kreisumlage callout.

### IN-04: Page-wide `useJahr` registers a redirect watcher in every component that calls it

**File:** `app/src/lib/jahr.ts:96-107`
**Issue:** `useJahr` is called in `App.vue`, each page, `JahrUmschalter`, `GeldflussBalken` and `SankeyDiagramm`. Each call installs its own `watch(..., { immediate: true })` that issues `router.replace` when `?jahr=` is invalid. On a page with an invalid `jahr`, up to six identical replaces are fired in one tick, and each cancels the previous pending navigation. It converges, but it is redundant and fragile. Also, `leseJahr` returns the first element of an array, so `?jahr=2025&jahr=abc` is treated as valid and never cleaned.
**Fix:** Install the cleaning watcher once (in `App.vue` or via a module-level guard) and have the other call sites use only the read-only part. Treat an array with more than one element as invalid.

### IN-05: Mobile drawer stays open after clicking the link of the current page

**File:** `app/src/App.vue:60-68`
**Issue:** The drawer closes in a `watch` on `route.path`. A menu link to the page the user is already on (same path, same query) produces no navigation, so the drawer stays open with no feedback. A query-only change (e.g. "Woher?" with a different `jahr`) behaves the same.
**Fix:** Close the drawer on the click itself (`@click="drawerOffen = false"` on the drawer's `RouterLink`s) in addition to the route watcher.

### IN-06: Lesehilfe states "Erträge und Aufwendungen gleichen sich … genau aus" even when only the Minderaufwand closes the gap

**File:** `app/src/lib/geldfluss.ts:584-586`
**Issue:** The fallback sentence is added when there is neither a Defizit nor an Überschuss. If `ergebnis_nach_minderaufwand` is exactly 0 while `globaler_minderaufwand` is not 0, the Erträge and Aufwendungen do *not* balance; the Minderaufwand does. The static text `geldfluss_lesehilfe` also says "Beide Seiten sind gleich groß", while the data differ by 1 to 2 € in 2024 and 2028 (PDF rounding). Neither case occurs in the current data.
**Fix:** Add the sentence only if `!minderaufwand`, and use "ausgeglichen" wording for the Minderaufwand-only case.

### IN-07: `minderaufwandHinweis` can print a negative "Minderaufwand"

**File:** `app/src/lib/aufwandsarten.ts:172-178`
**Issue:** `betrag = -wert` assumes the Z. 27 value is negative. If a later Jahrgang had a positive value, `satz` would read "setzt der Plan einen globalen Minderaufwand von -600.000 €". `baueGeldfluss` guards the same case with a thrown error ("Globaler Minderaufwand ist positiv: Datenfehler"); this function does not, so the two pages could disagree.
**Fix:** Throw (or return `null`) for `betrag < 0`, as `geldfluss.ts` does.

### IN-08: `EbenenTabelle` silently drops the per-capita column when `einwohner` is not a number

**File:** `app/src/components/EbenenTabelle.vue:28`, `:53`
**Issue:** `typeof einwohner === 'number' ? proKopf(...) : null` turns a data error into a column of "–". `kennzahlen.ts` and `produkt.ts` throw in the same situation. Inconsistent error policy; a broken `meta.einwohner` would be visible on the Start page but not here.
**Fix:** Reuse a shared `einwohnerZahl()` helper that throws.

### IN-09: Placeholder contact data and PDF URL are live links, guarded only by a comment

**File:** `app/src/config.ts:12`, `:21`; `app/src/App.vue:168,179`
**Issue:** The footer renders a `mailto:` to `…@example.invalid` and an external link to `https://haushaltsplan-noch-nicht-festgelegt.invalid/` that opens in a new tab. The deployment gate ("Phase 7 MUSS … prüfen") exists only in the doc comment. `istPlatzhalter` is tested, but nothing fails the build or CI when a placeholder is still in place.
**Fix:** Add a vitest (or a CI step before deploy) that fails when `istPlatzhalter(KONTAKT_EMAIL) || istPlatzhalter(ORIGINAL_PDF_URL)` is true, and gate it on the deploy workflow so day-to-day CI stays green.

### IN-10: Digit rule in `pruefe_text` lets hand-typed numbers between 1900 and 2099 through

**File:** `pipeline/ostbevern/texte.py:44`, `:205`
**Issue:** The year exception `\b(?:19|20)\d{2}\b` is context-free, so a typed "2000 Euro" or "1950 Einwohner" passes the "no hand-typed numbers" rule. The Core Value depends on that rule, but the range is easy to hit with small amounts.
**Fix:** Allow the year pattern only when it is not followed by a unit word, or only when it is within `[haushaltsjahr − 10, haushaltsjahr + 10]`.

### IN-11: Documentation and tooling drift

**File:** `.claude/CLAUDE.md` (section "CI lokal nachstellen"); `app/package.json:117-119,100-101`; `.github/workflows/ci.yml:3-8`
**Issue:**
- CLAUDE.md says the local CI replication is "identisch zu `.github/workflows/ci.yml`", but it omits the `npm run test` (vitest) step and the pipeline reproducibility step (`alle.py` plus `git diff --exit-code`).
- `engines.node` is `^22.18.0` and `.nvmrc` pins Node 22, while `@types/node` is `^24` and `@tsconfig/node24` is used, so type-checking allows Node 24 APIs that Node 22 lacks.
- The header comment of `ci.yml` still says there is no GitHub remote.
- `typen.ts` documents that `absaetze[0]` of a glossary term "enthält nie einen Platzhalter", but `lies_glossar` does not enforce this (the rendering code still resolves placeholders, so nothing breaks).

**Fix:** Update the CLAUDE.md block, align `@types/node` / `@tsconfig/node22` with the runtime, refresh the `ci.yml` header, and add a check in `lies_glossar` for placeholders in `absaetze[0]`.

---

_Reviewed: 2026-10-04T16:40:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
