import { useAuth } from '../context/AuthContext.jsx'
import { ButtonLink } from '../components/ui/Button.jsx'
import TipCard from '../components/TipCard.jsx'
import GlowBackdrop from '../components/GlowBackdrop.jsx'
import Waveform from '../components/Waveform.jsx'

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

  return (
    <div className="grid gap-10 lg:grid-cols-[1fr_19rem]">
      <div className="space-y-10">
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
      </div>

      <aside className="space-y-6">
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
        </section>
      </aside>
    </div>
  )
}
