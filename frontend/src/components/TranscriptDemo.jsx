import { useEffect, useState } from 'react'
import Waveform from './Waveform.jsx'

/*
  Landing page demo: an example answer "types itself out" like a live transcript
  while a waveform shows the app listening. Then the analysis appears.
  This is exactly what the real app will do with your voice.
*/

const QUESTION = 'Tell me about yourself.'

// Each item is a word, or a pause marker. Fillers are flagged.
const ANSWER = [
  'So,', { filler: 'um,' }, "I'm", 'a', 'final-year', 'computer', 'science', 'student.', 'I',
  { filler: 'like,' }, 'really', 'enjoy', 'building', 'web', 'apps,', 'and', 'this', 'semester',
  'I', 'built,', { pause: '2.4s' }, { filler: 'uh,' }, 'an', 'AI', 'tool', 'that', 'helps',
  'students', 'practise', 'interviews', 'out', 'loud.',
]

const STATS = [
  { value: '3', label: 'filler words', highlight: true },
  { value: '146', label: 'words per minute' },
  { value: '1', label: 'long pause' },
]

const FULL_TEXT = ANSWER.map((t) => (typeof t === 'string' ? t : t.filler ?? '')).join(' ')

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export default function TranscriptDemo() {
  const [shown, setShown] = useState(0)
  const [run, setRun] = useState(0) // changing this restarts the animation
  const done = shown >= ANSWER.length

  useEffect(() => {
    if (prefersReducedMotion()) {
      setShown(ANSWER.length)
      return
    }
    setShown(0)
    let count = 0
    let timer = setTimeout(function tick() {
      count += 1
      setShown(count)
      if (count < ANSWER.length) {
        const nextIsPause = typeof ANSWER[count] === 'object' && ANSWER[count].pause
        timer = setTimeout(tick, nextIsPause ? 700 : 115)
      }
    }, 900)
    return () => clearTimeout(timer) // cleanup: stop the timer if the page closes
  }, [run])

  return (
    <div className="relative">
      {/* The glow behind the card: breathes while listening, calms down when done */}
      <div
        aria-hidden="true"
        className={`pointer-events-none absolute -inset-8 rounded-[3rem] bg-glow/20 blur-3xl transition-opacity duration-1000 ${
          done ? 'opacity-40' : 'animate-breathe'
        }`}
      />

      <figure className="relative rounded-2xl border border-white/10 bg-white/[0.04] p-6 text-white shadow-[0_0_0_1px_rgba(62,224,191,0.08),0_30px_80px_-30px_rgba(62,224,191,0.35)] backdrop-blur-md [--filler:var(--color-mark-light)] sm:p-8">
        <div className="flex items-center justify-between gap-4">
          <p className="flex items-center gap-2 text-sm text-white/70">
            <span className="relative flex size-2">
              {!done && <span className="absolute inline-flex size-full animate-ping rounded-full bg-glow opacity-75" />}
              <span className="relative inline-flex size-2 rounded-full bg-glow" />
            </span>
            {done ? 'Analysis ready' : 'Listening'}
          </p>
          <Waveform active={!done} bars={24} />
        </div>

        <p className="mt-6 text-sm text-white/50">Question</p>
        <p className="mt-1 font-serif text-2xl tracking-tight">&ldquo;{QUESTION}&rdquo;</p>

        <div className="mt-5 border-t border-white/10 pt-5">
          <p className="text-sm text-white/50">Your answer, transcribed</p>

          {/* Screen readers get the full text at once; the animation is visual only */}
          <p className="sr-only">{FULL_TEXT}</p>
          <p aria-hidden="true" className="mt-2 min-h-[7em] text-[17px] leading-[1.75] text-white/90">
            {ANSWER.slice(0, shown).map((token, i) => {
              if (typeof token === 'string') return <span key={i}>{token} </span>
              if (token.filler) return <span key={i}><span className="filler">{token.filler}</span> </span>
              return (
                <span key={i} className="mx-0.5 inline-block rounded bg-white/10 px-1.5 align-[1px] text-xs font-medium text-white/60">
                  pause {token.pause}
                </span>
              )
            })}
            {!done && (
              <span className="inline-block h-[1.1em] w-0.5 translate-y-[3px] animate-pulse bg-glow shadow-[0_0_8px_var(--color-glow)]" />
            )}
          </p>
        </div>

        <figcaption className="mt-5 flex min-h-8 flex-wrap items-baseline gap-x-6 gap-y-2 border-t border-white/10 pt-5">
          {done &&
            STATS.map((stat, i) => (
              <p
                key={`${run}-${stat.label}`}
                className="animate-fade-up text-sm text-white/60"
                style={{ animationDelay: `${i * 150}ms` }}
              >
                <span className={`mr-1 text-lg font-semibold ${stat.highlight ? 'text-mark-light' : 'text-white'}`}>
                  {stat.value}
                </span>
                {stat.label}
              </p>
            ))}
          {done && (
            <button
              onClick={() => setRun(run + 1)}
              className="ml-auto animate-fade-up text-sm font-semibold text-glow underline-offset-4 hover:underline"
              style={{ animationDelay: '500ms' }}
            >
              Replay
            </button>
          )}
        </figcaption>
      </figure>
    </div>
  )
}
