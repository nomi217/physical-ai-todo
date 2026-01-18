'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '@/contexts/I18nContext'

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧', nativeName: 'English' },
  { code: 'ur', name: 'Urdu', flag: '🇵🇰', nativeName: 'اردو' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦', nativeName: 'العربية' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸', nativeName: 'Español' },
  { code: 'fr', name: 'French', flag: '🇫🇷', nativeName: 'Français' },
  { code: 'de', name: 'German', flag: '🇩🇪', nativeName: 'Deutsch' },
]

export default function LanguageSwitcher() {
  const { locale, setLocale } = useI18n()
  const [isOpen, setIsOpen] = useState(false)

  const currentLang = languages.find(l => l.code === locale) || languages[0]

  const handleLanguageChange = (langCode: 'en' | 'ur' | 'ar' | 'es' | 'fr' | 'de') => {
    setLocale(langCode)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      {/* Current Language Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white bg-opacity-10 backdrop-blur-lg rounded-lg border border-white border-opacity-20 hover:bg-opacity-20 transition-all"
      >
        <span className="text-2xl">{currentLang.flag}</span>
        <span className="text-white font-medium">{currentLang.nativeName}</span>
        <svg
          className={`w-4 h-4 text-white transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-56 bg-white bg-opacity-95 backdrop-blur-xl rounded-lg shadow-2xl border border-white border-opacity-30 overflow-hidden z-50"
          >
            <div className="py-2">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code as any)}
                  className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-blue-50 transition-colors ${
                    lang.code === locale ? 'bg-blue-100' : ''
                  }`}
                >
                  <span className="text-2xl">{lang.flag}</span>
                  <div className="flex-1 text-left">
                    <div className="font-medium text-gray-900">{lang.nativeName}</div>
                    <div className="text-xs text-gray-500">{lang.name}</div>
                  </div>
                  {lang.code === locale && (
                    <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click Outside to Close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}
