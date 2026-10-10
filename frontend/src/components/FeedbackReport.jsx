import { useEffect, useState } from 'react'
import { Button } from './ui/Button.jsx'
import Waveform from './Waveform.jsx'

/*
  Shows the AI interviewer's feedback:
  overall score + verdict, three score bars, what worked / what to improve,
  and a stronger version of the answer.
*/
export default function FeedbackReport({ feedback, onNext }) {
  const criteria = [
    { label: 'Relevance', ...feedback.relevance },
    { label: 'Structure', ...feedback.structure },
    { label: 'Clarity', ...feedback.clarity },
  ]

  return (
    <section
      aria-labelledby="feedback-title"
      className="animate-fade-up rounded-2xl border border-line bg-white p-6 sm:p-10"
    >
      <h2 id="feedback-title" className="sr-only">Feedback on your answer</h2>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-8">
        <div className="shrink-0">
          <p className="font-serif text-7xl leading-none tracking-tight" aria-label={`Content score ${feedback.overall} out of 10`}>
            {feedback.overall}
            <span className="ml-1 font-sans text-xl text-muted">/10</span>
          </p>
          <p className="mt-2 text-sm text-muted">Content score</p>
        </div>
        <p className="text-lg leading-relaxed">{feedback.summary}</p>
      </div>

      <div className="mt-8 space-y-6 border-t border-line pt-8">
        {criteria.map((criterion, i) => (
          <ScoreBar key={criterion.label} {...criterion} delay={i * 150} />
        ))}
      </div>

      <div className="mt-8 grid gap-8 border-t border-line pt-8 sm:grid-cols-2">
        <FeedbackList
          title="What worked"
          items={feedback.strengths}
          dotClass="bg-brand"
          empty="Nothing stood out in this answer yet. Start with the suggestions under What to improve."
        />
        <FeedbackList title="What to improve" items={feedback.improvements} dotClass="border-2 border-ink/40" />
      </div>

      <div className="mt-8 border-t border-line pt-8">
        <h3 className="text-lg font-semibold">A stronger answer</h3>
        <p className="mt-1 text-sm text-muted">
          Built from what you said. Replace the parts in brackets with your own details.
        </p>
        <blockquote className="mt-5 border-l-2 border-brand pl-5 font-serif text-xl leading-relaxed">
          <Placeholders text={feedback.sample_answer} />
        </blockquote>
      </div>

      <Button onClick={onNext} className="mt-10">Try another question</Button>
    </section>
  )
}

// A bar that fills up to the score when it first appears
function ScoreBar({ label, score, comment, delay }) {
  const [filled, setFilled] = useState(false)
  useEffect(() => {
    const timer = setTimeout(() => setFilled(true), 60 + delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <div>
      <div className="flex items-baseline justify-between gap-4">
        <p className="font-semibold">{label}</p>
        <p className="text-sm text-muted tabular-nums">
          <span className="text-base font-semibold text-ink">{score}</span> / 10
        </p>
      </div>
      <div
        className="mt-2 h-2 rounded-full bg-line"
        role="meter"
        aria-label={`${label} score`}
        aria-valuemin={1}
        aria-valuemax={10}
        aria-valuenow={score}
      >
        <div
          className="h-full rounded-full bg-brand transition-[width] duration-700 ease-out"
          style={{ width: filled ? `${score * 10}%` : '0%' }}
        />
      </div>
      <p className="mt-2 text-sm leading-relaxed text-muted">{comment}</p>
    </div>
  )
}

function FeedbackList({ title, items, dotClass, empty }) {
  return (
    <div>
      <h3 className="text-lg font-semibold">{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-3">
          {items.map((item) => (
            <li key={item} className="flex gap-3 leading-relaxed">
              <span className={`mt-2 size-2 shrink-0 rounded-full ${dotClass}`} aria-hidden="true" />
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 leading-relaxed text-muted">{empty}</p>
      )}
    </div>
  )
}

// Highlights "[like this]" placeholders the student should fill in
function Placeholders({ text }) {
  return text.split(/(\[[^\]]+\])/g).map((part, i) =>
    part.startsWith('[') && part.endsWith(']') ? (
      <span key={i} className="rounded bg-brand-soft px-1 text-brand">{part}</span>
    ) : (
      <span key={i}>{part}</span>
    )
  )
}

export function FeedbackLoading() {
  return (
    <section className="rounded-2xl border border-line bg-white p-6 sm:p-10" role="status">
      <div className="flex items-center gap-4">
        <Waveform bars={14} tone="brand" />
        <p className="font-semibold">Scoring your answer…</p>
      </div>
      <p className="mt-2 text-sm text-muted">The AI interviewer is reading your answer. This takes a few seconds.</p>
      <div className="mt-8 space-y-4" aria-hidden="true">
        {['60%', '90%', '75%', '85%'].map((width) => (
          <div key={width} className="h-3 animate-pulse rounded bg-line" style={{ width }} />
        ))}
      </div>
    </section>
  )
}
