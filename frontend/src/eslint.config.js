import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'
import eslintConfigPrettier from 'eslint-config-prettier'
import globals from 'globals'

export default tseslint.config(
  { ignores: ['dist/**', 'node_modules/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        __APP_VERSION__: 'readonly',
        __RT_VERSION__: 'readonly',
      },
    },
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      // renderRichText() escapes raw text then reintroduces a fixed tag allowlist —
      // not a free-form injection vector like typical v-html usage.
      'vue/no-v-html': 'off',
      // This codebase consistently uses camelCase for custom component props/events,
      // matching the TS defineProps/defineEmits keys used in <script setup> — not a
      // native-HTML-attribute convention issue, so the kebab-case rules don't apply.
      'vue/attribute-hyphenation': 'off',
      'vue/v-on-event-hyphenation': 'off',
      'vue/prop-name-casing': 'off',
    },
  },
  eslintConfigPrettier,
)
