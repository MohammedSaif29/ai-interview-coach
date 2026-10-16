import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router'
import { useAuth } from '../context/AuthContext.jsx'
import { api, streamPost } from '../lib/api.js'
import { Button } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import MarkdownText from '../components/MarkdownText.jsx'
import Waveform from '../components/Waveform.jsx'

const SUGGESTIONS = [
  'What should I work on next?',
  'How do I answer “Tell me about yourself”?',
  'Make me a 7-day plan before my placement interviews',
  'How do I use the STAR method?',
]

export default function Coach() {
  const { user } = useAuth()
  const firstName = user.name.split(' ')[0]
  const [searchParams, setSearchParams] = useSearchParams()

  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [sendError, setSendError] = useState('')
  const [confirmingClear, setConfirmingClear] = useState(false)

  const scroller = useRef(null)
  const textarea = useRef(null)

  // Load the saved conversation
  useEffect(() => {
    api('/coach/messages')
      .then(setMessages)
      .catch((err) => setLoadError(err.message))
      .finally(() => setLoading(false))
  }, [])

  // Arrived from "Ask your coach" on the dashboard? Put that question in the box.
  useEffect(() => {
    const ask = searchParams.get('ask')
    if (ask) {
      setInput(ask)
      setSearchParams({}, { replace: true })
      textarea.current?.focus()
    }
  }, [searchParams, setSearchParams])

  // Keep the newest message in view
  useEffect(() => {
    const box = scroller.current
    if (box) box.scrollTop = box.scrollHeight
  }, [messages])

  // Grow the text box with its content (up to about 6 lines)
  useEffect(() => {
    const box = textarea.current
    if (!box) return
    box.style.height = 'auto'
    box.style.height = `${Math.min(box.scrollHeight, 160)}px`
  }, [input])

  async function send(text) {
    const content = text.trim()
    if (!content || streaming) return

    setSendError('')
    setInput('')
    setStreaming(true)
    // Show the question straight away, plus an empty reply that fills in as it streams
    setMessages((current) => [
      ...current,
      { id: `you-${Date.now()}`, role: 'user', content },
      { id: 'streaming', role: 'assistant', content: '' },
    ])

    try {
      await streamPost('/coach/messages', { content }, (piece) => {
        setMessages((current) =>
          current.map((m) => (m.id === 'streaming' ? { ...m, content: m.content + piece } : m))
        )
      })
      setMessages((current) => current.map((m) => (m.id === 'streaming' ? { ...m, id: `coach-${Date.now()}` } : m)))
    } catch (err) {
      // The server didn't save this question, so take it back off the screen and
      // put the text back in the box, ready to send again
      setMessages((current) => current.slice(0, -2))
      setInput(content)
      setSendError(err.message)
    } finally {
      setStreaming(false)
    }
  }

  function handleKeyDown(e) {
    // Enter sends; Shift + Enter makes a new line. isComposing: don't send mid-way
    // through typing with an input method (e.g. Hindi or Telugu keyboards).
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      send(input)
    }
  }

  async function clearChat() {
    try {
      await api('/coach/messages', { method: 'DELETE' })
      setMessages([])
    } catch (err) {
      setSendError(err.message)
    } finally {
      setConfirmingClear(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Coach</h1>
          <p className="mt-2 text-muted">Your interview and placement guide. It can see your practice scores.</p>
        </div>
        {messages.length > 0 && !streaming && (
          confirmingClear ? (
            <div className="flex items-center gap-2">
              <span className="text-sm">Clear all messages?</span>
              <Button size="sm" variant="danger" onClick={clearChat}>Clear</Button>
              <Button size="sm" variant="secondary" onClick={() => setConfirmingClear(false)}>Cancel</Button>
            </div>
          ) : (
            <button
              onClick={() => setConfirmingClear(true)}
              className="text-sm font-semibold text-muted underline-offset-4 hover:text-ink hover:underline"
            >
              Clear chat
            </button>
          )
        )}
      </div>

      <section className="mt-6 flex h-[calc(100dvh-17rem)] min-h-[26rem] flex-col overflow-hidden rounded-2xl border border-line bg-white lg:h-[calc(100dvh-15rem)]">
        {/* role="log": a live list of messages. aria-busy: screen readers wait until a reply finishes */}
        <div ref={scroller} role="log" aria-live="polite" aria-busy={streaming} className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
          {loading ? (
            <p className="text-center text-sm text-muted">Loading your conversation…</p>
          ) : loadError ? (
            <Alert>{loadError}</Alert>
          ) : messages.length === 0 ? (
            <div className="mx-auto max-w-md py-6 text-center">
              <CoachAvatar large />
              <p className="mt-5 font-serif text-2xl tracking-tight">Hi {firstName}, I'm your interview coach.</p>
              <p className="mt-2 text-sm leading-relaxed text-muted">
                Ask me anything about interviews, placements, coding rounds or your resume.
              </p>
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => send(suggestion)}
                    className="rounded-full border border-line px-3.5 py-1.5 text-left text-sm transition-colors hover:border-brand hover:text-brand"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((message) => (
                <Message key={message.id} message={message} />
              ))}
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
          className="border-t border-line p-3 sm:p-4"
        >
          {sendError && <Alert className="mb-3">{sendError}</Alert>}
          <div className="flex items-end gap-2">
            <label htmlFor="coach-input" className="sr-only">Message your coach</label>
            <textarea
              id="coach-input"
              ref={textarea}
              rows={1}
              maxLength={2000}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask your coach…"
              className="max-h-40 min-h-[2.75rem] flex-1 resize-none rounded-xl border border-line bg-white px-3.5 py-2.5 text-[15px] placeholder:text-muted/60 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/25"
            />
            <Button type="submit" disabled={streaming || !input.trim()} className="h-11">
              {streaming ? 'Replying…' : 'Send'}
            </Button>
          </div>
          <p className="mt-2 hidden text-xs text-muted sm:block">Enter to send. Shift + Enter for a new line.</p>
        </form>
      </section>
    </div>
  )
}

function Message({ message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-brand px-4 py-2.5 leading-relaxed text-white">
          {message.content}
        </div>
      </div>
    )
  }
  return (
    <div className="flex gap-3">
      <CoachAvatar />
      <div className="min-w-0 max-w-[85%] break-words rounded-2xl rounded-tl-md bg-paper px-4 py-3 leading-relaxed">
        {message.content ? (
          <MarkdownText text={message.content} />
        ) : (
          <span className="flex items-center gap-3 text-sm text-muted">
            <Waveform bars={10} tone="brand" className="h-5" />
            Thinking…
          </span>
        )}
      </div>
    </div>
  )
}

// The coach's picture: the app's sound-wave mark on the dark "booth" colour
function CoachAvatar({ large = false }) {
  return (
    <span
      className={`grid shrink-0 place-items-center rounded-xl bg-night shadow-[0_0_20px_-6px_var(--color-glow)] ${
        large ? 'mx-auto size-14' : 'size-8'
      }`}
      aria-hidden="true"
    >
      <svg width={large ? 24 : 15} height={large ? 24 : 15} viewBox="0 0 16 16" fill="var(--color-glow)">
        <rect x="1.5" y="5" width="3" height="6" rx="1.5" />
        <rect x="6.5" y="1.5" width="3" height="13" rx="1.5" />
        <rect x="11.5" y="4" width="3" height="8" rx="1.5" />
      </svg>
    </span>
  )
}
