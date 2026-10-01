import '@awesome.me/webawesome/dist/styles/webawesome.css'
import '@awesome.me/webawesome/dist/styles/color/variants/brand.css'
import '@awesome.me/webawesome/dist/translations/de.js'
import { setIconPath } from '@awesome.me/webawesome'

// Self-hosted icons: no third-party CDN request (UI-SPEC Icon library decision, T-01-06).
setIconPath(`${import.meta.env.BASE_URL}icons`)
