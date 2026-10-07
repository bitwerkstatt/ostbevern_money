// Einzige Quelle für Zahlenformatierung in der App (UI-05). Jede Zahl, die in
// der Oberfläche erscheint, wird über diese Funktionen oder die hier
// exportierten Formatoptionen (EURO_OPTIONEN) formatiert — niemals mit einer
// eigenen, pro Komponente duplizierten Formatierungslogik. Das gilt auch für die
// Regel „rd.“/„rund“ (nur auf T€ genaue Beträge): sie steht nur hier (D-22).

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

/** „rd.“ mit geschütztem Leerzeichen (U+00A0), damit der Zusatz nie allein am Zeilenende steht. */
export const RD_PRAEFIX = 'rd. '

/** „rund“ mit geschütztem Leerzeichen (U+00A0) für Fließtext, damit der Betrag nicht abreißt. */
export const RUND_PRAEFIX = 'rund '

/** Betrag mit „rd.“ davor, wenn er nur auf T€ genau ist; sonst der genaue Euro-Betrag. */
export function betragMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RD_PRAEFIX}${euro(wert)}` : euro(wert)
}

/** Wie `betragMitHinweis`, aber gekürzt über `euroKurz` (Diagrammbeschriftungen). */
export function kurzMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RD_PRAEFIX}${euroKurz(wert)}` : euroKurz(wert)
}

/** Betrag im Fließtext: „rund“ davor nur bei einem Betrag, der nur auf T€ genau ist. */
export function rundMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RUND_PRAEFIX}${euro(wert)}` : euro(wert)
}

/**
 * Gekürzter Betrag im Fließtext, immer mit „rund“ davor, weil `euroKurz` auf drei
 * signifikante Stellen rundet (z. B. „rund 30,5 Mio. €“).
 */
export function rundKurz(wert: number): string {
  return `${RUND_PRAEFIX}${euroKurz(wert)}`
}

/**
 * Gruppierte Ganzzahl ohne Einheit, z. B. "11.741". Für Jahreszahlen (z. B. das
 * Haushaltsjahr) nicht zahl(), sondern jahr() verwenden, weil zahl() sie
 * fälschlich als "2.026" gruppieren würde (CR-01).
 */
export function zahl(wert: number): string {
  return ZAHL_FORMAT.format(wert)
}

/**
 * Anzahl mit passendem Substantiv, z. B. "1 Maßnahme" oder "15 Maßnahmen". Der Singular
 * gilt nur für genau 1; 0 und jede andere Anzahl stehen im Plural (WR-02). Für Texte in
 * Live-Regionen und Zusammenfassungen, damit die Zahl wie überall über zahl() entsteht.
 */
export function anzahlText(anzahl: number, einzahl: string, mehrzahl: string): string {
  return `${zahl(anzahl)} ${anzahl === 1 ? einzahl : mehrzahl}`
}

/** Jahreszahl ohne Tausendertrennung, z. B. "2026" (nicht "2.026", CR-01). */
export function jahr(wert: number): string {
  return JAHR_FORMAT.format(wert)
}

/** Vollzeitäquivalent mit höchstens zwei Nachkommastellen, z. B. "12,75". */
export function vzae(wert: number): string {
  return VZAE_FORMAT.format(wert)
}

const DATUM_FORMAT = new Intl.DateTimeFormat(LOCALE, {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
})

/**
 * ISO-Datum (JJJJ-MM-TT) als deutsches Datum, z. B. "3. März 2026". Das Datum wird
 * als UTC-Tag gelesen und formatiert, damit die Zeitzone des Geräts nie einen Tag
 * verschiebt. Kein gültiges Datum erscheint als `KEIN_WERT`.
 */
export function datum(iso: string): string {
  const treffer = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  if (treffer === null) {
    return KEIN_WERT
  }
  const [jahrTeil, monatTeil, tagTeil] = [
    Number(treffer[1]),
    Number(treffer[2]),
    Number(treffer[3]),
  ]
  const zeitpunkt = new Date(Date.UTC(jahrTeil, monatTeil - 1, tagTeil))
  const unveraendert =
    zeitpunkt.getUTCFullYear() === jahrTeil &&
    zeitpunkt.getUTCMonth() === monatTeil - 1 &&
    zeitpunkt.getUTCDate() === tagTeil
  return unveraendert ? DATUM_FORMAT.format(zeitpunkt) : KEIN_WERT
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
