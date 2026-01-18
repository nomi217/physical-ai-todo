'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function ClientTest() {
  const [count, setCount] = useState(0)
  const router = useRouter()

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom right, #1a202c, #2563eb, #7c3aed)',
      padding: '32px',
      color: 'white',
      fontFamily: 'system-ui'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{
          background: '#10b981',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '24px',
          fontSize: '24px',
          fontWeight: 'bold'
        }}>
          ✅ CLIENT-SIDE RENDERING WORKING! (SSR Disabled)
        </div>

        <div style={{
          background: 'rgba(255,255,255,0.1)',
          padding: '32px',
          borderRadius: '12px'
        }}>
          <h1 style={{ fontSize: '48px', marginBottom: '24px' }}>FlowTask Test</h1>

          <div style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '24px', marginBottom: '16px' }}>Click Counter Test:</h2>
            <p style={{ fontSize: '32px', marginBottom: '16px' }}>Count: {count}</p>
            <button
              onClick={() => setCount(count + 1)}
              style={{
                background: '#10b981',
                color: 'white',
                padding: '16px 32px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '18px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = '#059669'}
              onMouseOut={(e) => e.currentTarget.style.background = '#10b981'}
            >
              Click Me! (+1)
            </button>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <button
              onClick={() => alert('Alert works!')}
              style={{
                background: '#3b82f6',
                color: 'white',
                padding: '16px 32px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '18px',
                cursor: 'pointer',
                marginRight: '16px',
                fontWeight: 'bold'
              }}
            >
              Test Alert
            </button>

            <button
              onClick={() => router.push('/auth/signup')}
              style={{
                background: '#8b5cf6',
                color: 'white',
                padding: '16px 32px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '18px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Go to Signup
            </button>
          </div>

          <div style={{
            background: 'rgba(255,255,255,0.9)',
            color: '#000',
            padding: '24px',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '20px', marginBottom: '12px' }}>✅ If you can see this and buttons work:</h3>
            <ul style={{ paddingLeft: '24px' }}>
              <li>React IS working with client-side rendering</li>
              <li>The problem is with SSR (Server-Side Rendering) hydration</li>
              <li>Solution: Use dynamic imports with ssr: false for all pages</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
