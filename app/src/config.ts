// Projektkonfiguration, die nicht aus dem Haushalts-PDF stammt: Kontakt, Link zum
// Original-Haushaltsplan (D-06, D-07) und die Impressumsfelder (D-08). Die Fußzeile in
// `App.vue` und die Seite `UeberPage.vue` lesen ausschließlich diese Konstanten; weder die
// Adresse noch die URL noch Name oder Anschrift stehen in Komponenten.

/**
 * Kontaktadresse in der Fußzeile und im Impressum (D-07).
 *
 * Der Wert ist festgelegt. Die Prüfung `istPlatzhalter(KONTAKT_EMAIL)` bleibt als Wächter
 * bestehen: `config.test.ts` und der Smoke-Test weisen das Deployment ab, falls hier je
 * wieder ein Platzhalter auf der reservierten Domain `.invalid` (RFC 2606) steht.
 */
export const KONTAKT_EMAIL = 'mail@thomas-manthey.de'

/**
 * Link zum Original-Haushaltsplan (PDF) der Gemeinde Ostbevern (D-06): die offizielle Datei
 * der Gemeinde. Es wird keine eigene Kopie des PDFs ausgeliefert.
 *
 * Der Wert ist festgelegt. `istPlatzhalter(ORIGINAL_PDF_URL)` bleibt als Wächter für den
 * Smoke-Test bestehen (D-07).
 */
export const ORIGINAL_PDF_URL =
  'https://www.ostbevern.de/_Resources/Persistent/3/2/6/0/3260f0ed6ed16745ad93c953c061f765866667a6/Haushalt%202026%20komplett.pdf'

/**
 * Name der verantwortlichen Person im Impressum (D-08).
 *
 * Bis der Text-Checkpoint (07-10, D-15) den echten Namen setzt, steht hier ein Platzhalter
 * auf `.invalid`. `istImpressumPlatzhalter` erkennt ihn, damit ein unfertiges Impressum nie
 * deployt wird.
 */
export const IMPRESSUM_NAME = 'name-noch-nicht-festgelegt.invalid'

/**
 * Anschrift im Impressum als Zeilenliste, eine Zeile je Eintrag (1 bis n Zeilen, D-08).
 *
 * Bis der Text-Checkpoint (07-10, D-15) die echte Anschrift setzt, steht hier ein Platzhalter
 * auf `.invalid`. `istAnschriftPlatzhalter` erkennt ihn, auch bei einer halb gefüllten Anschrift.
 */
export const IMPRESSUM_ANSCHRIFT: readonly string[] = ['anschrift-noch-nicht-festgelegt.invalid']

function istInvalidHost(host: string): boolean {
  const klein = host.toLowerCase()
  return klein === 'invalid' || klein.endsWith('.invalid')
}

/**
 * Ob eine Adresse (E-Mail) oder URL ein Platzhalter ist: ihr Host (URL) bzw. der
 * Domainteil (E-Mail) liegt auf `.invalid`. Leere oder unlesbare Werte gelten
 * ebenfalls als Platzhalter, damit nie ein unbrauchbarer Wert als echt durchgeht.
 * Phase 7 weist das Deployment ab, solange diese Funktion für eine der beiden
 * Konstanten `true` liefert (D-17).
 */
export function istPlatzhalter(wert: string): boolean {
  const text = wert.trim()
  if (text === '') {
    return true
  }
  if (text.includes('@')) {
    return istInvalidHost(text.slice(text.lastIndexOf('@') + 1))
  }
  try {
    return istInvalidHost(new URL(text).hostname)
  } catch {
    return true
  }
}

/**
 * Ob ein Impressumsfeld ein Platzhalter ist: leerer oder nur aus Leerraum bestehender Text
 * oder ein Text, der `.invalid` enthält (ohne Beachtung der Groß- und Kleinschreibung).
 */
export function istImpressumPlatzhalter(wert: string): boolean {
  const text = wert.trim()
  return text === '' || text.toLowerCase().includes('.invalid')
}

/**
 * Ob die Impressumsanschrift ein Platzhalter ist: eine leere Liste oder mindestens eine
 * Zeile, die ein Platzhalter ist. So gilt auch eine halb gefüllte Anschrift als unfertig.
 */
export function istAnschriftPlatzhalter(zeilen: readonly string[]): boolean {
  return zeilen.length === 0 || zeilen.some(istImpressumPlatzhalter)
}
