'use client'

import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Header */}
      <header className="px-6 py-6">
        <nav className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-4xl">✓</div>
            <h1 className="text-2xl font-bold text-white">FlowTask</h1>
          </div>
          <div className="flex gap-4">
            <Link
              href="/auth/signin"
              className="px-6 py-2 text-white hover:bg-white hover:bg-opacity-10 rounded-lg transition-all backdrop-blur-sm border border-white border-opacity-20 inline-block text-center"
            >
              Sign In
            </Link>
            <Link
              href="/auth/signup"
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-xl transition-all inline-block text-center"
            >
              Get Started Free
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="px-6 py-20 md:py-32">
        <div className="max-w-7xl mx-auto text-center">
          <div className="text-9xl mb-6">✓</div>
          <h2 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Effortless Productivity,<br/>
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
              Beautiful Design
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto">
            Experience the future of task management with AI-powered intelligence
          </p>
          <Link
            href="/auth/signup"
            className="px-10 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xl font-bold rounded-xl shadow-2xl hover:shadow-purple-500/50 transition-all inline-block"
          >
            Start Your Free Journey →
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Powered by Innovation
            </h3>
            <p className="text-xl text-gray-300">
              Built with the latest 2025 design trends
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: '🎯', title: 'Smart Organization', desc: 'Priorities, tags, advanced filtering' },
              { icon: '🎮', title: 'Interactive Management', desc: 'Drag & drop, bulk actions, shortcuts' },
              { icon: '📝', title: 'Rich Task Details', desc: 'Subtasks, notes, file attachments' },
              { icon: '✨', title: '3D Visual Effects', desc: 'Glassmorphism, smooth animations' },
              { icon: '🌙', title: 'Perfect Dark Mode', desc: 'Flicker-free dark/light themes' },
              { icon: '🤖', title: 'AI Intelligence', desc: 'Claude-powered chatbot' }
            ].map((feature, index) => (
              <div
                key={index}
                className="backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-3xl p-8 hover:bg-opacity-20 transition-all"
              >
                <div className="text-6xl mb-4">{feature.icon}</div>
                <h4 className="text-2xl font-bold text-white mb-3">{feature.title}</h4>
                <p className="text-gray-300">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto text-center backdrop-blur-xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-white border-opacity-20 rounded-3xl p-12">
          <h3 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Productivity?
          </h3>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of users revolutionizing task management
          </p>
          <Link
            href="/auth/signup"
            className="px-10 py-4 bg-white text-purple-600 text-xl font-bold rounded-xl shadow-2xl hover:shadow-white/50 transition-all inline-block"
          >
            Get Started for Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-10 border-t border-white border-opacity-10">
        <div className="max-w-7xl mx-auto text-center text-white">
          <div className="mb-4 flex items-center justify-center gap-2">
            <span className="text-2xl">✓</span>
            <span className="text-xl font-bold">FlowTask</span>
          </div>
          <p className="text-gray-400 mb-2">Effortless Productivity, Beautiful Design</p>
          <p className="text-gray-500">
            Powered by <span className="font-semibold bg-gradient-to-r from-blue-400 to-purple-400 text-transparent bg-clip-text">Nauman Khalid</span>
          </p>
          <p className="text-gray-600 text-sm mt-4">© 2025 FlowTask. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
