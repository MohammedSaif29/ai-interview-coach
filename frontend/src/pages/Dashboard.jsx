import { lazy, Suspense, useEffect, useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../context/AuthContext.jsx'
import { api } from '../lib/api.js'
import { ButtonLink } from '../components/ui/Button.jsx'
import TipCard from '../components/TipCard.jsx'
import GlowBackdrop from '../components/GlowBackdrop.jsx'
import Waveform from '../components/Waveform.jsx'
import SessionRow from '../components/SessionRow.jsx'

// CODE SPLITTING: the chart library is big, so it's downloaded only when the
// dashboard actually needs charts. Login and landing pages stay fast.
const ProgressCharts = lazy(() => import('../components/ProgressCharts.jsx'))

function greeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function Dashboard() {
  const { user } = useAuth()
  const firstName = user.name.split(' ')[0]
  const displayName = firstName.charAt(0).toUpperCase() + firstName.slice(1)
  const memberSince = new Date(user.created_at).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [loadError, setLoadError] = useState(false)

  useEffect(() => {
    // Promise.all: ask for both at the same time instead of one after the other
    Promise.all([api('/sessions/stats'), api('/sessions?limit=5')])
      .then(([statsData, recentData]) => {
        setStats(statsData)
        setRecent(recentData)
      })
      .catch(() => setLoadError(true))
  }, [])

  return (
    <div className="grid gap-10 xl:grid-cols-[1fr_19rem]">
      <div className="min-w-0 space-y-10">
        <header>
          <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">
            {greeting()}, {displayName}
          </h1>
          <p className="mt-2 text-muted">Each practice question takes about two minutes.</p>
        </header>

        <section className="relative isolate overflow-hidden rounded-2xl bg-night p-8 text-white sm:p-10">
          <GlowBackdrop />
          <Waveform bars={20} className="absolute right-8 top-8 hidden opacity-60 sm:flex" />
          <div className="relative">
            <h2 className="font-serif text-3xl tracking-tight">Start a practice session</h2>
            <p className="mt-2 max-w-md leading-relaxed text-white/70">
              You'll get one question at a time. Answer it out loud, as you would in the room.
            </p>
            <ButtonLink to="/practice" variant="glow" className="mt-7">
              Start practice
            </ButtonLink>
          </div>
        </section>

        {loadError && (
          <p className="text-sm text-muted">Your progress couldn't be loaded. Refresh the page to try again.</p>
        )}

        {!stats && !loadError && (
          <div className="space-y-4" aria-hidden="true">
            <div className="h-24 animate-pulse rounded-2xl bg-line/60" />
            <div className="h-72 animate-pulse rounded-2xl bg-line/60" />
          </div>
        )}

        {stats && stats.total_sessions === 0 && (
          <section>
            <h2 className="text-lg font-semibold">Your sessions</h2>
            {/* Empty state: honest about having no data yet, and says what will appear */}
            <div className="mt-3 rounded-2xl border border-dashed border-ink/20 px-6 py-12 text-center">
              <p className="font-medium">No sessions yet</p>
              <p className="mx-auto mt-1 max-w-sm text-sm leading-relaxed text-muted">
                After your first practice session, your scores and progress will show up here.
              </p>
            </div>
          </section>
        )}

        {stats && stats.total_sessions > 0 && (
          <>
            <dl className="grid grid-cols-3 divide-x divide-line rounded-2xl border border-line bg-white">
              <StatTile label="Sessions" value={stats.total_sessions} />
              <StatTile label="Average content score" value={stats.average_content} outOf={10} />
              <StatTile label="Average delivery score" value={stats.average_delivery} outOf={10} />
            </dl>

            {stats.trend.length >= 2 ? (
              <Suspense fallback={<div className="h-[34rem] animate-pulse rounded-2xl bg-line/60" aria-hidden="true" />}>
                <ProgressCharts trend={stats.trend} />
              </Suspense>
            ) : (
              <div className="rounded-2xl border border-dashed border-ink/20 px-6 py-8 text-center">
                <p className="font-medium">Your progress chart starts after two sessions</p>
                <p className="mt-1 text-sm text-muted">Record one more answer to see how you're improving.</p>
              </div>
            )}

            <section>
              <div className="flex items-baseline justify-between gap-4">
                <h2 className="text-lg font-semibold">Recent sessions</h2>
                <Link to="/history" className="text-sm font-semibold text-brand underline-offset-4 hover:underline">
                  See all
                </Link>
              </div>
              <div className="mt-3 divide-y divide-line overflow-hidden rounded-2xl border border-line bg-white">
                {recent.map((session) => (
                  <SessionRow key={session.id} session={session} />
                ))}
              </div>
            </section>
          </>
        )}
      </div>

      <aside className="space-y-6">
        <section className="relative isolate overflow-hidden rounded-2xl bg-night p-6 text-white">
          <GlowBackdrop />
          <div className="relative">
            <h2 className="text-sm font-semibold text-glow">Your coach</h2>
            <p className="mt-2 leading-relaxed text-white/80">
              Not sure what to practise next? Your coach can see your scores and suggest a plan.
            </p>
            <Link
              to={`/coach?ask=${encodeURIComponent('What should I work on next?')}`}
              className="mt-4 inline-block text-sm font-semibold text-glow underline-offset-4 hover:underline"
            >
              Ask your coach
            </Link>
          </div>
        </section>
        <TipCard />
        <section className="rounded-2xl border border-line bg-white p-6">
          <h2 className="text-sm font-semibold text-brand">Your account</h2>
          <dl className="mt-3 space-y-3 text-sm">
            <div>
              <dt className="text-muted">Name</dt>
              <dd className="font-medium">{user.name}</dd>
            </div>
            <div>
              <dt className="text-muted">Email</dt>
              <dd className="font-medium break-all">{user.email}</dd>
            </div>
            <div>
              <dt className="text-muted">Member since</dt>
              <dd className="font-medium">{memberSince}</dd>
            </div>
          </dl>
          <Link to="/settings" className="mt-4 inline-block text-sm font-semibold text-brand underline-offset-4 hover:underline">
            Account settings
          </Link>
        </section>
      </aside>
    </div>
  )
}

function StatTile({ label, value, outOf }) {
  return (
    <div className="p-4 sm:p-5">
      <dt className="text-xs text-muted sm:text-sm">{label}</dt>
      <dd className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">
        {value ?? '–'}
        {outOf && value != null && <span className="text-sm font-normal text-muted">/{outOf}</span>}
      </dd>
    </div>
  )
}
