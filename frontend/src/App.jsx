import { Routes, Route } from 'react-router'
import { ProtectedRoute, GuestOnlyRoute } from './components/RouteGuards.jsx'
import AppLayout from './components/AppLayout.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Practice from './pages/Practice.jsx'
import NotFound from './pages/NotFound.jsx'

// ROUTES: which page shows for which URL.
export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Landing />} />

      {/* Only for logged-OUT users (logged-in users get sent to the dashboard) */}
      <Route path="/login" element={<GuestOnlyRoute><Login /></GuestOnlyRoute>} />
      <Route path="/signup" element={<GuestOnlyRoute><Signup /></GuestOnlyRoute>} />

      {/* Only for logged-IN users. They share the AppLayout (top navigation bar). */}
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/practice" element={<Practice />} />
      </Route>

      {/* Anything else */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
