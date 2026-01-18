import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="max-w-md w-full bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center">
        <div className="text-6xl mb-4">404</div>
        <h2 className="text-2xl font-bold text-white mb-4">Page Not Found</h2>
        <p className="text-gray-300 mb-6">
          The page you're looking for doesn't exist.
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-xl transition-all"
        >
          Go Home
        </Link>
      </div>
    </div>
  )
}
