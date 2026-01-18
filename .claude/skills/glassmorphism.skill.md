# Glassmorphism UI Design Skill

## Purpose
Create modern glassmorphism (frosted glass) UI components with backdrop blur, transparency, and depth effects for Next.js applications.

## When to Use
- Creating modern, premium UI designs
- Building cards, modals, and overlays
- Adding depth and hierarchy to interfaces
- Implementing trendy design patterns

## Inputs Required
- **Component Type**: Card, modal, navbar, etc.
- **Variant**: Light or dark mode
- **Blur Intensity**: sm, md, lg, xl
- **Background Opacity**: 0-1

## Process

### 1. Configure Tailwind CSS
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      backdropBlur: {
        xs: '2px',
      }
    }
  },
  plugins: [],
}
```

### 2. Glass Card Component
```tsx
'use client'
import { ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  variant?: 'light' | 'dark'
  blur?: 'sm' | 'md' | 'lg' | 'xl'
  intensity?: 'subtle' | 'medium' | 'strong'
  className?: string
}

export default function GlassCard({
  children,
  variant = 'light',
  blur = 'xl',
  intensity = 'medium',
  className = ''
}: GlassCardProps) {
  const blurClasses = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
    xl: 'backdrop-blur-xl'
  }

  const intensityClasses = {
    light: {
      subtle: 'bg-white/5 border-white/10',
      medium: 'bg-white/10 border-white/20',
      strong: 'bg-white/20 border-white/30'
    },
    dark: {
      subtle: 'bg-black/5 border-white/5',
      medium: 'bg-black/10 border-white/10',
      strong: 'bg-black/20 border-white/15'
    }
  }

  return (
    <div
      className={`
        ${blurClasses[blur]}
        ${intensityClasses[variant][intensity]}
        border rounded-2xl p-6 shadow-xl
        hover:bg-opacity-20 transition-all duration-300
        ${className}
      `}
    >
      {children}
    </div>
  )
}
```

### 3. Glass Modal
```tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { ReactNode } from 'react'

interface GlassModalProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  title?: string
}

export default function GlassModal({
  isOpen,
  onClose,
  children,
  title
}: GlassModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-md z-40"
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="
                backdrop-blur-2xl bg-white/10 border border-white/20
                rounded-3xl shadow-2xl max-w-2xl w-full p-8
                relative
              "
            >
              {/* Close button */}
              <button
                onClick={onClose}
                className="
                  absolute top-4 right-4
                  backdrop-blur-xl bg-white/10 border border-white/20
                  rounded-full p-2 hover:bg-white/20 transition-all
                "
              >
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>

              {/* Title */}
              {title && (
                <h2 className="text-3xl font-bold text-white mb-6">
                  {title}
                </h2>
              )}

              {/* Content */}
              <div className="text-gray-200">
                {children}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### 4. Glass Navbar
```tsx
'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function GlassNavbar() {
  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="
        fixed top-0 left-0 right-0 z-50
        backdrop-blur-2xl bg-white/5 border-b border-white/10
        shadow-lg
      "
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="text-white font-bold text-xl">
            Brand
          </Link>

          {/* Nav items */}
          <div className="flex gap-6">
            {['Features', 'Pricing', 'About'].map((item) => (
              <Link
                key={item}
                href={`/${item.toLowerCase()}`}
                className="
                  text-white/80 hover:text-white
                  transition-colors
                "
              >
                {item}
              </Link>
            ))}
          </div>

          {/* CTA */}
          <Link href="/signup">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="
                backdrop-blur-xl bg-white/10 border border-white/20
                px-6 py-2 rounded-xl text-white font-semibold
                hover:bg-white/20 transition-all
              "
            >
              Get Started
            </motion.button>
          </Link>
        </div>
      </div>
    </motion.nav>
  )
}
```

### 5. Glass Button
```tsx
'use client'
import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface GlassButtonProps {
  children: ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

export default function GlassButton({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false
}: GlassButtonProps) {
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  }

  const variantClasses = {
    primary: `
      backdrop-blur-xl bg-gradient-to-r from-blue-500/30 to-purple-500/30
      border-2 border-blue-400/50
      hover:from-blue-500/40 hover:to-purple-500/40
      hover:border-blue-400/70
    `,
    secondary: `
      backdrop-blur-xl bg-white/10 border border-white/20
      hover:bg-white/20
    `
  }

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        rounded-xl font-semibold text-white
        shadow-lg transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
      `}
    >
      {children}
    </motion.button>
  )
}
```

### 6. Glass Input Field
```tsx
'use client'

interface GlassInputProps {
  type?: string
  placeholder?: string
  value: string
  onChange: (value: string) => void
  icon?: React.ReactNode
}

export default function GlassInput({
  type = 'text',
  placeholder,
  value,
  onChange,
  icon
}: GlassInputProps) {
  return (
    <div className="relative">
      {icon && (
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/50">
          {icon}
        </div>
      )}

      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`
          w-full
          backdrop-blur-xl bg-white/10 border border-white/20
          rounded-xl px-4 py-3 text-white
          placeholder:text-white/50
          focus:bg-white/15 focus:border-white/30
          focus:outline-none focus:ring-2 focus:ring-white/20
          transition-all
          ${icon ? 'pl-12' : ''}
        `}
      />
    </div>
  )
}
```

### 7. Glass Notification Toast
```tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { useEffect } from 'react'

interface ToastProps {
  message: string
  type?: 'success' | 'error' | 'info'
  isVisible: boolean
  onClose: () => void
  duration?: number
}

export default function GlassToast({
  message,
  type = 'info',
  isVisible,
  onClose,
  duration = 3000
}: ToastProps) {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(onClose, duration)
      return () => clearTimeout(timer)
    }
  }, [isVisible, duration, onClose])

  const typeStyles = {
    success: 'border-green-400/50 bg-green-500/20',
    error: 'border-red-400/50 bg-red-500/20',
    info: 'border-blue-400/50 bg-blue-500/20'
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.8 }}
          className={`
            fixed top-4 right-4 z-50
            backdrop-blur-2xl border-2 ${typeStyles[type]}
            rounded-2xl px-6 py-4 shadow-2xl
            max-w-md
          `}
        >
          <div className="flex items-center gap-3">
            <span className="text-white font-semibold">{message}</span>

            <button
              onClick={onClose}
              className="text-white/70 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

### 8. CSS Utilities
```css
/* Add to globals.css */

/* Glassmorphism base classes */
.glass {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-dark {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Shine effect overlay */
.glass-shine {
  position: relative;
  overflow: hidden;
}

.glass-shine::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.glass-shine:hover::before {
  left: 100%;
}
```

## Best Practices

### Design
- Use on colorful or gradient backgrounds for best effect
- Ensure sufficient contrast for text readability
- Layer multiple glass elements for depth
- Combine with 3D effects for premium look
- Use subtle shadows and borders

### Performance
- Limit number of blur elements on screen
- Use `will-change: backdrop-filter` for animated elements
- Test on lower-end devices
- Consider fallbacks for unsupported browsers

### Accessibility
- Ensure text contrast meets WCAG standards
- Provide solid background fallback
- Test with screen readers
- Support keyboard navigation

## Browser Support
- Chrome/Edge: Full support
- Safari: Full support
- Firefox: Full support (with flag in older versions)
- Fallback: Solid semi-transparent background

## Output
- Modern glassmorphism components
- Accessible and performant
- Responsive design patterns
- Dark mode support
- Reusable UI primitives
