import { redirect } from 'next/navigation'

export default function HomePage() {
  // Middleware handles the redirect based on auth status
  // This should never be reached, but redirect to landing as fallback
  redirect('/landing')
}
