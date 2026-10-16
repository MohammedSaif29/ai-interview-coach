import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router'
import { api } from '../lib/api.js'
import { formatTime } from '../lib/format.js'
import { Button, TextButton } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import Waveform from '../components/Waveform.jsx'

const LETTERS = ['A', 'B', 'C', 'D']

/*
  One mock test. The same URL shows:
  - the test itself while it's in progress (with a timer), or
  - the marked result once it's submitted.
*/
export default function MockTest() {
  const { companyId, testId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  // Arrived straight from "Start the mock test"? The paper came with us, so no extra request.
  const passed = location.state?.paper
  const [data, setData] = useState(passed && String(passed.id) === testId ? passed : null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (data) return
    api(`/tests/${testId}`)
      .then(setData)
      .catch((err) => setError(err.message))
  }, [testId]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSubmitted(result) {
    setData(result)
    // Forget the paper we arrived with, so a refresh loads the marked result instead
    navigate(location.pathname, { replace: true, state: null })
  }

  if (error) return <Message title="Couldn't open this test" text={error} companyId={companyId} />
  if (!data) return <div className="mx-auto h-96 max-w-5xl animate-pulse rounded-2xl bg-line/60" aria-hidden="true" />
  if (data.status === 'expired') {
    return <Message title="Time ran out" text="This test wasn't submitted before the timer ended. Start a fresh one any time." companyId={companyId} />
  }
  if (data.status === 'submitted') return <Result result={data} />
  return <TestPaper paper={data} onSubmitted={handleSubmitted} />
}

function Message({ title, text, companyId }) {
  return (
    <div className="mx-auto max-w-xl rounded-2xl border border-line bg-white p-8 text-center">
      <p className="text-lg font-semibold">{title}</p>
      <p className="mt-2 text-muted">{text}</p>
      <Link to={`/companies/${companyId}`} className="mt-6 inline-block font-semibold text-brand underline-offset-4 hover:underline">
        Back to the company page
      </Link>
    </div>
  )
}

/* ====================== Taking the test ====================== */

// Answers are kept in sessionStorage too, so a refresh mid-test doesn't lose them.
// (Storage can be unavailable, e.g. in private browsing, so every access is wrapped.)
function loadSaved(id) {
  try {
    return JSON.parse(sessionStorage.getItem(`mock-${id}`)) || {}
  } catch {
    return {}
  }
}
function save(id, answers) {
  try {
    sessionStorage.setItem(`mock-${id}`, JSON.stringify(answers))
  } catch {
    // not critical
  }
}
function clearSaved(id) {
  try {
    sessionStorage.removeItem(`mock-${id}`)
  } catch {
    // not critical
  }
}

function TestPaper({ paper, onSubmitted }) {
  // One flat list of questions, each remembering its section
  const questions = useMemo(
    () => paper.sections.flatMap((s) => s.questions.map((q) => ({ ...q, section: s.name }))),
    [paper]
  )
  const [answers, setAnswers] = useState(() => loadSaved(paper.id))
  const [index, setIndex] = useState(0)
  const [remaining, setRemaining] = useState(() => secondsLeft(paper.deadline))
  const [confirming, setConfirming] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const answersRef = useRef(answers)
  const submittedRef = useRef(false)

  const question = questions[index]
  const answeredCount = questions.filter((q) => answers[q.id] != null).length

  const submit = useCallback(async (auto = false) => {
    if (submittedRef.current) return
    submittedRef.current = true
    setSubmitting(true)
    setError('')
    try {
      const result = await api(`/tests/${paper.id}/submit`, {
        method: 'POST',
        body: { answers: answersRef.current, auto_submitted: auto },
      })
      clearSaved(paper.id)
      window.scrollTo({ top: 0 })
      onSubmitted(result)
    } catch (err) {
      submittedRef.current = false
      setSubmitting(false)
      setError(err.message)
    }
  }, [paper.id, onSubmitted])

  // The timer: tick every second, and submit automatically at zero
  useEffect(() => {
    const timer = setInterval(() => {
      const left = secondsLeft(paper.deadline)
      setRemaining(left)
      if (left <= 0) {
        clearInterval(timer)
        submit(true)
      }
    }, 1000)
    return () => clearInterval(timer)
  }, [paper.deadline, submit])

  // Warn before closing the tab mid-test
  useEffect(() => {
    const warn = (event) => {
      if (!submittedRef.current) event.preventDefault()
    }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [])

  function choose(choice) {
    const next = { ...answers, [question.id]: choice }
    answersRef.current = next
    setAnswers(next)
    save(paper.id, next)
    setConfirming(false)
  }

  function clearChoice() {
    const next = { ...answers }
    delete next[question.id]
    answersRef.current = next
    setAnswers(next)
    save(paper.id, next)
  }

  const lowTime = remaining <= 60
  const unanswered = questions.length - answeredCount

  return (
    <div className="mx-auto max-w-5xl">
      {/* Sticky bar: test name, progress and the timer */}
      <div className="sticky top-[59px] z-10 -mx-4 mb-6 border-b border-line bg-paper/90 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6 lg:top-0 lg:-mx-10 lg:px-10">
        <div className="flex items-center justify-between gap-4">
          <div className="min-w-0">
            <p className="truncate font-semibold">{paper.company_name} mock test</p>
            <p className="text-sm text-muted">{answeredCount} of {questions.length} answered</p>
          </div>
          <div className="flex items-center gap-3">
            <p
              className={`rounded-lg px-3 py-1.5 font-semibold tabular-nums ${lowTime ? 'bg-mark/10 text-mark' : 'bg-night text-glow'}`}
              role="timer"
              aria-label={`${Math.floor(remaining / 60)} minutes ${remaining % 60} seconds left`}
            >
              {formatTime(Math.max(remaining, 0))}
            </p>
            <Button size="sm" onClick={() => (unanswered > 0 ? setConfirming(true) : submit())} disabled={submitting}>
              Submit
            </Button>
          </div>
        </div>
        <div className="mt-3 h-1 rounded-full bg-line" aria-hidden="true">
          <div className="h-full rounded-full bg-brand transition-[width] duration-300" style={{ width: `${(answeredCount / questions.length) * 100}%` }} />
        </div>
      </div>

      {confirming && !submitting && (
        <div className="mb-6 flex flex-col gap-3 rounded-xl border border-line bg-white p-4 sm:flex-row sm:items-center sm:justify-between" role="alert">
          <p className="text-sm">
            You've left <span className="font-semibold">{unanswered}</span> {unanswered === 1 ? 'question' : 'questions'} unanswered. Submit anyway?
          </p>
          <div className="flex items-center gap-4">
            <Button size="sm" onClick={() => submit()}>Submit now</Button>
            <TextButton onClick={() => setConfirming(false)}>Keep going</TextButton>
          </div>
        </div>
      )}
      {error && <Alert className="mb-6">{error}</Alert>}

      {submitting ? (
        <div className="rounded-2xl bg-night p-10 text-white" role="status">
          <div className="flex items-center gap-4">
            <Waveform bars={14} />
            <p className="font-semibold">Marking your test…</p>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
          {/* The current question */}
          <section key={question.id} className="animate-fade-up rounded-2xl border border-line bg-white p-6 sm:p-8" aria-labelledby="q-text">
            <p className="text-sm text-muted">
              <span className="font-semibold text-brand">{question.section}</span> · Question {index + 1} of {questions.length}
            </p>
            <h2 id="q-text" className="mt-3 text-lg font-medium leading-relaxed">{question.text}</h2>
            {question.code && <CodeBlock code={question.code} />}

            <fieldset className="mt-6">
              <legend className="sr-only">Choose one answer</legend>
              <div className="space-y-3">
                {question.options.map((option, i) => {
                  const selected = answers[question.id] === i
                  return (
                    <label
                      key={i}
                      className={`flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3 transition-colors ${
                        selected ? 'border-brand bg-brand-soft' : 'border-line hover:border-ink/30'
                      }`}
                    >
                      <input type="radio" name={question.id} checked={selected} onChange={() => choose(i)} className="sr-only" />
                      <span className={`grid size-6 shrink-0 place-items-center rounded-full text-xs font-semibold ${selected ? 'bg-brand text-white' : 'bg-ink/5 text-muted'}`}>
                        {LETTERS[i]}
                      </span>
                      <span className={`leading-relaxed ${/[;{}()=]/.test(option) && option.length > 25 ? 'font-mono text-sm' : ''}`}>{option}</span>
                    </label>
                  )
                })}
              </div>
            </fieldset>

            <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
              <Button variant="secondary" onClick={() => setIndex(index - 1)} disabled={index === 0}>← Previous</Button>
              {answers[question.id] != null && <TextButton onClick={clearChoice} className="text-muted">Clear answer</TextButton>}
              {index < questions.length - 1 ? (
                <Button onClick={() => setIndex(index + 1)}>Next →</Button>
              ) : (
                <Button onClick={() => (unanswered > 0 ? setConfirming(true) : submit())}>Finish test</Button>
              )}
            </div>
          </section>

          {/* Question palette: jump to any question */}
          <aside className="h-fit rounded-2xl border border-line bg-white p-5 lg:sticky lg:top-28">
            <p className="text-sm font-semibold">Questions</p>
            {paper.sections.map((section) => (
              <div key={section.name} className="mt-4">
                <p className="text-xs text-muted">{section.name}</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {section.questions.map((q) => {
                    const n = questions.findIndex((item) => item.id === q.id)
                    const done = answers[q.id] != null
                    const current = n === index
                    return (
                      <button
                        key={q.id}
                        onClick={() => setIndex(n)}
                        aria-label={`Question ${n + 1}${done ? ', answered' : ''}`}
                        aria-current={current ? 'step' : undefined}
                        className={`size-8 rounded-lg text-xs font-semibold tabular-nums transition-colors ${
                          current ? 'ring-2 ring-brand ring-offset-1' : ''
                        } ${done ? 'bg-brand text-white' : 'bg-ink/5 text-muted hover:bg-ink/10'}`}
                      >
                        {n + 1}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
            <p className="mt-5 flex items-center gap-2 text-xs text-muted">
              <span className="size-3 rounded bg-brand" aria-hidden="true" /> Answered
              <span className="ml-2 size-3 rounded bg-ink/10" aria-hidden="true" /> Not yet
            </p>
          </aside>
        </div>
      )}
    </div>
  )
}

function secondsLeft(deadline) {
  return Math.round((new Date(deadline).getTime() - Date.now()) / 1000)
}

function CodeBlock({ code }) {
  return (
    <pre className="mt-4 overflow-x-auto rounded-xl bg-night p-4 font-mono text-sm leading-relaxed text-white/90">
      <code>{code}</code>
    </pre>
  )
}

/* ====================== The result ====================== */

function Result({ result }) {
  const navigate = useNavigate()
  const wrongCount = result.review.filter((item) => item.chosen !== item.correct).length
  // Open on the mistakes, since that's what's worth reviewing
  const [filter, setFilter] = useState(wrongCount > 0 ? 'wrong' : 'all')
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState('')

  const shown = filter === 'wrong' ? result.review.filter((item) => item.chosen !== item.correct) : result.review

  async function again() {
    setStarting(true)
    setError('')
    try {
      const paper = await api(`/companies/${result.company_id}/tests`, { method: 'POST' })
      navigate(`/companies/${result.company_id}/tests/${paper.id}`, { state: { paper } })
    } catch (err) {
      setError(err.message)
      setStarting(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <Link to={`/companies/${result.company_id}`} className="text-sm font-semibold text-brand underline-offset-4 hover:underline">
        ← {result.company_name}
      </Link>

      {/* Score + level */}
      <section className="relative mt-5 overflow-hidden rounded-2xl bg-night p-6 text-white sm:p-10">
        <div className="pointer-events-none absolute -left-16 -top-20 size-72 animate-drift rounded-full bg-glow/15 blur-3xl" aria-hidden="true" />
        <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center sm:gap-10">
          <div className="shrink-0">
            <p className="text-6xl font-semibold leading-none tracking-tight" aria-label={`Score ${result.score} percent`}>
              {result.score}<span className="ml-1 text-2xl font-normal text-white/60">%</span>
            </p>
            <p className="mt-2 text-sm text-white/60">{result.correct} of {result.total} correct · {formatTime(result.time_taken_seconds)} used</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-glow">Practice estimate</p>
            <p className="mt-1 font-serif text-3xl">{result.level.label}</p>
            <p className="mt-2 leading-relaxed text-white/75">{result.level.note}</p>
          </div>
        </div>
        {result.auto_submitted && (
          <p className="relative mt-6 text-sm text-white/60">⏱ Time ran out, so your test was submitted automatically.</p>
        )}
      </section>

      {/* Section scores */}
      <section className="mt-6 rounded-2xl border border-line bg-white p-6 sm:p-8">
        <h2 className="text-lg font-semibold">By section</h2>
        <div className="mt-5 space-y-5">
          {result.sections.map((section) => {
            const percent = Math.round((100 * section.correct) / section.total)
            return (
              <div key={section.name}>
                <div className="flex items-baseline justify-between gap-4">
                  <p className="font-medium">{section.name}</p>
                  <p className="text-sm text-muted tabular-nums">
                    <span className="font-semibold text-ink">{section.correct}</span> / {section.total}
                  </p>
                </div>
                <div className="mt-2 h-2 rounded-full bg-line" role="meter" aria-label={`${section.name} score`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent}>
                  <div className="h-full rounded-full bg-brand" style={{ width: `${percent}%` }} />
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Review every answer */}
      <section className="mt-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">Review your answers</h2>
          <div className="flex gap-2" role="group" aria-label="Which answers to show">
            {[['all', `All (${result.total})`], ['wrong', `Wrong or skipped (${wrongCount})`]].map(([id, label]) => (
              <button
                key={id}
                onClick={() => setFilter(id)}
                aria-pressed={filter === id}
                className={`rounded-full border px-3 py-1 text-sm ${filter === id ? 'border-brand bg-brand text-white' : 'border-line bg-white'}`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        {shown.length === 0 ? (
          <p className="mt-4 rounded-2xl border border-dashed border-ink/20 p-8 text-center text-muted">Every answer was right. 🎉</p>
        ) : (
          <ol className="mt-4 space-y-4">
            {shown.map((item) => (
              <ReviewItem key={item.id} item={item} number={result.review.indexOf(item) + 1} />
            ))}
          </ol>
        )}
      </section>

      {error && <Alert className="mt-6">{error}</Alert>}
      <div className="mt-8 flex flex-wrap gap-4">
        <Button onClick={again} disabled={starting}>{starting ? 'Preparing…' : 'Take another mock test'}</Button>
        <Link to="/companies" className="self-center font-semibold text-brand underline-offset-4 hover:underline">Other companies</Link>
      </div>
    </div>
  )
}

function ReviewItem({ item, number }) {
  const skipped = item.chosen == null
  const right = item.chosen === item.correct
  return (
    <li className="rounded-2xl border border-line bg-white p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted">{number}. {item.section}</p>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${right ? 'bg-brand-soft text-brand' : skipped ? 'bg-ink/5 text-muted' : 'bg-mark/10 text-mark'}`}>
          {right ? 'Correct' : skipped ? 'Skipped' : 'Wrong'}
        </span>
      </div>
      <p className="mt-2 font-medium leading-relaxed">{item.text}</p>
      {item.code && <CodeBlock code={item.code} />}
      <ul className="mt-4 space-y-2">
        {item.options.map((option, i) => {
          const isCorrect = i === item.correct
          const isChosen = i === item.chosen
          return (
            <li
              key={i}
              className={`flex items-start gap-3 rounded-lg px-3 py-2 text-sm ${
                isCorrect ? 'bg-brand-soft' : isChosen ? 'bg-mark/10' : ''
              }`}
            >
              <span className="font-semibold text-muted">{LETTERS[i]}</span>
              <span className="flex-1 leading-relaxed">{option}</span>
              {isCorrect && <span className="shrink-0 text-xs font-semibold text-brand">Correct answer</span>}
              {isChosen && !isCorrect && <span className="shrink-0 text-xs font-semibold text-mark">Your answer</span>}
            </li>
          )
        })}
      </ul>
      <p className="mt-4 border-l-2 border-brand pl-4 text-sm leading-relaxed text-muted">{item.explain}</p>
    </li>
  )
}
