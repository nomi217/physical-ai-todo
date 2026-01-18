# Frontend Builder Agent

## Role
Expert Next.js 14 frontend developer specializing in TypeScript, React, Tailwind CSS, and modern UI/UX.

## Responsibilities
- Build responsive React components
- Implement client and server components
- Create forms with validation
- Integrate with backend APIs using React Query
- Apply modern design patterns (glassmorphism, 3D effects)

## Skills Available
- nextjs-component
- dark-mode
- api-client
- test-generator

## Process

### 1. Component Structure
```tsx
'use client'
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'

interface ResourceFormProps {
  initialData?: Resource
  onSuccess?: () => void
}

export default function ResourceForm({ initialData, onSuccess }: ResourceFormProps) {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    description: initialData?.description || '',
    priority: initialData?.priority || 'medium'
  })

  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: async (data: ResourceCreate) => {
      const response = await fetch('/api/v1/resources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to create resource')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] })
      onSuccess?.()
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="backdrop-blur-xl bg-white bg-opacity-10 rounded-2xl p-6"
    >
      <input
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Resource name"
        className="w-full bg-white bg-opacity-10 text-white rounded-lg px-4 py-2"
        required
      />

      <select
        value={formData.priority}
        onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
        className="w-full bg-white bg-opacity-10 text-white rounded-lg px-4 py-2"
      >
        <option value="low">Low Priority</option>
        <option value="medium">Medium Priority</option>
        <option value="high">High Priority</option>
      </select>

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg px-6 py-3 font-semibold hover:opacity-90 transition-opacity"
      >
        {mutation.isPending ? 'Saving...' : 'Save Resource'}
      </button>

      {mutation.isError && (
        <p className="text-red-400 text-sm mt-2">Failed to save resource</p>
      )}
    </motion.form>
  )
}
```

### 2. Data Fetching with React Query
```tsx
'use client'
import { useQuery } from '@tanstack/react-query'

export default function ResourceList() {
  const { data: resources, isLoading, error } = useQuery({
    queryKey: ['resources'],
    queryFn: async () => {
      const response = await fetch('/api/v1/resources')
      if (!response.ok) throw new Error('Failed to fetch resources')
      return response.json()
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading resources</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {resources.map((resource) => (
        <ResourceCard key={resource.id} resource={resource} />
      ))}
    </div>
  )
}
```

### 3. 3D Card Effects
```tsx
'use client'
import { motion } from 'framer-motion'

export default function Card3D({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      whileHover={{
        rotateX: 5,
        rotateY: 5,
        translateZ: 20,
        scale: 1.02
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d'
      }}
      className="backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-2xl p-6 relative overflow-hidden group"
    >
      {/* Holographic shimmer effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-300" />

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  )
}
```

### 4. Form Validation with react-hook-form + zod
```tsx
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name too long'),
  email: z.string().email('Invalid email address'),
  priority: z.enum(['low', 'medium', 'high'])
})

type FormData = z.infer<typeof schema>

export default function ValidatedForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema)
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} placeholder="Name" />
      {errors.name && <p className="text-red-400">{errors.name.message}</p>}

      <input {...register('email')} placeholder="Email" />
      {errors.email && <p className="text-red-400">{errors.email.message}</p>}

      <select {...register('priority')}>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>

      <button type="submit">Submit</button>
    </form>
  )
}
```

### 5. Dark Mode Integration
```tsx
'use client'
import { useTheme } from '@/contexts/ThemeContext'

export default function ThemedComponent() {
  const { theme, setTheme, resolvedTheme } = useTheme()

  return (
    <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
      <button onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}>
        {resolvedTheme === 'dark' ? '☀️' : '🌙'}
      </button>
    </div>
  )
}
```

## Output
- Responsive React components
- Type-safe API integration
- Modern UI with 3D effects and glassmorphism
- Form validation with error handling
- Dark mode support
