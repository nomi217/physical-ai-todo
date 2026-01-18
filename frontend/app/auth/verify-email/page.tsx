'use client'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'

export default function VerifyEmailPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')
  const registered = searchParams.get('registered')

  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'pending'>('pending')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')
  const [isResending, setIsResending] = useState(false)

  useEffect(() => {
    if (token) {
      verifyEmail(token)
    } else if (registered) {
      setStatus('pending')
      setMessage('Check your email for a verification link')
    }
  }, [token, registered])

  const verifyEmail = async (verificationToken: string) => {
    setStatus('loading')

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: verificationToken })
      })

      if (response.ok) {
        setStatus('success')
        setMessage('Email verified successfully! Redirecting to sign in...')
        setTimeout(() => {
          router.push('/auth/signin')
        }, 2000)
      } else {
        const error = await response.json()
        setStatus('error')
        // Handle all error formats properly
        let errorMsg = 'Verification failed'
        if (Array.isArray(error.detail)) {
          const firstError = error.detail[0]
          errorMsg = typeof firstError === 'object' ? (firstError.msg || JSON.stringify(firstError)) : String(firstError)
        } else if (typeof error.detail === 'string') {
          errorMsg = error.detail
        } else if (typeof error.detail === 'object' && error.detail !== null) {
          errorMsg = JSON.stringify(error.detail)
        }
        setMessage(errorMsg)
      }
    } catch (error) {
      setStatus('error')
      setMessage('Failed to verify email. Please try again.')
    }
  }

  const resendVerification = async () => {
    if (!email) {
      setMessage('Please enter your email address')
      return
    }

    setIsResending(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })

      if (response.ok) {
        setMessage('Verification email sent! Check your inbox.')
      } else {
        const error = await response.json()
        // Handle all error formats properly
        let errorMsg = 'Failed to resend email'
        if (Array.isArray(error.detail)) {
          const firstError = error.detail[0]
          errorMsg = typeof firstError === 'object' ? (firstError.msg || JSON.stringify(firstError)) : String(firstError)
        } else if (typeof error.detail === 'string') {
          errorMsg = error.detail
        } else if (typeof error.detail === 'object' && error.detail !== null) {
          errorMsg = JSON.stringify(error.detail)
        }
        setMessage(errorMsg)
      }
    } catch (error) {
      setMessage('Failed to resend email. Please try again.')
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      {/* Background animated orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 bg-blue-500 rounded-full blur-3xl opacity-20"
          animate={{
            x: [0, 100, 0],
            y: [0, 50, 0],
          }}
          transition={{ duration: 20, repeat: Infinity }}
          style={{ top: '10%', left: '10%' }}
        />
        <motion.div
          className="absolute w-96 h-96 bg-purple-500 rounded-full blur-3xl opacity-20"
          animate={{
            x: [0, -100, 0],
            y: [0, -50, 0],
          }}
          transition={{ duration: 15, repeat: Infinity }}
          style={{ bottom: '10%', right: '10%' }}
        />
      </div>

      {/* Verification card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md relative z-10"
      >
        <div className="backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-3xl p-8 shadow-2xl">
          {/* Icon */}
          <motion.div
            className="text-center mb-6"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
          >
            {status === 'loading' && (
              <div className="text-6xl mb-4">
                <svg className="animate-spin h-16 w-16 mx-auto text-blue-400" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
            )}
            {status === 'success' && (
              <div className="text-6xl mb-4 text-green-400">✓</div>
            )}
            {status === 'error' && (
              <div className="text-6xl mb-4 text-red-400">✗</div>
            )}
            {status === 'pending' && (
              <div className="text-6xl mb-4">📧</div>
            )}

            <h1 className="text-3xl font-bold text-white mb-2">
              {status === 'loading' && 'Verifying Email'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
              {status === 'pending' && 'Check Your Email'}
            </h1>
          </motion.div>

          {/* Message */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-center mb-6"
          >
            <p className="text-gray-300 text-sm leading-relaxed">
              {message || 'We sent a verification link to your email address. Please click the link to verify your account.'}
            </p>
          </motion.div>

          {/* Resend form */}
          {(status === 'error' || status === 'pending') && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-4"
            >
              <div className="border-t border-white border-opacity-20 pt-6">
                <p className="text-gray-300 text-sm mb-4 text-center">
                  Didn't receive the email?
                </p>

                <div className="space-y-3">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  />

                  <motion.button
                    onClick={resendVerification}
                    disabled={isResending}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isResending ? 'Sending...' : 'Resend Verification Email'}
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Success actions */}
          {status === 'success' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <p className="text-gray-300 text-sm mb-4">
                Redirecting you to sign in...
              </p>
            </motion.div>
          )}

          {/* Back to sign in */}
          <div className="mt-6 text-center">
            <Link href="/auth/signin" className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
              ← Back to Sign In
            </Link>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-gray-400 text-xs">
              Powered by <span className="text-white font-medium">Nauman Khalid</span>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
