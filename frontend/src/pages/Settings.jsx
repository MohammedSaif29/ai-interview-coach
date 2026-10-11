import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { api } from '../lib/api.js'
import { Button } from '../components/ui/Button.jsx'
import { Alert } from '../components/ui/Alert.jsx'
import { Field } from '../components/ui/Field.jsx'

export default function Settings() {
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Settings</h1>
      <p className="mt-2 text-muted">Manage your name, password and account.</p>
      <div className="mt-8 space-y-6">
        <NameSection />
        <PasswordSection />
        <DeleteSection />
      </div>
    </div>
  )
}

function Section({ title, description, children, danger = false }) {
  return (
    <section className={`rounded-2xl border bg-white p-6 sm:p-8 ${danger ? 'border-mark/30' : 'border-line'}`}>
      <h2 className={`text-lg font-semibold ${danger ? 'text-mark' : ''}`}>{title}</h2>
      {description && <p className="mt-1 text-sm leading-relaxed text-muted">{description}</p>}
      <div className="mt-5">{children}</div>
    </section>
  )
}

// A short green confirmation; role="status" lets screen readers announce it
function Saved({ children }) {
  return (
    <p role="status" className="text-sm font-medium text-brand">
      {children}
    </p>
  )
}

function NameSection() {
  const { user, setUser } = useAuth()
  const [name, setName] = useState(user.name)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  async function save(e) {
    e.preventDefault()
    if (!name.trim()) {
      setError('Enter your name.')
      return
    }
    setSaving(true)
    setError('')
    setSaved(false)
    try {
      setUser(await api('/auth/me', { method: 'PATCH', body: { name: name.trim() } }))
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Section title="Your name" description="Shown on your dashboard.">
      <form onSubmit={save} noValidate className="space-y-4">
        <Field label="Name" id="name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" />
        {error && <Alert>{error}</Alert>}
        <div className="flex flex-wrap items-center gap-4">
          <Button type="submit" disabled={saving || name.trim() === user.name}>
            {saving ? 'Saving…' : 'Save name'}
          </Button>
          {saved && <Saved>Name saved.</Saved>}
        </div>
      </form>
    </Section>
  )
}

function PasswordSection() {
  const [form, setForm] = useState({ current: '', next: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  async function save(e) {
    e.preventDefault()
    if (form.next.length < 8) {
      setError('Use at least 8 characters for your new password.')
      return
    }
    setSaving(true)
    setError('')
    setSaved(false)
    try {
      await api('/auth/change-password', {
        method: 'POST',
        body: { current_password: form.current, new_password: form.next },
      })
      setForm({ current: '', next: '' })
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Section
      title="Password"
      description="Changing your password logs you out on every other device. You stay logged in here."
    >
      <form onSubmit={save} noValidate className="space-y-4">
        <Field
          label="Current password"
          id="current-password"
          type="password"
          autoComplete="current-password"
          value={form.current}
          onChange={(e) => setForm({ ...form, current: e.target.value })}
        />
        <Field
          label="New password"
          id="new-password"
          type="password"
          autoComplete="new-password"
          hint="At least 8 characters."
          value={form.next}
          onChange={(e) => setForm({ ...form, next: e.target.value })}
        />
        {error && <Alert>{error}</Alert>}
        <div className="flex flex-wrap items-center gap-4">
          <Button type="submit" disabled={saving || !form.current || !form.next}>
            {saving ? 'Changing…' : 'Change password'}
          </Button>
          {saved && <Saved>Password changed. Other devices have been logged out.</Saved>}
        </div>
      </form>
    </Section>
  )
}

function DeleteSection() {
  const [confirming, setConfirming] = useState(false)
  const [password, setPassword] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')

  async function deleteAccount(e) {
    e.preventDefault()
    setDeleting(true)
    setError('')
    try {
      await api('/auth/me', { method: 'DELETE', body: { password } })
      // A full page load of the home page. It also wipes every bit of app state
      // left over from the deleted account, which is exactly what we want here.
      // (Navigating inside React didn't work: React handled "no user" first, and this
      // protected page redirected to /login before the navigation happened.)
      window.location.replace('/')
    } catch (err) {
      setError(err.message)
      setDeleting(false)
    }
  }

  return (
    <Section
      title="Delete account"
      description="Permanently deletes your account and every practice session you've recorded. This can't be undone."
      danger
    >
      {confirming ? (
        <form onSubmit={deleteAccount} noValidate className="space-y-4">
          <Field
            label="Enter your password to confirm"
            id="delete-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <Alert>{error}</Alert>}
          <div className="flex flex-wrap gap-3">
            <Button type="submit" variant="danger" disabled={deleting || !password}>
              {deleting ? 'Deleting…' : 'Delete my account'}
            </Button>
            <Button type="button" variant="secondary" onClick={() => { setConfirming(false); setPassword(''); setError('') }} disabled={deleting}>
              Cancel
            </Button>
          </div>
        </form>
      ) : (
        <button
          onClick={() => setConfirming(true)}
          className="rounded-lg border border-mark/40 bg-white px-4 py-2.5 text-[15px] font-semibold text-mark transition-colors hover:bg-mark/5"
        >
          Delete account…
        </button>
      )}
    </Section>
  )
}
