import { onScopeDispose, readonly, ref, type Ref } from 'vue'
import type { EChartsOption } from 'echarts'

/**
 * Reaktives Flag für `prefers-reduced-motion: reduce`. Liefert in Umgebungen
 * ohne `window` (SSR/Tests) einen schreibgeschützten Ref mit Startwert `false`.
 */
export function useReducedMotion(): Readonly<Ref<boolean>> {
  if (typeof window === 'undefined') {
    return readonly(ref(false))
  }

  const medienAbfrage = window.matchMedia('(prefers-reduced-motion: reduce)')
  const reduziert = ref(medienAbfrage.matches)

  function aktualisieren(ereignis: MediaQueryListEvent) {
    reduziert.value = ereignis.matches
  }

  medienAbfrage.addEventListener('change', aktualisieren)

  onScopeDispose(() => {
    medienAbfrage.removeEventListener('change', aktualisieren)
  })

  return readonly(reduziert)
}

/**
 * Bei reduzierter Bewegung eine Kopie der Option mit `animation: false`
 * (UI-SPEC Chart Contract „Bewegung“); sonst die Option selbst. Das übergebene
 * Objekt wird nie verändert.
 */
export function ohneAnimation(option: EChartsOption, reduziert: boolean): EChartsOption {
  return reduziert ? { ...option, animation: false } : option
}
