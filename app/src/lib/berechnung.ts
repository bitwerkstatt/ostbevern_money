// Gemeinsame Rechenhelfer für Pro-Kopf- und Anteilswerte. Reine Funktionen ohne
// Datenzugriff; formatiert wird ausschließlich über `charts/format.ts`.

/**
 * Betrag pro Einwohner, auf ganze Euro gerundet (kaufmännisch, `Math.round`; nicht
 * abgerundet, RESEARCH Pitfall 3). Der Schuldenstand pro Kopf wird hier nicht neu
 * berechnet, sondern aus `investitionen.schuldenstand.pro_kopf` gelesen.
 */
export function proKopf(betrag: number, einwohner: number): number {
  if (!(einwohner > 0)) {
    throw new Error(`Einwohnerzahl muss größer als 0 sein, war ${String(einwohner)}`)
  }
  return Math.round(betrag / einwohner)
}

/** Anteil `wert / summe` als Bruch (0–1); `null`, wenn die Summe 0 ist. */
export function anteil(wert: number, summe: number): number | null {
  return summe === 0 ? null : wert / summe
}

/** Summe der Werte; `null`-Einträge (fehlende Werte) zählen nicht mit. */
export function summe(werte: readonly (number | null)[]): number {
  return werte.reduce<number>((gesamt, wert) => gesamt + (wert ?? 0), 0)
}

/**
 * Die eine Minderaufwand-Regel für /geldfluss und /ausgaben (D-08, TXT-02). Der Gesamtergebnisplan
 * führt den globalen Minderaufwand (Z. 27) mit negativem Vorzeichen: ein fehlender Wert oder 0 ist
 * kein Minderaufwand (`null`), ein negativer Wert ergibt den positiven Betrag der Kürzung. Ein
 * positiver Wert widerspricht der Struktur des Plans und ist ein Datenfehler: er wirft, statt den
 * Hinweis still zu verbergen. `jahr` steht nur für die Fehlermeldung.
 */
export function minderaufwandBetrag(
  zeile27: number | null | undefined,
  jahr: number,
): number | null {
  if (zeile27 === null || zeile27 === undefined || zeile27 === 0) {
    return null
  }
  if (zeile27 > 0) {
    throw new Error(
      `Globaler Minderaufwand ist positiv: Datenfehler (Jahr ${String(jahr)}, Z. 27 = ${String(zeile27)})`,
    )
  }
  return -zeile27
}
