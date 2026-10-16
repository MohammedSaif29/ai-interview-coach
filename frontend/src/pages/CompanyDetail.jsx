import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { api } from '../lib/api.js'
import { formatDateTime } from '../lib/format.js'
import { Button, ButtonLink } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import { Monogram } from './Companies.jsx'

export default function CompanyDetail() {
  const { companyId } = useParams()
  const navigate = useNavigate()
  const [company, setCompany] = useState(null)
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)
  const [startError, setStartError] = useState('')

  useEffect(() => {
    setCompany(null)
    api(`/companies/${companyId}`)
      .then(setCompany)
      .catch((err) => setError(err.message))
  }, [companyId])

  async function startTest() {
    setStarting(true)
    setStartError('')
    try {
      const paper = await api(`/companies/${companyId}/tests`, { method: 'POST' })
      // Pass the paper along so the test page doesn't have to load it again
      navigate(`/companies/${companyId}/tests/${paper.id}`, { state: { paper } })
    } catch (err) {
      setStartError(err.message)
      setStarting(false)
    }
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl">
        <Alert>{error}</Alert>
        <Link to="/companies" className="mt-4 inline-block text-sm font-semibold text-brand">← All companies</Link>
      </div>
    )
  }
  if (!company) return <div className="mx-auto h-96 max-w-4xl animate-pulse rounded-2xl bg-line/60" aria-hidden="true" />

  const coachQuestion = `Make me a 2-week plan to prepare for the ${company.name} ${company.exam}`

  return (
    <div className="mx-auto max-w-4xl">
      <Link to="/companies" className="text-sm font-semibold text-brand underline-offset-4 hover:underline">← All companies</Link>

      <header className="mt-5 flex items-start gap-4">
        <Monogram name={company.name} size="lg" />
        <div>
          <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">{company.name}</h1>
          <p className="mt-1 text-muted">{company.full_name} · <span className="capitalize">{company.kind}</span> company · {company.exam}</p>
        </div>
      </header>
      <p className="mt-6 max-w-3xl text-lg leading-relaxed">{company.summary}</p>

      {/* How they sort freshers into roles */}
      <section className="mt-10">
        <h2 className="text-xl font-semibold">{company.roles.length > 1 ? 'How they sort freshers into roles' : 'The role and how they decide'}</h2>
        <ol className={`mt-4 grid gap-4 ${company.roles.length > 1 ? 'sm:grid-cols-2 lg:grid-cols-3' : ''}`}>
          {company.roles.map((role, i) => (
            <li key={role.name} className="relative overflow-hidden rounded-2xl border border-line bg-white p-5">
              {company.roles.length > 1 && (
                <span className="text-xs font-semibold uppercase tracking-wider text-muted">Level {i + 1}</span>
              )}
              <p className="mt-1 text-lg font-semibold">{role.name}</p>
              {role.pay && <p className="text-sm font-medium text-brand">{role.pay}</p>}
              <p className="mt-2 text-sm leading-relaxed text-muted">{role.how}</p>
              {/* a bar that grows with each level, so the "ladder" is visible at a glance */}
              {company.roles.length > 1 && (
                <div className="mt-4 h-1.5 rounded-full bg-line" aria-hidden="true">
                  <div className="h-full rounded-full bg-brand" style={{ width: `${((i + 1) / company.roles.length) * 100}%` }} />
                </div>
              )}
            </li>
          ))}
        </ol>
      </section>

      {/* Hiring rounds as a flowing timeline */}
      <section className="mt-10 rounded-2xl border border-line bg-white p-6 sm:p-8">
        <h2 className="text-xl font-semibold">Hiring rounds</h2>
        <ol className="relative mt-6">
          {/* the line, with a glowing pulse flowing down it */}
          <div className="absolute bottom-3 left-[15px] top-3 w-0.5 overflow-hidden rounded-full bg-line" aria-hidden="true">
            <div className="h-1/5 w-full animate-flow bg-gradient-to-b from-transparent via-glow to-transparent" />
          </div>
          {company.rounds.map((round, i) => (
            <li key={round.name} className="relative flex gap-5 pb-7 last:pb-0">
              <span className="relative z-10 grid size-8 shrink-0 place-items-center rounded-full border-2 border-brand bg-white text-sm font-semibold text-brand">
                {i + 1}
              </span>
              <div className="pt-1">
                <p className="font-semibold">{round.name}</p>
                <p className="mt-1 text-sm leading-relaxed text-muted">{round.detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <section className="rounded-2xl border border-line bg-white p-6">
          <h2 className="text-lg font-semibold">What to focus on</h2>
          <ul className="mt-4 flex flex-wrap gap-2">
            {company.focus.map((topic) => (
              <li key={topic} className="rounded-full border border-line px-3 py-1 text-sm">{topic}</li>
            ))}
          </ul>
        </section>
        <section className="rounded-2xl border border-line bg-white p-6">
          <h2 className="text-lg font-semibold">Tips</h2>
          <ul className="mt-3 space-y-3">
            {company.tips.map((tip) => (
              <li key={tip} className="flex gap-3 text-sm leading-relaxed">
                <span className="mt-1.5 size-2 shrink-0 rounded-full bg-brand" aria-hidden="true" />
                {tip}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Mock test */}
      <section className="relative mt-6 overflow-hidden rounded-2xl bg-night p-6 text-white sm:p-10">
        <div className="pointer-events-none absolute -right-20 -top-24 size-80 animate-drift rounded-full bg-glow/15 blur-3xl" aria-hidden="true" />
        <div className="relative">
          <p className="text-sm font-semibold text-glow">Mock test</p>
          <h2 className="mt-1 font-serif text-3xl">{company.name}-style practice test</h2>
          <p className="mt-2 max-w-xl text-white/70">
            {company.mock.question_count} questions in {company.mock.minutes} minutes. Original questions in the same style
            and sections. You'll get a score per section, an estimated level, and an explanation for every answer.
          </p>
          <ul className="mt-6 flex flex-wrap gap-2">
            {company.mock.sections.map((section) => (
              <li key={section.name} className="rounded-full border border-white/15 px-3 py-1 text-sm text-white/85">
                {section.name} <span className="text-white/50">· {section.count}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-sm text-white/55">{company.mock.coding_note} Coding practice is coming next.</p>
          {startError && <Alert dark className="mt-5">{startError}</Alert>}
          <div className="mt-7 flex flex-wrap items-center gap-4">
            <Button variant="glow" size="lg" onClick={startTest} disabled={starting}>
              {starting ? 'Preparing your test…' : 'Start the mock test'}
            </Button>
            <ButtonLink to={`/coach?ask=${encodeURIComponent(coachQuestion)}`} variant="outlineLight">
              Ask the coach for a plan
            </ButtonLink>
          </div>
        </div>
      </section>

      {company.attempts.length > 0 && (
        <section className="mt-8">
          <h2 className="text-lg font-semibold">Your attempts</h2>
          <ul className="mt-3 divide-y divide-line overflow-hidden rounded-2xl border border-line bg-white">
            {company.attempts.map((attempt) => (
              <li key={attempt.id}>
                <Link to={`/companies/${company.id}/tests/${attempt.id}`} className="flex items-center gap-4 px-5 py-4 hover:bg-paper">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium">{attempt.level}</p>
                    <p className="text-sm text-muted">{formatDateTime(attempt.submitted_at)} · {attempt.correct}/{attempt.total} correct</p>
                  </div>
                  <p className="text-lg font-semibold tabular-nums">{attempt.score}%</p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="mt-8 border-t border-line pt-6 text-sm leading-relaxed text-muted">
        <p>
          <span className="font-semibold text-ink">Where this comes from:</span> candidate reports and placement-prep
          sites, checked {company.last_checked}. Pay figures are approximate. Companies change their tests every year
          and most don't publish cut-offs, so always check the{' '}
          <a href={company.careers_url} target="_blank" rel="noreferrer" className="font-semibold text-brand underline-offset-4 hover:underline">
            official {company.name} careers page
          </a>
          . The level estimate is this app's practice guide, not the company's rule.
        </p>
        <ul className="mt-3 space-y-1">
          {company.sources.map((source) => (
            <li key={source.url}>
              <a href={source.url} target="_blank" rel="noreferrer" className="underline-offset-4 hover:text-ink hover:underline">
                {source.title} ↗
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
