'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type Locale = 'en' | 'ur' | 'ar' | 'es' | 'fr' | 'de'

interface I18nContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string) => string
  dir: 'ltr' | 'rtl'
}

const I18nContext = createContext<I18nContextType>({} as I18nContextType)

const RTL_LANGUAGES = ['ar', 'ur']

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('en')
  const [translations, setTranslations] = useState<Record<string, any>>({})

  // Load translations when locale changes
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const response = await fetch(`/locales/${locale}/common.json`)
        const data = await response.json()
        setTranslations(data)
      } catch (error) {
        console.error(`Failed to load translations for ${locale}:`, error)
        // Fallback to English
        if (locale !== 'en') {
          const fallbackResponse = await fetch('/locales/en/common.json')
          const fallbackData = await fallbackResponse.json()
          setTranslations(fallbackData)
        }
      }
    }

    loadTranslations()
  }, [locale])

  // Load initial locale from cookie or browser
  useEffect(() => {
    const cookieLocale = document.cookie
      .split('; ')
      .find(row => row.startsWith('NEXT_LOCALE='))
      ?.split('=')[1] as Locale

    const browserLocale = navigator.language.split('-')[0] as Locale
    const supportedLocales: Locale[] = ['en', 'ur', 'ar', 'es', 'fr', 'de']

    const initialLocale = cookieLocale ||
      (supportedLocales.includes(browserLocale) ? browserLocale : 'en')

    setLocaleState(initialLocale)
  }, [])

  // Update HTML dir attribute for RTL
  useEffect(() => {
    const dir = RTL_LANGUAGES.includes(locale) ? 'rtl' : 'ltr'
    document.documentElement.dir = dir
    document.documentElement.lang = locale
  }, [locale])

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale)
    // Save to cookie
    document.cookie = `NEXT_LOCALE=${newLocale};path=/;max-age=31536000`
  }

  // Translation function with nested key support
  const t = (key: string): string => {
    const keys = key.split('.')
    let value: any = translations

    for (const k of keys) {
      value = value?.[k]
      if (value === undefined) break
    }

    return value || key
  }

  const dir = RTL_LANGUAGES.includes(locale) ? 'rtl' : 'ltr'

  return (
    <I18nContext.Provider value={{ locale, setLocale, t, dir }}>
      {children}
    </I18nContext.Provider>
  )
}

export const useI18n = () => {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider')
  }
  return context
}
