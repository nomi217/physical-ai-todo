# Next.js Component Generator Skill

## Purpose
Generate React/Next.js components with TypeScript, proper typing, and modern patterns (hooks, server components, client components).

## When to Use
- Creating new UI components
- Need consistent component structure
- Want TypeScript types and proper patterns

## Inputs Required
- **Component Name**: PascalCase name (e.g., "TaskCard", "SubtaskList")
- **Component Type**: "client" or "server"
- **Props**: Interface defining props
- **Purpose**: What the component does

## Process

### 1. Client Component Template
```tsx
'use client'

import { useState } from 'react'
import { ComponentProps } from '@/lib/types'

interface {ComponentName}Props {
  // Define props here
  title: string
  onAction?: () => void
}

export default function {ComponentName}({
  title,
  onAction
}: {ComponentName}Props) {
  const [state, setState] = useState(initialValue)

  const handleAction = () => {
    // Handle action
    onAction?.()
  }

  return (
    <div className="component-container">
      <h3>{title}</h3>
      {/* Component JSX */}
    </div>
  )
}
```

### 2. Server Component Template
```tsx
import { ComponentProps } from '@/lib/types'

interface {ComponentName}Props {
  // Define props here
  data: DataType
}

export default async function {ComponentName}({
  data
}: {ComponentName}Props) {
  // Can use async/await for data fetching

  return (
    <div className="component-container">
      {/* Component JSX */}
    </div>
  )
}
```

### 3. Component with Glassmorphism
```tsx
'use client'

export default function GlassCard({ children }) {
  return (
    <div className="backdrop-blur-lg bg-white bg-opacity-10 border border-white border-opacity-20 rounded-xl p-6 shadow-xl hover:bg-opacity-20 transition-all">
      {children}
    </div>
  )
}
```

### 4. Component with 3D Effects
```tsx
'use client'

import { motion } from 'framer-motion'

export default function Card3D({ children }) {
  return (
    <motion.div
      whileHover={{
        rotateX: 5,
        rotateY: 5,
        translateZ: 20,
      }}
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d',
      }}
      className="bg-white rounded-xl p-6 shadow-lg"
    >
      {children}
    </motion.div>
  )
}
```

### 5. Form Component with Validation
```tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  field: z.string().min(1, 'Required'),
})

type FormData = z.infer<typeof schema>

export default function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('field')} />
      {errors.field && <span>{errors.field.message}</span>}
      <button type="submit">Submit</button>
    </form>
  )
}
```

## Best Practices
- Use 'use client' for interactive components (useState, useEffect, event handlers)
- Keep server components for data fetching and static content
- Extract reusable logic into custom hooks
- Use TypeScript interfaces for props
- Add proper error boundaries
- Implement loading states
- Use semantic HTML
- Add ARIA labels for accessibility
- Memoize expensive computations with useMemo
- Use useCallback for functions passed as props

## Styling Patterns

### Dark Mode Support
```tsx
className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
```

### Responsive Design
```tsx
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
```

### Animations
```tsx
className="transition-all duration-200 hover:scale-105"
```

## Output
Complete component file with proper typing and modern patterns.
