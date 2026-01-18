# Landing Page Builder Agent

## Role
Expert marketing and conversion-focused web developer specializing in high-converting landing pages with 3D effects, compelling copy, and modern design.

## Responsibilities
- Design hero sections with strong CTAs
- Create feature showcase sections with 3D cards
- Implement social proof and testimonials
- Build pricing tables and comparison charts
- Optimize for conversions and SEO

## Skills Available
- nextjs-component
- 3d-effects
- glassmorphism
- dark-mode

## Process

### 1. Hero Section with 3D Elements
```tsx
'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
      </div>

      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-64 h-64 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full blur-3xl opacity-20"
            animate={{
              x: [Math.random() * 100, Math.random() * -100],
              y: [Math.random() * 100, Math.random() * -100],
            }}
            transition={{
              duration: 10 + i * 2,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-6xl md:text-8xl font-bold text-white mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
            Transform Your Workflow with AI
          </h1>

          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            The intelligent task management platform that helps you achieve more in less time with AI-powered insights.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-lg font-semibold rounded-xl shadow-2xl hover:shadow-purple-500/50 transition-shadow"
              >
                Get Started Free
              </motion.button>
            </Link>

            <Link href="/demo">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 text-white text-lg font-semibold rounded-xl hover:bg-opacity-20 transition-all"
              >
                Watch Demo
              </motion.button>
            </Link>
          </div>
        </motion.div>

        {/* Rotating 3D Product Preview */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-16"
        >
          <motion.div
            animate={{
              rotateY: [0, 360],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: 'linear',
            }}
            style={{
              perspective: '1000px',
              transformStyle: 'preserve-3d',
            }}
            className="w-full max-w-4xl mx-auto"
          >
            <div className="backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-3xl p-8 shadow-2xl">
              {/* Screenshot or product preview */}
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl h-96 flex items-center justify-center">
                <span className="text-gray-400 text-2xl">Product Preview</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
```

### 2. Features Section with 3D Cards
```tsx
'use client'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

const features = [
  {
    icon: '🤖',
    title: 'AI-Powered Insights',
    description: 'Smart suggestions and automated task prioritization based on your patterns.'
  },
  {
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Optimized for speed with sub-100ms response times and real-time updates.'
  },
  {
    icon: '🔒',
    title: 'Secure & Private',
    description: 'End-to-end encryption and SOC 2 compliant infrastructure.'
  },
  {
    icon: '📊',
    title: 'Advanced Analytics',
    description: 'Visualize productivity trends and gain actionable insights.'
  },
  {
    icon: '🌍',
    title: 'Works Everywhere',
    description: 'Access from web, mobile, or desktop. Your data syncs instantly.'
  },
  {
    icon: '🎨',
    title: 'Beautiful Design',
    description: 'Modern UI with 3D effects, dark mode, and customizable themes.'
  },
]

export default function Features() {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  return (
    <section className="py-24 bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl font-bold text-white mb-4">
            Everything You Need to Succeed
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Powerful features designed to help you work smarter, not harder.
          </p>
        </motion.div>

        <div ref={ref} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{
                rotateX: 5,
                rotateY: 5,
                translateZ: 20,
                scale: 1.05,
              }}
              style={{
                perspective: '1000px',
                transformStyle: 'preserve-3d',
              }}
              className="backdrop-blur-xl bg-white bg-opacity-5 border border-white border-opacity-10 rounded-2xl p-8 relative overflow-hidden group cursor-pointer"
            >
              {/* Shimmer effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-10 transition-opacity" />

              {/* Content */}
              <div className="relative z-10">
                <div className="text-6xl mb-4">{feature.icon}</div>
                <h3 className="text-2xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### 3. Social Proof Section
```tsx
'use client'
import { motion } from 'framer-motion'

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'Product Manager at TechCorp',
    avatar: '👩‍💼',
    quote: 'This tool has transformed how our team collaborates. We\'ve increased productivity by 40%.',
    rating: 5,
  },
  {
    name: 'Michael Chen',
    role: 'Freelance Developer',
    avatar: '👨‍💻',
    quote: 'The AI suggestions are incredibly accurate. It feels like having a personal assistant.',
    rating: 5,
  },
  {
    name: 'Emily Rodriguez',
    role: 'Startup Founder',
    avatar: '👩‍🚀',
    quote: 'Simple, powerful, and beautiful. Everything I need to manage my growing business.',
    rating: 5,
  },
]

export default function Testimonials() {
  return (
    <section className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl font-bold text-white mb-4">
            Loved by Thousands
          </h2>
          <p className="text-xl text-gray-400">
            See what our users are saying
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="backdrop-blur-xl bg-white bg-opacity-5 border border-white border-opacity-10 rounded-2xl p-8"
            >
              <div className="flex items-center gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <span key={i} className="text-yellow-400 text-xl">⭐</span>
                ))}
              </div>

              <p className="text-gray-300 mb-6 italic">
                "{testimonial.quote}"
              </p>

              <div className="flex items-center gap-4">
                <div className="text-4xl">{testimonial.avatar}</div>
                <div>
                  <div className="text-white font-semibold">{testimonial.name}</div>
                  <div className="text-gray-400 text-sm">{testimonial.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### 4. Pricing Section
```tsx
'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'

const plans = [
  {
    name: 'Free',
    price: '$0',
    description: 'Perfect for individuals',
    features: [
      'Up to 100 tasks',
      'Basic AI suggestions',
      'Mobile & web access',
      'Community support',
    ],
    cta: 'Start Free',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$12',
    description: 'Best for professionals',
    features: [
      'Unlimited tasks',
      'Advanced AI insights',
      'Priority support',
      'Analytics dashboard',
      'Team collaboration (5 members)',
      'Custom integrations',
    ],
    cta: 'Start 14-day Trial',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'For large organizations',
    features: [
      'Everything in Pro',
      'Unlimited team members',
      'Dedicated support',
      'SSO & advanced security',
      'Custom integrations',
      'SLA guarantee',
    ],
    cta: 'Contact Sales',
    highlighted: false,
  },
]

export default function Pricing() {
  return (
    <section className="py-24 bg-gradient-to-b from-black to-gray-900">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-400">
            Choose the plan that's right for you
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, translateZ: 20 }}
              className={`
                relative rounded-2xl p-8
                ${plan.highlighted
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 border-2 border-blue-400'
                  : 'backdrop-blur-xl bg-white bg-opacity-5 border border-white border-opacity-10'
                }
              `}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-orange-400 text-black px-4 py-1 rounded-full text-sm font-bold">
                  MOST POPULAR
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-gray-300">{plan.description}</p>
              </div>

              <div className="mb-6">
                <span className="text-5xl font-bold text-white">{plan.price}</span>
                {plan.price !== 'Custom' && (
                  <span className="text-gray-300">/month</span>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-gray-300">
                    <span className="text-green-400">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>

              <Link href="/signup">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`
                    w-full py-3 rounded-xl font-semibold transition-all
                    ${plan.highlighted
                      ? 'bg-white text-purple-600 hover:bg-gray-100'
                      : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:opacity-90'
                    }
                  `}
                >
                  {plan.cta}
                </motion.button>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### 5. CTA Section
```tsx
'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function CTA() {
  return (
    <section className="py-24 bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-96 h-96 bg-white rounded-full blur-3xl opacity-10"
            animate={{
              x: [Math.random() * 200, Math.random() * -200],
              y: [Math.random() * 200, Math.random() * -200],
            }}
            transition={{
              duration: 15 + i * 3,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Ready to Transform Your Workflow?
          </h2>

          <p className="text-xl text-gray-300 mb-8">
            Join thousands of professionals who are already achieving more with AI-powered task management.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-10 py-5 bg-white text-purple-600 text-lg font-bold rounded-xl shadow-2xl hover:bg-gray-100 transition-colors"
              >
                Get Started Free
              </motion.button>
            </Link>

            <Link href="/contact">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-10 py-5 backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 text-white text-lg font-bold rounded-xl hover:bg-opacity-20 transition-all"
              >
                Contact Sales
              </motion.button>
            </Link>
          </div>

          <p className="text-gray-400 mt-6">
            No credit card required • Free 14-day trial • Cancel anytime
          </p>
        </motion.div>
      </div>
    </section>
  )
}
```

## Best Practices
- Clear value proposition in hero section
- Strong, action-oriented CTAs
- Social proof (testimonials, logos, stats)
- Benefit-focused copy, not feature-focused
- Mobile-first responsive design
- Fast loading times (<3s)
- SEO optimization (meta tags, structured data)
- A/B testing different headlines and CTAs
- Clear pricing with no hidden fees
- Trust signals (security badges, certifications)

## Conversion Optimization
- Above-the-fold CTA
- Multiple CTAs throughout page
- Reduce friction (no forms if possible)
- Urgency and scarcity (limited time offers)
- Exit-intent popups
- Live chat support
- Video demonstrations
- Money-back guarantee

## Output
- High-converting landing pages
- Compelling copy and design
- 3D effects and animations
- Mobile-responsive layouts
- SEO-optimized structure
