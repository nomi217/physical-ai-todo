# Phase 0: Technical Research - Phase II

**Feature**: Phase II - Full-Stack Web Application + Multi-language AI
**Date**: 2025-12-07
**Status**: Complete

## Overview

This document contains research findings for all technical decisions required for Phase II implementation. Each section follows the format: Decision → Rationale → Alternatives → Implementation → Risks.

---

## 1. Neon DB Setup & Connection

### Question
How to set up Neon DB and connect from FastAPI with SQLModel?

### Decision
Use **Neon DB Serverless PostgreSQL** with **asyncpg** driver via SQLModel.

### Rationale
- **Serverless**: No server management, auto-scaling, pay-per-use
- **PostgreSQL**: Full SQL support, ACID compliance, proven reliability
- **asyncpg**: Fastest PostgreSQL driver for Python, async/await support
- **SQLModel Integration**: Native async support, type-safe queries
- **Free Tier**: Sufficient for development and hackathon demo (512 MB storage, 0.5 vCPU)

### Alternatives Considered
1. **Local PostgreSQL**: More setup, no cloud hosting, not portable
2. **Supabase**: Good option but Neon has better FastAPI integration docs
3. **PlanetScale (MySQL)**: Different SQL dialect, less SQLModel examples
4. **psycopg2**: Synchronous only, slower than asyncpg

### Implementation

#### Setup Steps
1. **Create Neon DB Account**: https://neon.tech
2. **Create Project**: Get connection string from dashboard
3. **Connection String Format**:
   ```
   postgresql+asyncpg://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
   ```

#### FastAPI Integration (backend/app/database.py)
```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Dependency for routes
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

#### Environment Variables (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.neon.tech/dbname?sslmode=require
```

### Risks & Mitigation
- **Risk**: Neon DB free tier limits (512 MB storage, 0.5 vCPU)
  - **Mitigation**: Monitor usage, upgrade if needed ($19/month)
- **Risk**: Connection pool exhaustion
  - **Mitigation**: Configure pool size, implement connection retry logic
- **Risk**: SSL certificate issues
  - **Mitigation**: Always use `?sslmode=require` in connection string

---

## 2. Multi-language Implementation (6 Languages)

### Question
Best approach for 6-language support (EN, UR, AR, ES, FR, DE) in Next.js + FastAPI?

### Decision
Use **next-i18next** (frontend) + **Python gettext/custom JSON** (backend) with **RTL support** for Arabic/Urdu.

### Rationale
- **next-i18next**: Industry standard for Next.js i18n, built on i18next
- **JSON translation files**: Easy to manage, version control friendly
- **Server-side + Client-side**: Works with Next.js App Router
- **RTL Support**: Built-in Tailwind CSS directionality (`dir="rtl"`)
- **Language Detection**: Automatic from browser headers + manual switcher

### Alternatives Considered
1. **next-intl**: Newer, less mature, fewer examples
2. **react-i18next only**: No Next.js SSR optimization
3. **Custom solution**: Reinventing the wheel, error-prone
4. **Google Translate API**: Runtime translation, costs, latency

### Implementation

#### Frontend Structure
```
frontend/
├── public/locales/
│   ├── en/
│   │   ├── common.json
│   │   └── tasks.json
│   ├── ur/
│   ├── ar/
│   ├── es/
│   ├── fr/
│   └── de/
├── next-i18next.config.js
└── app/
    └── [locale]/
        └── page.tsx
```

#### Translation File Format (public/locales/en/common.json)
```json
{
  "app": {
    "title": "Todo App",
    "subtitle": "Manage your tasks efficiently"
  },
  "actions": {
    "add": "Add Task",
    "edit": "Edit",
    "delete": "Delete",
    "complete": "Mark Complete"
  },
  "priority": {
    "high": "High",
    "medium": "Medium",
    "low": "Low"
  }
}
```

#### Next.js Configuration (next-i18next.config.js)
```javascript
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur', 'ar', 'es', 'fr', 'de'],
  },
  localePath: './public/locales',
  reloadOnPrerender: process.env.NODE_ENV === 'development',
}
```

#### RTL Support (Tailwind CSS)
```typescript
// app/layout.tsx
export default function RootLayout({ children, params }: Props) {
  const { locale } = params
  const isRTL = ['ar', 'ur'].includes(locale)

  return (
    <html lang={locale} dir={isRTL ? 'rtl' : 'ltr'}>
      <body className={isRTL ? 'font-arabic' : 'font-sans'}>
        {children}
      </body>
    </html>
  )
}
```

#### Backend Translation (Simple JSON approach)
```python
# backend/app/services/translation.py
import json
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"

def load_translations(lang: str = "en") -> dict:
    file_path = TRANSLATIONS_DIR / f"{lang}.json"
    if not file_path.exists():
        file_path = TRANSLATIONS_DIR / "en.json"
    with open(file_path) as f:
        return json.load(f)

def translate(key: str, lang: str = "en") -> str:
    translations = load_translations(lang)
    return translations.get(key, key)
```

### Risks & Mitigation
- **Risk**: Translation quality (auto-translate vs native speakers)
  - **Mitigation**: Start with English, use Claude API for initial translations, refine with native speakers if time permits
- **Risk**: RTL layout bugs (CSS breaking)
  - **Mitigation**: Test early, use Tailwind's RTL-aware utilities (`ltr:`, `rtl:`)
- **Risk**: Missing translations (keys not defined)
  - **Mitigation**: Fallback to English, log missing keys

---

## 3. Voice Recognition

### Question
Web Speech API support across browsers and languages? Fallback strategies?

### Decision
Use **Web Speech API** (browser native) with **graceful degradation** for unsupported browsers/languages.

### Rationale
- **Free**: No API costs, runs in browser
- **Real-time**: Low latency, instant transcription
- **Multi-language**: Supports 50+ languages including our 6 target languages
- **Browser Support**: Chrome/Edge (excellent), Safari (good), Firefox (limited)
- **No Backend**: Reduces server load, simpler architecture

### Alternatives Considered
1. **OpenAI Whisper API**: $0.006/minute, requires audio upload, 200ms+ latency
2. **Google Cloud Speech-to-Text**: $0.006/15sec, requires API key, costs add up
3. **Azure Speech**: Similar pricing, more complex setup
4. **AssemblyAI**: Good accuracy but costs

### Implementation

#### Browser Support Matrix
| Browser | English | Urdu | Arabic | Spanish | French | German |
|---------|---------|------|--------|---------|--------|--------|
| Chrome  | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edge    | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Safari  | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Firefox | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

#### React Hook (frontend/hooks/useVoice.ts)
```typescript
import { useState, useEffect } from 'react'

interface VoiceRecognition {
  transcript: string
  isListening: boolean
  startListening: () => void
  stopListening: () => void
  error: string | null
}

export function useVoice(language: string = 'en-US'): VoiceRecognition {
  const [transcript, setTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recognition, setRecognition] = useState<any>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setError('Speech recognition not supported in this browser')
      return
    }

    const recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = false
    recognitionInstance.interimResults = false
    recognitionInstance.lang = getLanguageCode(language)

    recognitionInstance.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      setTranscript(transcript)
      setIsListening(false)
    }

    recognitionInstance.onerror = (event: any) => {
      setError(event.error)
      setIsListening(false)
    }

    setRecognition(recognitionInstance)
  }, [language])

  const startListening = () => {
    if (!recognition) return
    setTranscript('')
    setError(null)
    setIsListening(true)
    recognition.start()
  }

  const stopListening = () => {
    if (!recognition) return
    recognition.stop()
    setIsListening(false)
  }

  return { transcript, isListening, startListening, stopListening, error }
}

function getLanguageCode(locale: string): string {
  const codes: Record<string, string> = {
    'en': 'en-US',
    'ur': 'ur-PK',
    'ar': 'ar-SA',
    'es': 'es-ES',
    'fr': 'fr-FR',
    'de': 'de-DE',
  }
  return codes[locale] || 'en-US'
}
```

#### Voice Command Component
```typescript
'use client'

import { useVoice } from '@/hooks/useVoice'
import { MicrophoneIcon } from '@heroicons/react/24/outline'

export function VoiceInput({ onCommand, language }: Props) {
  const { transcript, isListening, startListening, error } = useVoice(language)

  useEffect(() => {
    if (transcript) {
      onCommand(transcript) // Parse and execute command
    }
  }, [transcript])

  return (
    <button
      onClick={startListening}
      disabled={isListening}
      className={`rounded-full p-3 ${isListening ? 'bg-red-500 animate-pulse' : 'bg-blue-500'}`}
    >
      <MicrophoneIcon className="h-6 w-6 text-white" />
    </button>
  )
}
```

### Risks & Mitigation
- **Risk**: Browser compatibility (Firefox limited support)
  - **Mitigation**: Show "unsupported browser" message, suggest Chrome/Edge
- **Risk**: Language accuracy varies (Urdu < English)
  - **Mitigation**: Show transcription for user confirmation before executing
- **Risk**: Microphone permissions denied
  - **Mitigation**: Clear UI prompts, explain why permission needed

---

## 4. Claude AI Integration

### Question
How to integrate Claude API for chatbot in FastAPI with streaming, rate limiting, and multi-language?

### Decision
Use **Anthropic Python SDK** with **streaming responses** and **Redis-based rate limiting**.

### Rationale
- **Official SDK**: Well-maintained, type-safe, best practices
- **Streaming**: Better UX, progressive responses, lower perceived latency
- **Claude 3.5 Sonnet**: Best balance of speed, intelligence, cost ($3/MTok in, $15/MTok out)
- **Multi-language**: Claude natively understands all 6 target languages
- **Rate Limiting**: Prevent abuse, control costs

### Alternatives Considered
1. **OpenAI GPT-4**: More expensive ($10/MTok in, $30/MTok out), similar capability
2. **GPT-3.5 Turbo**: Cheaper but less capable for complex queries
3. **Open-source LLMs (Llama, Mistral)**: Free but requires hosting, GPU, lower quality
4. **No streaming**: Simpler but worse UX for long responses

### Implementation

#### Backend Service (backend/app/services/ai_service.py)
```python
import anthropic
import os
from typing import AsyncGenerator

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def chat_with_claude(
    message: str,
    language: str = "en",
    context: list[dict] | None = None
) -> AsyncGenerator[str, None]:
    """Stream chat response from Claude"""

    system_prompt = get_system_prompt(language)
    messages = context or []
    messages.append({"role": "user", "content": message})

    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.7,
        system=system_prompt,
        messages=messages
    ) as stream:
        async for text in stream.text_stream:
            yield text

def get_system_prompt(language: str) -> str:
    """System prompt for task management assistant"""
    lang_instruction = {
        "en": "Respond in English",
        "ur": "Respond in Urdu (اردو میں جواب دیں)",
        "ar": "Respond in Arabic (أجب بالعربية)",
        "es": "Respond in Spanish (Responde en español)",
        "fr": "Respond in French (Répondez en français)",
        "de": "Respond in German (Antworte auf Deutsch)",
    }.get(language, "Respond in English")

    return f"""You are a helpful task management assistant. {lang_instruction}.

Your capabilities:
- Help users manage their todo tasks
- Provide intelligent suggestions for priorities and tags
- Answer questions about their tasks
- Parse natural language task creation requests

Keep responses concise and actionable. Focus on helping users be productive."""
```

#### FastAPI Route (backend/app/routes/chat.py)
```python
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.services.ai_service import chat_with_claude

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/message")
async def send_message(
    content: str,
    language: str = "en",
    # session: AsyncSession = Depends(get_session)
):
    """Stream AI response"""

    # Rate limiting (TODO: implement with Redis)
    # await check_rate_limit(user_id)

    async def generate():
        async for chunk in chat_with_claude(content, language):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

#### Frontend Chat Component (frontend/components/ChatBot.tsx)
```typescript
'use client'

import { useState } from 'react'

export function ChatBot({ language }: { language: string }) {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: input, language })
      })

      const reader = response.body?.getReader()
      let assistantMessage = ''

      while (true) {
        const { done, value } = await reader!.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            assistantMessage += line.slice(6)
            setMessages(prev => {
              const updated = [...prev]
              const lastMsg = updated[updated.length - 1]
              if (lastMsg?.role === 'assistant') {
                lastMsg.content = assistantMessage
              } else {
                updated.push({ role: 'assistant', content: assistantMessage })
              }
              return updated
            })
          }
        }
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-96 border rounded-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`rounded-lg px-4 py-2 max-w-[80%] ${
              msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t p-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className="flex-1 rounded-lg border px-4 py-2"
          placeholder="Ask about your tasks..."
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  )
}
```

### Risks & Mitigation
- **Risk**: API costs ($3-15 per 1M tokens)
  - **Mitigation**: Implement rate limiting (10 messages/user/hour), cache responses, use smaller context
- **Risk**: API latency (500ms-2s)
  - **Mitigation**: Use streaming for progressive UX, show loading indicators
- **Risk**: API quota limits
  - **Mitigation**: Monitor usage, implement graceful fallback ("AI temporarily unavailable")

---

## 5. Deployment Strategy

### Question
Best way to deploy Next.js + FastAPI + Neon DB for hackathon demo?

### Decision
- **Frontend**: **Vercel** (Next.js native hosting)
- **Backend**: **Railway** or **Render** (FastAPI containerized)
- **Database**: **Neon DB** (already cloud-hosted)

### Rationale
- **Vercel**: Zero-config Next.js deployment, auto-preview URLs, free tier
- **Railway**: Simple Docker deployment, $5/month, good Python support
- **Render**: Similar to Railway, free tier available (slower cold starts)
- **Neon DB**: Already cloud-hosted, no deployment needed

### Alternatives Considered
1. **All on Vercel**: Can't run FastAPI on Vercel (serverless functions only)
2. **AWS EC2**: Overkill, requires server management, not free
3. **Heroku**: Deprecated free tier, more expensive
4. **Docker + VPS**: More work, not necessary for demo

### Implementation

#### Frontend Deployment (Vercel)
1. **Connect GitHub**: Auto-deploy on push
2. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-xxx
   ```
3. **Build Command**: `npm run build`
4. **Output Directory**: `.next`

#### Backend Deployment (Railway)

**Dockerfile** (backend/Dockerfile):
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables**:
```
DATABASE_URL=postgresql+asyncpg://...@neon.tech/...
ANTHROPIC_API_KEY=sk-ant-xxx
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

#### docker-compose.yml (Local Development)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
```

### Risks & Mitigation
- **Risk**: Railway free tier insufficient (512MB RAM)
  - **Mitigation**: Use $5/month Hobby plan if needed
- **Risk**: Cold starts (Render free tier sleeps after 15min inactivity)
  - **Mitigation**: Use Railway instead, or keep-alive ping service
- **Risk**: CORS issues between Vercel and Railway
  - **Mitigation**: Configure CORS properly, test early

---

## Summary of Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Database | Neon DB (PostgreSQL) | Serverless, free tier, async support |
| Backend Framework | FastAPI + SQLModel | Modern, fast, type-safe, async |
| Frontend Framework | Next.js 14 + TypeScript | SSR, App Router, best React framework |
| Multi-language | next-i18next + JSON | Industry standard, RTL support |
| Voice Recognition | Web Speech API | Free, real-time, browser-native |
| AI Chatbot | Claude 3.5 Sonnet (Anthropic) | Best quality/cost, multi-language |
| Frontend Hosting | Vercel | Zero-config, free, fast |
| Backend Hosting | Railway | Simple, $5/month, Docker support |

## Next Steps

1. **Create data-model.md**: Define SQLModel schemas
2. **Create contracts/**: Define API OpenAPI spec
3. **Create quickstart.md**: Setup instructions
4. **Update agent context**: Run update script
5. **Generate tasks**: Run `/sp.tasks`
6. **Start implementation**: Run `/sp.implement`

---

**Research Status**: ✅ Complete
**All NEEDS CLARIFICATION resolved**: Yes
**Ready for Phase 1 Design**: Yes
