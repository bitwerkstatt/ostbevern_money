import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import skipFormatting from 'eslint-config-prettier/flat'

// To allow more languages other than `ts` in `.vue` files, uncomment the following lines:
// import { configureVueProject } from '@vue/eslint-config-typescript'
// configureVueProject({ scriptLangs: ['ts', 'tsx'] })
// More info at https://github.com/vuejs/eslint-config-typescript/#advanced-setup

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,ts,mts,tsx}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  ...pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,

  {
    name: 'app/wa-page-native-slots',
    rules: {
      // wa-page and wa-callout are native custom elements (Web Awesome); they use
      // the native HTML `slot` attribute for light-DOM slotting, not Vue's
      // v-slot/#name syntax, which only applies to Vue SFC components. Not a Vue 2
      // deprecation here.
      'vue/no-deprecated-slot-attribute': ['error', { ignoreParents: ['wa-page', 'wa-callout'] }],
    },
  },

  skipFormatting,
)
