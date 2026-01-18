'use client'
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface User {
  id: number
  email: string
  full_name: string | null
  is_verified: boolean
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check if user is logged in on mount
  useEffect(() => {
    refreshUser()
  }, [])

  const refreshUser = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        credentials: 'include'
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        setUser(null)
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      // Handle both FastAPI validation errors and regular errors
      if (Array.isArray(error.detail)) {
        // Pydantic validation error - extract first error message
        const firstError = error.detail[0]
        const errorMsg = typeof firstError === 'object' ? (firstError.msg || JSON.stringify(firstError)) : String(firstError)
        throw new Error(errorMsg)
      } else if (typeof error.detail === 'string') {
        throw new Error(error.detail)
      } else if (typeof error.detail === 'object' && error.detail !== null) {
        // Handle object error details
        throw new Error(JSON.stringify(error.detail))
      } else {
        throw new Error('Login failed')
      }
    }

    const data = await response.json()
    setUser(data.user)
    router.push('/dashboard')
  }

  const register = async (email: string, password: string, fullName: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName
      })
    })

    if (!response.ok) {
      const error = await response.json()
      // Handle both FastAPI validation errors and regular errors
      if (Array.isArray(error.detail)) {
        // Pydantic validation error - extract first error message
        const firstError = error.detail[0]
        const errorMsg = typeof firstError === 'object' ? (firstError.msg || JSON.stringify(firstError)) : String(firstError)
        throw new Error(errorMsg)
      } else if (typeof error.detail === 'string') {
        throw new Error(error.detail)
      } else if (typeof error.detail === 'object' && error.detail !== null) {
        // Handle object error details
        throw new Error(JSON.stringify(error.detail))
      } else {
        throw new Error('Registration failed')
      }
    }

    // Email verification disabled for hackathon demo - auto-login after signup
    // Users are auto-verified on the backend, so we can log them in immediately
    await login(email, password)
  }

  const logout = async () => {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      router.push('/landing')
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
