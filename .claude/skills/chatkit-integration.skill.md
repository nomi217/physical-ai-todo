# OpenAI ChatKit Integration Skill

## Purpose
Integrate OpenAI ChatKit (UI component library) for building conversational chat interfaces in Next.js applications.

## When to Use
- Building AI chatbot frontends
- Creating messaging interfaces
- Implementing conversational UIs
- Rapid prototyping of chat experiences

## Inputs Required
- **Backend Chat API**: Endpoint for sending messages
- **Authentication**: User auth tokens
- **Styling**: Theme customization

## Process

### 1. Install Dependencies
```bash
npm install @chatscope/chat-ui-kit-react
npm install @chatscope/chat-ui-kit-styles
```

### 2. Basic Chat Component
```tsx
'use client'
import { useState, useEffect } from 'use'
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from '@chatscope/chat-ui-kit-react'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export default function AIChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState<number | null>(null)

  const sendMessage = async (message: string) => {
    // Add user message immediately
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    try {
      // Call backend chat API
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          conversation_id: conversationId,
          message
        })
      })

      if (!response.ok) {
        throw new Error('Chat request failed')
      }

      const data = await response.json()

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Chat error:', error)

      // Add error message
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: "Sorry, I'm having trouble right now. Please try again.",
          timestamp: new Date().toISOString()
        }
      ])
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="h-screen bg-gray-50">
      <MainContainer>
        <ChatContainer>
          <MessageList
            typingIndicator={
              isTyping ? <TypingIndicator content="AI is typing..." /> : null
            }
          >
            {messages.map((msg) => (
              <Message
                key={msg.id}
                model={{
                  message: msg.content,
                  sentTime: msg.timestamp,
                  sender: msg.role === 'user' ? 'You' : 'AI Assistant',
                  direction: msg.role === 'user' ? 'outgoing' : 'incoming',
                  position: 'single'
                }}
              />
            ))}
          </MessageList>

          <MessageInput
            placeholder="Type your message..."
            onSend={sendMessage}
            attachButton={false}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  )
}
```

### 3. Custom Styled Chat with Glassmorphism
```tsx
'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function GlassChatbot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<number | null>(null)

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          conversation_id: conversationId,
          message: input
        })
      })

      const data = await response.json()

      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 p-4">
      <div className="max-w-4xl mx-auto h-[90vh] flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-t-2xl p-4"
        >
          <h2 className="text-2xl font-bold text-white">AI Task Assistant</h2>
          <p className="text-white/70 text-sm">Manage your tasks with natural language</p>
        </motion.div>

        {/* Messages */}
        <div className="flex-1 backdrop-blur-xl bg-white/5 border-x border-white/20 p-4 overflow-y-auto">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`mb-4 flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`
                    max-w-[70%] p-4 rounded-2xl
                    ${message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                      : 'backdrop-blur-xl bg-white/10 border border-white/20 text-white'
                    }
                  `}
                >
                  <p>{message.content}</p>
                  <span className="text-xs opacity-70 mt-2 block">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-4">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Input */}
        <form
          onSubmit={sendMessage}
          className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-b-2xl p-4"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="
                flex-1 px-4 py-3 rounded-xl
                backdrop-blur-xl bg-white/10 border border-white/20
                text-white placeholder:text-white/50
                focus:outline-none focus:ring-2 focus:ring-white/30
                disabled:opacity-50
              "
            />

            <motion.button
              type="submit"
              disabled={isLoading || !input.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="
                px-6 py-3 rounded-xl font-semibold
                bg-gradient-to-r from-blue-500 to-purple-600
                text-white
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              Send
            </motion.button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

### 4. Conversation History Sidebar
```tsx
'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface Conversation {
  id: number
  title: string
  last_message: string
  updated_at: string
}

export default function ConversationSidebar({
  currentConversationId,
  onSelectConversation
}: {
  currentConversationId: number | null
  onSelectConversation: (id: number) => void
}) {
  const [conversations, setConversations] = useState<Conversation[]>([])

  useEffect(() => {
    fetchConversations()
  }, [])

  const fetchConversations = async () => {
    try {
      const response = await fetch('/api/v1/conversations', {
        credentials: 'include'
      })

      const data = await response.json()
      setConversations(data.conversations)
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    }
  }

  const createNewConversation = () => {
    onSelectConversation(null)
  }

  return (
    <div className="w-64 backdrop-blur-xl bg-white/5 border-r border-white/20 p-4">
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={createNewConversation}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-xl font-semibold mb-4"
      >
        + New Chat
      </motion.button>

      <div className="space-y-2">
        {conversations.map((conv) => (
          <motion.div
            key={conv.id}
            whileHover={{ scale: 1.02 }}
            onClick={() => onSelectConversation(conv.id)}
            className={`
              p-3 rounded-xl cursor-pointer transition-all
              ${currentConversationId === conv.id
                ? 'bg-white/20 border border-white/30'
                : 'bg-white/5 border border-white/10 hover:bg-white/10'
              }
            `}
          >
            <h4 className="text-white font-semibold text-sm truncate">
              {conv.title}
            </h4>
            <p className="text-white/70 text-xs truncate mt-1">
              {conv.last_message}
            </p>
            <span className="text-white/50 text-xs">
              {new Date(conv.updated_at).toLocaleDateString()}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
```

### 5. Suggested Actions/Quick Replies
```tsx
'use client'

const suggestedActions = [
  { label: "📝 Add a task", action: "Add a task to" },
  { label: "📋 Show tasks", action: "Show me all my tasks" },
  { label: "✅ Complete task", action: "Mark task as complete" },
  { label: "🗑️ Delete task", action: "Delete a task" }
]

export default function QuickActions({
  onActionClick
}: {
  onActionClick: (action: string) => void
}) {
  return (
    <div className="flex gap-2 flex-wrap mb-4">
      {suggestedActions.map((item, index) => (
        <motion.button
          key={index}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onActionClick(item.action)}
          className="
            px-4 py-2 rounded-xl text-sm
            backdrop-blur-xl bg-white/10 border border-white/20
            text-white hover:bg-white/20 transition-all
          "
        >
          {item.label}
        </motion.button>
      ))}
    </div>
  )
}
```

### 6. Voice Input (Optional)
```tsx
'use client'
import { useState } from 'react'

export default function VoiceInput({
  onTranscript
}: {
  onTranscript: (text: string) => void
}) {
  const [isListening, setIsListening] = useState(false)

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported')
      return
    }

    const recognition = new (window as any).webkitSpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      onTranscript(transcript)
    }

    recognition.start()
  }

  return (
    <motion.button
      onClick={startListening}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className={`
        w-12 h-12 rounded-full
        flex items-center justify-center
        ${isListening
          ? 'bg-red-500 animate-pulse'
          : 'bg-gradient-to-r from-blue-500 to-purple-600'
        }
      `}
    >
      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16z" clipRule="evenodd" />
      </svg>
    </motion.button>
  )
}
```

### 7. Message Actions (Copy, Regenerate)
```tsx
'use client'

export default function MessageActions({
  message,
  onRegenerate
}: {
  message: Message
  onRegenerate: () => void
}) {
  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content)
  }

  if (message.role === 'user') return null

  return (
    <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button
        onClick={copyToClipboard}
        className="text-xs text-white/70 hover:text-white"
      >
        📋 Copy
      </button>

      <button
        onClick={onRegenerate}
        className="text-xs text-white/70 hover:text-white"
      >
        🔄 Regenerate
      </button>
    </div>
  )
}
```

## Best Practices

### UX Design
- Auto-scroll to latest message
- Show typing indicators
- Display timestamps
- Implement quick actions
- Add message animations

### Performance
- Virtualize long message lists
- Lazy load conversation history
- Debounce input
- Cache conversations locally
- Implement optimistic updates

### Accessibility
- Keyboard navigation support
- Screen reader friendly
- High contrast mode
- Focus management
- ARIA labels

### Error Handling
- Network error messages
- Retry failed messages
- Offline detection
- Rate limit warnings

## Output
- Complete chat UI
- Conversation management
- Real-time messaging
- Voice input support
- Quick actions and suggestions
