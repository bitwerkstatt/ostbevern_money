/**
 * Zentrale TypeScript-Typen der von `pipeline/07_app_daten.py` erzeugten JSON-Dateien
 * unter `app/src/data/` (D-21). `daten.ts` importiert `haushalt.json` und weist es ohne
 * Typumwandlung (kein `as`, kein `unknown`) dieser Form zu, sodass `npm run type-check`
 * bei struktureller Drift zwischen Pipeline und App fehlschlägt.
 *
 * Felder mit festem Vokabular (z. B. `wertarten`, `quelle_einheit`) sind als `string`
 * typisiert, weil ein JSON-Import TypeScript-Literale ohnehin zu `string`/`number`
 * verbreitert (keine `as const`-Assertion auf generierten Dateien).
 */

/** Ein einzelner Posten einer manuellen Vorberichtstabelle (D-02, D-05, D-21). */
export interface VorberichtPosten {
  /** Snake-Case-Schlüssel des Postens (z. B. "grundsteuer_a"). */
  posten: string
  /** Gedruckter Name, wie im Vorbericht abgeschrieben. */
  name: string
  /** Betrag in Euro je Eintrag von `jahre`/`wertarten`; `null` ohne Wert für dieses Jahr. */
  werte: (number | null)[]
  /** `true`, wenn der Wert aus einer in T€ geführten Vorbericht-Tabelle × 1000 stammt (D-02). */
  gerundet: boolean
  /** `true` für einen hergeleiteten Wert ohne eigene gedruckte Quelle (z. B. "Sonstige"). */
  berechnet: boolean
  /** 1-basierte PDF-Seite des Postens, `null` für einen rein berechneten Posten. */
  quelle: number | null
  /** Fußnotentext oder sonstige Anmerkung zum Posten, `null` ohne Anmerkung. */
  anmerkung: string | null
}

/** Eine manuelle Vorberichtstabelle (Steuerarten, Zuwendungen, ...), D-07, D-21. */
export interface VorberichtTabelle {
  /** Tabellenname wie in `daten/manuell/` (z. B. "steuerarten"). */
  tabelle: string
  /** Einheit der gedruckten Vorbericht-Beträge; aktuell immer "teur" (D-05). */
  quelle_einheit: string
  /** Kanonischer Schlüssel der zugeordneten Gesamtergebnisplan-Zeile, `null` ohne GEP-Bezug. */
  planzeile: string | null
  /** Eurogenaue GEP-Zeile je Eintrag von `jahre`, `null` ohne `planzeile` (D-01). */
  gesamt_plan: (number | null)[] | null
  /**
   * Die gedruckte, nur in T€ geführte Gesamtzeile × 1000. `werte`-Einträge sind `null` in
   * Jahren ohne gedruckte Gesamtzeile (z. B. kita_zuschuesse außerhalb des Haushaltsjahrs,
   * MANU-04); `quelle` ist `null`, wenn keine einzige Gesamtzeile existiert.
   */
  gesamt_vorbericht: {
    werte: (number | null)[]
    gerundet: boolean
    quelle: number | null
  }
  /** Die Einzelposten der Tabelle in gedruckter Reihenfolge. */
  posten: VorberichtPosten[]
}

/** Ein einzelner Wert in `meta.json` (D-10, MANU-06, D-21). */
export interface MetaWert {
  /** Der Wert selbst; ein ISO-Datum als String nur, wenn `einheit` "datum" ist. */
  wert: number | string
  /** Einheit: "personen" | "ha" | "prozent" | "promille" | "euro" | "datum". */
  einheit: string
  /** 1-basierte PDF-Seite des Werts. */
  quelle: number
  /** ISO-Stichtag des Werts (z. B. Einwohnerzahl), `null` ohne Stichtag. */
  stichtag?: string
  /** Herkunft des Werts (z. B. "IT.NRW"), `null` ohne eigene Herkunftsangabe. */
  herkunft?: string
  /** `true` für einen aus anderen meta.json-Werten berechneten Wert (D-10). */
  berechnet?: boolean
  /** `true`, wenn der Wert aus einer in T€ geführten Quelle × 1000 stammt. */
  gerundet?: boolean
  /** Formelhinweis für einen berechneten Wert, z. B. "netto + rueckstellungsaufloesung". */
  formel?: string
  /** Vorjahreswert desselben Felds, falls im Vorbericht genannt (z. B. Hebesätze). */
  vorjahr?: number
  /** Fußnotentext oder sonstige Anmerkung, `null` ohne Anmerkung. */
  anmerkung?: string
}

/** Meta-Angaben des Haushalts (D-10, MANU-06): Einwohner, Fläche, Hebesätze,
 * Kreisumlage, Satzungsdaten, reservierte Vorbericht-Einzelwerte. */
export interface Meta {
  einwohner: MetaWert
  flaeche: MetaWert
  hebesaetze: Record<string, MetaWert>
  kreisumlage: Record<string, MetaWert>
  satzung: Record<string, MetaWert>
  vorbericht_werte: Record<string, MetaWert>
}

/** Gesamtstruktur von `haushalt.json` (D-21, D-24). */
export interface Haushalt {
  /** Das aktuell dargestellte Haushaltsjahr. */
  haushaltsjahr: number
  /** Jahre der Ergebnisplan-Spalten, z. B. [2024, ..., 2029] (D-21). */
  jahre: number[]
  /** Wertart je Eintrag von `jahre` ("ergebnis" | "ansatz" | "planung"), D-06. */
  wertarten: string[]
  /** Meta-Angaben (Einwohner, Hebesätze, Kreisumlage, Satzung), D-10. */
  meta: Meta
  /** Manuelle Vorberichtstabellen, Schlüssel = Tabellenname. */
  vorbericht: Record<string, VorberichtTabelle>
  /** Entwicklung des Eigenkapitals (S. 311, int-Euro), D-11, D-12. */
  eigenkapital: VorberichtTabelle
}

/** Eine einzelne Stellenplan-Zeile (D-18 bis D-20, EXTR-10, D-21). */
export interface StellenplanZeile {
  /** "beamte" | "tarif" | "sozial_erziehungsdienst" | "nachwuchs". */
  teil: string
  /** Gedruckte Zeilenordnung innerhalb der Tabelle (Teil A/B) bzw. Spaltenordnung
   * (Stellenübersicht). */
  position: number
  /** Gedruckte Gruppe/Entgeltgruppe/Bezeichnung (z. B. "A 14", "9c", "S 12", "pauschal",
   * oder die Nachwuchskräfte-Bezeichnung). */
  gruppe: string
  /** Amtsbezeichnung (nur Beamte, S. 284), sonst `null`. */
  amtsbezeichnung: string | null
  /** Art der Vergütung (nur Nachwuchskräfte, S. 290), sonst `null`. */
  verguetung: string | null
  /** Zweistelliger Produktbereichscode (nur Stellenübersicht-Zeilen, S. 287-289), sonst
   * `null` (Teil A/B- und Nachwuchskräfte-Zeilen). */
  produktbereich: string | null
  /** "stellen" | "davon_ausgesondert" | "besetzt" | "vorgesehen" | "beschaeftigt". */
  merkmal: string
  /** Haushaltsjahr oder Vorjahr, je nach `merkmal` (D-19). */
  jahr: number
  /** ISO-Stichtag für `merkmal` "besetzt"/"beschaeftigt", sonst `null`. */
  stichtag: string | null
  /** Stellen in VZÄ (Hundertstel / 100), `null` für Nachwuchskräfte-Zeilen (D-19: nie
   * eine Stelle). */
  stellen: number | null
  /** Personenzahl (nur Nachwuchskräfte-Zeilen), sonst `null`. */
  personen: number | null
  /** Vermerk zur Gruppe (nur auf der merkmal="stellen"-Zeile des Haushaltsjahrs), sonst
   * `null`. */
  vermerk: string | null
  /** 1-basierte PDF-Seite der Zeile. */
  pdf_seite: number
}

/** Gesamtstruktur von `stellenplan.json` (D-18 bis D-20, EXTR-10, D-21). */
export interface Stellenplan {
  /** Das aktuell dargestellte Haushaltsjahr. */
  haushaltsjahr: number
  /** Einheit der `stellen`-Werte; aktuell immer "vzae" (D-18). */
  einheit_stellen: string
  /** Alle Stellenplan-Zeilen in CSV-Reihenfolge. */
  zeilen: StellenplanZeile[]
}
