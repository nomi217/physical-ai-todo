'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function LandingClient() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const features = [
    { icon: '🎯', title: 'Smart Organization', description: 'Priorities, tags, advanced filtering, and instant search', gradient: 'from-blue-500 to-cyan-500' },
    { icon: '🎮', title: 'Interactive Management', description: 'Drag & drop, bulk actions, inline editing, keyboard shortcuts', gradient: 'from-purple-500 to-pink-500' },
    { icon: '📝', title: 'Rich Task Details', description: 'Subtasks with progress, notes, file attachments up to 10MB', gradient: 'from-indigo-500 to-purple-500' },
    { icon: '✨', title: '3D Visual Effects', description: 'Glassmorphism design, smooth 60fps animations, parallax scrolling', gradient: 'from-pink-500 to-rose-500' },
    { icon: '🌙', title: 'Perfect Dark Mode', description: 'Flicker-free dark/light themes with WCAG AA accessibility', gradient: 'from-blue-600 to-indigo-600' },
    { icon: '📊', title: 'Data Management', description: 'Export/import CSV/JSON, templates, analytics dashboard', gradient: 'from-green-500 to-emerald-500' },
    { icon: '🎯', title: 'Focus Mode', description: 'Distraction-free view with Pomodoro timer', gradient: 'from-orange-500 to-yellow-500' },
    { icon: '🤖', title: 'AI Intelligence', description: 'Claude-powered chatbot, task breakdown, semantic search', gradient: 'from-cyan-500 to-blue-500' },
    { icon: '⚡', title: 'Lightning Fast', description: 'API responses <200ms, 60fps animations, real-time updates', gradient: 'from-yellow-500 to-orange-500' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white rounded-full opacity-20"
            animate={mounted ? { y: [null, Math.random() * 1080], opacity: [0.2, 0.5, 0.2] } : {}}
            transition={{ duration: Math.random() * 10 + 10, repeat: Infinity, ease: 'linear' }}
            style={{ left: Math.random() * 100 + '%', top: Math.random() * 100 + '%' }}
          />
        ))}
      </div>

      {/* Header */}
      <header className="relative z-10 px-6 py-6">
        <nav className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -20 }}
            animate={mounted ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <div className="text-4xl">✓</div>
            <h1 className="text-2xl font-bold text-white">FlowTask</h1>
          </motion.div>
          <motion.div
            className="flex gap-4"
            initial={{ opacity: 0, x: 20 }}
            animate={mounted ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <button
              onClick={() => router.push('/auth/signin')}
              className="px-6 py-2 text-white hover:bg-white hover:bg-opacity-10 rounded-lg transition-all backdrop-blur-sm border border-white border-opacity-20"
            >
              Sign In
            </button>
            <button
              onClick={() => router.push('/auth/signup')}
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-xl hover:shadow-purple-500/50 transition-all transform hover:scale-105"
            >
              Get Started Free
            </button>
          </motion.div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 px-6 py-20 md:py-32">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={mounted ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.div
              className="text-9xl filter drop-shadow-2xl mb-6 inline-block"
              animate={mounted ? { scale: [1, 1.05, 1], rotateY: [0, 10, 0] } : {}}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            >
              ✓
            </motion.div>
            <h2 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Effortless Productivity,<br />
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
                Beautiful Design
              </span>
            </h2>
            <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto">
              Experience the future of task management with stunning effects, AI-powered organization, and seamless dark mode
            </p>
            <button
              onClick={() => router.push('/auth/signup')}
              className="px-10 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xl font-bold rounded-xl shadow-2xl shadow-purple-500/50 hover:shadow-purple-500/80 transition-all transform hover:scale-105"
            >
              Start Your Free Journey →
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={mounted ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {[
              { label: '99.9%', desc: 'Uptime' },
              { label: '<100ms', desc: 'Response Time' },
              { label: '10K+', desc: 'Happy Users' }
            ].map((stat, i) => (
              <div key={i} className="backdrop-blur-lg bg-white bg-opacity-10 border border-white border-opacity-20 rounded-2xl p-6 hover:bg-opacity-20 transition-all transform hover:scale-105">
                <div className="text-4xl font-bold text-white mb-2">{stat.label}</div>
                <div className="text-gray-300">{stat.desc}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={mounted ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            <h3 className="text-4xl md:text-5xl font-bold text-white mb-4">Powered by Innovation</h3>
            <p className="text-xl text-gray-300">Built with the latest 2025 design trends</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="group relative backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-3xl p-8 hover:bg-opacity-20 transition-all cursor-pointer"
                initial={{ opacity: 0, y: 50 }}
                animate={mounted ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                whileHover={{ scale: 1.05, rotateY: 5 }}
              >
                <div className={`absolute -inset-1 bg-gradient-to-r ${feature.gradient} rounded-3xl opacity-0 group-hover:opacity-20 blur-xl transition-opacity`}></div>
                <div className="relative z-10">
                  <div className="text-6xl mb-4">{feature.icon}</div>
                  <h4 className="text-2xl font-bold text-white mb-3">{feature.title}</h4>
                  <p className="text-gray-300">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 px-6 py-20">
        <motion.div
          className="max-w-4xl mx-auto text-center backdrop-blur-xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-white border-opacity-20 rounded-3xl p-12"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={mounted ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8 }}
          whileHover={{ scale: 1.02 }}
        >
          <h3 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Productivity?
          </h3>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of users revolutionizing task management
          </p>
          <button
            onClick={() => router.push('/auth/signup')}
            className="px-10 py-4 bg-white text-purple-600 text-xl font-bold rounded-xl shadow-2xl hover:shadow-white/50 transition-all transform hover:scale-105"
          >
            Get Started for Free
          </button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-10 border-t border-white border-opacity-10">
        <div className="max-w-7xl mx-auto text-center">
          <div className="text-white mb-4 flex items-center justify-center gap-2">
            <span className="text-2xl">✓</span>
            <span className="text-xl font-bold">FlowTask</span>
          </div>
          <p className="text-gray-400 mb-2">Effortless Productivity, Beautiful Design</p>
          <p className="text-gray-500 flex items-center justify-center gap-2">
            <span>Powered by</span>
            <span className="font-semibold bg-gradient-to-r from-blue-400 to-purple-400 text-transparent bg-clip-text">
              Nauman Khalid
            </span>
          </p>
          <p className="text-gray-600 text-sm mt-4">© 2025 FlowTask. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
