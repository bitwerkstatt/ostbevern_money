---
phase: 06-kontext-seiten
reviewed: 2026-10-06T00:00:00Z
depth: standard
files_reviewed: 73
files_reviewed_list:
  - app/src/App.vue
  - app/src/charts/__tests__/beschriftung.test.ts
  - app/src/charts/__tests__/farben.test.ts
  - app/src/charts/__tests__/wertartStil.test.ts
  - app/src/charts/beschriftung.ts
  - app/src/charts/echartsTheme.ts
  - app/src/charts/wertartStil.ts
  - app/src/components/BindungsgradBalken.vue
  - app/src/components/EntwicklungsDiagramm.vue
  - app/src/components/ErgebnisBalken.vue
  - app/src/components/FinanzierungsDiagramm.vue
  - app/src/components/HinweisNichtImHaushalt.vue
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MassnahmenListe.vue
  - app/src/components/MenueGruppe.vue
  - app/src/components/NichtBeeinflussbarBlock.vue
  - app/src/components/PostenZeitreihe.vue
  - app/src/components/ProduktBalkenListe.vue
  - app/src/components/RueckgangBalken.vue
  - app/src/components/RuecklagenBalken.vue
  - app/src/components/SchuldenstandDiagramm.vue
  - app/src/components/StellenNachBereich.vue
  - app/src/components/StellenNachGruppe.vue
  - app/src/components/StellenNachTeil.vue
  - app/src/components/SteuerZeitreihe.vue
  - app/src/components/UeberschussListe.vue
  - app/src/components/VeFaelligkeiten.vue
  - app/src/components/ZuschussListe.vue
  - app/src/data/haushalt.json
  - app/src/data/texte.json
  - app/src/lib/__tests__/bindungsgrad.test.ts
  - app/src/lib/__tests__/entwicklung.test.ts
  - app/src/lib/__tests__/finanzierung.test.ts
  - app/src/lib/__tests__/hinweis.test.ts
  - app/src/lib/__tests__/investitionen.test.ts
  - app/src/lib/__tests__/menue.test.ts
  - app/src/lib/__tests__/quelltext.test.ts
  - app/src/lib/__tests__/ruecklagen.test.ts
  - app/src/lib/__tests__/schulden.test.ts
  - app/src/lib/__tests__/stellen.test.ts
  - app/src/lib/__tests__/zuschuesse.test.ts
  - app/src/lib/bindungsgrad.ts
  - app/src/lib/entwicklung.ts
  - app/src/lib/finanzierung.ts
  - app/src/lib/glossar.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/menue.ts
  - app/src/lib/ruecklagen.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/lib/zeitreihen.ts
  - app/src/lib/zuschuesse.ts
  - app/src/pages/AusgabenPage.vue
  - app/src/pages/EinnahmenPage.vue
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
  - app/src/pages/RatEntscheidetPage.vue
  - app/src/pages/StellenplanPage.vue
  - app/src/router/index.ts
  - daten/manuell/README.md
  - daten/manuell/meta.json
  - daten/manuell/texte/erklaerungen.md
  - daten/manuell/texte/glossar.md
  - daten/manuell/zuschuesse_lfd_zwecke.csv
  - daten/pruefberichte/konsistenz.md
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_app_daten.py
  - pipeline/tests/test_formatiere.py
  - pipeline/tests/test_manuell.py
  - pipeline/tests/test_texte.py
findings:
  critical: 1
  warning: 5
  info: 8
  total: 14
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-10-06
**Depth:** standard
**Files Reviewed:** 73
**Status:** issues_found

## Summary

Reviewed the Phase-6 additions: four new context pages (Entwicklung, Investitionen, Rat entscheidet, Stellenplan), their libraries, components and charts, the grouped header menu, the new pipeline table `zuschuesse_lfd_zwecke` (Regel 5), the new text formulas, and the tests. The generated JSON (`haushalt.json`, `texte.json`, `konsistenz.md`) was inspected through the Phase-6 diff only.

Overall the code is carefully built: no `v-html`, tooltips only through `tooltipZeilen`, URL filters validated against allowlists (`Set`, no prototype keys), missing values stay `null` and render as the dash, and the new numbers cross-check against the data (for example allgemeine Rücklage 2027 = 39.522.991 − 697.620; the text values 31.866.316 / 19,37 %, 14,7 Mio. credit / 2,7 Mio. repayment, and the 120 T€ sum of the eight Einzelposten all reproduce). The vitest suite could not be executed here (`rolldown` native binding missing in the mounted `node_modules`), so findings are from reading code and data only.

The one finding classed as critical is a user-facing derivation that does not reproduce the number it explains (Core Value: every number must be traceable). The warnings are a stale-measurement positioning bug in the new menu, a reachable ungrammatical count, an inconsistently applied `berechnet` flag, and two "never invent a value" violations in lib code that the data does not trigger today.

## Critical Issues

### CR-01: Footnote under the Rücklagen table does not reproduce the shown "Rückgang im Jahr"

**File:** `app/src/pages/EntwicklungPage.vue:77-82` (formula in `app/src/lib/ruecklagen.ts:504-517`)
**Issue:** The table footnote states the Rückgang is "der Fehlbetrag des Jahres, soweit die Ausgleichsrücklage ihn nicht deckt, geteilt durch die allgemeine Rücklage zu Jahresbeginn". The implemented (and, per the 2027 column, correct) formula is `max(0, −Ergebnis − Ausgleich) − Verrechnung`, that is it additionally adds the Verrechnung der Bilanzierungshilfe. For 2026 the data gives Fehlbetrag 2.353.506, Ausgleichsrücklage 2.132.213, Verrechnung −476.327. A reader applying the footnote gets 221.293 / 39.522.991 = 0,6 %, but the table and chart show 697.620 / 39.522.991 = 1,8 %. The footnote therefore understates the calculation for exactly the year the page is about, in an app whose Core Value is that every number is reproducible. The comment in `ruecklagen.ts` and `texte.py` document the Verrechnung term; only the citizen-facing text omits it.
**Fix:** Name the second term in the footnote, for example:
```ts
'der Fehlbetrag des Jahres, soweit die Ausgleichsrücklage ihn nicht deckt, zuzüglich der Verrechnung der Bilanzierungshilfe, geteilt durch die allgemeine Rücklage zu Jahresbeginn.'
```
Better, derive the sentence from the same constants so text and formula cannot drift, and add a test that the footnote mentions the Verrechnung whenever any year has a non-zero `verrechnung_bilanzierungshilfe`.

## Warnings

### WR-01: `MenueGruppe.positioniere` measures with the stale offset, so the list is clipped again on every second open and after resize

**File:** `app/src/components/MenueGruppe.vue:34-50`
**Issue:** `positioniere()` sets `versatz.value = 0` and then immediately calls `getBoundingClientRect()`. Vue has not re-rendered yet, so the element still carries the previous `left: {versatz}px` inline style (the `ul` is only `v-show`-hidden between opens, the style stays). Trace: open 1 overflows, `versatz` becomes −50, list is correct. Close. Open 2: `versatz` is reset to 0 in state only, the rect still reflects `left: −50px`, fits, no correction is computed, then the flush applies `left: 0px` and the list overflows the right edge again. The same happens in the `resize` handler (the delta is computed relative to the old offset, not the base position).
**Fix:** Measure the base position independent of the current offset and assign the absolute result:
```ts
const kasten = element.getBoundingClientRect()
const basisLinks = kasten.left - versatz.value
const basisRechts = kasten.right - versatz.value
let neu = 0
if (basisRechts > breite - rand) neu = breite - rand - basisRechts
if (basisLinks + neu < rand) neu = rand - basisLinks
versatz.value = neu
```

### WR-02: "1 Maßnahmen" is reachable (and the same pattern exists for "Produkte")

**File:** `app/src/components/MassnahmenFilter.vue:23-25` (also `ProduktBalkenListe.vue:39-42`, `BindungsgradBalken.vue:33-35`)
**Issue:** The result line is built as `${zahl(n)} Maßnahmen · zusammen …` with no singular. Filter combinations that yield exactly one Maßnahme exist in the real data (for example `pb=04`, `pb=15`, `pb=13&art=grundstuecke`, `pb=06&art=bau`), so the live region announces "1 Maßnahmen". `StellenplanPage.personenText` already handles the singular correctly (UI-SPEC E-12 zero-one-many), so the pattern is known but not applied here. The two "Produkte" strings are not triggered by the current 15/15/29 segment sizes but will break for another Jahrgang.
**Fix:** Add a small helper next to `zahl` (for example `anzahlText(n, 'Maßnahme', 'Maßnahmen')`) and use it in all three places. Because the line sits in an `aria-live` region this is also a screen-reader defect.

### WR-03: `berechnet` flag applied to one Schulden tile but hard-coded `false` on its sibling

**File:** `app/src/pages/InvestitionenPage.vue:40-54`
**Issue:** `schulden.berechnet` (the `schuldenstand.berechnet` value of the Vorjahr) drives the label of the "Schulden je Einwohner" tile, while the "Schuldenstand Ende {Vorjahr}" tile is hard-coded `berechnet: false`. Both values come from the same index of the same series: if the Vorjahr is a fortgeschriebenes Jahr, the Gesamtwert is as derived as the Pro-Kopf-Wert, yet it would be shown without the label. It is correct for the current data (Vorjahr 2025 is printed), but the whole point of the data-driven flag (see `schulden.ts` header) is that it must also hold for other Jahrgänge.
**Fix:** `berechnet: schulden.berechnet` on the first tile too. For the Pro-Kopf tile keep the documented rule.

### WR-04: `baueRuecklagen` presents a partial sum as "Summe" when one Rücklage is missing

**File:** `app/src/lib/ruecklagen.ts:493-494`
**Issue:** `summe` is `(allgemeine ?? 0) + (ausgleich ?? 0)` whenever at least one is non-null. A year with only one value gets that value as the "Summe" over the column, in the label above the bar, in the tooltip ("Summe: …") and implicitly in the chart. This contradicts the file's own rule ("Fehlt ein Schlüssel … statt still auf 0 zu fallen") and the type comment that `summe` is `null` "wenn beide fehlen" (so a missing half is silently treated as 0). Not triggered today (all six years complete), but a different Jahrgang or a parsing gap would show a wrong total with no hint.
**Fix:** `summe: allgemeine === null || ausgleich === null ? null : allgemeine + ausgleich`, and add a test case with one missing half.

### WR-05: Nachwuchs person counts treat a missing `personen` as 0

**File:** `app/src/lib/stellen.ts:162-167`
**Issue:** `personen()` sums `zeile.personen ?? 0`. A row without a value contributes 0 and is indistinguishable from a real 0, while `summe()` right above throws on a missing `stellen`. The page then prints "Im Haushaltsplan stehen N Personen" (`StellenplanPage.vue:104-113`) with a possibly too low number. This violates the project rule that missing values are never replaced by 0.
**Fix:** Throw like `hundertstel()` does, or return `null` when any contributing row has `personen === null`.

## Info

### IN-01: Hard-coded hex fallback colors in components

**File:** `app/src/components/StellenNachTeil.vue:49-50`, `app/src/components/StellenNachGruppe.vue:31`, `app/src/charts/wertartStil.ts:567,572`
**Issue:** `KATEGORIE_FARBEN[1] ?? '#545868'`, `?? '#9194a2'`, and `'white'` bypass the convention "Chartfarben ausschließlich aus `echartsTheme.ts`, Farben nur über `--wa-*`-Tokens". The fallbacks are dead in practice (the tuple is fixed) but duplicate token values that can silently drift. `RueckgangBalken`/`RuecklagenBalken` use `?? ''` instead, which would give ECharts an empty color. Pick one pattern.
**Fix:** Export named constants from `echartsTheme.ts` (as already done for `SCHWELLE_FARBE`, `HOHL_FLAECHE`) and import them; or drop the fallback and let the type (`noUncheckedIndexedAccess`) throw.

### IN-02: Dead or test-only production exports

**File:** `app/src/lib/ruecklagen.ts:575-587`, `app/src/lib/menue.ts:48-50`
**Issue:** `ausgleichsruecklageAufgebrauchtJahr` and `menueLinks` are only referenced from tests (the polster text is generated by the pipeline). Additionally `ausgleichsruecklageAufgebrauchtJahr` uses `haushalt.jahre.indexOf(haushaltsjahr)` unchecked: a missing Haushaltsjahr yields `-1` and the loop starts at index 0 instead of throwing like the sibling helper `haushaltsjahrIndex()`.
**Fix:** Remove both from the production API (move into the tests), or at least reuse `haushaltsjahrIndex()`.

### IN-03: Duplicated helpers across lib modules

**File:** `app/src/lib/bindungsgrad.ts:68`, `app/src/lib/zuschuesse.ts:236`, `app/src/lib/kennzahlen.ts:36` (`jahrIndex`); `app/src/lib/entwicklung.ts:56` and `app/src/lib/ruecklagen.ts:473` (`wertartAn`); `app/src/lib/investitionen.ts:57` and `app/src/lib/ruecklagen.ts:599` (Haushaltsjahr-Index)
**Issue:** The same "index of the Haushaltsjahr / wertart at index, else throw" logic exists at least six times with slightly different error texts. Easy to diverge; a fix in one place will not reach the others.
**Fix:** One shared `haushaltsjahrIndex()` and `wertartAn()` in `lib/jahr.ts`.

### IN-04: Cross-module coupling for small helpers

**File:** `app/src/components/FinanzierungsDiagramm.vue:17` (`jahreListe` from `lib/schulden`), `app/src/components/ProduktBalkenListe.vue:13` (`klickIndex` from `lib/investitionen`)
**Issue:** Generic helpers live in feature modules. Importing `lib/investitionen` also executes its module-level `MASSNAHMEN_AUFGABENBEREICHE` IIFE (a full `baueVorhaben` pass) and pulls in `vue-router` for a function that only validates a click payload. A data error in the Investitionen data would break the Rat-entscheidet page at import time.
**Fix:** Move `klickIndex` to `charts/` (next to `balken.ts`) and `jahreListe` to `charts/format.ts` or `lib/jahr.ts`.

### IN-05: `useMassnahmenFilter` is instantiated twice per page

**File:** `app/src/components/MassnahmenFilter.vue:12`, `app/src/pages/InvestitionenPage.vue:81`
**Issue:** Page and filter component both call `useMassnahmenFilter()`, so there are two `immediate` watchers; with an invalid `?pb=` both issue `router.replace` with the same query. Harmless today (the second is a duplicate navigation), but the cleanup logic runs twice and each instance recomputes `baueVorhaben`.
**Fix:** Call it once in the page and pass `filter`/`setzePb`/`setzeArt` down (provide/inject or props).

### IN-06: Minor markup and equality nits

**File:** `app/src/components/VeFaelligkeiten.vue:51` (`:key="m.produkt + m.massnahmeId"`), `app/src/components/EntwicklungsDiagramm.vue:54`, `app/src/pages/EntwicklungPage.vue:39,46` (`!= null` / `== null`), `app/src/components/RuecklagenBalken.vue:59`, `app/src/components/ErgebnisBalken.vue:30`
**Issue:** (a) The key concatenates without a separator (`"1601"+"01"` equals `"160"+"101"`); `lib/finanzierung.ts` uses `produkt/massnahme_id` elsewhere. (b) Loose `!=`/`==` against `null` is inconsistent with the otherwise strict style. (c) `.replace(' ', '\n')` only matches a regular space, while `euro()` (below 1 Mio.) uses a no-break space, so a Summe under 1 Mio. would not break; `zweizeilig()` in `charts/beschriftung.ts` already handles both.
**Fix:** Use a `/` separator in the key, `=== null || === undefined`, and `zweizeilig()` in both Balken components.

### IN-07: Derived sum shown without "berechnet" label; source line cites all pages on every tile

**File:** `app/src/components/ZuschussListe.vue:84`, `app/src/pages/StellenplanPage.vue:52-56`
**Issue:** "Zusammen rd. …" for the Transfer group is the sum of two printed values (no printed Gesamtzeile), shown without the `BerechnetEtikett` used for other derived values (UI convention). On the Stellenplan, `kachelZeile` appends the union of all PDF pages (`summen.pdfSeiten`) to every tile, so the "Stellen Vorjahr" tile cites pages that also belong to the Haushaltsjahr and the besetzt rows.
**Fix:** Show the label next to derived sums; pass the tile-specific page list to `kachelZeile`.

### IN-08: Pipeline formulas raise untyped errors

**File:** `pipeline/ostbevern/texte.py:317-322,328-338`
**Issue:** `_allgemeine_ruecklage_rueckgang_bis_letztes_jahr` divides by `anfang` with no guard (`ZeroDivisionError` instead of the `TexteFehler` used for the neighbouring formula), and the f-string key lookups raise a bare `KeyError` if a year column is missing. Step 07 would abort with an unhelpful trace.
**Fix:** Guard `anfang == 0` and wrap lookups so the failure names the formula, as `_ausgleichsruecklage_aufgebraucht_jahr` does.

---

_Reviewed: 2026-10-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
