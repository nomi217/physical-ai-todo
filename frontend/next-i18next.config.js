/**
 * next-i18next configuration
 *
 * Multi-language support for 6 languages with RTL support
 */

module.exports = {
  i18n: {
    // Default language (English)
    defaultLocale: 'en',

    // All supported locales
    locales: ['en', 'ur', 'ar', 'es', 'fr', 'de'],

    // Locale detection settings
    localeDetection: true,

    // RTL languages (Arabic and Urdu)
    // These languages will render right-to-left
    rtl: ['ar', 'ur'],
  },

  // Namespace configuration
  ns: ['common'],
  defaultNS: 'common',

  // Load all namespaces for all languages
  fallbackLng: 'en',

  // React configuration
  react: {
    useSuspense: false,
  },

  // Load path for translation files
  // Translations are in public/locales/{locale}/{namespace}.json
  localePath: './public/locales',

  // Reload translations in development
  reloadOnPrerender: process.env.NODE_ENV === 'development',
}
