# Phase 5: Leitfragen-Seiten - Pattern Map

**Mapped:** 2026-10-04
**Files analyzed:** 27 (neu/geaendert)
**Analogs found:** 24 / 27 (alle Pfade git-tracked, unter `app/src` bzw. `pipeline/`, `daten/`)

Hinweis: Die App hat KEIN JS-Testframework (`app/package.json` ohne vitest/test-Script). Die Tests fuer D-02, D-11 (Sankey-Ausgleich 6 Jahre, +-2 EUR) und D-16 (Begriffsschluessel) gehen entweder als pytest in `pipeline/tests/` (liest `app/src/data/*.json`, Muster `test_texte.py`) oder als Typ-Check ueber einen Schluesseltyp. Empfehlung: pytest.

## File Classification

| Neue/geaenderte Datei | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `app/src/router/index.ts` (Routen) | route | request-response | selbst (`router/index.ts`) | exact |
| `app/src/App.vue` (Kopfmenue, Fusszeile) | component | request-response | selbst (`App.vue`) | exact |
| `app/src/pages/StartPage.vue` | component/page | transform | selbst (Demo-Seite) | exact |
| `app/src/pages/EinnahmenPage.vue`, `AusgabenPage.vue`, `GeldflussPage.vue`, `GlossarPage.vue`, `ProduktPage.vue` | page | transform | `pages/StartPage.vue` | role-match |
| `app/src/lib/jahr.ts` (Composable `?jahr=`) | hook/utility | request-response | `lib/bildschirm.ts` | role-match |
| `app/src/lib/sankey.ts` / `lib/ausgaben.ts` (reine Ableitungen) | utility | transform | `charts/format.ts` (reine Funktionen) | partial |
| `app/src/charts/echartsTheme.ts` (+Treemap, Sankey, PB-Farben) | config | transform | selbst | exact |
| `app/src/components/Brotkrumen.vue`, `JahrUmschalter.vue`, `KennzahlKachel.vue`, `SankeyDiagramm.vue`, `GlossarBegriff.vue`, `ProduktAkkordeon.vue`, `ErklaerText.vue` | component | request-response | `components/ChartCard.vue`, `BaseChart.vue`, `PageIntro.vue` | role-match |
| `app/src/main.ts` / `lib/webawesome.ts` (wa-details, tooltip, drawer, radio-group) | config | - | selbst (`main.ts` Import-Block) | exact |
| `app/src/data/daten.ts`, `typen.ts` (neue Felder) | model | transform | selbst | exact |
| `app/src/data/jahrgang.json` bzw. Konfig (Kontakt-Mail, PDF-URL, D-17/18) | config | - | `data/jahrgang.json` | exact |
| `app/src/charts/format.ts` (`formatiere`-Fallback, WR-06/IN-01) | utility | transform | selbst | exact |
| `daten/manuell/<pauschalen>.csv`, 2.1.7 in `weitere_vorberichtstabellen.csv` | data | file-I/O | `daten/manuell/steuerarten.csv`, `weitere_vorberichtstabellen.csv` | exact |
| `daten/manuell/README.md` (Erweiterung) | doc | - | selbst | exact |
| `daten/manuell/texte/glossar.md` | data/text | file-I/O | `daten/manuell/texte/erklaerungen.md` | exact |
| `daten/manuell/texte/erklaerungen.md` (D-02 Platzhalter) | data/text | file-I/O | selbst | exact |
| `pipeline/ostbevern/texte.py` (`lies_glossar` o. ae.) | service | file-I/O | selbst (`lies_erklaerungen`) | exact |
| `pipeline/ostbevern/app_daten.py` (neue Tabellen, Glossar nach `texte.json`) | service | batch/transform | selbst (Z. 1007-1034, `baue_vorbericht_tabelle` ~Z. 654) | exact |
| `pipeline/ostbevern/pruefung.py` (Regel 5 neue Tabellen) | service | transform | selbst (Regel 5 fuer `steuerarten`) | exact |
| `pipeline/ostbevern/schema.py` (Pfadkonstanten) | config | - | selbst (`ERKLAERUNGEN_MD`) | exact |
| `pipeline/tests/test_texte.py` + neue Tests (D-02, D-11, D-16) | test | - | `pipeline/tests/test_texte.py` | exact |

## Pattern Assignments

### Seiten (`pages/*Page.vue`) - Analog `app/src/pages/StartPage.vue`

**Imports/Struktur** (Z. 1-14):
```vue
<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import PageIntro from '@/components/PageIntro.vue'
import ChartCard from '@/components/ChartCard.vue'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { euro, euroKurz } from '@/charts/format'
import { POL_FARBEN } from '@/charts/echartsTheme'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
```
Neu: `import { haushalt, produkte, texte } from '@/data/daten'` statt `beispieldaten.json`; `ChartCard` ohne `beispieldaten`-Flag, mit `:pdf="{ seite }"` fuer jede Zahl-Aussage.

**Core-Pattern** (Z. 17-47): `computed<EChartsOption>`, Schmal-/Breit-Umschaltung ueber `istSchmal.value` (x/y-Achse tauschen), `tooltip.valueFormatter: (wert) => euro(wert as number)`, Negativwerte mit `POL_FARBEN.negativ`. Fuer Zuschussbedarf-Balken (D-05) genau dieses Schema (horizontal, negative Balken).

**Tabellenalternative** (Z. 57-69, 80-83): `DatenSpalte[]` mit `art: 'text'|'euro'|'zahl'|'prozent'`, `DatenZeile[]` per computed; `<DatenTabelle beschriftung spalten zeilen />` im `ChartCard` direkt nach `BaseChart`.

### `lib/jahr.ts` (Composable `?jahr=`) - Analog `app/src/lib/bildschirm.ts`
Muster: Composable mit `readonly`-Ref, Cleanup ueber `onScopeDispose`, SSR-Guard (Z. 1-35). Fuer das Jahr: `useRoute()`/`useRouter()`, `computed` aus `route.query.jahr`, Validierung gegen `haushalt.jahre`, Fallback `haushalt.haushaltsjahr`; Setter per `router.replace({ query: { ...route.query, jahr } })`. Hash-Router bereits aktiv (`createWebHashHistory`). Alle `RouterLink`s auf andere Leitfragen-Seiten muessen `query: { jahr }` weitergeben (D-10).

### `router/index.ts` - Analog selbst
```ts
const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'start', component: StartPage },
    { path: '/:pathMatch(.*)*', redirect: { name: 'start' } },
  ],
})
```
Neue benannte Routen vor dem Catch-all: `einnahmen`, `ausgaben`, `geldfluss`, `glossar`, `produkt` (`/produkt/:code`). Fuer Glossar-Anker `#schluessel` `scrollBehavior` ergaenzen (Hash + Fokus, D-16). Fokussteuerung beim Routenwechsel (D-13) im `router.afterEach`.

### `App.vue` (Kopfmenue/Fusszeile) - Analog selbst
Rahmen: `<wa-page>` mit `slot="header"`, `slot="footer"`, `<nav aria-label="Hauptnavigation" class="om-nav"><ul><li><RouterLink :to="{ name }">`; Active-Style `.om-nav a.router-link-exact-active`. Scoped CSS nur mit `--wa-*`-Tokens, Klassen `om-*`. Erweitern: 5 Menuepunkte, `wa-drawer` bei `useSchmalerBildschirm()`, Fusszeile mit Datenstand aus `meta.satzung.beschluss`, PDF-Link/Kontakt aus Konfiguration (nicht im Komponentencode). Muenster-Dank-Link (Z. 21-28) beibehalten.

### Neue Komponenten (`Brotkrumen`, `JahrUmschalter`, `KennzahlKachel`, `SankeyDiagramm`, `GlossarBegriff`, `ProduktAkkordeon`) - Analoga `ChartCard.vue`, `BaseChart.vue`, `PageIntro.vue`
Muster aus `ChartCard.vue` (Z. 1-36): typisierte `defineProps<{...}>()`, `useId()` fuer ARIA-Verknuepfung, `<section :aria-labelledby>`, Web-Awesome-Elemente (`<wa-callout variant>`, `<wa-icon>`) direkt im Template (Custom Elements, in `main.ts` registriert).

`SankeyDiagramm`/Treemap nutzen `BaseChart` (`option`, `hoehe`, `@chartClick`, Leer-Erkennung ueber `series[].data`; BaseChart Z. 1-50). Achtung: `istLeer` prueft nur `data`; Sankey nutzt `data`+`links`, Treemap `data`, also kompatibel.

`GlossarBegriff`: `wa-tooltip` (neu in `main.ts` importieren) + `RouterLink :to="{ name:'glossar', hash:'#'+schluessel }"`; Schluesseltyp aus `texte.json`-Schluesseln ableiten (D-16).

### `echartsTheme.ts` - Analog selbst
Registrierung (Z. 9-12):
```ts
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])
```
Ergaenzen: `TreemapChart`, `SankeyChart` (+ ggf. `AriaComponent` fuer Decal, `LegendComponent`). Farben immer ueber `token('--wa-color-...', '#fallback')` (Z. 20-30), exportierte Konstanten wie `KATEGORIE_FARBEN`/`POL_FARBEN` (Z. 39-61). PB-Palette als neuer Export `PB_FARBEN` (Record PB-Code -> Farbe, Abstufungen fuer Kinder) und `KL_FARBE` + Decal, gleiche Token-Disziplin, keine Hex-Literale ausser als `token`-Fallback.

### `main.ts` / `lib/webawesome.ts` - Analog selbst
Import-Block (main.ts Z. 4-8): `import '@awesome.me/webawesome/dist/components/<name>/<name>.js'` je Komponente. Neu: `details`, `tooltip`, `drawer`, `radio-group` + `radio`, ggf. `button`, `select`.

### `data/daten.ts` / `typen.ts` - Analog selbst
Zuweisung ohne Cast (daten.ts Z. 13-17): `export const texte: Texte = texteJson`. Neue Typfelder (z. B. `Glossarbegriff` in `Texte`) in `typen.ts` ergaenzen; Abweichung des JSON schlaegt `npm run type-check` fehl. Nur lesen, nie neu rechnen (`ergebnisplan[code].berechnet`).

### `format.ts` - Analog selbst
`formatiere(wert, kuerzel)` (Z. 80-97) ist ein erschoepfender `switch` ohne Fallback (WR-06/IN-01). Beim Verdrahten Platzhalterersetzung in einer zentralen Funktion/Komponente (`ErklaerText`): Regex `/\{\{([a-z0-9_.]+)\|([a-z]+)\}\}/g` (identisch zu `PLATZHALTER_MUSTER` in `texte.py` Z. 38), Wert aus `texte.werte[schluessel]`, bei fehlendem Wert Fehler/sichtbarer Platzhalter statt `undefined`. `FormatKuerzel`-Union muss mit `FORMATKUERZEL` in `texte.py` synchron bleiben (Test `test_formatkuerzel_wie_format_ts`).

### Pipeline: manuelle Tabellen (Pauschalen, 2.1.7) - Analog `daten/manuell/steuerarten.csv` / `weitere_vorberichtstabellen.csv`
Langformat-Header:
```
tabelle,position,posten,posten_name,ist_gesamt,jahr,wertart,betrag_teur,anmerkung,quelle
steuerarten,1,grundsteuer_a,Grundsteuer A,false,2024,ergebnis,160,,27
```
Je Posten und Jahr eine Zeile, `betrag_teur`, `quelle` = 1-basierte PDF-Seite, einmal abgeschrieben (D-09), Begruendung im `README.md`. 2.1.7 als neue `tabelle` in `weitere_vorberichtstabellen.csv`. Regel 5 (`pruefung.py`) neu: Pauschalen gegen GFP `investitionszuwendungen` (Z. 18), 2.1.7 zweistufig gegen GEP Z. 07 `sonstige_ordentliche_ertraege`; ein nicht aufgeschluesselter Rest wird in `app_daten.py` als berechnetes „Sonstige“ gebildet. Laeuft ueber `baue_vorbericht_tabelle` (`app_daten.py` ~Z. 654) nach `haushalt.json -> vorbericht`; `typen.ts` `VorberichtTabelle` bleibt unveraendert.

### Pipeline: Glossar (`daten/manuell/texte/glossar.md`, `texte.py`, `app_daten.py`) - Analog `erklaerungen.md` + `lies_erklaerungen`
Dateiformat (`erklaerungen.md` Z. 1-7):
```
# Erklärtexte

## schluesselzuweisung
Titel: Die Schlüsselzuweisung bricht ein
Quelle: S. 28

Absatz mit {{vorbericht.zuwendungen.schluesselzuweisung.2025|mio}} ...
```
Parser (`texte.py` Z. 44-130): Kopfzeile, `^## schluessel$` (`^[a-z][a-z0-9_]*$`, eindeutig), genau Titel- und Quelle-Zeile, Absaetze durch Leerzeilen, `pruefe_text` gegen Ziffernregel (nur Jahreszahlen, `§ n`, `S. n`). Fuer Glossar: `lies_erklaerungen` mit konfigurierbarer Kopfzeile (`_KOPFZEILE = "# Erklärtexte"` -> Parameter, z. B. `# Glossar`) wiederverwenden statt zweiten Parser. `app_daten.py` Z. 1007-1034 (`lies_erklaerungen` -> `pruefe_text` je Absatz -> `textwerte` -> `loese_auf` -> `schreibe_app_json(texte_daten, ..., praefix="texte")`) um die Glossarabschnitte erweitern (z. B. Feld `glossar` in `texte.json`, Typ in `typen.ts`). Schluessel-Namensraum `ABGELEITET`/`textwerte` bei Bedarf erweitern. Pipeline formatiert nie.

### D-02: `erklaerungen.md` Gewerbesteuer
Heute (Z. 11): `{{grundzahlen.160101.1.2022|mio}}`, `...1.2023`, `...1.2024`. 2022/2023 bleiben Grundzahlen (D-01), 2024 wird `{{vorbericht.steuerarten.gewerbesteuer.2024|mio}}` (Muster wie `...gewerbesteuer.2026` im selben Absatz).

### Tests - Analog `pipeline/tests/test_texte.py`
Konventionen: Jahre nie als Literal, sondern aus `haushalt.json` (`haushaltsjahr`/`jahre`); App-JSON via `APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"`; Fixtures wie `echte_erklaerungen`; vorhandene Tests `test_erklaerungen_keine_nackten_ziffern` (Z. 350), `test_erklaerungen_alle_schluessel_existieren` (Z. 356). Neu: (a) D-02: kein `grundzahlen.160101.*`-Platzhalter mit Jahr >= 2024; (b) D-11: je Jahr aus `haushalt.jahre` Summe links == Summe rechts (+-2 EUR, D-19: Minderaufwand links), Ableitungslogik als reine Funktion (TS in `lib/`, Gegenpruefung in pytest ueber JSON); (c) D-16: jeder `GlossarBegriff`-Schluessel existiert.

## Shared Patterns

### Zahlen & Formatierung
**Quelle:** `app/src/charts/format.ts` (`euro`, `euroKurz`, `zahl`, `jahr`, `prozent`, `formatiere`). **Anwenden auf:** alle Seiten/Komponenten. Jahreszahlen immer `jahr()`, nie `zahl()` (CR-01). Keine eigene Intl-Formatierung.

### ChartCard + BaseChart + DatenTabelle
**Quelle:** `StartPage.vue` Z. 55-83. **Anwenden auf:** jedes Diagramm (Treemap, Balken, Sankey, Zeitreihe, Mobilbalken): Tabellenalternative immer mitliefern; `pdf`-Prop fuer Quellseite.

### Schmal/Breit
**Quelle:** `lib/bildschirm.ts` (`useSchmalerBildschirm`, `SCHMAL_BIS = 699`). **Anwenden auf:** Sankey -> gestapelte Balken (D-12), Menue -> `wa-drawer` (D-13).

### Farben
**Quelle:** `charts/echartsTheme.ts` (`token()`, `KATEGORIE_FARBEN`, `POL_FARBEN`). **Anwenden auf:** alle Diagramme; Ausserhalb Charts nur `--wa-*`-Tokens.

### Konventionen
CSS-Praefix `om-`, Du-Anrede, deutsche Bezeichner ohne Umlaute, Werte nur aus `app/src/data/*.json` (kein Neuberechnen), `?jahr=` an allen internen Links, Beispieldaten nur hinter `beispieldaten`-Flag, keine Drittanbieter-Requests.

### Pipeline-Fehlerbehandlung
**Quelle:** `texte.py` (`TexteFehler(ValueError)`), `manuell.py` (`ManuellFehler`); fail-fast, Schritt 07 faengt in `07_app_daten.py` (`AppDatenFehler`, `TexteFehler`, `SchemaFehler`, `PruefungsFehler`). Neue Pruefungen werfen eigene/vorhandene Fehlerklassen mit Dateipfad im Text.

## No Analog Found

| Datei | Role | Data Flow | Grund |
|---|---|---|---|
| Treemap-/Sankey-Optionsbau (`lib/` oder Komponente) | utility | transform | Bisher nur Bar-Chart; Planer nutzt RESEARCH.md (Treemap hierarchisch aus `eltern`, Sankey `nodes`/`links` mit D-19-Bilanz). |
| Brotkrumen-Drilldown-Zustand (Query PB/PG) | component | request-response | Kein Drilldown vorhanden; Muster `lib/jahr.ts` (Query-Composable) uebertragen. |
| JS-Tests fuer Ableitungslogik | test | - | Kein vitest in `app/`; pytest gegen JSON oder vitest neu einfuehren (Plan-Entscheidung). |

## Metadata

**Analog search scope:** `app/src/**`, `pipeline/ostbevern/`, `pipeline/tests/`, `daten/manuell/`
**Files scanned:** ~35 (vollstaendig gelesen: router, App, StartPage, echartsTheme, bildschirm, daten.ts; teilweise: format.ts, texte.py, app_daten.py, typen.ts, ChartCard, BaseChart)
**Pattern extraction date:** 2026-10-04
