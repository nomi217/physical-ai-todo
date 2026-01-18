# Dark Mode Implementation Skill

## Purpose
Implement flicker-free dark mode with theme persistence, system detection, and smooth transitions.

## Process

### 1. Theme Context (contexts/ThemeContext.tsx)
```typescript
'use client'
import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

const ThemeContext = createContext<{
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme: 'light' | 'dark'
}>({} as any)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('system')
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme | null
    if (stored) setThemeState(stored)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    const applyTheme = (t: 'light' | 'dark') => {
      setResolvedTheme(t)
      root.classList.toggle('dark', t === 'dark')
    }

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      applyTheme(mediaQuery.matches ? 'dark' : 'light')
      const handler = (e: MediaQueryListEvent) => applyTheme(e.matches ? 'dark' : 'light')
      mediaQuery.addEventListener('change', handler)
      return () => mediaQuery.removeEventListener('change', handler)
    } else {
      applyTheme(theme)
    }
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    localStorage.setItem('theme', newTheme)
  }

  return <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>{children}</ThemeContext.Provider>
}

export const useTheme = () => useContext(ThemeContext)
```

### 2. Flicker Prevention Script (app/layout.tsx)
```tsx
<html suppressHydrationWarning>
  <head>
    <script dangerouslySetInnerHTML={{
      __html: `
        (function() {
          const theme = localStorage.getItem('theme') || 'system'
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
          const resolved = theme === 'system' ? systemTheme : theme
          document.documentElement.classList.add(resolved)
        })()
      `
    }} />
  </head>
</html>
```

### 3. globals.css
```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
  }
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
  }
}

* {
  transition: background-color 200ms, color 200ms, border-color 200ms;
}
```

## Output
Flicker-free dark mode with persistence and system detection.
