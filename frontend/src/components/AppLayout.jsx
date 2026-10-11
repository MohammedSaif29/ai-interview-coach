import { NavLink, Outlet, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext.jsx'
import Wordmark from './Wordmark.jsx'

// The frame around every logged-in page: top bar + page content (<Outlet />).
export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  async function handleLogout() {
    try {
      await logout()
    } finally {
      navigate('/', { replace: true })
    }
  }

  // Tighter spacing on phones (no prefix), roomier from the "sm" breakpoint up
  const linkClasses = ({ isActive }) =>
    `rounded-md px-2 py-1.5 text-sm font-medium transition-colors sm:px-3 sm:text-[15px] ${
      isActive ? 'bg-brand-soft text-brand' : 'text-muted hover:text-ink'
    }`

  return (
    <div className="min-h-screen">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-3 sm:gap-8 sm:px-6">
          <Wordmark to="/dashboard" compact />
          <nav className="flex gap-1" aria-label="Main">
            <NavLink to="/dashboard" className={linkClasses}>Dashboard</NavLink>
            <NavLink to="/practice" className={linkClasses}>Practice</NavLink>
            <NavLink to="/history" className={linkClasses}>History</NavLink>
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <span className="hidden text-sm text-muted md:inline">{user.name}</span>
            {/* A plain text link on phones (saves space), a bordered button on wider screens */}
            <button
              onClick={handleLogout}
              className="whitespace-nowrap rounded-md text-sm font-semibold text-muted hover:text-ink sm:rounded-lg sm:border sm:border-line sm:bg-white sm:px-3 sm:py-1.5 sm:text-ink sm:hover:border-ink/30"
            >
              Log out
            </button>
          </div>
        </div>
      </header>
      {/* key changes on every page, so each page fades in smoothly */}
      <main key={location.pathname} className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6 sm:py-14">
        <Outlet />
      </main>
    </div>
  )
}
