/** Ein einzelner Link im Kopfmenü (D-13). */
export interface MenueLink {
  typ: 'link'
  /** Routenname in `router/index.ts`. */
  name: string
  /** Sichtbarer Text des Menüpunkts. */
  text: string
  /** `true`, wenn der Link das gewählte Jahr (`?jahr=`) übernimmt (D-10). */
  mitJahr: boolean
}

/** Eine Gruppe von Links unter einer gemeinsamen Überschrift (D-19). */
export interface MenueGruppe {
  typ: 'gruppe'
  /** Sichtbarer Gruppenname (Schalter im Kopfmenü, Überschrift im Drawer). */
  text: string
  /** Die Untereinträge; eine leere Gruppe wird nicht gerendert. */
  eintraege: readonly MenueLink[]
}

/** Ein Eintrag der obersten Menüebene: Link oder Gruppe. */
export type MenueEintrag = MenueLink | MenueGruppe

/**
 * Die Einträge des Kopfmenüs in der Reihenfolge von D-19. `App.vue` rendert horizontale
 * Liste und mobilen Drawer aus dieser Liste; sie ist die einzige Quelle für beide
 * Darstellungen. Die Gruppe „Mehr wissen“ führt die vier Kontextseiten der Phase 6.
 */
export const MENUE: readonly MenueEintrag[] = [
  { typ: 'link', name: 'start', text: 'Start', mitJahr: false },
  { typ: 'link', name: 'einnahmen', text: 'Woher?', mitJahr: true },
  { typ: 'link', name: 'ausgaben', text: 'Wofür?', mitJahr: true },
  { typ: 'link', name: 'geldfluss', text: 'Geldfluss', mitJahr: true },
  {
    typ: 'gruppe',
    text: 'Mehr wissen',
    eintraege: [
      { typ: 'link', name: 'entwicklung', text: 'Entwicklung', mitJahr: false },
      { typ: 'link', name: 'investitionen', text: 'Investitionen', mitJahr: false },
      { typ: 'link', name: 'rat-entscheidet', text: 'Rat entscheidet', mitJahr: false },
      { typ: 'link', name: 'stellenplan', text: 'Stellenplan', mitJahr: false },
    ],
  },
  { typ: 'link', name: 'glossar', text: 'Glossar', mitJahr: false },
]

/**
 * Routen, die nur aus der Fußzeile verlinkt sind und deshalb nicht in `MENUE` stehen (D-08):
 * „Über dieses Projekt“ mit Impressum und Datenschutz. `menue.test.ts` verlangt, dass jede
 * Route des Routers im Menü oder in dieser Liste steht.
 */
export const FUSSZEILEN_ROUTEN: readonly string[] = ['ueber']

/** Alle Links des Menüs in Anzeigereihenfolge, Gruppen aufgelöst. */
export function menueLinks(): readonly MenueLink[] {
  return MENUE.flatMap((eintrag) => (eintrag.typ === 'gruppe' ? eintrag.eintraege : [eintrag]))
}
