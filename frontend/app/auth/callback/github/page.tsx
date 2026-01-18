'use client'
import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { motion } from 'framer-motion'
import Link from 'next/link'

type Status = 'loading' | 'success' | 'error'

export default function GitHubCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { refreshUser } = useAuth()
  const [status, setStatus] = useState<Status>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setMessage(getErrorMessage(error))
      return
    }

    if (!code) {
      setStatus('error')
      setMessage('No authorization code received from GitHub')
      return
    }

    handleCallback(code)
  }, [searchParams])

  const handleCallback = async (code: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/auth/github/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ code })
      })

      if (!response.ok) {
        const error = await response.json()
        let errorMsg = 'Authentication failed'
        if (typeof error.detail === 'string') {
          errorMsg = error.detail
        } else if (typeof error.detail === 'object' && error.detail !== null) {
          errorMsg = JSON.stringify(error.detail)
        }
        throw new Error(errorMsg)
      }

      setStatus('success')
      setMessage('Signed in successfully!')
      await refreshUser()
      setTimeout(() => router.push('/dashboard'), 1000)
    } catch (err: any) {
      setStatus('error')
      if (err.message && err.message.includes('fetch')) {
        setMessage('Network error. Please check your connection.')
      } else {
        setMessage(err.message || 'An error occurred during sign-in')
      }
    }
  }

  const getErrorMessage = (error: string): string => {
    const messages: Record<string, string> = {
      'access_denied': 'You denied GitHub authorization.',
      'invalid_request': 'Invalid OAuth request.'
    }
    return messages[error] || `GitHub error: ${error}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-3xl p-8 shadow-2xl">
          {status === 'loading' && (
            <div className="text-center">
              <svg className="animate-spin h-16 w-16 mx-auto mb-6 text-blue-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <h2 className="text-2xl font-bold text-white mb-2">Completing Sign-In</h2>
              <p className="text-gray-300">Please wait while we sign you in with GitHub...</p>
            </div>
          )}
          {status === 'success' && (
            <div className="text-center">
              <div className="text-6xl mb-4">✓</div>
              <h2 className="text-2xl font-bold text-white mb-2">Success!</h2>
              <p className="text-gray-300 mb-4">{message}</p>
              <p className="text-sm text-gray-400">Redirecting...</p>
            </div>
          )}
          {status === 'error' && (
            <div className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-white mb-4">Authentication Failed</h2>
              <div className="mb-6 p-4 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg">
                <p className="text-red-200 text-sm">{message}</p>
              </div>
              <Link href="/auth/signin" className="block w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg text-center">
                Back to Sign In
              </Link>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
