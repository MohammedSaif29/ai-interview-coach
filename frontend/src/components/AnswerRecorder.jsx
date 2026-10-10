import { useState } from 'react'
import { api } from '../lib/api.js'
import { MAX_SECONDS, useRecorder } from '../hooks/useRecorder.js'
import { Button } from './ui/Button.jsx'
import { Alert } from './ui/Alert.jsx'
import LiveWaveform from './LiveWaveform.jsx'
import Waveform from './Waveform.jsx'

// 75 -> "1:15"
function formatTime(totalSeconds) {
  const s = Math.max(0, Math.round(totalSeconds))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

/*
  The recording flow, one step at a time:
  idle -> recording -> recorded (listen back) -> transcribing -> transcript
*/
export default function AnswerRecorder() {
  const recorder = useRecorder()
  const [transcribing, setTranscribing] = useState(false)
  const [result, setResult] = useState(null)
  const [uploadError, setUploadError] = useState('')

  async function getTranscript() {
    const { blob } = recorder.recording
    const extension = blob.type.includes('mp4') ? 'mp4' : blob.type.includes('ogg') ? 'ogg' : 'webm'
    // FormData: how browsers send files to a server
    const form = new FormData()
    form.append('audio', blob, `answer.${extension}`)

    setTranscribing(true)
    setUploadError('')
    try {
      setResult(await api('/answers/transcribe', { method: 'POST', body: form }))
    } catch (err) {
      setUploadError(err.message)
    } finally {
      setTranscribing(false)
    }
  }

  function recordAgain() {
    setResult(null)
    setUploadError('')
    recorder.reset()
  }

  // ----- Step 5: transcript is ready -----
  if (result) {
    const wordCount = result.words.length || result.transcript.split(/\s+/).filter(Boolean).length
    const duration = result.duration_seconds || recorder.recording?.seconds || 0
    return (
      <div className="animate-fade-up">
        <p className="text-sm text-white/50">Your answer, transcribed</p>
        {result.transcript ? (
          <p className="mt-2 text-[17px] leading-[1.75] text-white/90">{result.transcript}</p>
        ) : (
          <p className="mt-2 text-white/60">
            No speech was detected. Record again, a little closer to your microphone.
          </p>
        )}
        <div className="mt-5 flex flex-wrap gap-x-6 gap-y-2 border-t border-white/10 pt-5">
          <Stat value={formatTime(duration)} label="speaking time" />
          <Stat value={wordCount} label="words" />
        </div>
        <Button variant="outlineLight" onClick={recordAgain} className="mt-6">
          Record again
        </Button>
      </div>
    )
  }

  // ----- Step 3 & 4: listen back, then send for transcription -----
  if (recorder.status === 'recorded') {
    return (
      <div className="animate-fade-up">
        <p className="text-sm text-white/50">
          Your recording, {formatTime(recorder.recording.seconds)}. Listen back before you send it.
        </p>
        {/* color-scheme: dark makes the browser draw dark audio controls */}
        <audio controls src={recorder.recording.url} className="mt-3 w-full [color-scheme:dark]" />

        {transcribing && (
          <div className="mt-6 flex items-center gap-4" role="status">
            <Waveform bars={18} />
            <p className="text-sm text-white/70">Transcribing your answer…</p>
          </div>
        )}
        {uploadError && <Alert dark className="mt-5">{uploadError}</Alert>}

        <div className="mt-6 flex flex-wrap gap-3">
          <Button variant="glow" onClick={getTranscript} disabled={transcribing}>
            {transcribing ? 'Transcribing…' : 'Get transcript'}
          </Button>
          <Button variant="outlineLight" onClick={recordAgain} disabled={transcribing}>
            Record again
          </Button>
        </div>
      </div>
    )
  }

  // ----- Step 2: recording -----
  if (recorder.status === 'recording') {
    return (
      <div className="flex flex-col items-center text-center">
        <div className="relative w-full max-w-sm">
          <div aria-hidden="true" className="absolute inset-x-6 inset-y-0 animate-breathe rounded-full bg-glow/15 blur-2xl" />
          <LiveWaveform levels={recorder.levels} className="relative" />
        </div>
        <p className="mt-6 text-4xl font-semibold tabular-nums" aria-live="off">
          {formatTime(recorder.seconds)}
          <span className="ml-2 text-base font-normal text-white/40">/ {formatTime(MAX_SECONDS)}</span>
        </p>
        <p className="mt-2 flex items-center gap-2 text-sm text-white/60">
          <span className="size-2 animate-pulse rounded-full bg-mark-light" />
          Recording
        </p>
        <Button variant="outlineLight" onClick={recorder.stop} className="mt-7">
          <span className="size-3 rounded-[3px] bg-current" aria-hidden="true" />
          Stop recording
        </Button>
      </div>
    )
  }

  // ----- Step 1: ready to record -----
  const requesting = recorder.status === 'requesting'
  return (
    <div className="flex flex-col items-center text-center">
      <button
        onClick={recorder.start}
        disabled={requesting}
        aria-label="Start recording"
        className="grid size-20 place-items-center rounded-full bg-glow text-night shadow-[0_0_40px_-6px_var(--color-glow)] transition-all duration-200 hover:scale-105 hover:shadow-[0_0_60px_-4px_var(--color-glow)] active:scale-95 disabled:opacity-70"
      >
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor" />
          <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
        </svg>
      </button>
      <p className="mt-5 font-semibold">{requesting ? 'Waiting for microphone permission…' : 'Start recording'}</p>
      <p className="mt-1 max-w-xs text-sm text-white/50">
        Your browser will ask to use your microphone. You can record for up to 3 minutes.
      </p>
      {recorder.error && <Alert dark className="mt-5 text-left">{recorder.error}</Alert>}
    </div>
  )
}

function Stat({ value, label }) {
  return (
    <p className="text-sm text-white/60">
      <span className="mr-1 text-lg font-semibold text-white">{value}</span>
      {label}
    </p>
  )
}
