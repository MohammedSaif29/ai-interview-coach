import { Routes, Route } from 'react-router'
import { ProtectedRoute, GuestOnlyRoute } from './components/RouteGuards.jsx'
import AppLayout from './components/AppLayout.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Practice from './pages/Practice.jsx'
import History from './pages/History.jsx'
import SessionDetail from './pages/SessionDetail.jsx'
import Settings from './pages/Settings.jsx'
import Coach from './pages/Coach.jsx'
import Resume from './pages/Resume.jsx'
import Companies from './pages/Companies.jsx'
import CompanyDetail from './pages/CompanyDetail.jsx'
import MockTest from './pages/MockTest.jsx'
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
        <Route path="/history" element={<History />} />
        {/* :id is a URL parameter, e.g. /history/12 -> id = "12" */}
        <Route path="/history/:id" element={<SessionDetail />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/coach" element={<Coach />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/companies" element={<Companies />} />
        <Route path="/companies/:companyId" element={<CompanyDetail />} />
        <Route path="/companies/:companyId/tests/:testId" element={<MockTest />} />
      </Route>

      {/* Anything else */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
