// Horizontale Position der geöffneten „Mehr wissen“-Liste (D-19, UI-SPEC E12 Überlauf).
//
// WR-01: Die Liste behält ihr inline gesetztes `left`, auch wenn sie geschlossen ist. Ein
// gemessenes Rechteck enthält deshalb den zuletzt angewandten Versatz; eine Korrektur relativ
// zu diesem Rechteck lässt beim zweiten Öffnen und beim Verändern der Fenstergröße den Überlauf
// zurückkehren. Hier wird die Basisposition (Rechteck minus angewandter Versatz) bestimmt und
// der absolute Versatz zurückgegeben. Die Funktion ist rein, damit der Node-Test sie ohne DOM
// abdeckt.

/** Gemessenes Rechteck der Liste und Fenstermaße, alles in px. */
export interface ListenMessung {
  /** Linke Kante des gemessenen Rechtecks; enthält `angewandterVersatz`. */
  links: number
  /** Rechte Kante des gemessenen Rechtecks; enthält `angewandterVersatz`. */
  rechts: number
  /** Versatz, den die Liste beim Messen bereits trägt (inline `left`). */
  angewandterVersatz: number
  fensterbreite: number
  /** Mindestabstand zum Fensterrand. */
  rand: number
}

/** Absoluter Versatz gegenüber der CSS-Basisposition; hängt nicht vom angewandten Versatz ab. */
export function listenVersatz(messung: ListenMessung): number {
  const basisLinks = messung.links - messung.angewandterVersatz
  const basisRechts = messung.rechts - messung.angewandterVersatz
  let versatz = 0
  if (basisRechts > messung.fensterbreite - messung.rand) {
    versatz = messung.fensterbreite - messung.rand - basisRechts
  }
  if (basisLinks + versatz < messung.rand) {
    versatz = messung.rand - basisLinks
  }
  return versatz
}

/**
 * Rand aus der berechneten `max-width` der Liste (`100vw - 2 * Rand`): ohne Pixelwert 0,
 * nie negativ.
 */
export function randAusMaximalbreite(fensterbreite: number, maximalbreite: string): number {
  const maximal = parseFloat(maximalbreite)
  if (Number.isNaN(maximal)) {
    return 0
  }
  return Math.max(0, (fensterbreite - maximal) / 2)
}
