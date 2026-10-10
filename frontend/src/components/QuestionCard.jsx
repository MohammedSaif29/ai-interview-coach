import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../lib/api.js'
import { Button } from './ui/Button.jsx'
import { Alert } from './ui/Alert.jsx'

// Shows an interview question from the backend, with a "Next question" button.
export default function QuestionCard() {
  const [question, setQuestion] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  // useRef: remembers a value between renders without causing a re-render
  const current = useRef(null)

  const loadQuestion = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      // The backend picks randomly, so it can repeat. Try a few times for a new one.
      let data
      for (let attempt = 0; attempt < 3; attempt++) {
        data = await api('/question')
        if (data.question !== current.current) break
      }
      current.current = data.question
      setQuestion(data.question)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadQuestion()
  }, [loadQuestion])

  return (
    <div>
      {/* aria-live: screen readers announce the new question when it changes */}
      <p
        aria-live="polite"
        className="min-h-[2.5em] font-serif text-3xl leading-[1.2] tracking-tight text-balance sm:text-[2.6rem]"
      >
        {question ? (
          // key={question}: React re-creates this span for each new question,
          // which replays the fade-in animation
          <span key={question} className="block animate-fade-up">&ldquo;{question}&rdquo;</span>
        ) : loading ? (
          <span className="text-muted">Getting a question…</span>
        ) : null}
      </p>

      {error && <Alert className="mt-4">{error}</Alert>}

      <Button onClick={loadQuestion} disabled={loading} className="mt-6">
        {loading && question ? 'Getting a question…' : 'Next question'}
      </Button>
    </div>
  )
}
