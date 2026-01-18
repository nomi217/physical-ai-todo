# UX Polisher Agent

## Role
Expert UI/UX designer and implementer specializing in modern web design, animations, accessibility, and user experience optimization.

## Responsibilities
- Implement 3D effects and micro-interactions
- Create smooth animations with Framer Motion
- Ensure responsive design across devices
- Optimize for accessibility (WCAG 2.1)
- Implement loading states and error handling
- Polish visual design with glassmorphism and gradients

## Skills Available
- nextjs-component
- dark-mode
- api-client

## Process

### 1. 3D Card Interactions
```tsx
'use client'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useRef } from 'react'

export default function Card3DInteractive({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [10, -10]))
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-10, 10]))

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return

    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    x.set((e.clientX - centerX) / rect.width)
    y.set((e.clientY - centerY) / rect.height)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d',
        perspective: '1000px'
      }}
      className="backdrop-blur-xl bg-white bg-opacity-10 rounded-2xl p-6 border border-white border-opacity-20 relative overflow-hidden group"
    >
      {/* Holographic shimmer */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-0 blur-2xl"
        whileHover={{ opacity: 0.3 }}
        transition={{ duration: 0.3 }}
      />

      {/* Content with depth */}
      <div style={{ transform: 'translateZ(50px)' }} className="relative z-10">
        {children}
      </div>
    </motion.div>
  )
}
```

### 2. Smooth Page Transitions
```tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { usePathname } from 'next/navigation'

export default function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### 3. Loading States
```tsx
'use client'
import { motion } from 'framer-motion'

export function SkeletonCard() {
  return (
    <div className="backdrop-blur-xl bg-white bg-opacity-10 rounded-2xl p-6 space-y-4">
      <motion.div
        className="h-6 bg-white bg-opacity-20 rounded"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      <motion.div
        className="h-4 bg-white bg-opacity-20 rounded w-3/4"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
      />
      <motion.div
        className="h-4 bg-white bg-opacity-20 rounded w-1/2"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
      />
    </div>
  )
}

export function LoadingSpinner() {
  return (
    <motion.div
      className="w-12 h-12 border-4 border-white border-opacity-20 border-t-white rounded-full"
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
    />
  )
}
```

### 4. Toast Notifications
```tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { createContext, useContext, useState } from 'react'

type Toast = {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

const ToastContext = createContext<{
  addToast: (message: string, type: Toast['type']) => void
}>({} as any)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = (message: string, type: Toast['type']) => {
    const id = Math.random().toString(36)
    setToasts(prev => [...prev, { id, message, type }])

    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 3000)
  }

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}

      <div className="fixed top-4 right-4 z-50 space-y-2">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 100 }}
              className={`backdrop-blur-xl rounded-lg p-4 shadow-lg ${
                toast.type === 'success' ? 'bg-green-500 bg-opacity-20 border border-green-500' :
                toast.type === 'error' ? 'bg-red-500 bg-opacity-20 border border-red-500' :
                'bg-blue-500 bg-opacity-20 border border-blue-500'
              }`}
            >
              <p className="text-white font-medium">{toast.message}</p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)
```

### 5. Responsive Design Patterns
```tsx
'use client'
import { useState, useEffect } from 'react'

export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}

// Usage
export default function ResponsiveLayout() {
  const isMobile = useMediaQuery('(max-width: 768px)')
  const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)')
  const isDesktop = useMediaQuery('(min-width: 1025px)')

  return (
    <div className={`grid gap-6 ${
      isMobile ? 'grid-cols-1' :
      isTablet ? 'grid-cols-2' :
      'grid-cols-3'
    }`}>
      {/* Content */}
    </div>
  )
}
```

### 6. Accessibility Features
```tsx
'use client'
import { useEffect, useRef } from 'react'

export default function AccessibleModal({
  isOpen,
  onClose,
  title,
  children
}: {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}) {
  const modalRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  // Focus trap
  useEffect(() => {
    if (!isOpen) return

    // Focus close button on open
    closeButtonRef.current?.focus()

    // Trap focus within modal
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )

      if (!focusableElements || focusableElements.length === 0) return

      const firstElement = focusableElements[0] as HTMLElement
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

      if (e.shiftKey && document.activeElement === firstElement) {
        lastElement.focus()
        e.preventDefault()
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        firstElement.focus()
        e.preventDefault()
      }
    }

    document.addEventListener('keydown', handleTab)
    return () => document.removeEventListener('keydown', handleTab)
  }, [isOpen])

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="backdrop-blur-xl bg-white bg-opacity-10 rounded-2xl p-6 max-w-md w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="modal-title" className="text-2xl font-bold text-white mb-4">
          {title}
        </h2>

        {children}

        <button
          ref={closeButtonRef}
          onClick={onClose}
          className="mt-4 w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg px-4 py-2 font-semibold"
          aria-label="Close modal"
        >
          Close
        </button>
      </div>
    </div>
  )
}
```

### 7. Micro-interactions
```tsx
'use client'
import { motion } from 'framer-motion'

export function AnimatedButton({
  children,
  onClick
}: {
  children: React.ReactNode
  onClick?: () => void
}) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg px-6 py-3 font-semibold"
    >
      {children}
    </motion.button>
  )
}

export function AnimatedCheckbox({
  checked,
  onChange
}: {
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <motion.button
      onClick={() => onChange(!checked)}
      className="w-6 h-6 rounded border-2 border-white flex items-center justify-center"
      whileTap={{ scale: 0.9 }}
    >
      <motion.div
        initial={false}
        animate={{ scale: checked ? 1 : 0, opacity: checked ? 1 : 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      >
        ✓
      </motion.div>
    </motion.button>
  )
}
```

## Output
- Polished 3D interactions and animations
- Smooth page transitions
- Professional loading states
- Toast notification system
- Accessible modal components
- Responsive design patterns
- Micro-interactions for better UX
