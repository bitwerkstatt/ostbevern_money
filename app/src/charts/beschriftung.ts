// Gemeinsamer Helfer für Diagrammbeschriftungen über Säulen (Phase 6): Beträge wie „21,3 Mio. €“
// werden auf schmalen Bildschirmen und in gruppierten Säulen zweizeilig gesetzt, damit sechs
// Beschriftungen nebeneinander nicht überlappen.

/**
 * Trennt einen Text am ersten Leerraum in zwei Zeilen: „21,3 Mio. €“ wird „21,3“ und
 * „Mio. €“, „712.600 €“ wird „712.600“ und „€“ (das Euro-Format trennt mit geschütztem
 * Leerzeichen, auch das zählt). Ein Text ohne Leerraum bleibt einzeilig.
 */
export function zweizeilig(text: string): string {
  const stelle = text.search(/\s/)
  return stelle < 0 ? text : `${text.slice(0, stelle)}\n${text.slice(stelle + 1)}`
}
