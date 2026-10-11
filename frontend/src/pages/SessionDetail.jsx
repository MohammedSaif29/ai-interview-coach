import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { api } from '../lib/api.js'
import { formatDateTime } from '../lib/format.js'
import { Button } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import DeliveryReport from '../components/DeliveryReport.jsx'
import FeedbackReport from '../components/FeedbackReport.jsx'
import GlowBackdrop from '../components/GlowBackdrop.jsx'

export default function SessionDetail() {
  const { id } = useParams() // from the URL: /history/12 -> "12"
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [error, setError] = useState(null)
  const [scoring, setScoring] = useState(false)
  const [scoreError, setScoreError] = useState('')
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  useEffect(() => {
    setSession(null)
    setError(null)
    api(`/sessions/${id}`)
      .then(setSession)
      .catch((err) => setError(err))
  }, [id])

  async function scoreNow() {
    setScoring(true)
    setScoreError('')
    try {
      const feedback = await api('/answers/evaluate', { method: 'POST', body: { session_id: Number(id) } })
      setSession({ ...session, feedback, content_score: feedback.overall })
    } catch (err) {
      setScoreError(err.message)
    } finally {
      setScoring(false)
    }
  }

  async function deleteSession() {
    setDeleting(true)
    try {
      await api(`/sessions/${id}`, { method: 'DELETE' })
      navigate('/history', { replace: true })
    } catch (err) {
      setDeleteError(err.message)
      setDeleting(false)
    }
  }

  const backLink = (
    <Link to="/history" className="text-sm font-semibold text-brand underline-offset-4 hover:underline">
      Back to history
    </Link>
  )

  if (error) {
    return (
      <div className="mx-auto max-w-3xl">
        {backLink}
        <h1 className="mt-6 font-serif text-3xl tracking-tight">
          {error.status === 404 ? "This session doesn't exist" : "Couldn't load this session"}
        </h1>
        <p className="mt-2 text-muted">
          {error.status === 404 ? 'It may have been deleted.' : error.message}
        </p>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="mx-auto max-w-3xl space-y-4" aria-hidden="true">
        <div className="h-4 w-32 animate-pulse rounded bg-line" />
        <div className="h-10 w-3/4 animate-pulse rounded bg-line" />
        <div className="h-72 animate-pulse rounded-2xl bg-line/60" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl">
      {backLink}
      <p className="mt-6 text-sm text-muted">
        {session.role_label}, {formatDateTime(session.created_at)}
      </p>
      <h1 className="mt-1 font-serif text-3xl leading-[1.2] tracking-tight text-balance sm:text-4xl">
        &ldquo;{session.question}&rdquo;
      </h1>

      <section className="relative isolate mt-8 overflow-hidden rounded-2xl bg-night p-6 text-white sm:p-10">
        <GlowBackdrop />
        <div className="relative">
          <DeliveryReport analysis={session.analysis} />
        </div>
      </section>

      <div className="mt-6">
        {session.feedback ? (
          <FeedbackReport feedback={session.feedback} />
        ) : (
          <div className="rounded-2xl border border-line bg-white p-6 sm:p-8">
            <p className="font-semibold">This answer hasn't been scored yet</p>
            <p className="mt-1 text-sm text-muted">Get the AI interviewer's feedback on what you said.</p>
            {scoreError && <Alert className="mt-4">{scoreError}</Alert>}
            <Button onClick={scoreNow} disabled={scoring} className="mt-5">
              {scoring ? 'Scoring your answer…' : 'Score this answer'}
            </Button>
          </div>
        )}
      </div>

      <div className="mt-10 border-t border-line pt-6">
        {deleteError && <Alert className="mb-4">{deleteError}</Alert>}
        {confirmingDelete ? (
          <div className="flex flex-wrap items-center gap-3">
            <p className="text-sm font-medium">Delete this session permanently?</p>
            <Button variant="danger" size="sm" onClick={deleteSession} disabled={deleting}>
              {deleting ? 'Deleting…' : 'Delete'}
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setConfirmingDelete(false)} disabled={deleting}>
              Cancel
            </Button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmingDelete(true)}
            className="text-sm font-semibold text-mark underline-offset-4 hover:underline"
          >
            Delete this session
          </button>
        )}
      </div>
    </div>
  )
}
