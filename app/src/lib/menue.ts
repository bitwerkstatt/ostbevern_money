/** Ein Eintrag im Kopfmenü (D-13). */
export interface MenueEintrag {
  /** Routenname in `router/index.ts`. */
  name: string
  /** Sichtbarer Text des Menüpunkts. */
  text: string
  /** `true`, wenn der Link das gewählte Jahr (`?jahr=`) übernimmt (D-10). */
  mitJahr: boolean
}

/**
 * Die Einträge des Kopfmenüs in der Reihenfolge von D-13. `App.vue` rendert horizontale
 * Liste und mobilen Drawer aus dieser Liste.
 *
 * Phase 6 ergänzt die Gruppe „Mehr wissen“ als weiteren Eintragstyp (Dropdown mit
 * Untereinträgen): `MenueEintrag` wird dafür zu einer Vereinigung erweitert, die Liste
 * bleibt die einzige Quelle für beide Darstellungen.
 */
export const MENUE: readonly MenueEintrag[] = [
  { name: 'start', text: 'Start', mitJahr: false },
  { name: 'einnahmen', text: 'Woher?', mitJahr: true },
  { name: 'ausgaben', text: 'Wofür?', mitJahr: true },
  { name: 'geldfluss', text: 'Geldfluss', mitJahr: true },
  { name: 'glossar', text: 'Glossar', mitJahr: false },
]
