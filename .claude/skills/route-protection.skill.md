# Route Protection & Auth Guards Skill

## Purpose
Implement authentication guards and protected routes for Next.js 14 applications with App Router and React Context.

## When to Use
- Protecting dashboard/admin pages
- Redirecting unauthenticated users
- Implementing role-based access control
- Managing authentication state

## Inputs Required
- **Protected Routes**: List of routes requiring authentication
- **Auth API**: Authentication API endpoints
- **Redirect Paths**: Where to redirect unauthorized users

## Process

### 1. Create Auth Context
```tsx
// contexts/AuthContext.tsx
'use client'
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: number
  email: string
  fullName: string
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  signup: (email: string, password: string, fullName: string) => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Check authentication status on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/v1/auth/me', {
        credentials: 'include'
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        setUser(null)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    await checkAuth()
    router.push('/dashboard')
  }

  const logout = async () => {
    await fetch('/api/v1/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })

    setUser(null)
    router.push('/')
  }

  const signup = async (email: string, password: string, fullName: string) => {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Signup failed')
    }

    // Auto-login after signup
    await login(email, password)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        signup,
        isAuthenticated: !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

### 2. Protected Route Component (Client-Side)
```tsx
// components/auth/ProtectedRoute.tsx
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireRole?: string[]
}

export default function ProtectedRoute({
  children,
  requireRole
}: ProtectedRouteProps) {
  const { user, loading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/signin')
    }

    if (!loading && requireRole && user) {
      if (!requireRole.includes(user.role)) {
        router.push('/unauthorized')
      }
    }
  }, [user, loading, isAuthenticated, requireRole, router])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  if (requireRole && user && !requireRole.includes(user.role)) {
    return null
  }

  return <>{children}</>
}
```

### 3. Protected Layout (App Router)
```tsx
// app/(protected)/layout.tsx
'use client'
import { useAuth } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import Navbar from '@/components/Navbar'

export default function ProtectedLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
      </div>
    </ProtectedRoute>
  )
}
```

### 4. Middleware-Based Protection (Server-Side)
```ts
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')
  const { pathname } = request.nextUrl

  // Protected routes
  const protectedPaths = ['/dashboard', '/settings', '/profile']
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path))

  // Redirect to signin if accessing protected route without token
  if (isProtectedPath && !token) {
    const url = new URL('/signin', request.url)
    url.searchParams.set('redirect', pathname)
    return NextResponse.redirect(url)
  }

  // Redirect to dashboard if accessing auth pages with token
  const authPaths = ['/signin', '/signup']
  const isAuthPath = authPaths.some(path => pathname.startsWith(path))

  if (isAuthPath && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/settings/:path*',
    '/profile/:path*',
    '/signin',
    '/signup'
  ]
}
```

### 5. Server Component Auth Check
```tsx
// app/(protected)/dashboard/page.tsx
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

async function getUser() {
  const cookieStore = cookies()
  const token = cookieStore.get('access_token')

  if (!token) {
    redirect('/signin')
  }

  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${token.value}`
      },
      cache: 'no-store'
    })

    if (!response.ok) {
      redirect('/signin')
    }

    return await response.json()
  } catch (error) {
    redirect('/signin')
  }
}

export default async function DashboardPage() {
  const user = await getUser()

  return (
    <div>
      <h1>Welcome, {user.fullName}!</h1>
      {/* Dashboard content */}
    </div>
  )
}
```

### 6. Role-Based Access Control
```tsx
// components/auth/RoleGuard.tsx
'use client'
import { useAuth } from '@/contexts/AuthContext'

interface RoleGuardProps {
  children: React.ReactNode
  allowedRoles: string[]
  fallback?: React.ReactNode
}

export default function RoleGuard({
  children,
  allowedRoles,
  fallback = null
}: RoleGuardProps) {
  const { user, loading } = useAuth()

  if (loading) {
    return <div>Loading...</div>
  }

  if (!user || !allowedRoles.includes(user.role)) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

// Usage
<RoleGuard
  allowedRoles={['admin', 'moderator']}
  fallback={<p>You don't have permission to view this.</p>}
>
  <AdminPanel />
</RoleGuard>
```

### 7. Higher-Order Component (HOC) Pattern
```tsx
// lib/withAuth.tsx
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    requireRole?: string[]
    redirectTo?: string
  }
) {
  return function AuthenticatedComponent(props: P) {
    const { user, loading, isAuthenticated } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!loading && !isAuthenticated) {
        router.push(options?.redirectTo || '/signin')
      }

      if (
        !loading &&
        options?.requireRole &&
        user &&
        !options.requireRole.includes(user.role)
      ) {
        router.push('/unauthorized')
      }
    }, [user, loading, isAuthenticated, router])

    if (loading || !isAuthenticated) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )
    }

    return <Component {...props} />
  }
}

// Usage
export default withAuth(DashboardPage, {
  requireRole: ['admin'],
  redirectTo: '/signin'
})
```

### 8. Redirect After Login
```tsx
// app/signin/page.tsx
'use client'
import { useSearchParams } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function SignInPage() {
  const searchParams = useSearchParams()
  const redirect = searchParams.get('redirect') || '/dashboard'
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (email: string, password: string) => {
    await login(email, password)
    router.push(redirect)
  }

  return (
    // ... form implementation
  )
}
```

### 9. API Route Protection (Next.js API Routes)
```ts
// app/api/protected/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

async function verifyAuth(request: NextRequest) {
  const cookieStore = cookies()
  const token = cookieStore.get('access_token')

  if (!token) {
    return null
  }

  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${token.value}`
      }
    })

    if (!response.ok) return null

    return await response.json()
  } catch (error) {
    return null
  }
}

export async function GET(request: NextRequest) {
  const user = await verifyAuth(request)

  if (!user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  return NextResponse.json({ data: 'Protected data', user })
}
```

### 10. Loading Skeleton for Protected Pages
```tsx
// components/auth/AuthLoadingSkeleton.tsx
export default function AuthLoadingSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 animate-pulse">
      <div className="h-16 bg-gray-200"></div>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="space-y-4">
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  )
}
```

## Best Practices

### Security
- Never store sensitive data in localStorage
- Use httpOnly cookies for tokens
- Implement token refresh mechanism
- Always verify auth on server-side
- Add rate limiting to auth endpoints
- Log authentication events

### Performance
- Cache auth status where appropriate
- Use suspense for loading states
- Implement optimistic UI updates
- Debounce auth checks
- Use middleware for faster redirects

### User Experience
- Show loading states during auth checks
- Preserve redirect URL after login
- Provide clear error messages
- Implement "Remember me" functionality
- Add session timeout warnings
- Handle token expiration gracefully

## Testing
```tsx
import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider } from '@/contexts/AuthContext'

test('redirects to signin when not authenticated', async () => {
  render(
    <AuthProvider>
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    </AuthProvider>
  )

  await waitFor(() => {
    expect(window.location.pathname).toBe('/signin')
  })
})
```

## Output
- Complete authentication system
- Protected routes (client + server)
- Role-based access control
- Middleware protection
- Auth context management
- Loading states and redirects
