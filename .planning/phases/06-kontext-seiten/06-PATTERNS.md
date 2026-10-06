# Phase 6: Kontext-Seiten - Pattern Map

**Mapped:** 2026-10-06
**Files analyzed:** 36 (neu/geändert, abgeleitet aus CONTEXT.md D-01…D-20 und RESEARCH.md „Recommended Project Structure“)
**Analogs found:** 33 / 36 (alle Analogpfade git-tracked unter `app/`, `pipeline/`, `daten/`)

Hinweis: Die konkreten Komponentennamen sind Empfehlungen aus CONTEXT/RESEARCH (Claude's Discretion). Die App hat vitest (`app/src/lib/__tests__/`), Pipeline hat pytest (`pipeline/tests/`).

## File Classification

| Neu/geänderte Datei | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `daten/manuell/zuschuesse_lfd_zwecke.csv` | data | file-I/O | `daten/manuell/kita_zuschuesse.csv` | exact |
| `daten/manuell/README.md` (Abschnitt) | doc | - | selbst (Abschnitt kita_zuschuesse) | exact |
| `daten/manuell/meta.json` (+2 `vorbericht_werte`: HSK-Schwellen) | config | file-I/O | selbst (`vorbericht_werte`-Einträge) | exact |
| `daten/manuell/texte/erklaerungen.md`, `glossar.md` (neue Abschnitte) | data/text | file-I/O | selbst (`## nicht_im_haushalt`, `schulden`) | exact |
| `pipeline/ostbevern/schema.py` (+Konstante) | config | - | `KITA_ZUSCHUESSE_CSV` Z. 49 | exact |
| `pipeline/ostbevern/pruefung.py` (Regel 5 + Lader) | service | transform | `_pruefe_regel5_kita_gegen_transfer` Z. 1038-1080, Aufruf Z. 1460, Lader Z. 2549 | exact |
| `pipeline/ostbevern/app_daten.py` (`vorbericht_quellen`) | service | batch | selbst Z. 960-975 | exact |
| `pipeline/ostbevern/texte.py` (ABGELEITET-Formeln, `jahr.letztes_jahr`) | service | transform | selbst (`ausgleichsruecklage_minderung_haushaltsjahr`, Z. ~275) | exact |
| `pipeline/tests/test_manuell.py`, `test_pruefung.py`, `test_app_daten.py`, `test_texte.py` | test | - | `test_manuell.py` Z. 106, 171-205; `test_app_daten.py` Z. 187 | exact |
| `app/src/lib/menue.ts` (Union Link/Gruppe) | utility | request-response | selbst | exact |
| `app/src/lib/__tests__/menue.test.ts` | test | - | selbst | exact |
| `app/src/App.vue` (Dropdown/Drawer) | component | request-response | selbst Z. 10-25, 122, 152 | exact |
| `app/src/components/MenueGruppe.vue` | component | request-response | `App.vue` Navigationsblock | role-match |
| `app/src/router/index.ts` (4 Routen) | route | request-response | selbst Z. 50-81 | exact |
| `app/src/charts/echartsTheme.ts` (+`MarkLineComponent`, Farben/Decal) | config | transform | selbst | exact |
| `app/src/lib/investitionen.ts` (Bündelung, Filter, Query) | utility | transform | `lib/zeitreihen.ts` + `lib/ansicht.ts` | role-match |
| `app/src/lib/bindungsgrad.ts` | utility | transform | `lib/berechnung.ts`, `lib/produkt.ts` | role-match |
| `app/src/lib/ruecklagen.ts`, `entwicklung.ts`, `schulden.ts` | utility | transform | `lib/zeitreihen.ts`, `lib/kennzahlen.ts` | role-match |
| `app/src/lib/stellen.ts` | utility | transform | `lib/zeitreihen.ts` (reine Funktion, Hundertstel) | partial |
| `app/src/lib/zuschuesse.ts` | utility | transform | `lib/kreisumlage.ts` | role-match |
| `app/src/lib/__tests__/*.test.ts` (je Modul) | test | - | `zeitreihen.test.ts`, `kreisumlage.test.ts`, `ansicht.test.ts` | exact |
| `app/src/lib/zeitreihen.ts` -> gemeinsames Stilmodul (Ist/Ansatz/Planung) | utility | transform | `components/SteuerZeitreihe.vue` `STILE`/`LEGENDE_TEXT` | partial |
| `app/src/components/BindungsgradBalken.vue`, `MassnahmenListe.vue`, `RuecklagenBalken.vue`, `StellenBalken.vue` | component | transform | `components/ZuschussBalken.vue` + `charts/balken.ts` | role-match |
| `app/src/components/EntwicklungsDiagramm.vue`, `MiniZeitreihe.vue` | component | transform | `components/SteuerZeitreihe.vue` | role-match |
| `app/src/components/HinweisNichtImHaushalt.vue`, `NichtBeeinflussbar.vue` | component | request-response | `components/KreisumlageCallout.vue` | exact |
| `app/src/components/` Kennzahl-Kacheln (Schulden, Stellen) | component | request-response | `components/KennzahlKachel.vue` | exact |
| `app/src/pages/EntwicklungPage.vue`, `InvestitionenPage.vue`, `RatEntscheidetPage.vue`, `StellenplanPage.vue` | page | transform | `pages/AusgabenPage.vue`, `pages/EinnahmenPage.vue` | exact |
| `AusgabenPage.vue`, `EinnahmenPage.vue` (Einbau Hinweisbox) | page | transform | selbst | exact |
| `app/src/lib/glossar.ts` (`GLOSSAR_SCHLUESSEL` +3) | config | - | selbst | exact |

## Pattern Assignments

### `daten/manuell/zuschuesse_lfd_zwecke.csv` (data, file-I/O)

**Analog:** `daten/manuell/kita_zuschuesse.csv` (Z. 1-5)
```csv
tabelle,position,posten,posten_name,ist_gesamt,jahr,wertart,betrag_teur,anmerkung,quelle
kita_zuschuesse,1,kita_st_ambrosius_st_josef,Kita St. Ambrosius und Kita St. Josef,false,2026,ansatz,72,,46
```
Übernehmen: gleiche Spalten, nur Haushaltsjahr, `wertart` `ansatz`, Gesamtzeile `ist_gesamt=true` (120, `quelle=47`), acht Posten von S. 47 (Σ 120 T€). Posten-Schlüssel laut RESEARCH Pattern 7. Kein `quelle` aus Spannen.

### `pipeline/ostbevern/schema.py` / `pruefung.py` / `app_daten.py` (Regel 5 + Weg ins JSON)

**Analog:** `schema.py` Z. 49 `KITA_ZUSCHUESSE_CSV = MANUELL_WURZEL / "kita_zuschuesse.csv"`; Import in `app_daten.py` Z. 40 und `pruefung.py` Z. 42.

**Regel-5-Muster** (`pruefung.py` Z. 1038-1075):
```python
REGEL5_KITA_POSTEN = "zuschuesse_kindertageseinrichtungen"

def _pruefe_regel5_kita_gegen_transfer(*, kita_df, transfer_df) -> tuple[int, list[Pruefpunkt]]:
    transfer_posten_df = transfer_df.filter(pl.col("posten") == REGEL5_KITA_POSTEN)
    if transfer_posten_df.height == 0:
        raise PruefungsFehler(f"Regel 5: Posten {REGEL5_KITA_POSTEN!r} fehlt in transferaufwendungen.csv")
    ...
    punkt = Pruefpunkt(regel=5, plan="vorbericht_kita_zuschuesse", ebene="GESAMT", code="",
        zeile="transfer_kita", jahr=jahr, wertart=kita_gesamt["wertart"],
        soll=transfer_zeile["betrag_teur"] * 1000, ist=kita_gesamt["betrag_teur"] * 1000,
        haushaltsjahr=jahrgang.haushaltsjahr)
```
Neu: Konstante `REGEL5_LFD_ZWECKE_POSTEN = "zuschuesse_laufende_zwecke"`, gleiche Funktionsform; **zusätzlich** Σ der Einzelposten = Gesamtzeile prüfen (siehe Kita-Funktion für Einzelposten-Summe). Aufruf analog Z. 1460-1466 (`if "kita_zuschuesse" in vorbericht and "transferaufwendungen" in vorbericht:` ... `geprueft += ...; abweichungen += ...`). Lader: Eintrag im Dict Z. ~2549 `"kita_zuschuesse": lies_vorbericht_csv(daten_wurzel / KITA_ZUSCHUESSE_CSV)`.

**`app_daten.py` Z. 970-972** (Reihenfolge ist JSON-Vertrag, Test `test_app_daten.py` Z. 187 mitpflegen):
```python
"transferaufwendungen": transferaufwendungen_df,
"kita_zuschuesse": lies_vorbericht_csv(daten_wurzel / KITA_ZUSCHUESSE_CSV),
# <- neu direkt danach: "zuschuesse_lfd_zwecke": lies_vorbericht_csv(daten_wurzel / ZUSCHUESSE_LFD_ZWECKE_CSV),
"investitionszuwendungen": ...
```
Kein `gep_zeile` (wie Kita). Tests: `test_manuell.py` Z. 106 (`(jahr, wertart)`-Menge), Z. 171-205 (grün und manipulierte Abweichung rot). Danach `alle.py --jahr 2026`, `daten/` und `app/src/data/*.json` einchecken.

### `daten/manuell/meta.json` HSK-Schwellen (config)
Analog: bestehende `vorbericht_werte`-Einträge (`einheit`, `quelle`, ganzzahliger `wert`). Neu: `hsk_schwelle_ein_jahr` (25, `prozent`, `quelle` 23) und `hsk_schwelle_zwei_jahre` (5). Keine Schemaänderung nötig (`manuell.py` prüft nur Namensmuster und Blattregeln).

### `texte.py` / `erklaerungen.md` / `glossar.md`
Analog: `daten/manuell/texte/erklaerungen.md` Abschnitt `## nicht_im_haushalt` (Z. 57) für Aufbau (Schlüssel, Platzhalter `{{schluessel|kuerzel}}`, `Quelle: S. n, S. m`), `texte.py` Z. ~275-280 für ABGELEITET-Formeln. Nur vorhandene Kürzel (`euro|mio|zahl|jahr|prozent|promille|vzae`); drei neue Glossarbegriffe `nicht_im_haushalt`, `vzae`, `entgeltgruppen` plus Eintrag in `GLOSSAR_SCHLUESSEL` (`glossar.test.ts` prüft beidseitig). Neue Texte durchlaufen den Abnahme-Checkpoint (D-20).

### `app/src/lib/menue.ts` (utility) + `menue.test.ts` + `App.vue`

**Analog:** `lib/menue.ts` (komplett, 25 Zeilen). Aktuell:
```typescript
export interface MenueEintrag { name: string; text: string; mitJahr: boolean }
export const MENUE: readonly MenueEintrag[] = [
  { name: 'start', text: 'Start', mitJahr: false },
  { name: 'einnahmen', text: 'Woher?', mitJahr: true }, ...
```
Zielform (RESEARCH Pattern 5): `MenueLink {typ:'link'...}`, `MenueGruppe {typ:'gruppe'; text; eintraege}`, `MenueEintrag = MenueLink | MenueGruppe`; Gruppe „Mehr wissen“ vor `glossar`.
**App.vue** Z. 10, 20, 122, 152: `v-for="eintrag in MENUE" :key="eintrag.name"` plus `menueZiel(eintrag)` müssen auf die Union (Schlüssel der Gruppe = `text`) umgestellt werden, in Kopfmenü **und** Drawer.
**Test** (`menue.test.ts`): bestehende Form `MENUE.map(e => e.name)` / `mitJahr`-Filter / Einmaligkeit wird zu: flache Linkliste (Gruppen aufgelöst), Reihenfolge, `mitJahr` nur bei einnahmen/ausgaben/geldfluss, kein doppelter Name über Gruppen, jeder Name existiert im Router.

### `app/src/router/index.ts` (route)
**Analog:** selbst Z. 50-81:
```typescript
{
  path: '/geldfluss',
  name: 'geldfluss',
  component: GeldflussPage,
  meta: { titel: 'Vom Ertrag zur Ausgabe' },
},
```
Vier neue Einträge vor `/:pathMatch(.*)*` mit `meta.titel`. Namen: `entwicklung`, `investitionen`, `rat-entscheidet`, `stellenplan`. Der `afterEach` (Fokus/Titel, reiner Query-Wechsel ändert nichts) bleibt unverändert.

### `app/src/lib/investitionen.ts` (Filter-Query + Bündelung)

**Analog Query-Zustand:** `lib/ansicht.ts` Z. 1-60, 130-200.
```typescript
const PRODUKTE: ReadonlyMap<string, Produkt> = new Map(produkte.map((p) => [p.code, p] as const))
const MODI: ReadonlySet<string> = new Set<Modus>(['aufwand', 'zuschussbedarf'])
function erster(roh: unknown): unknown { return Array.isArray(roh) ? roh[0] : roh }
export function useAnsicht() {
  const route = useRoute(); const router = useRouter()
  const ansicht = computed(() => leseAnsicht(route.query))
  watch(ansicht, (aktuell) => {
    if (aktuell.bereinigt) void router.replace({ query: bereinigteQuery(route.query, aktuell), hash: route.hash })
  }, { immediate: true })
  function setzeModus(modus) { void router.replace({ query: { ...route.query, modus }, hash: route.hash }) }
```
Kopieren: Allowlist über `Map/Set` (nie Objekt-Indexierung), `erster()`, `bereinigt`-Flag, `router.replace` für Filterwechsel (kein Verlaufseintrag), fremde Query-Schlüssel und `hash` erhalten. `art` in {bau, grundstuecke, ausstattung, sonstige}; `pb` nur PB-Codes mit Auszahlungs-Maßnahmen.
**Analog Datenzugriff:** `lib/zeitreihen.ts` (Import `haushalt` aus `@/data/daten`, Jahrgang aus Daten statt Literal, Konstante `ZEITREIHEN_PRODUKT = '160101'` Z. ~48). Bündelung: Schlüssel `produkt/massnahme_id` (nicht nur `massnahme_id`), erst filtern dann bündeln, nur `richtung === 'auszahlung'`, Summe ab `haushalt.jahre.indexOf(haushalt.haushaltsjahr)` (RESEARCH Pattern 1 hat den Code-Entwurf). Test: 89 Gruppen / 59 mit Summe ≠ 0 / Σ 36.361.784 = GFP `auszahlungen_investitionen` 2026-2029; Σ je Art = GFP-Zeile.

### `app/src/lib/bindungsgrad.ts`
**Analog:** `lib/berechnung.ts`, `lib/produkt.ts` (Zugriff auf `berechnet.zuschussbedarf[jahrIndex]`, nichts neu rechnen); Ausschlusskonstante für 160101 **wiederverwenden** aus `lib/zeitreihen.ts` (`ZEITREIHEN_PRODUKT`) oder an gemeinsame Stelle verschieben, kein zweites Literal. Werte > 0 summieren, < 0 in Überschussliste; Test mit Σ 2026: 6.358.143 / 4.491.669 / 2.436.628 = 13.286.440.

### `app/src/lib/ruecklagen.ts`, `entwicklung.ts`, `schulden.ts`, `stellen.ts`, `zuschuesse.ts`
Alle: reine Funktionen, lesen JSON aus `@/data/daten`, kein DOM, jeweils vitest-Test. Analoge Struktur zu `lib/kreisumlage.ts` Z. 1-40 (Kopfkommentar mit Quelle/Regel, Interface mit `gerundet`/`pdfSeite`, Fehler statt stiller Fallbacks: `throw new Error(...)` bei fehlendem Knoten). Besonderheiten:
- Rücklagen: Formel `abbau(t)=max(0,-JE-Ausgleich)-Verrechnung`, `rueckgang=abbau/AR(t)`; Test gegen S. 23 (1,77 / 4,23 / 4,73 / 10,04 %).
- Stellen: Summen in Hundertstel (`Math.round(x*100)`), nur `merkmal==='stellen'|'besetzt'`, Zeilen mit `produktbereich` nicht doppelt zählen; Gruppen absteigend nach `position`; PB nur `ebene==='PB' && eltern==='GESAMT' && !synthetisch`.
- Schulden: `gesamt` = Investitionskredite + NRW.Bank, Liquiditätskredite separat (`null` bleibt `null`).
- Zuschüsse: Kita (`vorbericht.kita_zuschuesse`) + Kinder- und Jugendwerk/OGS (`transferaufwendungen`) + neue Tabelle; `gerundet` (T€ × 1000).

### Balkenkomponenten (`BindungsgradBalken`, `MassnahmenListe`, `StellenBalken`, `RuecklagenBalken`)

**Analog:** `components/ZuschussBalken.vue` (61 Zeilen):
```vue
<script setup lang="ts">
import { computed } from 'vue'
import BaseChart from '@/components/BaseChart.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
const istSchmal = useSchmalerBildschirm()
const option = computed(() => zuschussBalkenOption(props.eintraege, { wertartText: props.wertartText, schmal: istSchmal.value }))
const beschreibung = computed(() => `Balkendiagramm ... Dieselben Werte stehen in der Tabelle darunter.`)
</script>
<template>
  <BaseChart :option="option" :hoehe="`${hoehe}px`" :beschreibung="beschreibung" leer-titel="..." leer-text="..." @chart-click="beiKlick" />
</template>
```
Dazu `charts/balken.ts`: `BalkenZeile {schluessel,name,wert,label,farbe?,decal?}`, `horizontaleBalkenOption`, `balkenHoehe(anzahl)` (40 px/Zeile + 48 px). Der Builder bekommt fertige Texte; Tooltips nur über `charts/tooltip.ts::tooltipZeilen`. Chart-Klick braucht immer Tastaturpfad (Tabelle mit `RouterLink` auf `/produkt/:code`). Diagrammtext/Beschreibung ohne handgetippte Zahlen (`quelltext.test.ts`).

### Zeitreihen (`EntwicklungsDiagramm`, `MiniZeitreihe`)
**Analog:** `components/SteuerZeitreihe.vue` + `lib/zeitreihen.ts` (`Zeitpunkt {jahr, wert, wertart, quelle, pdfSeite, gerundet}`, `ZeitreihenSerie {wertart, werte, geteilt}`). Stil-Tabelle `STILE`/`LEGENDE_TEXT` in ein gemeinsames Modul herausziehen statt kopieren (RESEARCH Don't Hand-Roll). Jahresergebnis-Balken nach Minderaufwand-Entscheidung (Open Question 1 in RESEARCH).

### `HinweisNichtImHaushalt.vue`, `NichtBeeinflussbar.vue` (component)
**Analog:** `components/KreisumlageCallout.vue` Z. 1-50: `wa-callout variant="neutral"` mit `wa-icon slot="icon" name="circle-info"`, `kurz`-Prop für Kurzform, `ErklaerText`, `RouterLink`, Seitenverweise aus Daten, Werte aus `baueKreisumlage(jahrIndex)`, nie neu berechnet. Hinweisbox nutzt Text `nicht_im_haushalt` (Pitfall 10: kein `jahr`-Prop an `ErklaerText`). `NichtBeeinflussbar` liest `KL.*` über `lib/kreisumlage.ts` und `vorbericht.transferaufwendungen.sozialleistungen`.

### Kennzahlkacheln
**Analog:** `components/KennzahlKachel.vue`: Props `bezeichnung`, `wert` (bereits via `format.ts` formatiert), `zeile` („{Wertart} {jahr} · PDF-Seite {n}“), `berechnet?` → `BerechnetEtikett`. Für Stellen (62,91 / 62,13 / 56,63 mit `vzae`-Format) und Schuldenstand (7,71 Mio. €, 656 €) direkt wiederverwenden; Differenzen mit `berechnet`.

### Seiten (`EntwicklungPage`, `InvestitionenPage`, `RatEntscheidetPage`, `StellenplanPage`)
**Analog:** `pages/AusgabenPage.vue` (466 Z., Query-Zustand, `PageIntro`, `ChartCard` mit `:pdf`, `DatenTabelle`-Alternative, `ErklaerText`, `wa-details`) und `pages/EinnahmenPage.vue`. Gemeinsame Regeln: `PageIntro` + `ChartCard` + `BaseChart` + `DatenTabelle`; `ChartCard` ohne `beispieldaten`; jede Zahl-Aussage mit PDF-Seite; Du-Anrede; CSS-Klassen `om-…`, nur `--wa-*`-Tokens (`stiltokens.test.ts`; keine Tokens aus der Hygieneliste: `font-weight: 600`, `--wa-font-weight-semibold`, `--wa-font-size-xl`, `--wa-space-3xs/-2xl`). Kein Jahr-Umschalter auf den vier Seiten. `/investitionen` nutzt zusätzlich `leseMassnahmenFilter`-Muster (siehe oben). In `AusgabenPage`/`EinnahmenPage` die Hinweisbox einbauen (D-18).

### `echartsTheme.ts` (config)
**Analog:** selbst. Nur `MarkLineComponent` ergänzen (`BarChart`/`LineChart` sind schon registriert); Chartfarben (`BINDUNG_FARBEN`, `BERECHNET_DECAL`, `SCHWELLE_FARBE`) ausschließlich dort, PB-Farben über `farbeFuerPb`.

## Shared Patterns

### Zahlenformat
**Source:** `app/src/charts/format.ts` (`euro`, `euroKurz`, `prozent` (Bruch 0-1), `vzae`, `jahr`, `formatiere`, `KEIN_WERT`)
**Apply to:** alle neuen Komponenten und Seiten; keine `toLocaleString`, keine handgetippten Zahlen im `<template>`.

### Tooltips und Balken
**Source:** `app/src/charts/tooltip.ts` (`tooltipZeilen`), `app/src/charts/balken.ts` (`horizontaleBalkenOption`, `balkenHoehe`)
**Apply to:** alle Diagrammbuilder; kein eigenes Tooltip-HTML, kein `v-html`.

### Daten und Allowlists
**Source:** `app/src/data/daten.ts`, `lib/ansicht.ts` (`Map/Set`, `erster()`, `bereinigt`)
**Apply to:** `lib/investitionen.ts` und jede URL-Query-Auswertung.

### Schmale Bildschirme
**Source:** `app/src/lib/bildschirm.ts` (`useSchmalerBildschirm()`)
**Apply to:** alle Diagramme (Achsen tauschen, kleinere Namensbreite, ab 360 px prüfen).

### Pipeline-Texte statt Prosa im Code
**Source:** `erklaerungen.md` + `ErklaerText.vue` / `lib/texte.ts` (`textFuerJahr`)
**Apply to:** RAT-04, Überschuss-Satz, Polster-Satz, Schuldenanstieg; Texte zahlenfrei oder mit Platzhaltern, Seitenverweis `Quelle: S. n`; jede Textänderung → `alle.py --jahr 2026`, `git diff --exit-code -- daten app/src/data`.

### Tests
**Source:** `app/src/lib/__tests__/zeitreihen.test.ts`, `kreisumlage.test.ts`, `ansicht.test.ts`; Pipeline `pipeline/tests/test_manuell.py`
**Apply to:** jedes neue `lib/`-Modul gegen Planzeilen bzw. gedruckte Zahlen; Pipeline-Tests gezielt (`pytest tests/test_manuell.py tests/test_pruefung.py tests/test_app_daten.py tests/test_texte.py -x -q`), volle Suite nur als Gate (ca. 5,5 min).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `app/src/components/MenueGruppe.vue` (Disclosure-Dropdown) | component | request-response | Kein Dropdown/Disclosure im Menü vorhanden; UI-SPEC verlangt Button + `aria-expanded` + Linkliste (kein `role="menu"`). Nur Navigationsblock in `App.vue` und Drawer als Anhalt |
| Gemeinsames Stilmodul Ist/Ansatz/Planung | utility | transform | Logik steckt in `SteuerZeitreihe.vue`; herausziehen, kein fertiger Analog |
| Schwellenlinie `markLine` in Balken | config | transform | Noch nirgends genutzt; `MarkLineComponent` aus `echarts/components` laut RESEARCH |

## Metadata

**Analog search scope:** `app/src/{lib,components,pages,charts,router}`, `pipeline/ostbevern/`, `pipeline/tests/`, `daten/manuell/`, `.planning/phases/05-leitfragen-seiten/05-PATTERNS.md`
**Files scanned:** ca. 30 gelesen/gegrept
**Tracked-Check:** `lib/menue.ts` und `daten/manuell/kita_zuschuesse.csv` via `git ls-files` bestätigt; übrige Analogpfade liegen unter den getrackten Verzeichnissen `app/src`, `pipeline/`, `daten/` (kein `.gsd/capabilities`-Mirror verwendet)
**Pattern extraction date:** 2026-10-06
