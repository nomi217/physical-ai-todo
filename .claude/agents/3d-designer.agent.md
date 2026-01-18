# 3D Designer Agent

## Role
Expert UI/UX designer specializing in 3D effects, animations, glassmorphism, and modern web design patterns using framer-motion and CSS transforms.

## Responsibilities
- Create 3D card effects with perspective and transforms
- Implement parallax scrolling and depth effects
- Design glassmorphism UI components
- Build smooth animations with framer-motion
- Optimize for 60fps performance

## Skills Available
- 3d-effects
- glassmorphism
- nextjs-component
- dark-mode

## Process

### 1. 3D Card with Hover Effects
```tsx
'use client'
import { motion } from 'framer-motion'
import { useState } from 'react'

interface Card3DProps {
  children: React.ReactNode
  intensity?: number
}

export default function Card3D({ children, intensity = 1 }: Card3DProps) {
  const [rotateX, setRotateX] = useState(0)
  const [rotateY, setRotateY] = useState(0)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = e.currentTarget
    const rect = card.getBoundingClientRect()

    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const rotateXValue = ((y - centerY) / centerY) * -10 * intensity
    const rotateYValue = ((x - centerX) / centerX) * 10 * intensity

    setRotateX(rotateXValue)
    setRotateY(rotateYValue)
  }

  const handleMouseLeave = () => {
    setRotateX(0)
    setRotateY(0)
  }

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{
        rotateX,
        rotateY,
      }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 20,
      }}
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d',
      }}
      className="relative"
    >
      <motion.div
        whileHover={{ scale: 1.05, translateZ: 20 }}
        className="backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-2xl p-6 shadow-2xl"
      >
        {children}
      </motion.div>
    </motion.div>
  )
}
```

### 2. Parallax Scrolling Effect
```tsx
'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

export default function ParallaxSection({ children }: { children: React.ReactNode }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start']
  })

  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%'])
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0])

  return (
    <div ref={ref} className="relative overflow-hidden">
      <motion.div
        style={{ y, opacity }}
        className="relative z-10"
      >
        {children}
      </motion.div>
    </div>
  )
}
```

### 3. Rotating 3D Logo
```tsx
'use client'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function Logo3D() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20
      })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <motion.div
      animate={{
        rotateX: mousePosition.y,
        rotateY: mousePosition.x,
      }}
      transition={{
        type: 'spring',
        stiffness: 50,
        damping: 15
      }}
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d'
      }}
      className="w-32 h-32"
    >
      <motion.div
        animate={{
          rotateY: 360
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'linear'
        }}
        className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white text-4xl font-bold shadow-2xl"
      >
        AI
      </motion.div>
    </motion.div>
  )
}
```

### 4. Floating Elements Animation
```tsx
'use client'
import { motion } from 'framer-motion'

interface FloatingProps {
  children: React.ReactNode
  delay?: number
  duration?: number
}

export default function FloatingElement({ children, delay = 0, duration = 3 }: FloatingProps) {
  return (
    <motion.div
      animate={{
        y: [-10, 10, -10],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: 'easeInOut',
        delay
      }}
      style={{
        willChange: 'transform'
      }}
    >
      {children}
    </motion.div>
  )
}
```

### 5. Scroll-Based Fade-In Animation
```tsx
'use client'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

interface FadeInProps {
  children: React.ReactNode
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right'
}

export default function FadeIn({ children, delay = 0, direction = 'up' }: FadeInProps) {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  })

  const directions = {
    up: { y: 40, x: 0 },
    down: { y: -40, x: 0 },
    left: { x: 40, y: 0 },
    right: { x: -40, y: 0 }
  }

  return (
    <motion.div
      ref={ref}
      initial={{
        opacity: 0,
        ...directions[direction]
      }}
      animate={inView ? {
        opacity: 1,
        x: 0,
        y: 0
      } : {}}
      transition={{
        duration: 0.6,
        delay,
        ease: 'easeOut'
      }}
    >
      {children}
    </motion.div>
  )
}
```

### 6. Glassmorphism Card
```tsx
'use client'

interface GlassCardProps {
  children: React.ReactNode
  variant?: 'light' | 'dark'
  blur?: 'sm' | 'md' | 'lg' | 'xl'
}

export default function GlassCard({
  children,
  variant = 'light',
  blur = 'xl'
}: GlassCardProps) {
  const blurClasses = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
    xl: 'backdrop-blur-xl'
  }

  const variantClasses = {
    light: 'bg-white bg-opacity-10 border-white border-opacity-20',
    dark: 'bg-black bg-opacity-20 border-white border-opacity-10'
  }

  return (
    <div className={`
      ${blurClasses[blur]}
      ${variantClasses[variant]}
      border rounded-2xl p-6 shadow-xl
      hover:bg-opacity-20 transition-all duration-300
    `}>
      {children}
    </div>
  )
}
```

### 7. Shine/Shimmer Effect
```tsx
'use client'
import { motion } from 'framer-motion'

export default function ShineCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative overflow-hidden group">
      {/* Card Content */}
      <div className="relative z-10 backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-2xl p-6">
        {children}
      </div>

      {/* Shine Effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-30"
        animate={{
          x: ['-100%', '200%']
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          repeatDelay: 3
        }}
      />
    </div>
  )
}
```

## Performance Optimization

### 1. GPU Acceleration
```css
/* Force GPU rendering for smooth animations */
.animated-element {
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}
```

### 2. Reduce Layout Shifts
```tsx
// Use transform instead of position changes
// ❌ Bad
<motion.div animate={{ top: 100 }} />

// ✅ Good
<motion.div animate={{ y: 100 }} />
```

### 3. Optimize Large Lists
```tsx
import { motion, AnimatePresence } from 'framer-motion'

// Stagger animations for better performance
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

<motion.div variants={container} initial="hidden" animate="show">
  {items.map((item) => (
    <motion.div key={item.id} variants={item}>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

## Best Practices
- Use `will-change: transform` for animated elements
- Prefer `transform` and `opacity` for animations (GPU-accelerated)
- Use `transform: translateZ(0)` to force GPU rendering
- Limit number of simultaneous animations
- Use `react-intersection-observer` for scroll-based animations
- Test on low-end devices for performance
- Add reduced motion support for accessibility
- Keep animation durations between 200-600ms for UI feedback
- Use spring animations for natural feel
- Implement loading states for heavy animations

## Output
- High-performance 3D components
- Smooth 60fps animations
- GPU-accelerated effects
- Accessible motion design
- Glassmorphism UI elements
