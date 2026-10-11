import { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { Button, ButtonLink } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import SessionRow from '../components/SessionRow.jsx'

const PAGE_SIZE = 20

export default function History() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [hasMore, setHasMore] = useState(false)

  // PAGINATION: load 20 at a time; "Show older sessions" loads the next 20
  async function loadPage(offset) {
    setLoading(true)
    setError('')
    try {
      const page = await api(`/sessions?limit=${PAGE_SIZE}&offset=${offset}`)
      setSessions((current) => (offset === 0 ? page : [...current, ...page]))
      setHasMore(page.length === PAGE_SIZE)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPage(0)
  }, [])

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">History</h1>
      <p className="mt-2 text-muted">Every answer you've recorded, newest first.</p>

      {error && <Alert className="mt-8">{error}</Alert>}

      {loading && sessions.length === 0 ? (
        <div className="mt-8 space-y-3" aria-hidden="true">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-[76px] animate-pulse rounded-2xl bg-line/60" />
          ))}
        </div>
      ) : sessions.length === 0 && !error ? (
        <div className="mt-8 rounded-2xl border border-dashed border-ink/20 px-6 py-12 text-center">
          <p className="font-medium">No sessions yet</p>
          <p className="mx-auto mt-1 max-w-sm text-sm leading-relaxed text-muted">
            Each answer you record is saved here, with its scores and feedback.
          </p>
          <ButtonLink to="/practice" className="mt-6">Start practice</ButtonLink>
        </div>
      ) : (
        <div className="mt-8 divide-y divide-line overflow-hidden rounded-2xl border border-line bg-white">
          {sessions.map((session) => (
            <SessionRow key={session.id} session={session} />
          ))}
        </div>
      )}

      {hasMore && (
        <Button variant="secondary" className="mt-6" onClick={() => loadPage(sessions.length)} disabled={loading}>
          {loading ? 'Loading…' : 'Show older sessions'}
        </Button>
      )}
    </div>
  )
}
