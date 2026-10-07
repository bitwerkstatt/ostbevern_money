# Phase 7: Feinschliff und Veröffentlichung - Pattern Map

**Mapped:** 2026-10-06
**Files analyzed:** 38 (neu/geändert)
**Analogs found:** 33 / 38 (alle Pfade per `git ls-files` als getrackt bestätigt)

## File Classification

| Neue/geänderte Datei | Role | Data Flow | Closest Analog | Match |
|----------------------|------|-----------|----------------|-------|
| `pipeline/08_quellenbelege.py` | pipeline-script (typer) | batch | `pipeline/07_app_daten.py` | exact |
| `pipeline/ostbevern/quellen.py` | service (Logik) | batch / file-I/O | `pipeline/ostbevern/app_daten.py` (+ `pdf.py`) | role-match |
| `pipeline/ostbevern/pdf.py` (Erweiterung: Wort mit `bottom`) | utility | transform | sich selbst (`Wort`, `Textzeile`) | exact |
| `pipeline/alle.py` (Schritt 08 anhängen) | pipeline-script | batch | sich selbst, Block Schritt 07 | exact |
| `pipeline/tests/test_quellen.py` | test | batch | `pipeline/tests/test_app_daten.py`, `conftest.py` | exact |
| `pipeline/tests/test_alle.py` (Anpassung) | test | batch | sich selbst | exact |
| `pipeline/pyproject.toml` / `uv.lock` | config | — | sich selbst | exact |
| `daten/pruefberichte/quellenbelege.md` | generierter Bericht | file-I/O | `daten/pruefberichte/konsistenz.md` (`pruefung.schreibe_konsistenzbericht`) | role-match |
| `app/src/data/quellen.json`, `app/public/quellen/*.webp` | generierte Daten | file-I/O | `app/src/data/*.json` via `schreibe_app_json` | role-match |
| `app/src/lib/quelle.ts` | service/store (Zustand) | event-driven | `app/src/lib/bildschirm.ts`, `lib/ansage.ts` | role-match |
| `app/src/components/QuelleKnopf.vue` | component | event-driven | `app/src/components/BerechnetEtikett.vue` + `om-menue-schalter` in `App.vue` | role-match |
| `app/src/components/QuelleSeitenleiste.vue` | component | event-driven | Menü-Drawer in `app/src/App.vue` Z. 22-75, 145-170 | exact (Muster) |
| `app/src/components/QuelleSeite.vue` | component | request-response (Bild) | `app/src/components/DatenTabelle.vue` (ResizeObserver, Lade-/Fehlerzweige) | partial |
| `app/src/components/KennzahlKachel.vue` (Prop `quelle`) | component | — | sich selbst | exact |
| `app/src/components/DatenTabelle.vue` / `datenTabelle.ts` (`art: 'quelle'`) | component | CRUD-Anzeige | sich selbst (Slot `zelle`) | exact |
| `app/src/pages/ProduktPage.vue` (Knopf) | page | request-response | sich selbst | exact |
| `app/src/pages/UeberPage.vue` | page | request-response | `app/src/pages/GlossarPage.vue` (+ `PageIntro.vue`) | role-match |
| `app/src/router/index.ts` (Route `ueber`) | route | — | sich selbst (`glossar`-Route) | exact |
| `app/src/App.vue` (Fußzeile, globaler Drawer, Token-Hygiene) | component | event-driven | sich selbst | exact |
| `app/src/config.ts` | config | — | sich selbst | exact |
| `app/src/styles/basis.css` (Reduced Motion) | config/CSS | — | sich selbst, Block `prefers-reduced-motion` | exact |
| `app/public/icons/solid/file-lines.svg` | asset | — | `app/public/icons/solid/circle-info.svg` | exact |
| Token-Hygiene: `GlossarPage.vue`, `GlossarListe.vue`, `EinnahmenPage.vue`, `StellenplanPage.vue`, `ZuschussListe.vue`, `App.vue` | component | — | `ZuschussListe.vue` Z. 231-237 (korrekte Spec-Rolle) | exact |
| WA-`size`-Deprecations: `BerechnetEtikett.vue`, `WertartEtikett.vue`, `AusgabenPage.vue`, `EinnahmenPage.vue`, `ProduktPage.vue`, `EinstiegsKachel.vue` | component | — | — (je Zeile `small`→`s`, `large`→`l`) | trivial |
| `app/src/lib/__tests__/quelle.test.ts` | test | transform | `lib/__tests__/menue.test.ts`, `kennzahlen.test.ts` | role-match |
| `app/src/lib/__tests__/duanrede.test.ts` | test | transform | `lib/__tests__/quelltext.test.ts` (`import.meta.glob ?raw`) | exact |
| `app/src/lib/__tests__/stiltokens.test.ts` (alle Dateien) | test | transform | sich selbst | exact |
| `app/src/lib/__tests__/config.test.ts`, `menue.test.ts` (Anpassung) | test | — | sich selbst | exact |
| `app/e2e/smoke.spec.ts`, `interaktion.spec.ts`, `mobil.spec.ts`, `inventar.spec.ts` | test (Playwright) | request-response | `07-RESEARCH.md` Pattern 4/5 (kein Playwright im Repo) | no analog |
| `app/playwright.config.ts`, `app/tsconfig.e2e.json`, `app/package.json`, `.gitignore` | config | — | `app/tsconfig.node.json`, `app/vitest.config.ts` | role-match |
| `.github/workflows/ci.yml` (Playwright-Schritt, Deploy-Job) | config (CI) | event-driven | sich selbst (SHA-Pins, `permissions`) | exact |
| `daten/manuell/texte/*`, `befunde.md` (D-20 Textänderungen) | doc | — | — | trivial |

## Pattern Assignments

### `pipeline/08_quellenbelege.py` (pipeline-script, batch)

**Analog:** `pipeline/07_app_daten.py` (Z. 1-55, vollständig gelesen)

**Muster:** dünner typer-Einstieg, `--jahr` mit `STANDARD_JAHR`, Fehlerklassen fangen und `typer.Exit(code=1)`, Pfade relativ zu `PROJEKT_WURZEL` ausgeben. Zusätzlich Flag `--neu-rendern` (RESEARCH Pattern 3).
```python
app = typer.Typer(add_completion=False, help="...")

@app.command()
def main(
    jahr: Annotated[
        int,
        typer.Option("--jahr", help="Haushaltsjahr; lädt pipeline/jahrgaenge/{jahr}.toml"),
    ] = STANDARD_JAHR,
) -> None:
    try:
        pfade = erzeuge_app_daten(jahr)
    except (AppDatenFehler, SchemaFehler, KonfigurationsFehler, PruefungsFehler, TexteFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    for pfad in pfade:
        typer.echo(f"Geschrieben: {pfad.relative_to(PROJEKT_WURZEL)}")
```
Eigene `QuellenFehler(ValueError)` analog zu `PdfFehler` in `ostbevern/pdf.py` Z. 17.

### `pipeline/ostbevern/quellen.py` (service, batch/file-I/O)

**Analogs:** `pipeline/ostbevern/app_daten.py` (Schreiben, Lesen der CSVs über `schema.lies_*`), `pipeline/ostbevern/pdf.py` (Wörter, einzige pdfplumber-Stelle).

**Imports/Lesen (app_daten.py Z. 1-60):** `from ostbevern.konfiguration import PROJEKT_WURZEL, lade_jahrgang`, `from ostbevern.schema import DATEN_WURZEL, lies_plan_csv, lies_grundzahlen_csv, lies_investitionen_csv, lies_stellenplan_csv, ...`. Pfade und Dateinamen nur aus `schema.py`-Konstanten, PDF-Pfad nur aus `jahrgang.pdf_pfad`, keine Jahrgangswerte im Code.

**Atomares, deterministisches JSON-Schreiben (app_daten.py Z. 677-692), direkt wiederverwenden:**
```python
def schreibe_app_json(daten: Mapping[str, object], pfad: Path, *, praefix: str) -> None:
    inhalt = json.dumps(daten, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    deskriptor, temp_pfad_str = tempfile.mkstemp(dir=pfad.parent, prefix=f".{praefix}-", suffix=".tmp")
    temp_pfad = Path(temp_pfad_str)
    try:
        with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
            datei.write(inhalt)
        os.replace(temp_pfad, pfad)
    finally:
        temp_pfad.unlink(missing_ok=True)
```
`quellen.json` per `schreibe_app_json(..., praefix="quellen")` schreiben (Koordinaten auf 2 Dezimalstellen runden, Reihenfolge deterministisch sortiert).

**PDF-Zugriff (pdf.py Z. 1-12, 18-45):** nur über `PdfDokument.oeffne(pfad)` als Context Manager; `Wort` (`text,x0,x1,top,groesse,fett`) bekommt ein neues Feld `bottom` **am Ende mit Default** (wie `fett`, damit positionale Konstruktionen gültig bleiben). `import pdfplumber` bleibt exklusiv in `pdf.py`. `pypdfium2`/`Pillow` werden nur im Render-Teil von `quellen.py` importiert (kein pdfplumber dort).

**Zeilensuche/Rendern:** kein Analog im Repo, siehe RESEARCH Pattern 2 (`bbox_mit_rand`) und Pattern 3 (`render(scale=2).to_pil()`, `save(..., "WEBP", quality=60, method=6)`), Bilder nur rendern, wenn sie fehlen.

**Wiederverwenden:** `plaene.lies_abschnitte`, `zeilen.normalisiere_bezeichnung` (RESEARCH „Don't Hand-Roll").

### `pipeline/alle.py` (Schritt 08 anhängen)

**Analog:** Block „Schritt 07“ am Dateiende (Z. ~150-170) und Import-Block Z. 14-45.
```python
try:
    pfade_app_daten = app_daten.erzeuge_app_daten(jahr)
except (AppDatenFehler, SchemaFehler, KonfigurationsFehler, PruefungsFehler, TexteFehler) as fehler:
    typer.echo(f"Fehler: {fehler}", err=True)
    raise typer.Exit(code=1) from fehler
for pfad in pfade_app_daten:
    typer.echo(f"Schritt 07: geschrieben: {pfad.relative_to(PROJEKT_WURZEL)}")
```
Schritt 08 danach (nach grünem Bericht und nach Schritt 07, weil er die App-JSON-Seiten gegenprüft), Modul-Docstring (Z. 1-10) um Schritt 08 ergänzen, `from ostbevern import quellen` und `QuellenFehler` importieren. Fehlende bbox bricht nicht ab (D-03), schreibt nur den Bericht.

### `pipeline/tests/test_quellen.py`, `test_alle.py`

**Analog:** `pipeline/tests/test_app_daten.py` (Z. 1-50: Docstring mit Regel „schreibt nur in tmp, nie in eingechecktes `app/src/data/`“; Test `test_haushalt_json_eingecheckt_aktuell` vergleicht tmp-Ergebnis gegen eingecheckte Datei) und `pipeline/tests/conftest.py` (session-scoped Fixtures `jahrgang`, `pdf_klassifikation`, damit das PDF nur einmal gelesen wird).
```python
@pytest.fixture(scope="session")
def jahrgang() -> Jahrgang:
    return lade_jahrgang(STANDARD_JAHR)
```
Test-Inhalte laut RESEARCH Validation (Probesatz bbox enthält Wort, Seitenmaße pdfplumber = pypdfium2, Bildmaße = 2×Punkt ±1 px, Abdeckungstest über alle `pdf_seite`-Felder der App-JSONs, keine verwaisten Bilder, WebP-Bytes **nicht** vergleichen). `test_alle.py`: Fake-Ergebnisse und `Reihenfolge`-Aufzeichnung (Dataclass mit `reihenfolge`, monkeypatchte Schritte) um Schritt 08 erweitern.

### `daten/pruefberichte/quellenbelege.md` (D-03)

**Analog:** `pruefung.schreibe_konsistenzbericht` (aufgerufen in `alle.py`), Pfadkonstanten `KONSISTENZ_MD`/`BEFUNDE_MD` in `pipeline/ostbevern/schema.py` Z. 38-39. Neue Konstante `QUELLENBELEGE_MD = Path("pruefberichte/quellenbelege.md")` dort anlegen; deterministisch sortiert schreiben (CI-Diff auf `daten/`).

---

### `app/src/lib/quelle.ts` (service/Zustand, event-driven)

**Analogs:** `app/src/lib/bildschirm.ts` (reaktive Flags, `onScopeDispose`, SSR-sicher) und `lib/ansage.ts`/`lib/sprungziel.ts` (kleine, DOM-arme Module mit reiner Logik und Vitest-Test). Reine Funktionen (Schlüsselableitung, bbox→Prozent) getrennt exportieren, damit vitest (`environment: 'node'`, kein DOM) sie testen kann.
```ts
import { onScopeDispose, readonly, ref, type Ref } from 'vue'
export const SCHMAL_BIS = 699
export function useSchmalerBildschirm(): Readonly<Ref<boolean>> { ... readonly(ref(...)) }
```
Zustand als modulweites `ref` (ein Drawer, `oeffneQuelle({ schluessel, bezeichnung, wert?, wertart?, ausloeser })`, `schliesseQuelle`). `quellen.json` über denselben Daten-Zugang importieren wie `haushalt` (`import { haushalt } from '@/data/daten'` in `App.vue` Z. 7) — Planer ergänzt `quellen` dort.

### `app/src/components/QuelleSeitenleiste.vue` (component, event-driven)

**Analog:** Menü-Drawer in `app/src/App.vue`, Z. 22-75 (Logik) und Z. 145-170 (Template).

**Fokusrückgabe + Zustandsabgleich (App.vue Z. 38-56):**
```ts
// `wa-hide` kommt auch bei Escape, Schließen-Knopf und Klick daneben: den Zustand angleichen
function beiHide(ereignis: Event) {
  if (ereignis.target === ereignis.currentTarget) { drawerOffen.value = false }
}
function beiAfterHide(ereignis: Event) {
  if (ereignis.target !== ereignis.currentTarget) { return }
  drawerAktiv.value = false
  if (schliesstDurchSeitenwechsel.value) { schliesstDurchSeitenwechsel.value = false; return }
  menueSchalter.value?.focus()
}
```
**Template (App.vue Z. 148-157):**
```vue
<wa-drawer :id="DRAWER_ID" placement="end" label="Menü" light-dismiss :open="drawerOffen"
  @wa-hide="beiHide" @wa-after-hide="beiAfterHide">
```
Anpassungen laut UI-SPEC: `label="Quelle: PDF-Seite {n}"`, `--size: min(56rem, 100vw)`, vollbreit bis 699 px über `useSchmalerBildschirm()`, Auslöser aus `oeffneQuelle` statt fester Schalter-Ref, Fallback `h1`, Bild per `v-if` erst im geöffneten Zustand. **Abweichung beachten (RESEARCH Pattern 7):** WA 3.14 fokussiert das `<dialog>`, nicht den Schließen-Knopf; Fokus-Vertrag im Test entsprechend prüfen. Eine Instanz in `App.vue` neben dem Menü-Drawer, Routenwechsel-Watch (App.vue Z. 58-66) übernehmen.

### `app/src/components/QuelleKnopf.vue` (component)

**Analog:** natives `<button type="button">` mit `aria-label`/Klick wie `.om-menue-schalter` in `App.vue` Z. 129-139; Props-/`withDefaults`-Stil und Scoped-CSS aus `KennzahlKachel.vue`; `om-visually-hidden` aus `styles/basis.css` für den ergänzten Namensteil (WCAG 2.5.3).
```vue
<button ref="menueSchalter" type="button" class="om-menue-schalter"
  aria-label="Menü öffnen" :aria-expanded=... :aria-controls="DRAWER_ID" @click="oeffneDrawer">
  <wa-icon name="bars" aria-hidden="true"></wa-icon>
</button>
```
`v-if` nur, wenn Schlüssel in `quellen.json` existiert. Klick übergibt `event.currentTarget` als `ausloeser`. Fokusstil/44px per `--wa-*`-Tokens, Klassenpräfix `om-`.

### `app/src/components/QuelleSeite.vue` (component)

**Analog:** teilweise `DatenTabelle.vue` Z. 62-97 (ResizeObserver mit Aufräumen in `onBeforeUnmount`, Zweige Skeleton/Fehler). Rest nach UI-SPEC „Seitenbild und Markierung“ und RESEARCH (bbox ÷ Seitenmaß in Prozent als reine, in `lib/quelle.ts` getestete Funktion). Bild-URL: `import.meta.env.BASE_URL + 'quellen/' + bild`, nie führender `/`.

### `app/src/components/KennzahlKachel.vue` (Erweiterung)

**Analog:** sich selbst (Z. 1-34). Props über `withDefaults(defineProps<{...}>(), {...})`; neuer optionaler Prop `quelle?: string`; `QuelleKnopf` als letztes Element nach `<p class="om-kennzahl__zeile">` (die Zeile behält `margin-top: auto`, `height: 100%` bleibt). Bestehende Tests der Textzeile dürfen nicht brechen.

### `app/src/components/DatenTabelle.vue` (Erweiterung `art: 'quelle'`)

**Analog:** sich selbst. Der Slot `zelle` (`defineSlots`, Z. 31-36) liefert `{ zeile, spalte, wert }`; `SpaltenArt` in `components/datenTabelle.ts` Z. 1-5 um `'quelle'` erweitern. Bestehende „PDF-Seite“-Zellen (`AusgabenPage`, `EinnahmenPage`, `ZuschussListe`, `StellenNachGruppe`) werden zum Knopf, keine zweite Spalte.

### `app/src/pages/UeberPage.vue` (page)

**Analog:** `app/src/pages/GlossarPage.vue` (Z. 1-50): `<script setup lang="ts">`, `PageIntro` mit `titel` und `beschreibung`, Abschnitte als `<section aria-labelledby>` mit `h2 id`, Scoped-CSS mit `--wa-space-*`-Tokens und Klassenpräfix `om-`.
```vue
<PageIntro titel="Glossar und alle Produkte" beschreibung="Hier findest du ..." />
...
<section aria-labelledby="alle-produkte">
  <h2 id="alle-produkte" class="om-glossar-produkte">Alle Produkte</h2>
```
Externe Links wie in der Fußzeile (`target="_blank" rel="noopener noreferrer"` + `wa-icon` + `om-visually-hidden` „(öffnet in neuem Tab)“, App.vue Z. 188-196). Werte aus `@/config`, Du-Anrede, kein `v-html`. Heading-Rolle `--wa-font-size-l` / `--wa-font-weight-bold`.

### `app/src/router/index.ts` (Route `ueber`)

**Analog:** Route `glossar` (Z. 96-100) samt `meta.titel`; neue Seite importieren wie die übrigen Seiten (Z. 10-19), **vor** dem Catch-all `/:pathMatch(.*)*`.
```ts
{ path: '/glossar', name: 'glossar', component: GlossarPage, meta: { titel: 'Glossar' } },
```
`router.afterEach` (Titel, Fokus `h1`, Ansage) greift ohne Änderung.

### `app/src/App.vue` (Fußzeile, Token-Hygiene)

**Analog:** sich selbst, Fußzeilen-Block (Z. ~180-215). Neue `<p>` mit `RouterLink :to="{ name: 'ueber' }"` zwischen Kontakt und „Inspiriert von“; Typografie-Fixes laut UI-SPEC-Tabelle (Z. 238/263 `font-weight: 600` → `var(--wa-font-weight-bold)`, Z. 318 → `--wa-font-weight-normal`, Z. 334 `--wa-space-3xs` → `--wa-space-2xs`). Zusätzlich zweiter `wa-drawer` (`QuelleSeitenleiste`) global. Der Test in `config.test.ts` (Z. 49-65) erwartet, dass `KONTAKT_EMAIL`/`ORIGINAL_PDF_URL` im Quelltext nur als Namen vorkommen, nie als Literale.

### `app/src/config.ts` (Erweiterung)

**Analog:** sich selbst, JSDoc-Stil mit Platzhalter-Konstanten; `istPlatzhalter` (Z. 30-53) bleibt. Neue Impressumsfelder (Name, Anschrift als Zeilenliste) mit `.invalid`-Platzhalter bis zum Text-Checkpoint; `config.test.ts` (`it.each` für Platzhalter/echte Werte, Z. 8-36) erweitern. `istPlatzhalter` erkennt nur E-Mail/URL; ein Name-Platzhalter braucht eine eigene Erkennung oder eine `.invalid`-Mailadresse im Feld.

### `app/src/styles/basis.css` (Reduced Motion)

**Analog:** vorhandener Block am Dateiende:
```css
@media (prefers-reduced-motion: reduce) {
  wa-skeleton::part(indicator) { animation: none; }
}
```
Ergänzen: `:root { --wa-transition-fast: 0ms; --wa-transition-normal: 0ms; --wa-transition-slow: 0ms }` und `wa-drawer { --show-duration: 0s; --hide-duration: 0s }` (Dauer immer mit Einheit).

### Token-Hygiene D-17/D-18

**Analog (Soll-Muster):** `ZuschussListe.vue` Z. 231-237 hat bereits die Rolle Heading nahezu korrekt (aber `font-size-m` statt `-l`):
```css
.om-zuschuesse__untertitel {
  margin: 0;
  font-size: var(--wa-font-size-m);   /* D-18: -> var(--wa-font-size-l) */
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}
```
`StellenplanPage.vue` Z. 244-246 (`.om-stellenplan__gruppe h3`) ebenso. `GlossarPage.vue` `.om-glossar-produkte` (`-xl`/`-semibold` → `-l`/`-bold`). Glossar-`heading-order` (Lighthouse 98): eine `h2` „Begriffe“ vor `<GlossarListe />` in `GlossarPage.vue`.

### `app/src/lib/__tests__/stiltokens.test.ts` (alle Dateien)

**Analog:** sich selbst. Bestehende Struktur: `import.meta.glob(['/src/**/*.vue','/src/**/*.css','/src/**/*.ts'], { query: '?raw', import: 'default', eager: true })`, `verwendeteTokens`, `appDateien` ohne `/__tests__/`, Fail-first-Beispiele. Ändern: `PHASE_6_TYPOGRAFIE_DATEIEN` durch alle `.vue`/`.css` ersetzen, `VERBOTENE_TYPOGRAFIE_TOKENS` um `--wa-font-weight-body`, `--wa-space-3xs`, `--wa-space-2xl`, `--wa-space-5xl` erweitern, zusätzlich Literal-Prüfung in `<style>`-Blöcken (`font-weight: 600`, `font-size: …px|rem`); `.ts` (echartsTheme) ausnehmen. Den Typ-Test „findet alle sechs Phase-6-Dateien“ anpassen.

### `app/src/lib/__tests__/duanrede.test.ts`

**Analog:** `quelltext.test.ts` Z. 1-12 (`import.meta.glob<string>('/src/**/*.vue', { query: '?raw', import: 'default', eager: true })`). `texte.json`/`daten/manuell/texte/*.md` über `?raw` oder `node:fs` wie `config.test.ts` (`readFileSync(new URL('../../App.vue', import.meta.url))`). Geschlossene Ausnahmeliste (Datei + 40 Zeichen Satzanfang + Begründung), Treffer innerhalb eines Satzes immer Fehler, Kommentare nicht prüfen (RESEARCH Pitfall 6).

### `app/src/lib/__tests__/menue.test.ts` (Ausnahmeliste `ueber`)

**Analog:** sich selbst; liest den Routerquelltext (Z. 5-12) und prüft, dass jeder Menüeintrag eine Route hat. Ergänzen: benannte Ausnahmeliste für Fußzeilenrouten (`ueber`), begründet im Test; Route außerhalb von Menü und Liste lässt den Test scheitern.

### `app/e2e/*.spec.ts`, `playwright.config.ts`, `tsconfig.e2e.json`

**Kein Playwright im Repo.** Vorlagen: `07-RESEARCH.md` Pattern 4 (Config und `smoke.spec.ts`, im Sandbox verifiziert), Pattern 5, „Inventar je ChartCard“, Pitfall 8 (`tsconfig.e2e.json`). Strukturanalogs für Config-Dateien:
- `app/tsconfig.node.json` (extends `@tsconfig/node24`, `tsBuildInfoFile` in `./node_modules/.tmp/`, `include` enthält schon `playwright.config.*`) → `tsconfig.e2e.json` mit `lib: ["ES2024","DOM"]`, Eintrag in `app/tsconfig.json` `references`.
- `app/vitest.config.ts`: `include: ['src/**/__tests__/*.test.ts']` bleibt auf `src/` begrenzt, damit vitest die `e2e/`-Specs nicht aufgreift.
- Routenliste aus `menueLinks()` in `app/src/lib/menue.ts` (keine Imports, daher aus Spec importierbar).
- `app/package.json`: Skript `"test:e2e": "playwright test"` nach dem Muster der vorhandenen Skripte (Z. 6-16), `devDependencies` alphabetisch, Versionen exakt wie in RESEARCH.

### `.github/workflows/ci.yml` (Playwright-Schritt, Deploy-Job)

**Analog:** sich selbst. Konventionen: deutsche `name:`-Texte, Aktionen mit voller Commit-SHA und Versionskommentar, `permissions: contents: read` global, `defaults.run.working-directory` je Job.
```yaml
permissions:
  contents: read
...
      - name: Quellcode auschecken
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - name: Node.js einrichten
        uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
```
Ergänzungen: `workflow_dispatch` unter `on:`; im `app`-Job nach „Build“ `npx playwright install --with-deps chromium`, `npm run test:e2e`, dann `actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9 # v5.0.0` (`path: app/dist`, nur `main`); neuer Job `deploy` mit `needs: [pipeline, app]`, `permissions: pages: write, id-token: write`, `environment: github-pages`, `actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346 # v5.0.1` (RESEARCH Pattern 6). Pipeline-Job: Diff-Schritt „Pipeline reproduzierbar (D-24)“ (`git diff --stat --exit-code -- daten app/src/data` plus `git status --porcelain`) läuft schon über `app/src/data/quellen.json`; WebP-Bytes bewusst **nicht** in den Diff aufnehmen (`app/public/quellen` nicht in den Pfadliste). Der Kommentar-Kopf der Datei (D-18 „noch kein Remote“) aktualisieren.

---

## Shared Patterns

### Datenaustausch Pipeline → App (deterministisch)
**Source:** `pipeline/ostbevern/app_daten.py` Z. 677-692 (`schreibe_app_json`)
**Apply to:** `quellen.py` (`quellen.json`), Berichtsdatei. Atomar, UTF-8 ohne BOM, LF, Einfügereihenfolge, `allow_nan=False`, Koordinaten gerundet.

### Fehlerbehandlung in Pipeline-Skripten
**Source:** `pipeline/07_app_daten.py` Z. 38-48, `alle.py`
**Apply to:** `08_quellenbelege.py`, Schritt-08-Block in `alle.py`: modulspezifische `*Fehler`-Klassen (Unterklassen von `ValueError`), `typer.echo(f"Fehler: {fehler}", err=True)`, `raise typer.Exit(code=1) from fehler`.

### Konfiguration statt Jahrgangswerte
**Source:** `ostbevern.konfiguration` (`lade_jahrgang`, `STANDARD_JAHR`, `PROJEKT_WURZEL`)
**Apply to:** alles in `quellen.py`; keine Haushaltsjahrzahl, kein PDF-Pfad, keine Seitenbereiche im Code; App-Texte mit Jahr nutzen Platzhalter aus Daten (`jahr(haushalt.haushaltsjahr)`, `App.vue` Z. 13).

### Quelltext-Wächter über `import.meta.glob ?raw`
**Source:** `app/src/lib/__tests__/quelltext.test.ts` Z. 1-12, `stiltokens.test.ts` Z. 9-13
**Apply to:** `duanrede.test.ts`, erweiterter `stiltokens.test.ts`, optionaler Inventar-Quelltext-Scan. vitest läuft in `environment: 'node'` (kein DOM); DOM-Verhalten wird in Playwright geprüft (jsdom ist nicht freigegeben, D-14).

### Barrierefreie Links/Icons
**Source:** `App.vue` Z. 188-196
**Apply to:** `UeberPage.vue`, `QuelleSeitenleiste.vue` (Link ins Original), Fußzeile:
```vue
<a :href="ORIGINAL_PDF_URL" target="_blank" rel="noopener noreferrer"
  >Original-Haushaltsplan (PDF) der Gemeinde Ostbevern<wa-icon
    name="arrow-up-right-from-square" class="om-extern-icon"></wa-icon
  ><span class="om-visually-hidden"> (öffnet in neuem Tab)</span></a>
```

### Komponenten-Stil
**Source:** `KennzahlKachel.vue`, `PageIntro.vue`
**Apply to:** alle neuen `.vue`: `<script setup lang="ts">`, `defineProps<{...}>()` mit `withDefaults`, `scoped` CSS, Klassen `om-…`, nur `--wa-*`-Tokens, vier Schriftgrößen (`-s`, `-m`, `-l`, `-2xl`) und zwei Gewichte (`-normal`, `-bold`), Absätze mit `margin: 0`, `hyphens: auto; overflow-wrap: break-word`, `@media (min-width: 700px)` als Breakpoint (= `SCHMAL_BIS` 699).

### Web-Awesome-Komponenten
**Source:** `app/src/main.ts` (einzelne Imports, bereits für `wa-drawer`, `wa-callout`, `wa-skeleton`, `wa-icon`, `wa-details` vorhanden), `lib/webawesome.ts` (de-Übersetzung, `setIconPath(import.meta.env.BASE_URL…)`).
**Apply to:** neue Komponenten; `size="s"`/`"l"` statt `small`/`large` (Konsolenwarnung, RESEARCH Pitfall 7).

## No Analog Found

| Datei | Role | Data Flow | Reason |
|-------|------|-----------|--------|
| `app/e2e/*.spec.ts` | test (Playwright) | request-response | Kein Playwright im Repo; RESEARCH Pattern 4/5 und „Code Examples“ (Sandbox-verifiziert) verwenden |
| `pipeline/ostbevern/quellen.py` (Zeilensuche, Rendern) | service | batch | Kein vorhandenes Rendern/bbox-Suchen; RESEARCH Pattern 2/3; Beschriftungsnormalisierung aus `zeilen.py`/`plaene.py` wiederverwenden |
| `.github/workflows` Deploy-Job | CI | event-driven | Kein Deploy im Bestand; RESEARCH Pattern 6 (SHAs per `git ls-remote` geprüft) |
| Lighthouse-Skript (einmalig) | script | batch | nicht im Repo, RESEARCH „Code Examples“; nicht in `package.json` |
| `QuelleSeite.vue` Bild/Overlay | component | — | nur Teilanalog `DatenTabelle.vue`; UI-SPEC „Seitenbild und Markierung“ |

## Hinweise für den Planer

- **Abweichung vom UI-SPEC (Fokus beim Öffnen):** WA 3.14 fokussiert das `<dialog>`, nicht den Schließen-Knopf (RESEARCH Pattern 7); Vertrag und Playwright-Spec anpassen. Eigene Fokusrückgabe wie `beiAfterHide` in `App.vue` bleibt nötig.
- **Seitenzahl:** 231 statt 188 Seiten (Union aller Seitenfelder, RESEARCH Open Question 7); Abdeckungstest über alle JSONs.
- **Datenschutz-Risiko:** Ganze PDF-Seiten können Personennamen zeigen (Stellenplan S. 284-290, Fraktionszuwendungen S. 307/308); Prüfaufgabe einplanen.
- **Paketfreigaben (D-14):** `@playwright/test@1.63.0`, `@axe-core/playwright@4.13.0`, `pypdfium2`/`Pillow` (beide schon in `uv.lock`, nur direkt deklarieren). `lighthouse` braucht einen Checkpoint.
- **D-20:** Kein Diff auf `daten/` und `app/src/data/` außer neuem `quellen.json`; `app/src/data/` ist im CI-Diff enthalten.

## Metadata

**Analog search scope:** `pipeline/`, `pipeline/ostbevern/`, `pipeline/tests/`, `app/src/{components,pages,lib,router,styles}`, `app/*.json|ts`, `.github/workflows`
**Files scanned:** ca. 200 getrackte Dateien (Liste per `git ls-files`), ca. 25 gelesen
**Pattern extraction date:** 2026-10-06
