'use client'

import { useTheme } from 'next-themes'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  const isDark = theme === 'dark'
  const toggleTheme = () => setTheme(isDark ? 'light' : 'dark')

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-16 h-8 rounded-full p-1 transition-colors duration-300 bg-gradient-to-r from-blue-500 to-purple-600 dark:from-gray-700 dark:to-gray-600 shadow-lg"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      {/* Sliding circle */}
      <motion.div
        className="w-6 h-6 rounded-full bg-white shadow-md flex items-center justify-center"
        animate={{
          x: isDark ? 32 : 0,
        }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      >
        <span className="text-xs">
          {isDark ? '🌙' : '☀️'}
        </span>
      </motion.div>
    </motion.button>
  )
}
