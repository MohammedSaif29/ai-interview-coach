import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext.jsx'
import Wordmark from './Wordmark.jsx'

// Small line icons (18px, drawn with the current text colour)
function Icon({ children }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {children}
    </svg>
  )
}
const icons = {
  dashboard: <Icon><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" /></Icon>,
  practice: <Icon><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" /></Icon>,
  coach: <Icon><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" /></Icon>,
  history: <Icon><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></Icon>,
  companies: <Icon><path d="M4 21V5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v16M15 9h4a1 1 0 0 1 1 1v11M3 21h18M8 8h3M8 12h3M8 16h3" /></Icon>,
  resume: <Icon><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5M9 13h6M9 17h4" /></Icon>,
}

// THE NAVIGATION LIST: add a section here and it appears in the sidebar and phone menu
const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: icons.dashboard },
  { to: '/practice', label: 'Practice', icon: icons.practice },
  { to: '/coach', label: 'Coach', icon: icons.coach },
  { to: '/companies', label: 'Companies', icon: icons.companies },
  { to: '/resume', label: 'Resume', icon: icons.resume },
  { to: '/history', label: 'History', icon: icons.history },
]

/*
  The frame around every logged-in page.
  Large screens: a sidebar on the left. Phones and tablets: a top bar with a Menu button.
*/
export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  // Close the phone menu whenever the page changes
  useEffect(() => setMenuOpen(false), [location.pathname])

  async function handleLogout() {
    try {
      await logout()
    } finally {
      navigate('/', { replace: true })
    }
  }

  const navLinks = NAV.map((item) => (
    <NavLink
      key={item.to}
      to={item.to}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 text-[15px] font-medium transition-colors ${
          isActive ? 'bg-brand-soft text-brand' : 'text-muted hover:bg-paper hover:text-ink'
        }`
      }
    >
      {item.icon}
      {item.label}
    </NavLink>
  ))

  const accountLinks = (
    <div className="flex items-center justify-between gap-3 px-3">
      <Link to="/settings" className="min-w-0 rounded-md text-sm hover:text-brand" title="Account settings">
        <span className="block truncate font-medium">{user.name}</span>
        <span className="block text-xs text-muted">Settings</span>
      </Link>
      <button
        onClick={handleLogout}
        className="shrink-0 rounded-lg border border-line bg-white px-3 py-1.5 text-sm font-semibold hover:border-ink/30"
      >
        Log out
      </button>
    </div>
  )

  return (
    <div className="min-h-screen lg:flex">
      {/* Large screens: sidebar */}
      <aside className="hidden border-r border-line bg-white lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-60 lg:shrink-0 lg:flex-col lg:px-3 lg:py-5">
        <div className="px-3">
          <Wordmark to="/dashboard" />
        </div>
        <nav aria-label="Main" className="mt-8 flex flex-col gap-1">{navLinks}</nav>
        <div className="mt-auto border-t border-line pt-4">{accountLinks}</div>
      </aside>

      {/* Phones and tablets: top bar + menu */}
      <header className="sticky top-0 z-20 border-b border-line bg-white/95 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between px-4 py-3 sm:px-6">
          <Wordmark to="/dashboard" />
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            aria-expanded={menuOpen}
            aria-controls="phone-menu"
            className="rounded-lg border border-line bg-white px-3 py-1.5 text-sm font-semibold"
          >
            {menuOpen ? 'Close' : 'Menu'}
          </button>
        </div>
        {menuOpen && (
          <div id="phone-menu" className="animate-fade-up border-t border-line px-3 pb-4 pt-2">
            <nav aria-label="Main" className="flex flex-col gap-1">{navLinks}</nav>
            <div className="mt-3 border-t border-line pt-3">{accountLinks}</div>
          </div>
        )}
      </header>

      {/* key changes on every page, so each page fades in smoothly */}
      <main key={location.pathname} className="mx-auto w-full min-w-0 max-w-5xl flex-1 animate-fade-up px-4 py-10 sm:px-6 sm:py-14 lg:px-10">
        <Outlet />
      </main>
    </div>
  )
}
