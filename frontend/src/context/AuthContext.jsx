/*
  AUTH CONTEXT: stores the logged-in user in one place.
  Any component can call useAuth() to read the user or log in / out,
  instead of passing the user down through every component by hand.
*/
import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../lib/api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // true while we ask the backend "am I logged in?" on first load
  const [checking, setChecking] = useState(true)

  // On page load: the login cookie may already exist from earlier,
  // so ask /auth/me who we are. 401 just means "not logged in".
  useEffect(() => {
    api('/auth/me')
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  async function login(email, password) {
    const loggedInUser = await api('/auth/login', { method: 'POST', body: { email, password } })
    setUser(loggedInUser)
  }

  async function signup(name, email, password) {
    const newUser = await api('/auth/signup', { method: 'POST', body: { name, email, password } })
    setUser(newUser)
  }

  async function logout() {
    try {
      await api('/auth/logout', { method: 'POST' })
    } finally {
      setUser(null) // log out on screen even if the request failed
    }
  }

  return (
    // setUser is shared too, so the Settings page can update the name everywhere at once
    <AuthContext.Provider value={{ user, checking, login, signup, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
