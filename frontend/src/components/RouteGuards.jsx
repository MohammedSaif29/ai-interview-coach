/*
  ROUTE GUARDS: decide who is allowed to see a page.
  This is only for a nice experience. The REAL security is on the backend:
  even if someone bypasses this, the API still rejects them without a valid cookie.
*/
import { Navigate, useLocation } from 'react-router'
import { useAuth } from '../context/AuthContext.jsx'
import Spinner from './Spinner.jsx'

// Logged-in users only. Others are sent to /login, remembering where they wanted to go.
export function ProtectedRoute({ children }) {
  const { user, checking } = useAuth()
  const location = useLocation()

  if (checking) return <Spinner />
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}

// Logged-out users only (login & signup pages). Logged-in users skip ahead.
export function GuestOnlyRoute({ children }) {
  const { user, checking } = useAuth()
  const location = useLocation()

  if (checking) return <Spinner />
  if (user) return <Navigate to={location.state?.from || '/dashboard'} replace />
  return children
}
