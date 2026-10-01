import { onScopeDispose, readonly, ref, type Ref } from 'vue'

/** Breite in Pixeln, bis zu der der Bildschirm als "schmal" gilt. 360px bleibt die kleinste unterstützte Breite (A11Y-03). */
export const SCHMAL_BIS = 699

/**
 * Reaktives Flag für schmale Bildschirme (<= SCHMAL_BIS px). Liefert in
 * Umgebungen ohne `window` (SSR/Tests) einen schreibgeschützten Ref mit
 * Startwert `false`.
 */
export function useSchmalerBildschirm(): Readonly<Ref<boolean>> {
  if (typeof window === 'undefined') {
    return readonly(ref(false))
  }

  const medienAbfrage = window.matchMedia(`(max-width: ${SCHMAL_BIS}px)`)
  const istSchmal = ref(medienAbfrage.matches)

  function aktualisieren(ereignis: MediaQueryListEvent) {
    istSchmal.value = ereignis.matches
  }

  medienAbfrage.addEventListener('change', aktualisieren)

  onScopeDispose(() => {
    medienAbfrage.removeEventListener('change', aktualisieren)
  })

  return readonly(istSchmal)
}
