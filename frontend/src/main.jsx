// Starting point: finds <div id="root"> in index.html and puts our App inside it.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import { AuthProvider } from './context/AuthContext.jsx'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* BrowserRouter: lets us have real pages (/login, /dashboard) in one React app */}
    <BrowserRouter>
      {/* AuthProvider: makes "who is logged in" available to every page */}
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
)
