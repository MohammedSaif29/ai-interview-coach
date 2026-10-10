/*
  useRecorder: records audio from the microphone in the browser.

  Uses two browser features:
  - MediaRecorder: records the microphone into an audio file (a Blob)
  - Web Audio API (AnalyserNode): measures how loud each frequency is, many times
    per second. We turn that into the live waveform bars.
*/
import { useCallback, useEffect, useRef, useState } from 'react'

export const MAX_SECONDS = 180 // stop automatically after 3 minutes
export const BAR_COUNT = 32

// Different browsers record in different formats (Safari can't do webm)
function pickMimeType() {
  const options = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus']
  return options.find((type) => window.MediaRecorder?.isTypeSupported?.(type)) ?? ''
}

function micErrorMessage(error) {
  if (error.name === 'NotAllowedError') {
    return 'Microphone access is blocked. Click the lock icon in the address bar, allow the microphone, then try again.'
  }
  if (error.name === 'NotFoundError') return 'No microphone was found. Connect one and try again.'
  if (error.name === 'NotReadableError') return 'Another app is using your microphone. Close it and try again.'
  return "Couldn't start the microphone. Try again."
}

const silent = () => Array(BAR_COUNT).fill(0)

export function useRecorder() {
  const [status, setStatus] = useState('idle') // idle | requesting | recording | recorded
  const [error, setError] = useState('')
  const [seconds, setSeconds] = useState(0)
  const [levels, setLevels] = useState(silent)
  const [recording, setRecording] = useState(null) // { blob, url, seconds }

  // Things we need to reach from several functions, but that shouldn't re-render the page
  const r = useRef({}).current

  const releaseMicrophone = useCallback(() => {
    cancelAnimationFrame(r.frame)
    clearInterval(r.timer)
    r.stream?.getTracks().forEach((track) => track.stop()) // turns off the mic light
    r.audioContext?.close().catch(() => {})
    r.stream = null
    r.audioContext = null
  }, [r])

  const stop = useCallback(() => {
    if (r.recorder && r.recorder.state !== 'inactive') r.recorder.stop()
  }, [r])

  const start = useCallback(async () => {
    setError('')
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setError("This browser can't record audio. Try the latest Chrome, Edge, Firefox or Safari.")
      return
    }

    setStatus('requesting')
    let stream
    try {
      // This is the moment the browser asks "Allow microphone?"
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
      })
    } catch (err) {
      setStatus('idle')
      setError(micErrorMessage(err))
      return
    }
    r.stream = stream
    r.discard = false

    // 1. The recorder: collects audio in small chunks
    const mimeType = pickMimeType()
    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
    r.recorder = recorder
    r.chunks = []
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) r.chunks.push(event.data)
    }
    recorder.onstop = () => {
      const elapsed = (Date.now() - r.startedAt) / 1000
      releaseMicrophone()
      setLevels(silent())
      if (r.discard) {
        setStatus('idle')
        return
      }
      // Glue the chunks into one audio file, and make a local URL so <audio> can play it
      const blob = new Blob(r.chunks, { type: recorder.mimeType || 'audio/webm' })
      if (r.url) URL.revokeObjectURL(r.url)
      r.url = URL.createObjectURL(blob)
      setRecording({ blob, url: r.url, seconds: elapsed })
      setStatus('recorded')
    }

    // 2. The analyser: reads loudness for the live waveform
    const AudioContext = window.AudioContext || window.webkitAudioContext
    const audioContext = new AudioContext()
    r.audioContext = audioContext
    const analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    analyser.smoothingTimeConstant = 0.7
    audioContext.createMediaStreamSource(stream).connect(analyser)
    const data = new Uint8Array(analyser.frequencyBinCount)
    const voiceBins = 64 // human speech is mostly in the lower frequencies
    const perBar = voiceBins / BAR_COUNT
    let lastDraw = 0

    const draw = (time) => {
      r.frame = requestAnimationFrame(draw)
      if (time - lastDraw < 50) return // about 20 updates a second is plenty
      lastDraw = time
      analyser.getByteFrequencyData(data) // fills `data` with values 0–255
      const bars = []
      for (let i = 0; i < BAR_COUNT; i++) {
        let sum = 0
        for (let j = i * perBar; j < (i + 1) * perBar; j++) sum += data[j]
        bars.push(Math.min(1, sum / perBar / 180))
      }
      setLevels(bars)
    }
    r.frame = requestAnimationFrame(draw)

    // 3. The timer
    r.startedAt = Date.now()
    setSeconds(0)
    r.timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - r.startedAt) / 1000)
      setSeconds(elapsed)
      if (elapsed >= MAX_SECONDS) stop()
    }, 250)

    recorder.start(1000) // hand us a chunk every second
    setStatus('recording')
  }, [r, releaseMicrophone, stop])

  // Throw away the current recording and go back to the start
  const reset = useCallback(() => {
    if (r.recorder?.state === 'recording') {
      r.discard = true
      r.recorder.stop()
    }
    if (r.url) URL.revokeObjectURL(r.url)
    r.url = null
    setRecording(null)
    setSeconds(0)
    setError('')
    setStatus('idle')
  }, [r])

  // When the component disappears (e.g. user leaves the page), turn the mic off
  useEffect(() => {
    return () => {
      r.discard = true
      if (r.recorder?.state === 'recording') r.recorder.stop()
      releaseMicrophone()
      if (r.url) URL.revokeObjectURL(r.url)
    }
  }, [r, releaseMicrophone])

  return { status, error, seconds, levels, recording, start, stop, reset }
}
