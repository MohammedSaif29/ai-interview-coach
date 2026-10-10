import { useState } from 'react'
import { useQuestion } from '../hooks/useQuestion.js'
import { Button } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import AnswerRecorder from '../components/AnswerRecorder.jsx'
import GlowBackdrop from '../components/GlowBackdrop.jsx'
import TipCard from '../components/TipCard.jsx'

export default function Practice() {
  const { question, loading, error, next } = useQuestion()
  const [number, setNumber] = useState(1)

  function nextQuestion() {
    setNumber(number + 1) // also resets the recorder (see key below)
    next()
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Practice</h1>
      <p className="mt-2 text-muted">
        Read the question, take a breath, then record your answer. Aim for one to two minutes.
      </p>

      <section className="relative isolate mt-8 overflow-hidden rounded-2xl bg-night p-6 text-white sm:p-10">
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
            {/* key: a new question number gives a fresh recorder (and turns the old mic off) */}
            <AnswerRecorder key={number} />
          </div>
        </div>
      </section>

      <TipCard className="mt-6" />
    </div>
  )
}
