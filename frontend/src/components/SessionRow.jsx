import { Link } from 'react-router'
import { formatDateTime } from '../lib/format.js'

// One saved session in a list (History page and the dashboard)
export default function SessionRow({ session }) {
  return (
    <Link
      to={`/history/${session.id}`}
      className="group flex items-center gap-4 px-5 py-4 transition-colors hover:bg-paper focus-visible:bg-paper sm:px-6"
    >
      <div className="min-w-0 flex-1">
        <p className="text-sm text-muted">
          {session.role_label}, {formatDateTime(session.created_at)}
        </p>
        <p className="mt-0.5 truncate font-medium group-hover:text-brand">{session.question}</p>
      </div>
      <div className="flex shrink-0 gap-5 text-right">
        <Score label="Content" value={session.content_score} />
        <Score label="Delivery" value={session.delivery_score} />
      </div>
    </Link>
  )
}

function Score({ label, value }) {
  return (
    <div>
      <p className="text-lg font-semibold leading-none">
        {value ?? '–'}
        {value != null && <span className="text-xs font-normal text-muted">/10</span>}
      </p>
      <p className="mt-1 text-xs text-muted">{value == null ? 'Not scored' : label}</p>
    </div>
  )
}
