# Phase 8: Fixes und Triage - Pattern Map

**Mapped:** 2026-10-07
**Files analyzed:** 38 (modified; 3 new)
**Analogs found:** 38 / 38 (Fix-Phase: fast jede Datei ist ihr eigener Analog, neue Dateien haben Rollen-Analoge)

Alle Pfade sind git-tracked (geprüft für `texte.py`, `geldfluss.ts`, `DatenTabelle.vue`, `App.vue`). Zeilennummern stammen vom 2026-10-07. Es gibt keine neuen Pakete.

## File Classification

| Datei (neu/geändert) | Rolle | Datenfluss | Closest Analog | Match |
|---|---|---|---|---|
| `pipeline/ostbevern/texte.py` (`pruefe_text`, `textwerte`, `loese_auf`) | service/validator | transform | selbst (:189-232, :418-428) | exact |
| `pipeline/tests/test_texte.py` (:388 umdrehen) | test | transform | selbst | exact |
| `daten/manuell/texte/erklaerungen.md` (7 Abschnitte) | config/content | transform | Platzhalter `{{jahr.vorjahr\|jahr}}` im Bestand | exact |
| `pipeline/ostbevern/konfiguration.py`, `pipeline/alle.py` | config/CLI | batch | selbst | exact |
| `app/src/charts/format.ts` (+`RD_PRAEFIX`, `betragMitHinweis`, `kurzMitHinweis`, `rundText`) | utility | transform | `lib/geldfluss.ts:123-129` | exact (Umzug) |
| `app/src/lib/geldfluss.ts` (`lesehilfeSatz`, Minderaufwand-Wurf) | service | transform | selbst (:655-686, :260-262) | exact |
| `app/src/lib/berechnung.ts` (reiner Minderaufwand-Helfer) | utility | transform | `proKopf` in selbem File (:9-14) | role-match |
| `app/src/lib/aufwandsarten.ts` (`minderaufwandHinweis`) | service | transform | selbst (:167-186) | exact |
| `app/src/lib/texte.ts` (`istJahrneutral`) | utility | transform | selbst (:62-64) | exact |
| `app/src/lib/einwohner.ts` (NEU) | utility | request-response | `kennzahlen.ts:60-66` | exact |
| `app/src/lib/kennzahlen.ts`, `lib/produkt.ts`, `EbenenTabelle.vue` | service/component | CRUD-read | `kennzahlen.ts:60-66` | exact |
| `app/src/lib/stellen.ts` (`stellenSummen`, `nachwuchs`) | service | transform | selbst (:122-133, :187-200) | exact |
| `app/src/pages/StellenplanPage.vue` | component | request-response | selbst (:66-124) | exact |
| `app/src/lib/zuschuesse.ts`, `components/ZuschussListe.vue` | service/component | transform | selbst (:138-144, :84) | exact |
| rd.-Altkopien: `SteuerZeitreihe.vue`, `PostenZeitreihe.vue`, `AusgabenPage.vue`, `EinnahmenPage.vue`, `drilldown.ts`, `zeitreihen.ts`, `AufwandTreemap.vue`, `NichtBeeinflussbarBlock.vue`, `KreisumlageCallout.vue`, `EuroBetrag.vue` | component/utility | transform | `EuroBetrag.vue` + `format.ts` | exact |
| `app/src/components/DatenTabelle.vue` (+ NEU `components/datenTabelle.ts`) | component | request-response | selbst (:124-169); `ChartCard.vue:2,13` (`useId`) | exact |
| `app/src/components/__tests__/zustaende.test.ts` | test | request-response | selbst | exact |
| `app/src/App.vue` (Drawer) | component | event-driven | selbst (:60-109) | exact |
| `app/e2e/interaktion.spec.ts`, `e2e/mobil.spec.ts` (A11Y-01/02/03, `menueVersatz`) | test (E2E) | event-driven | vorhandene Drawer-Tests (`interaktion.spec.ts:~175,~276`, `mobil.spec.ts:~194`) | exact |
| Wächter-Test rd. (NEU, in `lib/__tests__/` oder `quelltext.test.ts`) | test | file-I/O | `quelltext.test.ts`, `stiltokens.test.ts` (`?raw`-Glob) | role-match |
| `lib/jahr.ts`, `ruecklagen.ts`, `echartsTheme.ts`, `ChartCard.vue`, `app/src/data/beispieldaten.json` (löschen) | util/component | transform | `ruecklagen.ts:219` `haushaltsjahrIndex()`, `echartsTheme.ts` Konstanten | role-match |
| `.planning/milestones/v1.0-phases/{01,05,06}-*/*-REVIEW-DISPOSITION.md` | doc | batch | Fußtext-Format jeder DISPOSITION-Datei | exact |

## Pattern Assignments

### `pipeline/ostbevern/texte.py` (D-01, D-02, D-05)

**Analog:** selbst.

**Zu entfernen** (:42-44 und :221): `_JAHR_MUSTER = re.compile(r"\b(?:19|20)\d{2}\b")` und `rest = _JAHR_MUSTER.sub("", rest)`. Dasselbe Muster bleibt als Prüfmuster erhalten, aber als Fehlerquelle.

**Fehlerstil** (:197-231): nur `TexteFehler(f"...")`, deutsch, mit Textausschnitt. Neuer Check direkt vor der generischen Ziffernprüfung:
```python
rest = _PARAGRAF_MUSTER.sub("", rest)
rest = _SEITE_MUSTER.sub("", rest)
jahr_treffer = _JAHR_MUSTER.search(rest)   # Muster bleibt, Sub fällt weg
if jahr_treffer is not None:
    raise TexteFehler(
        f"Handgetippte Jahreszahl „{jahr_treffer.group(0)}“ ... Jahreszahlen stehen nur als "
        "Platzhalter, zum Beispiel {{jahr.haushaltsjahr|jahr}}."
    )
```
(`{{` im f-String verdoppeln.) Wortlaut: UI-SPEC/RESEARCH Pattern 2. D-05: Titel durch `pruefe_text` laufen lassen und zusätzlich `{{` ablehnen (`ErklaerText.vue:27` rendert Titel roh).

**Neue `jahr.`-Schlüssel** (:420-425, nach `jahr.vorjahr`; Muster):
```python
werte["jahr.haushaltsjahr"] = haushaltsjahr
werte["jahr.vorjahr"] = vorjahr
werte["jahr.letztes_jahr"] = int(jahre[-1])
```
Ergänzen: `jahr.vorvorjahr`, `jahr.haushaltsjahr_plus_1`, `jahr.haushaltsjahr_plus_2`. Feste Jahre `jahr.fest_<JJJJ>` generisch per Regex `^jahr\.fest_(\d{4})$` in `loese_auf`/`vorschau` auflösen, nicht in `werte` (Fixtures bauen `werte` ohne `texte`).

**Tests:** `test_texte.py:388` („im Jahr 2026“ gültig) wird zu `pytest.raises(TexteFehler)`; neue Fälle für Titel mit `{{`, `jahr.fest_2022`-Auflösung, `1990er` (generische Ziffernregel).

---

### `daten/manuell/texte/erklaerungen.md` (D-03)

Keine Code-Analoge, Zuordnung laut RESEARCH Pattern 2: `schluesselzuweisung` :7 `jahr.vorjahr`; `gewerbesteuer` :13 `fest_2022`, `fest_2023`, `vorvorjahr`; `kreisumlage` :19 `vorvorjahr`; `schulden` :49 `vorjahr`; `verpflichtungsermaechtigungen` :55 `haushaltsjahr_plus_1/2`; `ueberschuss_pb_11` :93 `fest_2023`, `fest_2025`; `ueberschuss_ruecklage` :109 `fest_2020`, `fest_2024`. Format: `{{jahr.vorjahr|jahr}}`. Sichtbarer Text 2026 muss identisch bleiben. Bewusster Diff nur in `app/src/data/texte.json`.

---

### `app/src/lib/texte.ts` (D-04)

**Analog:** selbst (:62-64). Aktuell:
```ts
export function istJahrneutral(text: Erklaertext): boolean {
  return text.absaetze.every((absatz) => !new RegExp(PLATZHALTER_MUSTER.source).test(absatz))
}
```
Neu: neutral, wenn jeder Platzhalter-Schlüssel mit `jahr.` beginnt (Schlüssel per Match-Gruppe von `PLATZHALTER_MUSTER` holen, mit `g`-Flag über alle Treffer). Invariantentest: jeder als neutral geltende Text nutzt nur `jahr.fest_*`.

---

### `app/src/charts/format.ts` + rd.-Altkopien (D-22)

**Analog (Quelle zum Verschieben):** `app/src/lib/geldfluss.ts:123-129`:
```ts
export const RD_PRAEFIX = 'rd. '
export function betragMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RD_PRAEFIX}${euro(wert)}` : euro(wert)
}
```
Nach `format.ts` verschieben, Kurzvariante daneben (`kurzMitHinweis` mit `euroKurz`), ebenso `rundText` für „rund“ (`lesehilfeSatz` Satz 1, `geldfluss.ts:661`). `EuroBetrag.vue` importiert dann aus `@/charts/format`. Templates: `<EuroBetrag :wert :gerundet :berechnet>` statt `<span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}`. Vollständige Fundstellenliste: RESEARCH Pattern 1 (17 Stellen). Nicht `zweizeilig()` auf `rd.`-Strings anwenden. Wächter-Test: `import.meta.glob(..., { query: '?raw' })` wie in `quelltext.test.ts`; Kommentare vorher entfernen; `charts/format.ts` und `__tests__/` ausnehmen. Tests anpassen: `geldfluss.test.ts` (~193-230), `zeitreihen.test.ts:232`, `drilldown.test.ts:337`, `quelltext.test.ts:151`.

---

### `app/src/lib/geldfluss.ts` `lesehilfeSatz` (D-06)

**Analog:** selbst (:655-686). Fehlerstelle (:678-680):
```ts
if (!defizit && !ueberschuss) {
  saetze.push('Erträge und Aufwendungen gleichen sich in diesem Jahr genau aus.')
}
```
Vier Fälle: A Defizit, B Überschuss, C nur Minderaufwand (`Die Aufwendungen sind höher als die Erträge. Erst der globale Minderaufwand von ${betragMitHinweis(minderaufwand.wert, minderaufwand.gerundet)} gleicht beide Seiten aus.`), D nichts. „genau“ nur in D, also Bedingung `!defizit && !ueberschuss && !minderaufwand`. Test mit konstruiertem `Geldfluss`-Literal (Typ `geldfluss.ts:73-79`, Knoten :44-58); Bestandstests `geldfluss.test.ts:397-440` bleiben grün.

---

### Minderaufwand-Regel (D-08): `geldfluss.ts:233-262`, `aufwandsarten.ts:167-186`

**Analog:** `geldfluss.ts:260-262` (wirft `'Globaler Minderaufwand ist positiv: Datenfehler'`). Extrahieren als reinen Helfer in `lib/berechnung.ts` (dort „keine Datenzugriffe“, Vorbild `proKopf`, :9-14, wirft bei `einwohner <= 0`), Signatur `(zeile27: number | undefined, jahr: number)`. `minderaufwandHinweis` ersetzt `wert >= 0 → null` (:173) durch: `> 0` wirft mit Jahr in der Meldung, `0`/fehlend gibt `null`. Tests in `aufwandsarten.test.ts:223-280` bleiben, neue Fälle gegen den Helfer.

---

### `app/src/lib/einwohner.ts` (NEU, D-09)

**Analog:** `lib/kennzahlen.ts:60-66`:
```ts
function einwohnerZahl(): number {
  const wert = haushalt.meta.einwohner.wert
  if (typeof wert !== 'number') {
    throw new Error('meta.einwohner.wert muss eine Zahl sein')
  }
  return wert
}
```
Exportieren, Meldung nach Muster „… fehlt in haushalt.json“. `lib/produkt.ts:157-163` und `EbenenTabelle.vue:29,58` darauf umstellen; in `EbenenTabelle` nur im Modus `zuschussbedarf` innerhalb des `zeilen`-Computed aufrufen. Für den Wurf-Test den Meta-Wert injizierbar machen (statischer Import).

---

### `app/src/lib/stellen.ts` + `StellenplanPage.vue` (D-10, D-11)

**Analog:** selbst. `stellen.ts:122-133` liefert nur die Vereinigung `pdfSeiten: seiten([...hj, ...vj, ...besetzt])`. Ergänzen: `seitenHaushaltsjahr`, `seitenVorjahr`, `seitenBesetzt`, Union-Feld und `belegSchluessel.seite(summen.pdfSeiten[0] ?? 0)` (`StellenplanPage.vue:68`) unverändert lassen (`quellen.json` bleibt byte-gleich). `nachwuchs()` (:187-200): nur Seiten der Jahre mit Wert. Kachel-Flags: `berechnet` für alle drei Summen je nach vorhandenem Wert. Tests brauchen ein konstruiertes `Stellenplan` mit unterschiedlichen Seiten, denn die echten Daten haben identische Seiten (284-286).

---

### `lib/zuschuesse.ts` + `ZuschussListe.vue` (D-12)

**Analog:** selbst. `zusammen()` (:138-144) liefert heute `number | null`:
```ts
if (gruppe.gesamt !== null) { return gruppe.gesamt }
const werte = gruppe.posten.flatMap((p) => (p.wert === null ? [] : [p.wert]))
return werte.length === 0 ? null : werte.reduce((summe, wert) => summe + wert, 0)
```
Neu `{ wert, berechnet: gruppe.gesamt === null } | null`. `ZuschussListe.vue:84` baut einen String (`Zusammen rd. …`), der auch als `ChartCard`-`beschreibung` dient (reiner String, keine Komponente). Etikett per `EuroBetrag` + `BerechnetEtikett` im Body, Beschreibung fällt auf `'Zuschuss je Einrichtung.'` zurück, wenn berechnet. Kandidaten für die Prüfung weiterer Summen: siehe RESEARCH Pattern 6 (`investitionen.ts ergebnisText`, `veGesamt`).

---

### `app/src/components/DatenTabelle.vue` (D-16, D-19, D-20)

**Analog:** selbst (:130, :147-169) plus `ChartCard.vue:2,13` (`useId` für `aria-labelledby`). Aktuell:
```vue
<div ref="rahmen" class="om-tabelle-rahmen"
  :role="scrollbarBenannt ? 'region' : undefined"
  :aria-label="scrollbarBenannt ? beschriftung : undefined"
  :tabindex="ueberlaeuft ? 0 : undefined">
...
<caption v-if="beschriftung" class="om-visually-hidden">
```
Neu: `beschriftung: string` (Pflicht); `captionId = useId()`; `<caption :id="captionId" class="om-visually-hidden">` immer; Rahmenattribute per reiner Funktion in neuem `components/datenTabelle.ts` (`rahmenAttribute(ueberlaeuft, captionId)` → `{}` oder `{ tabindex: 0, role: 'region', 'aria-labelledby': captionId }`), gebunden mit `v-bind`. Kein `aria-label`. Slot-Modus samt `istDatenModus` und Default-Slot (:44) entfernen, `zelle`/`zeilenzusatz` bleiben. Abweichungsnotiz (D-16) in Komponentenkommentar. vitest (SSR) sieht Überlauf-Attribute nie, daher Funktionstest plus Playwright bei 360 px. `zustaende.test.ts` um `beschriftung` ergänzen (vue-tsc fängt es nicht).

---

### `app/src/App.vue` Drawer (D-21, A11Y-02)

**Analog:** selbst (:60-109). Bestand: `beiAfterHide` überspringt `menueSchalter.value?.focus()` bei `schliesstDurchSeitenwechsel`; Route-Watcher (:67-75) setzt Flag und `drawerOffen = false`. Fokuslogik der Überschrift als Vorlage aus `beiSeitenklick` (:101-109):
```ts
const ziel = document.querySelector<HTMLElement>('h1') ?? document.querySelector<HTMLElement>('main')
if (ziel !== null) {
  if (!ziel.hasAttribute('tabindex')) { ziel.setAttribute('tabindex', '-1') }
  ziel.focus()
}
```
Umsetzung (RESEARCH Pattern 8, im Scratch verifiziert): `@click="beiDrawerLinkKlick"` an beiden `RouterLink`s (:173, :177); Handler setzt Flag und `drawerOffen = false`; `beiAfterHide` ruft bei gesetztem Flag `setTimeout(fokussiereUeberschrift)` auf, weil Web Awesome den Fokus per `setTimeout` auf den Menüknopf zurücksetzt. Gemeinsamen Helfer `fokussiereUeberschrift` auch für den Skip-Link nutzen. Escape, Schließen-Knopf, Außenklick fokussieren weiter den Menüknopf.

---

### E2E-Tests (A11Y-01/02/03, 06/IN-09)

**Analog:** `app/e2e/interaktion.spec.ts` (~175, ~276, nutzt `page.setViewportSize({ width: 360, height: 640 })`) und `app/e2e/mobil.spec.ts` (~194). Das Projekt `ci` ignoriert `mobil.spec.ts`; CI führt nur `--project=ci` aus. Drawer-Test daher zusätzlich in `interaktion.spec.ts` ablegen. Prettier prüft `e2e/` (`npm run format`). Region-Eindeutigkeit per eigener Prüfung, nicht per axe `landmark-unique`.

---

### Ledger-Dateien (D-17, D-18)

**Analog:** Format in der Fußnote jeder `*-REVIEW-DISPOSITION.md` (Frontmatter-Liste plus Tabelle, `open:` auf 0). Quellspalte: Beleg-Commit oder Begründung. Fixe Zuordnungen laut D-17.

## Shared Patterns

### Datenfehler werfen laut
**Quelle:** `lib/kennzahlen.ts:60-66`, `geldfluss.ts:260-262`, `berechnung.ts:9-14`
**Gilt für:** `einwohner.ts`, Minderaufwand-Helfer, `DatenTabelle.alsZahl` (:139-143). Kein stilles Weglassen, deutsche Meldung mit Jahr bzw. Dateinamen.

### Eine Quelle pro Regel
**Quelle:** `charts/format.ts` (alle Betragsformate), `TexteFehler` in `texte.py`
**Gilt für:** „rd.“, „rund“, Einwohnerzahl, Jahres-Platzhalter, Minderaufwand-Prüfung.

### Quelltext-Wächter per `?raw`
**Quelle:** `lib/__tests__/quelltext.test.ts`, `stiltokens.test.ts`
**Gilt für:** rd.-Wächtertest. Behaltene Konventionstests bekommen einen Begründungskommentar (D-14).

### Scratch-Kopie und Byte-Identität
`app/`-Prüfungen nur in Scratch-Kopie (macOS-`node_modules`). `uv run --directory pipeline python alle.py --jahr 2026` danach `git diff` auf `daten/`, `app/src/data/`, `app/public/quellen`. Erlaubte Diffs: `texte.json` (D-03) und Löschung von `beispieldaten.json` (D-15).

### Commit-Disziplin
Befund-ID mit Phasenpräfix im Betreff (z. B. `05/IN-06`). Nur explizit benannte Pfade stagen, denn `.claude/` und `.planning/state.json` sind ungetrackt bzw. geändert.

## No Analog Found

| Datei | Rolle | Datenfluss | Grund |
|---|---|---|---|
| Playwright-Test für `menueVersatz` (`MenueGruppe.vue:36-62`) | test (E2E) | event-driven | Kein bestehender Resize-/`style.left`-Test; Struktur von `interaktion.spec.ts` übernehmen |
| Test der Überlauf-Attribute von `DatenTabelle` | test | request-response | SSR sieht `ueberlaeuft` nie; über reine Funktion plus Playwright lösen |
| D-15 Icon-Wechsel in `ChartCard` (`triangle-exclamation`) | component | request-response | Icon-Name im Bestand prüfen und unter `app/public/icons` ablegen, falls nicht vorhanden |

Hinweis: Die verbleibenden Befunde (01/IN-02, 01/IN-04, 05/IN-01/03/04/11, 06/IN-01..08) sind klein; Fundstellen stehen in den jeweiligen REVIEW-Dateien. Dort jeweils Datei selbst als Analog nutzen.

## Metadata

**Analog search scope:** `pipeline/ostbevern/`, `pipeline/tests/`, `app/src/{lib,charts,components,pages}`, `app/e2e/`, `daten/manuell/texte/`
**Quellen:** 08-CONTEXT.md, 08-RESEARCH.md (Zeilen 1-392 gelesen, Rest nicht; dort liegen die Befundtabelle und die Konfliktmatrix), direkte Lesungen der oben zitierten Code-Ausschnitte
**Pattern extraction date:** 2026-10-07
