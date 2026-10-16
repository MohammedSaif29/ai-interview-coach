import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../lib/api.js'
import { Alert } from '../components/ui/Alert.jsx'

const FILTERS = [
  { id: 'all', label: 'All companies' },
  { id: 'service', label: 'Service companies' },
  { id: 'product', label: 'Product companies' },
]

export default function Companies() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    api('/companies')
      .then(setCompanies)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const shown = filter === 'all' ? companies : companies.filter((c) => c.kind === filter)

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Company prep</h1>
      <p className="mt-2 max-w-2xl text-muted">
        How each company tests freshers, how it sorts them into roles, and a timed mock test in its style.
      </p>

      <div className="mt-6 rounded-xl border border-line bg-white px-4 py-3 text-sm leading-relaxed text-muted">
        📘 <span className="font-semibold text-ink">Service vs product companies:</span> service companies
        (TCS, Infosys…) hire thousands of freshers through one big test and sort them into pay tracks by score.
        Product companies (Amazon, Microsoft…) hire fewer people, mostly on coding and problem-solving interviews.
      </div>

      <div className="mt-6 flex flex-wrap gap-2" role="group" aria-label="Filter companies">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            aria-pressed={filter === f.id}
            className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === f.id ? 'border-brand bg-brand text-white' : 'border-line bg-white hover:border-ink/30'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && <Alert className="mt-6">{error}</Alert>}

      {loading ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-hidden="true">
          {[0, 1, 2, 3, 4, 5].map((i) => <div key={i} className="h-48 animate-pulse rounded-2xl bg-line/60" />)}
        </div>
      ) : (
        <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {shown.map((company, i) => (
            <li key={company.id} className="animate-fade-up" style={{ animationDelay: `${i * 40}ms` }}>
              <CompanyCard company={company} />
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function CompanyCard({ company }) {
  return (
    <Link
      to={`/companies/${company.id}`}
      className="group flex h-full flex-col rounded-2xl border border-line bg-white p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-[0_12px_32px_-16px_var(--color-brand)]"
    >
      <div className="flex items-start justify-between gap-3">
        <Monogram name={company.name} />
        <span className="rounded-full bg-ink/5 px-2.5 py-0.5 text-xs font-medium capitalize text-muted">{company.kind}</span>
      </div>
      <p className="mt-4 text-lg font-semibold">{company.name}</p>
      <p className="text-sm text-muted">{company.exam}</p>
      <p className="mt-3 text-sm leading-relaxed">
        {company.roles.length > 1 ? `${company.roles.length} roles: ${company.roles.join(' · ')}` : company.roles[0]}
      </p>
      <div className="mt-auto flex items-end justify-between gap-3 pt-5 text-sm">
        <p className="text-muted">{company.question_count} questions · {company.minutes} min mock</p>
        {company.best_score != null ? (
          <p className="shrink-0 text-muted">Best <span className="font-semibold text-ink">{company.best_score}%</span></p>
        ) : (
          <span className="shrink-0 font-semibold text-brand group-hover:underline">Prepare →</span>
        )}
      </div>
    </Link>
  )
}

// A neutral initials badge (we don't use company logos)
export function Monogram({ name, size = 'md' }) {
  const sizes = size === 'lg' ? 'size-14 text-lg' : 'size-11 text-sm'
  return (
    <span className={`grid shrink-0 place-items-center rounded-xl bg-night font-semibold tracking-wide text-glow ${sizes}`} aria-hidden="true">
      {name.slice(0, 2).toUpperCase()}
    </span>
  )
}
