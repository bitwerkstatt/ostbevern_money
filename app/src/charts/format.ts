// Einzige Quelle für Zahlenformatierung in der App (UI-05). Jede Zahl, die in
// der Oberfläche erscheint, wird über diese Funktionen oder die hier
// exportierten Formatoptionen (EURO_OPTIONEN) formatiert — niemals mit einer
// eigenen toLocaleString()-Logik in Komponenten.

export const LOCALE = 'de-DE'

export const EURO_OPTIONEN: Intl.NumberFormatOptions = {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
}

const EURO_FORMAT = new Intl.NumberFormat(LOCALE, EURO_OPTIONEN)
const MIO_FORMAT = new Intl.NumberFormat(LOCALE, { maximumSignificantDigits: 3 })
const ZAHL_FORMAT = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 0 })
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

/** Gruppierte Ganzzahl ohne Einheit, z. B. "11.741". */
export function zahl(wert: number): string {
  return ZAHL_FORMAT.format(wert)
}

/** Vollzeitäquivalent mit höchstens zwei Nachkommastellen, z. B. "12,75". */
export function vzae(wert: number): string {
  return VZAE_FORMAT.format(wert)
}

/** Anteil (0–1) als Prozentsatz mit höchstens einer Nachkommastelle, z. B. "34,1 %". */
export function prozent(anteil: number): string {
  return PROZENT_FORMAT.format(anteil)
}
