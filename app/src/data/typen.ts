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

/** Ein Knoten der Haushaltshierarchie (PB/PG/P, GESAMT, oder die synthetische
 * "Weitergabe an Kreis und Land" KL/KL.<posten>), D-03, D-21. */
export interface Knoten {
  /** Eindeutiger Code; "GESAMT" | "KL" | "KL.<posten>" | PB-/PG-/Produktcode. */
  code: string
  /** "GESAMT" | "PB" | "PG" | "P". */
  ebene: string
  /** Gedruckter Name ("Allgemeine Finanzwirtschaft" für PB 16 nach der Reduktion, D-03). */
  name: string
  /** Code des Elternknotens; `null` nur für GESAMT. */
  eltern: string | null
  /** `true` für einen nicht gedruckten Knoten (synthetische PG, KL, KL.<posten>). */
  synthetisch: boolean
  /** `true` für die drei KL-Unterposten: ihr Wert ist die Vorbericht-Abschrift × 1000,
   * nicht eurogenau (D-02; die App zeigt sie als "rd."). */
  gerundet: boolean
  /** 1-basierte PDF-Seite des Knotens, `null` ohne eigene Quellseite. */
  pdf_seite: number | null
}

/** Ergebnisplan-Werte eines Knotens (D-01 bis D-04, D-22, D-23). */
export interface KnotenWerte {
  /** Zeile (kanonischer Schlüssel, `ERGEBNISPLAN_APP_ZEILEN`) -> Betrag je `jahre`. */
  zeilen: Record<string, number[]>
  /** Aus `zeilen` abgeleitete, gekennzeichnet berechnete Werte (DATA-03). Aufwand =
   * Z. 17 + Z. 20, Erträge = Z. 10 + Z. 19, Zuschussbedarf = Aufwand − Erträge (vor
   * Minderaufwand, D-23); Überschuss = Zuschussbedarf < 0, ohne Sonderregel für
   * irgendeinen Knoten (D-04). */
  berechnet: {
    aufwand: number[]
    ertraege: number[]
    zuschussbedarf: number[]
    ueberschuss: boolean[]
  }
}

/** Gesamtfinanzplan-Werte, nur auf GESAMT-Ebene (D-22). */
export interface FinanzplanWerte {
  /** Zeile (kanonischer Schlüssel) -> Betrag je `jahre` (Zeilen 01-41). */
  zeilen: Record<string, number[]>
  /** Zeile (kanonischer Schlüssel) -> VE-Betrag zum Haushaltsjahr (nicht je `jahre`,
   * VE wird nur für das Haushaltsjahr geführt). */
  ve: Record<string, number>
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
  /** Alle Knoten der Hierarchie inkl. KL und seinen drei Kindern (D-03). */
  knoten: Knoten[]
  /** Ergebnisplan-Werte je Knoten-Code (D-01 bis D-04, D-22, D-23). */
  ergebnisplan: Record<string, KnotenWerte>
  /** Gesamtfinanzplan-Werte, nur GESAMT (D-22). */
  finanzplan: Record<string, FinanzplanWerte>
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

/** Ein einzelner Jahreswert einer Grundzahl (EXTR-07, D-13, D-21). */
export interface GrundzahlWert {
  jahr: number
  /** `int`, wenn `nachkommastellen` der Grundzahl 0 ist, sonst mit `nachkommastellen`
   * Nachkommastellen gerundet (Gebühren, Quoten). */
  wert: number
  /** Stichtag- oder Fußnotentext, `null` ohne Hinweis. */
  hinweis: string | null
}

/** Eine Grundzahl (Kennzahl) eines Produkts, gruppiert nach `position` (EXTR-07, D-13). */
export interface Grundzahl {
  position: number
  /** Gruppenüberschrift, `null` ohne eigene Gruppe. */
  gruppe: string | null
  bezeichnung: string
  einheit: string
  nachkommastellen: number
  pdf_seite: number
  werte: GrundzahlWert[]
}

/** Ein Erläuterungsposten eines Produkts (EXTR-08). */
export interface Erlaeuterung {
  block: number
  position: number
  /** Zweistellige Zeilennummern, auf die sich der Posten bezieht, `null` ohne Bezug. */
  zu_zeilen: string[] | null
  /** `null` für eine Freitextzeile. */
  betrag: number | null
  text: string
  pdf_seite: number
}

/** Ein Produkt der App (DATA-01, D-13, D-21): `daten/aufbereitet/produkte.json`
 * (bereits namensfrei, Phase 3 D-09) plus seine Grundzahlen. */
export interface Produkt {
  code: string
  name: string
  pb: string
  pg: string
  fachbereich: string
  gremium: string
  beschreibung: string
  leistungen: string[]
  auftragsgrundlage: string
  bindungsgrad: string
  bindungsgrad_original: string
  klassifizierung: string
  zielgruppe: string
  ziele: string
  erlaeuterungen: Erlaeuterung[]
  pdf_seiten: number[]
  grundzahlen: Grundzahl[]
}

/** Eine Investitionsmaßnahme (D-13, D-21), gruppiert nach Produkt/Maßnahme/Konto. */
export interface Massnahme {
  produkt: string
  /** Produktbereichscode, über die Hierarchie aus `produkt` abgeleitet. */
  pb: string
  massnahme_id: string
  massnahme_name: string
  konto: string
  konto_name: string
  /** "einzahlung" | "auszahlung". */
  richtung: string
  /** Investitionsart (z. B. "bau", "ausstattung", "grundstuecke"), `null` für
   * Finanzierungstätigkeit-Konten. */
  art: string | null
  /** Betrag je Eintrag von `jahre` (haushalt.json-Jahre), `null` ohne Wert für dieses
   * Jahr. */
  werte: (number | null)[]
  /** Verpflichtungsermächtigung zum Haushaltsjahr, `null` ohne VE. */
  ve: number | null
  pdf_seite: number
}

/** Eine VE-Fälligkeitszeile (EXTR-09, D-13, D-21). */
export interface VeFaelligkeit {
  produkt: string
  massnahme_id: string
  konto: string
  jahr: number
  betrag: number
  pdf_seite: number
}

/** Finanzierung der Investitionstätigkeit (GFP Z. 23, 30, 33, 35), D-13, D-21. */
export interface Finanzierung {
  /** 1-basierte PDF-Seite des Gesamtfinanzplans. */
  quelle: number
  zeilen: {
    einzahlungen_investitionen: number[]
    auszahlungen_investitionen: number[]
    kreditaufnahme: number[]
    tilgung: number[]
  }
}

/** Schuldenstand nach Vorbericht-Definition (D-14, D-21): Investitionskredite plus die
 * als Transferverbindlichkeit gebuchten NRW.Bank-Mittel. Fortgeschrieben ab dem letzten
 * gedruckten Stand (`berechnet: true`), NRW.Bank-Anteil dabei konstant (Pitfall 5). */
export interface Schuldenstand {
  /** 1-basierte PDF-Seite der Verbindlichkeiten-Tabelle (S. 310). */
  quelle: number
  einwohner: number
  /** Je Eintrag von `jahre`. */
  investitionskredite: number[]
  nrw_bank: number[]
  /** `null` für ein Jahr ohne gedruckten Stand. */
  liquiditaetskredite: (number | null)[]
  gesamt: number[]
  /** Abgerundet (`pro_kopf_euro`, ganzzahlige Division). */
  pro_kopf: number[]
  /** `true` für ein fortgeschriebenes (nicht gedrucktes) Jahr. */
  berechnet: boolean[]
  /** Deutscher Formelhinweis, identisch für jedes Jahr (D-15: keine Formatierung). */
  formel: string
}

/** Eine Bürgschaft (nachrichtlich, D-21). */
export interface Buergschaft {
  name: string
  /** Je Eintrag von `jahre`, `null` ohne gedruckten Wert. */
  werte: (number | null)[]
}

/** Gesamtstruktur von `investitionen.json` (D-13, D-14, D-21). */
export interface Investitionen {
  haushaltsjahr: number
  jahre: number[]
  wertarten: string[]
  massnahmen: Massnahme[]
  ve_faelligkeiten: VeFaelligkeit[]
  finanzierung: Finanzierung
  schuldenstand: Schuldenstand
  /** Schlüssel = Postenname (z. B. "bbo_buergschaft"). */
  buergschaften: Record<string, Buergschaft>
}

/**
 * Ein geprüfter Erklärtext (D-15 bis D-17, MANU-08). `absaetze` enthält den Rohtext
 * mit unaufgelösten `{{schluessel|formatkuerzel}}`-Platzhaltern — die App ersetzt sie
 * zur Laufzeit gegen `Texte.werte` und formatiert mit `format.ts::formatiere`. Die
 * Pipeline formatiert nie (D-15).
 */
export interface Erklaertext {
  /** Eindeutiger Schlüssel, z. B. "schluesselzuweisung". */
  schluessel: string
  titel: string
  /** 1-basierte PDF-Seite(n) des Vorberichts, die diesen Text belegen. */
  quelle_seiten: number[]
  /** Absätze in Reihenfolge; jeder kann mehrere Platzhalter enthalten. */
  absaetze: string[]
}

/** Gesamtstruktur von `texte.json` (D-15 bis D-17, MANU-08, D-21). */
export interface Texte {
  haushaltsjahr: number
  texte: Erklaertext[]
  /** Nur die tatsächlich in `texte` verwendeten Datenschlüssel -> Rohwert (kein
   * vollständiger Daten-Dump, D-15). */
  werte: Record<string, number>
}
