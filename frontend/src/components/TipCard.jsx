import { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { TextButton } from './ui/Button.jsx'

export default function TipCard({ className = '' }) {
  const [tip, setTip] = useState('')
  const [loading, setLoading] = useState(false)

  async function loadTip() {
    setLoading(true)
    try {
      const data = await api('/tip')
      setTip(data.tip)
    } catch {
      setTip('') // tips are optional, so we simply hide the card if this fails
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTip()
  }, [])

  if (!tip) return null

  return (
    <section className={`rounded-2xl border border-line bg-white p-6 ${className}`}>
      <h2 className="text-sm font-semibold text-brand">Interview tip</h2>
      <p className="mt-2 leading-relaxed" aria-live="polite">{tip}</p>
      <TextButton onClick={loadTip} disabled={loading} className="mt-4">
        Show another tip
      </TextButton>
    </section>
  )
}
