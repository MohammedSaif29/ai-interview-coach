import { useEffect, useRef, useState } from 'react'
import { api } from '../lib/api.js'
import { formatDateTime } from '../lib/format.js'
import { Button, ButtonLink, TextButton } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import { Placeholders } from '../components/FeedbackReport.jsx'
import Waveform from '../components/Waveform.jsx'

const TARGETS = [
  { id: 'any', label: 'Any tech role' },
  { id: 'software', label: 'Software developer' },
  { id: 'web', label: 'Web developer' },
  { id: 'data', label: 'Data analyst' },
]

const MAX_BYTES = 5 * 1024 * 1024

export default function Resume() {
  const [history, setHistory] = useState([])
  const [current, setCurrent] = useState(null) // the full review being shown
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Load past reviews, and open the newest one
  useEffect(() => {
    api('/resumes')
      .then(async (list) => {
        setHistory(list)
        if (list.length > 0) setCurrent(await api(`/resumes/${list[0].id}`))
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  function handleReviewed(review) {
    setCurrent(review)
    setHistory((list) => [review, ...list])
  }

  async function open(id) {
    setError('')
    try {
      setCurrent(await api(`/resumes/${id}`))
      document.getElementById('resume-result')?.scrollIntoView({ behavior: 'smooth' })
    } catch (err) {
      setError(err.message)
    }
  }

  async function remove(id) {
    setError('')
    try {
      await api(`/resumes/${id}`, { method: 'DELETE' })
      const remaining = history.filter((item) => item.id !== id)
      setHistory(remaining)
      if (current?.id === id) setCurrent(remaining.length > 0 ? await api(`/resumes/${remaining[0].id}`) : null)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Resume review</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Upload your resume as a PDF. You get automatic ATS checks, an AI review with rewrites, and interview
        questions about your own projects.
      </p>

      <UploadCard onReviewed={handleReviewed} />

      {error && <Alert className="mt-6">{error}</Alert>}

      {loading ? (
        <div className="mt-10 h-64 animate-pulse rounded-2xl bg-line/60" aria-hidden="true" />
      ) : (
        current && <ReviewResult key={current.id} resume={current} />
      )}

      {history.length > 0 && (
        <PastReviews items={history} currentId={current?.id} onOpen={open} onDelete={remove} />
      )}
    </div>
  )
}

/* ---------- Upload ---------- */

function UploadCard({ onReviewed }) {
  const input = useRef(null)
  const [file, setFile] = useState(null)
  const [target, setTarget] = useState('any')
  const [dragging, setDragging] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  function choose(picked) {
    setError('')
    if (!picked) return
    // Quick checks in the browser; the server checks again (never trust the browser alone)
    if (picked.type !== 'application/pdf' && !picked.name.toLowerCase().endsWith('.pdf')) {
      setError('Choose a PDF file. In Word or Google Docs, use File → Download → PDF.')
      return
    }
    if (picked.size > MAX_BYTES) {
      setError('That file is larger than 5 MB.')
      return
    }
    setFile(picked)
  }

  async function submit(event) {
    event.preventDefault()
    if (!file || busy) return
    setBusy(true)
    setError('')
    const form = new FormData()
    form.append('file', file)
    form.append('target_role', target)
    try {
      const review = await api('/resumes', { method: 'POST', body: form })
      setFile(null)
      if (input.current) input.current.value = ''
      onReviewed(review)
      setTimeout(() => document.getElementById('resume-result')?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (busy) {
    return (
      <section className="mt-8 rounded-2xl bg-night p-8 text-white sm:p-10" role="status">
        <div className="flex items-center gap-4">
          <Waveform bars={16} tone="glow" />
          <p className="font-semibold">Reviewing {file?.name}…</p>
        </div>
        <p className="mt-3 text-sm text-white/70">
          Reading the PDF, running the ATS checks, then the AI reviewer reads it like a recruiter would. This
          takes about 10–20 seconds.
        </p>
      </section>
    )
  }

  return (
    <form onSubmit={submit} className="mt-8 rounded-2xl border border-line bg-white p-6 sm:p-8">
      <label
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          choose(e.dataTransfer.files[0])
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
          dragging ? 'border-brand bg-brand-soft' : 'border-ink/15 hover:border-brand/60'
        }`}
      >
        <svg viewBox="0 0 24 24" className="size-9 text-brand" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
          <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
          <path d="M14 3v5h5M12 18v-6M9.5 14.5 12 12l2.5 2.5" />
        </svg>
        {file ? (
          <>
            <p className="mt-3 font-semibold break-all">{file.name}</p>
            <p className="text-sm text-muted">{(file.size / 1024).toFixed(0)} KB · click to choose a different file</p>
          </>
        ) : (
          <>
            <p className="mt-3 font-semibold">Drop your resume here, or click to choose</p>
            <p className="text-sm text-muted">PDF only, up to 5 MB</p>
          </>
        )}
        <input
          ref={input}
          type="file"
          accept="application/pdf,.pdf"
          className="sr-only"
          onChange={(e) => choose(e.target.files[0])}
        />
      </label>

      <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label htmlFor="target" className="text-sm font-semibold">Role you're applying for</label>
          <select
            id="target"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            className="mt-2 w-full rounded-lg border border-line bg-white px-3 py-2.5 focus:border-brand focus:outline-none"
          >
            {TARGETS.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
        </div>
        <Button type="submit" disabled={!file} size="lg">Review my resume</Button>
      </div>

      {error && <Alert className="mt-5">{error}</Alert>}
      <p className="mt-5 text-xs leading-relaxed text-muted">
        Your resume text is saved to your account so you can come back to the review. Delete it any time below.
      </p>
    </form>
  )
}

/* ---------- Results ---------- */

const STATUS = {
  strong: { label: 'Strong', className: 'bg-brand-soft text-brand' },
  needs_work: { label: 'Needs work', className: 'bg-ink/5 text-ink' },
  missing: { label: 'Missing', className: 'bg-mark/10 text-mark' },
}

function ReviewResult({ resume }) {
  const { review, checks } = resume
  const passed = checks.filter((c) => c.passed).length

  return (
    <div id="resume-result" className="mt-10 scroll-mt-24 space-y-6">
      {/* Score + summary */}
      <section className="animate-fade-up rounded-2xl border border-line bg-white p-6 sm:p-10">
        <p className="text-sm text-muted">
          {resume.filename} · {resume.target_label} · {resume.page_count} {resume.page_count === 1 ? 'page' : 'pages'} ·{' '}
          {resume.word_count} words
        </p>
        <div className="mt-5 flex flex-col gap-5 sm:flex-row sm:items-center sm:gap-8">
          <div className="shrink-0">
            <p className="text-6xl font-semibold leading-none tracking-tight" aria-label={`Resume score ${review.overall_score} out of 100`}>
              {review.overall_score}
              <span className="ml-1 text-xl font-normal text-muted">/100</span>
            </p>
            <p className="mt-2 text-sm text-muted">Resume score</p>
          </div>
          <p className="text-lg leading-relaxed">{review.summary}</p>
        </div>
      </section>

      {/* ATS checklist */}
      <section className="rounded-2xl border border-line bg-white p-6 sm:p-10">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-lg font-semibold">ATS checks</h2>
          <p className="text-sm text-muted"><span className="font-semibold text-ink">{passed}</span> of {checks.length} passed</p>
        </div>
        <p className="mt-1 text-sm text-muted">
          📘 An ATS (Applicant Tracking System) is software companies use to scan resumes before a person reads them.
        </p>
        <ul className="mt-6 grid gap-x-8 gap-y-5 sm:grid-cols-2">
          {checks.map((check) => (
            <li key={check.id} className="flex gap-3">
              <CheckIcon passed={check.passed} />
              <div>
                <p className="font-medium">
                  {check.label}
                  <span className="sr-only">{check.passed ? ' — passed' : ' — needs fixing'}</span>
                </p>
                {!check.passed && <p className="mt-1 text-sm leading-relaxed text-muted">{check.tip}</p>}
              </div>
            </li>
          ))}
        </ul>
      </section>

      {/* Section-by-section */}
      {review.sections.length > 0 && (
        <section className="rounded-2xl border border-line bg-white p-6 sm:p-10">
          <h2 className="text-lg font-semibold">Section by section</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {review.sections.map((section) => {
              const status = STATUS[section.status] ?? STATUS.needs_work
              return (
                <div key={section.name} className="rounded-xl border border-line p-5">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold">{section.name}</p>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${status.className}`}>{status.label}</span>
                  </div>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{section.feedback}</p>
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* Strengths / improvements */}
      <section className="grid gap-8 rounded-2xl border border-line bg-white p-6 sm:grid-cols-2 sm:p-10">
        <BulletList title="What works" items={review.strengths} dotClass="bg-brand" />
        <BulletList title="Fix these first" items={review.improvements} dotClass="border-2 border-ink/40" />
      </section>

      {/* Rewrites */}
      {review.rewrites.length > 0 && (
        <section className="rounded-2xl border border-line bg-white p-6 sm:p-10">
          <h2 className="text-lg font-semibold">Stronger bullet points</h2>
          <p className="mt-1 text-sm text-muted">Replace the parts in brackets with your real numbers and details.</p>
          <ol className="mt-6 space-y-6">
            {review.rewrites.map((rewrite, i) => (
              <li key={i} className="grid gap-3 sm:grid-cols-2 sm:gap-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted">Before</p>
                  <p className="mt-1 leading-relaxed text-muted line-through decoration-ink/20">{rewrite.original}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-brand">After</p>
                  <p className="mt-1 leading-relaxed"><Placeholders text={rewrite.improved} /></p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Keywords */}
      {review.keywords_to_add.length > 0 && (
        <section className="rounded-2xl border border-line bg-white p-6 sm:p-10">
          <h2 className="text-lg font-semibold">Keywords to consider</h2>
          <p className="mt-1 text-sm text-muted">
            Common for {resume.target_label.toLowerCase()} roles. Only add the ones you can genuinely talk about.
          </p>
          <ul className="mt-5 flex flex-wrap gap-2">
            {review.keywords_to_add.map((word) => (
              <li key={word} className="rounded-full border border-line px-3 py-1 text-sm">{word}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Interview questions — dark "booth" section that leads into practice */}
      {review.interview_questions.length > 0 && (
        <section className="relative overflow-hidden rounded-2xl bg-night p-6 text-white sm:p-10">
          <div
            className="pointer-events-none absolute -right-24 -top-24 size-72 rounded-full bg-glow/20 blur-3xl"
            aria-hidden="true"
          />
          <h2 className="relative text-lg font-semibold">Questions an interviewer could ask about this resume</h2>
          <ol className="relative mt-6 space-y-4">
            {review.interview_questions.map((question, i) => (
              <li key={i} className="flex gap-4">
                <span className="mt-0.5 text-sm font-semibold tabular-nums text-glow">{String(i + 1).padStart(2, '0')}</span>
                <span className="font-serif text-lg leading-relaxed">{question}</span>
              </li>
            ))}
          </ol>
          <ButtonLink to="/practice?role=resume" variant="glow" className="relative mt-8">
            Practise these out loud
          </ButtonLink>
        </section>
      )}
    </div>
  )
}

function CheckIcon({ passed }) {
  return passed ? (
    <span className="mt-0.5 grid size-6 shrink-0 place-items-center rounded-full bg-brand text-white" aria-hidden="true">
      <svg viewBox="0 0 24 24" className="size-3.5" fill="none" stroke="currentColor" strokeWidth="3"><path d="m5 12 5 5 9-10" /></svg>
    </span>
  ) : (
    <span className="mt-0.5 grid size-6 shrink-0 place-items-center rounded-full bg-mark/10 text-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" className="size-3.5" fill="none" stroke="currentColor" strokeWidth="3"><path d="M12 7v6M12 17h.01" /></svg>
    </span>
  )
}

function BulletList({ title, items, dotClass }) {
  return (
    <div>
      <h2 className="text-lg font-semibold">{title}</h2>
      <ul className="mt-3 space-y-3">
        {items.map((item) => (
          <li key={item} className="flex gap-3 leading-relaxed">
            <span className={`mt-2 size-2 shrink-0 rounded-full ${dotClass}`} aria-hidden="true" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

/* ---------- Past reviews ---------- */

function PastReviews({ items, currentId, onOpen, onDelete }) {
  const [confirming, setConfirming] = useState(null)

  return (
    <section className="mt-12">
      <h2 className="text-lg font-semibold">Past reviews</h2>
      <ul className="mt-4 divide-y divide-line overflow-hidden rounded-2xl border border-line bg-white">
        {items.map((item) => (
          <li key={item.id} className={`flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-4 ${item.id === currentId ? 'bg-brand-soft/50' : ''}`}>
            <button onClick={() => onOpen(item.id)} className="min-w-0 flex-1 text-left">
              <p className="truncate font-medium">{item.filename}</p>
              <p className="text-sm text-muted">{item.target_label} · {formatDateTime(item.created_at)}</p>
            </button>
            <p className="text-sm text-muted tabular-nums"><span className="text-base font-semibold text-ink">{item.score}</span>/100</p>
            {confirming === item.id ? (
              <span className="flex items-center gap-3">
                <Button size="sm" variant="danger" onClick={() => { setConfirming(null); onDelete(item.id) }}>Delete</Button>
                <TextButton onClick={() => setConfirming(null)}>Cancel</TextButton>
              </span>
            ) : (
              <TextButton onClick={() => setConfirming(item.id)} className="text-muted">Delete</TextButton>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}
