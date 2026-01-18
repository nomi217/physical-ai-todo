import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Routes that require authentication
const protectedRoutes = ['/dashboard']  // /chat handles its own auth

// Auth routes (should redirect to dashboard if already logged in)
const authRoutes = ['/auth/signin', '/auth/signup']

// Public routes
const publicRoutes = ['/', '/landing', '/auth/verify-email', '/auth/callback']

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get access token from cookies
  const accessToken = request.cookies.get('access_token')?.value

  // Check if user is authenticated by verifying token with backend
  let isAuthenticated = false
  if (accessToken) {
    try {
      // Use NEXT_PUBLIC_API_URL_INTERNAL for server-side calls (Docker service name)
      // Falls back to NEXT_PUBLIC_API_URL for browser calls (localhost)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL_INTERNAL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          Cookie: `access_token=${accessToken}`
        },
        cache: 'no-store'
      })
      isAuthenticated = response.ok
    } catch (error) {
      console.error('Auth check failed:', error)
      isAuthenticated = false
    }
  }

  // Handle protected routes - only /dashboard and /chat need auth
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    if (!isAuthenticated) {
      const url = request.nextUrl.clone()
      url.pathname = '/auth/signin'
      url.searchParams.set('redirect', pathname)
      return NextResponse.redirect(url)
    }
  }

  // Handle root path - ALWAYS show landing page (no auto-redirect to dashboard)
  if (pathname === '/') {
    const url = request.nextUrl.clone()
    url.pathname = '/landing'
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
