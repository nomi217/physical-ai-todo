# 3D Effects & Animations Skill

## Purpose
Create 3D transforms, parallax scrolling, and smooth animations using framer-motion and CSS for Next.js applications.

## When to Use
- Creating interactive 3D cards
- Implementing parallax scrolling
- Building engaging landing pages
- Adding depth and perspective to UI elements

## Inputs Required
- **Component Name**: Name of the 3D component
- **Effect Type**: Hover, scroll, or continuous animation
- **Intensity**: Strength of the 3D effect (0-1)

## Process

### 1. Install Dependencies
```bash
npm install framer-motion@^10.16.16
npm install react-intersection-observer@^9.5.3
```

### 2. 3D Card with Mouse Tracking
```tsx
'use client'
import { motion } from 'framer-motion'
import { useState, useRef } from 'react'

interface Card3DProps {
  children: React.ReactNode
  intensity?: number
  className?: string
}

export default function Card3D({
  children,
  intensity = 1,
  className = ''
}: Card3DProps) {
  const [rotateX, setRotateX] = useState(0)
  const [rotateY, setRotateY] = useState(0)
  const cardRef = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return

    const rect = cardRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    const mouseX = e.clientX - centerX
    const mouseY = e.clientY - centerY

    const rotateXValue = (mouseY / (rect.height / 2)) * -15 * intensity
    const rotateYValue = (mouseX / (rect.width / 2)) * 15 * intensity

    setRotateX(rotateXValue)
    setRotateY(rotateYValue)
  }

  const handleMouseLeave = () => {
    setRotateX(0)
    setRotateY(0)
  }

  return (
    <motion.div
      ref={cardRef}
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
        transformStyle: 'preserve-3d',
        perspective: '1000px',
      }}
      className={className}
    >
      <motion.div
        whileHover={{ scale: 1.05, translateZ: 20 }}
        style={{
          transformStyle: 'preserve-3d',
        }}
        className="relative"
      >
        {children}
      </motion.div>
    </motion.div>
  )
}
```

### 3. Parallax Scroll Effect
```tsx
'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

interface ParallaxProps {
  children: React.ReactNode
  speed?: number
  direction?: 'up' | 'down' | 'left' | 'right'
}

export default function Parallax({
  children,
  speed = 0.5,
  direction = 'up'
}: ParallaxProps) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start']
  })

  const transforms = {
    up: useTransform(scrollYProgress, [0, 1], ['0%', `${-100 * speed}%`]),
    down: useTransform(scrollYProgress, [0, 1], ['0%', `${100 * speed}%`]),
    left: useTransform(scrollYProgress, [0, 1], ['0%', `${-100 * speed}%`]),
    right: useTransform(scrollYProgress, [0, 1], ['0%', `${100 * speed}%`]),
  }

  const styleMap = {
    up: { y: transforms.up },
    down: { y: transforms.down },
    left: { x: transforms.left },
    right: { x: transforms.right },
  }

  return (
    <div ref={ref} className="overflow-hidden">
      <motion.div style={styleMap[direction]}>
        {children}
      </motion.div>
    </div>
  )
}
```

### 4. Rotating 3D Logo
```tsx
'use client'
import { motion, useMotionValue, useSpring } from 'framer-motion'
import { useEffect } from 'react'

interface Logo3DProps {
  size?: number
  children: React.ReactNode
}

export default function Logo3D({ size = 128, children }: Logo3DProps) {
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  const rotateX = useSpring(mouseY, { stiffness: 50, damping: 15 })
  const rotateY = useSpring(mouseX, { stiffness: 50, damping: 15 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 30
      const y = (e.clientY / window.innerHeight - 0.5) * 30

      mouseX.set(x)
      mouseY.set(-y)
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [mouseX, mouseY])

  return (
    <motion.div
      style={{
        width: size,
        height: size,
        rotateX,
        rotateY,
        perspective: '1000px',
        transformStyle: 'preserve-3d',
      }}
    >
      <motion.div
        animate={{
          rotateY: 360,
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          transformStyle: 'preserve-3d',
        }}
        className="w-full h-full"
      >
        {children}
      </motion.div>
    </motion.div>
  )
}
```

### 5. Floating Animation
```tsx
'use client'
import { motion } from 'framer-motion'

interface FloatingProps {
  children: React.ReactNode
  delay?: number
  duration?: number
  distance?: number
}

export default function Floating({
  children,
  delay = 0,
  duration = 3,
  distance = 20
}: FloatingProps) {
  return (
    <motion.div
      animate={{
        y: [-distance, distance, -distance],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: 'easeInOut',
        delay,
      }}
      style={{
        willChange: 'transform',
      }}
    >
      {children}
    </motion.div>
  )
}
```

### 6. Scroll-Triggered Fade In
```tsx
'use client'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

interface FadeInProps {
  children: React.ReactNode
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right'
  distance?: number
}

export default function FadeIn({
  children,
  delay = 0,
  direction = 'up',
  distance = 50
}: FadeInProps) {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  const directionOffset = {
    up: { x: 0, y: distance },
    down: { x: 0, y: -distance },
    left: { x: distance, y: 0 },
    right: { x: -distance, y: 0 },
  }

  return (
    <motion.div
      ref={ref}
      initial={{
        opacity: 0,
        ...directionOffset[direction],
      }}
      animate={
        inView
          ? {
              opacity: 1,
              x: 0,
              y: 0,
            }
          : {}
      }
      transition={{
        duration: 0.6,
        delay,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
    >
      {children}
    </motion.div>
  )
}
```

### 7. Stagger Children Animation
```tsx
'use client'
import { motion } from 'framer-motion'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
}

interface StaggerProps {
  children: React.ReactNode[]
  className?: string
}

export default function StaggerContainer({ children, className }: StaggerProps) {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className={className}
    >
      {children.map((child, index) => (
        <motion.div key={index} variants={item}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}
```

### 8. Tilt Card Effect
```tsx
'use client'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useRef } from 'react'

interface TiltCardProps {
  children: React.ReactNode
  intensity?: number
}

export default function TiltCard({ children, intensity = 10 }: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null)

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const mouseXSpring = useSpring(x)
  const mouseYSpring = useSpring(y)

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], [intensity, -intensity])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], [-intensity, intensity])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return

    const rect = ref.current.getBoundingClientRect()

    const width = rect.width
    const height = rect.height

    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top

    const xPct = mouseX / width - 0.5
    const yPct = mouseY / height - 0.5

    x.set(xPct)
    y.set(yPct)
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
      }}
      className="relative"
    >
      {children}
    </motion.div>
  )
}
```

### 9. CSS for GPU Acceleration
```css
/* Add to global.css or component styles */

/* Force GPU rendering */
.gpu-accelerated {
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

/* Perspective container */
.perspective-container {
  perspective: 1000px;
  transform-style: preserve-3d;
}

/* 3D card base */
.card-3d {
  transform-style: preserve-3d;
  transition: transform 0.3s ease-out;
}

.card-3d:hover {
  transform: rotateY(5deg) rotateX(5deg) translateZ(20px);
}

/* Smooth animations */
.smooth-animation {
  transition: all 0.3s cubic-bezier(0.21, 0.47, 0.32, 0.98);
}
```

### 10. Performance Optimization Wrapper
```tsx
'use client'
import { motion, useReducedMotion } from 'framer-motion'

interface AnimationWrapperProps {
  children: React.ReactNode
  animation: any
}

export default function AnimationWrapper({
  children,
  animation
}: AnimationWrapperProps) {
  const shouldReduceMotion = useReducedMotion()

  if (shouldReduceMotion) {
    return <>{children}</>
  }

  return (
    <motion.div {...animation}>
      {children}
    </motion.div>
  )
}
```

## Best Practices

### Performance
- Use `will-change: transform` for animated elements
- Prefer `transform` and `opacity` (GPU-accelerated)
- Limit simultaneous animations
- Use `useReducedMotion` for accessibility
- Test on low-end devices

### User Experience
- Keep animations subtle (200-600ms duration)
- Use easing functions for natural feel
- Provide visual feedback for interactions
- Don't animate on page load (wait for user interaction)
- Respect prefers-reduced-motion

### Code Quality
- Extract reusable animation components
- Use variants for complex animations
- Implement loading states
- Add error boundaries
- Type props with TypeScript

## Common Patterns

### Page Transition
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
>
  {children}
</motion.div>
```

### Button Press Effect
```tsx
<motion.button
  whileTap={{ scale: 0.95 }}
  whileHover={{ scale: 1.05 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>
  Click Me
</motion.button>
```

### Modal Animation
```tsx
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.2 }}
    >
      Modal Content
    </motion.div>
  )}
</AnimatePresence>
```

## Output
- High-performance 3D components
- Smooth 60fps animations
- Accessible motion design
- Reusable animation primitives
- GPU-accelerated effects
