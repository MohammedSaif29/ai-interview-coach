import { useQuestion } from '../hooks/useQuestion.js'
import { Button } from './ui/Button.jsx'
import { Alert } from './ui/Alert.jsx'

// Shows an interview question with a "Next question" button (used on the landing page).
export default function QuestionCard() {
  const { question, loading, error, next } = useQuestion()

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

      <Button onClick={next} disabled={loading} className="mt-6">
        {loading && question ? 'Getting a question…' : 'Next question'}
      </Button>
    </div>
  )
}
