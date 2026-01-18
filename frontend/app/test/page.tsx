'use client'

import dynamic from 'next/dynamic'

// Force client-side only rendering
const ClientOnlyTest = dynamic(() => import('./ClientTest'), { ssr: false })

export default function TestPage() {
  return <ClientOnlyTest />
}
