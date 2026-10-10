import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../lib/api.js'

// Loads an interview question for a role. `next()` fetches a different one.
// When `role` changes, a new question loads automatically.
export function useQuestion(role = 'hr') {
  const [question, setQuestion] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  // useRef: remembers a value between renders without causing a re-render
  const current = useRef(null)

  const next = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      // The backend picks randomly, so it can repeat. Try a few times for a new one.
      let data
      for (let attempt = 0; attempt < 3; attempt++) {
        data = await api(`/question?role=${encodeURIComponent(role)}`)
        if (data.question !== current.current) break
      }
      current.current = data.question
      setQuestion(data.question)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [role])

  useEffect(() => {
    current.current = null
    next()
  }, [next])

  return { question, loading, error, next }
}
