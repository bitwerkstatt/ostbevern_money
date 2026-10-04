// Einzige Quelle für Zahlenformatierung in der App (UI-05). Jede Zahl, die in
// der Oberfläche erscheint, wird über diese Funktionen oder die hier
// exportierten Formatoptionen (EURO_OPTIONEN) formatiert — niemals mit einer
// eigenen, pro Komponente duplizierten Formatierungslogik.

export const LOCALE = 'de-DE'

/** Sichtbarer Ersatz für einen fehlenden Zahlenwert (UI-SPEC „Fehlender Zahlenwert“). */
export const KEIN_WERT = '–'

export const EURO_OPTIONEN: Intl.NumberFormatOptions = {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
}

const EURO_FORMAT = new Intl.NumberFormat(LOCALE, EURO_OPTIONEN)
const MIO_FORMAT = new Intl.NumberFormat(LOCALE, { maximumSignificantDigits: 3 })
const ZAHL_FORMAT = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 0 })
const JAHR_FORMAT = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 0, useGrouping: false })
const VZAE_FORMAT = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 2 })
const PROZENT_FORMAT = new Intl.NumberFormat(LOCALE, {
  style: 'percent',
  maximumFractionDigits: 1,
})

/** Voller Euro-Betrag ohne Nachkommastellen, z. B. "2.353.506 €". */
export function euro(wert: number): string {
  return EURO_FORMAT.format(wert)
}

/**
 * Gekürzter Euro-Betrag für Beträge ab 1 Mio. € (absolut), z. B. "27,5 Mio. €"
 * oder "-2,35 Mio. €". Kleinere Beträge fallen auf euro() zurück.
 */
export function euroKurz(wert: number): string {
  if (Math.abs(wert) >= 1_000_000) {
    return `${MIO_FORMAT.format(wert / 1_000_000)} Mio. €`
  }
  return euro(wert)
}

/**
 * Gruppierte Ganzzahl ohne Einheit, z. B. "11.741". Für Jahreszahlen (z. B. das
 * Haushaltsjahr) nicht zahl(), sondern jahr() verwenden, weil zahl() sie
 * fälschlich als "2.026" gruppieren würde (CR-01).
 */
export function zahl(wert: number): string {
  return ZAHL_FORMAT.format(wert)
}

/** Jahreszahl ohne Tausendertrennung, z. B. "2026" (nicht "2.026", CR-01). */
export function jahr(wert: number): string {
  return JAHR_FORMAT.format(wert)
}

/** Vollzeitäquivalent mit höchstens zwei Nachkommastellen, z. B. "12,75". */
export function vzae(wert: number): string {
  return VZAE_FORMAT.format(wert)
}

/** Anteil (0–1) als Prozentsatz mit höchstens einer Nachkommastelle, z. B. "34,1 %". */
export function prozent(anteil: number): string {
  return PROZENT_FORMAT.format(anteil)
}

/**
 * Formatkürzel der Platzhalter in `texte.json` (D-15), z. B. `{{meta.einwohner|zahl}}`.
 * Muss exakt `ostbevern.texte.FORMATKUERZEL` entsprechen
 * (Pipeline-Test `test_formatkuerzel_wie_format_ts`).
 */
export type FormatKuerzel = 'euro' | 'mio' | 'zahl' | 'jahr' | 'prozent' | 'promille' | 'vzae'

/**
 * Formatiert einen Rohwert aus `texte.json` nach seinem Platzhalter-Formatkürzel
 * (D-15): die Pipeline liefert nur Rohwerte, diese Funktion ist die einzige Stelle,
 * die einen `{{…|kuerzel}}`-Platzhalter in einen angezeigten String verwandelt.
 * `zahl` gruppiert Tausender (z. B. Einwohnerzahlen), `jahr` tut das bewusst nicht
 * (Jahreszahlen wie das Haushaltsjahr, CR-01). `prozent`/`promille` erwarten den
 * Rohwert als ganze Prozent- bzw. Promillepunkte (z. B. Hebesatz 554 oder 363),
 * nicht als Anteil 0–1.
 *
 * Fehlender Zahlenwert (UI-SPEC „Fehlender Zahlenwert“, WR-06/IN-01): `null`,
 * `undefined`, `NaN` und `±Infinity` erscheinen als sichtbarer Gedankenstrich
 * `KEIN_WERT` — nie als 0, „NaN“ oder „undefined“, damit ein Text keine falsche
 * Zahl still anzeigt. Ein unbekanntes Formatkürzel wirft einen Fehler, der das
 * Kürzel nennt, statt `undefined` zu liefern.
 */
export function formatiere(wert: number | null | undefined, kuerzel: FormatKuerzel): string {
  if (wert === null || wert === undefined || !Number.isFinite(wert)) {
    return KEIN_WERT
  }
  switch (kuerzel) {
    case 'euro':
      return euro(wert)
    case 'mio':
      return euroKurz(wert)
    case 'zahl':
      return zahl(wert)
    case 'jahr':
      return jahr(wert)
    case 'prozent':
      return prozent(wert / 100)
    case 'promille':
      return prozent(wert / 1000)
    case 'vzae':
      return vzae(wert)
    default: {
      const unbekannt: never = kuerzel
      throw new Error(`Unbekanntes Formatkürzel: ${String(unbekannt)}`)
    }
  }
}
