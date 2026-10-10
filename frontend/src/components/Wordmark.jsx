import { Link } from 'react-router'

// The logo: three sound-wave bars (voice) + the name.
export default function Wordmark({ to = '/', compact = false, light = false }) {
  return (
    <Link to={to} className="flex items-center gap-2.5 rounded-md" aria-label="Interview Bot home">
      <span className="grid size-8 place-items-center rounded-lg bg-brand" aria-hidden="true">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="white">
          <rect x="1.5" y="5" width="3" height="6" rx="1.5" />
          <rect x="6.5" y="1.5" width="3" height="13" rx="1.5" />
          <rect x="11.5" y="4" width="3" height="8" rx="1.5" />
        </svg>
      </span>
      <span
        className={`text-[17px] font-bold tracking-tight ${compact ? 'hidden sm:inline' : ''} ${light ? 'text-white' : ''}`}
      >
        Interview Bot
      </span>
    </Link>
  )
}
