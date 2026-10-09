---
phase: 09-sicherheit-und-audit
reviewed: 2026-10-09T00:00:00Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - app/src/components/DatenTabelle.vue
  - app/src/components/ErklaerText.vue
  - app/src/components/KreisumlageCallout.vue
  - app/src/components/__tests__/erklaertext.test.ts
  - app/src/components/__tests__/zustaende.test.ts
  - app/src/components/datenTabelle.ts
  - app/src/lib/__tests__/geldfluss.test.ts
  - app/src/lib/__tests__/hilfsfunktionen.test.ts
  - app/src/lib/__tests__/kreisumlage.test.ts
  - app/src/lib/__tests__/quelltext.test.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/hilfsfunktionen.ts
  - app/src/lib/kreisumlage.ts
  - app/src/pages/AusgabenPage.vue
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: issues_found
---

# Phase 9: Code Review Report

**Reviewed:** 2026-10-09
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Reviewed the diff since `2fe66ee` (plan 09-02 `tabellenRahmen`, plan 09-14 G-09-01..03). The `tabellenRahmen` extraction is clean: the pure function is covered for all branches (leere Beschriftung, Whitespace, Überlauf, laden, leer), and `aria-labelledby` points at a caption that exists exactly when the attributes are emitted. No security issues were found; there is no `v-html`, and all text is interpolated.

The three G-09 fixes have gaps. The Superlativ guard can crash the Startseite instead of falling back. `seitenText` prints page lists unsorted, and the data contains such lists. The fallback sentence is not covered by any test.

Vitest could not be run in this environment: the rolldown native binding is missing for this OS (the `node_modules` are macOS binaries). The findings come from reading the code and the data (`haushalt.json`, `texte.json`).

## Warnings

### WR-01: `istGroessterEinzelposten` wirft statt auf die neutrale Fassung zurückzufallen

**File:** `app/src/lib/kreisumlage.ts:88-99,128-141` (aufgerufen aus `app/src/components/KreisumlageCallout.vue:25-29`)
**Issue:** Der Docstring verspricht, dass der Satz auf die neutrale Fassung zurückfällt, wenn der Superlativ nicht trägt. Das gilt nur, wenn die Daten vollständig sind. `kreisumlageWert` wirft, wenn der Posten `kreisumlage` oder der Wert des Jahres `null` ist. `aufwand()` und `baueAufwandsarten()` werfen ebenfalls bei fehlenden Daten.

`einleitung` ist ein `computed` im Template des `kurz`-Zweigs, der Fehler läuft also ungefangen durch den Render. Die Startseite (`StartPage.vue:106`) zeigt dann gar keine Kreisumlage-Karte mehr, oder die ganze Seite bricht ab. Betroffen ist jeder Jahrgang oder jedes Jahr, in dem der Vorbericht die Kreisumlage nicht nennt (`werte[i] === null`). Das ist genau der Fall, für den der Fallback gedacht ist. Die Zeile „Weitergabe an Kreis und Land: X“ selbst bräuchte den Superlativ nicht.
**Fix:** Fehlende Daten bedeuten „Superlativ nicht belegt“, nicht „Absturz“:
```ts
export function istGroessterEinzelposten(jahrIndex: number): boolean {
  try {
    const kl = findeKlKnoten()
    return pruefeGroessterEinzelposten({ /* wie bisher */ })
  } catch {
    return false
  }
}
```
Oder `kreisumlageWert` liefert `number | null` und `istGroessterEinzelposten` gibt bei `null` `false` zurück. Dazu einen Test mit einem Datensatz ohne Kreisumlagewert ergänzen.

### WR-02: `seitenText` gibt Seitenlisten ungeordnet und ungeprüft aus; die Daten enthalten unsortierte Listen

**File:** `app/src/lib/hilfsfunktionen.ts:25-34`; Daten `app/src/data/texte.json`; Aufrufer `ErklaerText.vue:23`, `AusgabenPage.vue:132`, `KreisumlageCallout.vue:47`
**Issue:** `texte.json` enthält `globaler_minderaufwand: [51, 8]` und `defizit_ruecklagen: [24, 9, 311]`. Mit der neuen Funktion erscheint für Bürger „Quelle: PDF-Seiten 51, 8“ bzw. „PDF-Seiten 24, 9, 311“. Das liest sich wie ein Tippfehler. `seitenText` sortiert und dedupliziert nicht. In `KreisumlageCallout` folgt die Reihenfolge der Knotenreihenfolge, nur dort wird per `Set` dedupliziert.

Die Tests zementieren das Verhalten: `erklaertext.test.ts:21` erwartet `seiten.join(', ')` in Datenreihenfolge, `hilfsfunktionen.test.ts:23` prüft nur die Regex `\d+(, \d+)+`. Ein Seitenverweis, der „falsch“ aussieht, verletzt den Kernwert „Jede Zahl ist korrekt belegt“.
**Fix:** In `seitenText` normalisieren:
```ts
const geordnet = [...new Set(seiten)].sort((a, b) => a - b)
if (geordnet.length === 0) return ''
return `${geordnet.length === 1 ? 'PDF-Seite' : 'PDF-Seiten'} ${geordnet.join(', ')}`
```
Die Erwartung in `erklaertext.test.ts` entsprechend anpassen. Alternativ die Reihenfolge in `texte.json` bewusst ordnen, falls sie die Relevanz abbildet, und das dokumentieren. Der Wortlaut „Seiten“ hängt mit der deduplizierten Anzahl zusammen, nicht mit der Rohlänge.

### WR-03: Der Superlativ der Startseite nennt als Quelle nur die Gesamtseite, nicht die Seiten, auf denen der Vergleich beruht

**File:** `app/src/components/KreisumlageCallout.vue:55-63`; `app/src/lib/kreisumlage.ts:101-141`
**Issue:** „Der größte Einzelposten ist …“ ist eine Aussage über Aufgabenbereiche (Teilergebnisplan), Aufwandsarten (Gesamtergebnisplan) und die Vorbericht-Tabelle „Transferaufwendungen“ (gerundete T€-Werte). Die Karte zitiert aber nur `kreisumlage.pdfSeite`, die Seite des Gesamtbetrags. Die Konvention verlangt, dass jede erklärende Aussage mit Zahl auf ihre PDF-Seite verweist. Außerdem vergleicht die Prüfung den gerundeten Vorbericht-Wert (T€ × 1000) mit eurogenauen Aufwandsarten. Bei knappem Abstand (< 1 T€) wäre die Aussage nicht belastbar. Der Test bildet das nicht ab, und die Differenz der Daten ist derzeit groß.
**Fix:** Entweder die Superlativ-Aussage mit den belegenden Seiten kennzeichnen (Gesamtergebnisplan, Vorbericht-Tabelle) oder im Docstring dokumentieren, dass der Satz nur durch den Gesamtbetrag belegt ist. Zusätzlich dem Vergleich der gerundeten gegen genaue Werte eine Toleranz (±1 T€) geben, oder dokumentieren, warum keine nötig ist.

## Info

### IN-01: Der Fallback-Zweig von `einleitung` ist ungetestet

**File:** `app/src/components/KreisumlageCallout.vue:25-29`; `app/src/lib/__tests__/kreisumlage.test.ts:68-112`
**Issue:** Die Tests prüfen `istGroessterEinzelposten` gegen die echten Daten (immer `true`) und `pruefeGroessterEinzelposten` rein. Es gibt keinen Test, der die Komponente rendert und beide Satzfassungen bestätigt, also den eigentlichen Zweck von G-09-01 (der Satz kippt mit den Daten). Eine Regression, bei der `einleitung` nicht mehr im Template steht, bliebe unentdeckt.
**Fix:** `istGroessterEinzelposten` per `vi.mock('@/lib/kreisumlage', …)` auf `false` setzen, die Komponente per `renderToString` rendern (Muster aus `erklaertext.test.ts`) und auf „Weitergabe an Kreis und Land:“ ohne „größte“ prüfen.

### IN-02: Region und Tabelle tragen denselben Namen

**File:** `app/src/components/DatenTabelle.vue:170,181-185`; `app/src/components/datenTabelle.ts:78-84`
**Issue:** Der Rahmen (`role="region"`, `aria-labelledby` → Caption) und die darin liegende `<table>` (Caption) werden von Screenreadern beide mit demselben Namen angesagt („Einnahmen 2026, Region“ … „Einnahmen 2026, Tabelle“). Das ist durch D-20 entschieden, aber bei Ersatzname „Tabelle“ wird es zu „Tabelle, Region“ und „Tabelle, Tabelle“, also nahezu informationslos, und die DEV-Warnung gibt es nur in der Entwicklung. Wirkung bei Aufrufern, die `beschriftung` leer lassen, ist ein stiller Rückfall in schlechte A11y.
**Fix:** Optional: `console.warn` auch in Tests als Fehler behandeln, damit leere Beschriftungen in Aufrufern auffallen (z. B. eine Prüfung über alle Seiten, dass keine `DatenTabelle` mit leerer Beschriftung gerendert wird).

### IN-03: Doppelter Wortlaut „Weitergabe an Kreis und Land:“ im Template

**File:** `app/src/components/KreisumlageCallout.vue:27,71`
**Issue:** Der Text steht an zwei Stellen (im `computed` und im `v-else`-Zweig). Eine spätere Textänderung kann auseinanderlaufen.
**Fix:** Als Konstante `WEITERGABE_LABEL` in der Komponente führen und beide Stellen daraus bilden.

---

_Reviewed: 2026-10-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
