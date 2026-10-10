import { useEffect, useRef, useState } from 'react'
import { api } from '../lib/api.js'
import { useQuestion } from '../hooks/useQuestion.js'
import { Button } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import AnswerRecorder from '../components/AnswerRecorder.jsx'
import FeedbackReport, { FeedbackLoading } from '../components/FeedbackReport.jsx'
import GlowBackdrop from '../components/GlowBackdrop.jsx'
import TipCard from '../components/TipCard.jsx'

const DEFAULT_ROLES = [{ id: 'hr', label: 'HR round' }]

// Remember the last interview type in this browser (a small convenience, so it's
// fine if storage is unavailable, e.g. in private browsing)
function savedRole() {
  try {
    return localStorage.getItem('practice-role') || 'hr'
  } catch {
    return 'hr'
  }
}

export default function Practice() {
  const [roles, setRoles] = useState(DEFAULT_ROLES)
  const [role, setRole] = useState(savedRole)
  const { question, loading, error, next } = useQuestion(role)
  const [number, setNumber] = useState(1)

  const [feedback, setFeedback] = useState(null)
  const [scoring, setScoring] = useState(false)
  const [feedbackError, setFeedbackError] = useState('')
  const lastTranscript = useRef('')
  // Each scoring request gets a number. If the user moves on before the answer
  // comes back, the old (now outdated) response is ignored.
  const requestId = useRef(0)
  const feedbackRef = useRef(null)

  useEffect(() => {
    api('/roles')
      .then((list) => {
        setRoles(list)
        if (!list.some((r) => r.id === role)) setRole('hr')
      })
      .catch(() => {}) // keep the default role if this fails
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function clearFeedback() {
    requestId.current += 1
    setFeedback(null)
    setFeedbackError('')
    setScoring(false)
  }

  async function scoreAnswer(transcript) {
    const id = ++requestId.current
    lastTranscript.current = transcript
    setFeedback(null)
    setFeedbackError('')
    setScoring(true)
    // Scroll down so the user sees the feedback arrive
    setTimeout(() => feedbackRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
    try {
      const result = await api('/answers/evaluate', {
        method: 'POST',
        body: { question, role, transcript },
      })
      if (id === requestId.current) setFeedback(result)
    } catch (err) {
      if (id === requestId.current) setFeedbackError({ message: err.message, canRetry: err.status !== 400 })
    } finally {
      if (id === requestId.current) setScoring(false)
    }
  }

  function nextQuestion() {
    clearFeedback()
    setNumber(number + 1) // also gives a fresh recorder (see key below)
    next()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function changeRole(id) {
    if (id === role) return
    clearFeedback()
    setRole(id)
    setNumber(1)
    try {
      localStorage.setItem('practice-role', id)
    } catch {
      // storage unavailable: nothing to do
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Practice</h1>
      <p className="mt-2 text-muted">
        Pick an interview type, read the question, then record your answer. Aim for one to two minutes.
      </p>

      {/* radiogroup: screen readers announce these as "one of four options" */}
      <div className="mt-6" role="radiogroup" aria-label="Interview type">
        <div className="flex flex-wrap gap-2">
          {roles.map((r) => {
            const active = r.id === role
            return (
              <button
                key={r.id}
                role="radio"
                aria-checked={active}
                onClick={() => changeRole(r.id)}
                className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-colors ${
                  active
                    ? 'border-brand bg-brand text-white shadow-[0_6px_18px_-8px_var(--color-brand)]'
                    : 'border-line bg-white text-ink hover:border-ink/30'
                }`}
              >
                {r.label}
              </button>
            )
          })}
        </div>
      </div>

      <section className="relative isolate mt-6 overflow-hidden rounded-2xl bg-night p-6 text-white sm:p-10">
        <GlowBackdrop />
        <div className="relative">
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-white/50">Question {number}</p>
            <Button variant="outlineLight" size="sm" onClick={nextQuestion} disabled={loading}>
              Next question
            </Button>
          </div>

          <p
            aria-live="polite"
            className="mt-3 min-h-[2.4em] font-serif text-3xl leading-[1.2] tracking-tight text-balance sm:text-4xl"
          >
            {question ? (
              <span key={question} className="block animate-fade-up">&ldquo;{question}&rdquo;</span>
            ) : loading ? (
              <span className="text-white/50">Getting a question…</span>
            ) : null}
          </p>
          {error && <Alert dark className="mt-4">{error}</Alert>}

          <div className="mt-8 border-t border-white/10 pt-8">
            {/* key: a new question or role gives a fresh recorder (and turns the old mic off) */}
            <AnswerRecorder key={`${role}-${number}`} onTranscript={scoreAnswer} onReset={clearFeedback} />
          </div>
        </div>
      </section>

      {/* Feedback appears here once the transcript is ready */}
      <div ref={feedbackRef} className="scroll-mt-6">
        {scoring && <div className="mt-6"><FeedbackLoading /></div>}
        {feedbackError && (
          <div className="mt-6 rounded-2xl border border-line bg-white p-6 sm:p-8">
            <Alert>{feedbackError.message}</Alert>
            {/* 400 = a problem with the answer itself (e.g. too short), so retrying won't help */}
            {feedbackError.canRetry && (
              <Button variant="secondary" className="mt-4" onClick={() => scoreAnswer(lastTranscript.current)}>
                Try scoring again
              </Button>
            )}
          </div>
        )}
        {feedback && <div className="mt-6"><FeedbackReport feedback={feedback} onNext={nextQuestion} /></div>}
      </div>

      <TipCard className="mt-6" />
    </div>
  )
}
