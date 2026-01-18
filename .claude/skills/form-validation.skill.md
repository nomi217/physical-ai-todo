# Form Validation Skill (react-hook-form + zod)

## Purpose
Create type-safe form validation with react-hook-form and zod schema validation for Next.js applications.

## When to Use
- Building sign-up/sign-in forms
- Creating data entry forms
- Validating user input
- Implementing complex form logic

## Inputs Required
- **Form Fields**: Field names and types
- **Validation Rules**: Required, min/max length, patterns
- **Submit Handler**: Function to handle form submission

## Process

### 1. Install Dependencies
```bash
npm install react-hook-form@^7.49.2
npm install zod@^3.22.4
npm install @hookform/resolvers@^3.3.4
```

### 2. Basic Form with Validation
```tsx
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

// Define validation schema
const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain uppercase letter')
    .regex(/[a-z]/, 'Password must contain lowercase letter')
    .regex(/[0-9]/, 'Password must contain number'),
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  age: z.number().min(18, 'Must be 18 or older').max(120),
})

// Infer TypeScript type from schema
type FormData = z.infer<typeof schema>

export default function SignUpForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: '',
      password: '',
      fullName: '',
      age: 18
    }
  })

  const onSubmit = async (data: FormData) => {
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })

      if (!response.ok) throw new Error('Registration failed')

      reset()
      // Redirect or show success message
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Full Name */}
      <div>
        <label className="block text-sm font-medium mb-1">Full Name</label>
        <input
          {...register('fullName')}
          className="w-full px-4 py-2 border rounded-lg"
          placeholder="John Doe"
        />
        {errors.fullName && (
          <p className="text-red-500 text-sm mt-1">{errors.fullName.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          {...register('email')}
          type="email"
          className="w-full px-4 py-2 border rounded-lg"
          placeholder="john@example.com"
        />
        {errors.email && (
          <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
        )}
      </div>

      {/* Password */}
      <div>
        <label className="block text-sm font-medium mb-1">Password</label>
        <input
          {...register('password')}
          type="password"
          className="w-full px-4 py-2 border rounded-lg"
        />
        {errors.password && (
          <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
        )}
      </div>

      {/* Age */}
      <div>
        <label className="block text-sm font-medium mb-1">Age</label>
        <input
          {...register('age', { valueAsNumber: true })}
          type="number"
          className="w-full px-4 py-2 border rounded-lg"
        />
        {errors.age && (
          <p className="text-red-500 text-sm mt-1">{errors.age.message}</p>
        )}
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? 'Submitting...' : 'Sign Up'}
      </button>
    </form>
  )
}
```

### 3. Reusable Form Input Component
```tsx
'use client'
import { UseFormRegister, FieldError } from 'react-hook-form'

interface FormInputProps {
  name: string
  label: string
  type?: string
  placeholder?: string
  register: UseFormRegister<any>
  error?: FieldError
  icon?: React.ReactNode
}

export default function FormInput({
  name,
  label,
  type = 'text',
  placeholder,
  register,
  error,
  icon
}: FormInputProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700">
        {label}
      </label>

      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}

        <input
          id={name}
          type={type}
          {...register(name)}
          placeholder={placeholder}
          className={`
            w-full px-4 py-3 border rounded-lg
            focus:outline-none focus:ring-2 focus:ring-blue-500
            ${icon ? 'pl-10' : ''}
            ${error ? 'border-red-500' : 'border-gray-300'}
          `}
        />
      </div>

      {error && (
        <p className="text-red-500 text-sm flex items-center gap-1">
          <span>⚠️</span>
          {error.message}
        </p>
      )}
    </div>
  )
}

// Usage
<FormInput
  name="email"
  label="Email Address"
  type="email"
  placeholder="you@example.com"
  register={register}
  error={errors.email}
  icon={<EmailIcon />}
/>
```

### 4. Advanced Validation Schemas
```tsx
import * as z from 'zod'

// Password confirmation
const passwordSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword']
})

// Conditional validation
const userSchema = z.object({
  role: z.enum(['admin', 'user']),
  adminCode: z.string().optional()
}).refine((data) => {
  if (data.role === 'admin') {
    return data.adminCode !== undefined && data.adminCode.length > 0
  }
  return true
}, {
  message: 'Admin code is required for admin role',
  path: ['adminCode']
})

// Custom validation
const phoneSchema = z.object({
  phone: z.string().refine((val) => {
    return /^\+?[1-9]\d{1,14}$/.test(val)
  }, {
    message: 'Invalid phone number format'
  })
})

// Date validation
const dateSchema = z.object({
  birthDate: z.date()
    .min(new Date('1900-01-01'), 'Too old')
    .max(new Date(), 'Cannot be in the future')
})

// Array validation
const tagsSchema = z.object({
  tags: z.array(z.string())
    .min(1, 'At least one tag required')
    .max(5, 'Maximum 5 tags allowed')
})

// File upload validation
const fileSchema = z.object({
  avatar: z.instanceof(FileList)
    .refine((files) => files?.length === 1, 'File is required')
    .refine(
      (files) => files?.[0]?.size <= 5000000,
      'Max file size is 5MB'
    )
    .refine(
      (files) => ['image/jpeg', 'image/png'].includes(files?.[0]?.type),
      'Only .jpg and .png formats are supported'
    )
})
```

### 5. Multi-Step Form
```tsx
'use client'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

// Step schemas
const step1Schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

const step2Schema = z.object({
  fullName: z.string().min(2),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/),
})

const step3Schema = z.object({
  company: z.string().min(2),
  role: z.string().min(2),
})

type Step1Data = z.infer<typeof step1Schema>
type Step2Data = z.infer<typeof step2Schema>
type Step3Data = z.infer<typeof step3Schema>

export default function MultiStepForm() {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState<Partial<Step1Data & Step2Data & Step3Data>>({})

  const currentSchema = step === 1 ? step1Schema : step === 2 ? step2Schema : step3Schema

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({
    resolver: zodResolver(currentSchema),
    defaultValues: formData
  })

  const onSubmit = (data: any) => {
    if (step < 3) {
      setFormData({ ...formData, ...data })
      setStep(step + 1)
    } else {
      // Final submission
      const completeData = { ...formData, ...data }
      console.log('Submitting:', completeData)
    }
  }

  return (
    <div>
      {/* Progress indicator */}
      <div className="flex gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className={`h-2 flex-1 rounded ${
              s <= step ? 'bg-blue-600' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        {step === 1 && (
          <>
            <FormInput name="email" label="Email" register={register} error={errors.email} />
            <FormInput name="password" label="Password" type="password" register={register} error={errors.password} />
          </>
        )}

        {step === 2 && (
          <>
            <FormInput name="fullName" label="Full Name" register={register} error={errors.fullName} />
            <FormInput name="phone" label="Phone" register={register} error={errors.phone} />
          </>
        )}

        {step === 3 && (
          <>
            <FormInput name="company" label="Company" register={register} error={errors.company} />
            <FormInput name="role" label="Role" register={register} error={errors.role} />
          </>
        )}

        <div className="flex gap-4 mt-6">
          {step > 1 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="px-6 py-2 border rounded-lg"
            >
              Back
            </button>
          )}

          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            {step === 3 ? 'Submit' : 'Next'}
          </button>
        </div>
      </form>
    </div>
  )
}
```

### 6. Dynamic Field Arrays
```tsx
'use client'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  tasks: z.array(
    z.object({
      title: z.string().min(1, 'Task title required'),
      description: z.string().optional(),
    })
  ).min(1, 'At least one task required')
})

type FormData = z.infer<typeof schema>

export default function TaskListForm() {
  const { register, control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      tasks: [{ title: '', description: '' }]
    }
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'tasks'
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {fields.map((field, index) => (
        <div key={field.id} className="border p-4 rounded-lg mb-4">
          <FormInput
            name={`tasks.${index}.title`}
            label="Task Title"
            register={register}
            error={errors.tasks?.[index]?.title}
          />

          <FormInput
            name={`tasks.${index}.description`}
            label="Description"
            register={register}
            error={errors.tasks?.[index]?.description}
          />

          <button
            type="button"
            onClick={() => remove(index)}
            className="text-red-600 mt-2"
          >
            Remove Task
          </button>
        </div>
      ))}

      <button
        type="button"
        onClick={() => append({ title: '', description: '' })}
        className="px-4 py-2 bg-gray-200 rounded-lg mb-4"
      >
        Add Task
      </button>

      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-3 rounded-lg"
      >
        Submit
      </button>
    </form>
  )
}
```

### 7. Async Validation (Check Email Availability)
```tsx
const schema = z.object({
  email: z.string().email()
    .refine(async (email) => {
      const response = await fetch(`/api/check-email?email=${email}`)
      const data = await response.json()
      return data.available
    }, {
      message: 'Email is already taken'
    })
})
```

## Best Practices

### Performance
- Use `mode: 'onBlur'` for less aggressive validation
- Debounce async validations
- Memoize validation schemas
- Use `shouldUnregister: false` for dynamic fields

### User Experience
- Show inline errors near inputs
- Disable submit during validation
- Provide helpful error messages
- Show loading states for async validation
- Focus first invalid field on submit

### Security
- Always validate on server-side too
- Sanitize user input
- Use zod transform for data sanitization
- Never trust client-side validation alone

## Testing
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

test('shows validation errors', async () => {
  render(<SignUpForm />)

  const submitButton = screen.getByRole('button', { name: /sign up/i })
  fireEvent.click(submitButton)

  await waitFor(() => {
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
  })
})
```

## Output
- Type-safe form validation
- Reusable form components
- Multi-step form support
- Dynamic field arrays
- Async validation
- Excellent error handling
